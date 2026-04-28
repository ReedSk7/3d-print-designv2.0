// project_stem: example_project
// version: v01
// units: millimeters
// orientation: Z+ is up
// printer_name: Bambu Lab P2S
// material: PETG
// print_orientation: largest flat face on bed
// support_notes: update before export
// brim_notes: update before export

$fn = 64;

// -------------------------
// Parameters
// -------------------------
project_stem = "example_project";
version = "v01";
printer_name = "Bambu Lab P2S";
material = "PETG";

clearance_profile = "normal_slip";
loose_clearance = 0.5;
normal_clearance = 0.3;
tight_clearance = 0.15;
fit_clearance = normal_clearance;

part_width = 60;
part_depth = 30;
part_height = 12;
wall_thickness = 3.2;

screw_diameter = 4.5;
screw_head_diameter = 8.5;
screw_head_depth = 3;
use_countersink = false;
use_counterbore = true;

rib_thickness = 2.4;
rib_height = 10;
edge_chamfer = 0.8;

export_part = "main";
split_part = "none"; // none, left, right

// -------------------------
// Helper Modules
// -------------------------
module rounded_box(size_vec, radius = 1) {
    // Simple editable box. Add real fillets only where needed.
    cube(size_vec);
}

module screw_clearance_hole(height) {
    cylinder(h = height, d = screw_diameter + fit_clearance);
}

module screw_head_pocket(depth) {
    if (use_counterbore) {
        cylinder(h = depth, d = screw_head_diameter + fit_clearance);
    } else if (use_countersink) {
        cylinder(h = depth, d1 = screw_head_diameter + fit_clearance, d2 = screw_diameter + fit_clearance);
    }
}

module reinforcement_rib(length) {
    linear_extrude(height = rib_thickness)
        polygon(points = [[0, 0], [length, 0], [0, rib_height]]);
}

// -------------------------
// Body Modules
// -------------------------
module main_body() {
    difference() {
        rounded_box([part_width, part_depth, part_height], edge_chamfer);
        translate([part_width * 0.3, part_depth / 2, -1])
            screw_clearance_hole(part_height + 2);
        translate([part_width * 0.7, part_depth / 2, -1])
            screw_clearance_hole(part_height + 2);
        translate([part_width * 0.3, part_depth / 2, part_height - screw_head_depth])
            screw_head_pocket(screw_head_depth + 1);
        translate([part_width * 0.7, part_depth / 2, part_height - screw_head_depth])
            screw_head_pocket(screw_head_depth + 1);
    }
}

module reinforced_part() {
    union() {
        main_body();
        translate([8, part_depth / 2 - rib_thickness / 2, part_height])
            reinforcement_rib(18);
    }
}

// -------------------------
// Final Render
// -------------------------
module final_render() {
    if (export_part == "main") {
        reinforced_part();
    }
}

final_render();
