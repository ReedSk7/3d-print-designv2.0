// project_stem: simple_wall_bracket_example
// version: v01
// units: millimeters
// orientation: Z+ is up
// printer_name: Bambu Lab P2S
// material: PETG
// print_orientation: wall plate flat on bed, ribs rising in Z
// support_notes: designed for no supports in default orientation
// brim_notes: brim optional for PETG if bed adhesion is marginal

use <../../../standards/hardware_library.scad>;

$fn = 72;

// -------------------------
// Parameters
// -------------------------
project_stem = "simple_wall_bracket_example";
version = "v01";
printer_name = "Bambu Lab P2S";
material = "PETG";
material_profile = "petg";
nozzle_diameter = 0.40;

clearance_profile = "normal_slip";
loose_clearance = 0.5;
normal_clearance = 0.3;
tight_clearance = 0.15;
fit_clearance = normal_clearance;

bracket_width = 84;
bracket_height = 64;
bracket_depth = 58;
wall_thickness = 4.0;

hardware_size = "number_8_wood";
hardware_fit_class = "normal";
screw_size_label = "#8 wood screw";
screw_clearance_diameter = clearance_hole_d(hardware_size, hardware_fit_class, material_profile, nozzle_diameter);
screw_head_pocket_diameter = counterbore_d(hardware_size, hardware_fit_class, material_profile, nozzle_diameter);
screw_head_depth = counterbore_depth(hardware_size, 0.40);
use_countersink = false;
use_counterbore = true;

wall_hole_spacing = 46;
wall_hole_height = 42;
shelf_hole_spacing = 46;
shelf_hole_y = 38;

rib_count = 2;
rib_thickness = 5.0;
rib_inset = 18;
rib_y_clearance = 6;
rib_z_clearance = 8;

edge_chamfer = 0.8;

export_part = "main"; // main, left, right
split_part = "none"; // none, left, right

// -------------------------
// Helper Modules
// -------------------------
module wall_screw_hole(x_pos, z_pos) {
    translate([x_pos, wall_thickness + 1, z_pos])
        rotate([90, 0, 0])
            cylinder(h = wall_thickness + 2, d = screw_clearance_diameter);
}

module shelf_screw_hole(x_pos, y_pos) {
    translate([x_pos, y_pos, -1])
        cylinder(h = wall_thickness + 2, d = screw_clearance_diameter);
}

module wall_head_pocket(x_pos, z_pos) {
    if (use_counterbore) {
        translate([x_pos, wall_thickness - screw_head_depth, z_pos])
            rotate([90, 0, 0])
                cylinder(h = screw_head_depth + 1, d = screw_head_pocket_diameter);
    } else if (use_countersink) {
        translate([x_pos, wall_thickness - screw_head_depth, z_pos])
            rotate([90, 0, 0])
                cylinder(h = screw_head_depth + 1, d1 = screw_head_pocket_diameter, d2 = screw_clearance_diameter);
    }
}

module shelf_head_pocket(x_pos, y_pos) {
    if (use_counterbore) {
        translate([x_pos, y_pos, wall_thickness - screw_head_depth])
            cylinder(h = screw_head_depth + 1, d = screw_head_pocket_diameter);
    } else if (use_countersink) {
        translate([x_pos, y_pos, wall_thickness - screw_head_depth])
            cylinder(h = screw_head_depth + 1, d1 = screw_clearance_diameter, d2 = screw_head_pocket_diameter);
    }
}

module triangular_rib(x_center) {
    x0 = x_center - rib_thickness / 2;
    x1 = x_center + rib_thickness / 2;
    y0 = wall_thickness;
    y1 = bracket_depth - rib_y_clearance;
    z0 = wall_thickness;
    z1 = bracket_height - rib_z_clearance;

    polyhedron(
        points = [
            [x0, y0, z0],
            [x0, y1, z0],
            [x0, y0, z1],
            [x1, y0, z0],
            [x1, y1, z0],
            [x1, y0, z1]
        ],
        faces = [
            [0, 2, 1],
            [3, 4, 5],
            [0, 1, 4, 3],
            [0, 3, 5, 2],
            [1, 2, 5, 4]
        ]
    );
}

module split_keep_volume(side) {
    if (side == "left") {
        translate([-bracket_width / 2 - 1, -1, -1])
            cube([bracket_width / 2 + 1, bracket_depth + 2, bracket_height + 2]);
    } else if (side == "right") {
        translate([0, -1, -1])
            cube([bracket_width / 2 + 1, bracket_depth + 2, bracket_height + 2]);
    }
}

// -------------------------
// Body Modules
// -------------------------
module solid_bracket() {
    union() {
        translate([-bracket_width / 2, 0, 0])
            cube([bracket_width, bracket_depth, wall_thickness]);

        translate([-bracket_width / 2, 0, 0])
            cube([bracket_width, wall_thickness, bracket_height]);

        triangular_rib(-rib_inset);
        triangular_rib(rib_inset);
    }
}

module bracket_with_holes() {
    difference() {
        solid_bracket();

        for (x_pos = [-wall_hole_spacing / 2, wall_hole_spacing / 2]) {
            wall_screw_hole(x_pos, wall_hole_height);
            wall_head_pocket(x_pos, wall_hole_height);
        }

        for (x_pos = [-shelf_hole_spacing / 2, shelf_hole_spacing / 2]) {
            shelf_screw_hole(x_pos, shelf_hole_y);
            shelf_head_pocket(x_pos, shelf_hole_y);
        }
    }
}

module selected_part() {
    if (export_part == "left" || split_part == "left") {
        intersection() {
            bracket_with_holes();
            split_keep_volume("left");
        }
    } else if (export_part == "right" || split_part == "right") {
        intersection() {
            bracket_with_holes();
            split_keep_volume("right");
        }
    } else {
        bracket_with_holes();
    }
}

// -------------------------
// Final Render
// -------------------------
module final_render() {
    selected_part();
}

final_render();
