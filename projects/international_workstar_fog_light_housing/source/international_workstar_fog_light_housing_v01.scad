$fn = 96;

// Best-faith parametric reconstruction from user photos for an International
// dump-truck fog light housing, likely in the WorkStar / 7000-series family.
// The ~254 mm overall width is a soft anchor from the user and remains
// measurement-gated for later refinement.

overall_width = 254;
overall_height = 149;
body_depth = 82;

front_lip_depth = 9;
rear_wall_thickness = 9;
shell_corner_radius = 5;

front_cavity_inset = 11;
mid_cavity_inset = 13;
rear_cavity_inset = 15;

collar_center_x = 82;
collar_center_z = 63;
collar_outer_d = 108;
collar_rear_pad_d = 124;
collar_seat_d = 96;
collar_clear_d = 88;
collar_front_projection = 16;
collar_seat_depth = 5;

lamp_screw_circle_d = 108;
lamp_screw_boss_d = 10;
lamp_screw_boss_h = 8;
lamp_screw_hole_d = 4.2;
lamp_screw_angles = [38, 132, 228, 320];

rear_stud_boss_d = 19;
rear_stud_boss_h = 8;
rear_stud_d = 7;
rear_stud_h = 18;

outer_profile_pts = [
    [0, 10],
    [6, 0],
    [198, 0],
    [236, 4],
    [254, 18],
    [254, 126],
    [244, 144],
    [80, 149],
    [32, 136],
    [4, 92]
];

outer_section_specs = [
    [0, 0, 0, 0],
    [34, 2, 6, 4],
    [82, 6, 16, 9]
];

cavity_section_specs = [
    [front_lip_depth, front_cavity_inset, 2, 2],
    [46, mid_cavity_inset, 12, 6],
    [body_depth - rear_wall_thickness, rear_cavity_inset, 22, 11]
];

rear_stud_positions = [
    [28, 38],
    [223, 122],
    [220, 37]
];

rear_stud_anchors = [
    [[16, 0], [6, 13], [0, -14]],
    [[-18, 0], [-8, -14], [0, -18]],
    [[-18, 0], [-8, 12], [0, 16]]
];

module rounded_profile_2d(inset = 0, dx = 0, dz = 0) {
    translate([dx, dz])
        offset(r = shell_corner_radius)
            offset(delta = -shell_corner_radius)
                offset(delta = -inset)
                    polygon(points = outer_profile_pts);
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
            cylinder(h = collar_front_projection + collar_seat_depth + 1, d = collar_seat_d);

    translate([collar_center_x, body_depth - rear_wall_thickness - 0.5, collar_center_z])
        rotate([-90, 0, 0])
            cylinder(h = rear_wall_thickness + 2, d = collar_clear_d);
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

module housing_shell() {
    difference() {
        union() {
            outer_body();
            collar_positive();

            for (angle_deg = lamp_screw_angles)
                lamp_screw_boss(angle_deg);

            for (idx = [0 : len(rear_stud_positions) - 1])
                rear_mount_boss(rear_stud_positions[idx], rear_stud_anchors[idx]);
        }

        cavity_void();
        collar_negative();

        for (angle_deg = lamp_screw_angles)
            lamp_screw_hole(angle_deg);
    }
}

housing_shell();
