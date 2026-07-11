// hardware_library.scad
// Parametric FDM hardware starters for common fasteners.
// Units: millimeters.
//
// Measured hardware and supplier drawings override these starter values.
// Use lowercase hardware names: "m3", "m4", "m5", "number_8_wood", "quarter_20".
// Use fit classes: "close", "normal", "loose".

function material_hole_offset(material) =
    (material == "pla") ? 0.00 :
    (material == "petg") ? 0.05 :
    (material == "asa") ? 0.07 :
    (material == "abs") ? 0.07 :
    (material == "tpu") ? 0.15 :
    0.05;

function nozzle_hole_offset(nozzle_diameter) =
    nozzle_diameter <= 0.40 ? 0.00 :
    nozzle_diameter <= 0.60 ? 0.10 :
    (nozzle_diameter - 0.40) * 0.50;

function hardware_nominal_d(bolt_size) =
    (bolt_size == "m3") ? 3.00 :
    (bolt_size == "m4") ? 4.00 :
    (bolt_size == "m5") ? 5.00 :
    (bolt_size == "number_8_wood") ? 4.40 :
    (bolt_size == "quarter_20") ? 6.35 :
    undef;

function clearance_base_d(bolt_size, fit_class="normal") =
    (bolt_size == "number_8_wood") ?
        (fit_class == "normal" ? 4.65 : undef) :
    (bolt_size == "m3") ?
        (fit_class == "close" ? 3.20 : fit_class == "loose" ? 3.60 : 3.40) :
    (bolt_size == "m4") ?
        (fit_class == "close" ? 4.30 : fit_class == "loose" ? 4.80 : 4.50) :
    (bolt_size == "m5") ?
        (fit_class == "close" ? 5.30 : fit_class == "loose" ? 5.80 : 5.50) :
    (bolt_size == "quarter_20") ?
        (fit_class == "close" ? 6.60 : fit_class == "loose" ? 7.10 : 6.80) :
    undef;

function clearance_hole_d(bolt_size, fit_class="normal", material="petg", nozzle_diameter=0.40) =
    clearance_base_d(bolt_size, fit_class) == undef ? undef :
    clearance_base_d(bolt_size, fit_class)
        + material_hole_offset(material)
        + nozzle_hole_offset(nozzle_diameter);

function pilot_hole_d(bolt_size, material="petg") =
    (bolt_size == "m3") ? (material == "pla" ? 2.45 : 2.50) :
    (bolt_size == "m4") ? (material == "pla" ? 3.25 : 3.30) :
    (bolt_size == "m5") ? (material == "pla" ? 4.10 : 4.20) :
    (bolt_size == "quarter_20") ? (material == "pla" ? 5.10 : 5.20) :
    undef;

function counterbore_d(bolt_size, fit_class="normal", material="petg", nozzle_diameter=0.40) =
    (bolt_size == "number_8_wood") ? 9.25 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m3") ? 6.20 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m4") ? 8.20 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m5") ? 10.20 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "quarter_20") ? 12.80 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    undef;

function counterbore_depth(bolt_size, head_clearance=0.40) =
    (bolt_size == "number_8_wood") ? 2.40 + head_clearance :
    (bolt_size == "m3") ? 3.00 + head_clearance :
    (bolt_size == "m4") ? 4.00 + head_clearance :
    (bolt_size == "m5") ? 5.00 + head_clearance :
    (bolt_size == "quarter_20") ? 6.35 + head_clearance :
    undef;

function countersink_head_d(bolt_size, fit_class="normal", material="petg", nozzle_diameter=0.40) =
    (bolt_size == "number_8_wood") ? 9.25 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m3") ? 6.30 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m4") ? 8.40 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m5") ? 10.50 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "quarter_20") ? 13.50 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    undef;

function countersink_angle(bolt_size) =
    (bolt_size == "quarter_20") ? 82 :
    (bolt_size == "number_8_wood") ? 82 :
    (bolt_size == "m3" || bolt_size == "m4" || bolt_size == "m5") ? 90 :
    undef;

