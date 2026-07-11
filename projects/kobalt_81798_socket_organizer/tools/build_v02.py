from __future__ import annotations

import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
SOURCE = PROJECT / "source" / "kobalt_81798_socket_organizer_v02.scad"
INVENTORY_JSON = PROJECT / "notes" / "kobalt_81798_socket_organizer_v02_inventory.json"
NOTES = PROJECT / "notes" / "kobalt_81798_socket_organizer_v02_notes.md"
MANIFEST = PROJECT / "notes" / "kobalt_81798_socket_organizer_v02_manifest.md"
COMPARISON = PROJECT / "notes" / "kobalt_81798_socket_organizer_v02_reference_comparison_log.md"
REVIEW = PROJECT / "notes" / "kobalt_81798_socket_organizer_v02_review_report.md"
PRINTABILITY = PROJECT / "notes" / "kobalt_81798_socket_organizer_v02_printability_review.md"

OVERALL_W = 621.03
OVERALL_D = 332.74
BASE_T = 12.70
SAFE_MAX = 245.0
MIN_WEB = 2.5
EDGE_MARGIN = 5.0

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
LABEL_HEIGHT = 0.6


def display_label(raw: str, drive_prefix: str | None = None) -> str:
    value = raw.upper().replace("MM", "M").replace(".", "_").replace("/", "_")
    value = value.replace(" FLAT", "").replace(" SLOT", "")
    value = value.replace(" ", "")
    if drive_prefix:
        value = f"{drive_prefix}{value}"
    return value


def label_width(label: str, size: float = LABEL_SIZE) -> float:
    return max(1, len(label)) * size * 0.62


inventory: list[dict] = []
sort_order = 1


def row_positions(module_name: str, labels: list[str], diameters: list[float]) -> list[float]:
    mod = MODULES[module_name]
    max_d = max(diameters)
    max_label = max(label_width(label) for label in labels)
    margin = max(EDGE_MARGIN + max_d / 2, max_label / 2 + 3.0, 9.0)
    if len(labels) == 1:
        return [mod["w"] / 2]
    pitch = (mod["w"] - 2 * margin) / (len(labels) - 1)
    if pitch < max_d + MIN_WEB:
        raise ValueError(
            f"Row spacing fail in {module_name}: pitch {pitch:.2f}, diameter {max_d:.2f}"
        )
    return [round(margin + i * pitch, 3) for i in range(len(labels))]


def add_cup_row(
    module_name: str,
    group_name: str,
    drive: str,
    type_name: str,
    raw_labels: list[str],
    diameters: list[float],
    row_id: str,
    y: float,
    label_side: int = -1,
) -> None:
    global sort_order
    if len(raw_labels) != len(diameters):
        raise ValueError(f"Diameter count mismatch for {group_name}")
    labels = [display_label(raw) for raw in raw_labels]
    xs = row_positions(module_name, labels, diameters)
    depth = DEPTH_BY_DRIVE[drive]
    for raw, label, diameter, x in zip(raw_labels, labels, diameters, xs):
        radius = diameter / 2
        label_y = y + label_side * (radius + LABEL_SIZE / 2 + 1.1)
        inventory.append(
            {
                "module_name": module_name,
                "group_name": group_name,
                "drive": drive,
                "type": type_name,
                "raw_label": raw,
                "display_label": label,
                "pocket_diameter": diameter,
                "pocket_depth": depth,
                "row_id": row_id,
                "sort_order": sort_order,
                "kind": "cup",
                "x": round(x, 3),
                "y": round(y, 3),
                "label_x": round(x, 3),
                "label_y": round(label_y, 3),
                "label_rotation": 0,
                "label_size": LABEL_SIZE,
                "channel_width": 0.0,
                "channel_x1": 0.0,
                "channel_y1": 0.0,
                "channel_x2": 0.0,
                "channel_y2": 0.0,
                "end_x": round(x, 3),
                "end_y": round(y, 3),
            }
        )
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
    mod = MODULES[module_name]
    drives = drive if isinstance(drive, list) else [drive] * len(raw_labels)
    prefixes = drive_prefix if isinstance(drive_prefix, list) else [drive_prefix] * len(raw_labels)
    labels = [display_label(raw, prefix) for raw, prefix in zip(raw_labels, prefixes)]
    xs = row_positions(module_name, labels, end_diameters)
    y1 = 34.0
    y2 = 130.0
    end_y = 146.0
    for raw, label, diameter, width, x, item_drive in zip(raw_labels, labels, end_diameters, channel_widths, xs, drives):
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
                "label_y": 17.0,
                "label_rotation": 90,
                "label_size": LABEL_SIZE,
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


