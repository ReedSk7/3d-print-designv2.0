from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import trimesh


PROJECT = Path(__file__).resolve().parents[1]
INVENTORY = PROJECT / "notes" / "kobalt_81798_socket_organizer_v03_inventory.json"
SOURCE = PROJECT / "source" / "kobalt_81798_socket_organizer_v03.scad"
EXPORTS = PROJECT / "exports"
SAFE_MAX = 245.0
BASE_T = 12.70
LABEL_H = 0.70

MODULES = {
    "left_top": {"w": 219.71, "d": 197.87},
    "left_bottom": {"w": 219.71, "d": 134.87},
    "center_top_left": {"w": 127.00, "d": 166.37},
    "center_top_right": {"w": 127.00, "d": 166.37},
    "center_bottom_left": {"w": 127.00, "d": 166.37},
    "center_bottom_right": {"w": 127.00, "d": 166.37},
    "right_top": {"w": 147.32, "d": 157.40},
    "right_bottom": {"w": 147.32, "d": 175.26},
}
FIT_TEST = {"w": 230.0, "d": 90.0}

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
    "kind",
    "x",
    "y",
    "label_x",
    "label_y",
    "label_rotation",
    "label_size",
}

MODULE_NAMES = list(MODULES)
REQUIRED_BODY_STLS = {
    name: EXPORTS / f"kobalt_81798_socket_organizer_v03_{name}_body.stl"
    for name in MODULE_NAMES
}
REQUIRED_LABEL_STLS = {
    name: EXPORTS / f"kobalt_81798_socket_organizer_v03_{name}_labels.stl"
    for name in MODULE_NAMES
}
REQUIRED_BODY_STLS["fit_test_plate"] = EXPORTS / "kobalt_81798_socket_organizer_v03_fit_test_plate_body.stl"
REQUIRED_LABEL_STLS["fit_test_plate"] = EXPORTS / "kobalt_81798_socket_organizer_v03_fit_test_plate_labels.stl"

LABEL_RE = re.compile(r"^[A-Z0-9_]+$")


def label_width(label: str, size: float) -> float:
    return max(1, len(label)) * size * 0.62


def label_bbox(row: dict) -> tuple[float, float, float, float]:
    size = float(row["label_size"])
    w = label_width(str(row["display_label"]), size)
    h = size
    rot = abs(float(row.get("label_rotation", 0))) % 180
    if 45 <= rot <= 135:
        w, h = h, w
    cx = float(row["label_x"])
    cy = float(row["label_y"])
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def rects_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float], pad: float = 0.0) -> bool:
    return not (
        a[2] <= b[0] + pad
        or b[2] <= a[0] + pad
        or a[3] <= b[1] + pad
        or b[3] <= a[1] + pad
    )


def rect_circle_overlap(rect: tuple[float, float, float, float], cx: float, cy: float, cr: float) -> bool:
    rx = (rect[0] + rect[2]) / 2
    ry = (rect[1] + rect[3]) / 2
    rw = rect[2] - rect[0]
    rh = rect[3] - rect[1]
    dx = max(abs(cx - rx) - rw / 2, 0.0)
    dy = max(abs(cy - ry) - rh / 2, 0.0)
    return dx * dx + dy * dy < cr * cr


