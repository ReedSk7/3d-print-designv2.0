// project_stem: kobalt_81798_socket_organizer
// version: v04
// task_mode: reference_based_reconstruction
// v04 corrective rebuild: free-STL-informed pocket diameters plus interlocking shiplap tab seams.
// Units: millimeters. Z+ is up. OpenSCAD remains the source of truth.

$fn = 48;

project_version = "v04";
render_mode = "reference_layout";
render_mode_index = 0;
render_mode_index_override = -1;
// 0 reference_layout
// 1 left_top_body, 2 left_top_labels, 3 left_bottom_body, 4 left_bottom_labels
// 5 center_top_left_body, 6 center_top_left_labels
// 7 center_top_right_body, 8 center_top_right_labels
// 9 center_bottom_left_body, 10 center_bottom_left_labels
// 11 center_bottom_right_body, 12 center_bottom_right_labels
// 13 right_top_body, 14 right_top_labels, 15 right_bottom_body, 16 right_bottom_labels
// 17 fit_test_plate_body, 18 fit_test_plate_labels

overall_width = 621.030;
overall_depth = 332.740;
base_thickness = 12.700;
safe_build_max = 245.000;
printer_build = [256, 256, 256];
min_floor = 2.5;
min_web = 2.5;
edge_margin = 5.0;
pocket_chamfer = 1.0;
label_height = 0.700;
label_font = "Liberation Sans:style=Bold";
label_size_min = 5.0;
long_channel_depth = 4.0;
lip_height = 0.8;
lip_width = 1.2;
rib_height = 0.65;
rib_width = 1.4;
seam_lap_width = 8.0;
seam_clearance = 0.25;

// Inventory field indices.
F_MODULE = 0;
F_GROUP = 1;
F_DRIVE = 2;
F_TYPE = 3;
F_RAW_LABEL = 4;
F_DISPLAY_LABEL = 5;
F_POCKET_DIAMETER = 6;
F_POCKET_DEPTH = 7;
F_ROW_ID = 8;
F_SORT_ORDER = 9;
F_KIND = 10;
F_X = 11;
F_Y = 12;
F_LABEL_X = 13;
F_LABEL_Y = 14;
F_LABEL_ROT = 15;
F_LABEL_SIZE = 16;
F_CHANNEL_WIDTH = 17;
F_CHANNEL_X1 = 18;
F_CHANNEL_Y1 = 19;
F_CHANNEL_X2 = 20;
F_CHANNEL_Y2 = 21;
F_END_X = 22;
F_END_Y = 23;

