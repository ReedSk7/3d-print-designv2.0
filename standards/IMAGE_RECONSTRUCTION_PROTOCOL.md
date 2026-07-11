# Image Reconstruction Protocol

Use this standard for `reference_based_reconstruction` and `mesh_cleanup_and_remodel` tasks that rely on user photos, marked-up images, screenshots, scans, or other 2D visual references.

## Perspective De-warping

- Never treat a photo angle as a flat orthographic projection.
- Identify the camera orientation before using the image for geometry.
- Explicitly calculate or ask for the true perpendicular plane dimensions for any face used as a profile, mounting plane, hole layout, slot layout, or latch interface.
- If the image is oblique, use it only as supporting evidence until at least one perpendicular view or authoritative anchor measurement is available.
- Do not infer depth, taper, recess depth, or countersink depth from perspective alone.

## Scale Reference Gating

- If an image contains a calibration object such as a digital caliper display, ruler, coin, grid, known fastener, or known hardware, extract the pixel-to-millimeter ratio before proposing a Geometry Contract.
- Record the scale source, measured pixel span, real millimeter span, and resulting pixels-per-millimeter or millimeters-per-pixel value in project notes.
- Apply scale only to features in the same plane as the calibration object unless perspective correction is documented.
- If no hard anchor measurement is visible, ask for one before final model generation or produce only a measurement checklist or fit-test scaffold.

## Feature Isolation Checklist

When analyzing each reference image, document the following before modeling:

1. Primary Extrusion Plane
   - Which face provides the main 2D profile to extrude from?
   - Is the face perpendicular to the camera, angled, curved, or partially hidden?
   - What known dimensions anchor that plane?

2. Subtractive Features
   - Identify every visible hidden recess, countersink, counterbore, slot, notch, through-hole, blind hole, relief cut, clip window, and clearance pocket.
   - Record whether each feature is authoritative, inferred, or unknown.
   - Ask for missing depth, diameter, width, center spacing, and edge offset values before final geometry.

3. Intersecting Primitives
   - Break complex molded shapes into simple overlapping primitives such as cubes, cylinders, spheres, wedges, ribs, bosses, and plates.
   - Use `union()` for joined solids, `difference()` for cuts, `intersection()` for trims, and `hull()` only where a smoothed transition is intentionally modeled.
   - Keep each primitive parametric with named dimensions, radii, offsets, and clearances.

## Geometry Contract Requirements

- Image-derived dimensions must be labeled with confidence: authoritative, scaled from calibrated image, inferred from perspective, or guessed.
- Protected interfaces cannot be finalized from guessed or perspective-only image dimensions.
- Bounding boxes from images are not enough. Local feature checks must include hole centers, slot widths, recess shapes, latch faces, tab thicknesses, and mounting surfaces.
- If image evidence conflicts with measured dimensions, measured dimensions win unless the measurement is clearly wrong and the conflict is documented.

## Required Notes

Record these fields in project notes or the reference comparison log:

- image filename or reference label
- camera orientation
- primary visible plane
- scale anchor used
- pixel-to-millimeter ratio, if available
- features treated as authoritative
- features treated as inferred
- missing views or dimensions
- perspective risks and low-confidence zones
