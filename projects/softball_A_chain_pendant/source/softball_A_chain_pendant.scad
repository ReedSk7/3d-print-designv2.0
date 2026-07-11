// project_stem: softball_A_chain_pendant
// version: v01
// task_mode: mesh_cleanup_and_remodel
// units: millimeters
// orientation: Z+ is up
// printer_name: Bambu Lab P2S with AMS
// material: PLA or PETG
// print_orientation: flat on bed, face up
// support_notes: designed for no supports in default orientation

$fn = 56;

// ------------------------------------------------------------
// Export controls
// ------------------------------------------------------------
part = is_undef(part_index_override) ? (is_undef(part_override) ? "full_multicolor_assembly" : part_override) : (part_index_override == 1 ? "full_single_color" : part_index_override == 2 ? "black_base_outline" : part_index_override == 3 ? "yellow_softball_face" : part_index_override == 4 ? "red_A_and_stitches" : part_index_override == 5 ? "white_highlight_optional" : "full_multicolor_assembly");
// part options:
// full_multicolor_assembly, full_single_color,
// black_base_outline, yellow_softball_face,
// red_A_and_stitches, white_highlight_optional

size_variant = is_undef(size_index_override) ? (is_undef(size_variant_override) ? "large" : size_variant_override) : (size_index_override == 1 ? "small" : "large");      // large, small
bail_variant = is_undef(bail_index_override) ? (is_undef(bail_variant_override) ? "standard" : bail_variant_override) : (bail_index_override == 1 ? "oversized" : "standard");   // standard, oversized
use_font_A = is_undef(use_font_A_override) ? false : use_font_A_override;              // false uses the reliable geometric fallback
include_optional_highlights = is_undef(include_optional_highlights_override) ? false : include_optional_highlights_override;

// ------------------------------------------------------------
// Core dimensions
// ------------------------------------------------------------
project_stem = "softball_A_chain_pendant";
version = "v01";

large_target_height = 104;
small_target_height = 75;
xy_scale = size_variant == "small" ? small_target_height / large_target_height : 1;

body_diameter = 84 * xy_scale;
body_radius = body_diameter / 2;
outer_rim_width = max(2.2, 3.2 * xy_scale);

base_height = size_variant == "small" ? 3.9 : 4.2;
face_height = 0.85;
rim_height = 1.05;
stitch_shadow_height = 0.45;
stitch_height = 0.95;
letter_outline_height = 1.45;
letter_red_height = 1.05;
highlight_height = 0.42;
overlap = 0.06;

body_chamfer = min(0.55, 0.75 * xy_scale);
feature_chamfer = min(0.30, 0.42 * xy_scale);
letter_outline_width = max(2.1, 2.9 * xy_scale);

bail_open_w = bail_variant == "oversized" ? max(16, 22 * xy_scale) : max(10, 15 * xy_scale);
bail_open_h = bail_variant == "oversized" ? max(8, 12 * xy_scale) : max(6, 8.5 * xy_scale);
bail_wall = bail_variant == "oversized" ? max(3.4, 4.8 * xy_scale) : max(3.2, 4.5 * xy_scale);
bail_outer_w = bail_open_w + bail_wall * 2;
bail_outer_h = bail_open_h + bail_wall * 2 + 6 * xy_scale;
bail_center_y = body_radius + bail_outer_h / 2 - 4.2 * xy_scale;
bail_corner = max(2.8, 4.0 * xy_scale);
fusion_pad_h = max(8, 12 * xy_scale);

stitch_width = max(1.2, 1.45 * xy_scale);
stitch_spacing_clear = 0.9;
stitch_len = max(4.5, 6.4 * xy_scale);
seam_line_width = max(1.2, 1.35 * xy_scale);

letter_leg_width = max(7.8, 11.5 * xy_scale);
letter_height = body_diameter * 0.86;
letter_bar_height = max(6.8, 9.4 * xy_scale);
letter_corner = max(1.5, 2.4 * xy_scale);

black = [0.01, 0.01, 0.01];
yellow = [1.0, 0.82, 0.08];
red = [0.86, 0.02, 0.02];
white = [1.0, 1.0, 0.92];

// ------------------------------------------------------------
// 2D helper modules
// ------------------------------------------------------------
module rounded_rect_2d(w, h, r) {
    rr = min(r, min(w, h) / 2 - 0.01);
    offset(r = rr)
        square([max(0.1, w - 2 * rr), max(0.1, h - 2 * rr)], center = true);
}

module capsule_between_2d(p1, p2, w) {
    hull() {
        translate(p1) circle(d = w);
        translate(p2) circle(d = w);
    }
}

