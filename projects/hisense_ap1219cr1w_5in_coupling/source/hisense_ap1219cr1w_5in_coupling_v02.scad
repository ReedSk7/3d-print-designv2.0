// hisense_ap1219cr1w_5in_coupling_v02.scad
// Task mode: mesh_cleanup_and_remodel
// v02 keeps the v01 geometry family but upgrades the lock tabs, hose entry, and top-level tuning controls.

$fn = 192;

// Hose fit tracks.
hose_nominal_d_user_target = 127.0;
seller_family_hose_side_id = 155.6;
use_user_hose_target = true;
user_hose_receiver_id_track = 129.0;
hose_fit_clearance = 0.2;

// Receiver sizing.
hose_receiver_id = use_user_hose_target
    ? user_hose_receiver_id_track + hose_fit_clearance
    : seller_family_hose_side_id;
receiver_wall = 2.6;
hose_receiver_od = hose_receiver_id + (2 * receiver_wall);
hose_receiver_depth = 11.0;
hose_lead_in_chamfer_d = 3.2;
hose_lead_in_chamfer_len = 3.0;
hose_retention_lip_od = hose_receiver_od + 1.4;
hose_retention_lip_h = 1.6;

// Outer envelope family.
flange_w = 158.0;
flange_h = 118.0;
flange_extra_w = 2.0;
flange_extra_h = 2.0;
flange_thickness = 2.8;
flange_corner_r = 5.0;
transition_depth = 30.0;
seat_plane_thickness = 2.8;
body_outer_d = 162.0;
body_insert_depth = 43.0;
body_total_depth = 57.5;
general_fillet_r = 4.0;

// Inner transition family recovered from v01 and the seed sections.
seat_opening_w = 152.0;
seat_opening_h = 112.0;
seat_opening_corner_r = 4.0;
body_inner_round_d = 156.0;
receiver_anchor_id = 150.0;
receiver_anchor_outer_d = 150.0;
receiver_mid_outer_d = 142.0;
receiver_mid_inner_d = 138.0;
receiver_mid_z = 38.0;

// Lock band and tab behavior.
lock_band_z_start = 43.0;
lock_band_height = 12.5;
lock_band_z_end = lock_band_z_start + lock_band_height;
tab_count = 4;
tab_angle_list = [0, 90, 180, 270];
tab_width = 28.0;
tab_thickness = 0.8;
tab_height = 8.5;
tab_projection = 2.0;
tab_lead_in_angle = 28.0;
tab_lead_in_len = 8.0;
tab_stop_face_angle = 3.0;
tab_relief_depth = 3.2;
tab_relief_len = 8.0;
tab_root_fillet_r = 1.5;
tab_radial_taper = 0.75;
lock_stop_depth = 2.0;
tab_base_overlap = 1.0;

preview_cutaway = false;

slice_height = 0.35;
epsilon = 0.05;

function clamp_radius(value, limit) = min(max(value, 0.01), limit);
function lerp(a, b, t) = a + (b - a) * t;
function flange_w_eff() = flange_w + flange_extra_w;
function flange_h_eff() = flange_h + flange_extra_h;
function ring_radius() = body_outer_d / 2;
function tab_z_start() = lock_band_z_start + ((lock_band_height - tab_height) / 2);
function tab_z_end() = tab_z_start() + tab_height;
function tab_top_projection() = max(tab_thickness, tab_projection - (tab_height * tan(tab_radial_taper)));
function receiver_socket_z() = body_total_depth - hose_receiver_depth;
function receiver_chamfer_z() = body_total_depth - hose_lead_in_chamfer_len;
function lead_projection(value) = max(tab_thickness, value - (tab_lead_in_len * tan(tab_lead_in_angle)));
function stop_face_skew(value) = min(tab_width * 0.15, value * tan(tab_stop_face_angle));

module rounded_rect_2d(width, height, radius) {
    safe_radius = clamp_radius(radius, min(width, height) / 2 - 0.01);
    offset(r = safe_radius)
        offset(delta = -safe_radius)
            square([width, height], center = true);
}

module rounded_polygon_2d(points, radius) {
    safe_radius = max(radius, 0.01);
    offset(r = safe_radius)
        offset(delta = -safe_radius)
            polygon(points = points);
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
    shape_w = lerp(flange_w_eff(), body_outer_d, t);
    shape_h = lerp(flange_h_eff(), body_outer_d, t);
    shape_r = lerp(flange_corner_r, general_fillet_r, t);
    rounded_rect_2d(shape_w, shape_h, shape_r);
}

module inner_transition_profile(t) {
    shape_w = lerp(seat_opening_w, body_inner_round_d, t);
    shape_h = lerp(seat_opening_h, body_inner_round_d, t);
    shape_r = lerp(seat_opening_corner_r, general_fillet_r, t);
    rounded_rect_2d(shape_w, shape_h, shape_r);
}

module flange_plate() {
    linear_extrude(height = seat_plane_thickness)
        rounded_rect_2d(flange_w_eff(), flange_h_eff(), flange_corner_r);
}

module outer_transition_shell() {
    z0 = seat_plane_thickness;
    z1 = seat_plane_thickness + (transition_depth - seat_plane_thickness) * 0.35;
    z2 = seat_plane_thickness + (transition_depth - seat_plane_thickness) * 0.72;

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
            circle_slice(transition_depth, body_outer_d);
        }
    }
}

