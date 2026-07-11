# Reconstruction Notes

## task mode

`reference_based_reconstruction`

## target part

Single bumper-mounted fog light housing / bucket reconstructed for the CAT CT660 fog light opening shown in the user photos.

The CAT CT660 is the authoritative target vehicle platform for this v02. Public sources indicate the CT660 was built by Navistar / International-family manufacturing and shares vocational-truck conventions with that family, but this reconstruction target is specifically the CAT CT660 housing shown in the user photos, not a generic International part.

## what is reused

- the existing CAT CT660 bumper and its fog-light opening
- the existing fog lamp or lamp-size interface as a fit target only
- the existing mounting concept and surrounding bumper geometry

## what is not modeled

- the full truck bumper
- the fog lamp assembly beyond a circular clearance and seating interface
- wiring, bulb, lens, adjusters, or unrelated brackets
- any verified OEM part number claim

## authoritative references

Primary detached-part geometry references:

- `references/measured/cat_ct660_fog_light_housing/3520.jpg`
- `references/measured/cat_ct660_fog_light_housing/3521.jpg`

User-provided CAT CT660 context photos:

- `references/measured/cat_ct660_fog_light_housing/image_e36f1283-0f75-434b-8121-186974821d42.png`
- `references/measured/cat_ct660_fog_light_housing/image_e36f1283-0f75-434b-8121-186974821d42 (2).png`
- `references/measured/cat_ct660_fog_light_housing/image_4fabd419-154b-453d-a13c-4c077ff03470.png`

User-provided authoritative statements:

- target vehicle platform is `CAT CT660`
- the part is approximately `10 in` wide at the longest point, used only as a soft anchor at approximately `254 mm`

## supporting references

- prior supporting seed only, not authoritative:
  `projects/international_workstar_fog_light_housing/source/international_workstar_fog_light_housing_v01.scad`
- Cat CT660 technical specifications PDF noting a `3-piece T-304 stainless steel bumper` and `optional ... fog lights`, accessed 2026-04-19:
  <https://s3.amazonaws.com/drivecat/downloads/overview/CT660-Technical-Specifications.pdf>
- Cat parts listing `444-6431` for a `Bumper Fog Light` compatible with `CT660`, accessed 2026-04-19:
  <https://parts.cat.com/en/catcorp/product/444-6431>
- FleetOwner article noting the CT660 was built by Navistar and assembled where the International PayStar was built, accessed 2026-04-19:
  <https://www.fleetowner.com/operations/article/21684466/cat-shows-its-first-truck>
- Construction Equipment article stating the CT660 is based on the International PayStar 5000 and built at Navistar's vocational truck plant, accessed 2026-04-19:
  <https://www.constructionequipment.com/field-test/article/10727499/cat-trucks-show-premium-features>

These supporting references were used only for vehicle-family context and bumper/fog-light plausibility. They were not used to invent missing dimensions.

## reference trust order used

1. detached-part user photos `3520.jpg` and `3521.jpg`
2. user-provided CAT CT660 installed-context photos
3. user-provided CAT CT660 vehicle identification
4. user-provided approximate width
5. prior International-family CAD seed as supporting only
6. public CAT / Navistar / truck-family references as supporting only

## anchor dimensions

- soft width anchor from user statement: `overall body width approximately 254 mm`
- photo-proportion estimate for body height: `approximately 146 mm`
- photo-proportion estimate for shell depth to rear wall and boss region: `approximately 86 mm`
- photo-proportion estimate for collar outer diameter: `approximately 110 mm`
- photo-proportion estimate for collar clear opening: `approximately 88 mm`

## authoritative dimensions used

No caliper-confirmed dimensions were available during this run.

Estimated from user statement:

- `254 mm` overall width anchor

Estimated from photo proportion:

- `146 mm` body height
- `86 mm` body depth
- `110 mm` collar outer diameter
- `126 mm` rear collar pad diameter
- `97 mm` seat diameter
- `88 mm` clear opening diameter
- three rear stud-center positions

Inherited from prior supporting v01 seed, then revised in v02:

- hulled section workflow for bumper-face curvature
- basic collar / rear boss module structure
- overall single-piece parametric bucket strategy

Unknown / needs caliper confirmation:

- exact collar clear diameter and seating lip depth
- exact stud diameters and stud-center distances
- bumper-contact flange thickness variation around the perimeter
- exact rear-wall angle and right-side cavity taper

