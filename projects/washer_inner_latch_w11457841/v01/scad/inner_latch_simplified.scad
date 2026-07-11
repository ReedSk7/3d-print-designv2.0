// Simplified fallback replacement for the W11457841 inner spring-loaded latch insert
// Intended to reuse the existing round carrier and, if possible, the original spring
// Units: millimeters

include <common_params.scad>;

render_variant = "simplified_nominal"; // simplified_nominal, simplified_test_fit, reinforced_simplified, installed_mockup
test_fit_mode = false;
reinforced_mode = false;
mockup_mode = false;

latch_body_width = 19.3;
latch_body_height = 27.8;
latch_body_depth = 8.8;
engagement_face_width = 19.3;
engagement_face_depth = 5.1;
top_hook_width = 8.4;
top_hook_depth = 2.9;
left_feature_width = 7.6;
right_feature_width = 1.9;
spring_contact_width = 3.4;
spring_contact_depth = 2.3;
guide_rail_width = 2.1;
guide_rail_height = 5.3;
pivot_or_capture_diameter = 3.1;
fit_adjustment = 0.0;
reinforcement_thickness = 1.5;
clearance_to_carrier = 0.15;
test_fit_reduction = 0.18;
break_plane_reference = 13.8;
carrier_reference_width = 28.1;

pivot_center_z = 5.4;
pivot_center_y = 6.2;
body_front_y = 0.0;
body_back_y = latch_body_depth;
tip_step_height = 3.2;
tip_relief_depth = 2.4;
upper_core_width = carrier_reference_width - left_feature_width - right_feature_width;

function carrier_adj(test_fit = false) = test_fit ? test_fit_reduction : 0;
function clamp_pos(value, minimum = 0.1) = value < minimum ? minimum : value;

module simplified_insert(test_fit = false, reinforced = false) {
    adj = carrier_adj(test_fit) + fit_adjustment;
    rail_height = clamp_pos(guide_rail_height - adj);
    rail_width = clamp_pos(guide_rail_width - adj / 2);
    pivot_d = clamp_pos(pivot_or_capture_diameter - adj);
    span = clamp_pos(carrier_reference_width - adj);
    upper_width = clamp_pos(upper_core_width - adj / 2);

    difference() {
        union() {
            body_blank(upper_width = upper_width);
            capture_bar(span = span, pivot_d = pivot_d);
            top_hook(upper_width = upper_width, adj = adj);
            asymmetrical_features(upper_width = upper_width);
            spring_tab(adj = adj);
            guide_rails(upper_width = upper_width, rail_width = rail_width, rail_height = rail_height);

            if (reinforced)
                reinforcement_web();
        }

        arm_reliefs();
        tip_center_relief();
        root_clearance();
    }
}

module body_blank(upper_width = 18.6) {
    hull() {
        translate([0, latch_body_depth / 2, 9.2])
            rounded_block([upper_width, latch_body_depth, 8.2], r = 1.4, center = true);

        translate([0, latch_body_depth / 2 - 0.4, 18.0])
            rounded_block([latch_body_width - 0.8, latch_body_depth - 0.6, 10.2], r = 1.2, center = true);

        translate([0, engagement_face_depth / 2 + 0.8, latch_body_height - 3.4])
            rounded_block([engagement_face_width, engagement_face_depth + 1.4, 7.4], r = 1.0, center = true);
    }

    translate([0, engagement_face_depth / 2 + 0.9, latch_body_height - 1.8])
        rounded_block([engagement_face_width, engagement_face_depth + 0.8, tip_step_height], r = 0.8, center = true);
}

module capture_bar(span = 28.1, pivot_d = 3.1) {
    translate([0, pivot_center_y, pivot_center_z])
        lead_in_bar(length = span, d = pivot_d, taper = 0.45);
}

module top_hook(upper_width = 18.6, adj = 0) {
    translate([0, latch_body_depth * 0.35, -1.2])
        rounded_block([top_hook_width, top_hook_depth, 4.4], r = 0.8, center = true);

    translate([0, latch_body_depth * 0.1, -3.0])
        rounded_block([top_hook_width * 0.55, top_hook_depth + 1.0, 2.2], r = 0.5, center = true);

