# Reference Comparison Log

## date/revision

`2026-04-22 / v01`

## current version

`projects/hisense_ap1219cr1w_5in_coupling/source/hisense_ap1219cr1w_5in_coupling_v01.scad`

## reference used

- supporting STL family: `references/measured/hisense_k1983844_dummy_coupling/ac_vent_tube_adapter.stl`
- user hose measurement photo
- user AP1219CR1W rear-panel photos
- marketplace screenshots supplied in the task prompt

## bbox comparison

- supporting STL after print orientation: `164.0 x 162.0 x 57.5 mm`
- v01 STL: `162.0 x 162.0 x 57.5 mm`
- delta: `-2.0 x +0.0 x +0.0 mm`

## silhouette comparison

- front IoU: `0.9804`
- side IoU: `0.9587`
- top IoU: `0.5666`

## critical feature comparison

- square-to-round overall family: preserved
- appliance-side flat seat: preserved
- round lock-band OD family: preserved as a native rebuild
- lock band rebuilt as four clocked tabs with relief pockets instead of a direct mesh copy
- hose interface rebuilt to the user's nominal `5 in` requirement

## mismatches found

- v01 is `2 mm` narrower in one silhouette axis than the supporting seed
- top-view silhouette is cleaner and more centered than the rough mesh
- exact twist-lock stop placement is still inferred

## corrections planned

- first real-world print should be checked for appliance-side tab clocking
- if the rear bezel shows interference, widen or shift the flange footprint parametrically
- if the hose grip is too tight or too loose, adjust `hose_fit_clearance`, `hose_receiver_od`, or `hose_receiver_depth`

## confidence level

Overall confidence for the v01 geometry family is `medium`.

- outer family shape: `medium`
- hose-side nominal fit intent: `medium`
- exact real-machine lock behavior: `low`