// Machine-readable v04 inventory. Every storage row has explicit diameter data.
inventory = [
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "5/8", "5_8", 22.500, 7.500, "lt_01", 1, "cup", 28.250, 178.000, 28.250, 162.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 17.750, 178.000],
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "11/16", "11_16", 24.500, 7.500, "lt_01", 2, "cup", 69.053, 178.000, 69.053, 161.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 63.803, 178.000],
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "3/4", "3_4", 26.500, 7.500, "lt_01", 3, "cup", 109.855, 178.000, 109.855, 160.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 178.000],
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "13/16", "13_16", 30.500, 7.500, "lt_01", 4, "cup", 150.657, 178.000, 150.657, 158.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 155.907, 178.000],
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "7/8", "7_8", 32.500, 7.500, "lt_01", 5, "cup", 191.460, 178.000, 191.460, 157.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 201.960, 178.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "E18", "E18", 22.500, 7.500, "lt_02", 6, "cup", 24.750, 139.000, 24.750, 123.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 17.400, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "E20", "E20", 23.500, 7.500, "lt_02", 7, "cup", 53.118, 139.000, 53.118, 122.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 48.218, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "E22", "E22", 24.500, 7.500, "lt_02", 8, "cup", 81.487, 139.000, 81.487, 122.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 79.037, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "E24", "E24", 25.000, 7.500, "lt_02", 9, "cup", 109.855, 139.000, 109.855, 122.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "T55", "T55", 24.500, 7.500, "lt_02", 10, "cup", 138.223, 139.000, 138.223, 122.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 140.673, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "T60", "T60", 25.000, 7.500, "lt_02", 11, "cup", 166.592, 139.000, 166.592, 122.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 171.492, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "T70", "T70", 25.500, 7.500, "lt_02", 12, "cup", 194.960, 139.000, 194.960, 121.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 202.310, 139.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "5/16", "5_16", 20.800, 7.500, "lt_03", 13, "cup", 23.000, 100.000, 23.000, 85.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 17.000, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "3/8", "3_8", 21.000, 7.500, "lt_03", 14, "cup", 47.816, 100.000, 47.816, 85.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 43.530, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "7/16", "7_16", 21.200, 7.500, "lt_03", 15, "cup", 72.631, 100.000, 72.631, 85.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 70.060, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "1/2", "1_2", 21.400, 7.500, "lt_03", 16, "cup", 97.447, 100.000, 97.447, 84.950, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 96.590, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "9/16", "9_16", 21.600, 7.500, "lt_03", 17, "cup", 122.263, 100.000, 122.263, 84.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 123.120, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "5/8", "5_8", 21.800, 7.500, "lt_03", 18, "cup", 147.079, 100.000, 147.079, 84.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 149.650, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "11/16", "11_16", 22.000, 7.500, "lt_03", 19, "cup", 171.894, 100.000, 171.894, 84.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 176.180, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "3/4", "3_4", 22.000, 7.500, "lt_03", 20, "cup", 196.710, 100.000, 196.710, 84.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 202.710, 100.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "6mm", "6M", 22.500, 7.500, "lt_04", 21, "cup", 24.500, 61.000, 24.500, 45.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 16.750, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "7mm", "7M", 22.800, 7.500, "lt_04", 22, "cup", 52.952, 61.000, 52.952, 45.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 47.785, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "8mm", "8M", 23.200, 7.500, "lt_04", 23, "cup", 81.403, 61.000, 81.403, 45.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 78.820, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "9mm", "9M", 23.600, 7.500, "lt_04", 24, "cup", 109.855, 61.000, 109.855, 44.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "10mm", "10M", 24.000, 7.500, "lt_04", 25, "cup", 138.307, 61.000, 138.307, 44.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 140.890, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "11mm", "11M", 24.500, 7.500, "lt_04", 26, "cup", 166.758, 61.000, 166.758, 44.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 171.925, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "12mm", "12M", 25.000, 7.500, "lt_04", 27, "cup", 195.210, 61.000, 195.210, 44.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 202.960, 61.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "13mm", "13M", 23.000, 7.500, "lt_05", 28, "cup", 24.750, 22.000, 24.750, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 17.600, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "14mm", "14M", 23.500, 7.500, "lt_05", 29, "cup", 53.118, 22.000, 53.118, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 48.352, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "15mm", "15M", 24.000, 7.500, "lt_05", 30, "cup", 81.487, 22.000, 81.487, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 79.103, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "16mm", "16M", 24.500, 7.500, "lt_05", 31, "cup", 109.855, 22.000, 109.855, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "17mm", "17M", 25.000, 7.500, "lt_05", 32, "cup", 138.223, 22.000, 138.223, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 140.607, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "18mm", "18M", 25.300, 7.500, "lt_05", 33, "cup", 166.592, 22.000, 166.592, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 171.358, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "19mm", "19M", 25.500, 7.500, "lt_05", 34, "cup", 194.960, 22.000, 194.960, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 202.110, 22.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "1/4", "1_4", 17.500, 6.500, "lb_01", 35, "cup", 25.250, 116.000, 25.250, 102.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 15.000, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "5/16", "5_16", 18.500, 6.500, "lb_01", 36, "cup", 59.092, 116.000, 59.092, 102.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 52.942, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "3/8", "3_8", 20.500, 6.500, "lb_01", 37, "cup", 92.934, 116.000, 92.934, 101.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 90.884, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "7/16", "7_16", 22.500, 6.500, "lb_01", 38, "cup", 126.776, 116.000, 126.776, 100.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 128.826, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "1/2", "1_2", 24.500, 6.500, "lb_01", 39, "cup", 160.618, 116.000, 160.618, 99.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 166.768, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "9/16", "9_16", 26.500, 6.500, "lb_01", 40, "cup", 194.460, 116.000, 194.460, 98.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 204.710, 116.000],
    ["left_bottom", "3/8DR external Torx", "3/8", "external Torx", "E10", "E10", 17.500, 6.500, "lb_02", 41, "cup", 23.250, 84.000, 23.250, 70.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 14.700, 84.000],
    ["left_bottom", "3/8DR external Torx", "3/8", "external Torx", "E12", "E12", 18.500, 6.500, "lb_02", 42, "cup", 80.987, 84.000, 80.987, 70.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 78.137, 84.000],
    ["left_bottom", "3/8DR external Torx", "3/8", "external Torx", "E14", "E14", 20.500, 6.500, "lb_02", 43, "cup", 138.723, 84.000, 138.723, 69.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 141.573, 84.000],
    ["left_bottom", "3/8DR external Torx", "3/8", "external Torx", "E16", "E16", 22.500, 6.500, "lb_02", 44, "cup", 196.460, 84.000, 196.460, 68.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 205.010, 84.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "1/8", "1_8", 17.500, 6.500, "lb_03", 45, "cup", 24.250, 52.000, 24.250, 38.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 14.800, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "5/32", "5_32", 17.800, 6.500, "lb_03", 46, "cup", 52.785, 52.000, 52.785, 38.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 46.485, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "3/16", "3_16", 18.500, 6.500, "lb_03", 47, "cup", 81.320, 52.000, 81.320, 38.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 78.170, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "7/32", "7_32", 20.500, 6.500, "lb_03", 48, "cup", 109.855, 52.000, 109.855, 37.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "1/4", "1_4", 21.500, 6.500, "lb_03", 49, "cup", 138.390, 52.000, 138.390, 36.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 141.540, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "5/16", "5_16", 22.500, 6.500, "lb_03", 50, "cup", 166.925, 52.000, 166.925, 36.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 173.225, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "3/8", "3_8", 24.500, 6.500, "lb_03", 51, "cup", 195.460, 52.000, 195.460, 35.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 204.910, 52.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "3mm", "3M", 15.200, 6.500, "lb_04", 52, "cup", 20.500, 20.000, 20.500, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 14.000, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "4mm", "4M", 15.400, 6.500, "lb_04", 53, "cup", 40.357, 20.000, 40.357, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 35.301, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "5mm", "5M", 15.600, 6.500, "lb_04", 54, "cup", 60.213, 20.000, 60.213, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 56.602, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "6mm", "6M", 15.800, 6.500, "lb_04", 55, "cup", 80.070, 20.000, 80.070, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 77.903, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "7mm", "7M", 16.000, 6.500, "lb_04", 56, "cup", 99.927, 20.000, 99.927, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 99.204, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "8mm", "8M", 16.200, 6.500, "lb_04", 57, "cup", 119.783, 20.000, 119.783, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 120.506, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "9mm", "9M", 16.400, 6.500, "lb_04", 58, "cup", 139.640, 20.000, 139.640, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 141.807, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "10mm", "10M", 16.600, 6.500, "lb_04", 59, "cup", 159.497, 20.000, 159.497, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 163.108, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "11mm", "11M", 16.800, 6.500, "lb_04", 60, "cup", 179.353, 20.000, 179.353, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 184.409, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "12mm", "12M", 17.000, 6.500, "lb_04", 61, "cup", 199.210, 20.000, 199.210, 5.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 205.710, 20.000],
    ["right_top", "1/4DR 8-point shallow SAE", "1/4", "8-point shallow SAE", "1/4", "1_4", 12.500, 5.500, "rt_01", 62, "cup", 16.250, 140.000, 16.250, 150.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.700, 140.000],
    ["right_top", "1/4DR 8-point shallow SAE", "1/4", "8-point shallow SAE", "5/16", "5_16", 14.500, 5.500, "rt_01", 63, "cup", 73.660, 140.000, 73.660, 151.000, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 140.000],
    ["right_top", "1/4DR 8-point shallow SAE", "1/4", "8-point shallow SAE", "3/8", "3_8", 16.500, 5.500, "rt_01", 64, "cup", 131.070, 140.000, 131.070, 151.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 134.620, 140.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E4", "E4", 12.500, 5.500, "rt_02", 65, "cup", 15.250, 119.000, 15.250, 109.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.000, 119.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E5", "E5", 12.500, 5.500, "rt_02", 66, "cup", 44.455, 119.000, 44.455, 109.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 42.830, 119.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E6", "E6", 13.000, 5.500, "rt_02", 67, "cup", 73.660, 119.000, 73.660, 108.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 119.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E7", "E7", 13.500, 5.500, "rt_02", 68, "cup", 102.865, 119.000, 102.865, 108.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 104.490, 119.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E8", "E8", 14.500, 5.500, "rt_02", 69, "cup", 132.070, 119.000, 132.070, 108.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.320, 119.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "1/16", "1_16", 12.500, 5.500, "rt_03", 70, "cup", 14.750, 98.000, 14.750, 88.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 11.500, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "5/64", "5_64", 12.500, 5.500, "rt_03", 71, "cup", 44.205, 98.000, 44.205, 88.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 42.580, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "3/32", "3_32", 12.500, 5.500, "rt_03", 72, "cup", 73.660, 98.000, 73.660, 88.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "7/64", "7_64", 13.000, 5.500, "rt_03", 73, "cup", 103.115, 98.000, 103.115, 87.950, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 104.740, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "1/8", "1_8", 13.500, 5.500, "rt_03", 74, "cup", 132.570, 98.000, 132.570, 87.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.820, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "9/64", "9_64", 13.500, 5.500, "rt_04", 75, "cup", 15.750, 77.000, 15.750, 66.550, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 12.500, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "5/32", "5_32", 14.000, 5.500, "rt_04", 76, "cup", 44.705, 77.000, 44.705, 66.550, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 43.080, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "3/16", "3_16", 14.500, 5.500, "rt_04", 77, "cup", 73.660, 77.000, 73.660, 66.550, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "7/32", "7_32", 15.000, 5.500, "rt_04", 78, "cup", 102.615, 77.000, 102.615, 66.550, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 104.240, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "1/4", "1_4", 15.500, 5.500, "rt_04", 79, "cup", 131.570, 77.000, 131.570, 66.550, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 134.820, 77.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "2mm", "2M", 12.500, 5.500, "rt_05", 80, "cup", 15.750, 56.000, 15.750, 46.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.300, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "2.5mm", "2_5M", 12.500, 5.500, "rt_05", 81, "cup", 38.914, 56.000, 38.914, 46.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 36.844, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "3mm", "3M", 13.000, 5.500, "rt_05", 82, "cup", 62.078, 56.000, 62.078, 46.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 61.388, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "4mm", "4M", 13.500, 5.500, "rt_05", 83, "cup", 85.242, 56.000, 85.242, 45.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 85.932, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "5mm", "5M", 14.500, 5.500, "rt_05", 84, "cup", 108.406, 56.000, 108.406, 45.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 110.476, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "6mm", "6M", 15.500, 5.500, "rt_05", 85, "cup", 131.570, 56.000, 131.570, 44.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.020, 56.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "7/32 slot", "7_32", 14.000, 5.500, "rt_06", 86, "cup", 15.500, 35.000, 15.500, 24.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.300, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "1/4 slot", "1_4", 15.000, 5.500, "rt_06", 87, "cup", 38.764, 35.000, 38.764, 23.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 36.844, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "PH3", "PH3", 14.500, 5.500, "rt_06", 88, "cup", 62.028, 35.000, 62.028, 24.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 61.388, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "S1", "S1", 13.000, 5.500, "rt_06", 89, "cup", 85.292, 35.000, 85.292, 24.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 85.932, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "S2", "S2", 13.500, 5.500, "rt_06", 90, "cup", 108.556, 35.000, 108.556, 24.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 110.476, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "PZ1", "PZ1", 14.000, 5.500, "rt_06", 91, "cup", 131.820, 35.000, 131.820, 24.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.020, 35.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T8", "T8", 12.500, 5.500, "rt_07", 92, "cup", 15.000, 14.000, 15.000, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 12.200, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T9", "T9", 12.500, 5.500, "rt_07", 93, "cup", 31.760, 14.000, 31.760, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 29.760, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T10", "T10", 12.500, 5.500, "rt_07", 94, "cup", 48.520, 14.000, 48.520, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 47.320, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T15", "T15", 13.000, 5.500, "rt_07", 95, "cup", 65.280, 14.000, 65.280, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 64.880, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T20", "T20", 13.300, 5.500, "rt_07", 96, "cup", 82.040, 14.000, 82.040, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 82.440, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T25", "T25", 13.600, 5.500, "rt_07", 97, "cup", 98.800, 14.000, 98.800, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 100.000, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T27", "T27", 13.800, 5.500, "rt_07", 98, "cup", 115.560, 14.000, 115.560, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 117.560, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T30", "T30", 14.000, 5.500, "rt_07", 99, "cup", 132.320, 14.000, 132.320, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 135.120, 14.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T20", "T20", 17.000, 6.500, "rb_01", 100, "cup", 18.250, 160.000, 18.250, 145.900, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 15.250, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T25", "T25", 17.800, 6.500, "rb_01", 101, "cup", 45.955, 160.000, 45.955, 145.900, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 44.455, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T27", "T27", 18.500, 6.500, "rb_01", 102, "cup", 73.660, 160.000, 73.660, 145.900, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T30", "T30", 19.200, 6.500, "rb_01", 103, "cup", 101.365, 160.000, 101.365, 145.900, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 102.865, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T40", "T40", 20.500, 6.500, "rb_01", 104, "cup", 129.070, 160.000, 129.070, 145.900, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 132.070, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T45", "T45", 21.200, 6.500, "rb_02", 105, "cup", 19.600, 130.000, 19.600, 115.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 16.600, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T47", "T47", 21.800, 6.500, "rb_02", 106, "cup", 55.640, 130.000, 55.640, 115.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 54.640, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T50", "T50", 22.500, 6.500, "rb_02", 107, "cup", 91.680, 130.000, 91.680, 115.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 92.680, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T55", "T55", 23.200, 6.500, "rb_02", 108, "cup", 127.720, 130.000, 127.720, 115.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 130.720, 130.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT15", "TT15", 16.800, 6.500, "rb_03", 109, "cup", 17.600, 103.000, 17.600, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 14.600, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT20", "TT20", 17.400, 6.500, "rb_03", 110, "cup", 45.630, 103.000, 45.630, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 44.130, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT25", "TT25", 18.000, 6.500, "rb_03", 111, "cup", 73.660, 103.000, 73.660, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT27", "TT27", 18.600, 6.500, "rb_03", 112, "cup", 101.690, 103.000, 101.690, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 103.190, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT30", "TT30", 19.200, 6.500, "rb_03", 113, "cup", 129.720, 103.000, 129.720, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 132.720, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT40", "TT40", 20.400, 6.500, "rb_04", 114, "cup", 19.700, 75.000, 19.700, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 16.700, 75.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT45", "TT45", 21.000, 6.500, "rb_04", 115, "cup", 46.680, 75.000, 46.680, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 45.180, 75.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT50", "TT50", 21.800, 6.500, "rb_04", 116, "cup", 73.660, 75.000, 73.660, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 75.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT55", "TT55", 22.600, 6.500, "rb_04", 117, "cup", 100.640, 75.000, 100.640, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 102.140, 75.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT60", "TT60", 23.400, 6.500, "rb_04", 118, "cup", 127.620, 75.000, 127.620, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 130.620, 75.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "9/32 flat", "9_32", 18.600, 6.500, "rb_05", 119, "cup", 18.250, 47.000, 18.250, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 15.250, 47.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "3/8 flat", "3_8", 20.500, 6.500, "rb_05", 120, "cup", 45.955, 47.000, 45.955, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 44.455, 47.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "4mm flat", "4M", 17.200, 6.500, "rb_05", 121, "cup", 73.660, 47.000, 73.660, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 47.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "5mm flat", "5M", 18.400, 6.500, "rb_05", 122, "cup", 101.365, 47.000, 101.365, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 102.865, 47.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "6mm flat", "6M", 19.600, 6.500, "rb_05", 123, "cup", 129.070, 47.000, 129.070, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 132.070, 47.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH1", "PH1", 17.800, 6.500, "rb_06", 124, "cup", 18.100, 20.000, 18.100, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 15.100, 20.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH2", "PH2", 18.800, 6.500, "rb_06", 125, "cup", 45.880, 20.000, 45.880, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 44.380, 20.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH3", "PH3", 19.800, 6.500, "rb_06", 126, "cup", 73.660, 20.000, 73.660, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 20.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PZ2", "PZ2", 19.200, 6.500, "rb_06", 127, "cup", 101.440, 20.000, 101.440, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 102.940, 20.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PZ3", "PZ3", 20.200, 6.500, "rb_06", 128, "cup", 129.220, 20.000, 129.220, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 132.220, 20.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "1/8", "Q1_8", 12.200, 5.500, "ctl_01", 129, "channel", 14.600, 80.000, 14.600, 19.000, 90.000, 5.500, 6.100, 14.600, 32.000, 14.600, 128.000, 14.600, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "5/32", "Q5_32", 12.400, 5.500, "ctl_01", 130, "channel", 34.160, 80.000, 34.160, 19.000, 90.000, 5.500, 6.200, 34.160, 32.000, 34.160, 128.000, 34.160, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "3/16", "Q3_16", 12.600, 5.500, "ctl_01", 131, "channel", 53.720, 80.000, 53.720, 19.000, 90.000, 5.500, 6.300, 53.720, 32.000, 53.720, 128.000, 53.720, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "7/32", "Q7_32", 12.800, 5.500, "ctl_01", 132, "channel", 73.280, 80.000, 73.280, 19.000, 90.000, 5.500, 6.400, 73.280, 32.000, 73.280, 128.000, 73.280, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "3mm", "Q3M", 13.000, 5.500, "ctl_01", 133, "channel", 92.840, 80.000, 92.840, 19.000, 90.000, 5.500, 6.200, 92.840, 32.000, 92.840, 128.000, 92.840, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "4mm", "Q4M", 13.200, 5.500, "ctl_01", 134, "channel", 112.400, 80.000, 112.400, 19.000, 90.000, 5.500, 6.400, 112.400, 32.000, 112.400, 128.000, 112.400, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "1/4", "long-ball hex", "5mm", "Q5M", 13.400, 5.500, "ctr_01", 135, "channel", 16.000, 80.000, 16.000, 19.000, 90.000, 5.500, 6.500, 16.000, 32.000, 16.000, 128.000, 16.000, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "1/4", "long-ball hex", "6mm", "Q6M", 13.800, 5.500, "ctr_01", 136, "channel", 35.000, 80.000, 35.000, 19.000, 90.000, 5.500, 6.700, 35.000, 32.000, 35.000, 128.000, 35.000, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "3/8", "long-ball hex", "1/8", "D1_8", 14.600, 6.500, "ctr_01", 137, "channel", 54.000, 80.000, 54.000, 19.000, 90.000, 5.500, 6.500, 54.000, 32.000, 54.000, 128.000, 54.000, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "3/8", "long-ball hex", "5/32", "D5_32", 15.000, 6.500, "ctr_01", 138, "channel", 73.000, 80.000, 73.000, 19.000, 90.000, 5.500, 6.600, 73.000, 32.000, 73.000, 128.000, 73.000, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "3/8", "long-ball hex", "3/16", "D3_16", 15.500, 6.500, "ctr_01", 139, "channel", 92.000, 80.000, 92.000, 19.000, 90.000, 5.500, 6.700, 92.000, 32.000, 92.000, 128.000, 92.000, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "3/8", "long-ball hex", "7/32", "D7_32", 16.000, 6.500, "ctr_01", 140, "channel", 111.000, 80.000, 111.000, 19.000, 90.000, 5.500, 6.800, 111.000, 32.000, 111.000, 128.000, 111.000, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "1/4", "D1_4", 12.400, 6.500, "cbl_01", 141, "channel", 14.600, 80.000, 14.600, 19.000, 90.000, 5.500, 6.800, 14.600, 32.000, 14.600, 128.000, 14.600, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "5/16", "D5_16", 12.600, 6.500, "cbl_01", 142, "channel", 30.900, 80.000, 30.900, 19.000, 90.000, 5.500, 7.000, 30.900, 32.000, 30.900, 128.000, 30.900, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "3/8", "D3_8", 13.000, 6.500, "cbl_01", 143, "channel", 47.200, 80.000, 47.200, 19.000, 90.000, 5.500, 7.200, 47.200, 32.000, 47.200, 128.000, 47.200, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "3mm", "D3M", 12.400, 6.500, "cbl_01", 144, "channel", 63.500, 80.000, 63.500, 19.000, 90.000, 5.500, 6.500, 63.500, 32.000, 63.500, 128.000, 63.500, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "4mm", "D4M", 12.600, 6.500, "cbl_01", 145, "channel", 79.800, 80.000, 79.800, 19.000, 90.000, 5.500, 6.600, 79.800, 32.000, 79.800, 128.000, 79.800, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "5mm", "D5M", 13.000, 6.500, "cbl_01", 146, "channel", 96.100, 80.000, 96.100, 19.000, 90.000, 5.500, 6.700, 96.100, 32.000, 96.100, 128.000, 96.100, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "6mm", "D6M", 13.200, 6.500, "cbl_01", 147, "channel", 112.400, 80.000, 112.400, 19.000, 90.000, 5.500, 6.800, 112.400, 32.000, 112.400, 128.000, 112.400, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "7mm", "D7M", 15.000, 6.500, "cbr_01", 148, "channel", 16.000, 80.000, 16.000, 19.000, 90.000, 5.500, 7.200, 16.000, 32.000, 16.000, 128.000, 16.000, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "8mm", "D8M", 15.200, 6.500, "cbr_01", 149, "channel", 35.000, 80.000, 35.000, 19.000, 90.000, 5.500, 7.400, 35.000, 32.000, 35.000, 128.000, 35.000, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "9mm", "D9M", 15.400, 6.500, "cbr_01", 150, "channel", 54.000, 80.000, 54.000, 19.000, 90.000, 5.500, 7.600, 54.000, 32.000, 54.000, 128.000, 54.000, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "10mm", "D10M", 15.600, 6.500, "cbr_01", 151, "channel", 73.000, 80.000, 73.000, 19.000, 90.000, 5.500, 7.800, 73.000, 32.000, 73.000, 128.000, 73.000, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "11mm", "D11M", 15.800, 6.500, "cbr_01", 152, "channel", 92.000, 80.000, 92.000, 19.000, 90.000, 5.500, 8.000, 92.000, 32.000, 92.000, 128.000, 92.000, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "12mm", "D12M", 16.000, 6.500, "cbr_01", 153, "channel", 111.000, 80.000, 111.000, 19.000, 90.000, 5.500, 8.200, 111.000, 32.000, 111.000, 128.000, 111.000, 146.000]
];

