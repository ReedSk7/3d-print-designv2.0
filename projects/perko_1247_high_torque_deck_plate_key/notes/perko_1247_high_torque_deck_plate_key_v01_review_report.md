# Review Report

## Proposed Repo Artifacts

- source: `source/perko_1247_high_torque_deck_plate_key_v01.scad`
- STL: `exports/perko_1247_high_torque_deck_plate_key_v01.stl`
- optional STL: `exports/perko_1247_high_torque_deck_plate_key_v01_metal_pin_body.stl`
- previews: `previews/perko_1247_high_torque_deck_plate_key_v01_iso.png`, `previews/perko_1247_high_torque_deck_plate_key_v01_front.png`, `previews/perko_1247_high_torque_deck_plate_key_v01_side.png`
- notes: `notes/perko_1247_high_torque_deck_plate_key_v01_notes.md`
- manifest: `notes/perko_1247_high_torque_deck_plate_key_v01_manifest.md`
- comparison log: `notes/perko_1247_high_torque_deck_plate_key_v01_reference_comparison_log.md`
- printability review: `notes/perko_1247_high_torque_deck_plate_key_v01_printability_review.md`
- release notes: `notes/perko_1247_high_torque_deck_plate_key_v01_release_notes.md`

## Verified Artifacts

- source: validated with `scripts/validate_scad.py`
- STL: default and metal-pin STLs exported and mesh-checked
- previews: iso, front, and side PNGs exported
- notes: drafted
- manifest: drafted

## STL Export Attempted

yes/no: yes

## Preview Render Attempted

yes/no: yes

## Measured Versus Inferred

- measured: protected lug dimensions supplied by user.
- inferred: handle silhouette, head width, grip width, root relief diameter, metal-pin boss sizing, metal-pin hole default.

## Low-Confidence Zones

- Actual cap-face clearance around lug roots.
- Actual press-fit or epoxy-fit behavior for the chosen dowel/bolt hardware.
- OEM Perko 1247 non-mating silhouette.

## Failure Points

- Printed lugs can still shear if printed upright or with poor PETG layer bonding.
- Root collars could prevent full seating if the cap face is flat around the holes.
- Metal-pin hole diameter must be tuned to the actual pin and printer.

## Printability Risks

Medium. The side-print orientation improves lug strength but needs supports and a brim.

## Next Corrective Actions

- Run physical fit-test on the actual cap.
- Tune the metal-pin hole diameter with a small coupon before installing hardware.
- Use the metal-pin body if the printed root collars interfere with cap-face clearance.
