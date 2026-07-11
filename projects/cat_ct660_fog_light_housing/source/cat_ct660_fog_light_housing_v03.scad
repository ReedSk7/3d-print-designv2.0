$fn = 88;

// CAT CT660 fog light housing / bucket
// reference_based_reconstruction
//
// v03 is a refinement pass on v02, with improved cavity sectioning
// and further validation against the user-provided CT660 reference photos.
// All dimensions anchored to user estimate (~254 mm width) and photo-derived proportions.

overall_width = 254;
overall_height = 156;          // v03: refined from photo aspect analysis
body_depth = 92;               // v03: refined profile depth

front_lip_depth = 10;
rear_wall_thickness = 9;
shell_corner_radius = 6;

front_cavity_inset = 10;
mid_cavity_inset = 13;         // v03: increased for better taper
rear_cavity_inset = 16;

collar_center_x = 80;
collar_center_z = 63;          // v03: adjusted from photo measurement
collar_outer_d = 110;
collar_rear_pad_d = 126;
collar_seat_d = 97;
collar_clear_d = 88;
collar_front_projection = 16;
collar_seat_depth = 5.5;

lamp_screw_circle_d = 108;
lamp_screw_boss_d = 10;
lamp_screw_boss_h = 8;
lamp_screw_hole_d = 4.2;
lamp_screw_angles = [40, 132, 228, 320];

rear_stud_boss_d = 19;
rear_stud_boss_h = 8;
rear_stud_d = 7;
rear_stud_h = 18;

rear_rib_radius = 4.5;

outer_profile_pts = [
    [0, 18],
    [6, 8],
    [18, 0],
    [194, 0],
    [228, 4],
    [248, 16],
    [254, 32],
    [254, 114],
    [247, 134],
    [225, 143],
    [88, 156],
    [40, 136],
    [8, 94]
];

outer_section_specs = [
    [0, 0, 0, 0],
    [18, 1, 3, 2],
    [42, 2, 8, 5],
    [body_depth, 7, 18, 10]
];

cavity_section_specs = [
    [front_lip_depth, front_cavity_inset, 2, 2],
    [24, front_cavity_inset + 1, 5, 4],
    [54, mid_cavity_inset, 13, 8],
    [body_depth - rear_wall_thickness, rear_cavity_inset, 24, 12]
];

rear_stud_positions = [
    [30, 38],
    [222, 121],
    [221, 36]
];

rear_stud_anchors = [
    [[17, 0], [6, 14], [0, -15]],
    [[-19, 0], [-8, -15], [0, -18]],
    [[-19, 0], [-8, 13], [0, 16]]
];

rear_ribs = [
    [[136, 84], [210, 113]],
    [[146, 56], [209, 43]],
    [[130, 73], [188, 77]]
];

module rounded_profile_2d(inset = 0, dx = 0, dz = 0) {
    translate([dx, dz])
        offset(r = shell_corner_radius)
            offset(delta = -shell_corner_radius)
                offset(delta = -inset)
                    polygon(points = outer_profile_pts);
}

module rounded_rect_2d(size = [10, 10], radius = 2) {
    offset(r = radius)
        offset(delta = -radius)
            square(size, center = false);
}

module xz_slice(y_pos, inset = 0, dx = 0, dz = 0, thickness = 0.6) {
    translate([0, y_pos, 0])
        rotate([90, 0, 0])
            linear_extrude(height = thickness, center = true, convexity = 10)
                rounded_profile_2d(inset = inset, dx = dx, dz = dz);
}

module hulled_sections(section_specs) {
    hull()
        for (section = section_specs)
            xz_slice(
                y_pos = section[0],
                inset = section[1],
                dx = section[2],
                dz = section[3]
            );
}

module outer_body() {
    hulled_sections(outer_section_specs);
}

module cavity_void() {
    hulled_sections(cavity_section_specs);
}

