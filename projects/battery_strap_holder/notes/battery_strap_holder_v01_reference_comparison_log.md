# Reference Comparison Log

## Date/Revision

2026-05-29 / v01

## Current Version

`battery_strap_holder_v01`

## References Used

- Authoritative: user-provided caliper values correlated to `20260524_173041.jpg`, `20260524_173058.jpg`, `20260524_173128.jpg`, and `20260524_173112.jpg`.
- Supporting: PETG/0.6 mm hole calibration in `standards/GEOMETRY_FEEDBACK_LOOP.md`.
- Supporting: M4 hardware functions in `standards/hardware_library.scad`.

## BBox Comparison

- target measured Y length: 74.0 mm
- target measured Z height: 7.1 mm
- exported mesh extents: 11.000 x 74.000 x 7.100 mm
- status: PASS for measured Y/Z envelope; X width remains inferred.

## Silhouette Comparison

- front: raised center bridge over lower end-tab geometry.
- side: 4.0 mm tabs with 7.1 mm total step height.
- top: rounded end tabs, narrower bridge, two M4 clearance holes.

## Critical Feature Comparison

- tabs: derived from 74.0 mm outer length and 50.2 mm inner span, giving 11.9 mm per tab.
- step: 7.1 mm total step height with 4.0 mm tab sub-thickness.
- holes: M4 normal clearance from hardware library with PETG/0.6 mm calibrated compensation.

## Mismatches / Unknowns

- overall part width is inferred at 11.0 mm.
- bridge width is inferred at 8.5 mm.
- screw centers are inferred as centered in each derived end tab.
- screw-head recess/counterbore geometry is not modeled because no measurement was supplied.

## Confidence Level

Medium for the measured length/span/height geometry. Low for width, screw-center placement, and hidden underside/recess details.
