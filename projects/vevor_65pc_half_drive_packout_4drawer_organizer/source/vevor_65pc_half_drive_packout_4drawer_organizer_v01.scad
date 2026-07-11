// vevor_65pc_half_drive_packout_4drawer_organizer_v01
// Task mode: original_product_design
// This v01 is a measurement-gated scaffold. Replace estimated drawer and tool
// envelopes with real measurements before trusting final fit.
// Units: millimeters

$fn = 48;

// ---------------------------------------------------------------------------
// Required top-level editable parameters
// ---------------------------------------------------------------------------

drawer_inner_w = 414.0;  // Estimated from prior Packout layout work. Not verified here.
drawer_inner_d = 317.5;  // Estimated from prior Packout layout work. Not verified here.
drawer_inner_h = 58.4;   // Estimated from prior Packout layout work. Not verified here.

wall_clearance = 0.8;
floor_clearance = 1.0;
tray_base_thickness = 2.8;
min_wall = 2.4;
label_depth = 0.6;
finger_scallop_r = 6.5;
socket_clearance_diam = 0.6;
socket_clearance_depth = 0.8;
split_tray = true;
joiner_clearance = 0.3;

// ---------------------------------------------------------------------------
// Render controls
// render_mode:
// 0 = assembled full tray
// 1 = left split half
// 2 = right split half
// 3 = split preview pair
// ---------------------------------------------------------------------------

render_mode = 0;

// ---------------------------------------------------------------------------
// General tuning
// ---------------------------------------------------------------------------

label_font = "Liberation Sans:style=Bold";
label_size = 3.5;
group_label_size = 4.6;
item_gap = 2.2;
band_gap = 3.0;
corner_radius = 8.0;
channel_support_ratio = 0.74;
vertical_support_ratio = 0.42;
entry_ease = 0.9;
max_tray_height = 28.0;
accessory_strip_width = 34.0;
split_gap_preview = 8.0;

// ---------------------------------------------------------------------------
// Estimated tool spec tables
// Field order per row: [label, estimated_outer_diameter, estimated_height]
// Replace every estimated value with measured data before final fit.
// ---------------------------------------------------------------------------

metric_std_specs = [
    ["10mm", 18.2, 38.0],
    ["11mm", 19.6, 38.5],
    ["12mm", 20.8, 39.0],
    ["13mm", 22.4, 39.5],
    ["14mm", 23.6, 40.0],
    ["15mm", 24.8, 40.5],
    ["16mm", 26.2, 41.0],
    ["17mm", 27.5, 42.0],
    ["18mm", 28.8, 42.5],
    ["19mm", 30.4, 43.5],
    ["20mm", 31.8, 44.0],
    ["21mm", 33.4, 45.0],
    ["22mm", 34.8, 46.0],
    ["23mm", 36.2, 47.0],
    ["24mm", 37.6, 48.0]
];

metric_deep_specs = [
    ["10mm", 19.6, 78.0],
    ["11mm", 21.0, 78.5],
    ["12mm", 22.2, 79.0],
    ["13mm", 23.8, 79.5],
    ["14mm", 25.2, 80.0],
    ["15mm", 26.8, 81.0],
    ["16mm", 28.2, 82.0],
    ["17mm", 29.8, 83.0],
    ["18mm", 31.2, 84.0],
    ["19mm", 32.8, 85.0],
    ["20mm", 34.4, 86.0],
    ["21mm", 36.0, 87.0],
    ["22mm", 37.6, 88.0],
    ["23mm", 39.2, 89.0],
    ["24mm", 40.8, 90.0]
];

sae_std_specs = [
    ["3/8\"", 20.0, 39.0],
    ["7/16\"", 21.6, 39.5],
    ["1/2\"", 22.8, 40.0],
    ["9/16\"", 24.6, 41.0],
    ["5/8\"", 26.2, 42.0],
    ["11/16\"", 27.8, 43.0],
    ["3/4\"", 29.4, 44.0],
    ["13/16\"", 31.0, 45.0],
    ["7/8\"", 33.4, 46.0],
    ["15/16\"", 35.0, 47.0],
    ["1\"", 36.8, 48.0],
    ["1-1/16\"", 38.8, 49.5],
    ["1-1/8\"", 41.0, 51.0],
    ["1-1/4\"", 44.5, 53.5]
];

