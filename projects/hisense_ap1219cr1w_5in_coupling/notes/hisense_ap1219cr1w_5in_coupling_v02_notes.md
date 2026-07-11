# Reconstruction Notes

## task mode used

`mesh_cleanup_and_remodel`

## exact target part

Rear appliance coupling / exhaust hose adapter for a Hisense portable air conditioner model `AP1219CR1W`, revised from `v01` into `v02` as a native parametric OpenSCAD reconstruction for a nominal `5 in` hose target.

## what surrounding parts are reused

- Hisense `AP1219CR1W` rear housing / lock opening
- existing rear-panel twist-lock engagement on the appliance
- existing exhaust hose family associated with the compatible appliance-adapter listings for `AP1419CR1G`, `AP1319HR1G`, and `AP1219CR1W`

## what is not modeled

- AC unit
- grille panel
- hose body
- window adapter
- speculative hidden seals
- decorative branding or molded text not required for fit

## authoritative references

1. user rear-panel photos for the real `AP1219CR1W`
2. user hose measurement photos
3. user requirement that the part fit `AP1219CR1W` and the user's hose

## supporting references

4. `projects/hisense_ap1219cr1w_5in_coupling/source/hisense_ap1219cr1w_5in_coupling_v01.scad`
5. `projects/hisense_ap1219cr1w_5in_coupling/exports/hisense_ap1219cr1w_5in_coupling_v01.stl`
6. `projects/hisense_ap1219cr1w_5in_coupling/notes/hisense_ap1219cr1w_5in_coupling_v01_notes.md`
7. `projects/hisense_ap1219cr1w_5in_coupling/notes/hisense_ap1219cr1w_5in_coupling_v01_comparison_log.md`
8. `references/measured/hisense_k1983844_dummy_coupling/ac_vent_tube_adapter.stl`
9. user-supplied marketplace screenshots for the compatible appliance-adapter family
10. Hisense installation manual for `AP1219CR1W` family showing the part name `Coupling`
11. supporting compatible-family appliance-adapter listing for `AP1419CR1G`, `AP1319HR1G`, `AP1219CR1W`
12. supporting OEM / seller-family connector listings including the related `6-1/8 in` hose-side ID and `6-1/2 x 5-7/16 in` square-side claims

## locked_dimensions

- `hose_nominal_d_user_target = 127.0 mm`
- project stem: `hisense_ap1219cr1w_5in_coupling`
- task mode: `mesh_cleanup_and_remodel`
- part family: rear appliance coupling for `Hisense AP1219CR1W`
- build units: `mm`
- build axis: `Z+` up
- build volume target: Bambu P2S with `245 mm` safety target

## photo_derived_estimates

- hose target remains in the nominal `127 to 130 mm` family from the user's hose photo: confidence `medium`
- rear vent occupied height still appears to be in the `127 to 140 mm` zone: confidence `low`
- rear vent occupied width still appears smaller than the final seating flange and surrounded by additional bezel area: confidence `low`
- appliance lock direction shown on the real machine is `UNLOCK <-> LOCK`: confidence `high`

## inferred_dimensions

These remain inferred and parameterized in `v02`:

- overall depth: `57.5 mm`
- round lock-band OD family: `162.0 mm`
- `v02` flange family after growth: `160.0 x 120.0 mm`
- seat opening family: about `152 x 112 mm`
- lock band zone: `z = 43.0` to `z = 55.5`
- active hose receiver ID on the user track: `129.2 mm`
- seller-family comparison track: `155.6 mm`
- hose entry chamfer top opening: about `132.4 mm`
- hose receiver OD: `134.4 mm`

## unknown_dimensions_needing_measurement

- exact tab angular clocking on the real `AP1219CR1W` lock slots
- exact twist-lock travel and hard-stop timing on the real appliance
- exact flange footprint needed against the user's rear bezel after a real print test
- exact best final hose receiver ID for the user's hose cuff
- exact best lip behavior for the user's hose cuff after a real insertion test
- whether a foam tape or gasket strip is needed on the seating plane

## anchor points

- hose receiver center axis at the model origin
- appliance seating plane at `z = 0`
- transition start plane from square scoop to round body at `z = 30.0`
- lock-band start plane at `z = 43.0`
- lock-band end plane at `z = 55.5`
- flange outer perimeter at `160.0 x 120.0 mm` in the default `v02` setting
- lock-band OD `162.0 mm`
- tab root planes centered within the lock-band zone
- tab stop faces on the steeper trailing faces of the cam tabs
- hose lead-in chamfer start at `z = 54.5`
- hose retention lip plane at `z = 55.9`

## protected interfaces

- appliance seating plane
- circular lock-band OD family
- four-tab clock family from `v01` / seed family
- tab engagement depth and stop-face intent
- insertion depth from seating plane to the lock band
- hose receiver circularity and user-target fit track

## geometry behavior decisions

