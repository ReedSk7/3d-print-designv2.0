$fn = 64;

// CAT CT660 fog light housing / bucket
// reference_based_reconstruction
//
// v04 rebuilds the housing around the user-photo silhouette and anchors:
// - locked 254 mm overall width
// - left-shifted fog lamp collar
// - deeper right-side cavity
// - non-rectangular three-stud mounting layout
// - swept trapezoidal mouth instead of a generic rounded rectangle

overall_width = 254;
overall_height = 150;
overall_depth = 116;
wall_thickness = 3.5;
front_flange_width = 7.5;

collar_outer_diameter = 106;
collar_inner_diameter = 87;
collar_front_projection = 11;
collar_center_x = 68;
collar_center_y = 92; // measured from top edge in the photo notes

main_stud_positions = [
    [31, 103],
    [213, 27],
    [231, 109]
];
main_stud_diameter = 10;
main_stud_hole_diameter = 6.5;

small_collar_boss_angles_deg = [135, 35, 235];
small_collar_boss_diameter = 12;

curvature_primary = 16;
curvature_secondary = 8;
cavity_taper = 0.22;

corner_radius = 6.5;
front_face_thickness = wall_thickness + 1.25;
rear_wall_thickness = wall_thickness + 2.25;
main_boss_diameter = main_stud_diameter + 12;
main_boss_height = 7;
main_stud_length = 8;
small_collar_boss_height = wall_thickness + 4.5;
small_collar_boss_hole_diameter = 4.2;
small_collar_boss_radius = collar_outer_diameter / 2 + 8.5;
rear_collar_raise = wall_thickness + 1.5;
seat_rebate_depth = wall_thickness + 1.0;
seat_rebate_diameter = collar_inner_diameter + 10;

collar_center_z = overall_height - collar_center_y;
cavity_rear_stop = overall_depth - rear_wall_thickness;
right_edge_trim = 0.4;

outer_profile_pts = [
    [8, 16],
    [20, 5],
    [44, 0],
    [178, 0],
    [224, 3],
    [246 - right_edge_trim, 14],
    [overall_width - right_edge_trim, 36],
    [overall_width - right_edge_trim, 118],
    [247, 138],
    [229, 147],
    [191, 149],
    [146, 150],
    [92, 146],
    [49, 138],
    [19, 122],
    [4, 95],
    [0, 68],
    [0, 34]
];

outer_section_specs = [
    [0, 0.0, 0.0, 0.0],
    [18, 1.2, 1.3, 0.5],
    [44, 2.6, 2.9, 1.0],
    [76, 4.4, 4.8, 1.8],
    [overall_depth, 6.1, 6.0, 2.6]
];

cavity_section_specs = [
    [front_face_thickness, front_flange_width, 0.5, 0.4],
    [26, front_flange_width + wall_thickness * 0.55, 1.5, 0.9],
    [58, front_flange_width + wall_thickness * (1.15 + cavity_taper), 3.2, 1.8],
    [cavity_rear_stop, front_flange_width + wall_thickness * (2.05 + cavity_taper * 2.0), 5.8, 3.0]
];

main_stud_anchor_offsets = [
    [[13, 18], [25, 4], [22, -16]],
    [[-18, -18], [-27, -5], [-13, -29]],
    [[-21, 16], [-28, 2], [-18, -14]]
];

panel_rib_pairs = [
    [[112, overall_depth + 0.8, 40], [196, overall_depth + 0.8, 41]],
    [[126, overall_depth + 0.8, 96], [205, overall_depth + 0.8, 112]]
];

function top_to_z(y_from_top) = overall_height - y_from_top;

function stud_center(index) = [
    main_stud_positions[index][0],
    top_to_z(main_stud_positions[index][1])
];

function collar_boss_center(angle_deg) = [
    collar_center_x + small_collar_boss_radius * cos(angle_deg),
    collar_center_z + small_collar_boss_radius * sin(angle_deg)
];

