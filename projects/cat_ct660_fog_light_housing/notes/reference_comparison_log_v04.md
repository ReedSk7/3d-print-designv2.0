# Reference Comparison Log

## date/revision

- Date: 2026-04-19
- Revision: `v04`

## current version

- `projects/cat_ct660_fog_light_housing/source/cat_ct660_fog_light_housing_v04.scad`
- `projects/cat_ct660_fog_light_housing/exports/cat_ct660_fog_light_housing_v04.stl`

## reference used

- `references/measured/cat_ct660_fog_light_housing/3520.jpg`
- `references/measured/cat_ct660_fog_light_housing/3521.jpg`
- Installed/context images in `references/measured/cat_ct660_fog_light_housing/`
- `v03` SCAD and STL for change tracking only, not as governing geometry

## bbox comparison

- User-locked shell width target: `254 mm`
- Verified `v04` STL bbox: `254.0 x 141.8 x 149.993 mm`
- Verified `v03` STL bbox: `264.82 x 118.30 x 158.845 mm`
- `v04` is narrower than `v03`, deeper overall because of the collar projection plus rear hardware stack, and closer to the user-specified `254 x 150 mm` front-view envelope
- The main shell body still follows the `116 mm` photo-derived depth target, while the verified STL depth grows because the model includes a forward collar projection and rear mounting features

## silhouette comparison

- Front silhouette: revised from the broader `v03` rounded-rectangle tendency to a tighter swept trapezoid with a long shallow top sweep and a flatter lower edge
- Side silhouette: revised to emphasize the deeper right-side cavity and the collar projection instead of the shallower `v03` body
- Top silhouette: remains asymmetric and biased to the right-side depth, consistent with the user-photo interpretation
- `compare_mesh.py` against `v03` reported notable silhouette deltas in front, side, and top views, which is expected because `v04` intentionally re-anchored the model to the new brief

## critical feature comparison

- Collar placement: moved to `collar_center_x = 68 mm` and `collar_center_y = 92 mm from top`
- Collar diameters: kept at `106 mm OD` and `87 mm ID`
- Collar seating lip: included as a stepped internal rebate; exact size remains low confidence
- Main studs: placed at `[[31, 103], [213, 27], [231, 109]]` from the user brief
- Small collar bosses: included at `[135, 35, 235]` degrees
- Right-side cavity: intentionally deeper and more vertical than the left side
- Bumper-contact contour: built from staged hull transitions and contour pads instead of a single-radius subtraction

## mismatches found

- Exact bumper curvature is still inferred, not directly measured
- Exact molded draft angles remain unconfirmed
- Exact small collar-boss size and hole size remain assumed
- Exact stud shaft length and washer geometry remain assumed
- No additional obvious silhouette mismatch was strong enough in the available photos to justify another geometry rewrite before export

## corrections planned

- No additional pre-export correction planned in this pass
- Next revision should be driven by caliper measurements or more square-on photos rather than more freehand inference

## confidence level

- Moderate confidence in front silhouette, collar placement, asymmetry, and main stud-center layout
- Moderate confidence that the right-side cavity intent is closer to the user photos than `v03`
- Lower confidence in bumper-contact curvature, draft angles, small collar-boss sizing, and exact stud hardware geometry