module chamfered_extrude(height, top_chamfer = 0.25) {
    clean_chamfer = min(top_chamfer, height / 3);
    if (clean_chamfer > 0) {
        linear_extrude(height = height - clean_chamfer)
            children();
        translate([0, 0, height - clean_chamfer])
            linear_extrude(height = clean_chamfer)
                offset(delta = -clean_chamfer)
                    children();
    } else {
        linear_extrude(height = height)
            children();
    }
}

// ------------------------------------------------------------
// Pendant body and bail
// ------------------------------------------------------------
module body_circle_2d() {
    circle(r = body_radius);
}

module bail_hole_2d() {
    translate([0, bail_center_y])
        rounded_rect_2d(bail_open_w, bail_open_h, min(3 * xy_scale, bail_open_h / 2 - 0.05));
}

module full_body_silhouette_2d() {
    union() {
        body_circle_2d();

        // Chunky top bail, centered and heavily blended into the medallion.
        translate([0, bail_center_y])
            rounded_rect_2d(bail_outer_w, bail_outer_h, bail_corner);

        translate([0, body_radius - 1.8 * xy_scale])
            rounded_rect_2d(bail_outer_w + 7 * xy_scale, fusion_pad_h, bail_corner);
    }
}

module black_base_2d() {
    difference() {
        full_body_silhouette_2d();
        bail_hole_2d();
    }
}

module softball_face_2d() {
    circle(r = body_radius - outer_rim_width);
}

module outer_rim_2d() {
    difference() {
        circle(r = body_radius);
        circle(r = body_radius - outer_rim_width);
    }
}

// ------------------------------------------------------------
// Softball stitching
// ------------------------------------------------------------
function seam_point(side, angle) =
    [
        side * (body_radius * 0.63 + body_radius * 0.10 * cos(angle)),
        body_radius * 0.74 * sin(angle)
    ];

module seam_curve_2d(side, w = seam_line_width) {
    for (i = [0 : 10]) {
        a1 = -62 + i * 124 / 11;
        a2 = -62 + (i + 1) * 124 / 11;
        capsule_between_2d(seam_point(side, a1), seam_point(side, a2), w);
    }
}

module stitch_laces_2d(side, w = stitch_width) {
    for (i = [0 : 10]) {
        a = -54 + i * 108 / 10;
        p = seam_point(side, a);
        translate(p)
            rotate(side * 34)
                rounded_rect_2d(stitch_len, w, w / 2);
    }
}

module stitches_2d(w = stitch_width) {
    union() {
        for (side = [-1, 1]) {
            seam_curve_2d(side, max(w, seam_line_width));
            stitch_laces_2d(side, w);
        }
    }
}

// ------------------------------------------------------------
// Decorative printable A
// ------------------------------------------------------------
module script_stroke(points, w) {
    for (i = [0 : len(points) - 2])
        capsule_between_2d(points[i], points[i + 1], w);
}

module fallback_A_union_2d() {
    // Built from chunky strokes so the decorative A remains printable and
    // does not inherit distortions from the rough AI mesh references.
    union() {
        // Right upright/slanted stem.
        script_stroke([
            [ body_diameter * 0.205, -body_diameter * 0.385],
            [ body_diameter * 0.245, -body_diameter * 0.120],
            [ body_diameter * 0.210,  body_diameter * 0.360]
        ], letter_leg_width * 1.18);

        // Left arched stem with the hook-like upper curl from the reference style.
        script_stroke([
            [-body_diameter * 0.330, -body_diameter * 0.350],
            [-body_diameter * 0.190, -body_diameter * 0.125],
            [-body_diameter * 0.070,  body_diameter * 0.170],
            [ body_diameter * 0.065,  body_diameter * 0.345]
        ], letter_leg_width * 0.98);

        // Curved top cap.
        script_stroke([
            [-body_diameter * 0.270,  body_diameter * 0.245],
            [-body_diameter * 0.145,  body_diameter * 0.365],
            [ body_diameter * 0.075,  body_diameter * 0.390]
        ], max(7.2, 9.5 * xy_scale));

        // Crossbar, slightly rising like the Meshy reference.
        script_stroke([
            [-body_diameter * 0.165, -body_diameter * 0.070],
            [ body_diameter * 0.065, -body_diameter * 0.045],
            [ body_diameter * 0.245, -body_diameter * 0.025]
        ], letter_bar_height);

        // Lower left swash protrudes beyond the ball, but stays thick.
        script_stroke([
            [-body_diameter * 0.450, -body_diameter * 0.415],
            [-body_diameter * 0.270, -body_diameter * 0.335],
            [-body_diameter * 0.080, -body_diameter * 0.350],
            [ body_diameter * 0.105, -body_diameter * 0.315]
        ], max(8.0, 11.0 * xy_scale));

