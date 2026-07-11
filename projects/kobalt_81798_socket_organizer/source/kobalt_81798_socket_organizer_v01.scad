// project_stem: kobalt_81798_socket_organizer
// version: v01
// task_mode: reference_based_reconstruction
// Units: millimeters. Z+ is up.
// This is an original organizer layout for the Kobalt 81798 set. It does not
// copy paid STL geometry or any brand/seller logo artwork.

$fn = 24;

project_version = "v01";
render_mode = "all_modules"; // all_modules, left_top, left_bottom, center_top_left, center_top_right, center_bottom_left, center_bottom_right, right_top, right_bottom
render_mode_index = 0; // 0 all_modules, 1 left_top, 2 left_bottom, 3 center_top_left, 4 center_top_right, 5 center_bottom_left, 6 center_bottom_right, 7 right_top, 8 right_bottom
active_render_mode = is_undef(render_mode_override) ? render_mode : render_mode_override;
active_render_mode_index = is_undef(render_mode_index_override) ? render_mode_index : render_mode_index_override;
units = "mm";

overall_width = 621.03;
overall_depth = 332.74;
base_thickness = 12.70;

left_w = 219.71;
center_w = 254.00;
right_w = 147.32;
center_half_w = center_w / 2;

left_lower_d = 134.87;
left_upper_d = 197.87;
right_lower_d = 175.26;
right_upper_d = 157.40;
center_mid_y = 166.37;
center_top_d = overall_depth - center_mid_y;

safe_build_max = 245;
printer_build = [256, 256, 256];

socket_cup_depth = 6.0;
long_channel_depth = 4.0;
min_floor = 2.5;
min_web = 3.0;
edge_margin = 5.0;

clearance_regular = 0.35;
clearance_loose = 0.50;
clearance_snug = 0.20;
long_channel_clearance = 0.60;
alignment_clearance = 0.25;

outer_chamfer = 1.0;
pocket_chamfer = 0.8;
label_depth = 0.45;
label_size_small = 4.0;
label_size_medium = 5.0;
label_size_large = 6.0;

od_1_4_bit_socket_default = 13.0; // estimated, low confidence
od_3_8_bit_socket_default = 18.0; // estimated, low confidence
od_1_2_bit_socket_default = 24.0; // estimated, low confidence
od_1_4_shallow_socket_default = 14.0; // estimated, low confidence
od_3_8_shallow_socket_default = 19.0; // estimated, low confidence
od_1_2_shallow_socket_default = 26.0; // estimated, low confidence
long_bit_shaft_default = 6.0; // estimated, low confidence

panel_corner_radius = 2.4;
key_depth = 4.0;
glyph_w = 1.00;
glyph_h = 1.60;
glyph_stroke = 0.16;
glyph_advance = 1.08;