module collar_positive() {
    translate([collar_center_x, body_depth - rear_wall_thickness - collar_front_projection, collar_center_z])
        rotate([-90, 0, 0])
            cylinder(h = collar_front_projection + 0.01, d = collar_outer_d);

    translate([collar_center_x, body_depth - rear_wall_thickness, collar_center_z])
        rotate([-90, 0, 0])
            cylinder(h = rear_wall_thickness, d = collar_rear_pad_d);
}

module collar_negative() {
    translate([collar_center_x, body_depth - rear_wall_thickness - collar_front_projection - 0.5, collar_center_z])
        rotate([-90, 0, 0])
            cylinder(h = collar_front_projection + collar_seat_depth + 1.0, d = collar_seat_d);

    translate([collar_center_x, body_depth - rear_wall_thickness - 0.5, collar_center_z])
        rotate([-90, 0, 0])
            cylinder(h = rear_wall_thickness + 2.0, d = collar_clear_d);
}

module lamp_screw_boss(angle_deg) {
    screw_radius = lamp_screw_circle_d / 2;
    px = collar_center_x + screw_radius * cos(angle_deg);
    pz = collar_center_z + screw_radius * sin(angle_deg);

    translate([px, body_depth, pz])
        rotate([-90, 0, 0])
            cylinder(h = lamp_screw_boss_h, d = lamp_screw_boss_d);
}

module lamp_screw_hole(angle_deg) {
    screw_radius = lamp_screw_circle_d / 2;
    px = collar_center_x + screw_radius * cos(angle_deg);
    pz = collar_center_z + screw_radius * sin(angle_deg);

    translate([px, body_depth + lamp_screw_boss_h / 2, pz])
        rotate([-90, 0, 0])
            cylinder(
                h = rear_wall_thickness + lamp_screw_boss_h + 4,
                d = lamp_screw_hole_d,
                center = true
            );
}

module rear_mount_boss(center_pos, anchor_pts) {
    cx = center_pos[0];
    cz = center_pos[1];

    translate([cx, body_depth, cz])
        rotate([-90, 0, 0])
            cylinder(h = rear_stud_boss_h, d = rear_stud_boss_d);

    translate([cx, body_depth + rear_stud_boss_h, cz])
        rotate([-90, 0, 0])
            cylinder(h = rear_stud_h, d = rear_stud_d);

    for (anchor = anchor_pts)
        hull() {
            translate([cx, body_depth + rear_stud_boss_h * 0.55, cz])
                sphere(r = rear_stud_boss_d * 0.22);
            translate([cx + anchor[0], body_depth + 0.8, cz + anchor[1]])
                sphere(r = rear_stud_boss_d * 0.14);
        }
}

module rear_rib(start_pt, end_pt) {
    hull() {
        translate([start_pt[0], body_depth + 1.1, start_pt[1]])
            sphere(r = rear_rib_radius);
        translate([end_pt[0], body_depth + 1.1, end_pt[1]])
            sphere(r = rear_rib_radius);
    }
}

module rear_panel_recess() {
    translate([112, body_depth - rear_wall_thickness - 0.6, 42])
        rotate([90, 0, 0])
            linear_extrude(height = 2.6, center = false, convexity = 4)
                rounded_rect_2d(size = [56, 34], radius = 4);
}

module housing_shell() {
    difference() {
        union() {
            outer_body();
            collar_positive();

            for (angle_deg = lamp_screw_angles)
                lamp_screw_boss(angle_deg);

            for (idx = [0 : len(rear_stud_positions) - 1])
                rear_mount_boss(rear_stud_positions[idx], rear_stud_anchors[idx]);

            for (rib = rear_ribs)
                rear_rib(rib[0], rib[1]);
        }

        cavity_void();
        collar_negative();
        rear_panel_recess();

        for (angle_deg = lamp_screw_angles)
            lamp_screw_hole(angle_deg);
    }
}

housing_shell();
