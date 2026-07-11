/*
metric_to_standard_chart
task_mode: original_product_design
units: millimeters
orientation: portrait sign on XY plane, Z+ up

Geometry Contract
- Overall sign: 250 mm wide x 360 mm tall.
- Base thickness: 3.0 mm.
- Raised frame and grid top out 1.0 mm above the base.
- Raised text tops out 1.4 mm above the base for AMS color visibility.
- Mount holes: four 5.0 mm through-holes, centers inset 10.0 mm from edges.
- Minimum raised line feature width: 0.9 mm.
- Source of truth: this OpenSCAD file; STL files are export artifacts.

Export selector:
- default / combined
- base_and_grid
- title_and_headers
- metric_text_red
- standard_text_green
- decimal_text_blue
- difference_text_orange
- all_text_white
*/

$fn = 48;

project_stem = "metric_to_standard_chart";
version = "v01";
printer_name = "generic_fdm";
material = "pla_or_petg";
nozzle_diameter = 0.4;
fit_clearance = 0.2;

overall_width = 250;
overall_height = 360;
base_thickness = 3.0;
wall_thickness = base_thickness;

feature_raise = 1.0;
text_protrusion_above_grid = 0.4;
text_raise = feature_raise + text_protrusion_above_grid;
layer_overlap = 0.04;
feature_start_z = base_thickness - layer_overlap;
feature_total_height = feature_raise + layer_overlap;
text_start_z = base_thickness - layer_overlap;
text_total_height = text_raise + layer_overlap;

border_width = 3.0;
grid_line_width = 0.9;
title_rule_width = 1.1;
text_stroke_offset = 0.10;

mount_hole_diameter = 5.0;
mount_hole_center_offset = 10.0;
cutter_overlap = 0.6;

table_left = 10.0;
table_right = overall_width - table_left;
table_width = table_right - table_left;
table_top = 292.0;
table_bottom = 32.0;
table_height = table_top - table_bottom;
header_height = 16.0;
table_header_bottom_y = table_top - header_height;

row_count = 23;
data_row_height = (table_height - header_height) / row_count;

metric_column_width = table_width * 0.22;
standard_column_width = table_width * 0.28;
decimal_column_width = table_width * 0.25;
difference_column_width = table_width * 0.25;

column_edges = [
    table_left,
    table_left + metric_column_width,
    table_left + metric_column_width + standard_column_width,
    table_left + metric_column_width + standard_column_width + decimal_column_width,
    table_right
];

title_line_one_y = 337.0;
title_line_two_y = 319.0;
title_underline_y = 303.0;
footer_note_y = 18.0;

title_line_one_size = 13.5;
title_line_two_size = 9.8;
header_text_size = 3.9;
data_text_size = 4.5;
footer_text_size = 3.8;

font_name = "Arial:style=Bold";

header_labels = [
    "Metric Size (mm)",
    "Closest Standard Size",
    "Decimal Equivalent",
    "Difference"
];

conversion_rows = [
    [3.18, 1, 8, "3.18mm", "1/8\"", "0.125\"", "+0.000\""],
    [4, 5, 32, "4mm", "5/32\"", "0.156\"", "-0.001\""],
    [5, 3, 16, "5mm", "3/16\"", "0.188\"", "-0.009\""],
    [6, 7, 32, "6mm", "7/32\"", "0.219\"", "-0.017\""],
    [7, 1, 4, "7mm", "1/4\"", "0.250\"", "-0.026\""],
    [8, 5, 16, "8mm", "5/16\"", "0.312\"", "-0.002\""],
    [9, 11, 32, "9mm", "11/32\"", "0.344\"", "-0.011\""],
    [10, 3, 8, "10mm", "3/8\"", "0.375\"", "-0.019\""],
    [11, 7, 16, "11mm", "7/16\"", "0.438\"", "+0.004\""],
    [12, 15, 32, "12mm", "15/32\"", "0.469\"", "-0.004\""],
    [13, 1, 2, "13mm", "1/2\"", "0.500\"", "-0.012\""],
    [14, 9, 16, "14mm", "9/16\"", "0.562\"", "+0.011\""],
    [15, 19, 32, "15mm", "19/32\"", "0.594\"", "+0.003\""],
    [16, 5, 8, "16mm", "5/8\"", "0.625\"", "-0.005\""],
    [17, 21, 32, "17mm", "21/32\"", "0.656\"", "-0.013\""],
    [18, 11, 16, "18mm", "11/16\"", "0.688\"", "-0.021\""],
    [19, 3, 4, "19mm", "3/4\"", "0.750\"", "+0.002\""],
    [20, 25, 32, "20mm", "25/32\"", "0.781\"", "-0.006\""],
    [21, 13, 16, "21mm", "13/16\"", "0.812\"", "-0.014\""],
    [22, 7, 8, "22mm", "7/8\"", "0.875\"", "+0.009\""],
    [23, 29, 32, "23mm", "29/32\"", "0.906\"", "+0.001\""],
    [24, 15, 16, "24mm", "15/16\"", "0.938\"", "-0.007\""],
    [25, 1, 1, "25mm", "1\"", "1.000\"", "+0.016\""]
];

selected_part = is_undef(export_part) ? "combined" : export_part;
row_echo_enabled = is_undef(enable_row_echo) ? false : enable_row_echo;

function column_center(column_index) =
    (column_edges[column_index] + column_edges[column_index + 1]) / 2;

function data_row_center_y(row_index) =
    table_header_bottom_y - data_row_height * (row_index + 0.5);

function standard_decimal_inches(row) = row[1] / row[2];
function exact_metric_inches(row) = row[0] / 25.4;
function difference_inches(row) = standard_decimal_inches(row) - exact_metric_inches(row);