sae_deep_specs = [
    ["3/8\"", 21.2, 79.0],
    ["7/16\"", 22.8, 80.0],
    ["1/2\"", 24.0, 81.0],
    ["9/16\"", 25.8, 82.0],
    ["5/8\"", 27.4, 83.0],
    ["11/16\"", 29.0, 84.0],
    ["3/4\"", 30.6, 85.0],
    ["13/16\"", 32.2, 86.0],
    ["7/8\"", 34.8, 87.0],
    ["15/16\"", 36.4, 88.0],
    ["1\"", 38.2, 89.0],
    ["1-1/16\"", 40.4, 90.5],
    ["1-1/8\"", 42.8, 92.0],
    ["1-1/4\"", 46.4, 95.0]
];

// [label, estimated_length, estimated_width, estimated_depth]
ratchet_spec = ["ratchet", 258.0, 30.0, 14.5];

extension_specs = [
    ["10 in ext", 258.0, 16.5, 11.5],
    ["5 in ext", 132.0, 16.5, 11.5],
    ["3 in ext", 82.0, 16.5, 11.5]
];

adapter_specs = [
    ["u-joint", 34.0, 18.0, 14.5],
    ["1/2F-3/8M", 24.0, 14.0, 14.5],
    ["3/8F-1/2M", 24.0, 14.0, 14.5]
];

// ---------------------------------------------------------------------------
// Field indexes
// ---------------------------------------------------------------------------

spec_label_i = 0;
spec_od_i = 1;
spec_height_i = 2;

accessory_label_i = 0;
accessory_length_i = 1;
accessory_width_i = 2;
accessory_depth_i = 3;

// ---------------------------------------------------------------------------
// Basic helpers
// ---------------------------------------------------------------------------

function list_sum(values, i = 0) =
    i >= len(values) ? 0 : values[i] + list_sum(values, i + 1);

function rows_from_columns(items, row_count) =
    row_count <= 0 || len(items) == 0
        ? []
        : [
            for (r = [0:row_count - 1])
                [for (i = [r:row_count:len(items) - 1]) items[i]]
          ];

function spec_label(spec) = spec[spec_label_i];
function spec_od(spec) = spec[spec_od_i];
function spec_height(spec) = spec[spec_height_i];

function accessory_label(spec) = spec[accessory_label_i];
function accessory_length(spec) = spec[accessory_length_i];
function accessory_width(spec) = spec[accessory_width_i];
function accessory_depth(spec) = spec[accessory_depth_i];

function pocket_diameter(spec) = spec_od(spec) + socket_clearance_diam;

function horizontal_channel_length(spec) =
    max(
        pocket_diameter(spec) + finger_scallop_r * 0.9,
        spec_height(spec) * channel_support_ratio + socket_clearance_depth * 2
    );

function vertical_pocket_depth(spec) =
    min(
        tray_height - tray_base_thickness - 0.8,
        max(11.0, spec_height(spec) * vertical_support_ratio + socket_clearance_depth)
    );

function horizontal_channel_depth(spec) =
    min(
        tray_height - tray_base_thickness - 0.8,
        max(8.0, pocket_diameter(spec) * 0.54)
    );

function row_total_channel_length(row) =
    len(row) == 0
        ? 0
        : list_sum([for (spec = row) horizontal_channel_length(spec)]) + item_gap * (len(row) - 1);

function row_total_pocket_width(row) =
    len(row) == 0
        ? 0
        : list_sum([for (spec = row) pocket_diameter(spec)]) + item_gap * (len(row) - 1);

function row_max_diameter(row) =
    len(row) == 0 ? 0 : max([for (spec = row) pocket_diameter(spec)]);

function row_horizontal_pitch(row) =
    len(row) == 0 ? 0 : max(19.0, row_max_diameter(row) * 0.55 + min_wall * 0.45);

function row_vertical_pitch(row) =
    len(row) == 0 ? 0 : max(21.0, row_max_diameter(row) * 0.68 + min_wall * 0.4);

