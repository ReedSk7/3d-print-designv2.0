# Reconstruction Notes

## task mode used

`mesh_cleanup_and_remodel`

## exact target part

Rear appliance coupling / exhaust hose adapter for a Hisense portable air conditioner model `AP1219CR1W`, rebuilt as a clean OpenSCAD source model and tuned for a nominal `5 in` hose interface.

## what surrounding parts are reused

- Hisense `AP1219CR1W` rear housing / vent frame
- existing rear-panel lock / twist engagement on the appliance
- existing nominal `5 in` portable AC hose

## what is not modeled

- full AC housing
- rear grille assembly
- flexible hose body
- window kit
- branding or molded text
- speculative hidden sealing parts not visible in references

## authoritative references

1. user photos with tape measurements of the actual hose and rear panel area:
   - `references/measured/hisense_k1983844_dummy_coupling/IMG_20260422_171512.jpg`
   - `references/measured/hisense_k1983844_dummy_coupling/IMG_20260422_171525.jpg`
   - `references/measured/hisense_k1983844_dummy_coupling/IMG_20260422_171520.jpg`
   - `references/measured/hisense_k1983844_dummy_coupling/IMG_20260422_171529.jpg`
   - `references/measured/hisense_k1983844_dummy_coupling/IMG_20260421_202246.jpg`
   - `references/measured/hisense_k1983844_dummy_coupling/IMG_20260421_202248.jpg`
2. user requirement that the part fit `Hisense AP1219CR1W` and a nominal `5 in` hose

## supporting references

3. `references/measured/hisense_k1983844_dummy_coupling/ac_vent_tube_adapter.stl`
4. supplied marketplace screenshots showing the square-to-round appliance adapter form and outer tab family
5. user prompt seller-dimension estimates and compatibility notes

## reference trust order used

1. user hose photo and explicit `5 in` requirement for the hose-side fit target
2. user rear-panel photos for the appliance family, lock direction, and approximate occupied opening area
3. supplied STL for outer-envelope topology, section proportions, and lock-band feature family only

The supplied STL was treated as supporting geometry only and was not imported into the final model.

## locked_dimensions

- `hose_nominal_d = 127.0 mm`
- model family target: `Hisense AP1219CR1W`
- part function: appliance-side coupling adapter, not the window adapter
- build units: `mm`
- build axis: `Z+` up

## photo_derived_estimates

- hose cuff visible internal target is approximately in the `127 to 130 mm` zone from the tape photo: confidence `medium`
- rear vent / grille occupied height visible in the tape photos appears to be roughly in the `127 to 140 mm` zone: confidence `low`
- rear vent / grille occupied width visible in the tape photos appears to be smaller than the final adapter flange and sits within a broader mounting surround: confidence `low`
- lock direction is explicitly indicated on the appliance as `UNLOCK <-> LOCK`: confidence `high`

## inferred_dimensions

These were inferred from seed-mesh sectioning and kept parameterized:

- body total depth: `57.5 mm`
- cylindrical lock-band OD: `162.0 mm`
- AC-side front opening envelope: about `152 x 112 mm`
- outer flange envelope used in v01: `158.0 x 118.0 mm`
- flange thickness / seat plane thickness: `2.8 mm`
- transition depth to the fully round body: `30.0 mm`
- lock-band start plane from the seat face: `44.0 mm`
- lock-band end plane before terminal stop rim: `55.9 mm`
- receiver lip OD for the hose: `126.4 mm`
- receiver retaining bore ID: `122.0 mm`

## unknown_dimensions_needing_measurement

- exact tab angular placement on the real AP1219CR1W rear interface
- exact twist-lock travel and hard-stop timing on the machine
- exact flange footprint against the user's rear bezel once a print is physically test-fit
- exact hose retention lip profile preferred by the user's actual hose cuff
- whether a foam tape or gasket strip is needed on the appliance-side seating plane

## anchor points

- hose receiver center axis at the model origin
- outer seating plane against the AC rear panel at `z = 0`
- fully round body start at `z = 30.0`
- lock-band root plane at `z = 44.0`
- lock-band terminal stop rim at `z = 55.9`
- outer flange perimeter `158.0 x 118.0 mm`
- circular lock-band OD `162.0 mm`
- hose receiver lip OD / ID `126.4 / 122.0 mm`

