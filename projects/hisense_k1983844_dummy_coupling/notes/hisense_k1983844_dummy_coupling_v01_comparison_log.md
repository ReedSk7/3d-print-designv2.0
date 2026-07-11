# Reference Comparison Log

## date/revision

2026-04-22 / `v01`

## current version

`hisense_k1983844_dummy_coupling_v01`

## reference used

- `references/measured/hisense_k1983844_dummy_coupling/ac_vent_tube_adapter.stl`

## bbox comparison

- reference STL bbox after print-orientation transform: `164.000 x 162.000 x 57.500 mm`
- rebuilt v01 bbox: `164.000 x 162.000 x 57.500 mm`
- delta (v01 - reference): `0.000 x -0.000 x 0.000 mm`

## silhouette comparison

- front silhouette IoU: `0.9887`
- side silhouette IoU: `0.9902`
- top silhouette IoU: `0.6436`
- front and side views remained close because the supplied outer shell was preserved.
- top view diverges because the remodeled inner reducer and seating lip intentionally change the visible opening from above.

## critical feature comparison

- square flange perimeter and tab placement:
  - reference: from supplied STL
  - v01: preserved by direct STL shell reuse
- circular locking collar outer shell:
  - reference: from supplied STL
  - v01: preserved by direct STL shell reuse
- round collar opening:
  - reference: about `156 mm` bore in the preserved round zone
  - v01 throat near `z = 45.0 mm`: about `126.85 mm`
- seating lip check at `z = 50.0 mm` and `z = 56.0 mm`:
  - v01 lip OD: `126.00 mm`
  - v01 lip bore: `122.00 mm`
- STL watertight status:
  - reference: yes
  - v01: yes

## mismatches found

- the internal collar opening is intentionally smaller than the reference STL
- top-view projection differs because the new lip is visible from above
- the user-requested `127 mm` nominal target cannot exist at the exact same section as a `126 mm` outer lip, so v01 treats `127 mm` as the transition throat immediately behind the seating lip

## corrections planned

No further CAD correction is planned before physical hose testing. Any next change should be driven by real PETG fit on the user's hose.

## confidence level

High for preserving the supplied outer locking geometry. Medium for the 5 in hose fit until the printed part is physically tested.