module_table = [
    ["left_top", 219.710, 197.870, 0.000, 134.870, 1],
    ["left_bottom", 219.710, 134.870, 0.000, 0.000, 2],
    ["center_top_left", 127.000, 166.370, 219.710, 166.370, 3],
    ["center_top_right", 127.000, 166.370, 346.710, 166.370, 4],
    ["center_bottom_left", 127.000, 166.370, 219.710, 0.000, 5],
    ["center_bottom_right", 127.000, 166.370, 346.710, 0.000, 6],
    ["right_top", 147.320, 157.400, 473.710, 175.260, 7],
    ["right_bottom", 147.320, 175.260, 473.710, 0.000, 8]
];

function selected_mode() = render_mode_index_override >= 0 ? render_mode_index_override : render_mode_index;
function count_kind(kind, i = 0) = i >= len(inventory) ? 0 : (inventory[i][F_KIND] == kind ? 1 : 0) + count_kind(kind, i + 1);
function module_w(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][1] : module_w(name, i + 1);
function module_d(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][2] : module_d(name, i + 1);
function module_ox(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][3] : module_ox(name, i + 1);
function module_oy(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][4] : module_oy(name, i + 1);

assert(len(inventory) == 153, str("Storage count must be 153, got ", len(inventory)));
assert(count_kind("cup") == 128, str("Circular pocket count must be 128, got ", count_kind("cup")));
assert(count_kind("channel") == 25, str("Long channel count must be 25, got ", count_kind("channel")));

