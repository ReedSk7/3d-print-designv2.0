// project_stem: kobalt_81798_socket_organizer
// version: v02
// task_mode: reference_based_reconstruction
// Corrective rebuild: v01 was rejected for near-uniform pockets and unreadable labels.
// Units: millimeters. Z+ is up. OpenSCAD remains the source of truth.

$fn = 40;

project_version = "v02";
render_mode = "reference_layout";
render_mode_index = 0; // 0 reference_layout, 1 left_top, 2 left_bottom, 3 center_top_left, 4 center_top_right, 5 center_bottom_left, 6 center_bottom_right, 7 right_top, 8 right_bottom, 9 fit_test_plate

overall_width = 621.030;
overall_depth = 332.740;
base_thickness = 12.700;
safe_build_max = 245.000;
printer_build = [256, 256, 256];
min_floor = 2.5;
min_web = 2.5;
edge_margin = 5.0;
pocket_chamfer = 1.0;
label_height = 0.600;
label_font = "Liberation Sans:style=Bold";
label_size_min = 5.5;
long_channel_depth = 4.0;

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

// Machine-readable v02 inventory. Every storage row has explicit diameter data.
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
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "9/64", "9_64", 13.200, 5.500, "rt_04", 75, "cup", 12.500, 77.000, 12.500, 87.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.500, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "5/32", "5_32", 13.600, 5.500, "rt_04", 76, "cup", 43.080, 77.000, 43.080, 87.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 43.080, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "3/16", "3_16", 14.000, 5.500, "rt_04", 77, "cup", 73.660, 77.000, 73.660, 87.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "7/32", "7_32", 14.500, 5.500, "rt_04", 78, "cup", 104.240, 77.000, 104.240, 88.100, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 104.240, 77.000],
    ["right_top", "1/4DR hex SAE bit sockets large", "1/4", "hex SAE bit socket", "1/4", "1_4", 15.000, 5.500, "rt_04", 79, "cup", 134.820, 77.000, 134.820, 88.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 134.820, 77.000],
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
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T8", "T8", 11.200, 5.500, "rt_07", 92, "cup", 12.200, 14.000, 12.200, 4.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 12.200, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T9", "T9", 11.600, 5.500, "rt_07", 93, "cup", 29.760, 14.000, 29.760, 4.350, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 29.760, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T10", "T10", 12.000, 5.500, "rt_07", 94, "cup", 47.320, 14.000, 47.320, 4.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 47.320, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T15", "T15", 12.600, 5.500, "rt_07", 95, "cup", 64.880, 14.000, 64.880, 3.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 64.880, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T20", "T20", 13.200, 5.500, "rt_07", 96, "cup", 82.440, 14.000, 82.440, 3.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 82.440, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T25", "T25", 13.800, 5.500, "rt_07", 97, "cup", 100.000, 14.000, 100.000, 3.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 100.000, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T27", "T27", 14.100, 5.500, "rt_07", 98, "cup", 117.560, 14.000, 117.560, 3.100, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 117.560, 14.000],
    ["right_top", "1/4DR Torx bit sockets", "1/4", "Torx bit socket", "T30", "T30", 14.400, 5.500, "rt_07", 99, "cup", 135.120, 14.000, 135.120, 2.950, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 135.120, 14.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T20", "T20", 17.000, 6.500, "rb_01", 100, "cup", 15.250, 160.000, 15.250, 147.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 15.250, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T25", "T25", 17.800, 6.500, "rb_01", 101, "cup", 44.455, 160.000, 44.455, 147.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 44.455, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T27", "T27", 18.500, 6.500, "rb_01", 102, "cup", 73.660, 160.000, 73.660, 146.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T30", "T30", 19.200, 6.500, "rb_01", 103, "cup", 102.865, 160.000, 102.865, 146.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 102.865, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets small", "3/8", "Torx bit socket", "T40", "T40", 20.500, 6.500, "rb_01", 104, "cup", 132.070, 160.000, 132.070, 145.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 132.070, 160.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T45", "T45", 21.200, 6.500, "rb_02", 105, "cup", 16.600, 130.000, 16.600, 115.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 16.600, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T47", "T47", 21.800, 6.500, "rb_02", 106, "cup", 54.640, 130.000, 54.640, 115.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 54.640, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T50", "T50", 22.500, 6.500, "rb_02", 107, "cup", 92.680, 130.000, 92.680, 114.900, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 92.680, 130.000],
    ["right_bottom", "3/8DR Torx bit sockets large", "3/8", "Torx bit socket", "T55", "T55", 23.200, 6.500, "rb_02", 108, "cup", 130.720, 130.000, 130.720, 114.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 130.720, 130.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT15", "TT15", 16.800, 6.500, "rb_03", 109, "cup", 14.600, 100.000, 14.600, 87.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 14.600, 100.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT20", "TT20", 17.400, 6.500, "rb_03", 110, "cup", 44.130, 100.000, 44.130, 87.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 44.130, 100.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT25", "TT25", 18.000, 6.500, "rb_03", 111, "cup", 73.660, 100.000, 73.660, 87.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 100.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT27", "TT27", 18.600, 6.500, "rb_03", 112, "cup", 103.190, 100.000, 103.190, 86.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 103.190, 100.000],
    ["right_bottom", "3/8DR tamper-proof Torx small", "3/8", "tamper-proof Torx bit socket", "TT30", "TT30", 19.200, 6.500, "rb_03", 113, "cup", 132.720, 100.000, 132.720, 86.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 132.720, 100.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT40", "TT40", 20.400, 6.500, "rb_04", 114, "cup", 16.700, 70.000, 16.700, 55.950, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 16.700, 70.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT45", "TT45", 21.000, 6.500, "rb_04", 115, "cup", 45.180, 70.000, 45.180, 55.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 45.180, 70.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT50", "TT50", 21.800, 6.500, "rb_04", 116, "cup", 73.660, 70.000, 73.660, 55.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 70.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT55", "TT55", 22.600, 6.500, "rb_04", 117, "cup", 102.140, 70.000, 102.140, 54.850, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 102.140, 70.000],
    ["right_bottom", "3/8DR tamper-proof Torx large", "3/8", "tamper-proof Torx bit socket", "TT60", "TT60", 23.400, 6.500, "rb_04", 118, "cup", 130.620, 70.000, 130.620, 54.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 130.620, 70.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "9/32 flat", "9_32", 18.600, 6.500, "rb_05", 119, "cup", 15.250, 40.000, 15.250, 53.150, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 15.250, 40.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "3/8 flat", "3_8", 20.500, 6.500, "rb_05", 120, "cup", 44.455, 40.000, 44.455, 54.100, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 44.455, 40.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "4mm flat", "4M", 17.200, 6.500, "rb_05", 121, "cup", 73.660, 40.000, 73.660, 52.450, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 40.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "5mm flat", "5M", 18.400, 6.500, "rb_05", 122, "cup", 102.865, 40.000, 102.865, 53.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 102.865, 40.000],
    ["right_bottom", "3/8DR flat screwdriver bit sockets", "3/8", "flat screwdriver bit socket", "6mm flat", "6M", 19.600, 6.500, "rb_05", 123, "cup", 132.070, 40.000, 132.070, 53.650, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 132.070, 40.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH1", "PH1", 17.800, 6.500, "rb_06", 124, "cup", 15.100, 18.000, 15.100, 5.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 15.100, 18.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH2", "PH2", 18.800, 6.500, "rb_06", 125, "cup", 44.380, 18.000, 44.380, 4.750, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 44.380, 18.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PH3", "PH3", 19.800, 6.500, "rb_06", 126, "cup", 73.660, 18.000, 73.660, 4.250, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 73.660, 18.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PZ2", "PZ2", 19.200, 6.500, "rb_06", 127, "cup", 102.940, 18.000, 102.940, 4.550, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 102.940, 18.000],
    ["right_bottom", "3/8DR Phillips and Pozidriv sockets", "3/8", "Phillips/Pozidriv bit socket", "PZ3", "PZ3", 20.200, 6.500, "rb_06", 128, "cup", 132.220, 18.000, 132.220, 4.050, 0.000, 5.500, 0.000, 0.000, 0.000, 0.000, 0.000, 132.220, 18.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric", "1/4", "long-ball hex", "1/8", "Q1_8", 12.400, 5.500, "ctl_01", 129, "channel", 11.900, 82.000, 11.900, 17.000, 90.000, 5.500, 6.700, 11.900, 34.000, 11.900, 130.000, 11.900, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric", "1/4", "long-ball hex", "5/32", "Q5_32", 12.800, 5.500, "ctl_01", 130, "channel", 29.100, 82.000, 29.100, 17.000, 90.000, 5.500, 6.800, 29.100, 34.000, 29.100, 130.000, 29.100, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric", "1/4", "long-ball hex", "3/16", "Q3_16", 13.100, 5.500, "ctl_01", 131, "channel", 46.300, 82.000, 46.300, 17.000, 90.000, 5.500, 6.900, 46.300, 34.000, 46.300, 130.000, 46.300, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric", "1/4", "long-ball hex", "7/32", "Q7_32", 13.500, 5.500, "ctl_01", 132, "channel", 63.500, 82.000, 63.500, 17.000, 90.000, 5.500, 7.000, 63.500, 34.000, 63.500, 130.000, 63.500, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric", "1/4", "long-ball hex", "3mm", "Q3M", 13.000, 5.500, "ctl_01", 133, "channel", 80.700, 82.000, 80.700, 17.000, 90.000, 5.500, 6.800, 80.700, 34.000, 80.700, 130.000, 80.700, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric", "1/4", "long-ball hex", "4mm", "Q4M", 13.400, 5.500, "ctl_01", 134, "channel", 97.900, 82.000, 97.900, 17.000, 90.000, 5.500, 7.000, 97.900, 34.000, 97.900, 130.000, 97.900, 146.000],
    ["center_top_left", "1/4DR long-ball hex SAE and metric", "1/4", "long-ball hex", "5mm", "Q5M", 13.800, 5.500, "ctl_01", 135, "channel", 115.100, 82.000, 115.100, 17.000, 90.000, 5.500, 7.200, 115.100, 34.000, 115.100, 130.000, 115.100, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex transition", "1/4", "long-ball hex", "6mm", "Q6M", 14.200, 5.500, "ctr_01", 136, "channel", 13.650, 82.000, 13.650, 17.000, 90.000, 5.500, 7.300, 13.650, 34.000, 13.650, 130.000, 13.650, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex transition", "3/8", "long-ball hex", "1/8", "D1_8", 15.200, 6.500, "ctr_01", 137, "channel", 33.590, 82.000, 33.590, 17.000, 90.000, 5.500, 7.000, 33.590, 34.000, 33.590, 130.000, 33.590, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex transition", "3/8", "long-ball hex", "5/32", "D5_32", 15.800, 6.500, "ctr_01", 138, "channel", 53.530, 82.000, 53.530, 17.000, 90.000, 5.500, 7.100, 53.530, 34.000, 53.530, 130.000, 53.530, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex transition", "3/8", "long-ball hex", "3/16", "D3_16", 16.400, 6.500, "ctr_01", 139, "channel", 73.470, 82.000, 73.470, 17.000, 90.000, 5.500, 7.200, 73.470, 34.000, 73.470, 130.000, 73.470, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex transition", "3/8", "long-ball hex", "7/32", "D7_32", 17.000, 6.500, "ctr_01", 140, "channel", 93.410, 82.000, 93.410, 17.000, 90.000, 5.500, 7.300, 93.410, 34.000, 93.410, 130.000, 93.410, 146.000],
    ["center_top_right", "1/4DR and 3/8DR long-ball hex transition", "3/8", "long-ball hex", "1/4", "D1_4", 17.300, 6.500, "ctr_01", 141, "channel", 113.350, 82.000, 113.350, 17.000, 90.000, 5.500, 7.500, 113.350, 34.000, 113.350, 130.000, 113.350, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric small", "3/8", "long-ball hex", "5/16", "D5_16", 16.400, 6.500, "cbl_01", 142, "channel", 13.600, 82.000, 13.600, 17.000, 90.000, 5.500, 7.700, 13.600, 34.000, 13.600, 130.000, 13.600, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric small", "3/8", "long-ball hex", "3/8", "D3_8", 17.200, 6.500, "cbl_01", 143, "channel", 33.560, 82.000, 33.560, 17.000, 90.000, 5.500, 7.900, 33.560, 34.000, 33.560, 130.000, 33.560, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric small", "3/8", "long-ball hex", "3mm", "D3M", 15.400, 6.500, "cbl_01", 144, "channel", 53.520, 82.000, 53.520, 17.000, 90.000, 5.500, 7.000, 53.520, 34.000, 53.520, 130.000, 53.520, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric small", "3/8", "long-ball hex", "4mm", "D4M", 15.800, 6.500, "cbl_01", 145, "channel", 73.480, 82.000, 73.480, 17.000, 90.000, 5.500, 7.100, 73.480, 34.000, 73.480, 130.000, 73.480, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric small", "3/8", "long-ball hex", "5mm", "D5M", 16.200, 6.500, "cbl_01", 146, "channel", 93.440, 82.000, 93.440, 17.000, 90.000, 5.500, 7.200, 93.440, 34.000, 93.440, 130.000, 93.440, 146.000],
    ["center_bottom_left", "3/8DR long-ball hex SAE and metric small", "3/8", "long-ball hex", "6mm", "D6M", 16.600, 6.500, "cbl_01", 147, "channel", 113.400, 82.000, 113.400, 17.000, 90.000, 5.500, 7.400, 113.400, 34.000, 113.400, 130.000, 113.400, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric large", "3/8", "long-ball hex", "7mm", "D7M", 16.200, 6.500, "cbr_01", 148, "channel", 13.600, 82.000, 13.600, 17.000, 90.000, 5.500, 7.800, 13.600, 34.000, 13.600, 130.000, 13.600, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric large", "3/8", "long-ball hex", "8mm", "D8M", 16.400, 6.500, "cbr_01", 149, "channel", 33.560, 82.000, 33.560, 17.000, 90.000, 5.500, 8.000, 33.560, 34.000, 33.560, 130.000, 33.560, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric large", "3/8", "long-ball hex", "9mm", "D9M", 16.600, 6.500, "cbr_01", 150, "channel", 53.520, 82.000, 53.520, 17.000, 90.000, 5.500, 8.200, 53.520, 34.000, 53.520, 130.000, 53.520, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric large", "3/8", "long-ball hex", "10mm", "D10M", 16.800, 6.500, "cbr_01", 151, "channel", 73.480, 82.000, 73.480, 17.000, 90.000, 5.500, 8.400, 73.480, 34.000, 73.480, 130.000, 73.480, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric large", "3/8", "long-ball hex", "11mm", "D11M", 17.000, 6.500, "cbr_01", 152, "channel", 93.440, 82.000, 93.440, 17.000, 90.000, 5.500, 8.600, 93.440, 34.000, 93.440, 130.000, 93.440, 146.000],
    ["center_bottom_right", "3/8DR long-ball hex metric large", "3/8", "long-ball hex", "12mm", "D12M", 17.200, 6.500, "cbr_01", 153, "channel", 113.400, 82.000, 113.400, 17.000, 90.000, 5.500, 8.800, 113.400, 34.000, 113.400, 130.000, 113.400, 146.000]
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

function count_kind(kind, i = 0) = i >= len(inventory) ? 0 : (inventory[i][F_KIND] == kind ? 1 : 0) + count_kind(kind, i + 1);
function module_w(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][1] : module_w(name, i + 1);
function module_d(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][2] : module_d(name, i + 1);
function module_ox(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][3] : module_ox(name, i + 1);
function module_oy(name, i = 0) = i >= len(module_table) ? 0 : module_table[i][0] == name ? module_table[i][4] : module_oy(name, i + 1);

assert(len(inventory) == 153, str("Storage count must be 153, got ", len(inventory)));
assert(count_kind("cup") == 128, str("Circular pocket count must be 128, got ", count_kind("cup")));
assert(count_kind("channel") == 25, str("Long channel count must be 25, got ", count_kind("channel")));

module panel(w, d) {
    cube([w, d, base_thickness]);
}

module socket_cup_cut(x, y, diameter, depth) {
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

module raised_label(txt, x, y, rot = 0, size = 5.5) {
    color([0.02, 0.02, 0.02])
        translate([x, y, base_thickness - 0.03])
            rotate([0, 0, rot])
                linear_extrude(height = label_height + 0.03)
                    text(txt, size = size, font = label_font, halign = "center", valign = "center");
}

module module_cuts(module_name) {
    for (item = inventory) {
        if (item[F_MODULE] == module_name && item[F_KIND] == "cup") {
            socket_cup_cut(item[F_X], item[F_Y], item[F_POCKET_DIAMETER], item[F_POCKET_DEPTH]);
        }
        if (item[F_MODULE] == module_name && item[F_KIND] == "channel") {
            rounded_channel_cut(item[F_CHANNEL_X1], item[F_CHANNEL_Y1], item[F_CHANNEL_X2], item[F_CHANNEL_Y2], item[F_CHANNEL_WIDTH], long_channel_depth);
            socket_cup_cut(item[F_END_X], item[F_END_Y], item[F_POCKET_DIAMETER], item[F_POCKET_DEPTH]);
        }
    }
}

module module_labels(module_name) {
    for (item = inventory) {
        if (item[F_MODULE] == module_name) {
            raised_label(item[F_DISPLAY_LABEL], item[F_LABEL_X], item[F_LABEL_Y], item[F_LABEL_ROT], item[F_LABEL_SIZE]);
        }
    }
}

module organizer_module(module_name) {
    w = module_w(module_name);
    d = module_d(module_name);
    assert(w <= safe_build_max && d <= safe_build_max, str("Build-volume fail before seam features: ", module_name));
    union() {
        difference() {
            panel(w, d);
            module_cuts(module_name);
        }
        module_labels(module_name);
    }
}

module fit_test_plate() {
    ft_w = 230.000;
    ft_d = 90.000;
    union() {
        difference() {
            panel(ft_w, ft_d);
            socket_cup_cut(20, 62, 11.2, 5.5);
            socket_cup_cut(54, 62, 15.4, 5.5);
            socket_cup_cut(91, 62, 16.5, 6.5);
            socket_cup_cut(129, 62, 23.4, 6.5);
            socket_cup_cut(171, 62, 22.0, 7.5);
            socket_cup_cut(211, 62, 29.0, 7.5);
            rounded_channel_cut(62, 18, 160, 18, 7.8, 4.0);
            socket_cup_cut(174, 18, 19.4, 6.5);
        }
        raised_label("QSM", 20, 39, 0, 6.5);
        raised_label("QLG", 54, 39, 0, 6.5);
        raised_label("DSM", 91, 39, 0, 6.5);
        raised_label("DLG", 129, 39, 0, 6.5);
        raised_label("HSM", 171, 39, 0, 6.5);
        raised_label("HLG", 211, 39, 0, 6.5);
        raised_label("LONG", 111, 8, 0, 6.5);
    }
}

module reference_layout() {
    for (m = module_table) {
        translate([m[3], m[4], 0]) organizer_module(m[0]);
    }
}

if (render_mode_index_override == 1 || render_mode_index == 1 || render_mode == "left_top") {
    organizer_module("left_top");
} else if (render_mode_index_override == 2 || render_mode_index == 2 || render_mode == "left_bottom") {
    organizer_module("left_bottom");
} else if (render_mode_index_override == 3 || render_mode_index == 3 || render_mode == "center_top_left") {
    organizer_module("center_top_left");
} else if (render_mode_index_override == 4 || render_mode_index == 4 || render_mode == "center_top_right") {
    organizer_module("center_top_right");
} else if (render_mode_index_override == 5 || render_mode_index == 5 || render_mode == "center_bottom_left") {
    organizer_module("center_bottom_left");
} else if (render_mode_index_override == 6 || render_mode_index == 6 || render_mode == "center_bottom_right") {
    organizer_module("center_bottom_right");
} else if (render_mode_index_override == 7 || render_mode_index == 7 || render_mode == "right_top") {
    organizer_module("right_top");
} else if (render_mode_index_override == 8 || render_mode_index == 8 || render_mode == "right_bottom") {
    organizer_module("right_bottom");
} else if (render_mode_index_override == 9 || render_mode_index == 9 || render_mode == "fit_test_plate") {
    fit_test_plate();
} else {
    reference_layout();
}
