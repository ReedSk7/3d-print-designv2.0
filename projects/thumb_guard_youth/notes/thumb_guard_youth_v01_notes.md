# Original Design Notes

## task mode

`original_product_design`

## goal

Create one clean parametric OpenSCAD v01 model for a youth baseball thumbguard inspired by commercial thumb protector products in the attached images, while remaining an original design and not a brand copy.

## constraints

- OpenSCAD is the editable source of truth.
- FDM-first geometry with a flat print face.
- TPU-first design intent, but printable in PLA or PETG for test fitting.
- One baseline model only for v01.
- Branding and text stay off.
- The provided overall envelope and qualitative image references drive the silhouette.
- Thumb opening fit values are estimated only and must be called out as such.

## chosen concept

One asymmetric thumbguard with:

- an oval thumb ring
- a smooth ring-to-body transition
- a palm-side protective contact pad
- soft external rounds and no knife edges
- a flat back face for support-light printing and easy test fitting

The model is inspired by the attached commercial references for overall use case and silhouette only. The ring geometry and bat-contact pad are rebuilt as an original parametric form.

## key parameters

- `overall_length = 82`
- `overall_width = 52`
- `overall_thickness = 15`
- `thumb_opening_major = 22`
- `thumb_opening_minor = 18`
- `ring_wall = 5`
- `ring_width = 14`
- `ring_to_pad_offset = 22`
- `pad_contact_width = 36`
- `pad_contact_length = 44`
- `pad_center_thickness = 12`
- `pad_edge_thickness = 5`
- `transition_blend_radius = 10`
- `outer_edge_round = 2`

Protected interfaces for this v01:

- thumb opening oval
- inner ring comfort surface
- ring-to-body transition
- palm-side bat-contact guard surface

## print orientation

Print flat on the broad back face with the outer guard surface facing up.

## support plan

The v01 shape is intended to print without supports in the default orientation. The back face is kept flat and the outer surface is sloped and rounded rather than sharply undercut.

## known risks

- The thumb opening may be too tight for a gloved 10U thumb.
- The thumb opening may be too loose and rotate during use.
- The guard may still feel too bulky around the bat handle.
- The palm-side contact surface is estimated from photos, not hand measurements.
- The side wing flare is a low-confidence area because it is partly hidden in the references.

## dimensions used

Overall envelope reference:

- overall length `82 mm`
- overall width `52 mm`
- overall thickness `15 mm`

Estimated v01 fit values:

- thumb opening major `22 mm`
- thumb opening minor `18 mm`
- ring wall `5 mm`
- ring width `14 mm`
- ring-to-pad offset `22 mm`
- pad contact width `36 mm`
- pad contact length `44 mm`
- pad center thickness `12 mm`
- pad edge thickness `5 mm`

## estimated vs verified dimensions

- Reference-provided target dimensions: overall envelope target `82 x 52 x 15 mm` from the provided spec image. These were not physically measured in this workflow.
- Estimated dimensions: thumb opening dimensions, internal comfort surface fit, ring/body transition bulk, exact pad curvature, glove allowance, and side flare proportions.
- Verified generated artifact dimensions from local STL mesh inspection: `49.896 x 80.994 x 15.000 mm`.

## exported STL filename

`exports/thumb_guard_youth_v01.stl`

## STL export status

Success. `exports/thumb_guard_youth_v01.stl` exported locally from OpenSCAD and loaded successfully in `trimesh` as a watertight mesh.

## what was generated

- `source/thumb_guard_youth_v01.scad`
- `exports/thumb_guard_youth_v01.stl`
- `previews/thumb_guard_youth_v01_iso.png`
- `previews/thumb_guard_youth_v01_front.png`
- `previews/thumb_guard_youth_v01_side.png`
- `previews/thumb_guard_youth_v01_top.png`

## what failed

No local generation failures in this workflow. Real-world fit remains unverified because no child thumb, glove, or bat-handle measurements were captured.

## recommended next measurements for v02

- gloved thumb major and minor circumference-derived fit targets
- bare thumb and gloved thumb thickness at the ring location
- desired glove compression allowance
- actual bat handle contact zone on the thumb during grip
- preferred pad width and side flare after first physical swing test

## next actions

- Print a TPU test part or ring-only fit coupon before game use.
- Measure the actual gloved thumb opening needed for the player.
- Check real bat-grip pressure contact and revise the guard curvature for v02.
- Adjust side flare and ring fit after first physical batting test.
