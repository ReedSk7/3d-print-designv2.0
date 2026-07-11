material = "petg";
nozzle_diameter = 0.4;
wall_thickness = 3.2;
fit_clearance = 0.2;
validation_marker_size = 0.01;
export_variant = "metal_pin_body";

module wrapper_validation_marker() {
    cube([validation_marker_size, validation_marker_size, validation_marker_size]);
}

include <perko_1247_high_torque_deck_plate_key_v01.scad>
