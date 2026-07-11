// project_stem: kobalt_81798_socket_organizer
// version: v03b fit-test plate only
// task_mode: reference_based_reconstruction
// Customer-facing calibration plate with separate aligned body and label STLs.
// Units: millimeters. Z+ is up.

$fn = 64;

project_version = "v03b";
render_mode = "combined_preview"; // combined_preview, body, labels
render_mode_index = 0; // 0 combined_preview, 1 body, 2 labels
render_mode_index_override = -1;

plate_w = 228.0;
plate_d = 98.0;
base_thickness = 12.70;

pocket_chamfer = 1.0;
pocket_depth_1_4 = 5.5;
pocket_depth_3_8 = 6.5;
pocket_depth_1_2 = 7.5;
long_channel_depth = 4.0;

lip_width = 1.2;
lip_height = 0.8;
label_height = 0.70;
label_font = "Liberation Sans:style=Bold";

// Representative calibration diameters. These are pocket diameters, not socket ODs.
d_1_4_small = 13.0;
d_1_4_large = 14.0;
d_3_8_small = 16.0;
d_3_8_large = 21.0;
d_1_2_small = 22.0;
d_1_2_large = 30.0;
long_shaft_width = 7.8;
long_end_pocket_d = 19.4;

hole_y = 66.0;
label_title_y = 40.0;
label_dia_y = 32.0;

module pocket_cut(x, y, diameter, depth) {
    translate([x, y, base_thickness - depth - 0.02])
        cylinder(h = depth + 0.05, d = diameter);
    translate([x, y, base_thickness - pocket_chamfer])
        cylinder(h = pocket_chamfer + 0.08, d1 = diameter, d2 = diameter + 2 * pocket_chamfer);
}

module rounded_channel_cut(x1, y1, x2, y2, width, depth) {
    translate([0, 0, base_thickness - depth - 0.02])
        hull() {
            translate([x1, y1, 0]) cylinder(h = depth + 0.05, d = width);
            translate([x2, y2, 0]) cylinder(h = depth + 0.05, d = width);
        }
    translate([0, 0, base_thickness - pocket_chamfer])
        hull() {
            translate([x1, y1, 0]) cylinder(h = pocket_chamfer + 0.08, d = width + 2 * pocket_chamfer);
            translate([x2, y2, 0]) cylinder(h = pocket_chamfer + 0.08, d = width + 2 * pocket_chamfer);
        }
}

module perimeter_lip() {
    translate([0, 0, base_thickness]) cube([plate_w, lip_width, lip_height]);
    translate([0, plate_d - lip_width, base_thickness]) cube([plate_w, lip_width, lip_height]);
    translate([0, 0, base_thickness]) cube([lip_width, plate_d, lip_height]);
    translate([plate_w - lip_width, 0, base_thickness]) cube([lip_width, plate_d, lip_height]);
}

module fit_test_plate_body() {
    color([0.08, 0.20, 0.90])
        difference() {
            union() {
                cube([plate_w, plate_d, base_thickness]);
                perimeter_lip();
            }
            pocket_cut(19, hole_y, d_1_4_small, pocket_depth_1_4);
            pocket_cut(55, hole_y, d_1_4_large, pocket_depth_1_4);
            pocket_cut(91, hole_y, d_3_8_small, pocket_depth_3_8);
            pocket_cut(127, hole_y, d_3_8_large, pocket_depth_3_8);
            pocket_cut(166, hole_y, d_1_2_small, pocket_depth_1_2);
            pocket_cut(207, hole_y, d_1_2_large, pocket_depth_1_2);

            rounded_channel_cut(24, 16, 132, 16, long_shaft_width, long_channel_depth);
            pocket_cut(150, 16, long_end_pocket_d, pocket_depth_3_8);
        }
}

module label_line(txt, x, y, size = 5.4) {
    translate([x, y, base_thickness])
        linear_extrude(height = label_height)
            text(txt, size = size, font = label_font, halign = "center", valign = "center");
}

module pocket_label(title, dia_text, x) {
    label_line(title, x, label_title_y, 5.6);
    label_line(dia_text, x, label_dia_y, 5.0);
}

module fit_test_plate_labels() {
    color([0.95, 0.08, 0.03]) {
        pocket_label("1/4 SM", "13.0MM", 19);
        pocket_label("1/4 LG", "14.0MM", 55);
        pocket_label("3/8 SM", "16.0MM", 91);
        pocket_label("3/8 LG", "21.0MM", 127);
        pocket_label("1/2 SM", "22.0MM", 166);
        pocket_label("1/2 LG", "30.0MM", 207);

        label_line("LONG SHAFT", 80, 8, 5.2);
        label_line("7.8MM", 126, 8, 5.0);
        label_line("END POCKET", 190, 22, 5.2);
        label_line("19.4MM", 190, 12, 5.0);
    }
}

module combined_preview() {
    fit_test_plate_body();
    fit_test_plate_labels();
}

mode = render_mode_index_override >= 0 ? render_mode_index_override : render_mode_index;

if (mode == 1 || render_mode == "body") {
    fit_test_plate_body();
} else if (mode == 2 || render_mode == "labels") {
    fit_test_plate_labels();
} else {
    combined_preview();
}
