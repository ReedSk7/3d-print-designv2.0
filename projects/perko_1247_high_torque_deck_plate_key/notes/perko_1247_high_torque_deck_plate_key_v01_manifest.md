---
project_stem: perko_1247_high_torque_deck_plate_key
version: v01
task_mode: reference_based_reconstruction
status: generated outputs; physical fit NOT VERIFIED
source_file: source/perko_1247_high_torque_deck_plate_key_v01.scad
optional_source_file: source/perko_1247_high_torque_deck_plate_key_v01_metal_pin_body.scad
export_file: exports/perko_1247_high_torque_deck_plate_key_v01.stl
optional_export_file: exports/perko_1247_high_torque_deck_plate_key_v01_metal_pin_body.stl
preview_files: previews/perko_1247_high_torque_deck_plate_key_v01_iso.png;previews/perko_1247_high_torque_deck_plate_key_v01_front.png;previews/perko_1247_high_torque_deck_plate_key_v01_side.png
notes_file: notes/perko_1247_high_torque_deck_plate_key_v01_notes.md
review_report: notes/perko_1247_high_torque_deck_plate_key_v01_review_report.md
authoritative_references: user_provided_critical_mating_dimensions
supporting_references: perko_1247_style_reference_only
measured_dimensions: lug_spacing_28_58_mm;lug_tip_4_5_mm;lug_base_5_2_mm;lug_protrusion_19_05_mm
inferred_dimensions: handle_outline;head_width;tail_width;root_relief;metal_pin_bosses
protected_interfaces: lug_center_spacing;lug_tip_diameter;lug_base_diameter;lug_protrusion;metal_pin_center_spacing
low_confidence_zones: cap_face_clearance_at_lug_roots;metal_pin_fit_tuning;oem_non_mating_silhouette
stl_export_status: exported and mesh-checked
preview_export_status: exported
verification_status: NOT VERIFIED
future_3mf_status: not created
---

# Project Manifest

## Project Summary

Parametric high-torque marine deck plate key with exact two-lug mating geometry and a 100 mm solid handle for stuck gas-cap leverage.

## Target Part

Perko 1247-style two-lug marine deck plate key, strength-optimized for FDM PETG.

## Reused Parts

Existing gas cap and deck plate.

## Not-Modeled Items

Deck plate, gas cap, gasket, chain, lock, and threads.

## References

### Authoritative

- User-provided critical mating dimensions.

### Supporting

- Perko 1247 two-lug key design style.

## Anchor Dimensions

- Lug center spacing: 28.58 mm.
- Lug tip diameter: 4.5 mm.
- Lug base shaft diameter: 5.2 mm.
- Lug protrusion: 19.05 mm.
- Handle total length: 100 mm.
- Body thickness: 11 mm.

## Protected Interfaces

- Lug centers and spacing.
- Lug taper endpoints.
- Lug protrusion.
- Optional metal-pin hole center spacing.

## Measured Versus Inferred Dimensions

### Measured

- User-provided protected lug dimensions.

### Inferred

- Handle/head/tail silhouette.
- Root relief collar diameter.
- Optional metal-pin boss size and hole default.

## Known Assumptions

- User-provided dimensions match the actual cap.
- Root relief collar has enough cap-face clearance or the metal-pin version will be used.
- Metal-pin hole diameter will be tuned to the actual dowel/bolt and printer.

## Low-Confidence Zones

- Physical fit and torque durability.
- OEM non-mating silhouette.
- Cap-face clearance around lug holes.

## Artifact Checklist

- [x] source exists
- [x] STL export exists
- [x] notes exist
- [x] manifest exists
- [x] required previews exist
- [x] review report exists
- [x] comparison log exists when reconstruction

## Verification Notes

SCAD validation, STL export, mesh quality checks, and required preview renders passed. Physical fit and stuck-cap torque durability are still `NOT VERIFIED`.

## Next Actions

- Print a two-lug fit-test or the full key and verify fit on the actual gas cap before applying high torque.
- Use the optional metal-pin body for repeated high-torque use.
