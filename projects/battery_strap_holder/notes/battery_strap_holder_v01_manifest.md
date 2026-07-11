---
project_stem: battery_strap_holder
version: v01
task_mode: reference_based_reconstruction
status: initial parametric reconstruction; physical fit not verified
source_file: source/battery_strap_holder_v01.scad
export_file: exports/battery_strap_holder_v01.stl
preview_files: [previews/battery_strap_holder_v01_iso.png, previews/battery_strap_holder_v01_front.png, previews/battery_strap_holder_v01_side.png]
notes_file: notes/battery_strap_holder_v01_notes.md
review_report: notes/battery_strap_holder_v01_review_report.md
authoritative_references: [20260524_173041.jpg caliper value, 20260524_173058.jpg caliper value, 20260524_173128.jpg caliper value, 20260524_173112.jpg caliper value]
supporting_references: [standards/GEOMETRY_FEEDBACK_LOOP.md, standards/printer_material_profiles.json, standards/hardware_library.scad]
measured_dimensions: [total_outer_length_y 74.0 mm, inner_body_span_y 50.2 mm, main_offset_step_height_z 7.1 mm, tab_sub_thickness_z 4.0 mm]
inferred_dimensions: [overall_width_x 11.0 mm, center_bridge_width_x 8.5 mm, mounting holes centered in derived tabs, M4 screw clearance]
protected_interfaces: [outer length, inner body span, tab thickness, step height, M4 clearance holes]
low_confidence_zones: [overall width, bridge width, screw center locations, screw head recesses, underside molded details]
stl_export_status: export and mesh QA passed
preview_export_status: iso/front/side rendered
verification_status: export verified; physical fit NOT VERIFIED
future_3mf_status: not created
---

# Project Manifest

## Project Summary

Initial OpenSCAD reconstruction of `battery_strap_holder` from hard caliper dimensions, PETG/0.6 mm profile offsets, and M4 hardware-library clearance.

## Target Part

Battery strap holder / retainer bracket.

## Reused Parts

Existing mounting surface, strap path, and assumed M4 screws.

## Not-Modeled Items

Battery, surrounding compartment, strap, screw heads, washers, and unmeasured underside features.

## References

### Authoritative

- 74.0 mm total outer length from `20260524_173041.jpg`
- 50.2 mm inner body span from `20260524_173058.jpg`
- 7.1 mm main offset step height from `20260524_173128.jpg`
- 4.0 mm tab sub-thickness from `20260524_173112.jpg`

### Supporting

- `standards/hardware_library.scad`
- `standards/printer_material_profiles.json`
- `standards/GEOMETRY_FEEDBACK_LOOP.md`

## Anchor Dimensions

- total outer length Y: 74.0 mm
- inner body span Y: 50.2 mm
- tab length per side: 11.9 mm
- tab thickness: 4.0 mm
- main step height: 7.1 mm

## Protected Interfaces

- M4 clearance holes
- end-tab boundaries
- measured length and height envelope

## Measured Versus Inferred Dimensions

Measured values are the four caliper dimensions listed above. Width, bridge width, hole center placement, and screw-head recess geometry are inferred for v01.

## Artifact Checklist

- [x] source exists
- [x] STL export exists
- [x] notes exist
- [x] manifest exists
- [x] required previews exist
- [x] review report exists
- [x] comparison log exists when reconstruction

## Verification Notes

`scripts/verify_project.py --project projects\battery_strap_holder --task-mode reference_based_reconstruction --version v01` passed. Physical fit remains unverified until a print is measured.