function row_prefix_offset(rows, row_index, pitch_mode = "horizontal") =
    row_index <= 0
        ? 0
        : list_sum([
            for (i = [0:row_index - 1])
                pitch_mode == "horizontal" ? row_horizontal_pitch(rows[i]) : row_vertical_pitch(rows[i])
          ]) + band_gap * row_index;

function row_channel_offset(row, item_index) =
    item_index <= 0
        ? 0
        : list_sum([for (i = [0:item_index - 1]) horizontal_channel_length(row[i])]) + item_gap * item_index;

function row_pocket_offset(row, item_index) =
    item_index <= 0
        ? 0
        : list_sum([for (i = [0:item_index - 1]) pocket_diameter(row[i])]) + item_gap * item_index;

function group_height(rows, pitch_mode = "horizontal") =
    len(rows) == 0
        ? 0
        : list_sum([
            for (row = rows)
                pitch_mode == "horizontal" ? row_horizontal_pitch(row) : row_vertical_pitch(row)
          ]) + band_gap * (len(rows) - 1);

function group_width(rows, placement_mode = "horizontal") =
    len(rows) == 0
        ? 0
        : max([
            for (row = rows)
                placement_mode == "horizontal" ? row_total_channel_length(row) : row_total_pocket_width(row)
          ]);

function accessory_channel_length(spec) =
    max(accessory_width(spec) + finger_scallop_r, accessory_length(spec) * 0.74);

// ---------------------------------------------------------------------------
// Tray envelope and derived layout data
// ---------------------------------------------------------------------------

tray_height = min(max_tray_height, drawer_inner_h - floor_clearance);
tray_outer_w = drawer_inner_w - 2 * wall_clearance;
tray_outer_d = drawer_inner_d - 2 * wall_clearance;
inner_w = tray_outer_w - 2 * min_wall;
inner_d = tray_outer_d - 2 * min_wall;

metric_deep_rows = rows_from_columns(metric_deep_specs, 3);
sae_deep_rows = rows_from_columns(sae_deep_specs, 3);
metric_std_rows = rows_from_columns(metric_std_specs, 3);
sae_std_rows = rows_from_columns(sae_std_specs, 3);

metric_deep_band_h = group_height(metric_deep_rows, "horizontal");
sae_deep_band_h = group_height(sae_deep_rows, "horizontal");
metric_std_block_w = group_width(metric_std_rows, "vertical");
sae_std_block_w = group_width(sae_std_rows, "vertical");
shallow_band_h = max(group_height(metric_std_rows, "vertical"), group_height(sae_std_rows, "vertical"));
shallow_total_w = metric_std_block_w + band_gap + sae_std_block_w;

accessory_row_1_h = max(accessory_width(ratchet_spec), accessory_specs_max_width(adapter_specs));
accessory_row_2_h = accessory_width(extension_specs[0]);
accessory_band_h = accessory_row_1_h + accessory_row_2_h + band_gap;

requested_depth =
    2 * min_wall +
    accessory_band_h +
    band_gap +
    metric_deep_band_h +
    band_gap +
    sae_deep_band_h +
    band_gap +
    shallow_band_h;

effective_tray_d = min(tray_outer_d, requested_depth);

split_x = tray_outer_w / 2;
joiner_length = 10.0;
joiner_depth = 22.0;
joiner_margin = 26.0;
joiner_positions = [
    joiner_margin,
    effective_tray_d / 2 - joiner_depth / 2,
    effective_tray_d - joiner_margin - joiner_depth
];

// ---------------------------------------------------------------------------
// Accessory helper functions
// ---------------------------------------------------------------------------

function accessory_specs_max_width(items) =
    len(items) == 0 ? 0 : max([for (item = items) accessory_width(item)]);

function accessory_stack_height(items) =
    len(items) == 0
        ? 0
        : list_sum([for (item = items) accessory_width(item)]) + item_gap * (len(items) - 1);

// ---------------------------------------------------------------------------
// Geometry helpers
// ---------------------------------------------------------------------------

module rounded_rect_2d(size = [10, 10], r = 2, center = false) {
    actual_r = min(r, min(size[0], size[1]) / 2 - 0.01);
    translate(center ? [-size[0] / 2, -size[1] / 2] : [0, 0])
        offset(r = actual_r)
            offset(delta = -actual_r)
                square(size);
}

