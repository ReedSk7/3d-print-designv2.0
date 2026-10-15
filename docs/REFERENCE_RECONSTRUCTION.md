# Reference Reconstruction Workflow

> Legacy pre-v3 workflow. For v3 replacement work, the typed Measurement
> Contract and release gate in `docs/rebuild/VERIFICATION_MODEL.md` are
> authoritative.

Use `reference_based_reconstruction` when the job is about recreating, repairing, replacing, or refining a known part. Use `mesh_cleanup_and_remodel` when a rough mesh exists but should be rebuilt as clean OpenSCAD.

Default output is one corrected model unless the user explicitly asks for multiple variants.

## Classification Triggers

Treat the task as reconstruction when the user provides any of these:

- measured dimensions or caliper notes
- sketches
- part number or OEM identifier
- OEM drawings, service docs, or diagrams
- OEM, product, intact-part, or broken-part photos
- product link or known replacement part target
- reference STL, STEP, or CAD
- purchased STL/CAD

Use `mesh_cleanup_and_remodel` when the input is a rough STL, GLB, OBJ, scan output, Meshy output, Trellis output, AI-generated mesh, or photo-to-3D output that should not be trusted as final geometry.

## Reference Trust Hierarchy

Use this order unless the user overrides it:

1. measured dimensions from the real part
2. trusted or purchased reference STL/STEP/CAD
3. official OEM drawings, service docs, or diagrams
4. official product photos
5. user photos of intact or broken part
6. AI-generated meshes or photo-to-3D outputs

Record authoritative references and supporting references separately. Paid references stay local-only unless redistribution rights are clear.

## Protected Interfaces

Protected interfaces are fit-critical or function-critical surfaces and dimensions. Define them before final geometry and before reinforcement.

Common protected interfaces:

- mounting hole spacing
- mounting faces
- latch faces
- hook tips
- snap faces
- clip faces
- slot widths
- tabs
- pivots
- shaft, rod, bearing, and insert fits
- spring contact regions
- locking tabs
- curved mating surfaces

Compare protected interfaces directly against authoritative references. Do not redesign them for looks. Do not thicken, chamfer, or reshape them unless the user explicitly requests an interface change.

## Rough Mesh Handling

Rough meshes are supporting references only unless the user explicitly says they are trusted.

- Inspect rough meshes for overall form, missing regions, and feature placement clues.
- Measure rough meshes when useful, but label the measurements as supporting unless the source is trusted.
- Do not copy rough mesh topology into final CAD.
- Remodel critical interfaces cleanly in OpenSCAD.

## Conflict Handling

- If measurements conflict with photos, measurements win unless clearly wrong.
- If trusted CAD conflicts with an AI-generated mesh, trusted CAD wins.
- If authoritative references conflict, document the conflict before export.

## Compare And Revise

After rebuilding the part, compare the current model against the best reference using:

- bounding box
- front silhouette
- side silhouette
- top silhouette when useful
- critical local features such as hooks, pivots, slots, latch faces, spring contacts, locking tabs, and mounting geometry

Overall dimensions alone are never enough. If the bbox matches but a hook, tab, slot, latch face, pivot, screw hole, or mounting interface does not match, the model is not done.

## Reinforcement Rules

Reinforce non-interface regions first. Preserve protected interfaces unless the user explicitly requests a changed fit or a durability-driven interface change.

## Low-Confidence Zones

Document guessed geometry, missing measurements, inferred radii, weak reference coverage, and any test-fit-only assumptions in notes, manifest, comparison logs, and review reports.

## Reconstruction Completion Checklist

- exact target part defined
- reused surrounding parts defined
- not-modeled items defined
- reference hierarchy recorded
- authoritative references identified
- anchor dimensions recorded
- protected interfaces recorded
- bbox compared
- front and side silhouettes compared
- top silhouette compared when useful
- critical local features compared
- reinforcement limited to non-interface zones
- low-confidence zones documented
- FDM printability reviewed
- STL exported or export failure documented
- required previews rendered or render failure documented
- manifest, notes, comparison log, and review report updated