module raised_rect(center_x, center_y, width_value, height_value, height_value_z = feature_total_height) {
    translate([
        center_x - width_value / 2,
        center_y - height_value / 2,
        feature_start_z
    ])
        cube([width_value, height_value, height_value_z]);
}

module raised_text(label, center_x, center_y, text_size, height_value_z = text_total_height) {
    translate([center_x, center_y, text_start_z])
        linear_extrude(height = height_value_z)
            offset(delta = text_stroke_offset)
                text(
                    label,
                    size = text_size,
                    font = font_name,
                    halign = "center",
                    valign = "center"
                );
}

module mount_hole_cutters() {
    for (x_pos = [mount_hole_center_offset, overall_width - mount_hole_center_offset]) {
        for (y_pos = [mount_hole_center_offset, overall_height - mount_hole_center_offset]) {
            translate([x_pos, y_pos, -cutter_overlap])
                cylinder(h = base_thickness + feature_raise + cutter_overlap * 2, d = mount_hole_diameter);
        }
    }
}

module outer_frame() {
    raised_rect(overall_width / 2, border_width / 2, overall_width, border_width);
    raised_rect(overall_width / 2, overall_height - border_width / 2, overall_width, border_width);
    raised_rect(border_width / 2, overall_height / 2, border_width, overall_height);
    raised_rect(overall_width - border_width / 2, overall_height / 2, border_width, overall_height);
}

module table_grid() {
    raised_rect(table_left + table_width / 2, table_top, table_width, grid_line_width);
    raised_rect(table_left + table_width / 2, table_bottom, table_width, grid_line_width);
    raised_rect(table_left, table_bottom + table_height / 2, grid_line_width, table_height);
    raised_rect(table_right, table_bottom + table_height / 2, grid_line_width, table_height);

    for (column_index = [1 : len(column_edges) - 2]) {
        raised_rect(
            column_edges[column_index],
            table_bottom + table_height / 2,
            grid_line_width,
            table_height
        );
    }

    raised_rect(
        table_left + table_width / 2,
        table_header_bottom_y,
        table_width,
        grid_line_width
    );

    for (row_index = [1 : row_count - 1]) {
        raised_rect(
            table_left + table_width / 2,
            table_header_bottom_y - data_row_height * row_index,
            table_width,
            grid_line_width
        );
    }
}

module title_rule() {
    raised_rect(overall_width / 2, title_underline_y, table_width, title_rule_width);
}

module base_and_grid_body() {
    difference() {
        union() {
            cube([overall_width, overall_height, base_thickness]);
            outer_frame();
            title_rule();
            table_grid();
        }
        mount_hole_cutters();
    }
}

module title_and_headers_part() {
    raised_text("METRIC TO STANDARD", overall_width / 2, title_line_one_y, title_line_one_size);
    raised_text("SIZE CONVERSION CHART", overall_width / 2, title_line_two_y, title_line_two_size);

    for (column_index = [0 : len(header_labels) - 1]) {
        raised_text(
            header_labels[column_index],
            column_center(column_index),
            table_top - header_height / 2,
            header_text_size
        );
    }

    raised_text("Quick reference only — exact 1 inch = 25.4 mm", overall_width / 2, footer_note_y, footer_text_size);
}

module metric_text_red_part() {
    for (row_index = [0 : row_count - 1]) {
        raised_text(
            conversion_rows[row_index][3],
            column_center(0),
            data_row_center_y(row_index),
            data_text_size
        );
    }
}

module standard_text_green_part() {
    for (row_index = [0 : row_count - 1]) {
        raised_text(
            conversion_rows[row_index][4],
            column_center(1),
            data_row_center_y(row_index),
            data_text_size
        );
    }
}

module decimal_text_blue_part() {
    for (row_index = [0 : row_count - 1]) {
        raised_text(
            conversion_rows[row_index][5],
            column_center(2),
            data_row_center_y(row_index),
            data_text_size
        );
    }
}

module difference_text_orange_part() {
    for (row_index = [0 : row_count - 1]) {
        raised_text(
            conversion_rows[row_index][6],
            column_center(3),
            data_row_center_y(row_index),
            data_text_size
        );
    }
}

module all_text_white_part() {
    union() {
        title_and_headers_part();
        metric_text_red_part();
        standard_text_green_part();
        decimal_text_blue_part();
        difference_text_orange_part();
    }
}

module combined_part() {
    union() {
        base_and_grid_body();
        all_text_white_part();
    }
}

module echo_table_rows() {
    echo("Metric Size, Standard Fraction, Decimal Equivalent, Difference");
    for (row_index = [0 : row_count - 1]) {
        echo(str(
            conversion_rows[row_index][3], ", ",
            conversion_rows[row_index][4], ", ",
            conversion_rows[row_index][5], ", ",
            conversion_rows[row_index][6],
            " | exact standard decimal: ",
            standard_decimal_inches(conversion_rows[row_index]),
            " | exact difference: ",
            difference_inches(conversion_rows[row_index])
        ));
    }
}

if (row_echo_enabled) {
    echo_table_rows();
}

if (selected_part == "base_and_grid") {
    base_and_grid_body();
} else if (selected_part == "title_and_headers") {
    title_and_headers_part();
} else if (selected_part == "metric_text_red") {
    metric_text_red_part();
} else if (selected_part == "standard_text_green") {
    standard_text_green_part();
} else if (selected_part == "decimal_text_blue") {
    decimal_text_blue_part();
} else if (selected_part == "difference_text_orange") {
    difference_text_orange_part();
} else if (selected_part == "all_text_white") {
    all_text_white_part();
} else {
    combined_part();
}
