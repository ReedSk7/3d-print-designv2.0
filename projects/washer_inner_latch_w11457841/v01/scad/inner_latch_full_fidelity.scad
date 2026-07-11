// Best-effort high-fidelity replacement for the W11457841 inner spring-loaded latch insert
// Intended to reuse the original round carrier and original torsion spring where practical
// Units: millimeters

include <common_params.scad>;

render_variant = "full_fidelity_nominal"; // full_fidelity_nominal, full_fidelity_test_fit, exploded_view, installed_mockup
test_fit_mode = false;
exploded_mode = false;
mockup_mode = false;

latch_body_width = 19.3;
latch_body_height = 28.1;
latch_body_depth = 8.9;
engagement_face_width = 19.3;
engagement_face_depth = 5.0;
top_hook_width = 8.6;
top_hook_depth = 3.0;
left_feature_width = 7.6;
right_feature_width = 1.9;
spring_contact_width = 3.2;
spring_contact_depth = 2.2;
guide_rail_width = 2.0;
guide_rail_height = 5.5;
pivot_or_capture_diameter = 3.1;
fit_adjustment = 0.0;
reinforcement_thickness = 1.2;
clearance_to_carrier = 0.15;
test_fit_reduction = 0.18;
break_plane_reference = 13.9;
carrier_reference_width = 28.1;

pivot_center_z = 5.5;
pivot_center_y = 6.25;
upper_core_width = carrier_reference_width - left_feature_width - right_feature_width;

function carrier_adj_ff(test_fit = false) = test_fit ? test_fit_reduction : 0;
function clamp_ff(value, minimum = 0.1) = value < minimum ? minimum : value;

module fidelity_insert(test_fit = false) {
    adj = carrier_adj_ff(test_fit) + fit_adjustment;
    upper_width = clamp_ff(upper_core_width - adj / 2);
    pivot_d = clamp_ff(pivot_or_capture_diameter - adj);
    span = clamp_ff(carrier_reference_width - adj);
    rail_width = clamp_ff(guide_rail_width - adj / 2);
    rail_height = clamp_ff(guide_rail_height - adj);

    difference() {
        union() {
            fidelity_body(upper_width = upper_width);
            fidelity_capture_bar(span = span, pivot_d = pivot_d);
            fidelity_upper_hook(upper_width = upper_width);
            fidelity_side_features(upper_width = upper_width);
            fidelity_spring_features();
            fidelity_guides(upper_width = upper_width, rail_width = rail_width, rail_height = rail_height);
            fidelity_stops();
        }

        fidelity_internal_windows();
        fidelity_tip_relief();
        fidelity_root_relief();
    }
}

module fidelity_body(upper_width = 18.6) {
    hull() {
        translate([0, latch_body_depth / 2, 8.6])
            rounded_block([upper_width, latch_body_depth, 7.8], r = 1.3, center = true);

        translate([0, latch_body_depth / 2 - 0.4, 15.8])
            rounded_block([latch_body_width - 0.7, latch_body_depth - 0.4, 7.6], r = 1.1, center = true);

        translate([0, latch_body_depth / 2 - 0.8, 22.8])
            rounded_block([latch_body_width - 0.3, latch_body_depth - 1.2, 8.0], r = 1.0, center = true);

        translate([0, engagement_face_depth / 2 + 1.0, latch_body_height - 2.8])
            rounded_block([engagement_face_width, engagement_face_depth + 1.2, 6.8], r = 0.8, center = true);
    }
}

module fidelity_capture_bar(span = 28.1, pivot_d = 3.1) {
    translate([0, pivot_center_y, pivot_center_z])
        lead_in_bar(length = span, d = pivot_d, taper = 0.42);
}

module fidelity_upper_hook(upper_width = 18.6) {
    difference() {
        union() {
            translate([0, latch_body_depth * 0.32, -1.0])
                rounded_block([top_hook_width, top_hook_depth, 4.8], r = 0.7, center = true);

            translate([0, latch_body_depth * 0.08, -3.2])
                rounded_block([top_hook_width * 0.52, top_hook_depth + 1.2, 2.4], r = 0.5, center = true);

            hull() {
                translate([0, latch_body_depth * 0.25, 0.8])
                    rounded_block([upper_width * 0.44, top_hook_depth + 1.4, 2.4], r = 0.5, center = true);
                translate([0, latch_body_depth * 0.12, -1.4])
                    rounded_block([top_hook_width * 0.34, top_hook_depth + 0.6, 2.0], r = 0.4, center = true);
            }
        }

        translate([0, latch_body_depth * 0.35, -1.0])
            rounded_block([top_hook_width * 0.45, top_hook_depth + 0.2, 2.0], r = 0.4, center = true);
    }
}

module fidelity_side_features(upper_width = 18.6) {
    left_center_x = -upper_width / 2 - left_feature_width / 2 + 0.2;
    right_center_x = upper_width / 2 + right_feature_width / 2 - 0.1;