module rounded_panel(w, d) {
    cube([w, d, base_thickness]);
}

module perimeter_lip(w, d) {
    translate([0, 0, base_thickness]) cube([w, lip_width, lip_height]);
    translate([0, d - lip_width, base_thickness]) cube([w, lip_width, lip_height]);
    translate([0, 0, base_thickness]) cube([lip_width, d, lip_height]);
    translate([w - lip_width, 0, base_thickness]) cube([lip_width, d, lip_height]);
}

module divider_ribs(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    if (module_name == "left_top") {
        for (y = [80, 120, 158]) translate([6, y, base_thickness]) cube([w - 12, rib_width, rib_height]);
    } else if (module_name == "left_bottom") {
        for (y = [36, 68, 100]) translate([6, y, base_thickness]) cube([w - 12, rib_width, rib_height]);
    } else if (module_name == "right_top") {
        for (y = [24, 45, 66, 87, 108, 129]) translate([5, y, base_thickness]) cube([w - 10, rib_width, rib_height]);
    } else if (module_name == "right_bottom") {
        for (y = [32, 60, 88, 116, 146]) translate([5, y, base_thickness]) cube([w - 10, rib_width, rib_height]);
    } else if (module_name == "center_top_left" || module_name == "center_top_right" || module_name == "center_bottom_left" || module_name == "center_bottom_right") {
        translate([4, 24, base_thickness]) cube([w - 8, rib_width, rib_height]);
        translate([4, 136, base_thickness]) cube([w - 8, rib_width, rib_height]);
    }
}

