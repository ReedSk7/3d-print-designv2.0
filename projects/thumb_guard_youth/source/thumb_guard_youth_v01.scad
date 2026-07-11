// thumb_guard_youth_v01
// Task mode: original_product_design
// Clean parametric youth baseball thumbguard inspired by the attached reference
// images and envelope dimensions, but rebuilt as an original design.
// Units: millimeters

$fn = 72;

// ---------------------------------------------------------------------------
// v01 anchor dimensions
// ---------------------------------------------------------------------------

overall_length = 82;
overall_width = 52;
overall_thickness = 15;

thumb_opening_major = 22;  // Estimated v01 fit value, not measured.
thumb_opening_minor = 18;  // Estimated v01 fit value, not measured.
ring_wall = 5;
ring_width = 14;
ring_to_pad_offset = 22;
pad_contact_width = 36;
pad_contact_length = 44;
pad_center_thickness = 12;
pad_edge_thickness = 5;
transition_blend_radius = 10;
outer_edge_round = 2;

// ---------------------------------------------------------------------------
// Derived layout controls
// ---------------------------------------------------------------------------

ring_outer_major = thumb_opening_major + ring_wall * 2;
ring_outer_minor = thumb_opening_minor + ring_width;

ring_center_y = overall_length - ring_outer_minor / 2;
shoulder_center_y = overall_length * 0.63;
pad_center_y = ring_center_y - ring_to_pad_offset - 10;
tail_center_y = overall_length * 0.13;

transition_anchor_width = transition_blend_radius * 2.2;
transition_anchor_length = transition_blend_radius * 1.3;
opening_relief_bottom = 0.8;
opening_relief_top = 1.2;

// ---------------------------------------------------------------------------
// Basic helpers
// ---------------------------------------------------------------------------

module ellipse_2d(width, length) {
    scale([width / 2, length / 2])
        circle(r = 1);
}

module ellipse_slice(width, length, z = 0) {
    translate([0, 0, z])
        linear_extrude(height = 0.02)
            ellipse_2d(width, length);
}

module rounded_hull_2d() {
    offset(r = outer_edge_round)
        offset(delta = -outer_edge_round)
            children();
}

// ---------------------------------------------------------------------------
// Required modules
// ---------------------------------------------------------------------------

module thumb_opening_profile(expand = 0) {
    ellipse_2d(
        thumb_opening_major + expand,
        thumb_opening_minor + expand
    );
}

module thumb_ring() {
    hull() {
        translate([0, ring_center_y, 0])
            ellipse_slice(ring_outer_major, ring_outer_minor);

        translate([0, ring_center_y - 1.2, overall_thickness - 0.02])
            ellipse_slice(ring_outer_major * 0.90, ring_outer_minor * 0.88);
    }
}

module guard_outline_2d(scale_factor = 1) {
    s = scale_factor;

    rounded_hull_2d() {
        hull() {
            translate([0, shoulder_center_y])
                ellipse_2d(overall_width * 0.96 * s, overall_length * 0.22 * s);

            translate([-overall_width * 0.10 * s, pad_center_y])
                ellipse_2d(pad_contact_width * 1.04 * s, pad_contact_length * 0.90 * s);

            translate([overall_width * 0.20 * s, pad_center_y + pad_contact_length * 0.08])
                ellipse_2d(overall_width * 0.38 * s, pad_contact_length * 0.46 * s);

            translate([-overall_width * 0.04 * s, tail_center_y])
                ellipse_2d(overall_width * 0.42 * s, overall_length * 0.22 * s);
        }
    }
}

module overall_envelope_2d() {
    rounded_hull_2d() {
        hull() {
            translate([0, ring_center_y])
                ellipse_2d(ring_outer_major * 1.04, ring_outer_minor * 1.04);

            translate([0, shoulder_center_y])
                ellipse_2d(overall_width * 0.96, overall_length * 0.22);

            translate([-overall_width * 0.10, pad_center_y])
                ellipse_2d(pad_contact_width * 1.04, pad_contact_length * 0.90);

            translate([overall_width * 0.18, pad_center_y + pad_contact_length * 0.06])
                ellipse_2d(overall_width * 0.38, pad_contact_length * 0.46);

            translate([-overall_width * 0.04, tail_center_y])
                ellipse_2d(overall_width * 0.42, overall_length * 0.22);
        }
    }
}

module bat_contact_pad() {
    union() {
        linear_extrude(height = pad_edge_thickness)
            guard_outline_2d(1.0);

        hull() {
            translate([0, 0, pad_edge_thickness - 0.02])
                linear_extrude(height = 0.02)
                    guard_outline_2d(0.96);

            translate([-overall_width * 0.04, pad_center_y + 1.8, pad_center_thickness - 0.02])
                linear_extrude(height = 0.02)
                    guard_outline_2d(0.72);
        }
    }
}

module guard_body() {
    union() {
        bat_contact_pad();

        hull() {
            translate([0, shoulder_center_y, 0])
                ellipse_slice(overall_width * 0.92, overall_width * 0.42);

            translate([0, ring_center_y - ring_outer_minor * 0.18, overall_thickness * 0.62])
                ellipse_slice(ring_outer_major * 1.05, ring_outer_minor * 0.94);

            translate([0, shoulder_center_y - 1.2, pad_center_thickness - 0.02])
                ellipse_slice(transition_anchor_width, transition_anchor_length);
        }

        hull() {
            translate([-overall_width * 0.20, pad_center_y + 2.5, pad_edge_thickness])
                ellipse_slice(overall_width * 0.20, overall_length * 0.12);

            translate([0, shoulder_center_y - 1.2, pad_center_thickness - 0.3])
                ellipse_slice(transition_blend_radius * 1.9, transition_blend_radius * 1.0);
        }
    }
}

module thumb_opening_cut() {
    hull() {
        translate([0, ring_center_y, -0.6])
            linear_extrude(height = 0.02)
                thumb_opening_profile(opening_relief_bottom);

        translate([0, ring_center_y - 0.4, 2.0])
            linear_extrude(height = 0.02)
                thumb_opening_profile(0);

        translate([0, ring_center_y - 1.0, overall_thickness + 0.6])
            linear_extrude(height = 0.02)
                thumb_opening_profile(opening_relief_top);
    }
}

module final_model() {
    intersection() {
        difference() {
            union() {
                guard_body();
                thumb_ring();
            }
            thumb_opening_cut();
        }

        linear_extrude(height = overall_thickness)
            overall_envelope_2d();
    }
}

echo(str("task_mode = original_product_design"));
echo(str("overall target mm = ", overall_width, " x ", overall_length, " x ", overall_thickness));
echo(str("thumb opening estimate mm = ", thumb_opening_major, " x ", thumb_opening_minor));
echo(str("pad center thickness mm = ", pad_center_thickness));

final_model();
