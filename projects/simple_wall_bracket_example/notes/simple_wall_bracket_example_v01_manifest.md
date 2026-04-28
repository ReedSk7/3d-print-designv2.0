---
project_stem: simple_wall_bracket_example
version: v01
task_mode: original_product_design
status: verified example
source_file: source/simple_wall_bracket_example_v01.scad
export_file: exports/simple_wall_bracket_example_v01.stl
preview_files:
  - previews/simple_wall_bracket_example_v01_iso.png
  - previews/simple_wall_bracket_example_v01_front.png
  - previews/simple_wall_bracket_example_v01_side.png
notes_file: notes/simple_wall_bracket_example_v01_notes.md
review_report: notes/simple_wall_bracket_example_v01_review_report.md
authoritative_references:
  - none, original design example
supporting_references:
  - standards/FDM_PRINTABILITY_CHECKS.md
measured_dimensions: []
inferred_dimensions:
  - overall dimensions are design parameters, not measured replacement-part dimensions
protected_interfaces:
  - screw clearance holes
  - screw head pockets
  - wall mounting face
low_confidence_zones:
  - screw fit must be tuned to actual screw and printer
stl_export_status: success
preview_export_status: success
verification_status: verified
future_3mf_status: not created
---

# Project Manifest

## Project Summary

Parametric wall bracket smoke-test project for the reconstruction-first OpenSCAD workflow.

## Target Part

Simple wall bracket example.

## Reused Parts

None.

## Not-Modeled Items

- screws
- wall anchors
- supported object or load case

## References

### Authoritative

None. This is an original design example.

### Supporting

- `standards/FDM_PRINTABILITY_CHECKS.md`
- `standards/HARDWARE_LIBRARY.md`

## Anchor Dimensions

- width: 84 mm
- depth: 58 mm
- height: 64 mm
- wall thickness: 4.0 mm
- screw clearance diameter: 4.7 mm

## Protected Interfaces

- screw clearance holes
- screw head pockets
- wall mounting face

## Measured Versus Inferred Dimensions

### Measured

None.

### Inferred

All dimensions are original design parameters. Screw and head clearances are starter values.

## Known Assumptions

- PETG is the default material for this functional example.
- #8 screw clearance starter may need printer-specific tuning.
- This example is not load-rated.

## Low-Confidence Zones

- actual screw head fit
- actual wall anchor choice
- real load capacity

## Artifact Checklist

- [x] source exists
- [x] STL export exists
- [x] notes exist
- [x] manifest exists
- [x] required previews exist
- [x] review report exists
- [ ] comparison log exists when reconstruction

## Verification Notes

- `validate_scad.py` passed.
- `export_stl.py` created the STL.
- `export_preview.py` created iso, front, and side previews.
- `check_project_outputs.py` passed.
- `trimesh` loaded the STL as watertight with extents `84.000 x 58.000 x 64.000 mm`.

## Next Actions

Create `v02` before modifying geometry.
