# Reconstruction Notes

## Task Mode

`reference_based_reconstruction`

## Geometry Contract

- project stem: `battery_strap_holder`
- target material profile: PETG
- target nozzle: 0.6 mm
- calibration source: `standards/printer_material_profiles.json` and `standards/GEOMETRY_FEEDBACK_LOOP.md`
- calibrated hole compensation used for PETG/0.6 mm: +0.15 mm

## Target Part

Initial parametric replacement battery strap holder / retainer bracket.

## What Is Reused

- existing battery compartment or mounting surface
- existing battery strap path
- assumed M4 mounting screws

## What Is Not Modeled

- surrounding battery box
- battery strap
- screw heads or washers beyond the M4 clearance holes
- hidden underside molded details not measured

## Authoritative References

- `20260524_173041.jpg`: total outer length 74.0 mm
- `20260524_173058.jpg`: inner body span between tabs 50.2 mm
- `20260524_173128.jpg`: main offset step height 7.1 mm
- `20260524_173112.jpg`: tab sub-thickness 4.0 mm

The image files were referenced by the user but were not found in the current repo search. The listed caliper values are treated as authoritative user-provided measurements.

## Supporting References

- PETG/0.6 mm calibration row in `standards/GEOMETRY_FEEDBACK_LOOP.md`
- M4 clearance functions in `standards/hardware_library.scad`

## Anchor Dimensions

- total outer length Y: 74.0 mm
- inner body span Y: 50.2 mm
- derived tab length per end: 11.9 mm
- main offset step height Z: 7.1 mm
- tab sub-thickness Z: 4.0 mm

## Protected Interfaces

- overall length envelope
- tab boundary positions from the 50.2 mm inner span
- 4.0 mm tab thickness
- 7.1 mm step height
- M4 clearance holes using hardware-library + PETG/0.6 calibration

## Inferred Dimensions

- overall width X: 11.0 mm
- center bridge width X: 8.5 mm
- hole centers: centered in each derived end tab
- no counterbore/countersink in v01 because screw-head geometry was not supplied

## Comparison Status

- bbox: expected 74.0 mm Y length, 11.0 mm inferred X width, 7.1 mm Z height
- front silhouette: two end tabs with raised center bridge
- side silhouette: 4.0 mm tabs and 7.1 mm stepped bridge
- top silhouette: rounded tab ends, narrower bridge, two M4 clearance holes
- critical local features: M4 holes are parametric and calibrated, but hole positions are inferred from tab centers

## Pass/Fail On Critical Features

- PASS: authoritative length, inner span, tab thickness, and step height are mapped to named variables.
- PASS: M4 clearance hole diameter comes from `clearance_hole_d()` and calibrated PETG/0.6 mm profile data.
- NOT PHYSICALLY VERIFIED: printed fit and screw alignment have not been tested.

## Print Orientation

Initial orientation: flat on bottom tab faces. The raised bridge is a long span; support or a rotated print orientation may be needed depending on slicer results.

## Support Plan

Use slicer preview before printing. If bridge underside is unsupported, print a fit-test or use supports under the central bridge.

## Next Revision Actions

- Measure overall part width.
- Measure screw center distance or confirm holes are centered in end tabs.
- Measure screw-head recess if present.
- Print v01 fit-test and record actual hole/length/height deviations in `standards/GEOMETRY_FEEDBACK_LOOP.md`.

## Exported STL Filename

`projects/battery_strap_holder/exports/battery_strap_holder_v01.stl`

## STL Export Status

`EXPORT + MESH QA PASSED`: `scripts/verify_project.py` exported the STL and `scripts/mesh_quality_check.py` reported watertight mesh, consistent winding, one connected body, and positive volume.

## Preview Export Status

`RENDERED`: iso, front, and side previews were rendered by `scripts/verify_project.py`.

## Future 3MF Status

`not created`
