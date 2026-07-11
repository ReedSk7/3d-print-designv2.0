# Reconstruction Notes

## task mode

`reference_based_reconstruction`

## target part

Single bumper-mounted fog light housing / bucket reconstructed from the provided user photos for an International dump truck application, likely within the WorkStar / 7000-series family based on supporting bumper references. This v01 is not verified to a specific OEM part number.

## what is reused

- the existing truck bumper and its fog-light opening
- the existing fog lamp or lamp-size interface as a measurement target only
- the existing bumper mounting hardware concept and stud-center pattern

## what is not modeled

- the full truck bumper
- the fog lamp assembly beyond a simple circular clearance interface
- wiring, bulb, lens, adjusters, or unrelated bracket assemblies
- any claim of exact OEM part-number identity

## authoritative references

- `references/measured/international_workstar_fog_light_housing/3520.jpg`
- `references/measured/international_workstar_fog_light_housing/3521.jpg`
- user statement that the longest width is approximately `10 in`, used only as a soft anchor at approximately `254 mm`

## supporting references

- Tacoma Parts Corporation listing for a `13"` chrome bumper with fog light holes compatible with International WorkStar 7000 Series, accessed 2026-04-19: <https://tacoma-truckparts.com/products/13-chrome-bumper-with-fog-light-holes-international-workstar>
- MiamiStar listing for a `16"` chrome bumper with tow and fog light holes for International WorkStar 7400 and 7600, accessed 2026-04-19: <https://miamistar.com/products/16-chrome-bumper-intl-workstar-7400-7600-fog-light-and-tow-hole>

These supporting references were used only to support likely vehicle-family context. They were not used to invent hidden geometry or override the user photos.

## reference trust order used

1. user photos
2. user-provided approximate overall width
3. supporting public bumper listings for truck-family context only

## anchor dimensions

- soft width anchor from user statement: `overall body width approximately 254 mm`
- photo-proportion estimate for visible body height: `approximately 149 mm`
- photo-proportion estimate for shell depth to rear wall/stud base region: `approximately 82 mm`
- photo-proportion estimate for fog collar outer diameter: `approximately 108 mm`
- photo-proportion estimate for fog clearance diameter: `approximately 88 mm`

## authoritative dimensions used

No caliper-confirmed dimensions were available during this run.

Numerically anchored values used in v01:

- `254 mm` overall body width from the user statement, explicitly treated as approximate

Photo-driven dimensions used as estimated reconstruction values:

- `149 mm` body height
- `82 mm` body depth
- `108 mm` collar outer diameter
- `124 mm` rear collar pad diameter
- `88 mm` collar clear opening diameter
- three rear stud-center positions inferred from the rear photo

Verified generated STL mesh extents in this environment:

- overall exported mesh including rear studs and bosses: `263.93 x 108.30 x 151.95 mm`

## protected interfaces

- circular fog lamp collar location
- collar wall thickness and front seating step
- rear collar pad around the lamp opening
- rear mounting boss / stud-center layout
- broad bumper-contact perimeter and asymmetric front mouth
- left/right asymmetry of the side walls and rear taper

## reinforced zones

- rear stud boss bases were thickened and gusseted
- rear collar pad was enlarged behind the opening for better local stiffness
- reinforcement stayed on the rear face and boss regions, not on the visible front mouth lip

## low-confidence zones

- exact collar clear diameter and seating-step depth
- precise stud-center spacing and stud diameter
- exact amount of bumper-face curvature across the visible perimeter
- exact rear-wall angle and right-side cavity depth
- small lamp-retention boss pattern around the circular opening

## comparison status

Qualitative compare-and-revise was completed against the two user photos, focusing on:

- bounding box intent
- front silhouette
- side silhouette
- top-plan asymmetry
- circular opening location
- rear boss / stud layout
- bumper-face curvature

No pixel-registered overlay was available, so v01 remains measurement-gated rather than fully verified.

## pass/fail on critical features

- bounding box intent: pass for the body envelope; still approximate because only width had a numerical anchor
- front silhouette: pass for the broad asymmetric trapezoidal mouth, left rolled shoulder, and right-side taper
- side silhouette: partial pass; general bucket depth and taper are captured, exact rear-wall lean remains estimated
- top silhouette: partial pass; left/right asymmetry is preserved, but bumper curvature is still approximate
- circular opening location: pass as a photo-faithful lower-left offset opening
- rear boss / stud layout: partial pass; all three visible rear stud locations are represented, but spacing remains photo-estimated
- bumper-face curvature: partial pass; represented as a mild sectional curve rather than a scan-accurate surface

## print orientation

Recommended FDM orientation for v01: print with the broad front mouth / bumper-contact lip facing down on the build plate and the rear studs pointing up.

This keeps the collar axis vertical, preserves the circular opening better, and avoids filling the visible cavity with dense support.

## support plan

- use PETG or ASA as the default material assumption
- use a wide brim because the front lip perimeter is broad but not perfectly rectangular
- keep supports limited to the rear stud placeholders and any isolated rear boss overhangs
- block supports from filling the main visible cavity whenever possible
- if the front lip rocks on the plate, add temporary slicer shims or a sacrificial setup base under the lowest perimeter areas

## next revision actions

- measure the real part or bumper opening width, height, and depth with calipers or a ruler
- measure collar clear diameter, collar seat diameter, and wall thickness directly from the surviving part
- measure all three rear stud-center locations from a shared datum
- confirm whether the printed stud placeholders should become metal-threaded inserts or captured hardware in v02
- compare the bumper-contact perimeter against the truck opening and tune the curvature locally

## exported STL filename

`exports/international_workstar_fog_light_housing_v01.stl`

## STL export status

Success. `openscad` exported `exports/international_workstar_fog_light_housing_v01.stl` locally in this environment on 2026-04-19, and the resulting mesh loaded successfully in `trimesh` as a watertight single connected body.

## future 3MF status

No 3MF package was generated in this run. 3MF remains a future enhancement after real-world fit confirmation.

## remaining mismatch notes

- This is a best-faith reconstruction for an International dump truck fog light housing, likely in the WorkStar / 7000-series family based on public bumper listings with fog light holes, but it is not verified to a specific OEM part number.
- The collar and rear stud pattern are functional placeholders until direct measurements are captured.
- Front/rear preview images were intentionally not generated because the user explicitly requested a non-visual task. STL export was completed and verified.
