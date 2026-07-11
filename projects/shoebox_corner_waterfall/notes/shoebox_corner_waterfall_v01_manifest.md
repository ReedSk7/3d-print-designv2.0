---
project_stem: shoebox_corner_waterfall
version: v01
task_mode: original_product_design
status: verified
source_file: source/shoebox_corner_waterfall_source_v01.scad
repo_wrapper_source_file: source/shoebox_corner_waterfall_v01.scad
export_file: exports/shoebox_corner_waterfall_v01.stl
variant_export_files: [exports/shoebox_corner_waterfall_simple_v01.stl, exports/shoebox_corner_waterfall_detailed_v01.stl]
preview_files: [previews/shoebox_corner_waterfall_v01_iso.png]
notes_file: notes/shoebox_corner_waterfall_v01_notes.md
review_report: notes/shoebox_corner_waterfall_v01_review_report.md
authoritative_references: [user request]
supporting_references: [repo FDM printability defaults]
measured_dimensions: [height 120 mm requested, wall-side width 70 mm requested, center protrusion 45 mm requested, base footprint about 70 mm x 70 mm requested]
inferred_dimensions: [4 mm glue panels, 6 mm base, 1.2 mm minimum raised detail, decorative rock layout]
protected_interfaces: [flat X=0 back face, flat Y=0 back face, flat bottom]
low_confidence_zones: [actual shoebox internal corner squareness and wall thickness not measured]
stl_export_status: verified
preview_export_status: verified
verification_status: verified
future_3mf_status: not created
---

# Project Manifest

## Project Summary

One-piece FDM-printable shoebox diorama corner insert with a rocky cliff, vertical raised waterfall, shallow pool, ripple rings, and splash details. The editable source generates both simple and detailed variants.

## Target Part

Decorative waterfall corner insert for the inside corner of a shoebox diorama.

## Reused Parts

Shoebox walls are reused as the backing surfaces after gluing.

## Not-Modeled Items

The shoebox, terrain around the insert, paint, glue, plants, figures, and other diorama scenery are not modeled.

## References

### Authoritative

- User-provided dimensional and design requirements in the request.

### Supporting

- Repo FDM printability defaults for 0.4 mm nozzle details.

## Anchor Dimensions

- Overall height: 120 mm.
- Wall-side width: 70 mm per side.
- Maximum central protrusion from either wall: 45 mm.
- Base footprint: approximately 70 mm x 70 mm.
- Minimum raised detail: 1.2 mm.

## Protected Interfaces

- Flat back face at X=0.
- Flat back face at Y=0.
- Flat bottom for bed contact and diorama placement.

## Measured Versus Inferred Dimensions

### Measured

No physical shoebox was measured in this environment.

### Inferred

- Back glue panel thickness set to 4 mm.
- Base thickness set to 6 mm.
- Rock layer and water detail layout are decorative and inferred from the requested craft style.

## Known Assumptions

- "Depth from corner: 45 mm max" is interpreted as maximum protrusion away from either wall at the visible front, while keeping 70 mm contact length along each wall.
- PLA is acceptable for an indoor painted craft/diorama piece.

## Low-Confidence Zones

- Real shoebox corners may not be perfectly square.
- Thin cardboard walls may bow if too much glue is used; dry fit before final gluing.

## Artifact Checklist

- [x] source exists
- [x] STL export exists
- [x] notes exist
- [x] manifest exists
- [x] required previews exist
- [x] review report exists
- [ ] comparison log exists when reconstruction

## Verification Notes

- `validate_scad.py` passed for the editable source and repo wrapper source.
- Simple STL exported and loaded watertight at 70.00 x 70.00 x 120.00 mm.
- Detailed STL exported and loaded watertight at 70.00 x 70.00 x 120.00 mm.
- Repo-standard detailed STL exported and loaded watertight at 70.00 x 70.00 x 120.00 mm.
- `check_project_outputs.py` passed for `original_product_design` `v01`.

## Next Actions

Dry fit against the target shoebox corner before final paint and glue.
