# Reference Comparison Log

## date/revision

- date: `2026-04-19`
- revision: `v02`

## current version

`projects/cat_ct660_fog_light_housing/source/cat_ct660_fog_light_housing_v02.scad`

## reference used

Authoritative primary geometry:

- `references/measured/cat_ct660_fog_light_housing/3520.jpg`
- `references/measured/cat_ct660_fog_light_housing/3521.jpg`

Authoritative vehicle-context support:

- `references/measured/cat_ct660_fog_light_housing/image_e36f1283-0f75-434b-8121-186974821d42.png`
- `references/measured/cat_ct660_fog_light_housing/image_e36f1283-0f75-434b-8121-186974821d42 (2).png`
- `references/measured/cat_ct660_fog_light_housing/image_4fabd419-154b-453d-a13c-4c077ff03470.png`
- user statement that the truck is a `CAT CT660`
- user statement that the part is around `10 in` wide

Supporting only:

- `projects/international_workstar_fog_light_housing/source/international_workstar_fog_light_housing_v01.scad`
- public CAT CT660 / Navistar / bumper context references listed in the notes file

## bbox comparison

- intended body envelope was built around approximately `254 x 146 x 86 mm`
- verified exported v02 mesh extents including rear studs and ribs: `264.82 x 112.30 x 150.98 mm`
- compared with the supporting International-family seed STL, v02 changed extents by approximately:
  - `+0.89 mm` overall width
  - `+4.00 mm` overall depth
  - `-0.97 mm` overall height
- bbox status: acceptable as a CAT-specific refinement, still measurement-gated

## silhouette comparison

- front silhouette: revised to a softer CAT bumper-opening mouth with a smoother upper-left shoulder and slightly fuller right-side wall
- side silhouette: deepened shell and slightly revised rear-wall progression
- top silhouette: preserved asymmetry and increased bumper-face bow relative to the seed model

## critical feature comparison

- circular opening remains offset toward one side of the housing as shown in the detached-part photos
- rear collar pad remains the dominant rear interface
- three visible rear stud locations are still represented
- lamp-retention bosses remain present around the collar
- new rear ribs were limited to non-interface zones only
- a shallow rectangular rear-wall recess was added to better reflect the visible interior feature in the detached front view

## mismatches found

- exact handedness versus the installed CT660 opening is still not fully proven from the photo set alone
- stud-center spacing remains photo-estimated
- collar seat diameter and seating depth remain unmeasured
- bumper-contact curvature is closer than the seed model but still not scan-accurate

## corrections planned

- confirm handedness against the actual truck side before production use
- replace inferred stud coordinates with measured values
- tune collar clear and seat diameters from the real part
- test the flange perimeter against the bumper opening and adjust local curvature if needed

## confidence level

Moderate for overall form, asymmetry, and general mounting concept.

Low-to-moderate for exact fit-critical dimensions until direct measurements are captured.
