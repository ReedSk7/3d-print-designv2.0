# softball_A_chain_pendant v01 Reference Comparison Log

Task mode: `mesh_cleanup_and_remodel`

## Supporting References

- `single_color (2).stl` and `reduced_color (3).3mf` from Downloads: cleaner rough AI mesh, watertight, one connected component, measured extents about 100.00 x 53.63 x 91.87 mm in its exported orientation.
- `single_color (1).stl` and `reduced_color (2).3mf` from Downloads: rough AI mesh with visible distortion risk, non-watertight, 429 connected components, measured extents about 100.00 x 51.63 x 99.99 mm in its exported orientation.
- Original photos: visual reference only for color layout, softball face, A silhouette, stitches, and pendant feel.

## Authoritative References

No mesh is authoritative. The rough meshes are supporting references only because the user reported distortion and one mesh set is non-watertight.

## Rebuild Decisions

- Keep the softball medallion, black rim, raised red A, black A outline, red stitches, and flat back.
- Use a taller swash-style A closer to the better rough mesh silhouette.
- Do not preserve faceting, warped thickness, detached fragments, or distorted mesh areas.
- Keep bail/hook geometry from the user requirements, even though the rough mesh previews emphasize the medallion and A more than the bail.

## Comparison Items

- Bounding box: final large STL must stay under 120 mm tall and 90 mm wide.
- Front silhouette: large A should dominate the softball face and extend slightly below the ball.
- Side silhouette: final should remain flat-printable with total thickness around 6 to 8 mm.
- Critical local features: bail wall, bail opening, raised stitch width, A outline, and lower swash thickness.
