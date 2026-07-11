from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import trimesh


PROJECT = Path(__file__).resolve().parents[1]
INVENTORY = PROJECT / "notes" / "kobalt_81798_socket_organizer_v02_inventory.json"
SOURCE = PROJECT / "source" / "kobalt_81798_socket_organizer_v02.scad"
EXPORTS = PROJECT / "exports"
SAFE_MAX = 245.0

REQUIRED_FIELDS = {
    "module_name",
    "group_name",
    "drive",
    "type",
    "raw_label",
    "display_label",
    "pocket_diameter",
    "pocket_depth",
    "row_id",
    "sort_order",
}

REQUIRED_STLS = {
    "left_top": "kobalt_81798_socket_organizer_v02_left_top.stl",
    "left_bottom": "kobalt_81798_socket_organizer_v02_left_bottom.stl",
    "center_top_left": "kobalt_81798_socket_organizer_v02_center_top_left.stl",
    "center_top_right": "kobalt_81798_socket_organizer_v02_center_top_right.stl",
    "center_bottom_left": "kobalt_81798_socket_organizer_v02_center_bottom_left.stl",
    "center_bottom_right": "kobalt_81798_socket_organizer_v02_center_bottom_right.stl",
    "right_top": "kobalt_81798_socket_organizer_v02_right_top.stl",
    "right_bottom": "kobalt_81798_socket_organizer_v02_right_bottom.stl",
    "fit_test_plate": "kobalt_81798_socket_organizer_v02_fit_test_plate.stl",
}

LABEL_RE = re.compile(r"^[A-Z0-9_]+$")


def label_width(label: str, size: float) -> float:
    return max(1, len(label)) * size * 0.62


def rect_circle_overlap(rx: float, ry: float, rw: float, rh: float, cx: float, cy: float, cr: float) -> bool:
    dx = max(abs(cx - rx) - rw / 2, 0.0)
    dy = max(abs(cy - ry) - rh / 2, 0.0)
    return dx * dx + dy * dy < cr * cr


def load_rows() -> list[dict]:
    if not INVENTORY.is_file():
        raise FileNotFoundError(f"inventory missing: {INVENTORY}")
    return json.loads(INVENTORY.read_text(encoding="utf-8-sig"))


def check_inventory(rows: list[dict]) -> tuple[list[str], dict]:
    errors: list[str] = []
    report: dict = {}

    if len(rows) != 153:
        errors.append(f"storage count {len(rows)} != 153")

    circular = [row for row in rows if row.get("kind") == "cup"]
    channels = [row for row in rows if row.get("kind") == "channel"]
    if len(circular) != 128:
        errors.append(f"circular pocket count {len(circular)} != 128")
    if len(channels) != 25:
        errors.append(f"long-channel count {len(channels)} != 25")

    blank_labels = [row for row in rows if not str(row.get("display_label", "")).strip()]
    if blank_labels:
        errors.append(f"blank display labels: {len(blank_labels)}")

    bad_ascii = []
    too_small = []
    for row in rows:
        missing = REQUIRED_FIELDS - row.keys()
        if missing:
            errors.append(f"row {row.get('sort_order')} missing required fields: {sorted(missing)}")
        label = str(row.get("display_label", ""))
        if not label.isascii() or not LABEL_RE.match(label):
            bad_ascii.append((row.get("sort_order"), label))
        if float(row.get("label_size", 0)) < 5.5:
            too_small.append((row.get("sort_order"), label, row.get("label_size")))
        if not isinstance(row.get("pocket_diameter"), (int, float)):
            errors.append(f"row {row.get('sort_order')} has no numeric explicit pocket_diameter")
    if bad_ascii:
        errors.append(f"non-ASCII or non-uppercase-safe labels: {bad_ascii[:10]}")
    if too_small:
        errors.append(f"labels below 5.5 mm: {too_small[:10]}")

    by_module: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_module[row["module_name"]].append(row)

    unique_by_module = {}
    for module, items in sorted(by_module.items()):
        diameters = sorted({round(float(item["pocket_diameter"]), 3) for item in items})
        unique_by_module[module] = len(diameters)
        if len(items) > 1 and len(diameters) < 2:
            errors.append(f"{module} uses fewer than two unique pocket diameters")
    report["unique_pocket_diameter_count_per_module"] = unique_by_module

    source_text = SOURCE.read_text(encoding="utf-8-sig") if SOURCE.is_file() else ""
    if "socket_hole_diameter" in source_text:
        errors.append("source contains banned socket_hole_diameter variable")

    label_overlaps = []
    for module, items in by_module.items():
        cup_like = []
        for item in items:
            if item["kind"] == "cup":
                cup_like.append((item["x"], item["y"], item["pocket_diameter"] / 2, item["sort_order"]))
            elif item["kind"] == "channel":
                cup_like.append((item["end_x"], item["end_y"], item["pocket_diameter"] / 2, item["sort_order"]))
        for item in items:
            if abs(float(item.get("label_rotation", 0))) > 0.001:
                continue
            lw = label_width(item["display_label"], float(item["label_size"]))
            lh = float(item["label_size"])
            for cx, cy, cr, target_order in cup_like:
                if rect_circle_overlap(float(item["label_x"]), float(item["label_y"]), lw, lh, cx, cy, cr):
                    label_overlaps.append((item["sort_order"], item["display_label"], target_order, module))
                    break
    if label_overlaps:
        errors.append(f"label overlaps pocket/end pocket: {label_overlaps[:20]}")
    report["label_overlap_count"] = len(label_overlaps)

    report["storage_count"] = len(rows)
    report["circular_pocket_count"] = len(circular)
    report["long_channel_count"] = len(channels)
    report["unreadable_label_count"] = 0 if not bad_ascii and not blank_labels and not too_small else len(bad_ascii) + len(blank_labels) + len(too_small)
    return errors, report


def check_stls() -> tuple[list[str], dict]:
    errors: list[str] = []
    extents_report: dict = {}
    for module, filename in REQUIRED_STLS.items():
        path = EXPORTS / filename
        if not path.is_file():
            errors.append(f"required STL missing: {path}")
            continue
        mesh = trimesh.load_mesh(path, force="mesh")
        ext = [float(v) for v in mesh.extents]
        extents_report[module] = {
            "file": filename,
            "x": round(ext[0], 3),
            "y": round(ext[1], 3),
            "z": round(ext[2], 3),
            "watertight": bool(mesh.is_watertight),
            "pass": ext[0] <= SAFE_MAX and ext[1] <= SAFE_MAX and ext[2] <= 256.0,
        }
        if ext[0] > SAFE_MAX or ext[1] > SAFE_MAX or ext[2] > 256.0:
            errors.append(f"{filename} exceeds build target: {ext}")
    return errors, extents_report


def main() -> int:
    errors: list[str] = []
    rows = load_rows()
    inventory_errors, report = check_inventory(rows)
    errors.extend(inventory_errors)
    stl_errors, extents = check_stls()
    errors.extend(stl_errors)
    report["build_volume"] = extents

    print(json.dumps(report, indent=2))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
