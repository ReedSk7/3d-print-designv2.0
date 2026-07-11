# Reference Comparison Log

## date/revision

- date: `2026-04-19`
- revision: `v01`

## current version

`projects/international_workstar_fog_light_housing/source/international_workstar_fog_light_housing_v01.scad`

## reference used

Authoritative:

- `references/measured/international_workstar_fog_light_housing/3520.jpg`
- `references/measured/international_workstar_fog_light_housing/3521.jpg`
- user estimate that the longest width is around `10 in`

Supporting only:

- Tacoma Parts Corporation WorkStar 7000 bumper listing with fog light holes
- MiamiStar WorkStar 7400/7600 bumper listing with fog light holes

## bbox comparison

- body width target was anchored at approximately `254 mm` from the user statement
- modeled body envelope was built around `254 x 149 x 82 mm`
- exported mesh extents including rear studs and bosses measured `263.93 x 108.30 x 151.95 mm`
- bbox status: acceptable for a v01 photo reconstruction, but still measurement-gated

## silhouette comparison

- front silhouette: broad trapezoidal mouth with a stronger left shoulder and a more vertical right wall captured
- side silhouette: bucket depth and rearward taper captured, exact rear wall lean still estimated
- top silhouette: asymmetry preserved and right-side taper maintained, bumper curvature remains simplified

## critical feature comparison

- circular opening is offset toward the lower-left area of the front mouth as shown in the photos
- rear collar pad was added to capture the thickened lamp interface seen from the back
- four small lamp-retention bosses were included around the collar as estimated placeholders
- three visible rear mounting stud locations were represented with gusseted bosses
- non-interface reinforcement was kept to the rear bosses and collar pad

## mismatches found

- exact collar diameter and lamp seat depth are not confirmed
- the stud-center spacing is inferred from perspective photos, not measured from a datum
- the bumper-contact perimeter curvature is approximated from the photos rather than traced from the truck opening
- the right-side wall depth and inner rear-wall angle are still low confidence

## corrections planned

- measure real collar diameters and transfer them into the top-level parameters
- replace inferred stud-center positions with measured coordinates
- tune the bumper-contact perimeter after a physical test fit against the bumper opening
- decide whether the rear studs should become hardware-ready bores or inserted metal studs in v02

## confidence level

Moderate for overall form and feature placement.

Low-to-moderate for exact fit-critical dimensions until direct measurements are captured.
