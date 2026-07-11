# Reconstruction Notes

## Task Mode

`reference_based_reconstruction`

## Target Part

Heavy-duty marine deck plate key based on the Perko 1247 two-lug key pattern, modified into a 100 mm high-leverage wrench arm for opening a stuck gas cap.

## What Is Reused

- Existing marine gas cap / deck plate with two lug holes at the user-provided spacing.
- Existing cap seal, cap body, threads, chain, and surrounding deck hardware.

## What Is Not Modeled

- Full cap or deck plate assembly.
- OEM Perko handle outline beyond the two-lug functional pattern.
- Cap threads, gasket compression, chain mount, or lock features.

## Authoritative References

- User-provided critical mating dimensions in the task request.

## Supporting References

- Perko 1247 design intent only: two-lug marine deck plate key style.

## Reference Trust Order Used

1. user-provided measured/required dimensions
2. Perko 1247 style reference

## Geometry Contract

| Feature | Required Value | Model Value | Confidence | Protected |
| --- | ---: | ---: | --- | --- |
| lug center-to-center spacing | 28.58 mm | 28.58 mm | high | yes |
| lug tip diameter | 4.5 mm | 4.5 mm | high | yes |
| lug base shaft diameter | 5.2 mm | 5.2 mm | high | yes |
| total protrusion below body | 19.05 mm | 19.05 mm | high | yes |
| printed root relief radius target | 3-4 mm | 3.8 mm | medium | no, reinforcement |
| handle total length | approx. 100 mm | 100 mm | high | no |
| handle/body thickness | 10-12 mm | 11 mm | high | no |
| metal pin hole center spacing | 28.58 mm | 28.58 mm | high | yes |
| metal pin body hole diameter | 4.5-5.0 mm pin support | 4.8 mm default | medium | yes |

## Anchor Dimensions

- Overall length: 100 mm.
- Lug center line: 24 mm from the rounded head end.
- Lug spacing axis: across the head width, centered on Y0.
- Lug center positions: Y +/-14.29 mm.
- Head width: 48 mm to cover reinforced lug roots and metal-pin bosses.
- Tail/grip width: 24 mm.
- Body thickness: 11 mm.

## Authoritative Dimensions Used

- `lug_center_spacing = 28.58`
- `lug_tip_d = 4.5`
- `lug_base_d = 5.2`
- `lug_protrusion = 19.05`
- `handle_total_length = 100`
- `body_thickness = 11`

## Protected Interfaces

- Two lug center positions and center spacing.
- Lug taper endpoints.
- Lug protrusion length.
- Metal-pin hole center spacing in the optional reinforced body.

## Reinforced Zones

- Printed-lug variant uses 3.8 mm root relief collars that expand from the 5.2 mm lug shaft into a 12.8 mm reinforced base at the body.
- Metal-pin variant uses 18 mm bosses around each vertical pin hole, plus top and underside boss material around the printed body.
- Main body is solid with no cutouts.

## Low-Confidence Zones

- Exact Perko 1247 handle silhouette was not used as authoritative geometry.
- The printed root relief collars may contact the cap face if the deck plate holes have no chamfer or surface clearance.
- The default 4.8 mm metal-pin hole should be treated as a starting value for a 5.0 mm dowel press-fit or epoxy-fit; print a small test coupon before committing hardware.

## Comparison Status

- bbox: model-controlled only; no OEM CAD or measured full key bbox supplied.
- front silhouette: functional spade/wrench silhouette, not OEM-authenticated.
- side silhouette: 11 mm thick solid body with 19.05 mm lug protrusion.
- top silhouette: 100 mm long high-leverage handle.
- critical local features: lug spacing, lug diameters, protrusion, and metal-pin spacing are parameterized from the authoritative dimensions.

## Pass/Fail On Critical Features

- lug center-to-center spacing: PASS in source parameters.
- lug tip diameter: PASS in source parameters.
- lug base shaft diameter: PASS in source parameters.
- lug protrusion: PASS in source parameters.
- physical fit on actual cap: NOT VERIFIED.

## Print Orientation

Print the key on its side, not with lugs pointing straight up. Rotate the model in the slicer so the lugs run parallel to the bed and the continuous perimeters carry through the handle and lugs.

## Support Plan

- Printed-lug variant: use supports under lug/root-relief overhangs after side rotation.
- Metal-pin body: supports may be needed under underside bosses after side rotation.

## PETG High-Torque Print Checklist

- Walls/perimeters: at least 5 or 6.
- Infill: 50% to 100% Gyroid or Grid.
- Temperature: upper safe PETG range for the filament, commonly 255 C to 260 C if supported by the brand.
- Cooling: 20% to 30%, or off for early layers if the printer/material setup tolerates it.
- Brim: recommended because the side-print orientation presents a long narrow bed contact patch.

## Variant Notes

- Default export: printed tapered plastic lugs.
- Optional export: use `source/perko_1247_high_torque_deck_plate_key_v01_metal_pin_body.scad` to create a body with two vertical metal-pin holes and reinforced bosses.
- For the optional metal-pin version, install 4.5 mm to 5.0 mm metal dowel pins or bolts so the exposed metal protrusion is 19.05 mm and the pin center spacing remains 28.58 mm.

## Exported STL Filename

- `exports/perko_1247_high_torque_deck_plate_key_v01.stl`
- `exports/perko_1247_high_torque_deck_plate_key_v01_metal_pin_body.stl`

## STL Export Status

`exported and mesh-checked`

## Preview Export Status

`iso, front, and side previews exported`

## Future 3MF Status

`not created`

## Remaining Mismatch Notes

Physical cap fit and torque durability are not verified until a printed fit-test is tried on the actual gas cap.