def channel_bbox(row: dict) -> tuple[float, float, float, float]:
    width = float(row["channel_width"])
    x1 = float(row["channel_x1"])
    y1 = float(row["channel_y1"])
    x2 = float(row["channel_x2"])
    y2 = float(row["channel_y2"])
    return (
        min(x1, x2) - width / 2,
        min(y1, y2) - width / 2,
        max(x1, x2) + width / 2,
        max(y1, y2) + width / 2,
    )


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

    center_top = [row for row in channels if row["module_name"] in {"center_top_left", "center_top_right"}]
    center_bottom = [row for row in channels if row["module_name"] in {"center_bottom_left", "center_bottom_right"}]
    if len(center_top) != 12:
        errors.append(f"center top channel count {len(center_top)} != 12")
    if len(center_bottom) != 13:
        errors.append(f"center bottom channel count {len(center_bottom)} != 13")

    bad_ascii: list[tuple[int, str]] = []
    blank_labels: list[int] = []
    too_small: list[tuple[int, str, float]] = []
    non_positive_diameters: list[int] = []
    for row in rows:
        missing = REQUIRED_FIELDS - row.keys()
        if missing:
            errors.append(f"row {row.get('sort_order')} missing required fields: {sorted(missing)}")
        label = str(row.get("display_label", ""))
        if not label.strip():
            blank_labels.append(row.get("sort_order"))
        if not label.isascii() or not LABEL_RE.match(label):
            bad_ascii.append((row.get("sort_order"), label))
        if float(row.get("label_size", 0)) < 5.0:
            too_small.append((row.get("sort_order"), label, float(row.get("label_size", 0))))
        if float(row.get("pocket_diameter", 0)) <= 0:
            non_positive_diameters.append(row.get("sort_order"))
    if blank_labels:
        errors.append(f"blank display labels: {blank_labels[:20]}")
    if bad_ascii:
        errors.append(f"non-ASCII or non-uppercase-safe labels: {bad_ascii[:20]}")
    if too_small:
        errors.append(f"labels below 5.0 mm: {too_small[:20]}")
    if non_positive_diameters:
        errors.append(f"rows with pocket_diameter <= 0: {non_positive_diameters[:20]}")

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

    sort_counts = Counter((row["module_name"], row["sort_order"]) for row in rows)
    duplicate_label_objects = [key for key, count in sort_counts.items() if count > 1]
    if duplicate_label_objects:
        errors.append(f"duplicate label objects for same item: {duplicate_label_objects[:20]}")

    xy_counts = Counter(
        (
            row["module_name"],
            round(float(row["label_x"]), 3),
            round(float(row["label_y"]), 3),
            round(float(row.get("label_rotation", 0)), 3),
        )
        for row in rows
    )
    xy_duplicates = [key for key, count in xy_counts.items() if count > 1]
    if xy_duplicates:
        errors.append(f"duplicate label XY positions: {xy_duplicates[:20]}")

    label_collisions: list[tuple[int, int, str]] = []
    label_pocket_overlaps: list[tuple[int, int, str]] = []
    label_channel_overlaps: list[tuple[int, int, str]] = []
    label_out_of_bounds: list[tuple[int, str, tuple[float, float, float, float]]] = []

    for module, items in by_module.items():
        dims = MODULES[module]
        bboxes = [(row, label_bbox(row)) for row in items]
        for i in range(len(bboxes)):
            row_a, bbox_a = bboxes[i]
            if bbox_a[0] < -0.001 or bbox_a[1] < -0.001 or bbox_a[2] > dims["w"] + 0.001 or bbox_a[3] > dims["d"] + 0.001:
                label_out_of_bounds.append((row_a["sort_order"], row_a["display_label"], tuple(round(v, 3) for v in bbox_a)))
            for j in range(i + 1, len(bboxes)):
                row_b, bbox_b = bboxes[j]
                if rects_overlap(bbox_a, bbox_b):
                    label_collisions.append((row_a["sort_order"], row_b["sort_order"], module))

        pocket_like = []
        channel_rects = []
        for target in items:
            if target["kind"] == "cup":
                pocket_like.append(
                    (
                        float(target["x"]),
                        float(target["y"]),
                        float(target["pocket_diameter"]) / 2,
                        target["sort_order"],
                    )
                )
            elif target["kind"] == "channel":
                pocket_like.append(
                    (
                        float(target["end_x"]),
                        float(target["end_y"]),
                        float(target["pocket_diameter"]) / 2,
                        target["sort_order"],
                    )
                )
                channel_rects.append((channel_bbox(target), target["sort_order"]))

        for row, bbox in bboxes:
            for cx, cy, cr, target_order in pocket_like:
                if rect_circle_overlap(bbox, cx, cy, cr):
                    label_pocket_overlaps.append((row["sort_order"], target_order, module))
                    break
            for cb, target_order in channel_rects:
                if rects_overlap(bbox, cb):
                    label_channel_overlaps.append((row["sort_order"], target_order, module))
                    break

    if label_out_of_bounds:
        errors.append(f"labels outside module bounds: {label_out_of_bounds[:20]}")
    if label_collisions:
        errors.append(f"label collisions: {label_collisions[:30]}")
    if label_pocket_overlaps:
        errors.append(f"label overlaps pocket/end pocket: {label_pocket_overlaps[:30]}")
    if label_channel_overlaps:
        errors.append(f"label overlaps long channel: {label_channel_overlaps[:30]}")

    right_bottom_collisions = [
        collision for collision in label_collisions if collision[2] == "right_bottom"
    ]
    right_bottom_pocket_overlaps = [
        collision for collision in label_pocket_overlaps if collision[2] == "right_bottom"
    ]
    if right_bottom_collisions or right_bottom_pocket_overlaps:
        errors.append(
            f"right_bottom stacked/overlapping labels: label={right_bottom_collisions[:20]}, pocket={right_bottom_pocket_overlaps[:20]}"
        )

    source_text = SOURCE.read_text(encoding="utf-8-sig") if SOURCE.is_file() else ""
    if "socket_hole_diameter" in source_text:
        errors.append("source contains banned socket_hole_diameter variable")

    report["storage_count"] = len(rows)
    report["circular_pocket_count"] = len(circular)
    report["long_channel_count"] = len(channels)
    report["center_top_channel_count"] = len(center_top)
    report["center_bottom_channel_count"] = len(center_bottom)
    report["blank_label_count"] = len(blank_labels)
    report["non_ascii_label_count"] = len(bad_ascii)
    report["unreadable_label_count"] = len(blank_labels) + len(bad_ascii) + len(too_small)
    report["duplicate_label_object_count"] = len(duplicate_label_objects)
    report["label_xy_duplicate_count"] = len(xy_duplicates)
    report["label_collision_count"] = len(label_collisions)
    report["label_pocket_overlap_count"] = len(label_pocket_overlaps)
    report["label_channel_overlap_count"] = len(label_channel_overlaps)
    report["stacked_overlapping_label_count"] = len(label_collisions) + len(label_pocket_overlaps) + len(label_channel_overlaps)
    report["right_bottom_stacked_overlapping_label_count"] = len(right_bottom_collisions) + len(right_bottom_pocket_overlaps)
    return errors, report