module rounded_box(size = [10, 10, 10], r = 2, center = false) {
    translate(center ? [-size[0] / 2, -size[1] / 2, -size[2] / 2] : [0, 0, 0])
        linear_extrude(height = size[2])
            rounded_rect_2d([size[0], size[1]], r = min(r, min(size[0], size[1]) / 2 - 0.01));
}

module engraved_label(text_value, x, y, angle = 0, size = label_size) {
    translate([x, y, tray_height - label_depth + 0.01])
        rotate([0, 0, angle])
            linear_extrude(height = label_depth)
                text(text_value, size = size, font = label_font, halign = "center", valign = "center");
}

module horizontal_socket_channel(spec) {
    channel_length = horizontal_channel_length(spec);
    channel_diameter = pocket_diameter(spec);
    channel_depth = horizontal_channel_depth(spec);

    union() {
        rounded_box(
            [channel_length, channel_diameter, channel_depth + 0.2],
            r = min(channel_diameter / 2 - 0.2, 3.4)
        );

        translate([channel_length * 0.12, channel_diameter / 2, channel_depth - entry_ease])
            cylinder(h = entry_ease + 0.25, d1 = finger_scallop_r * 1.35, d2 = finger_scallop_r * 1.65);

        translate([channel_length * 0.88, channel_diameter / 2, channel_depth - entry_ease])
            cylinder(h = entry_ease + 0.25, d1 = finger_scallop_r * 1.35, d2 = finger_scallop_r * 1.65);

        translate([channel_length * 0.18, channel_diameter / 2, channel_depth - finger_scallop_r * 0.58])
            cylinder(h = finger_scallop_r * 0.62 + 0.2, d = finger_scallop_r * 1.85);

        translate([channel_length * 0.82, channel_diameter / 2, channel_depth - finger_scallop_r * 0.58])
            cylinder(h = finger_scallop_r * 0.62 + 0.2, d = finger_scallop_r * 1.85);
    }
}

module vertical_socket_pocket(spec) {
    pocket_d = pocket_diameter(spec);
    pocket_depth = vertical_pocket_depth(spec);

    union() {
        cylinder(h = pocket_depth + 0.2, d = pocket_d);

        translate([0, 0, pocket_depth - entry_ease])
            cylinder(h = entry_ease + 0.25, d1 = pocket_d + 1.6, d2 = pocket_d + 0.5);

        translate([0, -pocket_d * 0.34, pocket_depth * 0.48])
            rotate([90, 0, 0])
                cylinder(h = pocket_d * 0.78, d = finger_scallop_r * 1.55, center = true);
    }
}

module accessory_channel(spec) {
    channel_length = accessory_channel_length(spec);
    channel_width = accessory_width(spec);
    channel_depth = accessory_depth(spec);

    union() {
        rounded_box(
            [channel_length, channel_width, channel_depth + 0.2],
            r = min(channel_width / 2 - 0.2, 3.2)
        );

        translate([channel_length * 0.18, channel_width / 2, channel_depth - entry_ease])
            cylinder(h = entry_ease + 0.25, d = finger_scallop_r * 1.5);

        translate([channel_length * 0.82, channel_width / 2, channel_depth - entry_ease])
            cylinder(h = entry_ease + 0.25, d = finger_scallop_r * 1.5);
    }
}

module accessory_block(spec) {
    rounded_box(
        [accessory_length(spec), accessory_width(spec), accessory_depth(spec) + 0.2],
        r = min(3.4, accessory_width(spec) / 2 - 0.2)
    );
}

// ---------------------------------------------------------------------------
// Layout placement
// ---------------------------------------------------------------------------

