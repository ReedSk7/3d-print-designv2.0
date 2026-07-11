// Battery strap holder / strap retainer bracket
// Task mode: reference_based_reconstruction
// Units: millimeters. X = width, Y = long direction, Z = vertical.
//
// Export variants by overriding variant_index:
//   1 = v01_exact
//   2 = v02_heavy_duty
//   3 = v03_fit_test
//
// A string override is also supported when your OpenSCAD shell quoting is reliable:
//   v01_exact
//   v02_heavy_duty
//   v03_fit_test

variant_index = 1;
selected_variant = variant_index == 3 ? "v03_fit_test" : variant_index == 2 ? "v02_heavy_duty" : is_undef(selected_variant_override) ? "v01_exact" : selected_variant_override;

// Overall measured Y length from outer end to outer end.
total_length_y = 74.1;

// Overall measured X width at the rounded screw bosses.
total_width_x = 11;

// Overall measured Z height / maximum thickness.
total_height_z = 7;

// Measured screw clearance hole diameter through both mounting ears.
hole_diameter = 4.8;

// Adjustable measured/estimated screw-hole center distance from each end.
hole_center_offset_from_end = 5.8;

// Adjustable width of the raised center strap bridge.
center_bar_width_x = 8.5;

// Top height of the raised center strap bridge.
center_bar_height_z = 7;

// Lower mounting-ear thickness at the screw-down areas.
base_thickness_z = 3;

// Open clearance under the raised center bridge for the battery strap.
strap_gap_z = 3.5;

// Plan-view corner radius used on rectangular bridge and transition features.
corner_radius = 2;

// Radius of the rounded screw boss ends. Clamped to total_width_x / 2.
screw_boss_radius = 5.5;

// Boolean/cutter overlap clearance for clean holes and exports.
clearance = 0.25;

// Extra parameters kept near the measured values so first-fit changes are easy.
transition_overlap_y = 1.2;      // bridge overlap into the rounded end bosses
fit_test_thickness_z = 2;        // thin plate for checking screw-hole spacing
edge_chamfer_z = 0.18;           // small print-friendly edge softening
heavy_bridge_extra_width_x = 1;  // v02 extra bridge width for durability
heavy_bridge_extra_thick_z = 0.35; // v02 lowers bridge underside slightly

$fn = 72;

function clamp(value, low, high) = min(max(value, low), high);
function boss_r() = min(screw_boss_radius, total_width_x / 2);
function half_y() = total_length_y / 2;
function hole_center_y_abs() = half_y() - hole_center_offset_from_end;
function boss_center_y_abs() = half_y() - boss_r();
function bridge_end_y_abs(overlap_y=transition_overlap_y) =
    half_y() - (2 * boss_r()) + overlap_y;
function safe_bridge_width(width_x=center_bar_width_x) =
    clamp(width_x, hole_diameter + (2 * clearance), total_width_x);
function center_top_z() = min(center_bar_height_z, total_height_z);
function safe_bridge_bottom_z(gap_z=strap_gap_z) =
    clamp(gap_z, base_thickness_z, center_top_z() - 1);

module rounded_rect_2d(width_x, length_y, radius_r) {
    r = max(0, min(radius_r, (width_x / 2) - 0.01, (length_y / 2) - 0.01));

    if (r <= 0) {
        square([width_x, length_y], center=true);
    } else {
        hull() {
            for (x = [-(width_x / 2) + r, (width_x / 2) - r])
                for (y = [-(length_y / 2) + r, (length_y / 2) - r])
                    translate([x, y])
                        circle(r=r);
        }
    }
}

module chamfered_extrude(height_z, chamfer_z=edge_chamfer_z) {
    c = clamp(chamfer_z, 0, height_z / 3);

    if (c <= 0) {
        linear_extrude(height=height_z)
            children();
    } else {
        union() {
            linear_extrude(height=c)
                offset(delta=-c)
                    children();
            translate([0, 0, c])
                linear_extrude(height=height_z - (2 * c))
                    children();
            translate([0, 0, height_z - c])
                linear_extrude(height=c)
                    offset(delta=-c)
                        children();
        }
    }
}

module bridge_footprint_2d(width_x=center_bar_width_x, overlap_y=transition_overlap_y) {
    rounded_rect_2d(
        safe_bridge_width(width_x),
        2 * bridge_end_y_abs(overlap_y),
        min(corner_radius, safe_bridge_width(width_x) / 2)
    );
}

module raised_end_footprint_2d(width_x=center_bar_width_x, overlap_y=transition_overlap_y) {
    bridge_w = safe_bridge_width(width_x);
    b_r = boss_r();

    for (s = [-1, 1]) {
        hull() {
            translate([0, s * boss_center_y_abs()])
                circle(r=b_r);
            translate([0, s * bridge_end_y_abs(overlap_y)])
                rounded_rect_2d(bridge_w, 0.2, 0.09);
        }
    }
}

module fit_test_footprint_2d() {
    spine_width_x = min(5, total_width_x);

    union() {
        for (s = [-1, 1])
            translate([0, s * boss_center_y_abs()])
                rounded_rect_2d(total_width_x, 2 * boss_r(), boss_r());

        rounded_rect_2d(
            spine_width_x,
            2 * bridge_end_y_abs(0),
            min(corner_radius, spine_width_x / 2)
        );
    }
}

module screw_holes(cut_height_z=total_height_z) {
    for (s = [-1, 1]) {
        translate([0, s * hole_center_y_abs(), -clearance])
            cylinder(h=cut_height_z + (2 * clearance), d=hole_diameter);
    }
}

module functional_holder(bridge_width_x=center_bar_width_x, bridge_gap_z=strap_gap_z, overlap_y=transition_overlap_y, chamfer_z=edge_chamfer_z) {
    bridge_bottom_z = safe_bridge_bottom_z(bridge_gap_z);
    bridge_height_z = center_top_z() - bridge_bottom_z;

    difference() {
        union() {
            // Lower screw-down ears: keep the mounting faces simple and flat.
            chamfered_extrude(base_thickness_z, chamfer_z)
                raised_end_footprint_2d(bridge_width_x, overlap_y);

            // Raised end bosses support screw load through the full 7 mm height.
            translate([0, 0, base_thickness_z])
                chamfered_extrude(total_height_z - base_thickness_z, chamfer_z)
                    raised_end_footprint_2d(bridge_width_x, overlap_y);

            // Raised center strap bridge. The underside is open by strap_gap_z.
            translate([0, 0, bridge_bottom_z])
                chamfered_extrude(bridge_height_z, chamfer_z)
                    bridge_footprint_2d(bridge_width_x, overlap_y);
        }

        screw_holes(total_height_z);
    }
}

module fit_test_plate() {
    difference() {
        linear_extrude(height=fit_test_thickness_z)
            fit_test_footprint_2d();
        screw_holes(fit_test_thickness_z);
    }
}

module battery_strap_holder(variant_name=selected_variant) {
    if (variant_name == "v03_fit_test") {
        fit_test_plate();
    } else if (variant_name == "v02_heavy_duty") {
        functional_holder(bridge_width_x=min(total_width_x, center_bar_width_x + heavy_bridge_extra_width_x), bridge_gap_z=max(base_thickness_z + clearance, strap_gap_z - heavy_bridge_extra_thick_z), overlap_y=transition_overlap_y + 0.8, chamfer_z=0.32);
    } else {
        functional_holder();
    }
}

battery_strap_holder(selected_variant);