## protected interfaces

- flat appliance seating plane
- circular body OD and lock-band family around the appliance interface
- tab clocking family, tangential width, and relief-pocket lead-in behavior
- insertion depth from the seat plane to the lock band
- hose-side receiver fit target around the nominal `127 mm` hose family
- hose retaining lip OD / bore relationship

## symmetry vs asymmetry decision

The rebuild keeps a centered hose axis and a four-clocked lock band because that is what the supporting STL family most clearly showed. I did not assume arbitrary asymmetry beyond that. Remaining asymmetry risk is concentrated in the exact tab clocking and flange footprint against the real rear bezel.

## build orientation

Seat plane / square flange down on the bed, circular body and hose receiver upward.

## support plan

Default plan is support-free FDM.

- Keep the seat plane flat on the bed.
- Let the square-to-round shell bridge gradually upward.
- Review slicer overhang preview at the internal receiver transition and at the lock-pocket lead-ins.
- Add supports only if the slicer shows weak unsupported spans inside the receiver.

## build volume check

Expected print envelope for v01 STL: `162.0 x 162.0 x 57.5 mm`

This fits comfortably inside the Bambu P2S `256 x 256 x 256 mm` build volume and the requested `245 mm` safety target. No split is needed.

## low-confidence zones

- `[low]` exact tab angular placement versus the real AP1219CR1W rear interface
- `[low]` exact lock travel and stop position on the appliance
- `[low]` exact flange footprint against the user's rear housing after physical test fit
- `[medium]` transition depth from the square seat to the round body
- `[medium]` exact hose retention lip geometry the user's hose cuff will prefer
- `[medium]` seller dimension conflict: the marketplace-style `6-1/8 in` opening claim does not match the user's `5 in` hose requirement, so v01 prioritizes the user's hose target

## comparison status

Comparison was completed locally against a print-oriented copy of the supporting STL plus the user photos.

- STL bbox: `162.0 x 162.0 x 57.5 mm`
- supporting seed bbox after print orientation: `164.0 x 162.0 x 57.5 mm`
- bbox delta versus the supporting seed: `-2.0 x +0.0 x +0.0 mm`
- silhouette IoU versus the supporting seed:
  - front: `0.9804`
  - side: `0.9587`
  - top: `0.5666`

Interpretation:

- front and side silhouette agreement stayed strong enough for a same-family reconstruction
- top silhouette is materially different because the final model is a centered, cleaned native rebuild with a new internal `5 in` receiver rather than a direct mesh copy
- hose-side fit was tuned to the user's `5 in` requirement even where seller-style dimensions suggested a larger opening family

## remaining mismatches

- the exact real-machine tab stop geometry is still inferred, not physically verified
- the flange footprint is conservative but not confirmed against a printed trial on the actual rear panel
- the top-view silhouette remains more idealized than the rough mesh
- no physical hose test-fit or rear-panel test-fit has been performed yet in this environment

## print strategy

- process target: `FDM`
- suggested material: `PETG` or another heat-tolerant functional plastic
- suggested starting wall count: at least `4`
- avoid decorative textures
- review lock-band durability after first print if the appliance twist engagement feels tight

## exported STL filename

`projects/hisense_ap1219cr1w_5in_coupling/exports/hisense_ap1219cr1w_5in_coupling_v01.stl`

## STL export status

Success. Export completed locally from OpenSCAD and the resulting STL loads as a watertight single-body mesh.

## preview status

Technical STL preview renders were generated locally to satisfy the repo output structure:

- `previews/hisense_ap1219cr1w_5in_coupling_v01_iso.png`
- `previews/hisense_ap1219cr1w_5in_coupling_v01_front.png`
- `previews/hisense_ap1219cr1w_5in_coupling_v01_side.png`
- `previews/hisense_ap1219cr1w_5in_coupling_v01_top.png`
- `previews/hisense_ap1219cr1w_5in_coupling_v01_detail_tabs.png`

No AI-generated imagery was used. The preview files are simple STL renders only.
