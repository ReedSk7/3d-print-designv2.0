from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import trimesh
from trimesh.graph import connected_components


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "source" / "kobalt_81798_socket_organizer_v04.scad"
INVENTORY_JSON = PROJECT / "notes" / "kobalt_81798_socket_organizer_v04_inventory.json"
DIAMETER_CHANGES_JSON = PROJECT / "notes" / "kobalt_81798_socket_organizer_v04_diameter_changes.json"
NOTES = PROJECT / "notes" / "kobalt_81798_socket_organizer_v04_notes.md"
DIAMETER_LOG = PROJECT / "notes" / "kobalt_81798_socket_organizer_v04_reference_diameter_log.md"
SEAM_NOTES = PROJECT / "notes" / "kobalt_81798_socket_organizer_v04_seam_design_notes.md"
MANIFEST = PROJECT / "notes" / "kobalt_81798_socket_organizer_v04_manifest.md"
REVIEW = PROJECT / "notes" / "kobalt_81798_socket_organizer_v04_review_report.md"

OVERALL_W = 621.03
OVERALL_D = 332.74
BASE_T = 12.70
SAFE_MAX = 245.0
MIN_WEB = 2.5
EDGE_MARGIN = 12.0
SEAM_LAP_WIDTH = 8.0
SEAM_CLEARANCE = 0.25

MODULES = {
    "left_top": {"w": 219.71, "d": 197.87, "ox": 0.00, "oy": 134.87, "index": 1},
    "left_bottom": {"w": 219.71, "d": 134.87, "ox": 0.00, "oy": 0.00, "index": 2},
    "center_top_left": {"w": 127.00, "d": 166.37, "ox": 219.71, "oy": 166.37, "index": 3},
    "center_top_right": {"w": 127.00, "d": 166.37, "ox": 346.71, "oy": 166.37, "index": 4},
    "center_bottom_left": {"w": 127.00, "d": 166.37, "ox": 219.71, "oy": 0.00, "index": 5},
    "center_bottom_right": {"w": 127.00, "d": 166.37, "ox": 346.71, "oy": 0.00, "index": 6},
    "right_top": {"w": 147.32, "d": 157.40, "ox": 473.71, "oy": 175.26, "index": 7},
    "right_bottom": {"w": 147.32, "d": 175.26, "ox": 473.71, "oy": 0.00, "index": 8},
}

FIT_TEST = {"w": 230.0, "d": 90.0, "index": 9}
DEPTH_BY_DRIVE = {"1/4": 5.5, "3/8": 6.5, "1/2": 7.5}
LABEL_SIZE = 5.5
LABEL_HEIGHT = 0.7

REFERENCE_PATHS = [
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\1-2 Imp 12 pt - 1-2 Imp 12 pt (1).stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\1-2 Metric 12 pt - 1-4- Drive - Metric - Deep - 12pt.stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\1-4 Imp 6 pt - 1-4- Imperial 6pt.stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\1-4 Imp 12 pt - 1-4- Drive - Imperial - Deep - 6pt.stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\1-4 Imp Deep - Vertical - 1-4- Drive - Imperial - Deep - 6pt.stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\1-4 Metric Deep - Vertical - 1-4- Drive - Metric - Deep - 6pt (5).stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\1-4 Metric Short - Vertical - 1-4- Drive - Metric - Short - 6 Pt.stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\3-8 Imp Deep - Tray (1).stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\3-8 Imperial 12 pt - Tray.stl(1).stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\3-8 Imperial 12 pt - Tray.stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\3-8 Metric 6pt - Plate (1).stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\3-8 Metric 12 pt - Tray (1).stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Koblat-pieces\3-8 Metric Deep - Plate (1).stl.stl"),
    Path(r"C:\Users\reeds\Downloads\Printable Kobalt Sockets Gridfinity.stl"),
]

diameter_changes: list[dict] = []
reference_summary: list[dict] = []


