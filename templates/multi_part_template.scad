use <../../../standards/hardware_library.scad>

// project_stem: <project_stem>
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
project_stem = "<project_stem>";
version = "v01";
printer_name = "Bambu Lab P2S";
material = "petg";
nozzle_diameter = 0.4;

clearance_profile = "normal_slip";
loose_clearance = 0.5;
normal_clearance = 0.3;
tight_clearance = 0.15;
fit_clearance = normal_clearance + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter);

overall_width = 180;
overall_depth = 80;
overall_height = 16;
wall_thickness = 3.2;

bolt_size = "m4";
screw_fit_class = "normal";
screw_diameter = clearance_hole_d(bolt_size, screw_fit_class, material, nozzle_diameter);
screw_head_diameter = counterbore_d(bolt_size, screw_fit_class, material, nozzle_diameter);
screw_head_depth = counterbore_depth(bolt_size);
use_countersink = false;
use_counterbore = true;

rib_thickness = 2.4;
rib_height = 12;

cutter_overlap_z = 1;
cutter_extra_z = cutter_overlap_z * 2;
hole_offset_x = 25;
hole_center_y = overall_depth / 2;
split_overlap = 1;
split_plane_x = overall_width / 2;
alignment_offset_x = 10;
alignment_y_ratio_a = 0.3;
alignment_y_ratio_b = 0.7;
alignment_x = split_plane_x - alignment_offset_x;
alignment_y_a = overall_depth * alignment_y_ratio_a;
alignment_y_b = overall_depth * alignment_y_ratio_b;
alignment_socket_z = overall_height - cutter_overlap_z;
alignment_pin_diameter = 5;
alignment_pin_height = 8;
alignment_socket_height = 9;

export_part = "all"; // all, left, right
split_part = "left_right";

// -------------------------
// Helper Modules
// -------------------------
module screw_clearance_hole(height) {
    clearance_hole(bolt_size, height, screw_fit_class, material, nozzle_diameter);
}

module counterbore(depth) {
    if (use_counterbore)
        counterbore_pocket(bolt_size, depth, screw_fit_class, material, nozzle_diameter);
}

module alignment_pin() {
    cylinder(h = alignment_pin_height, d = alignment_pin_diameter - tight_clearance);
}

module alignment_socket() {
    cylinder(h = alignment_socket_height, d = alignment_pin_diameter + normal_clearance);
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
        for (x_pos = [hole_offset_x, overall_width - hole_offset_x]) {
            translate([x_pos, hole_center_y, -cutter_overlap_z])
                screw_clearance_hole(overall_height + cutter_extra_z);
            translate([x_pos, hole_center_y, overall_height - screw_head_depth])
                counterbore(screw_head_depth + cutter_overlap_z);
        }
    }
}

module split_volume_left() {
    intersection() {
        base_body();
        translate([-split_overlap, -split_overlap, -split_overlap])
            cube([split_plane_x + split_overlap, overall_depth + cutter_extra_z, overall_height + cutter_extra_z]);
    }
}

module split_volume_right() {
    intersection() {
        base_body();
        translate([split_plane_x, -split_overlap, -split_overlap])
            cube([split_plane_x + split_overlap, overall_depth + cutter_extra_z, overall_height + cutter_extra_z]);
    }
}

module left_part() {
    union() {
        split_volume_left();
        translate([alignment_x, alignment_y_a, overall_height])
            alignment_pin();
        translate([alignment_x, alignment_y_b, overall_height])
            alignment_pin();
    }
}

module right_part() {
    difference() {
        split_volume_right();
        translate([alignment_x, alignment_y_a, alignment_socket_z])
            alignment_socket();
        translate([alignment_x, alignment_y_b, alignment_socket_z])
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
