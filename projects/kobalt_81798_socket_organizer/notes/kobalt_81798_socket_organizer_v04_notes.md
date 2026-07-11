# Kobalt 81798 Socket Organizer v04 Notes

Task mode: `reference_based_reconstruction`

Target part: Kobalt 81798 / Lowe's item 4103169 153-piece socket and bit-driver organizer.

v04 is a corrective rebuild from v03. It keeps the original modular organizer concept and separate AMS-ready label STLs while adding reference-informed pocket diameters and interlocking overlap seams.

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

## Reference Diameter Upgrade

The uploaded free socket organizer STLs and Gridfinity Kobalt socket STL were scanned for circular pocket wall components. Their diameters were used as dimensional baselines, then constrained to the Kobalt 81798 compact layout where needed.

## v04 Corrections

- Free STL reference pocket diameters incorporated into 1/4, 3/8, and 1/2 circular cup rows.
- Separate aligned label STLs retained for AMS/two-color printing.
- right_bottom label issue remains fixed.
- Interlocking shiplap-style tab/socket seams added to every touching module boundary.
- Seam features are full-height, support-free, and self-locating.
- Center long-bit layout remains 12 upper channels and 13 lower channels.

## Pocket Clearance Assumptions

- 1/4 drive pockets use 5.5 mm depth.
- 3/8 drive pockets use 6.5 mm depth.
- 1/2 drive pockets use 7.5 mm depth.
- Long-bit channels use 4.0 mm depth.
- Hole sizing remains printer/material dependent.
- Seam lap width: 8.0 mm.
- Seam clearance: 0.25 mm.

## Required Exports

- PASS: exports/kobalt_81798_socket_organizer_v04_left_top_body.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_left_top_labels.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_left_bottom_body.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_left_bottom_labels.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_center_top_left_body.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_center_top_left_labels.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_center_top_right_body.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_center_top_right_labels.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_center_bottom_left_body.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_center_bottom_left_labels.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_center_bottom_right_body.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_center_bottom_right_labels.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_right_top_body.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_right_top_labels.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_right_bottom_body.stl
- PASS: exports/kobalt_81798_socket_organizer_v04_right_bottom_labels.stl

## Validation Summary

- `scripts/validate_scad.py` PASS.
- `tools/validate_v04.py` PASS.
- Total storage locations: 153.
- Circular pockets: 128.
- Long channels: 25.
- Unreadable labels: 0.
- Overlapping or stacked labels: 0.

## Fit Warning

Do not treat v04 as guaranteed first-print fit. Caliper measurements of the actual Kobalt sockets still override every STL-derived estimate.
