# Reference Comparison Log

## date/revision

`2026-04-22 / v02`

## current version

`projects/hisense_ap1219cr1w_5in_coupling/source/hisense_ap1219cr1w_5in_coupling_v02.scad`

## reference used

- `v01` SCAD, STL, notes, and comparison log
- supporting seed STL family
- user hose and rear-panel photos
- user-supplied marketplace screenshots
- Hisense installation manual showing the family coupling part
- compatible-family listing for `AP1419CR1G`, `AP1319HR1G`, `AP1219CR1W`
- supporting OEM / seller-family connector listings

## bbox comparison

- `v01` STL: `162.0 x 162.0 x 57.5 mm`
- `v02` STL: `162.0 x 162.0 x 57.5 mm`
- supporting seed after print orientation: `164.0 x 162.0 x 57.5 mm`
- `v02` delta versus `v01`: `0.0 x 0.0 x 0.0 mm`
- `v02` delta versus supporting seed: `-2.0 x 0.0 x 0.0 mm`

## silhouette comparison

- `v01` to `v02`
  - front IoU: `0.9963`
  - side IoU: `0.9963`
  - top IoU: `0.9191`
- supporting seed to `v02`
  - front IoU: `0.9790`
  - side IoU: `0.9567`
  - top IoU: `0.6113`

## critical feature comparison

- overall square-to-round family: preserved
- seating plane: preserved
- lock-band OD family: preserved
- flange seating coverage: increased by `+2 mm` in width and `+2 mm` in height
- lock-band axial zone: now explicit and tunable
- hose receiver: enlarged and chamfered relative to `v01`
- tabs: rebuilt from blockier `v01` remnants into native cam-style tab bodies with ramp, stop, and relief behavior

## mismatches found

- `v02` remains `2 mm` narrower than the supporting seed in one axis
- top view differs materially from the rough seed because the internal receiver and tab details were revised as clean native geometry
- exact machine-side lock timing and hard stop are still inferred

## corrections planned

- first print should test appliance-side insertion and twist-lock behavior before any dimension is called final
- if the hose remains tight, increase `hose_fit_clearance` or raise `user_hose_receiver_id_track`
- if the seating plane still needs more coverage, increase `flange_extra_w` and/or `flange_extra_h`
- if the lock timing feels early or late, tune `lock_band_z_start` within the recorded `+/- 2 mm` window

## confidence level

Overall `v02` confidence is `medium`.

- geometry-family preservation: `medium-high`
- hose entry usability: `medium`
- exact lock timing on the real machine: `low`