Verified generated STL mesh extents in this environment:

- exported v02 mesh including rear studs and ribs: `264.82 x 112.30 x 150.98 mm`

## protected interfaces

- circular fog lamp collar location, diameter, and wall thickness
- lamp seating lip geometry
- rear mounting boss pattern
- mounting stud / fastener center locations
- bumper-contact perimeter curve on the visible face
- overall left/right asymmetry and angled side walls

## reinforced zones

- rear stud boss bases were gusseted
- rear collar pad was thickened for stiffness
- three shallow rear-side ribs were added in non-interface zones to support the boss field and rear wall

## low-confidence zones

- exact collar seat geometry and lamp-retention details
- exact stud-center spacing from a common datum
- exact bumper-face curvature at the installed CT660 opening
- exact right-side wall depth and rear-wall lean
- whether the shown housing is the same hand as the installed-context image or the mirrored mate

## comparison status

Qualitative compare-and-revise was completed against:

- detached part front and rear photos
- CAT CT660 installed context photos
- prior International-family v01 seed as supporting geometry only

v02 comparison focus:

- bounding box
- front silhouette
- side silhouette
- top silhouette / plan asymmetry
- circular opening location
- rear boss / stud layout
- bumper-face curvature

No pixel-registered overlay or direct physical measurement was available, so v02 remains measurement-gated.

## pass/fail on critical features

- bounding box intent: pass as a soft-anchor reconstruction
- front silhouette: pass with improved CAT bumper-opening likeness over the seed model
- side silhouette: partial pass; taper and depth improved, rear-wall lean still estimated
- top silhouette: partial pass; asymmetry preserved, curvature remains approximate
- circular opening location: pass for the detached-part reference
- rear boss / stud layout: partial pass; represented faithfully in concept, still photo-estimated
- bumper-face curvature: partial pass; v02 deepened the bow compared with the seed model, but the exact installed contour is still unmeasured

## print orientation

Recommended FDM orientation: print with the broad front mouth / bumper-contact lip facing down on the build plate and the rear studs pointing up.

This keeps the collar axis vertical, reduces support inside the visible cavity, and preserves the lamp opening more accurately.

## support plan

- PETG or ASA assumed by default for outdoor utility use
- use a brim because the front lip is broad and slightly curved
- keep supports limited to the rear stud placeholders and isolated rear overhangs
- block supports from filling the main visible cavity whenever possible
- if the front lip does not sit stably, use slicer-added support blockers plus local support enforcers only at low perimeter corners

## next revision actions

- capture direct measurements of width, height, depth, and perimeter flange thickness from the real part
- measure collar clear diameter, seat diameter, and collar wall thickness
- measure all three rear stud centers from a fixed datum
- verify whether the printed stud placeholders should become hardware bores, inserts, or bonded studs in v03
- check handedness against the installed CAT CT660 bumper opening before production printing

## exported STL filename

`exports/cat_ct660_fog_light_housing_v02.stl`

## STL export status

Success. `openscad` exported `exports/cat_ct660_fog_light_housing_v02.stl` locally in this environment on 2026-04-19, and the resulting mesh loaded successfully in `trimesh` as a watertight single connected body.

## future 3MF status

No 3MF package was generated in this run. 3MF remains a future packaging step after real-world fit confirmation.

## remaining mismatch notes

- This is a best-faith reconstruction for a CAT CT660 fog light housing using user photos and user vehicle identification as the primary references.
- No verified OEM part number was confirmed in this run.
- The collar, stud spacing, and bumper-contact curve remain measurement-gated.
- Preview images were intentionally not generated because the user explicitly requested a non-visual task.

## what changed from v01 to v02

No CAT-specific `projects/cat_ct660_fog_light_housing/*_v01` artifacts existed in the repo at the start of this run, so there was no CAT v01 to revise in place.

Relative to the earlier International-family supporting seed used for geometry guidance:

- vehicle context was retargeted explicitly to `CAT CT660`
- the front perimeter profile was revised to better match the CAT bumper opening photos
- bumper-face curvature was increased by adding more depth sections to the shell and cavity
- body depth increased by about `4 mm` while overall height dropped by about `1 mm`
- collar and rear stud locations were nudged to better match the detached-part photos
- shallow rear reinforcement ribs were added in non-interface zones
- a recessed rectangular inner rear-wall detail was added to better reflect the visible bucket interior
