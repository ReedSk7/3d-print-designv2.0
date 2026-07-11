# Original Design Notes

## task mode

`original_product_design`

## goal

Retarget the organizer print workflow so each printable STL section stays within a `245 x 245 x 40 mm` build volume unless future measured geometry forces a smaller section. This version keeps the v01 organizer layout intent but changes the split strategy for a smaller printer.

## constraints

- OpenSCAD remains the editable source of truth.
- `v01` stays intact. This printer-fit change is a new `v02`.
- Keep the organizer measurement-gated. Real drawer and tool fit is still unverified.
- Each printable section must target `<= 245 x 245 x 40 mm`.
- Preserve support-free FDM geometry.
- Preserve keyed section assembly instead of relying on loose butt joints.

## chosen concept

Use the verified `v01` organizer geometry as the base layout, then split it into four keyed sections:

- front left
- rear left
- front right
- rear right

The vertical left/right keyed seam from `v01` is retained. `v02` adds a second keyed front/rear seam so each printable section fits a smaller bed.

## key parameters

- `section_target_w = 245`
- `section_target_d = 245`
- `section_target_h = 40`
- `horizontal_joiner_length = 10`
- `horizontal_joiner_width = 20`
- `horizontal_joiner_depth = 22`
- `horizontal_joiner_clearance = 0.3`

Important status on these values:

- Verified real-world input dimensions: none yet.
- Verified generated artifact dimensions:
  - assembled reference STL: `412.4 x 314.348 x 28.0 mm`
  - `front_left`: `216.2 x 138.0 x 28.0 mm`
  - `rear_left`: `216.2 x 186.348 x 28.0 mm`
  - `front_right`: `216.2 x 138.0 x 28.0 mm`
  - `rear_right`: `216.2 x 186.348 x 28.0 mm`
- Estimated dimensions used for organizer fit remain inherited from `v01`.
- The new printer target dimensions are user-provided manufacturing constraints, not real drawer measurements.

## print orientation

Print each section flat on the tray floor. The assembled reference STL is not intended as the primary print artifact for a `245 x 245 x 40 mm` printer.

## support plan

No supports intended. The new section seams use straight keyed tabs and slots aligned with the tray floor.

## known risks

- `v02` improves printability for a smaller bed but does not improve real-world fit confidence.
- The keyed front/rear seam adds more assembly joints and may need tolerance tuning after the first physical print.
- The full assembled reference STL can still exceed a small printer bed even though the section STLs are targeted to fit it.

## exported STL filename

Primary reference export:

- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02.stl`

Expected printable section exports:

- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02_front_left.stl`
- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02_rear_left.stl`
- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02_front_right.stl`
- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02_rear_right.stl`

## STL export status

Completed in this environment.

Verified exports:

- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02.stl`
- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02_front_left.stl`
- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02_rear_left.stl`
- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02_front_right.stl`
- `exports/vevor_65pc_half_drive_packout_4drawer_organizer_v02_rear_right.stl`

All five STL files were loaded with `trimesh` as watertight meshes. All four printable section STLs stayed within the requested `245 x 245 x 40 mm` maximum.

## dimensions required before final lock

- drawer internal usable width
- drawer internal usable depth
- drawer internal usable closed height
- drawer corner radii and any wall taper or internal ribs
- every socket outside diameter
- every socket height
- ratchet overall length, head width, and head thickness
- extension bar lengths and maximum diameters
- adapter and universal joint bounding envelopes

## test-fit classification

`v02` is still a scaffold and printer-fit split update, not a verified final organizer.

## next actions

- Print one section set and test the new front/rear keyed seam fit.
- Replace all estimated drawer and tool envelopes with measured values before changing the organizer fit.
- If any seam is too tight or loose, tune `horizontal_joiner_clearance` in the v02 source and re-export just the affected sections.
