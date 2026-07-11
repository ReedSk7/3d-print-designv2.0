# DESIGN_NOTES

Project: `washer_inner_latch_W11457841`
Date: `2026-04-14`
Scope: replacement of only the broken inner spring-loaded latch insert from strike assembly `W11457841`

## Requirements Summary

- Replace only the broken moving inner latch insert
- Reuse the intact round carrier
- Reuse the original spring if practical
- Preserve real lock engagement geometry
- Preserve carrier fit surfaces
- Provide both a high-fidelity and simplified fallback design
- Provide test-fit variants
- Provide a helper carrier-fit gauge
- Use PETG minimum, with ABS/ASA/Nylon preferred for real use

## Concept Directions

| Concept | Description | Daily usability | Printability | Attachment reliability | Finger access / handling | Publishability | Material efficiency | Parametric flexibility | Weighted total |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | Near-OEM insert with spring-facing details and carrier-fit bar | 4 | 3 | 4 | 3 | 4 | 3 | 4 | 365 |
| B | Simplified one-piece insert that keeps fit and engagement but strengthens the weak neck | 5 | 5 | 4 | 4 | 4 | 4 | 5 | 450 |
| C | Diagnostic carrier-fit gauge / mock socket only | 2 | 5 | 2 | 5 | 2 | 5 | 4 | 325 |

## Selected Concept Justification

- Concept `B` is the best first-print path because it maximizes the chance of a successful carrier fit and working lock engagement on the first test.
- Concept `A` is still included because the original part is spring-loaded and the user explicitly asked for a higher-fidelity spring-reuse attempt.
- Concept `C` is not a replacement by itself, but it is useful as a fit/debug helper because the intact carrier is being reused.

## Parameter Plan

- `latch_body_width = 19.3`
- `latch_body_height = 27.8 to 28.1`
- `latch_body_depth = 8.8 to 8.9`
- `engagement_face_width = 19.3`
- `engagement_face_depth = 5.0 to 5.1`
- `top_hook_width = 8.4 to 8.6`
- `top_hook_depth = 2.9 to 3.0`
- `left_feature_width = 7.6`
- `right_feature_width = 1.9`
- `spring_contact_width = 3.2 to 3.4`
- `spring_contact_depth = 2.2 to 2.3`
- `guide_rail_width = 2.0 to 2.1`
- `guide_rail_height = 5.3 to 5.5`
- `pivot_or_capture_diameter = 3.1`
- `clearance_to_carrier = 0.15`
- `test_fit_reduction = 0.18`
- `break_plane_reference = 13.8 to 13.9`

## Assumptions From Photo Interpretation

- The broken insert is the moving latch element, not the round carrier.
- The insert likely pivots in the carrier by a molded horizontal bar.
- The torsion spring wraps that bar and bears against a small insert tab.
- The lower engagement geometry is the most important area for washer-side function.
- The upper hook and side pads are primarily carrier guidance / stop features.

## Dimensions Anchored From User Caliper Readings

- `19.3 mm` lower engagement width
- `28.1 mm` upper fit / beveled / insertion-related width
- `7.6 mm` left-side feature
- `1.9 mm` right-side feature

## Dimensions Inferred From The Grid Photo

- Total insert height below the capture region is about `28 mm`
- Pivot/capture bar diameter is about `3 mm`
- Guide-pad height is about `5 to 5.5 mm`
- Upper hook depth is about `3 mm`

## Highest Confidence Areas

- Lower engagement width and lower strike silhouette class
- Intentional asymmetry of the side features
- Presence of a pivot/capture bar
- Presence of a spring-contact tab near the pivot

## Lowest Confidence Areas

- Exact travel-stop geometry hidden by the spring and carrier walls
- Exact torsion spring preload angle
- Exact underside pocketing in the OEM molded part

## Carrier Reuse Strategy

- Intended retention mode: `pivot / snap into existing carrier side pockets`
- Intended spring strategy for Version A: `reuse original torsion spring if it can be transferred`
- Intended spring strategy for Version B: `still includes spring-contact geometry, but upper-body detail is simplified`
- Cleanup expectation: remove burrs from the broken original and inspect the carrier pivot sockets before installing the new insert

## Geometry Review

- Pass after corrective pass
- The first pass looked too slab-like through the lower arm and left too little visual distinction at the break-prone neck.
- Corrective pass retained the square lock face but added a more intentional neck transition, relief cuts, asymmetrical side features, and a dedicated reinforcement option.
- Mass reduction strategy:
  - root relief pockets
  - tip relief pocket
  - optional reinforcement only where the original break risk is highest

## Printability Review

- Recommended orientation:
  - print with the broad side of the latch body on the bed
  - keep the pivot bar horizontal in the print
  - this gives the strongest result across the hook/step and lower engagement block
- Supports:
  - none to minimal for simplified
  - minimal for full fidelity if the upper hook overhang needs cleanup
- Likely weak points:
  - the neck at the break-plane region
  - the spring-tab root if printed in brittle material
  - the pivot bar if the carrier sockets are overly tight

## Design-Quality Review

- Front-view quality: intentional enough for a functional hidden insert
- Side-profile quality: acceptable and not a pure rectangular test block
- Publishability: acceptable for a repair part, with Version B stronger than Version A for real-world use
- Chunky prototype risk: reduced by adding root reliefs, stepped tip geometry, and asymmetrical carrier-side features

## Most Likely To Work First

1. `inner_latch_simplified_test_fit.stl`
2. `inner_latch_simplified.stl`
3. `inner_latch_reinforced_simplified.stl`
4. `inner_latch_full_fidelity_test_fit.stl`
5. `inner_latch_full_fidelity.stl`
