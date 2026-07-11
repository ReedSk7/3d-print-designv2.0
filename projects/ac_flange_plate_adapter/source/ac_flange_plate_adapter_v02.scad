// ac_flange_plate_adapter_v02.scad
// Task mode: mesh_cleanup_and_remodel
// Seed mesh is supporting only. This file rebuilds the adapter as clean parametric CAD.

$fn = 96;

show_seed_reference = false;
seed_reference_path = "../../references/public/ac_flange_plate_adapter/AC_Flange_Plate.STL";

// Inferred protected-interface dimensions from the seed mesh.
plate_outer_w = 147.32;
plate_outer_h = 118.11;
plate_outer_corner_r = 1.6;

rear_opening_w = 139.70;
rear_opening_h = 107.95;
rear_opening_corner_r = 1.6;
rear_opening_offset_x = 1.27;
rear_opening_offset_y = 0.00;

duct_center_offset_x = 2.80;
duct_center_offset_y = 0.00;

// v02 engineering choices for a more standard-friendly 6 in hose interface.
plate_thickness = 3.20;
duct_od = 151.00;
duct_id = 145.00;
duct_length = 35.00;
duct_taper_deg = 0.75;
lip_height = 2.50;
lip_thickness = 1.00;
transition_height = 27.90;
transition_radius = 12.00;

// Optional rear gasket channel is off by default to keep the sealing face planar.
gasket_channel_enabled = false;
gasket_channel_offset = 4.00;
gasket_channel_depth = 0.80;
gasket_channel_width = 2.00;

slice_height = 0.40;
epsilon = 0.05;

function lerp(a, b, t) = a + (b - a) * t;
function spigot_tip_od() = duct_od - (2 * duct_length * tan(duct_taper_deg));
function clamp_radius(value, limit) = min(max(value, 0.01), limit);
function duct_wall() = (duct_od - duct_id) / 2;

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

module plate_outer_profile() {
    rounded_rect_2d(plate_outer_w, plate_outer_h, plate_outer_corner_r);
}

module rear_opening_profile() {
    rounded_rect_2d(rear_opening_w, rear_opening_h, rear_opening_corner_r);
}

module rear_gasket_channel_profile() {
    difference() {
        offset(delta = gasket_channel_offset + gasket_channel_width)
            rear_opening_profile();
        offset(delta = gasket_channel_offset)
            rear_opening_profile();
    }
}

module flange_plate() {
    difference() {
        linear_extrude(height = plate_thickness)
            plate_outer_profile();

        if (gasket_channel_enabled) {
            translate([rear_opening_offset_x, rear_opening_offset_y, 0])
                linear_extrude(height = gasket_channel_depth + epsilon)
                    rear_gasket_channel_profile();
        }
    }
}

module outer_transition_profile(t) {
    shape_w = lerp(plate_outer_w, duct_od, t);
    shape_h = lerp(plate_outer_h, duct_od, t);
    shape_r = lerp(plate_outer_corner_r, transition_radius, t);
    rounded_rect_2d(shape_w, shape_h, shape_r);
}

module inner_transition_profile(t) {
    shape_w = lerp(rear_opening_w, duct_id, t);
    shape_h = lerp(rear_opening_h, duct_id, t);
    shape_r = lerp(rear_opening_corner_r, transition_radius * 0.85, t);
    rounded_rect_2d(shape_w, shape_h, shape_r);
}

module transition_blend() {
    z0 = plate_thickness;
    z1 = plate_thickness + transition_height * 0.34;
    z2 = plate_thickness + transition_height * 0.70;
    z3 = plate_thickness + transition_height;

    shift0 = [0, 0];
    shift1 = [duct_center_offset_x * 0.34, duct_center_offset_y * 0.34];
    shift2 = [duct_center_offset_x * 0.70, duct_center_offset_y * 0.70];
    shift3 = [duct_center_offset_x, duct_center_offset_y];

