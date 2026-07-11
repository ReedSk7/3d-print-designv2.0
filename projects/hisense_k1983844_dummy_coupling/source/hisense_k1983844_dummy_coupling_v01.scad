// hisense_k1983844_dummy_coupling_v01.scad
// Task mode: mesh_cleanup_and_remodel
// Preserve the supplied outer locking interface and remodel only the hose-side collar opening.

$fn = 160;

show_reference = false;

reference_mesh_path = "../../../references/measured/hisense_k1983844_dummy_coupling/ac_vent_tube_adapter.stl";

// Raw mesh bounds after inspection of the supplied STL.
raw_x_min = -27.5;
raw_x_max = 30.0;
build_height = raw_x_max - raw_x_min;

// The imported STL's airflow axis is raw X. Rotate it upright so the square flange sits on the bed.
build_shift_z = -raw_x_min;

// Existing collar bore is about 156 mm in the round zone. Keep all protected outer geometry from the STL.
existing_collar_bore_d = 156.0;
anchor_overlap_outer_d = 160.0;
anchor_overlap_inner_d = 155.0;

// 5 in hose adaptation targets.
hose_nominal_d = 127.0;
lip_outer_d = 126.0;
lip_bore_d = 122.0;
entry_tip_outer_d = 124.8;

// PETG-friendly seating geometry.
support_mid_outer_d = 154.0;
support_mid_inner_d = 145.0;
throat_blend_outer_d = 144.0;
throat_blend_inner_d = 133.0;
nominal_opening_outer_d = 136.0;
nominal_opening_inner_d = hose_nominal_d;

slice_height = 0.35;
epsilon = 0.05;

// Heights below are expressed in print-oriented Z.
function raw_x_to_z(raw_x) = raw_x - raw_x_min;

anchor_z = raw_x_to_z(2.0);
support_mid_z = raw_x_to_z(9.0);
throat_blend_z = raw_x_to_z(15.0);
nominal_opening_z = raw_x_to_z(17.0);
lip_start_z = raw_x_to_z(20.0);
lip_bore_transition_end_z = raw_x_to_z(22.0);
lip_body_end_z = raw_x_to_z(29.0);
tip_z = raw_x_to_z(30.0) - slice_height;

module reference_mesh_raw() {
    import(file = reference_mesh_path, convexity = 10);
}

module print_oriented() {
    translate([0, 0, build_shift_z])
        rotate([0, -90, 0])
            children();
}

module reference_mesh() {
    print_oriented() reference_mesh_raw();
}

module z_profile_slice(z_pos, diameter) {
    translate([0, 0, z_pos])
        linear_extrude(height = slice_height)
            circle(d = diameter);
}

module insert_outer() {
    union() {
        hull() {
            z_profile_slice(anchor_z, anchor_overlap_outer_d);
            z_profile_slice(support_mid_z, support_mid_outer_d);
        }
        hull() {
            z_profile_slice(support_mid_z, support_mid_outer_d);
            z_profile_slice(throat_blend_z, throat_blend_outer_d);
        }
        hull() {
            z_profile_slice(throat_blend_z, throat_blend_outer_d);
            z_profile_slice(nominal_opening_z, nominal_opening_outer_d);
        }
        hull() {
            z_profile_slice(nominal_opening_z, nominal_opening_outer_d);
            z_profile_slice(lip_start_z, lip_outer_d);
        }
        hull() {
            z_profile_slice(lip_start_z, lip_outer_d);
            z_profile_slice(lip_body_end_z, lip_outer_d);
        }
        hull() {
            z_profile_slice(lip_body_end_z, lip_outer_d);
            z_profile_slice(tip_z, entry_tip_outer_d);
        }
    }
}

module insert_inner_bore() {
    union() {
        hull() {
            z_profile_slice(anchor_z - epsilon, anchor_overlap_inner_d);
            z_profile_slice(support_mid_z, support_mid_inner_d);
        }
        hull() {
            z_profile_slice(support_mid_z, support_mid_inner_d);
            z_profile_slice(throat_blend_z, throat_blend_inner_d);
        }
        hull() {
            z_profile_slice(throat_blend_z, throat_blend_inner_d);
            z_profile_slice(nominal_opening_z, nominal_opening_inner_d);
        }
        hull() {
            z_profile_slice(nominal_opening_z, nominal_opening_inner_d);
            z_profile_slice(lip_bore_transition_end_z, lip_bore_d);
        }
        hull() {
            z_profile_slice(lip_bore_transition_end_z, lip_bore_d);
            z_profile_slice(tip_z + epsilon, lip_bore_d);
        }
    }
}

module reducer_insert() {
    difference() {
        insert_outer();
        insert_inner_bore();
    }
}

module final_model() {
    union() {
        reference_mesh();
        reducer_insert();
    }
}

echo(str("task_mode = mesh_cleanup_and_remodel"));
echo(str("build height mm = ", build_height));
echo(str("nominal hose size mm = ", hose_nominal_d));
echo(str("lip geometry mm = ", lip_outer_d, " OD / ", lip_bore_d, " bore"));
echo(str("lip effective depth mm = ", (tip_z + slice_height) - lip_start_z));

if (show_reference) {
    color([0.75, 0.82, 0.90, 0.35]) reference_mesh();
}

final_model();