- `v02` preserves the successful `v01` overall square-to-round body family.
- `v01` left the engagement features as blocky ring remnants created mainly by relief cuts.
- `v02` replaces that with native cam-style tab bodies that have:
  - a distinct tangential lead-in ramp
  - a distinct steeper stop face
  - a relief pocket behind the tab
  - embedded tab roots so the final STL stays single-body
- `v02` changes the hose-side strategy from the tighter `v01` lip-centered geometry to a larger receiver entry with a lead-in chamfer for better first-print usability.
- `v02` keeps the listing-family confirmation separate from dimensional truth. Compatibility-family listings were used to confirm the correct appliance-adapter family, not to claim exact dimensions.

## symmetry vs asymmetry decision

I carried forward the four-clock family from `v01` and the supporting seed family because that is the strongest geometry-family evidence available locally. I did not introduce arbitrary asymmetry, but the exact real-machine tab clocking remains low confidence until a physical test fit proves it.

## print orientation

Appliance seating flange down on the bed, circular body upward.

## support plan

Default plan is support-light or support-free FDM.

- Keep the seat plane flat on the bed.
- Check slicer overhang preview around the receiver chamfer and the relief pockets.
- Only add support if slicer preview shows unstable internal receiver spans or weak tab-relief bridges.

## low-confidence zones

- `[low]` exact tab angular placement versus the real rear lock slots
- `[low]` exact twist-lock stop timing on the real machine
- `[low]` exact flange footprint against the rear bezel after first print
- `[medium]` exact hose receiver ID that the user's hose cuff will prefer
- `[medium]` exact retention behavior after heat, print shrink, and material choice
- `[medium]` whether the seller-family `6-1/8 in` claim refers to the same engagement diameter as the user's actual hose target

## comparison status

Comparison was completed locally against both `v01` and a print-oriented copy of the supporting seed STL.

- `v01` to `v02` bbox delta: `0.0 x 0.0 x 0.0 mm`
- `v01` to `v02` silhouette IoU:
  - front: `0.9963`
  - side: `0.9963`
  - top: `0.9191`
- supporting seed to `v02` bbox delta: `-2.0 x 0.0 x 0.0 mm`
- supporting seed to `v02` silhouette IoU:
  - front: `0.9790`
  - side: `0.9567`
  - top: `0.6113`

Interpretation:

- `v02` stayed very close to `v01` in front and side silhouette, so the family shape was preserved.
- `v02` changed the top silhouette more than `v01` because the hose receiver strategy and tab details were revised.
- `v02` remains `2 mm` narrower than the supporting seed in one silhouette axis, as in `v01`.

## remaining mismatches

- exact real-machine lock timing is still inferred and unverified
- exact appliance-side engagement clearance is still unverified
- flange seating coverage is improved by the default `+2 mm` growth in both width and height, but not yet physically proven
- the conflict between the user's `5 in` hose target and the supporting `6-1/8 in` seller-family claim remains unresolved without a real measured part

## print strategy

- process target: `FDM`
- suggested material: `PETG` or another heat-tolerant functional plastic
- suggested starting wall count: at least `4`
- keep the tab roots fully solid
- do not thin the stop faces aggressively

## mandatory v02 revision notes

- `v01` to `v02` tab change: `v01` used blockier ring remnants defined mostly by relief cuts, while `v02` uses explicit cam-style tabs with a lead-in ramp, stop face, relief pocket, and embedded root.
- hose entry change: `v02` enlarges the active receiver track to `129.2 mm` on the user-target path and adds a `3.2 mm` diametric lead-in chamfer over `3.0 mm` length.
- flange growth applied: `+2.0 mm` width and `+2.0 mm` height relative to `v01`, giving a default flange family of `160.0 x 120.0 mm`.
- lock-band tuning range: top-level parameters expose `lock_band_z_start`, `lock_band_height`, and `lock_band_z_end`. A practical first tuning window is `41.0 to 45.0 mm` for `lock_band_z_start`, which is `+/- 2.0 mm` around the current default.
- exact real-machine lock timing remains unverified until a physical test fit is performed.
- the compatible-family listing confirms the correct adapter family, but does not provide enough dimensional detail by itself to guarantee exact fit.
- related seller-family claims of `6-1/8 in` hose side ID and `6-1/2 x 5-7/16 in` square side were recorded as supporting-only, not locked truth.

## exported STL filename

`projects/hisense_ap1219cr1w_5in_coupling/exports/hisense_ap1219cr1w_5in_coupling_v02.stl`

## STL export status

Success. `v02` exported locally from OpenSCAD and loads as a watertight single-body mesh.

## preview status

Technical STL preview renders were generated locally to satisfy the repo output structure:

- `previews/hisense_ap1219cr1w_5in_coupling_v02_iso.png`
- `previews/hisense_ap1219cr1w_5in_coupling_v02_front.png`
- `previews/hisense_ap1219cr1w_5in_coupling_v02_side.png`
- `previews/hisense_ap1219cr1w_5in_coupling_v02_top.png`
- `previews/hisense_ap1219cr1w_5in_coupling_v02_detail_tabs.png`

These are simple STL renders only, not AI-generated imagery.