    translate([0, latch_body_depth * 0.25, 1.2])
        rounded_block([upper_width * 0.42, top_hook_depth + 1.8, 2.2], r = 0.7, center = true);
}

module asymmetrical_features(upper_width = 18.6) {
    left_center_x = -upper_width / 2 - left_feature_width / 2 + 0.2;
    right_center_x = upper_width / 2 + right_feature_width / 2 - 0.1;

    translate([left_center_x, 2.9, break_plane_reference + 1.0])
        rounded_block([left_feature_width, 4.0, 8.2], r = 0.8, center = true);

    translate([right_center_x, 2.8, break_plane_reference + 0.8])
        rounded_block([right_feature_width, 3.6, 6.8], r = 0.5, center = true);
}

module spring_tab(adj = 0) {
    translate([spring_contact_width * 0.8, pivot_center_y + spring_contact_depth * 0.35, pivot_center_z - 0.4])
        rounded_block([
            spring_contact_width,
            spring_contact_depth,
            5.0
        ], r = 0.5, center = true);
}

module guide_rails(upper_width = 18.6, rail_width = 2.1, rail_height = 5.3) {
    rail_center_x = upper_width / 2 + rail_width / 2;

    for (x_sign = [-1, 1])
        translate([x_sign * rail_center_x, latch_body_depth * 0.62, 8.4])
            rounded_block([rail_width, 2.8, rail_height], r = 0.4, center = true);
}

module reinforcement_web() {
    hull() {
        translate([0, latch_body_depth - 0.9, break_plane_reference + 0.2])
            rounded_block([engagement_face_width - 4.4, reinforcement_thickness, 5.0], r = 0.6, center = true);

        translate([0, latch_body_depth - 0.4, latch_body_height - 4.6])
            rounded_block([engagement_face_width - 7.0, reinforcement_thickness + 0.6, 7.4], r = 0.5, center = true);
    }
}

module arm_reliefs() {
    translate([0, -0.05, latch_body_height - 6.0])
        extrude_x(engagement_face_width + 1.0, center = true)
            polygon(points = [
                [0, -0.2],
                [tip_relief_depth, -0.2],
                [latch_body_depth + 0.2, 6.2],
                [latch_body_depth + 0.2, 9.6],
                [0, 9.6]
            ]);

    translate([0, latch_body_depth * 0.92, break_plane_reference + 0.8])
        rotate([0, 0, 180])
            extrude_x(engagement_face_width - 5.6, center = true)
                polygon(points = [
                    [0, 0],
                    [1.4, 0],
                    [3.6, 4.2],
                    [0, 4.2]
                ]);
}

module tip_center_relief() {
    translate([0, engagement_face_depth + 0.8, latch_body_height - 2.6])
        rounded_block([5.2, 2.4, 4.6], r = 0.5, center = true);
}

module root_clearance() {
    translate([0, latch_body_depth * 0.5, 4.4])
        rounded_block([10.2, 3.8, 2.6], r = 0.6, center = true);
}

module simplified_mockup() {
    color([0.82, 0.82, 0.82, 0.45])
        mock_carrier_socket(
            latch_span = carrier_reference_width,
            latch_window_width = engagement_face_width + 2.2,
            cavity_depth = latch_body_depth + 1.2,
            cavity_height = latch_body_height * 0.72,
            pivot_d = pivot_or_capture_diameter
        );

    color([0.16, 0.16, 0.16])
        simplified_insert(test_fit = false, reinforced = false);
}

module inner_latch_simplified_variant(variant = "nominal") {
    if (variant == "nominal")
        simplified_insert(test_fit = false, reinforced = false);
    else if (variant == "test_fit")
        simplified_insert(test_fit = true, reinforced = false);
    else if (variant == "reinforced")
        simplified_insert(test_fit = false, reinforced = true);
    else
        simplified_mockup();
}

if (mockup_mode || render_variant == "installed_mockup")
    inner_latch_simplified_variant("mockup");
else if (reinforced_mode || render_variant == "reinforced_simplified")
    inner_latch_simplified_variant("reinforced");
else if (test_fit_mode || render_variant == "simplified_test_fit")
    inner_latch_simplified_variant("test_fit");
else if (render_variant == "simplified_nominal")
    inner_latch_simplified_variant("nominal");
else
    inner_latch_simplified_variant("nominal");
