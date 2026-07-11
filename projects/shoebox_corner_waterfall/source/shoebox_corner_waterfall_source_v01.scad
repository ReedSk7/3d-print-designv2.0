// project_stem: shoebox_corner_waterfall
// version: v01
// task_mode: original_product_design
// units: millimeters
// orientation: Z+ is up
// default_variant: detailed
// export examples:
//   py -3 scripts\export_stl.py --input projects\shoebox_corner_waterfall\source\shoebox_corner_waterfall_source_v01.scad --output projects\shoebox_corner_waterfall\exports\shoebox_corner_waterfall_simple_v01.stl --define 'variant="simple"'
//   py -3 scripts\export_stl.py --input projects\shoebox_corner_waterfall\source\shoebox_corner_waterfall_source_v01.scad --output projects\shoebox_corner_waterfall\exports\shoebox_corner_waterfall_detailed_v01.stl --define 'variant="detailed"'

$fn = 36;

variant = "detailed"; // "simple" or "detailed"; override with OpenSCAD -D.

// -------------------------
// Main Parameters
// -------------------------
overall_height = 120;
wall_side_width = 70;
max_projection_from_wall = 45;
base_thickness = 6;
back_panel_thickness = 4;
minimum_detail_thickness = 1.2;

cliff_core_depth = 32;
waterfall_face_depth = 34;
waterfall_width_simple = 14;
waterfall_width_detailed = 18;
waterfall_thickness = 2.4;

pool_center_x = 37;
pool_center_y = 37;
pool_outer_radius = 21;
pool_recess_depth = 1.1;

rock_projection_simple = 1.8;
rock_projection_detailed = 2.4;
rock_layer_height = 3.0;

// The footprint keeps 70 mm flat contact length on each wall while limiting
// the central visible protrusion from either wall to 45 mm.
base_footprint_points = [
    [0, 0],
    [wall_side_width, 0],
    [66, 7],
    [58, 22],
    [max_projection_from_wall, max_projection_from_wall],
    [22, 58],
    [7, 66],
    [0, wall_side_width]
];

cliff_core_points = [
    [0, 0],
    [55, 0],
    [48, 10],
    [39, 24],
    [cliff_core_depth, cliff_core_depth],
    [24, 39],
    [10, 48],
    [0, 55]
];

function active_waterfall_width() =
    variant == "simple" ? waterfall_width_simple : waterfall_width_detailed;

function active_rock_projection() =
    variant == "simple" ? rock_projection_simple : rock_projection_detailed;

function diag_xy(center_depth, tangent_offset, normal_offset = 0) = [
    center_depth + (normal_offset - tangent_offset) / sqrt(2),
    center_depth + (normal_offset + tangent_offset) / sqrt(2)
];

// -------------------------
// Helper Modules
// -------------------------
module base_footprint_2d() {
    polygon(points = base_footprint_points);
}

module cliff_core_2d() {
    polygon(points = cliff_core_points);
}

module diagonal_box_at(center_depth, tangent_offset, normal_offset, normal_thickness, tangent_length, z_pos, height_value) {
    p = diag_xy(center_depth, tangent_offset, normal_offset);
    translate([p[0], p[1], z_pos + height_value / 2])
        rotate([0, 0, 45])
            cube([normal_thickness, tangent_length, height_value], center = true);
}

module clipped_to_base_detail(height_value) {
    intersection() {
        children();
        translate([0, 0, base_thickness - 0.25])
            linear_extrude(height = height_value + 0.5)
                base_footprint_2d();
    }
}

module oval_ring_at(cx, cy, outer_radius, inner_radius, height_value) {
    translate([cx, cy, base_thickness])
        linear_extrude(height = height_value)
            scale([1.12, 0.82])
                difference() {
                    circle(r = outer_radius);
                    circle(r = inner_radius);
                }
}

module splash_blob(cx, cy, diameter_value, height_value) {
    translate([cx, cy, base_thickness])
        cylinder(h = height_value, d = diameter_value);
    translate([cx, cy, base_thickness + height_value])
        scale([1, 1, 0.42])
            sphere(d = diameter_value);
}

