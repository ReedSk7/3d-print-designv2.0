use <../../../standards/hardware_library.scad>

// project_stem: <project_stem>
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

part_width = 60;
part_depth = 30;
part_height = 12;
wall_thickness = 3.2;

bolt_size = "m4";
screw_fit_class = "normal";
screw_diameter = clearance_hole_d(bolt_size, screw_fit_class, material, nozzle_diameter);
screw_head_diameter = counterbore_d(bolt_size, screw_fit_class, material, nozzle_diameter);
screw_head_depth = counterbore_depth(bolt_size);
use_countersink = false;
use_counterbore = true;

rib_thickness = 2.4;
rib_height = 10;
edge_chamfer = 0.8;

cutter_overlap_z = 1;
cutter_extra_z = cutter_overlap_z * 2;
left_hole_x_ratio = 0.3;
right_hole_x_ratio = 0.7;
hole_center_y = part_depth / 2;
left_hole_x = part_width * left_hole_x_ratio;
right_hole_x = part_width * right_hole_x_ratio;
screw_head_pocket_z = part_height - screw_head_depth;
rib_offset_x = 8;
rib_length = 18;
rib_center_y = part_depth / 2 - rib_thickness / 2;

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
    clearance_hole(bolt_size, height, screw_fit_class, material, nozzle_diameter);
}

module screw_head_pocket(depth) {
    if (use_counterbore) {
        counterbore_pocket(bolt_size, depth, screw_fit_class, material, nozzle_diameter);
    } else if (use_countersink) {
        countersink_pocket(bolt_size, screw_fit_class, material, nozzle_diameter);
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
        translate([left_hole_x, hole_center_y, -cutter_overlap_z])
            screw_clearance_hole(part_height + cutter_extra_z);
        translate([right_hole_x, hole_center_y, -cutter_overlap_z])
            screw_clearance_hole(part_height + cutter_extra_z);
        translate([left_hole_x, hole_center_y, screw_head_pocket_z])
            screw_head_pocket(screw_head_depth + cutter_overlap_z);
        translate([right_hole_x, hole_center_y, screw_head_pocket_z])
            screw_head_pocket(screw_head_depth + cutter_overlap_z);
    }
}

module reinforced_part() {
    union() {
        main_body();
        translate([rib_offset_x, rib_center_y, part_height])
            reinforcement_rib(rib_length);
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
