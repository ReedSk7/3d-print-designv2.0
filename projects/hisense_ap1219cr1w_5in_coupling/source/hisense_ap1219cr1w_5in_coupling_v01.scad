// hisense_ap1219cr1w_5in_coupling_v01.scad
// Task mode: mesh_cleanup_and_remodel
// Seed STL was treated as supporting input only. This file rebuilds the adapter as native parametric OpenSCAD.

$fn = 160;

// Nominal hose target and adjustable fit controls.
hose_nominal_d = 127.0;
hose_fit_clearance = 0.6;
receiver_wall = 2.2;
hose_receiver_od = hose_nominal_d - hose_fit_clearance;
hose_receiver_id = hose_receiver_od - (2 * receiver_wall);
hose_receiver_depth = 10.0;

// Measured / inferred outer envelope from the supplied mesh family.
flange_w = 158.0;
flange_h = 118.0;
flange_thickness = 2.8;
flange_corner_r = 5.0;
transition_depth = 30.0;
seat_plane_thickness = flange_thickness;
body_outer_d = 162.0;
body_insert_depth = 44.0;
body_total_depth = 57.5;
general_fillet_r = 4.0;
reinforcement_rib_thickness = 3.0;

// AC-side airflow opening recovered from the seed cross-sections.
seat_opening_w = 152.0;
seat_opening_h = 112.0;
seat_opening_corner_r = 4.0;
body_inner_round_d = 156.0;
receiver_anchor_id = 150.0;

// Lock-band features.
tab_count = 4;
tab_angle_list = [0, 90, 180, 270];
tab_width = 30.0;
tab_thickness = 5.5;
tab_height = 12.0;
tab_projection = 5.5;
tab_lead_in_chamfer = 2.5;
lock_stop_depth = 1.6;

// Preview helper.
preview_cutaway = false;

// Internal receiver shell profile.
receiver_support_outer_d = 154.0;
receiver_support_inner_d = 145.0;
receiver_throat_outer_d = 144.0;
receiver_throat_inner_d = 133.0;
nominal_opening_outer_d = 136.0;
nominal_opening_inner_d = hose_nominal_d;
entry_tip_outer_d = hose_receiver_od - 1.2;

slice_height = 0.35;
epsilon = 0.05;

function lerp(a, b, t) = a + (b - a) * t;
function clamp_radius(value, limit) = min(max(value, 0.01), limit);
function ring_radius() = body_outer_d / 2;
function notch_angle_list() = [for (angle = tab_angle_list) angle + (180 / tab_count / 2)];
function lock_end_z() = body_total_depth - lock_stop_depth;
function lip_start_z() = body_total_depth - hose_receiver_depth;
function support_mid_z() = transition_depth + 6.5;
function throat_blend_z() = transition_depth + 12.5;
function nominal_opening_z() = transition_depth + 15.5;
function lip_bore_transition_end_z() = lip_start_z() + 2.0;

module rounded_rect_2d(width, height, radius) {
    safe_radius = clamp_radius(radius, min(width, height) / 2 - 0.01);
    offset(r = safe_radius)
        offset(delta = -safe_radius)
            square([width, height], center = true);
}

module profile_slice(z_pos, shift = [0, 0]) {
    translate([shift[0], shift[1], z_pos])
        linear_extrude(height = slice_height)
            children();
}

module circle_slice(z_pos, diameter) {
    translate([0, 0, z_pos])
        linear_extrude(height = slice_height)
            circle(d = diameter);
}

module outer_transition_profile(t) {
    shape_w = lerp(flange_w, body_outer_d, t);
    shape_h = lerp(flange_h, body_outer_d, t);
    shape_r = lerp(flange_corner_r, general_fillet_r + (reinforcement_rib_thickness * 0.5), t);
    rounded_rect_2d(shape_w, shape_h, shape_r);
}

module inner_transition_profile(t) {
    shape_w = lerp(seat_opening_w, body_inner_round_d, t);
    shape_h = lerp(seat_opening_h, body_inner_round_d, t);
    shape_r = lerp(seat_opening_corner_r, general_fillet_r, t);
    rounded_rect_2d(shape_w, shape_h, shape_r);
}

module flange_plate() {
    linear_extrude(height = flange_thickness)
        rounded_rect_2d(flange_w, flange_h, flange_corner_r);
}

module outer_transition_shell() {
    z0 = flange_thickness;
    z1 = flange_thickness + (transition_depth - flange_thickness) * 0.35;
    z2 = flange_thickness + (transition_depth - flange_thickness) * 0.72;
    z3 = transition_depth;

    union() {
        hull() {
            profile_slice(z0) outer_transition_profile(0.00);
            profile_slice(z1) outer_transition_profile(0.35);
        }
        hull() {
            profile_slice(z1) outer_transition_profile(0.35);
            profile_slice(z2) outer_transition_profile(0.72);
        }
        hull() {
            profile_slice(z2) outer_transition_profile(0.72);
            circle_slice(z3, body_outer_d);
        }
    }
}