module rounded_profile_2d(points, inset = 0, dx = 0, dz = 0, radius = corner_radius) {
    translate([dx, dz])
        offset(r = radius)
            offset(delta = -radius)
                offset(delta = -inset)
                    polygon(points = points);
}

module rounded_rect_2d(size = [10, 10], radius = 2) {
    offset(r = radius)
        offset(delta = -radius)
            square(size, center = false);
}

module blend_ball(radius) {
    sphere(r = radius, $fn = 18);
}

module profile_slice(points, y_pos, inset = 0, dx = 0, dz = 0, thickness = 0.8) {
    translate([0, y_pos, 0])
        rotate([90, 0, 0])
            linear_extrude(height = thickness, center = true, convexity = 12)
                rounded_profile_2d(points = points, inset = inset, dx = dx, dz = dz);
}

module hulled_sections(points, section_specs) {
    hull()
        for (section = section_specs)
            profile_slice(
                points = points,
                y_pos = section[0],
                inset = section[1],
                dx = section[2],
                dz = section[3]
            );
}

module front_opening_profile(extra_inset = 0) {
    rounded_profile_2d(points = outer_profile_pts, inset = front_flange_width + extra_inset);
}

module base_outer_envelope() {
    blended_exterior_surfaces();
}

module blended_exterior_surfaces() {
    union() {
        hulled_sections(outer_profile_pts, outer_section_specs);

        // Local contour pads keep the rear upper body from collapsing into a box.
        hull() {
            translate([142, 38, 128])
                blend_ball(curvature_secondary * 0.9);
            translate([219, overall_depth - 6, 118])
                blend_ball(curvature_primary * 0.55);
            translate([204, overall_depth - 12, 88])
                blend_ball(curvature_secondary);
        }

        hull() {
            translate([36, 22, 16])
                blend_ball(curvature_secondary * 0.85);
            translate([72, overall_depth - 10, 42])
                blend_ball(curvature_secondary * 0.9);
        }
    }
}

module internal_cavity() {
    union() {
        hulled_sections(outer_profile_pts, cavity_section_specs);

        // The right half is visibly deeper and more vertical in the user photos.
        hull() {
            translate([118, 20, 18])
                rotate([90, 0, 0])
                    linear_extrude(height = 0.8, center = true, convexity = 8)
                        rounded_rect_2d(size = [114, 111], radius = curvature_primary * 0.5);
            translate([124, 72, 22])
                rotate([90, 0, 0])
                    linear_extrude(height = 0.8, center = true, convexity = 8)
                        rounded_rect_2d(size = [104, 103], radius = curvature_primary * 0.45);
            translate([130, cavity_rear_stop, 26])
                rotate([90, 0, 0])
                    linear_extrude(height = 0.8, center = true, convexity = 8)
                        rounded_rect_2d(size = [96, 96], radius = curvature_primary * 0.4);
        }

        // A shallow upper transition keeps the roof of the bucket blended instead of flat.
        hull() {
            translate([72, 24, 106])
                blend_ball(curvature_secondary * 0.9);
            translate([166, 68, 118])
                blend_ball(curvature_secondary);
            translate([214, cavity_rear_stop - 6, 110])
                blend_ball(curvature_secondary * 0.85);
        }
    }
}

module circular_collar() {
    translate([collar_center_x, -collar_front_projection, collar_center_z])
        rotate([-90, 0, 0])
            cylinder(h = overall_depth + collar_front_projection + rear_collar_raise, d = collar_outer_diameter);

    // Blend the collar into the shell instead of leaving an abrupt tube intersection.
    hull() {
        translate([collar_center_x + 16, 10, collar_center_z + 14])
            blend_ball(curvature_secondary * 0.95);
        translate([collar_center_x + 46, 44, collar_center_z + 20])
            blend_ball(curvature_secondary * 1.1);
        translate([collar_center_x + 72, overall_depth - 8, collar_center_z + 12])
            blend_ball(curvature_secondary);
    }

    hull() {
        translate([collar_center_x + 12, 8, collar_center_z - 18])
            blend_ball(curvature_secondary * 0.9);
        translate([collar_center_x + 54, 38, collar_center_z - 26])
            blend_ball(curvature_secondary);
        translate([collar_center_x + 84, overall_depth - 8, collar_center_z - 18])
            blend_ball(curvature_secondary * 0.8);
    }
}

