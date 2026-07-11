# Reconstruction Notes

## task mode

`mesh_cleanup_and_remodel`

## target part

Rear exhaust flange adapter for an Arctic Cat portable AC unit. The part slides into the rear panel slot/interface and transitions that outlet to a nominal 6 in flexible duct connection.

## what is reused

- AC unit rear slot / mounting interface
- AC unit rear sealing surface
- 6 in flexible duct hose

## what is not modeled

- AC unit housing
- duct hose
- hose clamp or separate fasteners

## authoritative references

None provided in this workflow.

## supporting references

- `references/public/ac_flange_plate_adapter/AC_Flange_Plate.STL`
- nominal 6 in duct assumption from common duct sizing practice

## reference trust order used

1. no measured dimensions were available
2. no trusted CAD or OEM drawing was available
3. provided STL mesh was inspected as supporting seed geometry only
4. common 6 in duct sizing assumptions were used to refine the spigot interface

## anchor dimensions

All dimensions below are inferred from the seed mesh or chosen deliberately for a safer v02 remodel:

- inferred seed overall bbox: `152.690 x 152.346 x 66.040 mm`
- inferred rear plate outer size near the sealing face: `147.320 x 118.110 mm`
- inferred rear opening size near the sealing face: `139.700 x 107.950 mm`
- inferred round spigot outer diameter from the seed mesh: `152.326 mm`
- inferred round spigot inner diameter from the seed mesh: `142.195 mm`
- inferred duct center offset from the rear plate center: approximately `+3.48 mm` in X and `-0.28 mm` in Y
- planned v02 plate thickness: `3.20 mm`
- planned v02 spigot outer diameter: `151.00 mm`
- planned v02 spigot inner diameter: `145.00 mm`
- planned v02 straight engagement length: `32.00 mm`
- planned v02 retaining lip height: `2.50 mm`
- planned v02 retaining lip radial thickness: `1.20 mm`

## authoritative dimensions used

None. All dimensions in this workflow are inferred or assumed and must be treated as unverified until measured against the real AC unit and hose.

## protected interfaces

- rear insertion plate perimeter
- rear rectangular opening that mates to the AC outlet zone
- duct connection outer diameter and engagement depth
- sealing face against the AC rear panel
- duct centerline location relative to the plate

## reinforced zones

- flange-to-duct transition ring
- outer transition shell between the rear opening and round spigot
- plate perimeter outside the protected opening

## low-confidence zones

- exact fit of the rear mounting interface into the AC slot
- exact rear slot tolerances and sealing compression
- exact duct center offset relative to the real unit
- exact hose retention force needed for the user's duct
- exact amount of taper that best balances easy insertion and sealing

## comparison status

Completed locally against the seed mesh.

- bbox delta vs seed mesh: `-0.156 x -0.197 x +0.060 mm`
- silhouette IoU vs seed mesh:
  - front: `0.9861`
  - side: `0.9662`
  - top: `0.6997`
- protected rear plate section at `z = 2.54 mm` matches the inferred seed dimensions:
  - outer plate: `147.320 x 118.110 mm`
  - rear opening: `139.700 x 107.950 mm`
  - rear opening center offset: `+1.27 mm` in X
- rebuilt round spigot section at `z = 31.1 mm` verifies:
  - outer diameter: `151.0 mm`
  - inner diameter: `145.0 mm`
  - spigot center offset: `+2.8 mm` in X

The lower top-view IoU is expected because v02 intentionally replaces the seed mesh's hard square-to-round transition with a smoother, more rounded transition shell.

## pass/fail on critical features

- rear insertion plate perimeter: pass locally against the inferred seed dimensions
- rear rectangular opening: pass locally against the inferred seed dimensions
- duct centerline placement: pass locally against the inferred seed dimensions
- nominal 6 in duct interface strategy: pass for local CAD intent, not physically hose-tested
- sealing face planarity: pass locally by model construction
- real AC slot fit: not verified

## print orientation

Flange face on the print bed with the duct spigot rising upward.

## support plan

Target support-light FDM geometry. Use chamfered or blended outer transition walls to avoid large unsupported overhangs. If the chosen slicer flags the inner transition roof, add support only from the build plate.

## fit strategy

Slip-fit hose strategy for a nominal 6 in duct. The v02 spigot should insert into a flexible hose with light clamp or friction support rather than forcing a zero-clearance fit.

## duct sizing assumption

Assume a nominal 6 in duct hose with target spigot OD in the `150 to 152 mm` range. Use a slight taper plus a small retaining lip instead of a blunt cylinder.

## next revision actions

- test-fit the rear plate and opening against the real AC unit
- test-fit the hose on the spigot and confirm clamp retention
- decide whether a rear gasket channel is needed after physical leakage testing
- refine transition proportions only after real fit data confirms the protected interface

## exported STL filename

`exports/ac_flange_plate_adapter_v02.stl`

## STL export status

Success. `exports/ac_flange_plate_adapter_v02.stl` exported locally from OpenSCAD and loaded successfully as a watertight single-body mesh.

## future 3MF status

Not created.

## remaining mismatch notes

The seed mesh used a sharp pyramidal transition from the rear opening to the round spigot. v02 intentionally changes that transition to a smoother loft for airflow and printability while preserving the inferred rear plate geometry and duct alignment. Exact AC slot tolerance, sealing compression, and hose retention force remain unverified until physical test fitting.
