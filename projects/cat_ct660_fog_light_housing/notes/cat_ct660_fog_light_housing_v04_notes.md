# CAT CT660 Fog Light Housing v04 Notes

- Project stem: `cat_ct660_fog_light_housing`
- Version: `v04`
- Task mode: `reference_based_reconstruction`
- Source file: `projects/cat_ct660_fog_light_housing/source/cat_ct660_fog_light_housing_v04.scad`
- Exported STL filename: `projects/cat_ct660_fog_light_housing/exports/cat_ct660_fog_light_housing_v04.stl`
- STL export status: Success. Exported with OpenSCAD 2021.01 on 2026-04-19. Verified with `trimesh` as `watertight=True` and a single connected body.
- Best-faith statement: This is a best-faith reconstruction from user photos for a CAT CT660 fog light housing. The separate OEM housing part number is not confirmed in this pass and is not claimed here.

## Target Part

- Exact target part: Single molded plastic bumper fog light housing / bucket for a CAT CT660 vocational dump truck.
- Truck platform context: CAT CT660 built on a Navistar / International-produced truck platform.
- Modeled intent: The specific housing shown in the user photos, not a generic fog lamp bezel.

## What Is Reused

- Reused the existing project folder and versioned workflow under `projects/cat_ct660_fog_light_housing/`.
- Reused prior `v02` and `v03` files only as supporting input for sanity checks and change tracking.
- Reused only geometry ideas that still matched the user photos. `v04` is a fresh rebuild, not a blind carry-forward of `v03`.

## What Is Not Modeled

- Fog lamp
- Bulb
- Wiring
- Truck bumper
- Unrelated brackets
- Decorative texture beyond simple printable surfaces

## Authoritative References

1. User photos of the actual broken part in `references/measured/cat_ct660_fog_light_housing/3520.jpg` and `3521.jpg`
2. User-provided vehicle identification: CAT CT660
3. User-provided locked overall width of about 10 inches, applied as `254 mm`

## Supporting References

- Prior `v02` and `v03` CAD and STL files in the same project folder
- User-supplied installed/context images in `references/measured/cat_ct660_fog_light_housing/`
- Per the task brief, CAT / Navistar platform context and public fog lamp listings were treated as supporting only. No public reference was allowed to overrule the user photos.

## Trust Order Applied

1. User photos of the actual part
2. User vehicle identification: CAT CT660
3. User width anchor: `254 mm`
4. Prior local versions only where they still matched the photos
5. All other context as non-governing support

## Locked Dimensions

- `overall_width = 254 mm`
- `overall_height = 150 mm`
- `overall_depth = 116 mm` for the main shell body
- `collar_outer_diameter = 106 mm`
- `collar_inner_diameter = 87 mm`
- `collar_front_projection = 11 mm`
- `wall_thickness = 3.5 mm`
- `front_flange_width = 7.5 mm`
- `collar_center_x = 68 mm`
- `collar_center_y = 92 mm from top edge`

## Photo-Derived Starter Dimensions

- `overall_width = 254 mm`
- `overall_height = 150 mm`
- `overall_depth = 116 mm`
- `collar_outer_diameter = 106 mm`
- `collar_inner_diameter = 87 mm`
- `collar_front_projection = 11 mm`
- `wall_thickness = 3.5 mm`
- `front_flange_width = 7.5 mm`
- `collar_center_x = 68 mm from left edge`
- `collar_center_y = 92 mm from top edge`
- `main_stud_positions = [[31, 103], [213, 27], [231, 109]]`
- `small_collar_boss_angles_deg = [135, 35, 235]`

## Protected Interfaces

- Overall front opening silhouette
- Collar inner diameter
- Collar outer diameter
- Collar placement
- Collar seating lip intent
- Three main stud center locations
- Bumper-contact outer contour intent
- Overall asymmetry, especially the deeper right side

## Reinforced Zones

- Rear main stud bases with molded boss pads and gussets
- Rear panel rib pairs on the non-interface panel zones
- Collar-to-shell blend regions on the upper-right and lower-right side of the collar
- Small collar-boss roots with short molded blends into the collar ring

## Low-Confidence Zones

- Exact bumper-contact curvature through the rear upper shell
- Exact wall taper through depth
- Exact stud shaft length, washer size, and real hardware construction
- Exact small collar-boss diameter and hole size
- Exact collar seating step diameter and depth
- Exact molded draft angles

## Comparison Status

- Compared manually against `3520.jpg`, `3521.jpg`, and the installed/context images in `references/measured/cat_ct660_fog_light_housing/`
- Overall silhouette: revised from the broader `v03` body to a narrower, shorter swept trapezoid that better matches the user brief
- Collar placement: moved left and lower relative to `v03` to match the photo-derived anchors
- Asymmetry: preserved; the ring remains left-shifted and the right wall stays deeper and more vertical
- Right-side cavity depth: intentionally increased versus `v03`
- Stud layout: changed to the three non-rectangular photo-driven centers from the user brief
- Collar-boss presence: three smaller molded collar-area bosses added from the supplied angle list
- Bumper-matching contour intent: modeled with blended hull transitions and local contour pads rather than a single cylindrical shortcut
- Current status: no additional mismatch was obvious enough from the available photos to justify another export pass before handoff

## Verified Mesh And Build-Volume Check

- Verified STL mesh bbox: `254.0 x 141.8 x 149.993 mm`
- BBox note: the `141.8 mm` depth includes the `11 mm` forward collar projection plus the provisional rear boss/stud stack
- `trimesh` verification: `watertight=True`
- Connected body count: `1`
- Bambu Lab P2S build-volume check: passes as a single-piece part inside `256 x 256 x 256 mm`
- Margin note: the `254.0 mm` width is very close to the machine limit, so bed centering and skirt/brim choices need to stay conservative

## Print Orientation

- Recommended orientation: rear mounting face down with the front opening facing up
- Reason: this preserves the front opening perimeter and collar geometry while keeping the large rear panel as the main datum
- Caution: the rear stud stubs will need support/interface management in this orientation

## Support Plan

- Supports allowed inside the cavity and under the rear boss/stud overhangs
- Avoid support contact on the visible front opening perimeter where possible
- Keep collar and front lip interfaces clean; do not thin those protected areas to save support

## What Changed From v03 To v04

- Rebuilt the front silhouette around the locked `254 x 150 mm` user brief instead of the larger `v03` envelope
- Increased the effective total depth by adding the requested `11 mm` collar projection and a deeper right-side cavity
- Shifted the collar from the more centered `v03` placement to the user-provided left offset
- Replaced the `v03` four-boss collar pattern with the three-boss pattern requested for `v04`
- Replaced the prior stud layout with the exact three photo-derived center locations supplied in the brief
- Changed the shell from a more generic rounded-rectangle feel to a more swept trapezoidal mouth with blended exterior transitions
- Tightened the export to a verified `254.0 mm` width after mesh checking

## Remaining Dimensions Needing Caliper Confirmation

- Exact bumper-contact curvature on the rear upper shell
- Exact collar seating lip diameter and step depth
- Exact stud shaft length and boss washer geometry
- Exact small collar-boss outer diameter and pilot-hole size
- Exact local wall taper and draft around the deeper right cavity

## Additional Notes

- No preview PNG files were generated in this pass because the user explicitly requested a non-visual task.
- Public OEM certainty is not claimed. This stays a best-faith local reconstruction from the user photos and supplied CAT CT660 context.
