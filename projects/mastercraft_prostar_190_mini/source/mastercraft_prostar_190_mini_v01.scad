$fn = 72;

full_size_length_in = 19 * 12 + 6;  // 19'6" for late ProStar 190 models
full_size_beam_in = 85;

model_length = 128;
swim_platform_length = 8;
hull_length = model_length - swim_platform_length;
scale_ratio = model_length / (full_size_length_in * 25.4);

beam = full_size_beam_in * 25.4 * scale_ratio;
deck_height = 16;
windshield_height = 5.5;
windshield_width = beam * 0.74;
cockpit_open_length = 38;
cockpit_open_width = beam * 0.58;
swim_platform_width = beam * 0.62;
swim_platform_thickness = 1.8;

module side_profile_2d() {
    polygon(points = [
        [0, 10.8],
        [14, 11.0],
        [40, 11.8],
        [72, 12.6],
        [96, 13.4],
        [110, 14.0],
        [118, 14.2],
        [120, 13.2],
        [118, 10.8],
        [112, 7.0],
        [102, 3.8],
        [88, 1.8],
        [64, 0.6],
        [34, 0.0],
        [10, 0.0],
        [0, 0.6]
    ]);
}

module plan_profile_2d() {
    polygon(points = [
        [0, beam * 0.50],
        [10, beam * 0.52],
        [30, beam * 0.55],
        [60, beam * 0.58],
        [82, beam * 0.57],
        [96, beam * 0.52],
        [108, beam * 0.40],
        [116, beam * 0.22],
        [120, 0],
        [116, -beam * 0.22],
        [108, -beam * 0.40],
        [96, -beam * 0.52],
        [82, -beam * 0.57],
        [60, -beam * 0.58],
        [30, -beam * 0.55],
        [10, -beam * 0.52],
        [0, -beam * 0.50]
    ]);
}

module hull_blank() {
    intersection() {
        rotate([90, 0, 0])
            linear_extrude(height = beam, center = true, convexity = 10)
                side_profile_2d();
        linear_extrude(height = deck_height + 6, convexity = 10)
            plan_profile_2d();
    }
}

module cockpit_cut() {
    hull() {
        translate([62, 0, 13.4])
            scale([10, cockpit_open_width * 0.44, 4.2])
                sphere(1);
        translate([84, 0, 12.7])
            scale([18, cockpit_open_width * 0.55, 5.6])
                sphere(1);
    }

    translate([94, 0, 11.8])
        scale([10, cockpit_open_width * 0.34, 3.6])
            sphere(1);
}

module windshield_massing() {
    hull() {
        translate([57, 0, 11.8])
            scale([4.8, windshield_width * 0.48, 2.4])
                sphere(1);
        translate([66, 0, 16.0])
            scale([3.4, windshield_width * 0.34, 2.0])
                sphere(1);
    }
}

module swim_platform() {
    translate([-swim_platform_length + 1.0, -swim_platform_width / 2, 9.4])
        cube([swim_platform_length + 1.0, swim_platform_width, swim_platform_thickness], center = false);
}

module boat_model() {
    difference() {
        union() {
            hull_blank();
            windshield_massing();
            swim_platform();
        }

        cockpit_cut();
    }
}

boat_model();