function countersink_depth(bolt_size, fit_class="normal", material="petg", nozzle_diameter=0.40) =
    (countersink_head_d(bolt_size, fit_class, material, nozzle_diameter)
        - clearance_hole_d(bolt_size, fit_class, material, nozzle_diameter))
    / (2 * tan(countersink_angle(bolt_size) / 2));

function washer_pocket_d(bolt_size, fit_class="normal", material="petg", nozzle_diameter=0.40) =
    (bolt_size == "m3") ? 7.20 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m4") ? 9.20 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m5") ? 10.80 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "quarter_20") ? 14.80 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    undef;

function heat_set_insert_bore_d(bolt_size, material="petg", nozzle_diameter=0.40) =
    (bolt_size == "m3") ? 4.20 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m4") ? 5.60 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    (bolt_size == "m5") ? 6.40 + material_hole_offset(material) + nozzle_hole_offset(nozzle_diameter) :
    undef;

function heat_set_insert_depth(bolt_size, depth_clearance=0.50) =
    (bolt_size == "m3") ? 5.00 + depth_clearance :
    (bolt_size == "m4") ? 6.00 + depth_clearance :
    (bolt_size == "m5") ? 8.00 + depth_clearance :
    undef;

function min_boss_outer_d(bolt_size, wall_thickness=3.20, fit_class="normal", material="petg", nozzle_diameter=0.40) =
    clearance_hole_d(bolt_size, fit_class, material, nozzle_diameter) + (2 * wall_thickness);

module clearance_hole(bolt_size, height, fit_class="normal", material="petg", nozzle_diameter=0.40, center=false) {
    hole_d = clearance_hole_d(bolt_size, fit_class, material, nozzle_diameter);
    assert(hole_d != undef, str("unsupported bolt_size: ", bolt_size))
        cylinder(h=height, d=hole_d, center=center);
}

module pilot_hole(bolt_size, height, material="petg", center=false) {
    hole_d = pilot_hole_d(bolt_size, material);
    assert(hole_d != undef, str("unsupported bolt_size: ", bolt_size))
        cylinder(h=height, d=hole_d, center=center);
}

module counterbore_pocket(bolt_size, depth, fit_class="normal", material="petg", nozzle_diameter=0.40, center=false) {
    pocket_d = counterbore_d(bolt_size, fit_class, material, nozzle_diameter);
    assert(pocket_d != undef, str("unsupported bolt_size: ", bolt_size))
        cylinder(h=depth, d=pocket_d, center=center);
}

module countersink_pocket(bolt_size, fit_class="normal", material="petg", nozzle_diameter=0.40) {
    head_d = countersink_head_d(bolt_size, fit_class, material, nozzle_diameter);
    shaft_d = clearance_hole_d(bolt_size, fit_class, material, nozzle_diameter);
    depth = countersink_depth(bolt_size, fit_class, material, nozzle_diameter);
    assert(head_d != undef && shaft_d != undef && depth != undef, str("unsupported bolt_size: ", bolt_size))
        cylinder(h=depth, d1=head_d, d2=shaft_d);
}

module washer_pocket(bolt_size, depth, fit_class="normal", material="petg", nozzle_diameter=0.40, center=false) {
    pocket_d = washer_pocket_d(bolt_size, fit_class, material, nozzle_diameter);
    assert(pocket_d != undef, str("unsupported bolt_size: ", bolt_size))
        cylinder(h=depth, d=pocket_d, center=center);
}

module heat_set_insert_pocket(bolt_size, material="petg", nozzle_diameter=0.40, depth_clearance=0.50, center=false) {
    pocket_d = heat_set_insert_bore_d(bolt_size, material, nozzle_diameter);
    pocket_depth = heat_set_insert_depth(bolt_size, depth_clearance);
    assert(pocket_d != undef && pocket_depth != undef, str("unsupported insert bolt_size: ", bolt_size))
        cylinder(h=pocket_depth, d=pocket_d, center=center);
}