module round_body_shell() {
    translate([0, 0, transition_depth - epsilon])
        cylinder(h = body_total_depth - transition_depth + epsilon, d = body_outer_d);
}

module airflow_transition_core() {
    z0 = -epsilon;
    z1 = flange_thickness;
    z2 = flange_thickness + (transition_depth - flange_thickness) * 0.35;
    z3 = flange_thickness + (transition_depth - flange_thickness) * 0.72;
    z4 = transition_depth + epsilon;

    union() {
        hull() {
            profile_slice(z0) rounded_rect_2d(seat_opening_w, seat_opening_h, seat_opening_corner_r);
            profile_slice(z1) rounded_rect_2d(seat_opening_w, seat_opening_h, seat_opening_corner_r);
        }
        hull() {
            profile_slice(z1) inner_transition_profile(0.00);
            profile_slice(z2) inner_transition_profile(0.35);
        }
        hull() {
            profile_slice(z2) inner_transition_profile(0.35);
            profile_slice(z3) inner_transition_profile(0.72);
        }
        hull() {
            profile_slice(z3) inner_transition_profile(0.72);
            circle_slice(z4, body_inner_round_d);
        }
    }
}

module receiver_shell() {
    union() {
        hull() {
            circle_slice(transition_depth - epsilon, body_inner_round_d);
            circle_slice(support_mid_z(), receiver_support_outer_d);
        }
        hull() {
            circle_slice(support_mid_z(), receiver_support_outer_d);
            circle_slice(throat_blend_z(), receiver_throat_outer_d);
        }
        hull() {
            circle_slice(throat_blend_z(), receiver_throat_outer_d);
            circle_slice(nominal_opening_z(), nominal_opening_outer_d);
        }
        hull() {
            circle_slice(nominal_opening_z(), nominal_opening_outer_d);
            circle_slice(lip_start_z(), hose_receiver_od);
        }
        hull() {
            circle_slice(lip_start_z(), hose_receiver_od);
            circle_slice(body_total_depth - slice_height, entry_tip_outer_d);
        }
    }
}

module receiver_bore() {
    union() {
        hull() {
            circle_slice(transition_depth - epsilon, receiver_anchor_id);
            circle_slice(support_mid_z(), receiver_support_inner_d);
        }
        hull() {
            circle_slice(support_mid_z(), receiver_support_inner_d);
            circle_slice(throat_blend_z(), receiver_throat_inner_d);
        }
        hull() {
            circle_slice(throat_blend_z(), receiver_throat_inner_d);
            circle_slice(nominal_opening_z(), nominal_opening_inner_d);
        }
        hull() {
            circle_slice(nominal_opening_z(), nominal_opening_inner_d);
            circle_slice(lip_bore_transition_end_z(), hose_receiver_id);
        }
        hull() {
            circle_slice(lip_bore_transition_end_z(), hose_receiver_id);
            circle_slice(body_total_depth - slice_height + epsilon, hose_receiver_id);
        }
    }
}

module lock_notch_2d(depth_value) {
    translate([ring_radius() - (depth_value / 2) + epsilon, 0])
        square([depth_value + (2 * epsilon), tab_width], center = true);
}

module notch_slice(z_pos, depth_value) {
    translate([0, 0, z_pos])
        linear_extrude(height = slice_height)
            lock_notch_2d(depth_value);
}

module lock_relief_pocket(angle) {
    rotate([0, 0, angle])
        union() {
            hull() {
                notch_slice(body_insert_depth, 0.2);
                notch_slice(body_insert_depth + tab_lead_in_chamfer, tab_projection);
            }
            if (lock_end_z() > body_insert_depth + tab_lead_in_chamfer) {
                translate([0, 0, body_insert_depth + tab_lead_in_chamfer])
                    linear_extrude(height = lock_end_z() - (body_insert_depth + tab_lead_in_chamfer))
                        lock_notch_2d(tab_projection);
            }
        }
}

module lock_relief_pockets() {
    for (angle = notch_angle_list()) {
        lock_relief_pocket(angle);
    }
}

module base_model() {
    difference() {
        union() {
            flange_plate();
            outer_transition_shell();
            round_body_shell();
            receiver_shell();
        }
        union() {
            airflow_transition_core();
            receiver_bore();
            lock_relief_pockets();
        }
    }
}

module final_model() {
    if (preview_cutaway) {
        intersection() {
            base_model();
            translate([-100, -100, -1])
                cube([200, 100, body_total_depth + 2]);
        }
    } else {
        base_model();
    }
}

echo(str("task_mode = mesh_cleanup_and_remodel"));
echo(str("outer flange mm = ", flange_w, " x ", flange_h));
echo(str("body OD mm = ", body_outer_d));
echo(str("receiver target mm = ", hose_nominal_d));
echo(str("receiver lip mm = ", hose_receiver_od, " OD / ", hose_receiver_id, " ID"));
echo(str("tab angles deg = ", tab_angle_list));
echo(str("tab start/end z mm = ", body_insert_depth, " / ", lock_end_z()));

final_model();
