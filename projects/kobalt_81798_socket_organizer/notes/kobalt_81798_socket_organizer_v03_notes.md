# Kobalt 81798 Socket Organizer v03 Notes

Task mode: `reference_based_reconstruction`

Target part: Kobalt 81798 / Lowe's item 4103169 153-piece socket and bit-driver organizer.

v03 is a corrective rebuild after user review of v02 in Bambu Studio. The v02 body geometry is used only as rough inventory/layout support; v03 source is the editable authority.

## What Is Reused

- User's actual Kobalt sockets and bit-driver sockets.
- Lowe's official set identity and inventory count.
- User screenshots as supporting footprint and grouping references only.

## What Is Not Modeled

- The metal sockets or bits.
- Kobalt logo artwork.
- ZLL Designs logo, Etsy branding, seller marks, or copied decorative artwork.
- Toolbox, drawer, case, packaging, or paid STL geometry.

## Locked Dimensions

- Overall reference footprint: 621.03 x 332.74 mm.
- Base thickness: 12.70 mm.
- Bambu Lab P2S build volume: 256 x 256 x 256 mm.
- Safe module target: 245 x 245 mm.
- Split modules: left_top, left_bottom, center_top_left, center_top_right, center_bottom_left, center_bottom_right, right_top, right_bottom.

## Estimated Dimensions

All pocket diameters are estimated because no caliper measurements were provided. Each item has its own explicit `pocket_diameter` value in the inventory table, but these are low-confidence fit values and should be verified with the v03 fit-test plate.

## v03 Corrections

- Separate aligned label STLs were added for color-ready Bambu Studio import.
- Labels are uppercase ASCII and raised from Z = base_thickness by 0.7 mm.
- right_bottom labels were repositioned into one clear row position per item with no stacked XY positions.
- Center long-bit layout was changed to 12 upper channels and 13 lower channels.
- Narrower individual shaft channels and individual end pockets are retained.
- Raised perimeter lips and section divider ribs were added to make each module read as a finished tray.

## Pocket Clearance Assumptions

- 1/4 drive pockets use 5.5 mm depth.
- 3/8 drive pockets use 6.5 mm depth.
- 1/2 drive pockets use 7.5 mm depth.
- Long-bit channels use 4.0 mm depth.
- Hole sizing remains printer/material dependent.

## Required Exports

- exports/kobalt_81798_socket_organizer_v03_left_top_body.stl
- exports/kobalt_81798_socket_organizer_v03_left_top_labels.stl
- exports/kobalt_81798_socket_organizer_v03_left_bottom_body.stl
- exports/kobalt_81798_socket_organizer_v03_left_bottom_labels.stl
- exports/kobalt_81798_socket_organizer_v03_center_top_left_body.stl
- exports/kobalt_81798_socket_organizer_v03_center_top_left_labels.stl
- exports/kobalt_81798_socket_organizer_v03_center_top_right_body.stl
- exports/kobalt_81798_socket_organizer_v03_center_top_right_labels.stl
- exports/kobalt_81798_socket_organizer_v03_center_bottom_left_body.stl
- exports/kobalt_81798_socket_organizer_v03_center_bottom_left_labels.stl
- exports/kobalt_81798_socket_organizer_v03_center_bottom_right_body.stl
- exports/kobalt_81798_socket_organizer_v03_center_bottom_right_labels.stl
- exports/kobalt_81798_socket_organizer_v03_right_top_body.stl
- exports/kobalt_81798_socket_organizer_v03_right_top_labels.stl
- exports/kobalt_81798_socket_organizer_v03_right_bottom_body.stl
- exports/kobalt_81798_socket_organizer_v03_right_bottom_labels.stl
- exports/kobalt_81798_socket_organizer_v03_fit_test_plate_body.stl
- exports/kobalt_81798_socket_organizer_v03_fit_test_plate_labels.stl

## Fit Warning

Do not treat v03 as guaranteed first-print fit. Print the fit-test plate first or update pocket diameters from caliper measurements.