module collar_seating_lip() {
    translate([collar_center_x, overall_depth - seat_rebate_depth - 0.2, collar_center_z])
        rotate([-90, 0, 0])
            cylinder(h = seat_rebate_depth + 0.4, d = seat_rebate_diameter);
}

module collar_clearance() {
    translate([collar_center_x, -collar_front_projection - 0.6, collar_center_z])
        rotate([-90, 0, 0])
            cylinder(h = overall_depth + collar_front_projection + rear_collar_raise + 1.2, d = collar_inner_diameter);
}

module main_rear_bosses() {
    for (index = [0 : len(main_stud_positions) - 1]) {
        center = stud_center(index);
        cx = center[0];
        cz = center[1];

        translate([cx, overall_depth - 0.2, cz])
            rotate([-90, 0, 0])
                cylinder(h = main_boss_height, d = main_boss_diameter);

        translate([cx, overall_depth + main_boss_height - 0.2, cz])
            rotate([-90, 0, 0])
                cylinder(h = main_stud_length, d = main_stud_diameter);
    }
}

module main_boss_holes() {
    for (index = [0 : len(main_stud_positions) - 1]) {
        center = stud_center(index);
        translate([center[0], overall_depth - 0.4, center[1]])
            rotate([-90, 0, 0])
                cylinder(h = main_boss_height + main_stud_length + 1.0, d = main_stud_hole_diameter);
    }
}

module small_collar_bosses() {
    for (angle_deg = small_collar_boss_angles_deg) {
        center = collar_boss_center(angle_deg);
        px = center[0];
        pz = center[1];

        translate([px, overall_depth - 0.1, pz])
            rotate([-90, 0, 0])
                cylinder(h = small_collar_boss_height, d = small_collar_boss_diameter);

        hull() {
            translate([px, overall_depth + 1.6, pz])
                blend_ball(small_collar_boss_diameter * 0.24);
            translate([collar_center_x + (px - collar_center_x) * 0.52, overall_depth - 2.4, collar_center_z + (pz - collar_center_z) * 0.52])
                blend_ball(small_collar_boss_diameter * 0.16);
        }
    }
}

module small_collar_boss_holes() {
    for (angle_deg = small_collar_boss_angles_deg) {
        center = collar_boss_center(angle_deg);
        translate([center[0], overall_depth - 0.4, center[1]])
            rotate([-90, 0, 0])
                cylinder(h = small_collar_boss_height + 0.8, d = small_collar_boss_hole_diameter);
    }
}

module reinforcement_gussets() {
    union() {
        for (index = [0 : len(main_stud_positions) - 1]) {
            center = stud_center(index);
            cx = center[0];
            cz = center[1];

            for (anchor = main_stud_anchor_offsets[index])
                hull() {
                    translate([cx, overall_depth + main_boss_height * 0.45, cz])
                        blend_ball(main_boss_diameter * 0.18);
                    translate([cx + anchor[0], overall_depth + 0.5, cz + anchor[1]])
                        blend_ball(main_boss_diameter * 0.12);
                }
        }

        for (rib_pair = panel_rib_pairs)
            hull() {
                translate(rib_pair[0])
                    blend_ball(curvature_secondary * 0.45);
                translate(rib_pair[1])
                    blend_ball(curvature_secondary * 0.45);
            }
    }
}

module housing_body() {
    difference() {
        union() {
            base_outer_envelope();
            circular_collar();
            main_rear_bosses();
            small_collar_bosses();
            reinforcement_gussets();
        }

        translate([0, -0.6, 0])
            rotate([90, 0, 0])
                linear_extrude(height = cavity_rear_stop + 1.2, center = false, convexity = 12)
                    front_opening_profile();

        internal_cavity();
        collar_clearance();
        collar_seating_lip();
        main_boss_holes();
        small_collar_boss_holes();
    }
}

housing_body();
