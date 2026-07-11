# Softball A Chain Pendant

Task mode: `mesh_cleanup_and_remodel`

This project creates a flat-back 3D printable softball-style chain pendant with a raised decorative `A`, raised stitch details, a raised outer rim, and a chunky top bail for chains, keychains, bag clips, or necklaces.

The provided photos and AI-generated mesh files were used as visual/supporting references only. The model is rebuilt as clean parametric OpenSCAD and is not an exact logo or trademark reconstruction.

## Source Files

- `source/softball_A_chain_pendant.scad` - editable OpenSCAD source of truth.
- `source/softball_A_chain_pendant_v01.scad` - versioned wrapper for repo validation.
- `source/softball_A_chain_pendant_config.json` - key parameters and export options.
- `source/export_presets/*.scad` - deterministic wrapper files used for STL exports.

## Exported Files

- `exports/single_color/full_single_color.stl` - large standard-bail single-color model.
- `exports/large/full_single_color_oversized_bail.stl` - large model with a larger chain opening.
- `exports/small/full_single_color_75mm.stl` - smaller 75 mm tall standard-bail model.
- `exports/small/full_single_color_75mm_oversized_bail.stl` - smaller model with oversized bail.
- `exports/multicolor_parts/black_base_outline.stl` - black base, bail, raised rim, stitch shadows, and A outline.
- `exports/multicolor_parts/yellow_softball_face.stl` - yellow softball face insert.
- `exports/multicolor_parts/red_A_and_stitches.stl` - raised red A and red stitches.
- `exports/multicolor_parts/white_highlight_optional.stl` - optional small raised highlight bodies, not included in the default assembly.
- `exports/full_multicolor_assembly.3mf` - simple 3MF assembly made from the aligned multicolor STL bodies.
- `exports/softball_A_chain_pendant_v01.stl` - repo-check single-color v01 export.

Import the multicolor STL files into Bambu Studio as parts of one object, keep their origins aligned, then assign AMS colors.

## Design Notes

- Verified large model extents are about 88.85 mm wide x 104.78 mm tall x 7.55 mm thick.
- Verified small model extents are about 64.30 mm wide x 75.75 mm tall x 7.25 mm thick.
- Bail opening is at least 10 mm x 6 mm, with wall thickness over 3 mm.
- Stitches use chunky raised geometry, not texture.
- The default `A` is a geometric fallback so OpenSCAD exports do not depend on a specific font.
- The A was revised toward the cleaner Meshy silhouette while avoiding the non-watertight/distorted mesh areas.

## Known Limits

- The A is decorative and printable, not an exact team/trademark logo.
- Multicolor assembly is provided as aligned STL bodies. A color-managed 3MF may depend on slicer/tool availability.