left_top_rows = [
    [["5/8", "11/16", "3/4", "13/16", "7/8"], 20.00, 44.00, 181.50, od_1_2_shallow_socket_default, 3.6, "1/2DR 8PT SAE"],
    [["E18", "E20", "E22", "E24", "T55", "T60", "T70"], 16.25, 31.20, 145.50, od_1_2_shallow_socket_default, 3.6, "1/2DR E/TORX"],
    [["5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "11/16", "3/4"], 15.25, 27.00, 109.50, od_1_2_bit_socket_default, 3.3, "1/2DR HEX SAE"],
    [["6mm", "7mm", "8mm", "9mm", "10mm", "11mm", "12mm"], 18.50, 30.40, 73.50, od_1_2_bit_socket_default, 3.3, "1/2DR HEX MM"],
    [["13mm", "14mm", "15mm", "16mm", "17mm", "18mm", "19mm"], 18.50, 30.40, 37.50, od_1_2_bit_socket_default, 3.3, "1/2DR HEX MM"]
];

left_bottom_rows = [
    [["1/4", "5/16", "3/8", "7/16", "1/2", "9/16"], 18.00, 36.40, 116.00, od_3_8_shallow_socket_default, 3.6, "3/8DR 8PT SAE"],
    [["E10", "E12", "E14", "E16"], 45.00, 43.00, 87.00, od_3_8_shallow_socket_default, 3.6, "3/8DR EXT TORX"],
    [["1/8", "5/32", "3/16", "7/32", "1/4", "5/16", "3/8"], 15.00, 31.60, 58.00, od_3_8_bit_socket_default, 3.5, "3/8DR HEX SAE"],
    [["3mm", "4mm", "5mm", "6mm", "7mm", "8mm", "9mm", "10mm", "11mm", "12mm"], 12.25, 21.69, 29.00, od_3_8_bit_socket_default, 3.1, "3/8DR HEX MM"]
];

right_top_rows = [
    [["1/4", "5/16", "3/8"], 35.00, 38.50, 140.00, od_1_4_shallow_socket_default, 3.4, "1/4DR 8PT SAE"],
    [["E4", "E5", "E6", "E7", "E8"], 17.00, 28.30, 120.00, od_1_4_shallow_socket_default, 3.4, "1/4DR EXT TORX"],
    [["1/16", "5/64", "3/32", "7/64", "1/8"], 17.00, 28.30, 100.00, od_1_4_bit_socket_default, 3.1, "1/4DR HEX SAE"],
    [["9/64", "5/32", "3/16", "7/32", "1/4"], 17.00, 28.30, 80.00, od_1_4_bit_socket_default, 3.1, "1/4DR HEX SAE"],
    [["2mm", "2.5", "3mm", "4mm", "5mm", "6mm"], 14.00, 23.86, 60.00, od_1_4_bit_socket_default, 3.1, "1/4DR HEX MM"],
    [["7/32", "1/4", "PH3", "S1", "S2", "PZ1"], 14.00, 23.86, 40.00, od_1_4_bit_socket_default, 3.1, "1/4DR SCREW"],
    [["T8", "T9", "T10", "T15", "T20", "T25", "T27", "T30"], 11.75, 17.69, 20.00, od_1_4_bit_socket_default, 3.0, "1/4DR TORX"]
];

right_bottom_rows = [
    [["T20", "T25", "T27", "T30", "T40"], 18.00, 27.80, 153.00, od_3_8_bit_socket_default, 3.3, "3/8DR TORX"],
    [["T45", "T47", "T50", "T55"], 32.00, 28.00, 126.00, od_3_8_bit_socket_default, 3.3, "3/8DR TORX"],
    [["TT15", "TT20", "TT25", "TT27", "TT30"], 18.00, 27.80, 99.00, od_3_8_bit_socket_default, 3.2, "3/8DR TTORX"],
    [["TT40", "TT45", "TT50", "TT55", "TT60"], 18.00, 27.80, 72.00, od_3_8_bit_socket_default, 3.2, "3/8DR TTORX"],
    [["9/32", "3/8", "4mm", "5mm", "6mm"], 18.00, 27.80, 45.00, od_3_8_bit_socket_default, 3.1, "3/8DR FLAT"],
    [["PH1", "PH2", "PH3", "PZ2", "PZ3"], 18.00, 27.80, 18.00, od_3_8_bit_socket_default, 3.3, "3/8DR PH/PZ"]
];

center_top_left_channels = [
    ["1/4 1/8", od_1_4_bit_socket_default],
    ["1/4 5/32", od_1_4_bit_socket_default],
    ["1/4 3/16", od_1_4_bit_socket_default],
    ["1/4 7/32", od_1_4_bit_socket_default],
    ["1/4 3mm", od_1_4_bit_socket_default],
    ["1/4 4mm", od_1_4_bit_socket_default]
];

center_top_right_channels = [
    ["1/4 5mm", od_1_4_bit_socket_default],
    ["1/4 6mm", od_1_4_bit_socket_default],
    ["3/8 1/8", od_3_8_bit_socket_default],
    ["3/8 5/32", od_3_8_bit_socket_default],
    ["3/8 3/16", od_3_8_bit_socket_default],
    ["3/8 7/32", od_3_8_bit_socket_default]
];

center_bottom_left_channels = [
    ["3/8 1/4", od_3_8_bit_socket_default],
    ["3/8 5/16", od_3_8_bit_socket_default],
    ["3/8 3/8", od_3_8_bit_socket_default],
    ["3/8 3mm", od_3_8_bit_socket_default],
    ["3/8 4mm", od_3_8_bit_socket_default],
    ["3/8 5mm", od_3_8_bit_socket_default],
    ["3/8 6mm", od_3_8_bit_socket_default]
];

center_bottom_right_channels = [
    ["3/8 7mm", od_3_8_bit_socket_default],
    ["3/8 8mm", od_3_8_bit_socket_default],
    ["3/8 9mm", od_3_8_bit_socket_default],
    ["3/8 10mm", od_3_8_bit_socket_default],
    ["3/8 11mm", od_3_8_bit_socket_default],
    ["3/8 12mm", od_3_8_bit_socket_default]
];

module_names = [
    "left_top", "left_bottom", "center_top_left", "center_top_right",
    "center_bottom_left", "center_bottom_right", "right_top", "right_bottom"
];

function sum_row_counts(rows, i = 0) =
    i >= len(rows) ? 0 : len(rows[i][0]) + sum_row_counts(rows, i + 1);

function sum_channel_counts(groups, i = 0) =
    i >= len(groups) ? 0 : len(groups[i]) + sum_channel_counts(groups, i + 1);

function modeled_count() =
    sum_row_counts(left_top_rows) +
    sum_row_counts(left_bottom_rows) +
    sum_row_counts(right_top_rows) +
    sum_row_counts(right_bottom_rows) +
    sum_channel_counts([
        center_top_left_channels,
        center_top_right_channels,
        center_bottom_left_channels,
        center_bottom_right_channels
    ]);

function module_bbox(name) = name == "left_top" ? [left_w + key_depth, left_upper_d, base_thickness] : name == "left_bottom" ? [left_w + key_depth, left_lower_d + key_depth, base_thickness] : name == "center_top_left" ? [center_half_w + key_depth, center_top_d, base_thickness] : name == "center_top_right" ? [center_half_w + key_depth, center_top_d, base_thickness] : name == "center_bottom_left" ? [center_half_w + key_depth, center_mid_y + key_depth, base_thickness] : name == "center_bottom_right" ? [center_half_w + key_depth, center_mid_y + key_depth, base_thickness] : name == "right_top" ? [right_w, right_upper_d, base_thickness] : name == "right_bottom" ? [right_w, right_lower_d + key_depth, base_thickness] : [0, 0, 0];

assert(modeled_count() == 153, str("Modeled inventory count is ", modeled_count(), " but expected 153."));
assert(socket_cup_depth <= base_thickness - min_floor, "Socket cup depth violates minimum floor thickness.");
assert(long_channel_depth <= base_thickness - min_floor, "Long bit channel depth violates minimum floor thickness.");

for (name = module_names) {
    bbox = module_bbox(name);
    echo(str("MODULE_BBOX ", name, " = ", bbox[0], " x ", bbox[1], " x ", bbox[2], " mm"));
    assert(bbox[0] <= safe_build_max && bbox[1] <= safe_build_max && bbox[2] <= printer_build[2],
        str("Build volume fail: ", name));
}

echo(str("MODELED_POCKET_CHANNEL_COUNT = ", modeled_count()));

module rounded_panel(w, d, h = base_thickness) {
    cube([w, d, h]);
}

module puzzle_key_edge(edge, w, d) {
    if (edge == "right")
        translate([w, 0, 0]) cube([key_depth, d, base_thickness]);
    if (edge == "top")
        translate([0, d, 0]) cube([w, key_depth, base_thickness]);
}

module puzzle_key_socket_cut(edge, w, d) {
    socket_depth = key_depth + alignment_clearance;
    over = 0.02;
    if (edge == "left")
        translate([-over, -alignment_clearance, -over])
            cube([socket_depth + over, d + 2 * alignment_clearance, base_thickness + 2 * over]);
    if (edge == "bottom")
        translate([-alignment_clearance, -over, -over])
            cube([w + 2 * alignment_clearance, socket_depth + over, base_thickness + 2 * over]);
}

module keyed_panel(w, d, male_right = false, male_top = false, female_left = false, female_bottom = false) {
    difference() {
        union() {
            rounded_panel(w, d, base_thickness);
            if (male_right) puzzle_key_edge("right", w, d);
            if (male_top) puzzle_key_edge("top", w, d);
        }
        if (female_left) puzzle_key_socket_cut("left", w, d);
        if (female_bottom) puzzle_key_socket_cut("bottom", w, d);
    }
}

module socket_cup(diameter, depth = socket_cup_depth) {
    translate([0, 0, base_thickness - depth - 0.01])
        cylinder(h = depth + 0.04, d = diameter);
    translate([0, 0, base_thickness - pocket_chamfer])
        cylinder(h = pocket_chamfer + 0.06, d1 = diameter, d2 = diameter + 2 * pocket_chamfer);
}

module rounded_slot_2d(length, width) {
    hull() {
        translate([0, -length / 2]) circle(d = width);
        translate([0, length / 2]) circle(d = width);
    }
}

module long_bit_channel(length, width, depth = long_channel_depth) {
    translate([0, 0, base_thickness - depth - 0.01])
        linear_extrude(height = depth + 0.04)
            rounded_slot_2d(length, width);
    translate([0, 0, base_thickness - pocket_chamfer])
        linear_extrude(height = pocket_chamfer + 0.06)
            rounded_slot_2d(length, width + 2 * pocket_chamfer);
}

module hseg(x, y, w = glyph_w, s = glyph_stroke) {
    translate([x, y]) square([w, s], center = false);
}

module vseg(x, y, h = glyph_h / 2, s = glyph_stroke) {
    translate([x, y]) square([s, h], center = false);
}

module dseg(x, y, angle = 55, len = 1.55, s = glyph_stroke) {
    translate([x, y]) rotate(angle) square([s, len], center = false);
}

module seven_segments(chars) {
    if (search("a", chars) != []) hseg(0, glyph_h - glyph_stroke);
    if (search("b", chars) != []) vseg(glyph_w - glyph_stroke, glyph_h / 2);
    if (search("c", chars) != []) vseg(glyph_w - glyph_stroke, 0);
    if (search("d", chars) != []) hseg(0, 0);
    if (search("e", chars) != []) vseg(0, 0);
    if (search("f", chars) != []) vseg(0, glyph_h / 2);
    if (search("g", chars) != []) hseg(0, glyph_h / 2 - glyph_stroke / 2);
}

module glyph_2d(ch) {
    if (ch == "0") seven_segments("abcdef");
    else if (ch == "1") seven_segments("bc");
    else if (ch == "2") seven_segments("abged");
    else if (ch == "3") seven_segments("abgcd");
    else if (ch == "4") seven_segments("fgbc");
    else if (ch == "5") seven_segments("afgcd");
    else if (ch == "6") seven_segments("afgecd");
    else if (ch == "7") seven_segments("abc");
    else if (ch == "8") seven_segments("abcdefg");
    else if (ch == "9") seven_segments("abfgcd");
    else if (ch == "E") seven_segments("afged");
    else if (ch == "T") { hseg(0, glyph_h - glyph_stroke); vseg(glyph_w / 2 - glyph_stroke / 2, 0, glyph_h); }
    else if (ch == "P") seven_segments("abfg");
    else if (ch == "H") seven_segments("fbgec");
    else if (ch == "Z") { hseg(0, glyph_h - glyph_stroke); hseg(0, glyph_h / 2 - glyph_stroke / 2); hseg(0, 0); dseg(0.20, 0.12, -33, 1.55); }
    else if (ch == "S") seven_segments("afgcd");
    else if (ch == "M" || ch == "m") { vseg(0, 0, glyph_h); vseg(glyph_w - glyph_stroke, 0, glyph_h); dseg(0.10, glyph_h - 0.05, -24, 0.85); dseg(0.86, glyph_h - 0.78, 24, 0.85); }
    else if (ch == "D") { vseg(0, 0, glyph_h); seven_segments("abcd"); }
    else if (ch == "R") { seven_segments("abfg"); dseg(0.46, glyph_h / 2 - 0.02, -34, 0.85); }
    else if (ch == "X") { dseg(0.05, 0.05, -31, 1.72); dseg(0.82, 0.05, 31, 1.72); }
    else if (ch == "O") seven_segments("abcdef");
    else if (ch == "L") seven_segments("fed");
    else if (ch == "F") seven_segments("afge");
    else if (ch == "A") seven_segments("abcefg");
    else if (ch == "/") dseg(0.82, 0.05, 31, 1.72);
    else if (ch == ".") translate([glyph_w / 2 - glyph_stroke / 2, 0]) square([glyph_stroke, glyph_stroke]);
    else if (ch == "-") hseg(0.12, glyph_h / 2 - glyph_stroke / 2, glyph_w * 0.76);
}

module stroke_text_2d(txt) {
    for (i = [0 : len(txt) - 1]) {
        translate([i * glyph_advance, 0]) glyph_2d(txt[i]);
    }
}

module label_text(txt, x, y, size = label_size_small, rot = 0, halign = "center", valign = "center") {
    scale_factor = size / glyph_h;
    text_w = len(txt) * glyph_advance * scale_factor;
    text_h = glyph_h * scale_factor;
    dx = halign == "left" ? 0 : halign == "right" ? -text_w : -text_w / 2;
    dy = valign == "bottom" ? 0 : valign == "top" ? -text_h : -text_h / 2;
    translate([x, y, base_thickness])
        rotate([0, 0, rot])
            linear_extrude(height = label_depth)
                translate([dx, dy])
                    scale([scale_factor, scale_factor])
                        stroke_text_2d(txt);
}

module zone_grid(rows) {
    for (row = rows) {
        labels = row[0];
        x0 = row[1];
        x_step = row[2];
        y = row[3];
        pocket_d = row[4] + clearance_loose;
        for (i = [0 : len(labels) - 1]) {
            translate([x0 + i * x_step, y, 0])
                socket_cup(pocket_d);
        }
    }
}

module zone_grid_labels(rows) {
    for (row = rows) {
        labels = row[0];
        x0 = row[1];
        x_step = row[2];
        y = row[3];
        pocket_d = row[4] + clearance_loose;
        txt_size = row[5];
        label_y = y - pocket_d / 2 - max(3.0, txt_size * 0.8);
        for (i = [0 : len(labels) - 1]) {
            label_text(labels[i], x0 + i * x_step, label_y, txt_size);
        }
    }
}

module long_bit_bank(entries, w, d, x_margin, channel_y1, channel_y2, collar_y, label_y, label_size = 3.0) {
    n = len(entries);
    x_step = n > 1 ? (w - 2 * x_margin) / (n - 1) : 0;
    channel_length = abs(channel_y2 - channel_y1);
    channel_center_y = (channel_y1 + channel_y2) / 2;
    channel_width = long_bit_shaft_default + long_channel_clearance;
    for (i = [0 : n - 1]) {
        x = x_margin + i * x_step;
        translate([x, channel_center_y, 0])
            long_bit_channel(channel_length, channel_width);
        translate([x, collar_y, 0])
            socket_cup(entries[i][1] + clearance_loose);
    }
}

module long_bit_bank_labels(entries, w, d, x_margin, label_y, label_size = 3.0) {
    n = len(entries);
    x_step = n > 1 ? (w - 2 * x_margin) / (n - 1) : 0;
    for (i = [0 : n - 1]) {
        x = x_margin + i * x_step;
        label_text(entries[i][0], x, label_y, label_size, 90);
    }
}

module module_left_top() {
    difference() {
        keyed_panel(left_w, left_upper_d, male_right = true, female_bottom = true);
        zone_grid(left_top_rows);
    }
    zone_grid_labels(left_top_rows);
}

module module_left_bottom() {
    difference() {
        keyed_panel(left_w, left_lower_d, male_right = true, male_top = true);
        zone_grid(left_bottom_rows);
    }
    zone_grid_labels(left_bottom_rows);
}

module module_center_top_left() {
    difference() {
        keyed_panel(center_half_w, center_top_d, male_right = true, female_left = true, female_bottom = true);
        long_bit_bank(center_top_left_channels, center_half_w, center_top_d, 14.0, 30.0, 139.0, 151.0, 14.0, 3.0);
    }
    long_bit_bank_labels(center_top_left_channels, center_half_w, center_top_d, 14.0, 14.0, 3.0);
}

module module_center_top_right() {
    difference() {
        keyed_panel(center_half_w, center_top_d, male_right = true, female_left = true, female_bottom = true);
        long_bit_bank(center_top_right_channels, center_half_w, center_top_d, 14.0, 30.0, 139.0, 151.0, 14.0, 3.0);
    }
    long_bit_bank_labels(center_top_right_channels, center_half_w, center_top_d, 14.0, 14.0, 3.0);
}

module module_center_bottom_left() {
    difference() {
        keyed_panel(center_half_w, center_mid_y, male_right = true, male_top = true, female_left = true);
        long_bit_bank(center_bottom_left_channels, center_half_w, center_mid_y, 13.0, 27.0, 141.0, 153.0, 13.0, 2.8);
    }
    long_bit_bank_labels(center_bottom_left_channels, center_half_w, center_mid_y, 13.0, 13.0, 2.8);
}

module module_center_bottom_right() {
    difference() {
        keyed_panel(center_half_w, center_mid_y, male_right = true, male_top = true, female_left = true);
        long_bit_bank(center_bottom_right_channels, center_half_w, center_mid_y, 14.0, 27.0, 141.0, 153.0, 13.0, 2.8);
    }
    long_bit_bank_labels(center_bottom_right_channels, center_half_w, center_mid_y, 14.0, 13.0, 2.8);
}

module module_right_top() {
    difference() {
        keyed_panel(right_w, right_upper_d, female_left = true, female_bottom = true);
        zone_grid(right_top_rows);
    }
    zone_grid_labels(right_top_rows);
}

module module_right_bottom() {
    difference() {
        keyed_panel(right_w, right_lower_d, male_top = true, female_left = true);
        zone_grid(right_bottom_rows);
    }
    zone_grid_labels(right_bottom_rows);
}

module full_reference_layout() {
    translate([0, left_lower_d, 0]) module_left_top();
    translate([0, 0, 0]) module_left_bottom();

    translate([left_w, center_mid_y, 0]) module_center_top_left();
    translate([left_w + center_half_w, center_mid_y, 0]) module_center_top_right();
    translate([left_w, 0, 0]) module_center_bottom_left();
    translate([left_w + center_half_w, 0, 0]) module_center_bottom_right();

    translate([left_w + center_w, right_lower_d, 0]) module_right_top();
    translate([left_w + center_w, 0, 0]) module_right_bottom();
}

if (render_mode_index_override == 1 || render_mode_index == 1 || active_render_mode == "left_top") {
    module_left_top();
} else if (render_mode_index_override == 2 || render_mode_index == 2 || active_render_mode == "left_bottom") {
    module_left_bottom();
} else if (render_mode_index_override == 3 || render_mode_index == 3 || active_render_mode == "center_top_left") {
    module_center_top_left();
} else if (render_mode_index_override == 4 || render_mode_index == 4 || active_render_mode == "center_top_right") {
    module_center_top_right();
} else if (render_mode_index_override == 5 || render_mode_index == 5 || active_render_mode == "center_bottom_left") {
    module_center_bottom_left();
} else if (render_mode_index_override == 6 || render_mode_index == 6 || active_render_mode == "center_bottom_right") {
    module_center_bottom_right();
} else if (render_mode_index_override == 7 || render_mode_index == 7 || active_render_mode == "right_top") {
    module_right_top();
} else if (render_mode_index_override == 8 || render_mode_index == 8 || active_render_mode == "right_bottom") {
    module_right_bottom();
} else {
    full_reference_layout();
}