    hull() {
        translate([left_center_x, 2.8, break_plane_reference - 0.2])
            rounded_block([left_feature_width, 3.8, 5.8], r = 0.6, center = true);
        translate([-upper_width / 2 + 1.2, 3.8, break_plane_reference + 2.2])
            rounded_block([3.4, 2.6, 4.2], r = 0.4, center = true);
    }

    hull() {
        translate([right_center_x, 2.7, break_plane_reference - 0.3])
            rounded_block([right_feature_width, 3.2, 5.2], r = 0.4, center = true);
        translate([upper_width / 2 - 0.8, 3.4, break_plane_reference + 1.8])
            rounded_block([2.0, 2.2, 3.8], r = 0.3, center = true);
    }
}

module fidelity_spring_features() {
    translate([spring_contact_width * 0.95, pivot_center_y + spring_contact_depth * 0.25, pivot_center_z - 0.2])
        rounded_block([spring_contact_width, spring_contact_depth, 5.4], r = 0.4, center = true);

    translate([spring_contact_width * 0.2, pivot_center_y - 1.8, pivot_center_z + 0.2])
        rounded_block([3.8, 1.4, 3.4], r = 0.3, center = true);
}

module fidelity_guides(upper_width = 18.6, rail_width = 2.0, rail_height = 5.5) {
    rail_center_x = upper_width / 2 + rail_width / 2;

    for (x_sign = [-1, 1]) {
        translate([x_sign * rail_center_x, latch_body_depth * 0.62, 8.4])
            rounded_block([rail_width, 2.6, rail_height], r = 0.3, center = true);

        translate([x_sign * rail_center_x, latch_body_depth * 0.48, 3.8])
            rounded_block([rail_width, 2.2, 2.8], r = 0.3, center = true);
    }
}

module fidelity_stops() {
    translate([-4.2, latch_body_depth * 0.52, 2.4])
        rounded_block([3.0, 1.8, 2.2], r = 0.3, center = true);

    translate([5.0, latch_body_depth * 0.48, 2.1])
        rounded_block([2.4, 1.8, 2.0], r = 0.3, center = true);
}

module fidelity_internal_windows() {
    translate([0, latch_body_depth * 0.55, 7.2])
        rounded_block([9.8, 3.4, 3.0], r = 0.5, center = true);

    translate([-4.4, latch_body_depth * 0.55, 11.2])
        rounded_block([4.6, 2.8, 4.8], r = 0.4, center = true);

    translate([4.2, latch_body_depth * 0.6, 11.0])
        rounded_block([3.4, 2.5, 4.2], r = 0.3, center = true);
}

module fidelity_tip_relief() {
    translate([0, -0.05, latch_body_height - 6.6])
        extrude_x(engagement_face_width + 1.2, center = true)
            polygon(points = [
                [0, -0.2],
                [2.0, -0.2],
                [latch_body_depth + 0.2, 5.8],
                [latch_body_depth + 0.2, 9.2],
                [0, 9.2]
            ]);

    translate([0, engagement_face_depth + 0.7, latch_body_height - 2.7])
        rounded_block([4.8, 2.0, 4.6], r = 0.3, center = true);
}

module fidelity_root_relief() {
    translate([0, latch_body_depth * 0.44, 4.1])
        rounded_block([8.8, 3.4, 2.4], r = 0.4, center = true);
}

module exploded_scene() {
    color([0.16, 0.16, 0.16])
        translate([0, 0, 0])
            fidelity_insert(test_fit = false);

    color([0.82, 0.82, 0.82, 0.45])
        translate([0, 14, 0])
            mock_carrier_socket(
                latch_span = carrier_reference_width,
                latch_window_width = engagement_face_width + 2.2,
                cavity_depth = latch_body_depth + 1.2,
                cavity_height = latch_body_height * 0.72,
                pivot_d = pivot_or_capture_diameter
            );
}

module installed_mockup_scene() {
    color([0.82, 0.82, 0.82, 0.45])
        mock_carrier_socket(
            latch_span = carrier_reference_width,
            latch_window_width = engagement_face_width + 2.2,
            cavity_depth = latch_body_depth + 1.2,
            cavity_height = latch_body_height * 0.72,
            pivot_d = pivot_or_capture_diameter
        );

    color([0.16, 0.16, 0.16])
        fidelity_insert(test_fit = false);
}

module inner_latch_full_fidelity_variant(variant = "nominal") {
    if (variant == "nominal")
        fidelity_insert(test_fit = false);
    else if (variant == "test_fit")
        fidelity_insert(test_fit = true);
    else if (variant == "exploded")
        exploded_scene();
    else
        installed_mockup_scene();
}

if (exploded_mode || render_variant == "exploded_view")
    inner_latch_full_fidelity_variant("exploded");
else if (mockup_mode || render_variant == "installed_mockup")
    inner_latch_full_fidelity_variant("mockup");
else if (test_fit_mode || render_variant == "full_fidelity_test_fit")
    inner_latch_full_fidelity_variant("test_fit");
else if (render_variant == "full_fidelity_nominal")
    inner_latch_full_fidelity_variant("nominal");
else
    inner_latch_full_fidelity_variant("nominal");
