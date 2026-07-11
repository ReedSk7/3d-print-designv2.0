# Reconstruction Notes

## task mode

`mesh_cleanup_and_remodel`

## target part

Modified Hisense-style portable AC dummy coupling / outlet adapter in the K1983844 geometry family, rebuilt to preserve the supplied outer locking interface while adapting the hose-side collar for a standard nominal 5 in hose.

## what is reused

- supplied dummy-coupling outer shell and locking geometry from the user STL
- Hisense rear outlet interface that mates to that shell
- standard nominal 5 in portable AC hose

## what is not modeled

- AC housing
- hose threads or hose body
- clamps, gaskets, or seals separate from the printed part

## authoritative references

- `references/measured/hisense_k1983844_dummy_coupling/ac_vent_tube_adapter.stl`
- user-requested fit targets:
  - nominal 5 in hose target
  - `127 mm` nominal opening target
  - `126 mm` hose seating lip OD
  - `120 to 122 mm` bore behind the lip
  - `10 to 15 mm` lip depth

## supporting references

- `references/measured/hisense_k1983844_dummy_coupling/IMG_20260422_171512.jpg`
- `references/measured/hisense_k1983844_dummy_coupling/IMG_20260422_171525.jpg`
- `references/measured/hisense_k1983844_dummy_coupling/IMG_20260422_171520.jpg`
- `references/measured/hisense_k1983844_dummy_coupling/IMG_20260422_171529.jpg`
- `references/measured/hisense_k1983844_dummy_coupling/IMG_20260421_202246.jpg`
- `references/measured/hisense_k1983844_dummy_coupling/IMG_20260421_202248.jpg`

## reference trust order used

1. supplied watertight STL was treated as authoritative for the protected outer locking interface
2. user-stated hose fit targets were treated as authoritative for the remodeled lip and throat
3. phone photos were used as supporting context for the Hisense rear interface and nominal hose size only

## anchor dimensions

- print-oriented reference mesh bbox: `164.000 x 162.000 x 57.500 mm`
- print-oriented rebuilt bbox: `164.000 x 162.000 x 57.500 mm`
- existing round collar bore in the preserved STL: about `156 mm`
- rebuilt nominal throat near `z = 45.0 mm`: about `126.85 mm`
- rebuilt hose seating lip near `z = 50.0 mm` and `z = 56.0 mm`:
  - outer lip diameter: `126.00 mm`
  - inner bore diameter: `122.00 mm`
- effective lip depth including the entry chamfer: `10.0 mm`

## authoritative dimensions used

- nominal hose target: `127.0 mm`
- hose seating lip OD: `126.0 mm`
- bore through the seating lip: `122.0 mm`
- slight entry chamfer at the hose-side lip edge

## protected interfaces

- square flange perimeter and thickness envelope from the supplied STL
- circular locking collar outer shell from the supplied STL
- locking notch and tab positions from the supplied STL
- overall part envelope and bed-facing flange face

## reinforced zones

- inside the round collar only
- remodeled reducer shell from the preserved collar wall down to the 5 in seating lip

## low-confidence zones

- final PETG friction fit with the user's exact hose cuff
- whether the user will prefer `122 mm` or a slightly looser `121 mm` lip bore after real test fitting
- whether a printed gasket or foam tape is needed for the AC-side seal

## comparison status

Completed locally against a print-oriented copy of the supplied STL.

- bbox delta vs reference STL: `0.000 x -0.000 x 0.000 mm`
- silhouette IoU vs reference STL:
  - front: `0.9887`
  - side: `0.9902`
  - top: `0.6436`

The front and side views stay close because the protected outer geometry was preserved. The top-view difference is expected because the new inner reducer and hose lip intentionally change the visible opening from above.

## pass/fail on critical features

- square flange outer envelope: pass by direct reuse of the supplied STL shell
- circular locking collar outer shell: pass by direct reuse of the supplied STL shell
- locking tab / notch placement: pass by direct reuse of the supplied STL shell
- nominal 5 in hose reducer intent: pass locally
- `126 mm` hose seating lip OD: pass locally by section check
- `122 mm` lip bore: pass locally by section check
- `127 mm` nominal throat target: pass locally as an approximately `126.85 mm` transition throat ahead of the lip
- watertight single-body STL export: pass locally
- physical hose fit: not verified

## print orientation

Square flange on the bed with the circular collar and seating lip rising upward.

## support plan

Target a support-light PETG print with no supports by default. The new reducer shell grows inward from the preserved collar wall instead of starting as a flat shelf. Review slicer overhang preview around the start of the internal reducer, but the design intent is flat-on-bed printing without support.

## next revision actions

- test-fit the printed lip to the actual 5 in hose cuff
- if PETG fit is too tight, try reducing the lip OD by `0.2 to 0.4 mm`
- if hose retention is too loose, increase lip depth or add a small bead
- confirm whether the AC-side seal needs gasket tape

## exported STL filename

`exports/hisense_k1983844_dummy_coupling_v01.stl`

## STL export status

Success. `exports/hisense_k1983844_dummy_coupling_v01.stl` exported locally from OpenSCAD and loaded successfully as a watertight mesh.

## future 3MF status

Not created.

## remaining mismatch notes

The outer shell was preserved from the supplied STL, but the internal collar opening was intentionally remodeled. The user requested a `127 mm` nominal 5 in target alongside a `126 mm` seating lip and `120 to 122 mm` bore range. This build interprets that as a `126 mm` PETG-friendly seating lip with a `122 mm` bore and an approximately `127 mm` transition throat immediately behind it.
