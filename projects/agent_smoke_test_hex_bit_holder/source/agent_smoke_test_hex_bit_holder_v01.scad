// project_stem: agent_smoke_test_hex_bit_holder
// version: v01
// task_mode: original_product_design
// units: millimeters
// orientation: Z+ is up
// printer_name: Bambu Lab P2S
// material: PETG
// print_orientation: bottom/base face flat on bed; pockets open upward in model coordinates
// support_notes: designed for no supports in pocket-first print orientation

$fn = 72;

// -------------------------
// Main parameters
// -------------------------
project_stem = "agent_smoke_test_hex_bit_holder";
version = "v01";
printer_name = "Bambu Lab P2S";
material = "PETG";

// Bit pocket controls. The hex pocket uses across-flats sizing.
bit_count = 6;
bit_nominal_size = 6.35;
pocket_clearance = 0.35;
pocket_across_flats = bit_nominal_size + pocket_clearance;
pocket_corner_diameter = pocket_across_flats / cos(30);
pocket_depth = 18;
pocket_spacing = 12.5;
pocket_chamfer_depth = 1.6;
pocket_chamfer_extra = 1.4;

// Holder body controls.
holder_width = 90;
holder_height = 45;
holder_depth = 22;
wall_thickness = 3;
edge_chamfer = 0.8;

// Screw mounting controls.
screw_diameter = 4.5;
screw_spacing = 65;
screw_z = 12;
screw_boss_diameter = 15;
screw_boss_depth = 2.4;
countersink_enable = true;
countersink_diameter = 9.5;
countersink_depth = 2.6;

// Label controls.
label_text = "BITS";
label_size = 8;
label_raise = 0.8;
label_z = 27;

export_part = "main";

// -------------------------
// Helper modules
// -------------------------
module y_cylinder(diameter, length, center_flag = false) {
    rotate([-90, 0, 0])
        cylinder(h = length, d = diameter, center = center_flag);
}

module y_taper(diameter_inner, diameter_outer, length) {
    rotate([-90, 0, 0])
        cylinder(h = length, d1 = diameter_inner, d2 = diameter_outer);
}

module x_centered_cube(size_vec) {
    translate([-size_vec[0] / 2, 0, 0])
        cube(size_vec);
}

module top_edge_chamfers() {
    // Small subtractive bevels on exposed upper front/back edges.
    translate([-holder_width / 2 - 1, holder_depth - edge_chamfer, holder_height - edge_chamfer])
        rotate([45, 0, 0])
            cube([holder_width + 2, edge_chamfer * 2, edge_chamfer * 2]);

    translate([-holder_width / 2 - 1, -edge_chamfer, holder_height - edge_chamfer])
        rotate([45, 0, 0])
            cube([holder_width + 2, edge_chamfer * 2, edge_chamfer * 2]);
}

module screw_boss(x_pos) {
    translate([x_pos, holder_depth, screw_z])
        y_cylinder(screw_boss_diameter, screw_boss_depth);
}

module screw_hole(x_pos) {
    translate([x_pos, -1, screw_z])
        y_cylinder(screw_diameter, holder_depth + screw_boss_depth + 3);
}

module screw_countersink(x_pos) {
    if (countersink_enable) {
        translate([x_pos, holder_depth + screw_boss_depth - countersink_depth, screw_z])
            y_taper(screw_diameter, countersink_diameter, countersink_depth + 0.4);
    }
}

module hex_bit_pocket(x_pos) {
    translate([x_pos, holder_depth / 2, holder_height - pocket_depth])
        cylinder(h = pocket_depth + 1, d = pocket_corner_diameter, $fn = 6);

    translate([x_pos, holder_depth / 2, holder_height - pocket_chamfer_depth])
        cylinder(
            h = pocket_chamfer_depth + 0.2,
            d1 = pocket_corner_diameter,
            d2 = (pocket_across_flats + pocket_chamfer_extra) / cos(30),
            $fn = 6
        );
}

module bit_pockets() {
    first_x = -pocket_spacing * (bit_count - 1) / 2;
    for (index = [0 : bit_count - 1]) {
        hex_bit_pocket(first_x + index * pocket_spacing);
    }
}

module raised_label() {
    translate([0, holder_depth + label_raise, label_z])
        rotate([90, 0, 0])
            linear_extrude(height = label_raise)
                text(label_text, size = label_size, halign = "center", valign = "center");
}

// -------------------------
// Body modules
// -------------------------
module holder_solid() {
    union() {
        x_centered_cube([holder_width, holder_depth, holder_height]);

        for (x_pos = [-screw_spacing / 2, screw_spacing / 2]) {
            screw_boss(x_pos);
        }

        raised_label();
    }
}

module holder_cutouts() {
    union() {
        bit_pockets();

        for (x_pos = [-screw_spacing / 2, screw_spacing / 2]) {
            screw_hole(x_pos);
            screw_countersink(x_pos);
        }

        top_edge_chamfers();
    }
}

module hex_bit_holder() {
    difference() {
        holder_solid();
        holder_cutouts();
    }
}

// -------------------------
// Final render
// -------------------------
module final_render() {
    if (export_part == "main") {
        hex_bit_holder();
    }
}

final_render();
