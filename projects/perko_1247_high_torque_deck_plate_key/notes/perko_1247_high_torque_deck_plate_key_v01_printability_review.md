# Printability Review

## Project Stem

`perko_1247_high_torque_deck_plate_key`

## Version

`v01`

## Printer

FDM printer

## Material

PETG

## Bed Fit

- intended printer: general FDM printer
- model extents: approx. 100 mm long, 48 mm wide, 30 mm tall including lugs
- bed size: not specified
- status: should fit typical consumer FDM beds

## Orientation

Print on a side face so the plastic lugs run parallel to the bed. Do not print with the lugs pointing straight up, because that would put the highest torque load across layer adhesion at the lug roots.

## Support Plan

- Printed-lug variant: supports expected under lugs/root-relief areas in side orientation.
- Metal-pin body: supports may be required around underside bosses in side orientation.

## Brim Plan

Use a brim to stabilize the long, narrow side-print setup.

## Wall Count

Use at least 5 or 6 walls/perimeters. This should make the narrow lug region close to fully perimeter-reinforced.

## Layer Height

0.16 mm to 0.24 mm is reasonable for PETG. Prefer stronger layer bonding over cosmetic finish.

## Infill

50% to 100% Gyroid or Grid.

## Overhangs And Bridges

The side-print orientation prioritizes lug strength but creates support needs under the protruding lugs and reinforced collars.

## Holes, Inserts, And Hardware

- Printed-lug variant has no hardware.
- Optional metal-pin variant includes two vertical holes at 28.58 mm center spacing.
- Default hole diameter is 4.8 mm for a 4.5 mm to 5.0 mm dowel/bolt workflow. Tune this with a test coupon for the actual pin and printer.

## Snap Fits Or Flex Features

None.

## Heat Exposure

PETG is appropriate for moderate outdoor/marine deck exposure but can soften in hot enclosed spaces.

## Outdoor Exposure

Use UV-resistant PETG or a more UV-stable material if the key will live outside.

## Screw Loads

No screw loads. Torque is transferred through the two lug roots or metal pins.

## Protected Interface Impact

The reinforced root collars strengthen the printed lug roots but may require cap-face clearance. The metal-pin body is the safer option for repeated high-torque use.

## Risk Rating

Medium

## Review Status

`reviewed; physical fit NOT VERIFIED`
