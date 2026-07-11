// Wrapper for test-fit exports of the W11457841 inner latch insert

use <inner_latch_full_fidelity.scad>;
use <inner_latch_simplified.scad>;

family = "simplified"; // simplified or full_fidelity
use_full_fidelity_family = false;

if (use_full_fidelity_family || family == "full_fidelity")
    inner_latch_full_fidelity_variant("test_fit");
else
    inner_latch_simplified_variant("test_fit");
