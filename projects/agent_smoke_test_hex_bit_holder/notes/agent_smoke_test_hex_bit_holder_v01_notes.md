# Original Design Notes

## Task Mode

`original_product_design`

## Goal

Create a compact wall-mounted holder for six standard 1/4 inch hex screwdriver bits, using the repo workflow from source creation through validation, STL export, preview export, and output verification.

## Constraints

- printer: Bambu Lab P2S
- material: PETG
- bed size: 256 x 256 x 256 mm
- strength needs: light-duty shop storage
- heat exposure: normal indoor/shop use
- outdoor exposure: not intended

## Chosen Concept

One compact rectangular wall holder with six vertical hex pockets, two screw mounting holes, optional countersink geometry, reinforced screw bosses, and a raised `BITS` label on the front face.

## Key Parameters

- overall dimensions: about 90 x 22 x 45 mm
- wall thickness: 3 mm minimum target
- bit count: 6
- nominal bit size: 6.35 mm across flats
- pocket clearance: 0.35 mm
- screw spacing: 65 mm
- screw diameter: 4.5 mm
- countersink: enabled, adjustable
- tolerance profile: slightly loose pocket fit

## Print Orientation

Print flat with the bottom/base face against the bed. The bit pockets open upward in model coordinates, so they should not require support.

## Support Plan

No supports preferred. Screw holes are small horizontal bridge features if printed pocket-up; tune orientation if the screw holes need cleaner roundness.

## Known Risks

- Actual screwdriver bit shank dimensions vary by manufacturer.
- Horizontal screw holes may print slightly oval without support.
- OpenSCAD text availability depends on the local font stack, but this source exported successfully during the smoke test if marked verified below.

## Exported STL Filename

`projects/agent_smoke_test_hex_bit_holder/exports/agent_smoke_test_hex_bit_holder_v01.stl`

## STL Export Status

Verified. `scripts/export_stl.py` created the STL in this environment.

## Preview Export Status

Verified. `scripts/export_preview.py` created the iso PNG preview in this environment.

## Mesh Verification

`trimesh` loaded the exported STL as `watertight=True` with extents `90.000 x 24.400 x 45.000 mm`.

## Next Actions

- Test-fit actual bits and screws before production use.
- Create `v02` before changing geometry.
