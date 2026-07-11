# Original Design Notes

## task mode

`original_product_design`

## goal

Create a simplified display miniature of a 1996 MasterCraft ProStar 190 sized for a Bambu-class desktop print, with a recognizable closed-bow ski boat silhouette at about 128 mm overall length.

## constraints

- Fidelity classification: `display miniature`
- Intended use: desk/display print, not a fit-critical replica
- Target printer envelope assumption: about 256 mm square bed, with longest model dimension targeting about half that size
- Material target: PLA or PETG friendly

Known anchor dimensions:

- full-size length: 19'6" (used as the main scale anchor)
- full-size beam: 85"
- supporting seller listing reference: 19 ft length and 7.08 ft beam, treated as a rounded corroborating source rather than the primary scale source

Inferred shape areas:

- exact hull bottom curvature
- deck crown
- windshield sweep and framing
- cockpit cutout outline
- swim platform shape

## chosen concept

One simplified closed-bow ski boat miniature with:

- hull body from intersected side and plan silhouettes
- shallow deck crown
- low windshield massing
- cockpit depression
- small stern swim platform

## key parameters

- intended overall model length: about 128 mm
- intended hull body length before swim platform: 120 mm
- intended beam from full-size ratio: about 46.5 mm
- deck height: 16 mm
- windshield height: 5.5 mm
- cockpit opening length: 38 mm
- cockpit opening width: about 27.0 mm
- swim platform length: 8 mm

Verified final mesh extents from exported STL:

- overall length: 127.0 mm
- beam: 46.50 mm
- overall height: 18.00 mm

## print orientation

Default orientation is upright on the hull bottom with the swim platform trailing aft.

## support plan

Model is intended to print support-free or with only minimal cleanup. The hull bottom is simplified and kept flat enough for stable bed contact.

## known risks

- The silhouette should read as ProStar-style, but this is not an exact hull reconstruction.
- The hull sides and bottom are intentionally simplified for printable miniature behavior.
- Fine windshield framing is intentionally simplified for print robustness.
- Small stern platform edges may need slight deburring after printing.
- Exact deck transitions and windshield sweep are inferred from public photos and listings, not verified from factory CAD.

## exported STL filename

`exports/mastercraft_prostar_190_mini_v01.stl`

## STL export status

Completed in this environment and verified with `trimesh` as a single watertight mesh.

## next actions

- Optionally refine hull flare or deck contour if a more sculpted display look is wanted in a future version.
- Optional future enhancement: add 3MF or Bambu Studio-ready packaging after the current STL-first workflow.
