# Battery Strap Holder

Task mode: `reference_based_reconstruction`

This project models a functional replacement battery box strap holder / strap retainer bracket. The uploaded photos were used as supporting visual reference only; measured dimensions are treated as the authoritative source.

## Measured Dimensions

- Overall Y length: 74.1 mm
- Overall X width: 11.0 mm
- Overall Z thickness / height: 7.0 mm
- Screw hole diameter: 4.8 mm
- Hole center offset from each end: 5.8 mm, adjustable
- Center bar width: 8.5 mm, adjustable
- Center bar height: 7.0 mm
- Base thickness: 3.0 mm
- Strap gap under raised bridge: 3.5 mm
- Corner radius: 2.0 mm
- Screw boss radius: 5.5 mm
- Clearance variable: 0.25 mm

## Variants

- `v01_exact`: closest functional copy from the supplied measured dimensions.
- `v02_heavy_duty`: slightly wider/thicker raised bridge with more transition overlap.
- `v03_fit_test`: 2 mm thin test plate for checking screw hole spacing before printing the final holder.

## Export Commands

```powershell
py -3 scripts\export_stl.py --input projects\battery-strap-holder\source\battery_strap_holder_v01.scad --output projects\battery-strap-holder\exports\battery_strap_holder_v01.stl --define variant_index=1
py -3 scripts\export_stl.py --input projects\battery-strap-holder\source\battery_strap_holder_v01.scad --output projects\battery-strap-holder\exports\battery_strap_holder_heavy_duty_v02.stl --define variant_index=2
py -3 scripts\export_stl.py --input projects\battery-strap-holder\source\battery_strap_holder_v01.scad --output projects\battery-strap-holder\exports\battery_strap_holder_fit_test_v03.stl --define variant_index=3
```

## Assumptions

- The photos show the overall form, but hidden underside details were not treated as exact.
- The screw-hole spacing is derived from `total_length_y - 2 * hole_center_offset_from_end`, giving 62.5 mm center-to-center with the current values.
- The raised bridge underside is set by `strap_gap_z`; change this after the first strap fit test if the strap is tighter or looser than expected.
- End bosses are rounded and centered within the 11 mm width; the screw-hole centers are slightly inward from the boss center because the supplied hole offset is 5.8 mm and the boss radius is 5.5 mm.
- No countersink or counterbore is modeled because screw head style was not measured.

## Print Recommendation

- Print flat on the mounting-ear bottom faces, with Z vertical.
- Print `v03_fit_test` first and confirm both screw holes line up before printing `v01_exact` or `v02_heavy_duty`.
- Prefer PETG or ASA for heat and compartment durability.
- ABS or nylon are also reasonable if your printer setup supports them.
- Avoid PLA for hot boat or battery compartment use.

## Suggested Settings

- 0.2 mm layer height
- 4 walls
- 40-60% infill
- 5 top/bottom layers
- PETG or ASA preferred

## Install Note

Print the fit-test plate first. If the holes do not align, adjust `hole_center_offset_from_end` in `source/battery_strap_holder_v01.scad`, re-export `v03_fit_test`, and repeat before printing the final part.