module place_horizontal_group(rows, origin_x, origin_y) {
    for (row_index = [0:len(rows) - 1]) {
        row = rows[row_index];
        row_w = row_total_channel_length(row);
        row_y = origin_y + row_prefix_offset(rows, row_index, "horizontal");
        row_x = origin_x + max(0, (inner_w - row_w) / 2);

        for (item_index = [0:len(row) - 1]) {
            spec = row[item_index];
            channel_length = horizontal_channel_length(spec);
            channel_diameter = pocket_diameter(spec);
            channel_depth = horizontal_channel_depth(spec);
            item_x = row_x + row_channel_offset(row, item_index);
            item_y = row_y;

            translate([item_x, item_y, tray_height - channel_depth])
                horizontal_socket_channel(spec);

            engraved_label(
                spec_label(spec),
                item_x + channel_length / 2,
                item_y + channel_diameter / 2,
                angle = channel_length > 60 ? 0 : 90,
                size = len(spec_label(spec)) > 4 ? 3.1 : 3.5
            );
        }
    }
}

module place_vertical_group(rows, origin_x, origin_y, block_width) {
    for (row_index = [0:len(rows) - 1]) {
        row = rows[row_index];
        row_w = row_total_pocket_width(row);
        row_y = origin_y + row_prefix_offset(rows, row_index, "vertical");
        row_x = origin_x + max(0, (block_width - row_w) / 2);

        for (item_index = [0:len(row) - 1]) {
            spec = row[item_index];
            pocket_d = pocket_diameter(spec);
            pocket_depth = vertical_pocket_depth(spec);
            pocket_x = row_x + row_pocket_offset(row, item_index) + pocket_d / 2;
            pocket_y = row_y + pocket_d / 2;

            translate([pocket_x, pocket_y, tray_height - pocket_depth])
                vertical_socket_pocket(spec);

            engraved_label(
                spec_label(spec),
                pocket_x,
                pocket_y,
                angle = 90,
                size = len(spec_label(spec)) > 4 ? 2.9 : 3.2
            );
        }
    }
}

module organizer_negative_space() {
    accessory_origin_y = min_wall;
    metric_deep_origin_y = accessory_origin_y + accessory_band_h + band_gap;
    sae_deep_origin_y = metric_deep_origin_y + metric_deep_band_h + band_gap;
    shallow_origin_y = sae_deep_origin_y + sae_deep_band_h + band_gap;

    // Accessory band
    row_1_y = accessory_origin_y;
    row_2_y = row_1_y + accessory_row_1_h + band_gap;

    ratchet_len = accessory_channel_length(ratchet_spec);
    ext_10_len = accessory_channel_length(extension_specs[0]);
    ext_5_len = accessory_channel_length(extension_specs[1]);
    ext_3_len = accessory_channel_length(extension_specs[2]);

    translate([min_wall, row_1_y, tray_height - accessory_depth(ratchet_spec)])
        accessory_channel(ratchet_spec);
    engraved_label("ratchet", min_wall + ratchet_len / 2, row_1_y + accessory_width(ratchet_spec) / 2, size = 3.8);

    ext_3_x = min_wall + ratchet_len + item_gap;
    translate([ext_3_x, row_1_y + (accessory_row_1_h - accessory_width(extension_specs[2])) / 2, tray_height - accessory_depth(extension_specs[2])])
        accessory_channel(extension_specs[2]);
    engraved_label(
        accessory_label(extension_specs[2]),
        ext_3_x + ext_3_len / 2,
        row_1_y + accessory_row_1_h / 2,
        size = 3.0
    );

    for (i = [0:len(adapter_specs) - 1]) {
        spec = adapter_specs[i];
        x =
            ext_3_x +
            ext_3_len +
            item_gap +
            (i <= 0 ? 0 : list_sum([for (j = [0:i - 1]) accessory_length(adapter_specs[j])]) + item_gap * i);
        y = row_1_y + (accessory_row_1_h - accessory_width(spec)) / 2;

        translate([x, y, tray_height - accessory_depth(spec)])
            accessory_block(spec);
        engraved_label(
            accessory_label(spec),
            x + accessory_length(spec) / 2,
            y + accessory_width(spec) / 2,
            angle = accessory_length(spec) > 28 ? 0 : 90,
            size = 2.7
        );
    }

    row_2_x = min_wall;
    translate([row_2_x, row_2_y, tray_height - accessory_depth(extension_specs[0])])
        accessory_channel(extension_specs[0]);
    translate([row_2_x + ext_10_len + item_gap, row_2_y, tray_height - accessory_depth(extension_specs[1])])
        accessory_channel(extension_specs[1]);
    engraved_label(accessory_label(extension_specs[0]), row_2_x + ext_10_len / 2, row_2_y + accessory_width(extension_specs[0]) / 2, size = 3.2);
    engraved_label(accessory_label(extension_specs[1]), row_2_x + ext_10_len + item_gap + ext_5_len / 2, row_2_y + accessory_width(extension_specs[1]) / 2, size = 3.2);

