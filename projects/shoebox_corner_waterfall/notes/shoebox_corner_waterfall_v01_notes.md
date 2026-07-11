# Original Design Notes

## Task Mode

`original_product_design`

## Goal

Create a one-piece decorative waterfall corner insert for a shoebox diorama. The piece glues into a 90 degree inside corner, presents stacked cliff rock texture, and includes a vertical waterfall dropping into a shallow splash pool.

## Constraints

- printer: FDM 0.4 mm nozzle
- material: PLA
- bed size: assumed at least 120 x 120 x 120 mm
- strength needs: decorative craft model, not load bearing
- heat exposure: indoor only
- outdoor exposure: none expected
- minimum feature/detail thickness: 1.2 mm

## Chosen Concept

Single upright corner wedge with flat X=0 and Y=0 glue faces, a wide flat base, a central raised waterfall ribbon, and raised rock ledges on both wall-side cliff faces. Two variants are generated from one source file:

- `simple`: fewer rock bands and water lines for faster printing.
- `detailed`: stronger rock texture, extra water streaks, extra splash/ripple details.

## Key Parameters

- overall height: 120 mm
- wall-side width: 70 mm on each shoebox wall
- center protrusion from either wall: 45 mm maximum at the visible front of the base
- base/splash pool footprint: approximately 70 mm x 70 mm corner footprint, faceted/chamfered at the exposed front
- back glue panels: 4 mm thick flat panels on both wall faces
- source file: `source/shoebox_corner_waterfall_source_v01.scad`
- variant selector: `variant = "simple"` or `variant = "detailed"`

## Print Orientation

Recommended orientation is upright on the flat bottom/base. The flat bottom gives the largest bed contact area. The two flat back faces remain available for gluing after printing.

## Support Plan

Designed for minimal supports when printed upright. Rock and water details are shallow raised features on vertical faces. The pool rings and splash blobs print from the top surface of the base.

## Known Risks

- This is a decorative original design, so shoebox fit is based on the requested dimensions rather than a measured box.
- The detailed version has more small raised texture; slow outer walls and 0.16-0.20 mm layers should improve paintable detail.
- Tall upright prints can benefit from a small brim if bed adhesion is weak.

## Exported STL Filename

- `exports/shoebox_corner_waterfall_simple_v01.stl`
- `exports/shoebox_corner_waterfall_detailed_v01.stl`
- `exports/shoebox_corner_waterfall_v01.stl` is the repo-standard detailed wrapper export.

## STL Export Status

Verified. Simple, detailed, and repo-standard detailed STL exports were generated successfully.

## Preview Export Status

Verified. Repo-standard iso/front/side/top previews plus simple/detailed iso previews were generated successfully.

## Next Actions

Dry fit the printed insert against the target shoebox corner before final paint and glue.