# LEFT_TOP: all 1/2 drive groups, split so large pockets remain visibly different and printable.
add_cup_row("left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE",
            ["5/8", "11/16", "3/4", "13/16", "7/8"],
            [22.5, 23.3, 24.0, 24.8, 25.5], "lt_01", 178.0)
add_cup_row("left_top", "1/2DR external Torx and Torx", "1/2", "external/torx",
            ["E18", "E20", "E22", "E24", "T55", "T60", "T70"],
            [21.2, 22.0, 22.8, 23.6, 22.8, 23.8, 24.8], "lt_02", 139.0)
add_cup_row("left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket",
            ["5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "11/16", "3/4"],
            [20.8, 21.2, 21.8, 22.3, 22.8, 23.2, 23.6, 24.0], "lt_03", 100.0)
add_cup_row("left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket",
            ["6mm", "7mm", "8mm", "9mm", "10mm", "11mm", "12mm"],
            [20.8, 21.2, 21.6, 22.0, 22.5, 23.0, 23.5], "lt_04", 61.0)
add_cup_row("left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket",
            ["13mm", "14mm", "15mm", "16mm", "17mm", "18mm", "19mm"],
            [22.8, 23.2, 23.6, 24.0, 24.4, 24.8, 25.2], "lt_05", 22.0, label_side=1)

# LEFT_BOTTOM: selected 3/8 drive shallow, external, and short hex groups.
add_cup_row("left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE",
            ["1/4", "5/16", "3/8", "7/16", "1/2", "9/16"],
            [16.0, 16.8, 17.6, 18.4, 19.2, 20.0], "lb_01", 116.0)
add_cup_row("left_bottom", "3/8DR external Torx", "3/8", "external Torx",
            ["E10", "E12", "E14", "E16"],
            [15.8, 17.0, 18.2, 19.4], "lb_02", 84.0)
add_cup_row("left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket",
            ["1/8", "5/32", "3/16", "7/32", "1/4", "5/16", "3/8"],
            [15.5, 16.0, 16.6, 17.2, 18.0, 18.8, 19.6], "lb_03", 52.0)
add_cup_row("left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket",
            ["3mm", "4mm", "5mm", "6mm", "7mm", "8mm", "9mm", "10mm", "11mm", "12mm"],
            [14.8, 15.2, 15.6, 16.0, 16.4, 16.8, 17.2, 17.5, 17.8, 18.0], "lb_04", 20.0, label_side=1)

# RIGHT_TOP: all 1/4 drive non-long groups.
add_cup_row("right_top", "1/4DR 8-point shallow SAE", "1/4", "8-point shallow SAE",
            ["1/4", "5/16", "3/8"],
            [13.2, 14.3, 15.4], "rt_01", 140.0, label_side=1)
add_cup_row("right_top", "1/4DR external Torx", "1/4", "external Torx",
            ["E4", "E5", "E6", "E7", "E8"],
            [11.6, 12.2, 12.8, 13.4, 14.0], "rt_02", 119.0)
add_cup_row("right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket",
            ["1/16", "5/64", "3/32", "7/64", "1/8"],
            [10.8, 11.2, 11.8, 12.4, 13.0], "rt_03", 98.0)
add_cup_row("right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket",
            ["9/64", "5/32", "3/16", "7/32", "1/4"],
            [13.2, 13.6, 14.0, 14.5, 15.0], "rt_04", 77.0, label_side=1)
add_cup_row("right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket",
            ["2mm", "2.5mm", "3mm", "4mm", "5mm", "6mm"],
            [11.0, 11.6, 12.2, 13.0, 13.8, 14.6], "rt_05", 56.0)
add_cup_row("right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket",
            ["7/32 slot", "1/4 slot", "PH3", "S1", "S2", "PZ1"],
            [13.8, 14.6, 14.2, 12.8, 13.4, 13.8], "rt_06", 35.0)
add_cup_row("right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket",
            ["T8", "T9", "T10", "T15", "T20", "T25", "T27", "T30"],
            [11.2, 11.6, 12.0, 12.6, 13.2, 13.8, 14.1, 14.4], "rt_07", 14.0)

# RIGHT_BOTTOM: remaining 3/8 drive Torx, tamper-proof Torx, and screwdriver groups.
add_cup_row("right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket",
            ["T20", "T25", "T27", "T30", "T40"],
            [17.0, 17.8, 18.5, 19.2, 20.5], "rb_01", 160.0)
add_cup_row("right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket",
            ["T45", "T47", "T50", "T55"],
            [21.2, 21.8, 22.5, 23.2], "rb_02", 130.0)
add_cup_row("right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket",
            ["TT15", "TT20", "TT25", "TT27", "TT30"],
            [16.8, 17.4, 18.0, 18.6, 19.2], "rb_03", 100.0)
add_cup_row("right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket",
            ["TT40", "TT45", "TT50", "TT55", "TT60"],
            [20.4, 21.0, 21.8, 22.6, 23.4], "rb_04", 70.0)
add_cup_row("right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket",
            ["9/32 flat", "3/8 flat", "4mm flat", "5mm flat", "6mm flat"],
            [18.6, 20.5, 17.2, 18.4, 19.6], "rb_05", 40.0, label_side=1)
add_cup_row("right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket",
            ["PH1", "PH2", "PH3", "PZ2", "PZ3"],
            [17.8, 18.8, 19.8, 19.2, 20.2], "rb_06", 18.0)

# CENTER: all 25 long-ball hex drivers.
add_channel_bank("center_top_left", "1/4DR long-ball hex SAE and metric", "1/4", "long-ball hex",
                 ["1/8", "5/32", "3/16", "7/32", "3mm", "4mm", "5mm"],
                 [12.4, 12.8, 13.1, 13.5, 13.0, 13.4, 13.8],
                 [6.7, 6.8, 6.9, 7.0, 6.8, 7.0, 7.2], "ctl_01", "Q")
add_channel_bank("center_top_right", "1/4DR and 3/8DR long-ball hex transition",
                 ["1/4", "3/8", "3/8", "3/8", "3/8", "3/8"], "long-ball hex",
                 ["6mm", "1/8", "5/32", "3/16", "7/32", "1/4"],
                 [14.2, 15.2, 15.8, 16.4, 17.0, 17.3],
                 [7.3, 7.0, 7.1, 7.2, 7.3, 7.5], "ctr_01",
                 ["Q", "D", "D", "D", "D", "D"])
add_channel_bank("center_bottom_left", "3/8DR long-ball hex SAE and metric small", "3/8", "long-ball hex",
                 ["5/16", "3/8", "3mm", "4mm", "5mm", "6mm"],
                 [16.4, 17.2, 15.4, 15.8, 16.2, 16.6],
                 [7.7, 7.9, 7.0, 7.1, 7.2, 7.4], "cbl_01", "D")
add_channel_bank("center_bottom_right", "3/8DR long-ball hex metric large", "3/8", "long-ball hex",
                 ["7mm", "8mm", "9mm", "10mm", "11mm", "12mm"],
                 [16.2, 16.4, 16.6, 16.8, 17.0, 17.2],
                 [7.8, 8.0, 8.2, 8.4, 8.6, 8.8], "cbr_01", "D")


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
    return f'''// project_stem: kobalt_81798_socket_organizer
// version: v02
// task_mode: reference_based_reconstruction
// Corrective rebuild: v01 was rejected for near-uniform pockets and unreadable labels.
// Units: millimeters. Z+ is up. OpenSCAD remains the source of truth.

$fn = 40;

project_version = "v02";
render_mode = "reference_layout";
render_mode_index = 0; // 0 reference_layout, 1 left_top, 2 left_bottom, 3 center_top_left, 4 center_top_right, 5 center_bottom_left, 6 center_bottom_right, 7 right_top, 8 right_bottom, 9 fit_test_plate

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
label_size_min = 5.5;
long_channel_depth = 4.0;

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

// Machine-readable v02 inventory. Every storage row has explicit diameter data.
inventory = [
{rows}
];

module_table = [
{modules}
];

function count_kind(kind, i = 0) = i >= len(inventory) ? 0 : (inventory[i][F_KIND] == kind ? 1 : 0) + count_kind(kind, i + 1);
function module_w(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][1] : module_w(name, i + 1);
function module_d(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][2] : module_d(name, i + 1);
function module_ox(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][3] : module_ox(name, i + 1);
function module_oy(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][4] : module_oy(name, i + 1);

assert(len(inventory) == 153, str("Storage count must be 153, got ", len(inventory)));
assert(count_kind("cup") == 128, str("Circular pocket count must be 128, got ", count_kind("cup")));
assert(count_kind("channel") == 25, str("Long channel count must be 25, got ", count_kind("channel")));

module panel(w, d) {{
    cube([w, d, base_thickness]);
}}

module socket_cup_cut(x, y, diameter, depth) {{
    translate([x, y, base_thickness - depth - 0.02])
        cylinder(h = depth + 0.05, d = diameter);
    translate([x, y, base_thickness - pocket_chamfer])
        cylinder(h = pocket_chamfer + 0.08, d1 = diameter, d2 = diameter + 2 * pocket_chamfer);
}}

module rounded_channel_cut(x1, y1, x2, y2, width, depth) {{
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

module raised_label(txt, x, y, rot = 0, size = 5.5) {{
    color([0.02, 0.02, 0.02])
        translate([x, y, base_thickness - 0.03])
            rotate([0, 0, rot])
                linear_extrude(height = label_height + 0.03)
                    text(txt, size = size, font = label_font, halign = "center", valign = "center");
}}

module module_cuts(module_name) {{
    for (item = inventory) {{
        if (item[F_MODULE] == module_name && item[F_KIND] == "cup") {{
            socket_cup_cut(item[F_X], item[F_Y], item[F_POCKET_DIAMETER], item[F_POCKET_DEPTH]);
        }}
        if (item[F_MODULE] == module_name && item[F_KIND] == "channel") {{
            rounded_channel_cut(item[F_CHANNEL_X1], item[F_CHANNEL_Y1], item[F_CHANNEL_X2], item[F_CHANNEL_Y2], item[F_CHANNEL_WIDTH], long_channel_depth);
            socket_cup_cut(item[F_END_X], item[F_END_Y], item[F_POCKET_DIAMETER], item[F_POCKET_DEPTH]);
        }}
    }}
}}

module module_labels(module_name) {{
    for (item = inventory) {{
        if (item[F_MODULE] == module_name) {{
            raised_label(item[F_DISPLAY_LABEL], item[F_LABEL_X], item[F_LABEL_Y], item[F_LABEL_ROT], item[F_LABEL_SIZE]);
        }}
    }}
}}

module organizer_module(module_name) {{
    w = module_w(module_name);
    d = module_d(module_name);
    assert(w <= safe_build_max && d <= safe_build_max, str("Build-volume fail before seam features: ", module_name));
    union() {{
        difference() {{
            panel(w, d);
            module_cuts(module_name);
        }}
        module_labels(module_name);
    }}
}}

module fit_test_plate() {{
    ft_w = {FIT_TEST["w"]:.3f};
    ft_d = {FIT_TEST["d"]:.3f};
    union() {{
        difference() {{
            panel(ft_w, ft_d);
            socket_cup_cut(20, 62, 11.2, 5.5);
            socket_cup_cut(54, 62, 15.4, 5.5);
            socket_cup_cut(91, 62, 16.5, 6.5);
            socket_cup_cut(129, 62, 23.4, 6.5);
            socket_cup_cut(171, 62, 22.0, 7.5);
            socket_cup_cut(211, 62, 29.0, 7.5);
            rounded_channel_cut(62, 18, 160, 18, 7.8, 4.0);
            socket_cup_cut(174, 18, 19.4, 6.5);
        }}
        raised_label("QSM", 20, 39, 0, 6.5);
        raised_label("QLG", 54, 39, 0, 6.5);
        raised_label("DSM", 91, 39, 0, 6.5);
        raised_label("DLG", 129, 39, 0, 6.5);
        raised_label("HSM", 171, 39, 0, 6.5);
        raised_label("HLG", 211, 39, 0, 6.5);
        raised_label("LONG", 111, 8, 0, 6.5);
    }}
}}

module reference_layout() {{
    for (m = module_table) {{
        translate([m[3], m[4], 0]) organizer_module(m[0]);
    }}
}}

if (render_mode_index_override == 1 || render_mode_index == 1 || render_mode == "left_top") {{
    organizer_module("left_top");
}} else if (render_mode_index_override == 2 || render_mode_index == 2 || render_mode == "left_bottom") {{
    organizer_module("left_bottom");
}} else if (render_mode_index_override == 3 || render_mode_index == 3 || render_mode == "center_top_left") {{
    organizer_module("center_top_left");
}} else if (render_mode_index_override == 4 || render_mode_index == 4 || render_mode == "center_top_right") {{
    organizer_module("center_top_right");
}} else if (render_mode_index_override == 5 || render_mode_index == 5 || render_mode == "center_bottom_left") {{
    organizer_module("center_bottom_left");
}} else if (render_mode_index_override == 6 || render_mode_index == 6 || render_mode == "center_bottom_right") {{
    organizer_module("center_bottom_right");
}} else if (render_mode_index_override == 7 || render_mode_index == 7 || render_mode == "right_top") {{
    organizer_module("right_top");
}} else if (render_mode_index_override == 8 || render_mode_index == 8 || render_mode == "right_bottom") {{
    organizer_module("right_bottom");
}} else if (render_mode_index_override == 9 || render_mode_index == 9 || render_mode == "fit_test_plate") {{
    fit_test_plate();
}} else {{
    reference_layout();
}}
'''


def write_notes() -> None:
    NOTES.write_text(
        """# Kobalt 81798 Socket Organizer v02 Notes

Task mode: `reference_based_reconstruction`

v02 is a corrective engineering rebuild after v01 failed visually. v01 is used only as failure context for the rough footprint and split-module idea.

## Corrected v01 Failures

- v01 near-uniform pocket issue: fixed by assigning an explicit pocket diameter to every one of the 153 inventory rows.
- v01 unreadable custom stroke labels: fixed by using uppercase ASCII display labels with OpenSCAD native `text()` at 5.5 mm minimum and `Liberation Sans:style=Bold`.
- v01 count ambiguity: fixed with machine-readable inventory and validation checks for 153 storage locations, 128 circular cups, and 25 long channels.

## Diameter Status

All socket and bit-socket diameters remain estimated because no caliper measurements were provided. Diameters are final modeled pocket diameters with loose clearance already included.

## Required Fit Action

Print `exports/kobalt_81798_socket_organizer_v02_fit_test_plate.stl` before committing to full tray modules.
""",
        encoding="utf-8",
    )
    MANIFEST.write_text(
        """---
project_stem: kobalt_81798_socket_organizer
version: v02
task_mode: reference_based_reconstruction
status: corrective rebuild pending validation
source_file: source/kobalt_81798_socket_organizer_v02.scad
inventory_file: notes/kobalt_81798_socket_organizer_v02_inventory.json
stl_export_status: NOT VERIFIED until exports complete
preview_export_status: NOT VERIFIED until preview exists
---

# Kobalt 81798 Socket Organizer v02 Manifest

v02 replaces v01 as the editable geometry source after v01 visual failure.
""",
        encoding="utf-8",
    )
    COMPARISON.write_text(
        """# Kobalt 81798 Socket Organizer v02 Reference Comparison Log

- Official inventory authority: Lowe's Kobalt 81798 Dimensions Guide component list.
- Supporting layout authority: user screenshot dimensions for footprint and module zones.
- v01 comparison: rejected for near-uniform pockets and unreadable labels.
- v02 target counts: 153 storage locations, 128 circular cups, 25 long channels.
""",
        encoding="utf-8",
    )
    REVIEW.write_text(
        """# Kobalt 81798 Socket Organizer v02 Review Report

This file is updated by the final validation pass. v02 is not complete until all required module STLs and the fit-test plate export successfully and `tools/validate_v02.py` passes.
""",
        encoding="utf-8",
    )
    PRINTABILITY.write_text(
        """# Kobalt 81798 Socket Organizer v02 Printability Review

- Process: FDM-first.
- Printer target: Bambu Lab P2S.
- Orientation: flat on bed, pocket side up.
- Supports: none intended.
- Required first print: fit-test plate.
- Fit confidence: low until socket ODs are measured.
""",
        encoding="utf-8",
    )


def main() -> int:
    PROJECT.joinpath("source").mkdir(exist_ok=True)
    PROJECT.joinpath("notes").mkdir(exist_ok=True)
    PROJECT.joinpath("exports").mkdir(exist_ok=True)
    PROJECT.joinpath("previews").mkdir(exist_ok=True)
    PROJECT.joinpath("tools").mkdir(exist_ok=True)

    if len(inventory) != 153:
        raise RuntimeError(f"inventory count is {len(inventory)}, expected 153")
    if sum(1 for row in inventory if row["kind"] == "cup") != 128:
        raise RuntimeError("circular cup count is not 128")
    if sum(1 for row in inventory if row["kind"] == "channel") != 25:
        raise RuntimeError("long channel count is not 25")

    SOURCE.write_text(build_scad(), encoding="utf-8")
    INVENTORY_JSON.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    write_notes()
    print(f"Wrote {SOURCE}")
    print(f"Wrote {INVENTORY_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