def load_mesh_bounds(path: Path) -> tuple[list[float], list[float], bool]:
    mesh = trimesh.load_mesh(path, force="mesh")
    bounds = mesh.bounds
    extents = mesh.extents
    return [float(v) for v in bounds[0]], [float(v) for v in bounds[1]], bool(mesh.is_watertight)


def expected_dims(name: str) -> dict[str, float]:
    if name == "fit_test_plate":
        return FIT_TEST
    return MODULES[name]


def check_stls() -> tuple[list[str], dict]:
    errors: list[str] = []
    report: dict = {}
    for name, body_path in REQUIRED_BODY_STLS.items():
        label_path = REQUIRED_LABEL_STLS[name]
        dims = expected_dims(name)
        entry = {
            "body": str(body_path.name),
            "labels": str(label_path.name),
            "pass": False,
        }
        if not body_path.is_file():
            errors.append(f"required body STL missing: {body_path}")
            report[name] = entry
            continue
        if not label_path.is_file():
            errors.append(f"required label STL missing: {label_path}")
            report[name] = entry
            continue

        body_min, body_max, body_watertight = load_mesh_bounds(body_path)
        label_min, label_max, label_watertight = load_mesh_bounds(label_path)
        body_ext = [body_max[i] - body_min[i] for i in range(3)]
        label_ext = [label_max[i] - label_min[i] for i in range(3)]
        entry.update(
            {
                "body_extents": [round(v, 3) for v in body_ext],
                "label_extents": [round(v, 3) for v in label_ext],
                "body_min": [round(v, 3) for v in body_min],
                "label_min": [round(v, 3) for v in label_min],
                "label_max": [round(v, 3) for v in label_max],
                "body_watertight": body_watertight,
                "label_watertight": label_watertight,
            }
        )

        if body_ext[0] > SAFE_MAX or body_ext[1] > SAFE_MAX or body_ext[2] > 256.0:
            errors.append(f"{body_path.name} exceeds build target: {body_ext}")
        if label_ext[0] > SAFE_MAX or label_ext[1] > SAFE_MAX or label_ext[2] > 256.0:
            errors.append(f"{label_path.name} exceeds build target: {label_ext}")
        if abs(body_min[0]) > 0.05 or abs(body_min[1]) > 0.05 or abs(body_min[2]) > 0.05:
            errors.append(f"{body_path.name} origin/bounds unexpected: min {body_min}")
        if body_max[0] > dims["w"] + 0.10 or body_max[1] > dims["d"] + 0.10:
            errors.append(f"{body_path.name} exceeds expected module XY: max {body_max}, expected {dims}")
        if label_min[0] < -0.05 or label_min[1] < -0.05 or label_max[0] > dims["w"] + 0.10 or label_max[1] > dims["d"] + 0.10:
            errors.append(f"{label_path.name} label geometry outside expected XY: min {label_min}, max {label_max}, expected {dims}")
        if not math.isclose(label_min[2], BASE_T, abs_tol=0.08):
            errors.append(f"{label_path.name} label bottom Z {label_min[2]:.3f} != {BASE_T:.3f}")
        if not math.isclose(label_max[2] - label_min[2], LABEL_H, abs_tol=0.08):
            errors.append(f"{label_path.name} label height {label_max[2] - label_min[2]:.3f} != {LABEL_H:.3f}")

        entry["pass"] = True
        report[name] = entry
    return errors, report


def main() -> int:
    errors: list[str] = []
    rows = load_rows()
    inventory_errors, report = check_inventory(rows)
    errors.extend(inventory_errors)
    stl_errors, stl_report = check_stls()
    errors.extend(stl_errors)
    report["build_volume"] = stl_report

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
