# Release Notes

## Project Stem

`perko_1247_high_torque_deck_plate_key`

## Version

`v01`

## Task Mode

`reference_based_reconstruction`

## Status

generated outputs; physical fit NOT VERIFIED

## Included Artifacts

- source: `source/perko_1247_high_torque_deck_plate_key_v01.scad`
- metal-pin wrapper source: `source/perko_1247_high_torque_deck_plate_key_v01_metal_pin_body.scad`
- STL: `exports/perko_1247_high_torque_deck_plate_key_v01.stl`
- optional STL: `exports/perko_1247_high_torque_deck_plate_key_v01_metal_pin_body.stl`
- previews: iso, front, and side PNG files in `previews/`
- notes: `notes/perko_1247_high_torque_deck_plate_key_v01_notes.md`
- manifest: `notes/perko_1247_high_torque_deck_plate_key_v01_manifest.md`
- review report: `notes/perko_1247_high_torque_deck_plate_key_v01_review_report.md`

## What Changed

- Created a parametric high-torque deck plate key with exact 28.58 mm lug center spacing.
- Added a printed-lug variant with tapered lugs and 3.8 mm root relief collars.
- Added an optional metal-pin body variant with 4.8 mm vertical pin holes and 18 mm reinforced bosses.
- Used a solid 100 mm handle/body with 11 mm thickness and chamfered body edges.

## Known Assumptions

- The user-provided critical dimensions are authoritative.
- Perko 1247 is treated as a design-style reference, not a measured OEM silhouette.
- The cap face has enough clearance for the printed root relief collars, or the metal-pin body will be used instead.

## Low-Confidence Zones

- Physical fit on the actual cap is not verified.
- Metal-pin press-fit/epoxy-fit hole size should be tuned with a test coupon.

## Print Instructions

- Print PETG on the side, not with lugs pointing up.
- Use at least 5 or 6 walls.
- Use 50% to 100% Gyroid or Grid infill.
- Use the upper safe PETG temperature range for the filament, commonly 255 C to 260 C when supported.
- Use low cooling, about 20% to 30%, for stronger layer bonding.

## Not Included

- OEM cap geometry.
- Physical fit-test result.
- 3MF or slicer project.

## Verification Status

`exports and previews generated; physical fit NOT VERIFIED`
