# Reconstruction Checklist v04

- [x] exact target part defined
- [x] reused surrounding parts defined
- [x] reference hierarchy recorded
- [x] anchor dimensions recorded
- [x] protected interfaces recorded
- [x] bbox compared
- [x] side silhouette compared
- [x] front silhouette compared
- [x] top silhouette compared when needed
- [x] critical local features compared
- [x] reinforcement limited to non-interface zones
- [x] print orientation chosen
- [x] support plan chosen
- [x] low-confidence zones documented
- [x] STL exported successfully or export failure documented
- [x] versioned files named correctly
- [x] collar placement compared against the user-photo anchors
- [x] asymmetry preserved and not forced into symmetry
- [x] right-side cavity kept deeper than the left side
- [x] main stud layout kept non-rectangular and photo-driven
- [x] smaller collar-boss presence included
- [x] bumper-matching contour intent kept as staged blends, not a single cylinder shortcut
- [x] single-piece build-volume fit checked against `256 x 256 x 256 mm`
- [x] no preview images generated, per explicit non-visual instruction

## Verification Notes

- Verified STL bbox: `254.0 x 141.8 x 149.993 mm`
- `trimesh`: `watertight=True`
- Connected body count: `1`
- Manual comparison source set: `3520.jpg`, `3521.jpg`, and the installed/context images in `references/measured/cat_ct660_fog_light_housing/`
