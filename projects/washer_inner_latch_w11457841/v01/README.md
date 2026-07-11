# washer_inner_latch_W11457841

Replacement project for the broken **inner spring-loaded latch insert only** from Whirlpool washer lid strike assembly `W11457841`, used on washer model `WTW8127LC0`.

The original round twist-lock carrier is intended to be reused.
This project does **not** target the full carrier as the primary replacement.

## Safety Note

This is a user-made replacement concept for a safety-interlock-related mechanism.
It is **not** a bypass device.
Only use it as a legitimate replacement insert inside an otherwise intact strike assembly and confirm normal lid-lock behavior before regular operation.

## Project Purpose

- Replace only the broken moving insert
- Preserve fit in the existing carrier
- Preserve washer-side lock engagement geometry
- Reuse the original torsion spring where possible
- Maximize first-print success by providing both a high-fidelity and simplified family

## Design Families

### Version A: High Fidelity Insert

- File: `scad/inner_latch_full_fidelity.scad`
- Intent: closest practical reconstruction of the original moving insert
- Best for: users trying to reuse the original spring and keep the original motion as closely as practical
- Main tradeoff: more geometry detail and slightly higher fit risk on the first try

### Version B: Simplified Functional Insert

- File: `scad/inner_latch_simplified.scad`
- Intent: stronger, more printable fallback that still preserves the critical carrier-fit and lock-engagement geometry
- Best for: fastest route to a working washer
- Main tradeoff: less exact upper-body detail than the OEM insert

## Recommended First Print Order

1. `inner_latch_simplified_test_fit.stl`
2. `inner_latch_simplified.stl`
3. `inner_latch_reinforced_simplified.stl`
4. `inner_latch_full_fidelity_test_fit.stl`
5. `inner_latch_full_fidelity.stl`

## Concept Comparison

| Concept | Summary | Why it exists |
|---|---|---|
| A | Near-OEM insert with spring-facing detail | Preserves the original mechanism concept as closely as practical |
| B | Stronger simplified insert | Highest chance of first-print success |
| C | Carrier-fit gauge / mock socket | Bench-check helper for insert fit and pivot capture |

## Selected Concept Logic

The simplified family is the primary first-print path because daily usability and printability matter most here.
The high-fidelity family is still included because the original mechanism is spring-loaded and the spring-contact geometry may matter in the intact carrier.

## Carrier Reuse Strategy

- Intended retention: pivot/capture by the insert's horizontal bar into the original carrier
- Intended spring reuse: transfer the original torsion spring to Version A first if the carrier and spring are intact
- Expected cleanup: remove broken plastic remnants and confirm the original carrier sockets are not cracked or spread
- Helper geometry: `carrier_fit_gauge.stl` provides a bench socket for quick fit checks outside the washer

## Print Settings

- Primary test material: `PETG`
- Preferred materials: `ABS`, `ASA`, `Nylon`
- Not primarily optimized for `PLA`
- Layer height: `0.16 mm` or `0.20 mm`
- Walls: `5 to 6`
- Infill: `100%` for functional tests
- Recommended nozzle: `0.4 mm`

## Orientation

- Print the latch on its broad side so the pivot bar is horizontal in the print.
- This improves strength across the lower hook/step and the break-prone neck.
- Supports:
  - simplified: none to minimal
  - full fidelity: minimal if the upper hook underside needs support cleanup

## Install Notes

1. Remove the broken insert and keep the intact round carrier.
2. Inspect the carrier pivot sockets and spring pocket for damage.
3. If reusing the original spring, note its leg orientation before removal.
4. Test the insert in the carrier by hand before reinstalling the carrier in the lid.
5. Confirm the latch returns and presents the engagement face correctly before washer testing.

## Fit Test Notes

- The `*_test_fit.stl` variants reduce carrier-contact dimensions by about `0.18 mm` where appropriate.
- The engagement face and lock-facing step are kept as close to nominal as possible.
- Use the test-fit versions to check:
  - pivot bar snap-in behavior
  - guide-pad clearance
  - spring seating
  - travel-stop interference

## Likely Failure Points

- Mid-body break-plane region
- Spring-tab root
- Pivot bar if the carrier side pockets are overly tight
- Upper stop hook if printed in brittle material

## Artifact Guide

- `scad/common_params.scad`
- `scad/inner_latch_full_fidelity.scad`
- `scad/inner_latch_simplified.scad`
- `scad/inner_latch_test_fit.scad`
- `scad/carrier_fit_gauge.scad`
- `stl/inner_latch_full_fidelity.stl`
- `stl/inner_latch_full_fidelity_test_fit.stl`
- `stl/inner_latch_simplified.stl`
- `stl/inner_latch_simplified_test_fit.stl`
- `stl/inner_latch_reinforced_simplified.stl`
- `stl/carrier_fit_gauge.stl`
- `renders/top_view.png`
- `renders/side_view.png`
- `renders/underside_view.png`
- `renders/installed_mockup.png`
- `renders/exploded_view.png`
- `references/photo_feature_map.md`
- `references/dimensional_sketches.md`
- `references/grid_photo_notes.md`
- `DESIGN_NOTES.md`

## Verification Checklist

- [ ] Broken insert removed cleanly
- [ ] Carrier pockets intact
- [ ] Spring reusable or intentionally omitted for the chosen test
- [ ] Test-fit insert seats without forcing
- [ ] Lock engagement face matches original presentation
- [ ] Insert returns freely inside the carrier
- [ ] Washer lock operates normally
- [ ] Replacement is used as a real repair, not a bypass