    union() {
        hull() {
            profile_slice(z0, shift0) outer_transition_profile(0.00);
            profile_slice(z1, shift1) outer_transition_profile(0.34);
        }
        hull() {
            profile_slice(z1, shift1) outer_transition_profile(0.34);
            profile_slice(z2, shift2) outer_transition_profile(0.70);
        }
        hull() {
            profile_slice(z2, shift2) outer_transition_profile(0.70);
            profile_slice(z3, shift3) circle(d = duct_od);
        }
    }
}

module airflow_transition() {
    z0 = -epsilon;
    z1 = plate_thickness;
    z2 = plate_thickness + transition_height * 0.34;
    z3 = plate_thickness + transition_height * 0.70;
    z4 = plate_thickness + transition_height;

    shift0 = [rear_opening_offset_x, rear_opening_offset_y];
    shift1 = [rear_opening_offset_x, rear_opening_offset_y];
    shift2 = [
        lerp(rear_opening_offset_x, duct_center_offset_x, 0.34),
        lerp(rear_opening_offset_y, duct_center_offset_y, 0.34),
    ];
    shift3 = [
        lerp(rear_opening_offset_x, duct_center_offset_x, 0.70),
        lerp(rear_opening_offset_y, duct_center_offset_y, 0.70),
    ];
    shift4 = [duct_center_offset_x, duct_center_offset_y];

    union() {
        hull() {
            profile_slice(z0, shift0) rear_opening_profile();
            profile_slice(z1, shift1) rear_opening_profile();
        }
        hull() {
            profile_slice(z1, shift1) rear_opening_profile();
            profile_slice(z2, shift2) inner_transition_profile(0.34);
        }
        hull() {
            profile_slice(z2, shift2) inner_transition_profile(0.34);
            profile_slice(z3, shift3) inner_transition_profile(0.70);
        }
        hull() {
            profile_slice(z3, shift3) inner_transition_profile(0.70);
            profile_slice(z4, shift4) circle(d = duct_id);
        }
    }
}

module lip_bead(length_tip_od) {
    half_lip = lip_height / 2;
    cylinder(h = half_lip, d1 = length_tip_od, d2 = length_tip_od + (2 * lip_thickness));
    translate([0, 0, half_lip])
        cylinder(h = half_lip, d1 = length_tip_od + (2 * lip_thickness), d2 = length_tip_od);
}

module duct_spigot() {
    spigot_z = plate_thickness + transition_height;
    straight_length = max(duct_length - lip_height, 0.01);
    tip_od = spigot_tip_od();
    tip_start_od = lerp(duct_od, tip_od, straight_length / duct_length);

    translate([duct_center_offset_x, duct_center_offset_y, spigot_z]) {
        cylinder(h = straight_length, d1 = duct_od, d2 = tip_start_od);
        translate([0, 0, straight_length])
            lip_bead(tip_start_od);
    }
}

module airflow_core() {
    spigot_z = plate_thickness + transition_height;
    total_height = duct_length + lip_height;

    union() {
        airflow_transition();
        translate([duct_center_offset_x, duct_center_offset_y, spigot_z - epsilon])
            cylinder(h = total_height + (2 * epsilon), d = duct_id);
    }
}

module final_model() {
    difference() {
        union() {
            flange_plate();
            transition_blend();
            duct_spigot();
        }
        airflow_core();
    }
}

module seed_reference_mesh() {
    translate([-73.66, -76.527, 0])
        import(seed_reference_path);
}

echo(str("task_mode = mesh_cleanup_and_remodel"));
echo(str("plate outer mm = ", plate_outer_w, " x ", plate_outer_h));
echo(str("rear opening mm = ", rear_opening_w, " x ", rear_opening_h));
echo(str("duct interface mm = ", duct_od, " OD / ", duct_id, " ID"));
echo(str("duct wall mm = ", duct_wall()));

if (show_seed_reference) {
    color([0.70, 0.78, 0.92, 0.35]) seed_reference_mesh();
}

final_model();
