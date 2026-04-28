# Original Design Notes

## Task Mode

`original_product_design`

## Goal

Create a simple parametric right-angle wall bracket that exercises the repo workflow with editable OpenSCAD source, screw holes, adjustable clearances, reinforcement ribs, STL export, previews, and artifact verification.

## Constraints

- printer: Bambu Lab P2S
- material: PETG
- bed size: 256 x 256 x 256 mm
- strength needs: light-duty example bracket only, not load-rated
- heat exposure: normal indoor conditions
- outdoor exposure: not intended

## Chosen Concept

Single L-style wall bracket with a horizontal shelf plate, vertical wall plate, two triangular reinforcement ribs, two wall screw holes, and two shelf screw holes.

## Key Parameters

- overall dimensions: 84 x 58 x 64 mm
- wall thickness: 4.0 mm
- screw size: adjustable #8 starter clearance
- screw clearance diameter: 4.7 mm
- screw head pocket: adjustable counterbore or countersink
- tolerance profile: normal slip fit, 0.3 mm clearance
- split_part mode: supports left or right half export when requested

## Print Orientation

Print with the wall plate flat on the bed and ribs rising in Z. This preserves the flat back face and keeps the ribs printable without supports.

## Support Plan

Designed for no supports in the default orientation.

## Known Risks

- Screw fit is a starter value and should be test-fit on the target printer.
- The bracket is a workflow example and is not load-rated.
- Counterbore depth and screw head diameter must be adjusted for the actual screw.

## Exported STL Filename

`projects/simple_wall_bracket_example/exports/simple_wall_bracket_example_v01.stl`

## STL Export Status

Verified. `scripts/export_stl.py` created the STL in this environment.

## Preview Export Status

Verified. `scripts/export_preview.py` created iso, front, and side PNG previews in this environment.

## Mesh Verification

`trimesh` loaded the STL as `watertight=True` with extents `84.000 x 58.000 x 64.000 mm`.

## Next Actions

- Use this as the smoke-test project for script and workflow checks.
- Create `v02` before changing geometry.
