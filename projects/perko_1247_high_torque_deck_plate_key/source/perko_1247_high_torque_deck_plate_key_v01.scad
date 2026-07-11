use <../../../standards/hardware_library.scad>

// project_stem: perko_1247_high_torque_deck_plate_key
// version: v01
// task_mode: reference_based_reconstruction
// units: millimeters
// orientation: Z+ is up
// print_orientation: rotate onto a side face so the lugs lie flat in the slicer
// support_notes: supports expected under lug/root-relief areas after side rotation
// brim_notes: brim recommended for the long side-print orientation

$fn = 96;

// -------------------------
// Project Parameters
// -------------------------
project_stem = "perko_1247_high_torque_deck_plate_key";
version = "v01";
printer_name = "FDM printer";
material = "petg";
nozzle_diameter = 0.4;
wall_thickness = 3.2;
fit_clearance = 0.15 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter);

selected_variant = is_undef(export_variant) ? "printed_lugs" : export_variant; // printed_lugs, metal_pin_body

origin_x = 0;
origin_y = 0;
origin_z = 0;
slice_thickness = 0.05;
cutter_overlap = 0.4;
mm_4_5 = 4.5;
mm_5_0 = 5.0;
mm_5_2 = 5.2;

// -------------------------
// Authoritative Mating Geometry
// -------------------------
lug_center_spacing = 28.58;
lug_center_y_offset = lug_center_spacing / 2;
lug_tip_d = mm_4_5;
lug_base_d = mm_5_2;
lug_protrusion = 19.05;

// -------------------------
// Handle And Strength Geometry
// -------------------------
handle_total_length = 100;
body_thickness = 11;
head_width = 48;
handle_tail_width = 24;
head_center_x = head_width / 2;
tail_center_x = handle_total_length - (handle_tail_width / 2);
lug_center_x = head_center_x;
edge_chamfer = 1.6;

root_fillet_radius = 3.8;
root_relief_height = root_fillet_radius;
root_relief_d = lug_base_d + (2 * root_fillet_radius);
root_relief_start_z = -root_relief_height;
lug_shaft_length = lug_protrusion - root_relief_height;

metal_pin_nominal_d = mm_5_0;
metal_pin_hole_d = metal_pin_nominal_d - 0.2;
metal_pin_boss_d = metal_pin_nominal_d + 13;
metal_pin_top_boss_height = 3.2;
metal_pin_bottom_boss_height = 4.0;
metal_pin_hole_depth = body_thickness + metal_pin_top_boss_height + metal_pin_bottom_boss_height + (2 * cutter_overlap);

// -------------------------
// 2D Footprint And Body
// -------------------------
module spade_footprint_2d() {
    hull() {
        translate([head_center_x, origin_y])
            circle(d = head_width);
        translate([tail_center_x, origin_y])
            circle(d = handle_tail_width);
    }
}

module footprint_layer(layer_z, inset) {
    translate([origin_x, origin_y, layer_z])
        linear_extrude(height = slice_thickness)
            offset(delta = -inset)
                spade_footprint_2d();
}

module chamfered_spade_body() {
    union() {
        hull() {
            footprint_layer(origin_z, edge_chamfer);
            footprint_layer(edge_chamfer, origin_z);
        }

        translate([origin_x, origin_y, edge_chamfer])
            linear_extrude(height = body_thickness - (2 * edge_chamfer))
                spade_footprint_2d();

        hull() {
            footprint_layer(body_thickness - edge_chamfer - slice_thickness, origin_z);
            footprint_layer(body_thickness - slice_thickness, edge_chamfer);
        }
    }
}

// -------------------------
// Printed Lug Variant
// -------------------------
module tapered_lug_shaft() {
    translate([origin_x, origin_y, -lug_protrusion])
        cylinder(h = lug_shaft_length, d1 = lug_tip_d, d2 = lug_base_d);
}

module lug_root_stress_relief() {
    translate([origin_x, origin_y, root_relief_start_z])
        cylinder(h = root_relief_height, d1 = lug_base_d, d2 = root_relief_d);
}

module printed_lug() {
    union() {
        tapered_lug_shaft();
        lug_root_stress_relief();
    }
}

module printed_lug_set() {
    for (lug_y = [-lug_center_y_offset, lug_center_y_offset]) {
        translate([lug_center_x, lug_y, origin_z])
            printed_lug();
    }
}

module printed_lug_key() {
    union() {
        chamfered_spade_body();
        printed_lug_set();
    }
}

// -------------------------
// Metal Pin Variant
// -------------------------
module metal_pin_boss_pair() {
    for (pin_y = [-lug_center_y_offset, lug_center_y_offset]) {
        translate([lug_center_x, pin_y, -metal_pin_bottom_boss_height])
            cylinder(h = metal_pin_bottom_boss_height, d = metal_pin_boss_d);

        translate([lug_center_x, pin_y, body_thickness])
            cylinder(h = metal_pin_top_boss_height, d = metal_pin_boss_d);
    }
}

module metal_pin_hole_pair() {
    for (pin_y = [-lug_center_y_offset, lug_center_y_offset]) {
        translate([
            lug_center_x,
            pin_y,
            -metal_pin_bottom_boss_height - cutter_overlap
        ])
            cylinder(h = metal_pin_hole_depth, d = metal_pin_hole_d);
    }
}

module metal_pin_body() {
    difference() {
        union() {
            chamfered_spade_body();
            metal_pin_boss_pair();
        }
        metal_pin_hole_pair();
    }
}

// -------------------------
// Final Render
// -------------------------
module final_render() {
    if (selected_variant == "metal_pin_body") {
        metal_pin_body();
    } else {
        printed_lug_key();
    }
}

final_render();
