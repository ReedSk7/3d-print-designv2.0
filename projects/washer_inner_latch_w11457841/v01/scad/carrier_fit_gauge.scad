// Helper gauge / mock socket for bench fitting the replacement inner latch insert

include <common_params.scad>;
use <inner_latch_simplified.scad>;

render_variant = "gauge"; // gauge or mockup

latch_body_width = 19.3;
latch_body_depth = 8.8;
latch_body_height = 27.8;
engagement_face_width = 19.3;
pivot_or_capture_diameter = 3.1;
carrier_reference_width = 28.1;

module carrier_fit_gauge_body() {
    mock_carrier_socket(
        latch_span = carrier_reference_width,
        latch_window_width = engagement_face_width + 2.2,
        cavity_depth = latch_body_depth + 1.2,
        cavity_height = latch_body_height * 0.72,
        pivot_d = pivot_or_capture_diameter
    );
}

if (render_variant == "mockup") {
    color([0.82, 0.82, 0.82, 0.45])
        carrier_fit_gauge_body();

    color([0.16, 0.16, 0.16])
        inner_latch_simplified_variant("nominal");
} else {
    carrier_fit_gauge_body();
}
