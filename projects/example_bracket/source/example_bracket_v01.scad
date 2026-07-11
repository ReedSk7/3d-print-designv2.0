$fn = 48;

leg_length = 60;
leg_height = 40;
leg_width = 24;
wall_thickness = 6;
hole_diameter = 5.2;
hole_offset = 14;
gusset_thickness = 6;

module bracket_body() {
    union() {
        cube([leg_length, leg_width, wall_thickness]);
        cube([wall_thickness, leg_width, leg_height]);
        linear_extrude(height = leg_width)
            polygon(points = [
                [wall_thickness, wall_thickness],
                [wall_thickness, leg_height - wall_thickness],
                [leg_length - wall_thickness, wall_thickness]
            ]);
    }
}

module mounting_holes() {
    translate([hole_offset, leg_width / 2, -1])
        cylinder(h = wall_thickness + 2, d = hole_diameter);

    translate([-1, leg_width / 2, leg_height - hole_offset])
        rotate([0, 90, 0])
            cylinder(h = wall_thickness + 2, d = hole_diameter);
}

difference() {
    bracket_body();
    mounting_holes();
}
