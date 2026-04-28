---
project_stem: agent_smoke_test_hex_bit_holder
version: v01
task_mode: original_product_design
status: verified smoke test
source_file: source/agent_smoke_test_hex_bit_holder_v01.scad
export_file: exports/agent_smoke_test_hex_bit_holder_v01.stl
preview_files:
  - previews/agent_smoke_test_hex_bit_holder_v01_iso.png
notes_file: notes/agent_smoke_test_hex_bit_holder_v01_notes.md
review_report:
authoritative_references:
  - none, original product design
supporting_references:
  - standards/FDM_PRINTABILITY_CHECKS.md
  - standards/HARDWARE_LIBRARY.md
measured_dimensions: []
inferred_dimensions:
  - 6.35 mm nominal bit size
  - 0.35 mm pocket clearance
  - exported STL extents: 90.000 x 24.400 x 45.000 mm
protected_interfaces:
  - six hex bit pockets
  - two screw mounting holes
  - countersink openings when enabled
low_confidence_zones:
  - actual bit brand fit
  - actual screw head fit
  - horizontal screw hole roundness
stl_export_status: success
preview_export_status: success
verification_status: verified
future_3mf_status: not created
---

# Project Manifest

## Project Summary

Compact wall-mounted holder for six standard 1/4 inch hex screwdriver bits.

## Target Part

`agent_smoke_test_hex_bit_holder_v01`

## Reused Parts

None.

## Not-Modeled Items

- screwdriver bits
- screws
- wall anchors

## References

### Authoritative

None. This is an original product design smoke test.

### Supporting

- `standards/FDM_PRINTABILITY_CHECKS.md`
- `standards/HARDWARE_LIBRARY.md`

## Anchor Dimensions

- width: about 90 mm
- height: about 45 mm
- depth: about 22 mm
- screw spacing: 65 mm
- pocket nominal across-flats size: 6.35 mm
- pocket clearance: 0.35 mm

## Protected Interfaces

- bit pocket across-flats clearance
- screw hole diameter
- countersink diameter and depth

## Measured Versus Inferred Dimensions

### Measured

None.

### Inferred

- bit fit based on 6.35 mm nominal size plus 0.35 mm clearance
- screw fit based on a 4.5 mm starter hole
- countersink based on a 9.5 mm starter head clearance

## Known Assumptions

- PETG is appropriate for indoor/shop use.
- Bit pockets are intentionally loose for easy removal.
- Actual bit and screw dimensions should override these starter values for production use.

## Low-Confidence Zones

- exact bit fit across brands
- screw head fit
- horizontal screw-hole print quality

## Artifact Checklist

- [x] source exists
- [x] STL export exists
- [x] notes exist
- [x] manifest exists
- [x] required previews exist
- [ ] review report exists
- [ ] comparison log exists when reconstruction

## Verification Notes

- `validate_scad.py` passed.
- `export_stl.py` created `exports/agent_smoke_test_hex_bit_holder_v01.stl`.
- `export_preview.py` created `previews/agent_smoke_test_hex_bit_holder_v01_iso.png`.
- `trimesh` loaded the exported STL as `watertight=True` with extents `90.000 x 24.400 x 45.000 mm`.

## Next Actions

Run a physical test fit with actual bits and mounting screws before production use.
