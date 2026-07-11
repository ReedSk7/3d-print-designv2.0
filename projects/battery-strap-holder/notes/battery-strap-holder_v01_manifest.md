---
project_stem: battery-strap-holder
version: v01
task_mode: reference_based_reconstruction
status: test-fit
source_file: projects/battery-strap-holder/source/battery-strap-holder_v01.scad
export_file: projects/battery-strap-holder/exports/battery-strap-holder_v01.stl
preview_files:
  - projects/battery-strap-holder/previews/battery-strap-holder_v01_iso.png
  - projects/battery-strap-holder/previews/battery-strap-holder_v01_front.png
  - projects/battery-strap-holder/previews/battery-strap-holder_v01_side.png
notes_file: projects/battery-strap-holder/notes/battery-strap-holder_v01_notes.md
review_report: projects/battery-strap-holder/notes/battery-strap-holder_v01_review_report.md
authoritative_references:
  - measured dimensions supplied by user
supporting_references:
  - uploaded photos 155.jpg, 156.jpg, 157.jpg, 158.jpg
measured_dimensions:
  - total_length_y 74.1 mm
  - total_width_x 11.0 mm
  - total_height_z 7.0 mm
  - hole_diameter 4.8 mm
  - hole_center_offset_from_end 5.8 mm
inferred_dimensions:
  - hidden underside shape
  - transition radii
  - screw head recess omitted
protected_interfaces:
  - screw hole diameter
  - screw hole spacing
  - mounting bottom faces
  - strap clearance gap
low_confidence_zones:
  - hidden underside geometry
  - exact molded edge radii
  - screw head style
stl_export_status: verified
preview_export_status: verified
verification_status: verified
future_3mf_status: not created
---

# Project Manifest

## Project Summary

Parametric OpenSCAD replacement battery strap holder with exact, heavy-duty, and fit-test variants.

## Target Part

Small plastic strap retainer bracket with two screw-down end bosses and a raised center bridge for the battery strap.

## Reused Parts

Existing battery compartment, strap, screw positions, and likely existing screws.

## Not-Modeled Items

Battery box, strap, screws, surrounding compartment, countersink/counterbore detail, and hidden molded underside detail.

## References

### Authoritative

Measured dimensions supplied by the user.

### Supporting

Uploaded photos used as visual reference only.

## Anchor Dimensions

- Overall size: 74.1 x 11.0 x 7.0 mm.
- Hole diameter: 4.8 mm.
- Hole center offset from each end: 5.8 mm.
- Derived hole center spacing: 62.5 mm.
- Strap gap: 3.5 mm.

## Protected Interfaces

- Screw-hole diameter and spacing.
- Flat screw-down bottom faces.
- Strap pass-through clearance.

## Measured Versus Inferred Dimensions

### Measured

- Overall length, width, height.
- Screw-hole diameter.
- Hole offset from end.

### Inferred

- Hidden underside shape.
- Small transition radii and edge softening.
- Lack of screw head recess.

## Known Assumptions

- The functional replacement should prioritize strength and fit over exact molded cosmetic detail.
- PETG or ASA is preferred for heat and compartment durability.

## Low-Confidence Zones

- Hidden underside detail.
- Exact screw head geometry.
- Final strap compression clearance.

## Artifact Checklist

- [x] source exists
- [x] STL export exists
- [x] notes exist
- [x] manifest exists
- [x] required previews exist
- [x] review report exists
- [x] comparison log exists when reconstruction

## Verification Notes

OpenSCAD STL exports, previews, mesh sanity checks, and the repo output checker completed successfully.

## Next Actions

Print the v03 fit-test plate and confirm screw alignment before printing the final holder.
