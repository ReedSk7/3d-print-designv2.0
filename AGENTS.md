# AGENTS.md

This is the main instruction hub for coding agents working in this repository.

## Mission

- Create clean, parametric, printable OpenSCAD models.
- Support both original product design and reference-driven reconstruction.
- Keep OpenSCAD as the editable source of truth.
- Treat STL as an export artifact, not the design authority.

## Global Defaults

- Units are millimeters.
- `Z+` is up.
- FDM-first by default unless the user explicitly requests another process.
- Prefer readable parametric CAD over messy geometry.
- Keep critical geometry in named modules and parameters when practical.
- For new empty repos or requested scaffolds, create the repository structure before attempting any modeling.
- Do not overwrite versioned outputs.
- Do not claim files were created unless they actually were.

## Task Modes

Use exactly one task mode before modeling begins.

### `original_product_design`

Use for truly greenfield work where the part is not defined by an existing object or reference part.

### `reference_based_reconstruction`

Use when the user wants a known part recreated, repaired, replaced, or refined from references.

Default to one corrected model unless the user explicitly asks for multiple variants.

Before modeling, define:

- the exact target part
- what surrounding parts are reused
- what is not being modeled

### `mesh_cleanup_and_remodel`

Use when a rough mesh exists but should not be trusted as final geometry. The mesh is supporting input, not final truth.

## Mode Selection Rules

- If a user provides a part number, measurements, OEM photos, broken-part photos, reference STL, purchased STL, or rough mesh, default to `reference_based_reconstruction`.
- Only use `original_product_design` when the request is truly greenfield.
- If a rough mesh exists but should not be trusted, use `mesh_cleanup_and_remodel`.

## Reference Trust Hierarchy

Unless the user overrides it, use this exact priority:

1. measured dimensions from the real part
2. trusted or purchased reference STL/STEP/CAD
3. official OEM drawings / service docs / diagrams
4. official product photos
5. user photos of intact or broken part
6. AI-generated meshes or photo-to-3D outputs

Rules:

- Record which references are authoritative and which are supporting only.
- If authoritative references conflict, note the conflict before export.
- Rough meshes may be measured and inspected, but they are seed geometry only unless the user explicitly says they are trusted.
- Paid references should remain local-only unless redistribution rights are clear.

## Reconstruction Workflow

For `reference_based_reconstruction` and `mesh_cleanup_and_remodel`, follow this workflow:

1. define exact scope
   - exact target part
   - reused surrounding parts
   - what is not being modeled
2. inventory references
3. identify authoritative references
4. record anchor dimensions and protected interfaces
5. inspect rough meshes if present, but treat them as supporting geometry only
6. rebuild clean parametric CAD in OpenSCAD
7. compare bbox + silhouettes + critical local features
8. revise until acceptable
9. run printability check
10. export final artifacts

Comparison in step 7 must include:

- bounding box
- front silhouette
- side silhouette
- top silhouette when useful
- critical local features such as hooks, pivots, slots, latch faces, spring contact regions, locking tabs, and mounting geometry

Overall dimensions alone are never enough when critical local geometry matters.

Protected interface examples:

- mounting hole spacing
- shaft or rod fits
- snap and latch faces
- bearing or insert seats
- clip tips
- slot widths
- hinge pivots

## Original Design Workflow

For `original_product_design`, this workflow is allowed:

1. requirements summary
2. concept generation if useful
3. concept selection if multiple directions are explored
4. parameter planning
5. OpenSCAD generation
6. printability review
7. export

## Guardrails

- Do not force concept scoring on reconstruction jobs.
- Do not blindly trust AI-generated meshes.
- Do not redesign authoritative interfaces just for aesthetics.
- Do not commit paid reference meshes by default.
- Do not create multiple speculative variants unless asked.
- Do not turn reconstruction jobs into creative redesign jobs unless requested.
- Do not confuse a full assembly with the broken subcomponent that actually needs replacement.
- Do not accept overall size matching as sufficient when hook, tip, slot, latch, or mounting geometry is still wrong.
- Do not treat rough meshes as authoritative just because they look complete.

## Failure Mode Prevention

- Confirm whether the task is the full assembly or only the broken subcomponent before modeling.
- Do not over-trust AI-generated meshes over measured geometry, trusted CAD, or paid references.
- Do not stop at bbox matching when hooks, tabs, slots, latch faces, pivots, spring contact regions, or mounting interfaces still mismatch.
- Do not produce extra speculative variants when one corrected part is wanted.

## Required Outputs

### Reconstruction Jobs

Minimum outputs:

- `source/<project_name>_vNN.scad`
- `exports/<project_name>_vNN.stl`
- `notes/<project_name>_vNN_notes.md`
- `previews/<project_name>_vNN_iso.png`
- `previews/<project_name>_vNN_front.png`
- `previews/<project_name>_vNN_side.png`

Add a top preview when footprint or asymmetry matters. Add detail previews when critical features need verification.
Generated STL export is a required artifact for completed modeling work unless export truly fails for a real technical reason.

### Original Design Jobs

Minimum outputs:

- `source/<project_name>_vNN.scad`
- `exports/<project_name>_vNN.stl`
- `notes/<project_name>_vNN_notes.md`
- at least one preview image

Generated STL export is a required artifact for completed modeling work unless export truly fails for a real technical reason.

## Export Note

- STL is the required export artifact for this repo version.
- 3MF or Bambu Studio project generation is preferred in the future, but it is not a current requirement.

## Working Rules

- Start by selecting task mode, not by brainstorming geometry.
- For reconstruction work, prefer one corrected model by default over multiple variants.
- Use compare-and-revise loops for reference-driven work, not one-shot geometry invention.
- For reconstruction work, use a versioned notes file plus a reconstruction checklist and comparison log.
- Reinforce only non-interface regions unless the user asks for interface changes.
- Be explicit about guessed dimensions and low-confidence zones in notes.
