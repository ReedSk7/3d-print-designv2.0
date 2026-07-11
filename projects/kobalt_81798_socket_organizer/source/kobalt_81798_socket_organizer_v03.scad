// project_stem: kobalt_81798_socket_organizer
// version: v03
// task_mode: reference_based_reconstruction
// v03 corrective rebuild: separate aligned body and label STLs for color-ready Bambu Studio import.
// Units: millimeters. Z+ is up. OpenSCAD remains the source of truth.

$fn = 48;

project_version = "v03";
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

// Machine-readable v03 inventory. Every storage row has explicit diameter data.
inventory = [
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "5/8", "5_8", 22.500, 7.500, "lt_01", 1, "cup", 17.750, 178.000, 17.750, 162.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 17.750, 178.000],
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "11/16", "11_16", 23.300, 7.500, "lt_01", 2, "cup", 63.803, 178.000, 63.803, 162.500, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 63.803, 178.000],
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "3/4", "3_4", 24.000, 7.500, "lt_01", 3, "cup", 109.855, 178.000, 109.855, 162.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 178.000],
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "13/16", "13_16", 24.800, 7.500, "lt_01", 4, "cup", 155.907, 178.000, 155.907, 161.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 155.907, 178.000],
    ["left_top", "1/2DR 8-point shallow SAE", "1/2", "8-point shallow SAE", "7/8", "7_8", 25.500, 7.500, "lt_01", 5, "cup", 201.960, 178.000, 201.960, 161.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 201.960, 178.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "E18", "E18", 21.200, 7.500, "lt_02", 6, "cup", 17.400, 139.000, 17.400, 124.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 17.400, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "E20", "E20", 22.000, 7.500, "lt_02", 7, "cup", 48.218, 139.000, 48.218, 124.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 48.218, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "E22", "E22", 22.800, 7.500, "lt_02", 8, "cup", 79.037, 139.000, 79.037, 123.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 79.037, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "E24", "E24", 23.600, 7.500, "lt_02", 9, "cup", 109.855, 139.000, 109.855, 123.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "T55", "T55", 22.800, 7.500, "lt_02", 10, "cup", 140.673, 139.000, 140.673, 123.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 140.673, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "T60", "T60", 23.800, 7.500, "lt_02", 11, "cup", 171.492, 139.000, 171.492, 123.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 171.492, 139.000],
    ["left_top", "1/2DR external Torx and Torx", "1/2", "external/torx", "T70", "T70", 24.800, 7.500, "lt_02", 12, "cup", 202.310, 139.000, 202.310, 122.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 202.310, 139.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "5/16", "5_16", 20.800, 7.500, "lt_03", 13, "cup", 17.000, 100.000, 17.000, 85.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 17.000, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "3/8", "3_8", 21.200, 7.500, "lt_03", 14, "cup", 43.530, 100.000, 43.530, 85.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 43.530, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "7/16", "7_16", 21.800, 7.500, "lt_03", 15, "cup", 70.060, 100.000, 70.060, 85.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 70.060, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "1/2", "1_2", 22.300, 7.500, "lt_03", 16, "cup", 96.590, 100.000, 96.590, 85.000, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 96.590, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "9/16", "9_16", 22.800, 7.500, "lt_03", 17, "cup", 123.120, 100.000, 123.120, 84.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 123.120, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "5/8", "5_8", 23.200, 7.500, "lt_03", 18, "cup", 149.650, 100.000, 149.650, 84.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 149.650, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "11/16", "11_16", 23.600, 7.500, "lt_03", 19, "cup", 176.180, 100.000, 176.180, 84.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 176.180, 100.000],
    ["left_top", "1/2DR hex SAE bit sockets", "1/2", "hex SAE bit socket", "3/4", "3_4", 24.000, 7.500, "lt_03", 20, "cup", 202.710, 100.000, 202.710, 84.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 202.710, 100.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "6mm", "6M", 20.800, 7.500, "lt_04", 21, "cup", 16.750, 61.000, 16.750, 46.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 16.750, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "7mm", "7M", 21.200, 7.500, "lt_04", 22, "cup", 47.785, 61.000, 47.785, 46.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 47.785, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "8mm", "8M", 21.600, 7.500, "lt_04", 23, "cup", 78.820, 61.000, 78.820, 46.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 78.820, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "9mm", "9M", 22.000, 7.500, "lt_04", 24, "cup", 109.855, 61.000, 109.855, 46.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "10mm", "10M", 22.500, 7.500, "lt_04", 25, "cup", 140.890, 61.000, 140.890, 45.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 140.890, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "11mm", "11M", 23.000, 7.500, "lt_04", 26, "cup", 171.925, 61.000, 171.925, 45.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 171.925, 61.000],
    ["left_top", "1/2DR hex metric small", "1/2", "hex metric bit socket", "12mm", "12M", 23.500, 7.500, "lt_04", 27, "cup", 202.960, 61.000, 202.960, 45.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 202.960, 61.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "13mm", "13M", 22.800, 7.500, "lt_05", 28, "cup", 17.600, 22.000, 17.600, 37.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 17.600, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "14mm", "14M", 23.200, 7.500, "lt_05", 29, "cup", 48.352, 22.000, 48.352, 37.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 48.352, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "15mm", "15M", 23.600, 7.500, "lt_05", 30, "cup", 79.103, 22.000, 79.103, 37.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 79.103, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "16mm", "16M", 24.000, 7.500, "lt_05", 31, "cup", 109.855, 22.000, 109.855, 37.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "17mm", "17M", 24.400, 7.500, "lt_05", 32, "cup", 140.607, 22.000, 140.607, 38.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 140.607, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "18mm", "18M", 24.800, 7.500, "lt_05", 33, "cup", 171.358, 22.000, 171.358, 38.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 171.358, 22.000],
    ["left_top", "1/2DR hex metric large", "1/2", "hex metric bit socket", "19mm", "19M", 25.200, 7.500, "lt_05", 34, "cup", 202.110, 22.000, 202.110, 38.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 202.110, 22.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "1/4", "1_4", 16.000, 6.500, "lb_01", 35, "cup", 15.000, 116.000, 15.000, 104.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 15.000, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "5/16", "5_16", 16.800, 6.500, "lb_01", 36, "cup", 52.942, 116.000, 52.942, 103.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 52.942, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "3/8", "3_8", 17.600, 6.500, "lb_01", 37, "cup", 90.884, 116.000, 90.884, 103.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 90.884, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "7/16", "7_16", 18.400, 6.500, "lb_01", 38, "cup", 128.826, 116.000, 128.826, 102.950, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 128.826, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "1/2", "1_2", 19.200, 6.500, "lb_01", 39, "cup", 166.768, 116.000, 166.768, 102.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 166.768, 116.000],
    ["left_bottom", "3/8DR 8-point shallow SAE", "3/8", "8-point shallow SAE", "9/16", "9_16", 20.000, 6.500, "lb_01", 40, "cup", 204.710, 116.000, 204.710, 102.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 204.710, 116.000],
    ["left_bottom", "3/8DR external Torx", "3/8", "external Torx", "E10", "E10", 15.800, 6.500, "lb_02", 41, "cup", 14.700, 84.000, 14.700, 72.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 14.700, 84.000],
    ["left_bottom", "3/8DR external Torx", "3/8", "external Torx", "E12", "E12", 17.000, 6.500, "lb_02", 42, "cup", 78.137, 84.000, 78.137, 71.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 78.137, 84.000],
    ["left_bottom", "3/8DR external Torx", "3/8", "external Torx", "E14", "E14", 18.200, 6.500, "lb_02", 43, "cup", 141.573, 84.000, 141.573, 71.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 141.573, 84.000],
    ["left_bottom", "3/8DR external Torx", "3/8", "external Torx", "E16", "E16", 19.400, 6.500, "lb_02", 44, "cup", 205.010, 84.000, 205.010, 70.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 205.010, 84.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "1/8", "1_8", 15.500, 6.500, "lb_03", 45, "cup", 14.800, 52.000, 14.800, 40.400, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 14.800, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "5/32", "5_32", 16.000, 6.500, "lb_03", 46, "cup", 46.485, 52.000, 46.485, 40.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 46.485, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "3/16", "3_16", 16.600, 6.500, "lb_03", 47, "cup", 78.170, 52.000, 78.170, 39.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 78.170, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "7/32", "7_32", 17.200, 6.500, "lb_03", 48, "cup", 109.855, 52.000, 109.855, 39.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 109.855, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "1/4", "1_4", 18.000, 6.500, "lb_03", 49, "cup", 141.540, 52.000, 141.540, 39.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 141.540, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "5/16", "5_16", 18.800, 6.500, "lb_03", 50, "cup", 173.225, 52.000, 173.225, 38.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 173.225, 52.000],
    ["left_bottom", "3/8DR hex SAE bit sockets", "3/8", "hex SAE bit socket", "3/8", "3_8", 19.600, 6.500, "lb_03", 51, "cup", 204.910, 52.000, 204.910, 38.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 204.910, 52.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "3mm", "3M", 14.800, 6.500, "lb_04", 52, "cup", 14.000, 20.000, 14.000, 31.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 14.000, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "4mm", "4M", 15.200, 6.500, "lb_04", 53, "cup", 35.301, 20.000, 35.301, 31.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 35.301, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "5mm", "5M", 15.600, 6.500, "lb_04", 54, "cup", 56.602, 20.000, 56.602, 31.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 56.602, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "6mm", "6M", 16.000, 6.500, "lb_04", 55, "cup", 77.903, 20.000, 77.903, 31.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 77.903, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "7mm", "7M", 16.400, 6.500, "lb_04", 56, "cup", 99.204, 20.000, 99.204, 32.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 99.204, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "8mm", "8M", 16.800, 6.500, "lb_04", 57, "cup", 120.506, 20.000, 120.506, 32.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 120.506, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "9mm", "9M", 17.200, 6.500, "lb_04", 58, "cup", 141.807, 20.000, 141.807, 32.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 141.807, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "10mm", "10M", 17.500, 6.500, "lb_04", 59, "cup", 163.108, 20.000, 163.108, 32.600, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 163.108, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "11mm", "11M", 17.800, 6.500, "lb_04", 60, "cup", 184.409, 20.000, 184.409, 32.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 184.409, 20.000],
    ["left_bottom", "3/8DR hex metric bit sockets", "3/8", "hex metric bit socket", "12mm", "12M", 18.000, 6.500, "lb_04", 61, "cup", 205.710, 20.000, 205.710, 32.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 205.710, 20.000],
    ["right_top", "1/4DR 8-point shallow SAE", "1/4", "8-point shallow SAE", "1/4", "1_4", 13.200, 5.500, "rt_01", 62, "cup", 12.700, 140.000, 12.700, 150.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.700, 140.000],
    ["right_top", "1/4DR 8-point shallow SAE", "1/4", "8-point shallow SAE", "5/16", "5_16", 14.300, 5.500, "rt_01", 63, "cup", 73.660, 140.000, 73.660, 151.000, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 140.000],
    ["right_top", "1/4DR 8-point shallow SAE", "1/4", "8-point shallow SAE", "3/8", "3_8", 15.400, 5.500, "rt_01", 64, "cup", 134.620, 140.000, 134.620, 151.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 134.620, 140.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E4", "E4", 11.600, 5.500, "rt_02", 65, "cup", 12.000, 119.000, 12.000, 109.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.000, 119.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E5", "E5", 12.200, 5.500, "rt_02", 66, "cup", 42.830, 119.000, 42.830, 109.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 42.830, 119.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E6", "E6", 12.800, 5.500, "rt_02", 67, "cup", 73.660, 119.000, 73.660, 108.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 119.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E7", "E7", 13.400, 5.500, "rt_02", 68, "cup", 104.490, 119.000, 104.490, 108.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 104.490, 119.000],
    ["right_top", "1/4DR external Torx", "1/4", "external Torx", "E8", "E8", 14.000, 5.500, "rt_02", 69, "cup", 135.320, 119.000, 135.320, 108.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.320, 119.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "1/16", "1_16", 10.800, 5.500, "rt_03", 70, "cup", 11.500, 98.000, 11.500, 88.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 11.500, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "5/64", "5_64", 11.200, 5.500, "rt_03", 71, "cup", 42.580, 98.000, 42.580, 88.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 42.580, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "3/32", "3_32", 11.800, 5.500, "rt_03", 72, "cup", 73.660, 98.000, 73.660, 88.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "7/64", "7_64", 12.400, 5.500, "rt_03", 73, "cup", 104.740, 98.000, 104.740, 87.950, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 104.740, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets small", "1/4", "hex SAE bit socket", "1/8", "1_8", 13.000, 5.500, "rt_03", 74, "cup", 135.820, 98.000, 135.820, 87.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.820, 98.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "9/64", "9_64", 13.200, 5.500, "rt_04", 75, "cup", 12.500, 77.000, 12.500, 66.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 12.500, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "5/32", "5_32", 13.600, 5.500, "rt_04", 76, "cup", 43.080, 77.000, 43.080, 66.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 43.080, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "3/16", "3_16", 14.000, 5.500, "rt_04", 77, "cup", 73.660, 77.000, 73.660, 66.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "7/32", "7_32", 14.500, 5.500, "rt_04", 78, "cup", 104.240, 77.000, 104.240, 66.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 104.240, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "1/4", "1_4", 15.000, 5.500, "rt_04", 79, "cup", 134.820, 77.000, 134.820, 66.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 134.820, 77.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "2mm", "2M", 11.000, 5.500, "rt_05", 80, "cup", 12.300, 56.000, 12.300, 46.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.300, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "2.5mm", "2_5M", 11.600, 5.500, "rt_05", 81, "cup", 36.844, 56.000, 36.844, 46.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 36.844, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "3mm", "3M", 12.200, 5.500, "rt_05", 82, "cup", 61.388, 56.000, 61.388, 46.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 61.388, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "4mm", "4M", 13.000, 5.500, "rt_05", 83, "cup", 85.932, 56.000, 85.932, 45.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 85.932, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "5mm", "5M", 13.800, 5.500, "rt_05", 84, "cup", 110.476, 56.000, 110.476, 45.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 110.476, 56.000],
    ["right_top", "1/4DR hex metric bit sockets", "1/4", "hex metric bit socket", "6mm", "6M", 14.600, 5.500, "rt_05", 85, "cup", 135.020, 56.000, 135.020, 44.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.020, 56.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "7/32 slot", "7_32", 13.800, 5.500, "rt_06", 86, "cup", 12.300, 35.000, 12.300, 24.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.300, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "1/4 slot", "1_4", 14.600, 5.500, "rt_06", 87, "cup", 36.844, 35.000, 36.844, 23.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 36.844, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "PH3", "PH3", 14.200, 5.500, "rt_06", 88, "cup", 61.388, 35.000, 61.388, 24.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 61.388, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "S1", "S1", 12.800, 5.500, "rt_06", 89, "cup", 85.932, 35.000, 85.932, 24.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 85.932, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "S2", "S2", 13.400, 5.500, "rt_06", 90, "cup", 110.476, 35.000, 110.476, 24.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 110.476, 35.000],
    ["right_top", "1/4DR screwdriver bit sockets", "1/4", "screwdriver bit socket", "PZ1", "PZ1", 13.800, 5.500, "rt_06", 91, "cup", 135.020, 35.000, 135.020, 24.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.020, 35.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T8", "T8", 11.200, 5.500, "rt_07", 92, "cup", 12.200, 14.000, 12.200, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 12.200, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T9", "T9", 11.600, 5.500, "rt_07", 93, "cup", 29.760, 14.000, 29.760, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 29.760, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T10", "T10", 12.000, 5.500, "rt_07", 94, "cup", 47.320, 14.000, 47.320, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 47.320, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T15", "T15", 12.600, 5.500, "rt_07", 95, "cup", 64.880, 14.000, 64.880, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 64.880, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T20", "T20", 13.200, 5.500, "rt_07", 96, "cup", 82.440, 14.000, 82.440, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 82.440, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T25", "T25", 13.800, 5.500, "rt_07", 97, "cup", 100.000, 14.000, 100.000, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 100.000, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T27", "T27", 14.100, 5.500, "rt_07", 98, "cup", 117.560, 14.000, 117.560, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 117.560, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T30", "T30", 14.400, 5.500, "rt_07", 99, "cup", 135.120, 14.000, 135.120, 4.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 135.120, 14.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T20", "T20", 17.000, 6.500, "rb_01", 100, "cup", 15.250, 160.000, 15.250, 146.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 15.250, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T25", "T25", 17.800, 6.500, "rb_01", 101, "cup", 44.455, 160.000, 44.455, 146.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 44.455, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T27", "T27", 18.500, 6.500, "rb_01", 102, "cup", 73.660, 160.000, 73.660, 146.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T30", "T30", 19.200, 6.500, "rb_01", 103, "cup", 102.865, 160.000, 102.865, 146.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 102.865, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T40", "T40", 20.500, 6.500, "rb_01", 104, "cup", 132.070, 160.000, 132.070, 146.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 132.070, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T45", "T45", 21.200, 6.500, "rb_02", 105, "cup", 16.600, 130.000, 16.600, 115.400, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 16.600, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T47", "T47", 21.800, 6.500, "rb_02", 106, "cup", 54.640, 130.000, 54.640, 115.400, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 54.640, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T50", "T50", 22.500, 6.500, "rb_02", 107, "cup", 92.680, 130.000, 92.680, 115.400, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 92.680, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T55", "T55", 23.200, 6.500, "rb_02", 108, "cup", 130.720, 130.000, 130.720, 115.400, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 130.720, 130.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT15", "TT15", 16.800, 6.500, "rb_03", 109, "cup", 14.600, 103.000, 14.600, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 14.600, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT20", "TT20", 17.400, 6.500, "rb_03", 110, "cup", 44.130, 103.000, 44.130, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 44.130, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT25", "TT25", 18.000, 6.500, "rb_03", 111, "cup", 73.660, 103.000, 73.660, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT27", "TT27", 18.600, 6.500, "rb_03", 112, "cup", 103.190, 103.000, 103.190, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 103.190, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT30", "TT30", 19.200, 6.500, "rb_03", 113, "cup", 132.720, 103.000, 132.720, 89.300, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 132.720, 103.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT40", "TT40", 20.400, 6.500, "rb_04", 114, "cup", 16.700, 75.000, 16.700, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 16.700, 75.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT45", "TT45", 21.000, 6.500, "rb_04", 115, "cup", 45.180, 75.000, 45.180, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 45.180, 75.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT50", "TT50", 21.800, 6.500, "rb_04", 116, "cup", 73.660, 75.000, 73.660, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 75.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT55", "TT55", 22.600, 6.500, "rb_04", 117, "cup", 102.140, 75.000, 102.140, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 102.140, 75.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT60", "TT60", 23.400, 6.500, "rb_04", 118, "cup", 130.620, 75.000, 130.620, 60.500, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 130.620, 75.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "9/32 flat", "9_32", 18.600, 6.500, "rb_05", 119, "cup", 15.250, 47.000, 15.250, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 15.250, 47.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "3/8 flat", "3_8", 20.500, 6.500, "rb_05", 120, "cup", 44.455, 47.000, 44.455, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 44.455, 47.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "4mm flat", "4M", 17.200, 6.500, "rb_05", 121, "cup", 73.660, 47.000, 73.660, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 47.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "5mm flat", "5M", 18.400, 6.500, "rb_05", 122, "cup", 102.865, 47.000, 102.865, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 102.865, 47.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "6mm flat", "6M", 19.600, 6.500, "rb_05", 123, "cup", 132.070, 47.000, 132.070, 33.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 132.070, 47.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH1", "PH1", 17.800, 6.500, "rb_06", 124, "cup", 15.100, 20.000, 15.100, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 15.100, 20.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH2", "PH2", 18.800, 6.500, "rb_06", 125, "cup", 44.380, 20.000, 44.380, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 44.380, 20.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH3", "PH3", 19.800, 6.500, "rb_06", 126, "cup", 73.660, 20.000, 73.660, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 20.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PZ2", "PZ2", 19.200, 6.500, "rb_06", 127, "cup", 102.940, 20.000, 102.940, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 102.940, 20.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PZ3", "PZ3", 20.200, 6.500, "rb_06", 128, "cup", 132.220, 20.000, 132.220, 5.000, 0.000, 5.000, 0.000, 0.000, 0.000, 0.000, 0.000, 132.220, 20.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "1/8", "Q1_8", 12.400, 5.500, "ctl_01", 129, "channel", 11.750, 80.000, 11.750, 16.000, 90.000, 5.500, 6.100, 11.750, 32.000, 11.750, 128.000, 11.750, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "5/32", "Q5_32", 12.800, 5.500, "ctl_01", 130, "channel", 32.450, 80.000, 32.450, 16.000, 90.000, 5.500, 6.200, 32.450, 32.000, 32.450, 128.000, 32.450, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "3/16", "Q3_16", 13.100, 5.500, "ctl_01", 131, "channel", 53.150, 80.000, 53.150, 16.000, 90.000, 5.500, 6.300, 53.150, 32.000, 53.150, 128.000, 53.150, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "7/32", "Q7_32", 13.500, 5.500, "ctl_01", 132, "channel", 73.850, 80.000, 73.850, 16.000, 90.000, 5.500, 6.400, 73.850, 32.000, 73.850, 128.000, 73.850, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "3mm", "Q3M", 13.000, 5.500, "ctl_01", 133, "channel", 94.550, 80.000, 94.550, 16.000, 90.000, 5.500, 6.200, 94.550, 32.000, 94.550, 128.000, 94.550, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric upper left", "1/4", "long-ball hex", "4mm", "Q4M", 13.400, 5.500, "ctl_01", 134, "channel", 115.250, 80.000, 115.250, 16.000, 90.000, 5.500, 6.400, 115.250, 32.000, 115.250, 128.000, 115.250, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "1/4", "long-ball hex", "5mm", "Q5M", 13.800, 5.500, "ctr_01", 135, "channel", 13.500, 80.000, 13.500, 16.000, 90.000, 5.500, 6.500, 13.500, 32.000, 13.500, 128.000, 13.500, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "1/4", "long-ball hex", "6mm", "Q6M", 14.200, 5.500, "ctr_01", 136, "channel", 33.500, 80.000, 33.500, 16.000, 90.000, 5.500, 6.700, 33.500, 32.000, 33.500, 128.000, 33.500, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "3/8", "long-ball hex", "1/8", "D1_8", 15.200, 6.500, "ctr_01", 137, "channel", 53.500, 80.000, 53.500, 16.000, 90.000, 5.500, 6.500, 53.500, 32.000, 53.500, 128.000, 53.500, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "3/8", "long-ball hex", "5/32", "D5_32", 15.800, 6.500, "ctr_01", 138, "channel", 73.500, 80.000, 73.500, 16.000, 90.000, 5.500, 6.600, 73.500, 32.000, 73.500, 128.000, 73.500, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "3/8", "long-ball hex", "3/16", "D3_16", 16.400, 6.500, "ctr_01", 139, "channel", 93.500, 80.000, 93.500, 16.000, 90.000, 5.500, 6.700, 93.500, 32.000, 93.500, 128.000, 93.500, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex upper transition", "3/8", "long-ball hex", "7/32", "D7_32", 17.000, 6.500, "ctr_01", 140, "channel", 113.500, 80.000, 113.500, 16.000, 90.000, 5.500, 6.800, 113.500, 32.000, 113.500, 128.000, 113.500, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "1/4", "D1_4", 13.600, 6.500, "cbl_01", 141, "channel", 12.100, 80.000, 12.100, 16.000, 90.000, 5.500, 6.800, 12.100, 32.000, 12.100, 128.000, 12.100, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "5/16", "D5_16", 13.800, 6.500, "cbl_01", 142, "channel", 29.233, 80.000, 29.233, 16.000, 90.000, 5.500, 7.000, 29.233, 32.000, 29.233, 128.000, 29.233, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "3/8", "D3_8", 14.200, 6.500, "cbl_01", 143, "channel", 46.367, 80.000, 46.367, 16.000, 90.000, 5.500, 7.200, 46.367, 32.000, 46.367, 128.000, 46.367, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "3mm", "D3M", 13.000, 6.500, "cbl_01", 144, "channel", 63.500, 80.000, 63.500, 16.000, 90.000, 5.500, 6.500, 63.500, 32.000, 63.500, 128.000, 63.500, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "4mm", "D4M", 13.200, 6.500, "cbl_01", 145, "channel", 80.633, 80.000, 80.633, 16.000, 90.000, 5.500, 6.600, 80.633, 32.000, 80.633, 128.000, 80.633, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "5mm", "D5M", 13.500, 6.500, "cbl_01", 146, "channel", 97.767, 80.000, 97.767, 16.000, 90.000, 5.500, 6.700, 97.767, 32.000, 97.767, 128.000, 97.767, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric lower left", "3/8", "long-ball hex", "6mm", "D6M", 13.800, 6.500, "cbl_01", 147, "channel", 114.900, 80.000, 114.900, 16.000, 90.000, 5.500, 6.800, 114.900, 32.000, 114.900, 128.000, 114.900, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "7mm", "D7M", 16.200, 6.500, "cbr_01", 148, "channel", 13.600, 80.000, 13.600, 16.000, 90.000, 5.500, 7.200, 13.600, 32.000, 13.600, 128.000, 13.600, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "8mm", "D8M", 16.400, 6.500, "cbr_01", 149, "channel", 33.560, 80.000, 33.560, 16.000, 90.000, 5.500, 7.400, 33.560, 32.000, 33.560, 128.000, 33.560, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "9mm", "D9M", 16.600, 6.500, "cbr_01", 150, "channel", 53.520, 80.000, 53.520, 16.000, 90.000, 5.500, 7.600, 53.520, 32.000, 53.520, 128.000, 53.520, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "10mm", "D10M", 16.800, 6.500, "cbr_01", 151, "channel", 73.480, 80.000, 73.480, 16.000, 90.000, 5.500, 7.800, 73.480, 32.000, 73.480, 128.000, 73.480, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "11mm", "D11M", 17.000, 6.500, "cbr_01", 152, "channel", 93.440, 80.000, 93.440, 16.000, 90.000, 5.500, 8.000, 93.440, 32.000, 93.440, 128.000, 93.440, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric lower right", "3/8", "long-ball hex", "12mm", "D12M", 17.200, 6.500, "cbr_01", 153, "channel", 113.400, 80.000, 113.400, 16.000, 90.000, 5.500, 8.200, 113.400, 32.000, 113.400, 128.000, 113.400, 146.000]
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

module module_body(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    assert(w <= safe_build_max && d <= safe_build_max, str("Build-volume fail before top detail: ", module_name));
    color([0.08, 0.20, 0.90])
        difference() {
            union() {
                rounded_panel(w, d);
                perimeter_lip(w, d);
                divider_ribs(module_name);
            }
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