module x_wall_rock_block(y_pos, z_pos, length_value, height_value, projection_value) {
    translate([back_panel_thickness - 0.15, y_pos, z_pos])
        cube([projection_value + 0.15, length_value, height_value]);
}

module y_wall_rock_block(x_pos, z_pos, length_value, height_value, projection_value) {
    translate([x_pos, back_panel_thickness - 0.15, z_pos])
        cube([length_value, projection_value + 0.15, height_value]);
}

module water_streak(tangent_offset, z_pos, height_value, diameter_value) {
    p = diag_xy(waterfall_face_depth, tangent_offset, waterfall_thickness / 2);
    translate([p[0], p[1], z_pos])
        cylinder(h = height_value, d = diameter_value);
}

// -------------------------
// Structural Body
// -------------------------
module base_with_shallow_pool() {
    difference() {
        linear_extrude(height = base_thickness)
            base_footprint_2d();

        translate([pool_center_x, pool_center_y, base_thickness - pool_recess_depth])
            scale([1.12, 0.82, 1])
                cylinder(h = pool_recess_depth + 0.5, r = pool_outer_radius);
    }
}

module flat_glue_contact_panels() {
    // Back faces at X=0 and Y=0 stay flat for glue contact with shoebox walls.
    cube([back_panel_thickness, wall_side_width, overall_height]);
    cube([wall_side_width, back_panel_thickness, overall_height]);
}

module solid_corner_cliff() {
    linear_extrude(height = overall_height)
        cliff_core_2d();
}

module main_printable_body() {
    union() {
        base_with_shallow_pool();
        flat_glue_contact_panels();
        solid_corner_cliff();
    }
}

// -------------------------
// Waterfall And Pool Detail
// -------------------------
module waterfall_sheet() {
    diagonal_box_at(
        waterfall_face_depth,
        0,
        0,
        waterfall_thickness,
        active_waterfall_width(),
        base_thickness + 0.2,
        overall_height - base_thickness - 10
    );

    // Wider lower fan where the falling water meets the splash pool.
    diagonal_box_at(
        waterfall_face_depth + 1.2,
        0,
        0,
        waterfall_thickness,
        active_waterfall_width() + 7,
        base_thickness + 0.1,
        12
    );

    // Top spill lip, thick enough to print and paint as white water.
    diagonal_box_at(
        waterfall_face_depth,
        0,
        0.4,
        waterfall_thickness + 0.8,
        active_waterfall_width() + 10,
        overall_height - 9,
        4
    );
}

module simple_water_lines() {
    water_streak(-4.8, base_thickness + 5, overall_height - 22, 1.35);
    water_streak(0, base_thickness + 10, overall_height - 32, 1.4);
    water_streak(4.8, base_thickness + 6, overall_height - 25, 1.35);
}

module detailed_water_lines() {
    water_streak(-7.2, base_thickness + 4, 92, 1.35);
    water_streak(-4.8, base_thickness + 22, 76, 1.25);
    water_streak(-2.2, base_thickness + 8, 101, 1.45);
    water_streak(1.8, base_thickness + 16, 88, 1.25);
    water_streak(5.0, base_thickness + 5, 96, 1.35);
    water_streak(7.4, base_thickness + 38, 58, 1.25);

    // Short raised breaks make the flow read as falling water after painting.
    diagonal_box_at(waterfall_face_depth + 1.4, -5.5, 0, 1.35, 7, 41, 2.0);
    diagonal_box_at(waterfall_face_depth + 1.4, 3.8, 0, 1.35, 8, 62, 2.0);
    diagonal_box_at(waterfall_face_depth + 1.4, -1.5, 0, 1.35, 8, 86, 2.0);
}

