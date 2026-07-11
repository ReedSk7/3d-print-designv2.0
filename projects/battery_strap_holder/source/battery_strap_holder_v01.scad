use <../../../standards/hardware_library.scad>

// project_stem: battery_strap_holder
// version: v01
// task_mode: reference_based_reconstruction
// units: millimeters
// orientation: Z+ is up
// material: petg
// nozzle_diameter: 0.6
// physical_fit_status: NOT VERIFIED

$fn = 96;

project_stem = "battery_strap_holder";
version = "v01";
printer_name = "high_performance_corexy_300";
material = "petg";
nozzle_diameter = 0.6;

// Geometry Contract: authoritative caliper/photo-correlated dimensions.
total_outer_length_y = 74.0;
inner_body_span_y = 50.2;
main_offset_step_height_z = 7.1;
tab_sub_thickness_z = 4.0;

// Geometry Contract: inferred but parametric dimensions.
overall_width_x = 11.0;
center_bridge_width_x = 8.5;
wall_thickness = (overall_width_x - center_bridge_width_x) / 2;
bolt_size = "m4";
screw_fit_class = "normal";
profile_calibrated_hole_compensation = 0.15;

// Derived dimensions.
tab_length_y = (total_outer_length_y - inner_body_span_y) / 2;
half_outer_length_y = total_outer_length_y / 2;
half_inner_span_y = inner_body_span_y / 2;
mounting_hole_center_y_abs = half_outer_length_y - (tab_length_y / 2);
fit_clearance = profile_calibrated_hole_compensation;
hardware_hole_d = clearance_hole_d(bolt_size, screw_fit_class, material, nozzle_diameter);
profile_hole_d = clearance_base_d(bolt_size, screw_fit_class) + profile_calibrated_hole_compensation;
mounting_hole_d = max(hardware_hole_d, profile_hole_d);
bridge_overlap_y = 1.0;
bridge_overlap_z = 0.2;
bridge_length_y = inner_body_span_y + (2 * bridge_overlap_y);
bridge_bottom_z = tab_sub_thickness_z - bridge_overlap_z;
bridge_height_z = main_offset_step_height_z - bridge_bottom_z;
cutter_overlap_z = 0.5;
cutter_height_z = main_offset_step_height_z + (2 * cutter_overlap_z);
minimum_radius_margin = 0.01;
tab_corner_radius = min(overall_width_x / 2, tab_length_y / 2) - minimum_radius_margin;
bridge_corner_radius = min(center_bridge_width_x / 2, bridge_length_y / 2) - minimum_radius_margin;

module rounded_rect_2d(width_x, length_y, radius) {
    safe_radius = max(0, min(radius, (width_x / 2) - minimum_radius_margin, (length_y / 2) - minimum_radius_margin));

    if (safe_radius <= 0) {
        square([width_x, length_y], center=true);
    } else {
        hull() {
            for (x_pos = [-(width_x / 2) + safe_radius, (width_x / 2) - safe_radius])
                for (y_pos = [-(length_y / 2) + safe_radius, (length_y / 2) - safe_radius])
                    translate([x_pos, y_pos])
                        circle(r=safe_radius);
        }
    }
}

module end_tab_footprint_2d() {
    rounded_rect_2d(overall_width_x, tab_length_y, tab_corner_radius);
}

module bridge_footprint_2d() {
    rounded_rect_2d(center_bridge_width_x, bridge_length_y, bridge_corner_radius);
}

module mounting_hole_cutters() {
    for (y_sign = [-1, 1]) {
        translate([0, y_sign * mounting_hole_center_y_abs, -cutter_overlap_z])
            cylinder(h=cutter_height_z, d=mounting_hole_d);
    }
}

module end_tabs() {
    for (y_sign = [-1, 1]) {
        translate([0, y_sign * (half_outer_length_y - (tab_length_y / 2)), 0])
            linear_extrude(height=tab_sub_thickness_z)
                end_tab_footprint_2d();
    }
}

module raised_center_bridge() {
    translate([0, 0, bridge_bottom_z])
        linear_extrude(height=bridge_height_z)
            bridge_footprint_2d();
}

module battery_strap_holder() {
    difference() {
        union() {
            end_tabs();
            raised_center_bridge();
        }
        mounting_hole_cutters();
    }
}

battery_strap_holder();
