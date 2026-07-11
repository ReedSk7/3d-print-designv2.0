# Original Design Notes

## task mode

`original_product_design`

## goal

Create a simple parametric right-angle mounting bracket that demonstrates the repo's OpenSCAD-first workflow with one printable example part.

## constraints

- Target process: FDM
- Geometry should stay simple and readable for review
- Default material assumption: PLA or PETG
- Part should print upright without mandatory supports

## chosen concept

One L-bracket with two perpendicular legs, a triangular gusset, and one mounting hole per leg.

## key parameters

- leg length: 60 mm
- leg height: 40 mm
- leg width: 24 mm
- wall thickness: 6 mm
- hole diameter: 5.2 mm
- hole offset: 14 mm
- gusset thickness: 6 mm

## print orientation

Print flat on the longer leg with the vertical leg rising in Z.

## support plan

Designed to print without supports in the default orientation.

## known risks

- Hole fit may still need printer-specific compensation.
- The example is a workflow sample, not a load-rated bracket.

## exported STL filename

`exports/example_bracket_v01.stl`

## STL export status

Completed in this environment with OpenSCAD 2021.01 and written to `exports/example_bracket_v01.stl`.

## next actions

- Run project validation.
- Bump to a new version if geometry changes are required.
