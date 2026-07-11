// Versioned wrapper for repo validation.
// The editable source of truth is softball_A_chain_pendant.scad.
module versioned_validation_hint() {
    linear_extrude(height = 0.01)
        square([0.01, 0.01], center = true);
}

include <softball_A_chain_pendant.scad>