module round_body_shell() {
    translate([0, 0, transition_depth - epsilon])
        cylinder(h = body_total_depth - transition_depth + epsilon, d = body_outer_d);
}

module airflow_transition_core() {
    z0 = -epsilon;
    z1 = seat_plane_thickness;
    z2 = seat_plane_thickness + (transition_depth - seat_plane_thickness) * 0.35;
    z3 = seat_plane_thickness + (transition_depth - seat_plane_thickness) * 0.72;

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
            circle_slice(transition_depth + epsilon, body_inner_round_d);
        }
    }
}

module receiver_shell() {
    union() {
        hull() {
            circle_slice(transition_depth - epsilon, receiver_anchor_outer_d);
            circle_slice(receiver_mid_z, receiver_mid_outer_d);
        }
        hull() {
            circle_slice(receiver_mid_z, receiver_mid_outer_d);
            circle_slice(receiver_socket_z(), hose_receiver_od);
        }
        hull() {
            circle_slice(receiver_socket_z(), hose_receiver_od);
            circle_slice(body_total_depth - hose_retention_lip_h, hose_receiver_od);
        }
        hull() {
            circle_slice(body_total_depth - hose_retention_lip_h, hose_receiver_od);
            circle_slice(body_total_depth - slice_height, hose_retention_lip_od);
        }
    }
}

module receiver_bore() {
    entry_d = hose_receiver_id + hose_lead_in_chamfer_d;

    union() {
        hull() {
            circle_slice(transition_depth - epsilon, receiver_anchor_id);
            circle_slice(receiver_mid_z, receiver_mid_inner_d);
        }
        hull() {
            circle_slice(receiver_mid_z, receiver_mid_inner_d);
            circle_slice(receiver_socket_z(), hose_receiver_id);
        }
        hull() {
            circle_slice(receiver_socket_z(), hose_receiver_id);
            circle_slice(receiver_chamfer_z(), hose_receiver_id);
        }
        hull() {
            circle_slice(receiver_chamfer_z(), hose_receiver_id);
            circle_slice(body_total_depth - slice_height + epsilon, entry_d);
        }
    }
}

module tab_profile_2d(projection_value) {
    ramp_projection = lead_projection(projection_value);
    stop_skew = stop_face_skew(projection_value);
    half_w = tab_width / 2;
    ramp_y = max(half_w - tab_lead_in_len, -half_w + 0.6);

    rounded_polygon_2d(
        [
            [0, -half_w],
            [projection_value, -half_w + stop_skew],
            [projection_value, ramp_y],
            [ramp_projection, half_w],
            [0, half_w]
        ],
        tab_root_fillet_r
    );
}

module tab_profile_slice(angle, z_pos, projection_value) {
    rotate([0, 0, angle])
        translate([ring_radius() - tab_base_overlap, 0, z_pos])
            linear_extrude(height = slice_height)
                tab_profile_2d(projection_value);
}

module cam_tab(angle) {
    hull() {
        tab_profile_slice(angle, tab_z_start(), tab_projection);
        tab_profile_slice(angle, tab_z_end() - slice_height, tab_top_projection());
    }
}

module cam_tabs() {
    for (angle = tab_angle_list) {
        cam_tab(angle);
    }
}

module relief_profile_2d(depth_value) {
    half_w = (tab_width / 2) + 1.2;
    relief_front_y = min(half_w, (tab_width / 2) + tab_relief_len);

    polygon(
        points = [
            [0, -half_w],
            [depth_value, -half_w],
            [depth_value, relief_front_y - tab_relief_len],
            [tab_thickness * 0.35, relief_front_y],
            [0, relief_front_y]
        ]
    );
}

module tab_relief_pocket(angle) {
    relief_height = max(lock_band_height - lock_stop_depth, slice_height);

    rotate([0, 0, angle])
        translate([ring_radius() - epsilon, 0, lock_band_z_start - epsilon])
            linear_extrude(height = relief_height + (2 * epsilon))
                relief_profile_2d(tab_relief_depth);
}

module tab_relief_pockets() {
    for (angle = tab_angle_list) {
        tab_relief_pocket(angle);
    }
}

module base_model() {
    difference() {
        union() {
            flange_plate();
            outer_transition_shell();
            round_body_shell();
            receiver_shell();
            cam_tabs();
        }
        union() {
            airflow_transition_core();
            receiver_bore();
            tab_relief_pockets();
        }
    }
}

module final_model() {
    if (preview_cutaway) {
        intersection() {
            base_model();
            translate([-110, -110, -1])
                cube([220, 110, body_total_depth + 2]);
        }
    } else {
        base_model();
    }
}

echo(str("task_mode = mesh_cleanup_and_remodel"));
echo(str("flange family mm = ", flange_w_eff(), " x ", flange_h_eff()));
echo(str("lock band mm = ", body_outer_d, " OD from z ", lock_band_z_start, " to ", lock_band_z_end));
echo(str("user hose track id mm = ", user_hose_receiver_id_track + hose_fit_clearance));
echo(str("seller family comparison id mm = ", seller_family_hose_side_id));
echo(str("active hose receiver id mm = ", hose_receiver_id));
echo(str("tab centers deg = ", tab_angle_list));

final_model();