module pool_ripples_and_splash() {
    clipped_to_base_detail(8) {
        oval_ring_at(pool_center_x, pool_center_y, pool_outer_radius + 1.7, pool_outer_radius, 1.3);
        oval_ring_at(pool_center_x + 1, pool_center_y - 1, 15.0, 13.5, 1.2);
        oval_ring_at(pool_center_x - 2, pool_center_y + 1, 10.2, 8.8, 1.2);
        oval_ring_at(pool_center_x, pool_center_y, 5.8, 4.3, 1.2);

        if (variant == "detailed") {
            oval_ring_at(pool_center_x + 4, pool_center_y - 3, 18.5, 17.1, 1.2);
            splash_blob(pool_center_x - 5, pool_center_y - 3, 2.4, 2.0);
            splash_blob(pool_center_x + 1, pool_center_y - 5, 2.0, 2.4);
            splash_blob(pool_center_x + 6, pool_center_y - 1, 2.3, 1.8);
            splash_blob(pool_center_x - 1, pool_center_y + 4, 1.8, 1.8);
        } else {
            splash_blob(pool_center_x - 3, pool_center_y - 3, 2.2, 1.7);
            splash_blob(pool_center_x + 4, pool_center_y - 1, 2.0, 1.7);
        }
    }
}

// -------------------------
// Rock Texture
// -------------------------
module simple_side_rocks() {
    for (i = [0:5]) {
        z_row = base_thickness + 8 + i * 17;
        x_wall_rock_block(8 + (i % 2) * 5, z_row, 24, rock_layer_height, rock_projection_simple);
        x_wall_rock_block(38 - (i % 2) * 4, z_row + 7, 20, 2.6, rock_projection_simple);
        y_wall_rock_block(8 + ((i + 1) % 2) * 5, z_row + 4, 24, rock_layer_height, rock_projection_simple);
        y_wall_rock_block(39 - ((i + 1) % 2) * 4, z_row + 11, 19, 2.6, rock_projection_simple);

        diagonal_box_at(cliff_core_depth, -14, 1.1, rock_projection_simple, 15, z_row + 1, 3.0);
        diagonal_box_at(cliff_core_depth, 14, 1.1, rock_projection_simple, 15, z_row + 8, 3.0);
    }
}

module detailed_side_rocks() {
    for (i = [0:8]) {
        z_row = base_thickness + 7 + i * 11;
        x_wall_rock_block(6 + (i % 3) * 4, z_row, 21 + (i % 2) * 5, 2.8, rock_projection_detailed);
        x_wall_rock_block(34 + (i % 2) * 3, z_row + 5, 19, 2.4, rock_projection_detailed - 0.4);
        y_wall_rock_block(7 + ((i + 1) % 3) * 4, z_row + 2, 22 + ((i + 1) % 2) * 4, 2.8, rock_projection_detailed);
        y_wall_rock_block(35 + ((i + 1) % 2) * 3, z_row + 8, 18, 2.4, rock_projection_detailed - 0.4);

        diagonal_box_at(cliff_core_depth, -18, 1.4, rock_projection_detailed, 12, z_row, 3.0);
        diagonal_box_at(cliff_core_depth, -9, 1.2, rock_projection_detailed - 0.3, 10, z_row + 6, 2.6);
        diagonal_box_at(cliff_core_depth, 10, 1.2, rock_projection_detailed - 0.3, 10, z_row + 3, 2.6);
        diagonal_box_at(cliff_core_depth, 18, 1.4, rock_projection_detailed, 12, z_row + 8, 3.0);
    }

    // Fine horizontal strata lines, still above the 1.2 mm detail minimum.
    for (j = [0:5]) {
        z_line = base_thickness + 15 + j * 15;
        x_wall_rock_block(5, z_line, 58, 1.25, 1.25);
        y_wall_rock_block(5, z_line + 5, 58, 1.25, 1.25);
        diagonal_box_at(cliff_core_depth, 0, 1.0, 1.3, 45, z_line + 8, 1.25);
    }
}

module rock_texture() {
    if (variant == "simple") {
        simple_side_rocks();
    } else {
        detailed_side_rocks();
    }
}

// -------------------------
// Final Render
// -------------------------
module shoebox_corner_waterfall() {
    union() {
        main_printable_body();
        rock_texture();
        waterfall_sheet();
        if (variant == "simple") {
            simple_water_lines();
        } else {
            detailed_water_lines();
        }
        pool_ripples_and_splash();
    }
}

shoebox_corner_waterfall();
