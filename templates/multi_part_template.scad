// project_stem: example_multi_part
// version: v01
// units: millimeters
// orientation: Z+ is up
// printer_name: Bambu Lab P2S
// material: PETG
// print_orientation: each split part uses largest flat face on bed
// support_notes: update before export
// brim_notes: update before export

$fn = 64;

// -------------------------
// Parameters
// -------------------------
project_stem = "example_multi_part";
version = "v01";
printer_name = "Bambu Lab P2S";
material = "PETG";

clearance_profile = "normal_slip";
loose_clearance = 0.5;
normal_clearance = 0.3;
tight_clearance = 0.15;
fit_clearance = normal_clearance;

overall_width = 180;
overall_depth = 80;
overall_height = 16;
wall_thickness = 3.2;

screw_diameter = 4.5;
screw_head_diameter = 8.5;
screw_head_depth = 3;
use_countersink = false;
use_counterbore = true;

rib_thickness = 2.4;
rib_height = 12;

export_part = "all"; // all, left, right
split_part = "left_right";

// -------------------------
// Helper Modules
// -------------------------
module screw_clearance_hole(height) {
    cylinder(h = height, d = screw_diameter + fit_clearance);
}

module counterbore(depth) {
    if (use_counterbore)
        cylinder(h = depth, d = screw_head_diameter + fit_clearance);
}

module alignment_pin() {
    cylinder(h = 8, d = 5 - tight_clearance);
}

module alignment_socket() {
    cylinder(h = 9, d = 5 + normal_clearance);
}

module reinforcement_rib(length) {
    linear_extrude(height = rib_thickness)
        polygon(points = [[0, 0], [length, 0], [0, rib_height]]);
}

// -------------------------
// Body Modules
// -------------------------
module base_body() {
    difference() {
        cube([overall_width, overall_depth, overall_height]);
        for (x_pos = [25, overall_width - 25]) {
            translate([x_pos, overall_depth / 2, -1])
                screw_clearance_hole(overall_height + 2);
            translate([x_pos, overall_depth / 2, overall_height - screw_head_depth])
                counterbore(screw_head_depth + 1);
        }
    }
}

module split_volume_left() {
    intersection() {
        base_body();
        translate([-1, -1, -1])
            cube([overall_width / 2 + 1, overall_depth + 2, overall_height + 2]);
    }
}

module split_volume_right() {
    intersection() {
        base_body();
        translate([overall_width / 2, -1, -1])
            cube([overall_width / 2 + 1, overall_depth + 2, overall_height + 2]);
    }
}

module left_part() {
    union() {
        split_volume_left();
        translate([overall_width / 2 - 10, overall_depth * 0.3, overall_height])
            alignment_pin();
        translate([overall_width / 2 - 10, overall_depth * 0.7, overall_height])
            alignment_pin();
    }
}

module right_part() {
    difference() {
        split_volume_right();
        translate([overall_width / 2 - 10, overall_depth * 0.3, overall_height - 1])
            alignment_socket();
        translate([overall_width / 2 - 10, overall_depth * 0.7, overall_height - 1])
            alignment_socket();
    }
}

// -------------------------
// Final Render
// -------------------------
module final_render() {
    if (export_part == "left") {
        left_part();
    } else if (export_part == "right") {
        right_part();
    } else {
        union() {
            left_part();
            right_part();
        }
    }
}

final_render();