module socket_cup_cut(x, y, diameter, depth) {
    translate([x, y, base_thickness - depth - 0.02])
        cylinder(h = depth + 0.05, d = diameter);
    translate([x, y, base_thickness - pocket_chamfer])
        cylinder(h = pocket_chamfer + 0.08, d1 = diameter, d2 = diameter + 2 * pocket_chamfer);
}

module socket_cup(x, y, diameter, depth) {
    socket_cup_cut(x, y, diameter, depth);
}

module long_bit_channel_cut(x1, y1, x2, y2, width, depth) {
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

module long_bit_channel(x1, y1, x2, y2, width, depth) {
    long_bit_channel_cut(x1, y1, x2, y2, width, depth);
}

module label_text(txt, x, y, rot = 0, size = 5.5) {
    translate([x, y, base_thickness])
        rotate([0, 0, rot])
            linear_extrude(height = label_height)
                text(txt, size = size, font = label_font, halign = "center", valign = "center");
}

module module_cuts(module_name) {
    for (item = inventory) {
        if (item[F_MODULE] == module_name && item[F_KIND] == "cup") {
            socket_cup_cut(item[F_X], item[F_Y], item[F_POCKET_DIAMETER], item[F_POCKET_DEPTH]);
        }
        if (item[F_MODULE] == module_name && item[F_KIND] == "channel") {
            long_bit_channel_cut(item[F_CHANNEL_X1], item[F_CHANNEL_Y1], item[F_CHANNEL_X2], item[F_CHANNEL_Y2], item[F_CHANNEL_WIDTH], long_channel_depth);
            socket_cup_cut(item[F_END_X], item[F_END_Y], item[F_POCKET_DIAMETER], item[F_POCKET_DEPTH]);
        }
    }
}

module module_labels(module_name) {
    color([0.95, 0.08, 0.03])
        for (item = inventory) {
            if (item[F_MODULE] == module_name) {
                label_text(item[F_DISPLAY_LABEL], item[F_LABEL_X], item[F_LABEL_Y], item[F_LABEL_ROT], item[F_LABEL_SIZE]);
            }
        }
}

vertical_seam_segments = [
    [22, 54], [82, 114], [142, 174], [202, 234], [262, 294], [306, 326]
];
horizontal_seam_segments = [
    [22, 60], [88, 126], [154, 192], [238, 270], [300, 332], [362, 394], [424, 462], [496, 532], [562, 600]
];

function has_east_tongue(name) = name == "left_top" || name == "left_bottom" || name == "center_top_left" || name == "center_bottom_left" || name == "center_top_right" || name == "center_bottom_right";
function has_west_socket(name) = name == "center_top_left" || name == "center_bottom_left" || name == "center_top_right" || name == "center_bottom_right" || name == "right_top" || name == "right_bottom";
function has_north_tongue(name) = name == "left_bottom" || name == "center_bottom_left" || name == "center_bottom_right";
function has_south_socket(name) = name == "left_top" || name == "center_top_left" || name == "center_top_right";
function has_south_tongue(name) = name == "right_top";
function has_north_socket(name) = name == "right_bottom";

module seam_tongues(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    ox = module_ox(module_name);
    oy = module_oy(module_name);
    if (has_east_tongue(module_name)) {
        for (seg = vertical_seam_segments) {
            y0 = max(0, seg[0] - oy);
            y1 = min(d, seg[1] - oy);
            if (y1 - y0 > 10)
                translate([w, y0, 0]) cube([seam_lap_width, y1 - y0, base_thickness]);
        }
    }
    if (has_north_tongue(module_name)) {
        for (seg = horizontal_seam_segments) {
            x0 = max(0, seg[0] - ox);
            x1 = min(w, seg[1] - ox);
            if (x1 - x0 > 10)
                translate([x0, d, 0]) cube([x1 - x0, seam_lap_width, base_thickness]);
        }
    }
    if (has_south_tongue(module_name)) {
        for (seg = horizontal_seam_segments) {
            x0 = max(0, seg[0] - ox);
            x1 = min(w, seg[1] - ox);
            if (x1 - x0 > 10)
                translate([x0, -seam_lap_width, 0]) cube([x1 - x0, seam_lap_width, base_thickness]);
        }
    }
}

module seam_socket_cuts(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    ox = module_ox(module_name);
    oy = module_oy(module_name);
    if (has_west_socket(module_name)) {
        for (seg = vertical_seam_segments) {
            y0 = max(0, seg[0] - oy);
            y1 = min(d, seg[1] - oy);
            if (y1 - y0 > 10)
                translate([-0.02, y0 - seam_clearance, -0.02])
                    cube([seam_lap_width + seam_clearance + 0.04, y1 - y0 + 2 * seam_clearance, base_thickness + lip_height + 0.08]);
        }
    }
    if (has_south_socket(module_name)) {
        for (seg = horizontal_seam_segments) {
            x0 = max(0, seg[0] - ox);
            x1 = min(w, seg[1] - ox);
            if (x1 - x0 > 10)
                translate([x0 - seam_clearance, -0.02, -0.02])
                    cube([x1 - x0 + 2 * seam_clearance, seam_lap_width + seam_clearance + 0.04, base_thickness + lip_height + 0.08]);
        }
    }
    if (has_north_socket(module_name)) {
        for (seg = horizontal_seam_segments) {
            x0 = max(0, seg[0] - ox);
            x1 = min(w, seg[1] - ox);
            if (x1 - x0 > 10)
                translate([x0 - seam_clearance, d - seam_lap_width - seam_clearance, -0.02])
                    cube([x1 - x0 + 2 * seam_clearance, seam_lap_width + seam_clearance + 0.04, base_thickness + lip_height + 0.08]);
        }
    }
}

module module_body(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    assert(w + seam_lap_width <= safe_build_max && d + seam_lap_width <= safe_build_max, str("Build-volume fail with seam overlap: ", module_name));
    color([0.08, 0.20, 0.90])
        difference() {
            union() {
                rounded_panel(w, d);
                seam_tongues(module_name);
                perimeter_lip(w, d);
                divider_ribs(module_name);
            }
            seam_socket_cuts(module_name);
            module_cuts(module_name);
        }
}

module zone_grid(module_name) {
    module_body(module_name);
}

module puzzle_key_edge() {
    // Placeholder helper kept parametric for future underside keys; v03 avoids protruding seam geometry to preserve build-volume bounds.
    cube([0.01, 0.01, 0.01]);
}

module module_combined(module_name) {
    module_body(module_name);
    module_labels(module_name);
}

module module_left_top(part = "combined") {
    if (part == "body") module_body("left_top"); else if (part == "labels") module_labels("left_top"); else module_combined("left_top");
}
module module_left_bottom(part = "combined") {
    if (part == "body") module_body("left_bottom"); else if (part == "labels") module_labels("left_bottom"); else module_combined("left_bottom");
}
module module_center_top_left(part = "combined") {
    if (part == "body") module_body("center_top_left"); else if (part == "labels") module_labels("center_top_left"); else module_combined("center_top_left");
}
module module_center_top_right(part = "combined") {
    if (part == "body") module_body("center_top_right"); else if (part == "labels") module_labels("center_top_right"); else module_combined("center_top_right");
}
module module_center_bottom_left(part = "combined") {
    if (part == "body") module_body("center_bottom_left"); else if (part == "labels") module_labels("center_bottom_left"); else module_combined("center_bottom_left");
}
module module_center_bottom_right(part = "combined") {
    if (part == "body") module_body("center_bottom_right"); else if (part == "labels") module_labels("center_bottom_right"); else module_combined("center_bottom_right");
}
module module_right_top(part = "combined") {
    if (part == "body") module_body("right_top"); else if (part == "labels") module_labels("right_top"); else module_combined("right_top");
}
module module_right_bottom(part = "combined") {
    if (part == "body") module_body("right_bottom"); else if (part == "labels") module_labels("right_bottom"); else module_combined("right_bottom");
}

module fit_test_plate_body() {
    ft_w = 230.000;
    ft_d = 90.000;
    color([0.08, 0.20, 0.90])
        difference() {
            union() {
                rounded_panel(ft_w, ft_d);
                perimeter_lip(ft_w, ft_d);
            }
            socket_cup_cut(20, 62, 11.2, 5.5);
            socket_cup_cut(54, 62, 15.4, 5.5);
            socket_cup_cut(91, 62, 16.5, 6.5);
            socket_cup_cut(129, 62, 23.4, 6.5);
            socket_cup_cut(171, 62, 22.0, 7.5);
            socket_cup_cut(211, 62, 29.0, 7.5);
            long_bit_channel_cut(62, 18, 160, 18, 7.8, 4.0);
            socket_cup_cut(174, 18, 19.4, 6.5);
        }
}

module fit_test_plate_labels() {
    color([0.95, 0.08, 0.03]) {
        label_text("QSM", 20, 39, 0, 6.5);
        label_text("QLG", 54, 39, 0, 6.5);
        label_text("DSM", 91, 39, 0, 6.5);
        label_text("DLG", 129, 39, 0, 6.5);
        label_text("HSM", 171, 39, 0, 6.5);
        label_text("HLG", 211, 39, 0, 6.5);
        label_text("LONG", 111, 8, 0, 6.5);
    }
}

module full_reference_layout() {
    for (m = module_table) {
        translate([m[3], m[4], 0]) module_combined(m[0]);
    }
}

module reference_layout() {
    full_reference_layout();
}

mode = selected_mode();

if (mode == 1 || render_mode == "left_top_body") {
    module_left_top("body");
} else if (mode == 2 || render_mode == "left_top_labels") {
    module_left_top("labels");
} else if (mode == 3 || render_mode == "left_bottom_body") {
    module_left_bottom("body");
} else if (mode == 4 || render_mode == "left_bottom_labels") {
    module_left_bottom("labels");
} else if (mode == 5 || render_mode == "center_top_left_body") {
    module_center_top_left("body");
} else if (mode == 6 || render_mode == "center_top_left_labels") {
    module_center_top_left("labels");
} else if (mode == 7 || render_mode == "center_top_right_body") {
    module_center_top_right("body");
} else if (mode == 8 || render_mode == "center_top_right_labels") {
    module_center_top_right("labels");
} else if (mode == 9 || render_mode == "center_bottom_left_body") {
    module_center_bottom_left("body");
} else if (mode == 10 || render_mode == "center_bottom_left_labels") {
    module_center_bottom_left("labels");
} else if (mode == 11 || render_mode == "center_bottom_right_body") {
    module_center_bottom_right("body");
} else if (mode == 12 || render_mode == "center_bottom_right_labels") {
    module_center_bottom_right("labels");
} else if (mode == 13 || render_mode == "right_top_body") {
    module_right_top("body");
} else if (mode == 14 || render_mode == "right_top_labels") {
    module_right_top("labels");
} else if (mode == 15 || render_mode == "right_bottom_body") {
    module_right_bottom("body");
} else if (mode == 16 || render_mode == "right_bottom_labels") {
    module_right_bottom("labels");
} else if (mode == 17 || render_mode == "fit_test_plate_body") {
    fit_test_plate_body();
} else if (mode == 18 || render_mode == "fit_test_plate_labels") {
    fit_test_plate_labels();
} else {
    reference_layout();
}
