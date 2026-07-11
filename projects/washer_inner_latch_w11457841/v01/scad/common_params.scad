// Common utilities for the W11457841 inner latch insert project
// Units: millimeters

$fn = 72;
eps = 0.02;

module extrude_x(width, center = true) {
    rotate([0, 90, 0])
        linear_extrude(height = width, center = center, convexity = 10)
            children();
}

module rounded_square_2d(size = [10, 10], r = 1.0) {
    sx = max(size[0], 0.1);
    sy = max(size[1], 0.1);
    rr = min(r, min(sx, sy) / 2 - 0.01);

    if (rr <= 0)
        square([sx, sy], center = true);
    else
        hull()
            for (x_sign = [-1, 1])
            for (y_sign = [-1, 1])
                translate([
                    x_sign * (sx / 2 - rr),
                    y_sign * (sy / 2 - rr)
                ])
                    circle(r = rr);
}

module rounded_block(size = [10, 10, 10], r = 1.0, center = true) {
    z_center = center ? 0 : size[2] / 2;

    translate([0, 0, z_center])
        linear_extrude(height = size[2], center = center, convexity = 10)
            rounded_square_2d([size[0], size[1]], r = r);
}

module cylinder_x(length = 10, d = 3, center = true) {
    rotate([0, 90, 0])
        cylinder(h = length, d = d, center = center);
}

module lead_in_bar(length = 10, d = 3, taper = 0.5) {
    union() {
        cylinder_x(length = max(0.1, length - 2 * taper), d = d, center = true);

        translate([length / 2 - taper / 2, 0, 0])
            rotate([0, 90, 0])
                cylinder(h = taper, d1 = d, d2 = max(0.2, d - 2 * taper), center = true);

        translate([-length / 2 + taper / 2, 0, 0])
            rotate([0, -90, 0])
                cylinder(h = taper, d1 = d, d2 = max(0.2, d - 2 * taper), center = true);
    }
}

module mirror_copy(axis = "x") {
    children();

    if (axis == "x")
        mirror([1, 0, 0]) children();
    else if (axis == "y")
        mirror([0, 1, 0]) children();
    else
        mirror([0, 0, 1]) children();
}

module mock_carrier_socket(
    latch_span = 28.1,
    latch_window_width = 21.0,
    cavity_depth = 10.2,
    cavity_height = 18.0,
    pivot_d = 3.1,
    wall = 3.0,
    base_thickness = 3.0
) {
    outer_width = latch_span + wall * 2 + 2.4;
    outer_depth = cavity_depth + wall * 2;
    outer_height = cavity_height + base_thickness;
    pivot_z = 5.5;

    difference() {
        translate([0, outer_depth / 2, outer_height / 2])
            rounded_block([outer_width, outer_depth, outer_height], r = 2.0, center = true);

        translate([0, wall + cavity_depth / 2, base_thickness + cavity_height / 2])
            rounded_block([latch_window_width, cavity_depth + eps, cavity_height + eps], r = 1.0, center = true);

        translate([0, wall + cavity_depth * 0.72, base_thickness + pivot_z])
            cylinder_x(length = outer_width + eps, d = pivot_d + 0.5, center = true);
    }
}