def import_v02_builder():
    path = Path(__file__).with_name("build_v02.py")
    spec = importlib.util.spec_from_file_location("kobalt_v02_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load v02 builder from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V02 = import_v02_builder()


def display_label(raw: str, drive_prefix: str | None = None) -> str:
    value = raw.upper().replace("MM", "M").replace(".", "_").replace("/", "_")
    value = value.replace(" FLAT", "").replace(" SLOT", "")
    value = value.replace(" ", "")
    if drive_prefix:
        value = f"{drive_prefix}{value}"
    return value


def label_width(label: str, size: float = LABEL_SIZE) -> float:
    return max(1, len(label)) * size * 0.62


def row_positions(module_name: str, labels: list[str], diameters: list[float]) -> list[float]:
    mod = MODULES[module_name]
    max_d = max(diameters)
    max_label = max(label_width(label) for label in labels)
    base_margin = 8.0 if module_name.startswith("center_") or module_name.startswith("right_") else EDGE_MARGIN
    margin = max(base_margin + max_d / 2, max_label / 2 + 3.0, 9.0)
    if len(labels) == 1:
        return [mod["w"] / 2]
    pitch = (mod["w"] - 2 * margin) / (len(labels) - 1)
    if pitch < max_d + MIN_WEB:
        raise ValueError(
            f"Row spacing fail in {module_name}: pitch {pitch:.2f}, diameter {max_d:.2f}"
        )
    return [round(margin + i * pitch, 3) for i in range(len(labels))]


inventory: list[dict] = []
sort_order = 1


def normalize_base_rows() -> None:
    global sort_order
    center_modules = {
        "center_top_left",
        "center_top_right",
        "center_bottom_left",
        "center_bottom_right",
    }
    for old_row in V02.inventory:
        if old_row["module_name"] in center_modules:
            continue
        row = dict(old_row)
        row["sort_order"] = sort_order
        row["label_size"] = 5.5

        if row["module_name"] == "right_top" and row["row_id"] == "rt_07":
            row["label_size"] = 5.0
            row["label_y"] = 4.0
        if row["module_name"] == "right_top" and row["row_id"] == "rt_04":
            row["label_size"] = 5.0
            row["label_y"] = 66.55

        if row["module_name"] == "right_bottom":
            row["label_size"] = 5.0
            y_by_row = {
                "rb_01": (160.0, 145.9),
                "rb_02": (130.0, 115.5),
                "rb_03": (103.0, 89.3),
                "rb_04": (75.0, 60.5),
                "rb_05": (47.0, 33.0),
                "rb_06": (20.0, 5.0),
            }
            y, label_y = y_by_row[row["row_id"]]
            row["y"] = y
            row["end_y"] = y
            row["label_y"] = label_y

        inventory.append(row)
        sort_order += 1


def add_channel_bank(
    module_name: str,
    group_name: str,
    drive: str | list[str],
    type_name: str,
    raw_labels: list[str],
    end_diameters: list[float],
    channel_widths: list[float],
    row_id: str,
    drive_prefix: str | list[str],
) -> None:
    global sort_order
    drives = drive if isinstance(drive, list) else [drive] * len(raw_labels)
    prefixes = drive_prefix if isinstance(drive_prefix, list) else [drive_prefix] * len(raw_labels)
    labels = [display_label(raw, prefix) for raw, prefix in zip(raw_labels, prefixes)]
    xs = row_positions(module_name, labels, end_diameters)
    y1 = 32.0
    y2 = 128.0
    end_y = 146.0
    for raw, label, diameter, width, x, item_drive in zip(
        raw_labels, labels, end_diameters, channel_widths, xs, drives
    ):
        inventory.append(
            {
                "module_name": module_name,
                "group_name": group_name,
                "drive": item_drive,
                "type": type_name,
                "raw_label": raw,
                "display_label": label,
                "pocket_diameter": diameter,
                "pocket_depth": DEPTH_BY_DRIVE[item_drive],
                "row_id": row_id,
                "sort_order": sort_order,
                "kind": "channel",
                "x": round(x, 3),
                "y": round((y1 + y2) / 2, 3),
                "label_x": round(x, 3),
                "label_y": 20.0,
                "label_rotation": 90,
                "label_size": 5.5,
                "channel_width": width,
                "channel_x1": round(x, 3),
                "channel_y1": y1,
                "channel_x2": round(x, 3),
                "channel_y2": y2,
                "end_x": round(x, 3),
                "end_y": end_y,
            }
        )
        sort_order += 1


def add_center_v03_channels() -> None:
    # v03 target: 12 upper center channels and 13 lower center channels.
    add_channel_bank(
        "center_top_left",
        "1/4DR long-ball hex SAE and metric upper left",
        "1/4",
        "long-ball hex",
        ["1/8", "5/32", "3/16", "7/32", "3mm", "4mm"],
        [12.2, 12.4, 12.6, 12.8, 13.0, 13.2],
        [6.1, 6.2, 6.3, 6.4, 6.2, 6.4],
        "ctl_01",
        "Q",
    )
    add_channel_bank(
        "center_top_right",
        "1/4DR and 3/8DR long-ball hex upper transition",
        ["1/4", "1/4", "3/8", "3/8", "3/8", "3/8"],
        "long-ball hex",
        ["5mm", "6mm", "1/8", "5/32", "3/16", "7/32"],
        [13.4, 13.8, 14.6, 15.0, 15.5, 16.0],
        [6.5, 6.7, 6.5, 6.6, 6.7, 6.8],
        "ctr_01",
        ["Q", "Q", "D", "D", "D", "D"],
    )
    add_channel_bank(
        "center_bottom_left",
        "3/8DR long-ball hex SAE and metric lower left",
        "3/8",
        "long-ball hex",
        ["1/4", "5/16", "3/8", "3mm", "4mm", "5mm", "6mm"],
        [12.4, 12.6, 13.0, 12.4, 12.6, 13.0, 13.2],
        [6.8, 7.0, 7.2, 6.5, 6.6, 6.7, 6.8],
        "cbl_01",
        "D",
    )
    add_channel_bank(
        "center_bottom_right",
        "3/8DR long-ball hex metric lower right",
        "3/8",
        "long-ball hex",
        ["7mm", "8mm", "9mm", "10mm", "11mm", "12mm"],
        [15.0, 15.2, 15.4, 15.6, 15.8, 16.0],
        [7.2, 7.4, 7.6, 7.8, 8.0, 8.2],
        "cbr_01",
        "D",
    )


def extract_reference_candidates(path: Path) -> list[float]:
    mesh = trimesh.load_mesh(path, force="mesh")
    normals = mesh.face_normals
    vertical = np.where(np.abs(normals[:, 2]) < 0.25)[0]
    vertical_set = set(int(i) for i in vertical)
    edges = [
        [int(a), int(b)]
        for a, b in mesh.face_adjacency
        if int(a) in vertical_set and int(b) in vertical_set
    ]
    if not edges:
        return []
    comps = connected_components(np.array(edges), nodes=vertical, min_len=8)
    diameters: list[float] = []
    for comp in comps:
        faces = mesh.faces[np.array(list(comp), dtype=int)].reshape(-1)
        verts = mesh.vertices[faces]
        mn = verts.min(axis=0)
        mx = verts.max(axis=0)
        dx, dy, dz = mx - mn
        if dz < 3 or dx < 5 or dy < 5 or dx > 45 or dy > 45:
            continue
        if max(dx, dy) / max(0.001, min(dx, dy)) > 1.35:
            continue
        diameters.append(round(float((dx + dy) / 2), 2))
    return sorted(diameters)


def collect_reference_summary() -> None:
    reference_summary.clear()
    for path in REFERENCE_PATHS:
        if not path.is_file():
            reference_summary.append({"file": str(path), "missing": True, "diameters": []})
            continue
        diameters = extract_reference_candidates(path)
        reference_summary.append(
            {
                "file": str(path),
                "missing": False,
                "diameters": diameters,
                "unique_diameters": sorted({round(d, 2) for d in diameters}),
                "count": len(diameters),
            }
        )


DIAMETER_RULES = {
    "lt_01": [22.5, 24.5, 26.5, 30.5, 32.5],
    "lt_02": [22.5, 23.5, 24.5, 25.0, 24.5, 25.0, 25.5],
    "lt_03": [20.8, 21.0, 21.2, 21.4, 21.6, 21.8, 22.0, 22.0],
    "lt_04": [22.5, 22.8, 23.2, 23.6, 24.0, 24.5, 25.0],
    "lt_05": [23.0, 23.5, 24.0, 24.5, 25.0, 25.3, 25.5],
    "lb_01": [17.5, 18.5, 20.5, 22.5, 24.5, 26.5],
    "lb_02": [17.5, 18.5, 20.5, 22.5],
    "lb_03": [17.5, 17.8, 18.5, 20.5, 21.5, 22.5, 24.5],
    "lb_04": [15.2, 15.4, 15.6, 15.8, 16.0, 16.2, 16.4, 16.6, 16.8, 17.0],
    "rt_01": [12.5, 14.5, 16.5],
    "rt_02": [12.5, 12.5, 13.0, 13.5, 14.5],
    "rt_03": [12.5, 12.5, 12.5, 13.0, 13.5],
    "rt_04": [13.5, 14.0, 14.5, 15.0, 15.5],
    "rt_05": [12.5, 12.5, 13.0, 13.5, 14.5, 15.5],
    "rt_06": [14.0, 15.0, 14.5, 13.0, 13.5, 14.0],
    "rt_07": [12.5, 12.5, 12.5, 13.0, 13.3, 13.6, 13.8, 14.0],
    "rb_01": [17.0, 17.8, 18.5, 19.2, 20.5],
    "rb_02": [21.2, 21.8, 22.5, 23.2],
    "rb_03": [16.8, 17.4, 18.0, 18.6, 19.2],
    "rb_04": [20.4, 21.0, 21.8, 22.6, 23.4],
    "rb_05": [18.6, 20.5, 17.2, 18.4, 19.6],
    "rb_06": [17.8, 18.8, 19.8, 19.2, 20.2],
}


def apply_reference_diameter_updates() -> None:
    by_row: dict[str, list[dict]] = defaultdict(list)
    for row in inventory:
        if row["kind"] == "cup":
            by_row[row["row_id"]].append(row)
    for row_id, values in DIAMETER_RULES.items():
        rows = by_row.get(row_id, [])
        if len(rows) != len(values):
            raise RuntimeError(f"diameter rule mismatch for {row_id}: {len(rows)} rows, {len(values)} values")
        for row, new_value in zip(rows, values):
            old_value = float(row["pocket_diameter"])
            if abs(old_value - new_value) > 0.001:
                diameter_changes.append(
                    {
                        "sort_order": row["sort_order"],
                        "module_name": row["module_name"],
                        "row_id": row_id,
                        "display_label": row["display_label"],
                        "old_diameter": old_value,
                        "new_diameter": new_value,
                        "basis": "free STL reference diameter band constrained to v04 layout",
                    }
                )
                row["pocket_diameter"] = new_value


def reflow_row_positions() -> None:
    by_module_row: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in inventory:
        by_module_row[(row["module_name"], row["row_id"])].append(row)
    for (module_name, _row_id), rows in by_module_row.items():
        rows.sort(key=lambda item: item["sort_order"])
        labels = [row["display_label"] for row in rows]
        diameters = [float(row["pocket_diameter"]) for row in rows]
        xs = row_positions(module_name, labels, diameters)
        for row, x in zip(rows, xs):
            if row["kind"] == "channel":
                dx = x - float(row["x"])
                row["channel_x1"] = round(float(row["channel_x1"]) + dx, 3)
                row["channel_x2"] = round(float(row["channel_x2"]) + dx, 3)
                row["end_x"] = round(float(row["end_x"]) + dx, 3)
            row["x"] = round(x, 3)
            row["label_x"] = round(x, 3)


def refresh_label_offsets() -> None:
    for row in inventory:
        if row["kind"] != "cup" or row["module_name"] in {"right_bottom", "right_top"}:
            continue
        side = 1 if float(row["label_y"]) > float(row["y"]) else -1
        clearance = 1.6
        row["label_y"] = round(
            float(row["y"]) + side * (float(row["pocket_diameter"]) / 2 + float(row["label_size"]) / 2 + clearance),
            3,
        )
    for row in inventory:
        if row["kind"] == "channel":
            row["label_y"] = 19.0
        if row["row_id"] == "lt_05":
            row["label_y"] = 5.5
        if row["row_id"] == "lb_04":
            row["label_y"] = 5.5
        if row["row_id"] == "rb_05":
            row["label_y"] = 33.0


def scad_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def item_scad(row: dict) -> str:
    fields = [
        scad_str(row["module_name"]),
        scad_str(row["group_name"]),
        scad_str(row["drive"]),
        scad_str(row["type"]),
        scad_str(row["raw_label"]),
        scad_str(row["display_label"]),
        f'{row["pocket_diameter"]:.3f}',
        f'{row["pocket_depth"]:.3f}',
        scad_str(row["row_id"]),
        str(row["sort_order"]),
        scad_str(row["kind"]),
        f'{row["x"]:.3f}',
        f'{row["y"]:.3f}',
        f'{row["label_x"]:.3f}',
        f'{row["label_y"]:.3f}',
        f'{row["label_rotation"]:.3f}',
        f'{row["label_size"]:.3f}',
        f'{row["channel_width"]:.3f}',
        f'{row["channel_x1"]:.3f}',
        f'{row["channel_y1"]:.3f}',
        f'{row["channel_x2"]:.3f}',
        f'{row["channel_y2"]:.3f}',
        f'{row["end_x"]:.3f}',
        f'{row["end_y"]:.3f}',
    ]
    return "    [" + ", ".join(fields) + "]"


def module_scad() -> str:
    module_rows = []
    for name, data in MODULES.items():
        module_rows.append(
            f'    [{scad_str(name)}, {data["w"]:.3f}, {data["d"]:.3f}, {data["ox"]:.3f}, {data["oy"]:.3f}, {data["index"]}]'
        )
    return ",\n".join(module_rows)


def build_scad() -> str:
    rows = ",\n".join(item_scad(row) for row in inventory)
    modules = module_scad()
    scad = f'''// project_stem: kobalt_81798_socket_organizer
// version: v04
// task_mode: reference_based_reconstruction
// v04 corrective rebuild: free-STL-informed pocket diameters plus interlocking shiplap tab seams.
// Units: millimeters. Z+ is up. OpenSCAD remains the source of truth.

$fn = 48;

project_version = "v04";
render_mode = "reference_layout";
render_mode_index = 0;
render_mode_index_override = -1;
// 0 reference_layout
// 1 left_top_body, 2 left_top_labels, 3 left_bottom_body, 4 left_bottom_labels
// 5 center_top_left_body, 6 center_top_left_labels
// 7 center_top_right_body, 8 center_top_right_labels
// 9 center_bottom_left_body, 10 center_bottom_left_labels
// 11 center_bottom_right_body, 12 center_bottom_right_labels
// 13 right_top_body, 14 right_top_labels, 15 right_bottom_body, 16 right_bottom_labels
// 17 fit_test_plate_body, 18 fit_test_plate_labels

overall_width = {OVERALL_W:.3f};
overall_depth = {OVERALL_D:.3f};
base_thickness = {BASE_T:.3f};
safe_build_max = {SAFE_MAX:.3f};
printer_build = [256, 256, 256];
min_floor = 2.5;
min_web = 2.5;
edge_margin = 5.0;
pocket_chamfer = 1.0;
label_height = {LABEL_HEIGHT:.3f};
label_font = "Liberation Sans:style=Bold";
label_size_min = 5.0;
long_channel_depth = 4.0;
lip_height = 0.8;
lip_width = 1.2;
rib_height = 0.65;
rib_width = 1.4;
seam_lap_width = 8.0;
seam_clearance = 0.25;

// Inventory field indices.
F_MODULE = 0;
F_GROUP = 1;
F_DRIVE = 2;
F_TYPE = 3;
F_RAW_LABEL = 4;
F_DISPLAY_LABEL = 5;
F_POCKET_DIAMETER = 6;
F_POCKET_DEPTH = 7;
F_ROW_ID = 8;
F_SORT_ORDER = 9;
F_KIND = 10;
F_X = 11;
F_Y = 12;
F_LABEL_X = 13;
F_LABEL_Y = 14;
F_LABEL_ROT = 15;
F_LABEL_SIZE = 16;
F_CHANNEL_WIDTH = 17;
F_CHANNEL_X1 = 18;
F_CHANNEL_Y1 = 19;
F_CHANNEL_X2 = 20;
F_CHANNEL_Y2 = 21;
F_END_X = 22;
F_END_Y = 23;

// Machine-readable v04 inventory. Every storage row has explicit diameter data.
inventory = [
{rows}
];

module_table = [
{modules}
];

function selected_mode() = render_mode_index_override >= 0 ? render_mode_index_override : render_mode_index;
function count_kind(kind, i = 0) = i >= len(inventory) ? 0 : (inventory[i][F_KIND] == kind ? 1 : 0) + count_kind(kind, i + 1);
function module_w(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][1] : module_w(name, i + 1);
function module_d(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][2] : module_d(name, i + 1);
function module_ox(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][3] : module_ox(name, i + 1);
function module_oy(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][4] : module_oy(name, i + 1);

assert(len(inventory) == 153, str("Storage count must be 153, got ", len(inventory)));
assert(count_kind("cup") == 128, str("Circular pocket count must be 128, got ", count_kind("cup")));
assert(count_kind("channel") == 25, str("Long channel count must be 25, got ", count_kind("channel")));

module rounded_panel(w, d) {{
    cube([w, d, base_thickness]);
}}

module perimeter_lip(w, d) {{
    translate([0, 0, base_thickness]) cube([w, lip_width, lip_height]);
    translate([0, d - lip_width, base_thickness]) cube([w, lip_width, lip_height]);
    translate([0, 0, base_thickness]) cube([lip_width, d, lip_height]);
    translate([w - lip_width, 0, base_thickness]) cube([lip_width, d, lip_height]);
}}

module divider_ribs(module_name) {{
    w = module_w(module_name);
    d = module_d(module_name);
    if (module_name == "left_top") {{
        for (y = [80, 120, 158]) translate([6, y, base_thickness]) cube([w - 12, rib_width, rib_height]);
    }} else if (module_name == "left_bottom") {{
        for (y = [36, 68, 100]) translate([6, y, base_thickness]) cube([w - 12, rib_width, rib_height]);
    }} else if (module_name == "right_top") {{
        for (y = [24, 45, 66, 87, 108, 129]) translate([5, y, base_thickness]) cube([w - 10, rib_width, rib_height]);
    }} else if (module_name == "right_bottom") {{
        for (y = [32, 60, 88, 116, 146]) translate([5, y, base_thickness]) cube([w - 10, rib_width, rib_height]);
    }} else if (module_name == "center_top_left" || module_name == "center_top_right" || module_name == "center_bottom_left" || module_name == "center_bottom_right") {{
        translate([4, 24, base_thickness]) cube([w - 8, rib_width, rib_height]);
        translate([4, 136, base_thickness]) cube([w - 8, rib_width, rib_height]);
    }}
}}

module socket_cup_cut(x, y, diameter, depth) {{
    translate([x, y, base_thickness - depth - 0.02])
        cylinder(h = depth + 0.05, d = diameter);
    translate([x, y, base_thickness - pocket_chamfer])
        cylinder(h = pocket_chamfer + 0.08, d1 = diameter, d2 = diameter + 2 * pocket_chamfer);
}}

module socket_cup(x, y, diameter, depth) {{
    socket_cup_cut(x, y, diameter, depth);
}}

module long_bit_channel_cut(x1, y1, x2, y2, width, depth) {{
    translate([0, 0, base_thickness - depth - 0.02])
        hull() {{
            translate([x1, y1, 0]) cylinder(h = depth + 0.05, d = width);
            translate([x2, y2, 0]) cylinder(h = depth + 0.05, d = width);
        }}
    translate([0, 0, base_thickness - pocket_chamfer])
        hull() {{
            translate([x1, y1, 0]) cylinder(h = pocket_chamfer + 0.08, d = width + 2 * pocket_chamfer);
            translate([x2, y2, 0]) cylinder(h = pocket_chamfer + 0.08, d = width + 2 * pocket_chamfer);
        }}
}}

module long_bit_channel(x1, y1, x2, y2, width, depth) {{
    long_bit_channel_cut(x1, y1, x2, y2, width, depth);
}}

module label_text(txt, x, y, rot = 0, size = 5.5) {{
    translate([x, y, base_thickness])
        rotate([0, 0, rot])
            linear_extrude(height = label_height)
                text(txt, size = size, font = label_font, halign = "center", valign = "center");
}}

module module_cuts(module_name) {{
    for (item = inventory) {{
        if (item[F_MODULE] == module_name && item[F_KIND] == "cup") {{
            socket_cup_cut(item[F_X], item[F_Y], item[F_POCKET_DIAMETER], item[F_POCKET_DEPTH]);
        }}
        if (item[F_MODULE] == module_name && item[F_KIND] == "channel") {{
            long_bit_channel_cut(item[F_CHANNEL_X1], item[F_CHANNEL_Y1], item[F_CHANNEL_X2], item[F_CHANNEL_Y2], item[F_CHANNEL_WIDTH], long_channel_depth);
            socket_cup_cut(item[F_END_X], item[F_END_Y], item[F_POCKET_DIAMETER], item[F_POCKET_DEPTH]);
        }}
    }}
}}

module module_labels(module_name) {{
    color([0.95, 0.08, 0.03])
        for (item = inventory) {{
            if (item[F_MODULE] == module_name) {{
                label_text(item[F_DISPLAY_LABEL], item[F_LABEL_X], item[F_LABEL_Y], item[F_LABEL_ROT], item[F_LABEL_SIZE]);
            }}
        }}
}}

module module_body(module_name) {{
    w = module_w(module_name);
    d = module_d(module_name);
    assert(w <= safe_build_max && d <= safe_build_max, str("Build-volume fail before top detail: ", module_name));
    color([0.08, 0.20, 0.90])
        difference() {{
            union() {{
                rounded_panel(w, d);
                perimeter_lip(w, d);
                divider_ribs(module_name);
            }}
            module_cuts(module_name);
        }}
}}

module zone_grid(module_name) {{
    module_body(module_name);
}}

module puzzle_key_edge() {{
    // Placeholder helper kept parametric for future underside keys; v03 avoids protruding seam geometry to preserve build-volume bounds.
    cube([0.01, 0.01, 0.01]);
}}

module module_combined(module_name) {{
    module_body(module_name);
    module_labels(module_name);
}}

module module_left_top(part = "combined") {{
    if (part == "body") module_body("left_top"); else if (part == "labels") module_labels("left_top"); else module_combined("left_top");
}}
module module_left_bottom(part = "combined") {{
    if (part == "body") module_body("left_bottom"); else if (part == "labels") module_labels("left_bottom"); else module_combined("left_bottom");
}}
module module_center_top_left(part = "combined") {{
    if (part == "body") module_body("center_top_left"); else if (part == "labels") module_labels("center_top_left"); else module_combined("center_top_left");
}}
module module_center_top_right(part = "combined") {{
    if (part == "body") module_body("center_top_right"); else if (part == "labels") module_labels("center_top_right"); else module_combined("center_top_right");
}}
module module_center_bottom_left(part = "combined") {{
    if (part == "body") module_body("center_bottom_left"); else if (part == "labels") module_labels("center_bottom_left"); else module_combined("center_bottom_left");
}}
module module_center_bottom_right(part = "combined") {{
    if (part == "body") module_body("center_bottom_right"); else if (part == "labels") module_labels("center_bottom_right"); else module_combined("center_bottom_right");
}}
module module_right_top(part = "combined") {{
    if (part == "body") module_body("right_top"); else if (part == "labels") module_labels("right_top"); else module_combined("right_top");
}}
module module_right_bottom(part = "combined") {{
    if (part == "body") module_body("right_bottom"); else if (part == "labels") module_labels("right_bottom"); else module_combined("right_bottom");
}}

module fit_test_plate_body() {{
    ft_w = {FIT_TEST["w"]:.3f};
    ft_d = {FIT_TEST["d"]:.3f};
    color([0.08, 0.20, 0.90])
        difference() {{
            union() {{
                rounded_panel(ft_w, ft_d);
                perimeter_lip(ft_w, ft_d);
            }}
            socket_cup_cut(20, 62, 11.2, 5.5);
            socket_cup_cut(54, 62, 15.4, 5.5);
            socket_cup_cut(91, 62, 16.5, 6.5);
            socket_cup_cut(129, 62, 23.4, 6.5);
            socket_cup_cut(171, 62, 22.0, 7.5);
            socket_cup_cut(211, 62, 29.0, 7.5);
            long_bit_channel_cut(62, 18, 160, 18, 7.8, 4.0);
            socket_cup_cut(174, 18, 19.4, 6.5);
        }}
}}

module fit_test_plate_labels() {{
    color([0.95, 0.08, 0.03]) {{
        label_text("QSM", 20, 39, 0, 6.5);
        label_text("QLG", 54, 39, 0, 6.5);
        label_text("DSM", 91, 39, 0, 6.5);
        label_text("DLG", 129, 39, 0, 6.5);
        label_text("HSM", 171, 39, 0, 6.5);
        label_text("HLG", 211, 39, 0, 6.5);
        label_text("LONG", 111, 8, 0, 6.5);
    }}
}}

module full_reference_layout() {{
    for (m = module_table) {{
        translate([m[3], m[4], 0]) module_combined(m[0]);
    }}
}}

module reference_layout() {{
    full_reference_layout();
}}

mode = selected_mode();

if (mode == 1 || render_mode == "left_top_body") {{
    module_left_top("body");
}} else if (mode == 2 || render_mode == "left_top_labels") {{
    module_left_top("labels");
}} else if (mode == 3 || render_mode == "left_bottom_body") {{
    module_left_bottom("body");
}} else if (mode == 4 || render_mode == "left_bottom_labels") {{
    module_left_bottom("labels");
}} else if (mode == 5 || render_mode == "center_top_left_body") {{
    module_center_top_left("body");
}} else if (mode == 6 || render_mode == "center_top_left_labels") {{
    module_center_top_left("labels");
}} else if (mode == 7 || render_mode == "center_top_right_body") {{
    module_center_top_right("body");
}} else if (mode == 8 || render_mode == "center_top_right_labels") {{
    module_center_top_right("labels");
}} else if (mode == 9 || render_mode == "center_bottom_left_body") {{
    module_center_bottom_left("body");
}} else if (mode == 10 || render_mode == "center_bottom_left_labels") {{
    module_center_bottom_left("labels");
}} else if (mode == 11 || render_mode == "center_bottom_right_body") {{
    module_center_bottom_right("body");
}} else if (mode == 12 || render_mode == "center_bottom_right_labels") {{
    module_center_bottom_right("labels");
}} else if (mode == 13 || render_mode == "right_top_body") {{
    module_right_top("body");
}} else if (mode == 14 || render_mode == "right_top_labels") {{
    module_right_top("labels");
}} else if (mode == 15 || render_mode == "right_bottom_body") {{
    module_right_bottom("body");
}} else if (mode == 16 || render_mode == "right_bottom_labels") {{
    module_right_bottom("labels");
}} else if (mode == 17 || render_mode == "fit_test_plate_body") {{
    fit_test_plate_body();
}} else if (mode == 18 || render_mode == "fit_test_plate_labels") {{
    fit_test_plate_labels();
}} else {{
    reference_layout();
}}
'''
    return apply_v04_scad_patches(scad)


def apply_v04_scad_patches(scad: str) -> str:
    old = '''module module_body(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    assert(w <= safe_build_max && d <= safe_build_max, str("Build-volume fail before top detail: ", module_name));
    color([0.08, 0.20, 0.90])
        difference() {
            union() {
                rounded_panel(w, d);
                perimeter_lip(w, d);
                divider_ribs(module_name);
            }
            module_cuts(module_name);
        }
}
'''
    new = '''vertical_seam_segments = [
    [22, 54], [82, 114], [142, 174], [202, 234], [262, 294], [306, 326]
];
horizontal_seam_segments = [
    [22, 60], [88, 126], [154, 192], [238, 270], [300, 332], [362, 394], [424, 462], [496, 532], [562, 600]
];

function has_east_tongue(name) = name == "left_top" || name == "left_bottom" || name == "center_top_left" || name == "center_bottom_left" || name == "center_top_right" || name == "center_bottom_right";
function has_west_socket(name) = name == "center_top_left" || name == "center_bottom_left" || name == "center_top_right" || name == "center_bottom_right" || name == "right_top" || name == "right_bottom";
function has_north_tongue(name) = name == "left_bottom" || name == "center_bottom_left" || name == "center_bottom_right";
function has_south_socket(name) = name == "left_top" || name == "center_top_left" || name == "center_top_right";
function has_south_tongue(name) = name == "right_top";
function has_north_socket(name) = name == "right_bottom";

module seam_tongues(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    ox = module_ox(module_name);
    oy = module_oy(module_name);
    if (has_east_tongue(module_name)) {
        for (seg = vertical_seam_segments) {
            y0 = max(0, seg[0] - oy);
            y1 = min(d, seg[1] - oy);
            if (y1 - y0 > 10)
                translate([w, y0, 0]) cube([seam_lap_width, y1 - y0, base_thickness]);
        }
    }
    if (has_north_tongue(module_name)) {
        for (seg = horizontal_seam_segments) {
            x0 = max(0, seg[0] - ox);
            x1 = min(w, seg[1] - ox);
            if (x1 - x0 > 10)
                translate([x0, d, 0]) cube([x1 - x0, seam_lap_width, base_thickness]);
        }
    }
    if (has_south_tongue(module_name)) {
        for (seg = horizontal_seam_segments) {
            x0 = max(0, seg[0] - ox);
            x1 = min(w, seg[1] - ox);
            if (x1 - x0 > 10)
                translate([x0, -seam_lap_width, 0]) cube([x1 - x0, seam_lap_width, base_thickness]);
        }
    }
}

module seam_socket_cuts(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    ox = module_ox(module_name);
    oy = module_oy(module_name);
    if (has_west_socket(module_name)) {
        for (seg = vertical_seam_segments) {
            y0 = max(0, seg[0] - oy);
            y1 = min(d, seg[1] - oy);
            if (y1 - y0 > 10)
                translate([-0.02, y0 - seam_clearance, -0.02])
                    cube([seam_lap_width + seam_clearance + 0.04, y1 - y0 + 2 * seam_clearance, base_thickness + lip_height + 0.08]);
        }
    }
    if (has_south_socket(module_name)) {
        for (seg = horizontal_seam_segments) {
            x0 = max(0, seg[0] - ox);
            x1 = min(w, seg[1] - ox);
            if (x1 - x0 > 10)
                translate([x0 - seam_clearance, -0.02, -0.02])
                    cube([x1 - x0 + 2 * seam_clearance, seam_lap_width + seam_clearance + 0.04, base_thickness + lip_height + 0.08]);
        }
    }
    if (has_north_socket(module_name)) {
        for (seg = horizontal_seam_segments) {
            x0 = max(0, seg[0] - ox);
            x1 = min(w, seg[1] - ox);
            if (x1 - x0 > 10)
                translate([x0 - seam_clearance, d - seam_lap_width - seam_clearance, -0.02])
                    cube([x1 - x0 + 2 * seam_clearance, seam_lap_width + seam_clearance + 0.04, base_thickness + lip_height + 0.08]);
        }
    }
}

module module_body(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    assert(w + seam_lap_width <= safe_build_max && d + seam_lap_width <= safe_build_max, str("Build-volume fail with seam overlap: ", module_name));
    color([0.08, 0.20, 0.90])
        difference() {
            union() {
                rounded_panel(w, d);
                seam_tongues(module_name);
                perimeter_lip(w, d);
                divider_ribs(module_name);
            }
            seam_socket_cuts(module_name);
            module_cuts(module_name);
        }
}
'''
    if old not in scad:
        raise RuntimeError("could not patch module_body for v04 seam geometry")
    return scad.replace(old, new)


def write_notes() -> None:
    body_exports = "\n".join(
        f"- exports/kobalt_81798_socket_organizer_v04_{name}_body.stl\n"
        f"- exports/kobalt_81798_socket_organizer_v04_{name}_labels.stl"
        for name in MODULES
    )
    changed_rows = "\n".join(
        f"- {c['module_name']} {c['row_id']} {c['display_label']}: {c['old_diameter']:.2f} -> {c['new_diameter']:.2f} mm"
        for c in diameter_changes
    )
    ref_rows = "\n".join(
        f"- {Path(item['file']).name}: {item.get('count', 0)} circular candidates; unique diameters {item.get('unique_diameters', [])}"
        for item in reference_summary
    )
    NOTES.write_text(
        f"""# Kobalt 81798 Socket Organizer v04 Notes

Task mode: `reference_based_reconstruction`

Target part: Kobalt 81798 / Lowe's item 4103169 153-piece socket and bit-driver organizer.

v04 is a corrective rebuild from v03. It keeps the original modular organizer concept and separate AMS-ready label STLs while adding reference-informed pocket diameters and interlocking overlap seams.

## What Is Reused

- User's actual Kobalt sockets and bit-driver sockets.
- Lowe's official set identity and inventory count.
- User screenshots as supporting footprint and grouping references only.

## What Is Not Modeled

- The metal sockets or bits.
- Kobalt logo artwork.
- ZLL Designs logo, Etsy branding, seller marks, or copied decorative artwork.
- Toolbox, drawer, case, packaging, or paid STL geometry.

## Locked Dimensions

- Overall reference footprint: 621.03 x 332.74 mm.
- Base thickness: 12.70 mm.
- Bambu Lab P2S build volume: 256 x 256 x 256 mm.
- Safe module target: 245 x 245 mm.
- Split modules: left_top, left_bottom, center_top_left, center_top_right, center_bottom_left, center_bottom_right, right_top, right_bottom.

## Reference Diameter Upgrade

The uploaded free socket organizer STLs and Gridfinity Kobalt socket STL were scanned for circular pocket wall components. Their diameters were used as dimensional baselines, then constrained to the Kobalt 81798 compact layout where needed.

## v04 Corrections

- Free STL reference pocket diameters incorporated into 1/4, 3/8, and 1/2 circular cup rows.
- Separate aligned label STLs retained for AMS/two-color printing.
- right_bottom label issue remains fixed.
- Interlocking shiplap-style tab/socket seams added to every touching module boundary.
- Seam features are full-height, support-free, and self-locating.
- Center long-bit layout remains 12 upper channels and 13 lower channels.

## Pocket Clearance Assumptions

- 1/4 drive pockets use 5.5 mm depth.
- 3/8 drive pockets use 6.5 mm depth.
- 1/2 drive pockets use 7.5 mm depth.
- Long-bit channels use 4.0 mm depth.
- Hole sizing remains printer/material dependent.
- Seam lap width: 8.0 mm.
- Seam clearance: 0.25 mm.

## Required Exports

{body_exports}

## Fit Warning

Do not treat v04 as guaranteed first-print fit. Caliper measurements of the actual Kobalt sockets still override every STL-derived estimate.
""",
        encoding="utf-8",
    )
    DIAMETER_LOG.write_text(
        f"""# Kobalt 81798 Socket Organizer v04 Reference Diameter Log

## Reference STL Circular Candidate Summary

{ref_rows}

## Diameter Values Changed From v03

{changed_rows}

## Interpretation

The extracted diameters are reference tray pocket wall candidates. Many source STLs contain stepped holes, so v04 uses them as fit bands rather than copying the source tray geometry.
""",
        encoding="utf-8",
    )
    SEAM_NOTES.write_text(
        """# Kobalt 81798 Socket Organizer v04 Seam Design Notes

Seam type: segmented shiplap/rabbet overlap using full-height rectangular tabs and matching sockets.

- Lap width: 8.0 mm.
- Clearance: 0.25 mm.
- The features print flat without supports because the tabs are full-height side geometry, not unsupported top shelves.
- Vertical seams use east-side tongues mating into west-side sockets.
- Horizontal seams mostly use bottom-module north tongues mating into top-module south sockets.
- The right-side horizontal seam reverses orientation: right_top has south tongues and right_bottom has north sockets to avoid the fixed right_top label area.
- Every touching boundary has at least two registered overlap segments.
- No snap latch geometry is used.
- No branding or source STL geometry is copied.
""",
        encoding="utf-8",
    )
    MANIFEST.write_text(
        """---
project_stem: kobalt_81798_socket_organizer
version: v04
task_mode: reference_based_reconstruction
source_file: source/kobalt_81798_socket_organizer_v04.scad
inventory_file: notes/kobalt_81798_socket_organizer_v04_inventory.json
status: generated pending validation
---

# Kobalt 81798 Socket Organizer v04 Manifest

v04 exports body and label STLs as aligned parts for color-ready slicer import and adds shiplap/rabbet seam registration.
""",
        encoding="utf-8",
    )
    REVIEW.write_text(
        """# Kobalt 81798 Socket Organizer v04 Review Report

Pending final export and `tools/validate_v04.py`.
""",
        encoding="utf-8",
    )
    (PROJECT / "notes" / "project_manifest.md").write_text(
        """# Project Manifest

Project: kobalt_81798_socket_organizer

Versions present: v01, v02, v03, v03b fit test, v04.

Current corrective version: v04.
""",
        encoding="utf-8",
    )


def main() -> int:
    PROJECT.joinpath("source").mkdir(exist_ok=True)
    PROJECT.joinpath("notes").mkdir(exist_ok=True)
    PROJECT.joinpath("exports").mkdir(exist_ok=True)
    PROJECT.joinpath("previews").mkdir(exist_ok=True)
    PROJECT.joinpath("tools").mkdir(exist_ok=True)

    collect_reference_summary()
    normalize_base_rows()
    add_center_v03_channels()
    apply_reference_diameter_updates()
    reflow_row_positions()
    refresh_label_offsets()

    circular = sum(1 for row in inventory if row["kind"] == "cup")
    channels = sum(1 for row in inventory if row["kind"] == "channel")
    if len(inventory) != 153:
        raise RuntimeError(f"inventory count is {len(inventory)}, expected 153")
    if circular != 128:
        raise RuntimeError(f"circular cup count is {circular}, expected 128")
    if channels != 25:
        raise RuntimeError(f"long channel count is {channels}, expected 25")

    SOURCE.write_text(build_scad(), encoding="utf-8")
    INVENTORY_JSON.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    DIAMETER_CHANGES_JSON.write_text(json.dumps(diameter_changes, indent=2), encoding="utf-8")
    write_notes()
    print(f"Wrote {SOURCE}")
    print(f"Wrote {INVENTORY_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
