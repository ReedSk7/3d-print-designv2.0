// vevor_65pc_half_drive_packout_4drawer_organizer_v02
// Task mode: original_product_design
// Purpose: retarget the printable split workflow to a 245 x 245 x 40 mm
// build volume while keeping the v01 organizer layout intact.
// Units: millimeters

use <vevor_65pc_half_drive_packout_4drawer_organizer_v01.scad>

// ---------------------------------------------------------------------------
// Verified base organizer envelope from the exported v01 mesh
// ---------------------------------------------------------------------------

base_full_w = 412.4;
base_full_d = 314.348;
base_full_h = 28.0;

// Verified split-half envelope from the exported v01 left/right meshes
base_half_w = 216.2;
base_right_x0 = base_full_w - base_half_w;

// ---------------------------------------------------------------------------
// Printer-fit section target
// ---------------------------------------------------------------------------

section_target_w = 245.0;
section_target_d = 245.0;
section_target_h = 40.0;

// ---------------------------------------------------------------------------
// Sectioning controls
// render_mode:
// 0 = assembled full tray reference
// 1 = front left printable section
// 2 = rear left printable section
// 3 = front right printable section
// 4 = rear right printable section
// 5 = exploded 4-piece preview
// ---------------------------------------------------------------------------

render_mode = 0;

// This split location is intentionally kept forward of the tray midpoint so the
// seam lands near the band transition instead of producing oversized pieces.
section_split_y = 128.0;

horizontal_joiner_width = 14.0;
horizontal_joiner_depth = 10.0;
horizontal_joiner_margin = 18.0;
horizontal_joiner_clearance = 0.3;
joiner_floor_z = 2.8;
joiner_height = base_full_h - joiner_floor_z;
preview_gap_x = 10.0;
preview_gap_y = 12.0;

front_section_depth = section_split_y + horizontal_joiner_depth;
rear_section_depth = base_full_d - section_split_y;

function x_joiner_positions(x0, zone_w) = [
    x0 + horizontal_joiner_margin,
    x0 + zone_w - horizontal_joiner_margin - horizontal_joiner_width
];

module section_mask(y0, y1) {
    translate([-1, y0, -1])
        cube([base_full_w + 2, y1 - y0, base_full_h + 2]);
}

module front_mask() {
    section_mask(-1, section_split_y + 1);
}

module rear_mask() {
    section_mask(section_split_y, base_full_d + 1);
}

module horizontal_tabs(x0, zone_w) {
    for (x = x_joiner_positions(x0, zone_w)) {
        translate([x, section_split_y, joiner_floor_z])
            cube([horizontal_joiner_width, horizontal_joiner_depth, joiner_height]);
    }
}

module horizontal_slots(x0, zone_w) {
    for (x = x_joiner_positions(x0, zone_w)) {
        translate([x - horizontal_joiner_clearance, section_split_y - horizontal_joiner_clearance, joiner_floor_z - 0.1])
            cube([
                horizontal_joiner_width + horizontal_joiner_clearance * 2,
                horizontal_joiner_depth + horizontal_joiner_clearance * 2,
                joiner_height + 0.3
            ]);
    }
}

module front_left_piece() {
    union() {
        intersection() {
            left_half();
            front_mask();
        }
        horizontal_tabs(0, base_half_w);
    }
}

module rear_left_piece() {
    difference() {
        intersection() {
            left_half();
            rear_mask();
        }
        horizontal_slots(0, base_half_w);
    }
}

module front_right_piece() {
    union() {
        intersection() {
            right_half();
            front_mask();
        }
        horizontal_tabs(base_right_x0, base_half_w);
    }
}

module rear_right_piece() {
    difference() {
        intersection() {
            right_half();
            rear_mask();
        }
        horizontal_slots(base_right_x0, base_half_w);
    }
}

module exploded_preview() {
    translate([0, 0, 0]) front_left_piece();
    translate([0, front_section_depth + preview_gap_y, 0]) rear_left_piece();
    translate([base_half_w + preview_gap_x, 0, 0]) front_right_piece();
    translate([base_half_w + preview_gap_x, front_section_depth + preview_gap_y, 0]) rear_right_piece();
}

echo(str("task_mode = original_product_design"));
echo(str("base_full_envelope_mm = ", base_full_w, " x ", base_full_d, " x ", base_full_h));
echo(str("section_target_mm = ", section_target_w, " x ", section_target_d, " x ", section_target_h));
echo(str("section_split_y_mm = ", section_split_y));
echo(str("front_section_target_depth_mm = ", front_section_depth));
echo(str("rear_section_target_depth_mm = ", rear_section_depth));
echo(str("target_check_front_left = ", base_half_w <= section_target_w && front_section_depth <= section_target_d && base_full_h <= section_target_h));
echo(str("target_check_rear_left = ", base_half_w <= section_target_w && rear_section_depth <= section_target_d && base_full_h <= section_target_h));
echo(str("target_check_front_right = ", base_half_w <= section_target_w && front_section_depth <= section_target_d && base_full_h <= section_target_h));
echo(str("target_check_rear_right = ", base_half_w <= section_target_w && rear_section_depth <= section_target_d && base_full_h <= section_target_h));

if (render_mode == 1)
    front_left_piece();
else if (render_mode == 2)
    rear_left_piece();
else if (render_mode == 3)
    front_right_piece();
else if (render_mode == 4)
    rear_right_piece();
else if (render_mode == 5)
    exploded_preview();
else
    organizer_full();
