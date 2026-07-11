# Measurement Notes

## Project Stem

`perko_1247_high_torque_deck_plate_key`

## Version

`v01`

## Task Mode

`reference_based_reconstruction`

## Measurement Sources

- calipers: not supplied
- ruler: not supplied
- photo scale: not supplied
- reference CAD/STL: not supplied
- other: user-provided critical dimensions in task request

## Required Dimensions

- Lug center-to-center distance: exactly 28.58 mm.
- Lug tip diameter: 4.5 mm.
- Lug base shaft diameter: 5.2 mm.
- Lug protrusion length: 19.05 mm.
- Handle total length: 100 mm.
- Handle/body thickness: 10 mm to 12 mm target.

## Critical Fit Dimensions

| Feature | Value | Source | Confidence | Notes |
| --- | ---: | --- | --- | --- |
| lug center spacing | 28.58 mm | user request | high | exact protected interface |
| lug tip diameter | 4.5 mm | user request | high | exact protected interface |
| lug base shaft diameter | 5.2 mm | user request | high | exact protected interface |
| lug protrusion | 19.05 mm | user request | high | exact protected interface |
| metal-pin center spacing | 28.58 mm | derived from lug spacing | high | same protected interface |

## Protected Interfaces To Measure

- Actual gas-cap lug-hole center spacing.
- Actual gas-cap lug-hole entry diameter.
- Actual gas-cap lug-hole bottom diameter/depth.
- Cap face clearance around each lug root for the printed root relief collar.
- Preferred metal dowel or bolt measured diameter if using the reinforced body.

## Measured Dimensions

| Feature | Value | Tool | Confidence | Notes |
| --- | ---: | --- | --- | --- |
| user-specified lug center spacing | 28.58 mm | task request | high | treated as authoritative |
| user-specified lug tip diameter | 4.5 mm | task request | high | treated as authoritative |
| user-specified lug base diameter | 5.2 mm | task request | high | treated as authoritative |
| user-specified lug protrusion | 19.05 mm | task request | high | treated as authoritative |

## Inferred Dimensions

| Feature | Value | Basis | Confidence | Notes |
| --- | ---: | --- | --- | --- |
| head width | 48 mm | boss/lug clearance and hand strength | medium | not OEM-authenticated |
| tail width | 24 mm | high-torque grip comfort | medium | not OEM-authenticated |
| body thickness | 11 mm | requested 10-12 mm range | high | chosen midpoint |
| root relief diameter | 12.8 mm | 5.2 mm lug plus 3.8 mm radial relief | medium | may need cap-face clearance check |
| metal-pin hole diameter | 4.8 mm | 5.0 mm dowel press/epoxy starting point | medium | print-test before hardware install |
| metal-pin boss diameter | 18 mm | strength margin around pin holes | medium | not OEM-authenticated |

## Missing Measurements

- Actual cap hole depth and chamfer.
- Actual cap surface clearance around the lug holes.
- Actual metal pin/bolt diameter and surface finish for press-fit or epoxy-fit.

## Measurement Conflicts

None identified.

## Next Measurement Actions

- Print a small two-pin fit-test coupon before applying high torque.
- If the printed root relief bottoms out on the cap face, use the metal-pin version or reduce/trim only the non-mating relief collar after confirming the lug shaft still seats.