    // Metric deep band
    engraved_label("metric deep", min_wall + 34, metric_deep_origin_y - 4.5, size = group_label_size);
    place_horizontal_group(metric_deep_rows, min_wall, metric_deep_origin_y);

    // SAE deep band
    engraved_label("SAE deep", min_wall + 26, sae_deep_origin_y - 4.5, size = group_label_size);
    place_horizontal_group(sae_deep_rows, min_wall, sae_deep_origin_y);

    // Shallow sockets in a shared rear band
    shallow_origin_x = min_wall + max(0, (inner_w - shallow_total_w) / 2);
    metric_block_x = shallow_origin_x;
    sae_block_x = metric_block_x + metric_std_block_w + band_gap;

    engraved_label("metric shallow", metric_block_x + metric_std_block_w / 2, shallow_origin_y - 4.5, size = 4.0);
    engraved_label("SAE shallow", sae_block_x + sae_std_block_w / 2, shallow_origin_y - 4.5, size = 4.0);

    place_vertical_group(metric_std_rows, metric_block_x, shallow_origin_y, metric_std_block_w);
    place_vertical_group(sae_std_rows, sae_block_x, shallow_origin_y, sae_std_block_w);
}

module tray_shell() {
    rounded_box([tray_outer_w, effective_tray_d, tray_height], r = corner_radius);
}

module organizer_full() {
    difference() {
        tray_shell();
        organizer_negative_space();
    }
}

module split_left_mask() {
    translate([-1, -1, -1])
        cube([split_x + joiner_length, effective_tray_d + 2, tray_height + 2]);
}

module split_right_mask() {
    translate([split_x - joiner_length, -1, -1])
        cube([tray_outer_w - split_x + joiner_length + 1, effective_tray_d + 2, tray_height + 2]);
}

module left_joiners(clearance = 0) {
    for (pos = joiner_positions) {
        translate([split_x - clearance, pos, tray_base_thickness])
            cube([
                joiner_length + clearance,
                joiner_depth,
                tray_height - tray_base_thickness
            ]);
    }
}

module right_joiner_slots(clearance = 0) {
    for (pos = joiner_positions) {
        translate([split_x - joiner_length - clearance, pos - clearance, tray_base_thickness - 0.1])
            cube([
                joiner_length + clearance * 2,
                joiner_depth + clearance * 2,
                tray_height - tray_base_thickness + 0.3
            ]);
    }
}

module left_half() {
    intersection() {
        union() {
            intersection() {
                organizer_full();
                split_left_mask();
            }
            left_joiners();
        }
        tray_shell();
    }
}

module right_half() {
    difference() {
        intersection() {
            organizer_full();
            split_right_mask();
        }
        right_joiner_slots(joiner_clearance);
    }
}

module split_pair_preview() {
    translate([0, 0, 0]) left_half();
    translate([split_x + split_gap_preview, 0, 0]) right_half();
}

echo(str("task_mode = original_product_design"));
echo(str("verified_dimensions_present = false"));
echo(str("drawer estimate used (w,d,h) = ", drawer_inner_w, ", ", drawer_inner_d, ", ", drawer_inner_h));
echo(str("tray envelope mm = ", tray_outer_w, " x ", effective_tray_d, " x ", tray_height));
echo(str("requested depth mm = ", requested_depth));
echo(str("metric sockets count = ", len(metric_std_specs) + len(metric_deep_specs)));
echo(str("sae sockets count = ", len(sae_std_specs) + len(sae_deep_specs)));
echo(str("accessories count = ", 1 + len(extension_specs) + len(adapter_specs)));
echo(str("split_tray parameter = ", split_tray));

if (render_mode == 1 && split_tray)
    left_half();
else if (render_mode == 2 && split_tray)
    right_half();
else if (render_mode == 3 && split_tray)
    split_pair_preview();
else
    organizer_full();
