# Geometric and visual review

Use `python scripts/export_preview.py --manifest <artifact-manifest.json>`.
It rechecks source/spec/STL/profile bindings and mesh bounds, then renders the
exact deterministic SCAD version with OpenSCAD. Top/front/side/isometric views
are orthographic; optional `--detail-camera x,y,z,rx,ry,rz,distance` gives an
explicit close view. Use a new `--revision r02` to preserve previous renders.
No `-D` geometry overrides may masquerade as the same source version.

Run `python scripts/verify_preview.py --preview-manifest <preview-manifest.json>`
before inspecting images. Open the actual CAD renders, check protected interfaces,
wall continuity, intended openings and silhouette. If not opened, say review is
pending. A successful PNG integrity check establishes no human visual judgment.

Keep the immutable preview manifest's agent/owner review pending fields intact.
Record each actual review in a NEW ignored local note alongside the preview,
including reviewer, time, manifest/image hashes, inspected views, findings and
remaining concerns. Owner review remains separate. No preview establishes fit.
If graphics context is unavailable, report the exact render failure; do not use
image generation or an imagined product image as a substitute.
