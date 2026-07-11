# Reference Comparison Log

## date/revision

2026-04-19 / `v02`

## current version

`ac_flange_plate_adapter_v02`

## reference used

- `references/public/ac_flange_plate_adapter/AC_Flange_Plate.STL`

## bbox comparison

- seed mesh bbox: `152.690 x 152.346 x 66.040 mm`
- rebuilt v02 bbox: `152.534 x 152.149 x 66.100 mm`
- delta (v02 - seed): `-0.156 x -0.197 x +0.060 mm`

## silhouette comparison

- front silhouette IoU: `0.9861`
- side silhouette IoU: `0.9662`
- top silhouette IoU: `0.6997`
- front and side silhouettes stayed close to the seed mesh.
- top silhouette diverges more because the v02 transition is intentionally smoother and less square-shouldered than the seed mesh.

## critical feature comparison

- rear plate outer section at `z = 2.54 mm`:
  - seed: `147.320 x 118.110 mm`
  - v02: `147.320 x 118.110 mm`
- rear opening section at `z = 2.54 mm`:
  - seed: `139.700 x 107.950 mm`
  - v02: `139.700 x 107.950 mm`
- rear opening center offset:
  - seed: `+1.27 mm` in X relative to the plate center
  - v02: `+1.27 mm` in X relative to the plate center
- round spigot center offset:
  - seed at `z = 40 mm`: about `+2.79 mm` in X relative to the plate center
  - v02 at `z = 31.1 mm`: `+2.80 mm` in X relative to the plate center
- round spigot sizing:
  - seed at `z = 40 mm`: about `152.326 mm` OD and `142.195 mm` ID
  - v02 at spigot base: `151.0 mm` OD and `145.0 mm` ID
- v02 intentionally shifts the spigot to a thinner-wall, standard-friendly hose interface while keeping the centerline and overall envelope close.

## mismatches found

- top-view shoulder shape is rounder than the seed mesh
- spigot wall is thinner than the seed mesh by design
- spigot includes a taper and retaining lip not present in the seed mesh
- seed mesh is non-watertight, while v02 is watertight and single-body

## corrections planned

No further CAD correction is planned before physical fit checks. Next changes should be driven by measured AC slot fit, leakage checks, and actual hose retention testing.

## confidence level

Medium for geometry cleanup and duct-interface intent. Low for final fit until the real AC unit and hose are measured and test-fitted.