        // Lower right foot/curl.
        script_stroke([
            [ body_diameter * 0.140, -body_diameter * 0.355],
            [ body_diameter * 0.285, -body_diameter * 0.420],
            [ body_diameter * 0.410, -body_diameter * 0.335]
        ], max(8.0, 10.6 * xy_scale));
    }
}

module fallback_A_2d() {
    difference() {
        fallback_A_union_2d();

        // Large inner counter. Kept broad so it slices cleanly.
        translate([body_diameter * 0.015, body_diameter * 0.055])
            polygon([
                [-body_diameter * 0.095, -body_diameter * 0.060],
                [ body_diameter * 0.095, -body_diameter * 0.060],
                [ body_diameter * 0.022,  body_diameter * 0.185]
            ]);

        // Lower notch keeps the A readable without making fragile tips.
        translate([body_diameter * 0.010, -body_diameter * 0.265])
            rounded_rect_2d(body_diameter * 0.165, max(4.6, 6.2 * xy_scale), max(1.1, 1.7 * xy_scale));
    }
}

module font_A_2d() {
    // Optional font path. The default fallback above is used for reliable exports.
    text("A", size = body_diameter * 0.76, font = "Liberation Serif:style=Bold", halign = "center", valign = "center");
}

module letter_A_2d() {
    if (use_font_A) {
        font_A_2d();
    } else {
        fallback_A_2d();
    }
}

module letter_outline_2d() {
    difference() {
        offset(delta = letter_outline_width)
            letter_A_2d();
        letter_A_2d();
    }
}

module white_highlight_2d() {
    union() {
        translate([-body_diameter * 0.125, body_diameter * 0.225])
            rotate(11)
                rounded_rect_2d(body_diameter * 0.18, max(1.2, 1.45 * xy_scale), max(0.55, 0.7 * xy_scale));

        translate([body_diameter * 0.155, -body_diameter * 0.055])
            rotate(13)
                rounded_rect_2d(body_diameter * 0.15, max(1.2, 1.45 * xy_scale), max(0.55, 0.7 * xy_scale));
    }
}

// ------------------------------------------------------------
// Color bodies
// ------------------------------------------------------------
module black_base_outline_body() {
    color(black)
    union() {
        chamfered_extrude(base_height, body_chamfer)
            black_base_2d();

        translate([0, 0, base_height - overlap])
            chamfered_extrude(rim_height + overlap, feature_chamfer)
                outer_rim_2d();

        translate([0, 0, base_height + face_height - overlap])
            chamfered_extrude(stitch_shadow_height + overlap, 0.10)
                offset(delta = 0.38)
                    stitches_2d(max(stitch_width, seam_line_width));

        translate([0, 0, base_height + face_height - overlap])
            chamfered_extrude(letter_outline_height + overlap, feature_chamfer)
                letter_outline_2d();
    }
}

module yellow_softball_face_body() {
    color(yellow)
    translate([0, 0, base_height - overlap])
        chamfered_extrude(face_height + overlap, 0.18)
            softball_face_2d();
}

module red_A_and_stitches_body() {
    color(red)
    union() {
        translate([0, 0, base_height + face_height + stitch_shadow_height - overlap])
            chamfered_extrude(stitch_height + overlap, 0.12)
                stitches_2d(stitch_width);

        translate([0, 0, base_height + face_height + letter_outline_height - overlap])
            chamfered_extrude(letter_red_height + overlap, feature_chamfer)
                letter_A_2d();
    }
}

module white_highlight_body() {
    color(white)
    translate([0, 0, base_height + face_height + letter_outline_height + letter_red_height - overlap])
        chamfered_extrude(highlight_height + overlap, 0.08)
            white_highlight_2d();
}

module full_multicolor_assembly_body() {
    black_base_outline_body();
    yellow_softball_face_body();
    red_A_and_stitches_body();
    if (include_optional_highlights)
        white_highlight_body();
}

module full_single_color_body() {
    union() {
        black_base_outline_body();
        yellow_softball_face_body();
        red_A_and_stitches_body();
        if (include_optional_highlights)
            white_highlight_body();
    }
}

// ------------------------------------------------------------
// Part selector
// ------------------------------------------------------------
if (part == "black_base_outline") {
    black_base_outline_body();
} else if (part == "yellow_softball_face") {
    yellow_softball_face_body();
} else if (part == "red_A_and_stitches") {
    red_A_and_stitches_body();
} else if (part == "white_highlight_optional") {
    white_highlight_body();
} else if (part == "full_single_color") {
    full_single_color_body();
} else {
    full_multicolor_assembly_body();
}
