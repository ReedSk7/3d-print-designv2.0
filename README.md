# Reconstruction-First OpenSCAD Repo

This repository is for practical OpenSCAD modeling with two primary use cases:

- original product design
- reference-based reconstruction and replacement-part remodeling

The editable source of truth is OpenSCAD. STL files are export artifacts and the current required export for completed modeling work.

## Quick Start

1. Choose the task mode before modeling.
2. Create a new project folder by copying `projects/_template/` to `projects/<project_stem>/`.
3. Place references into `references/measured/`, `references/public/`, or `references/paid/`.
4. Fill in `templates/reconstruction_notes.md` or `templates/original_design_notes.md`.
5. Build the OpenSCAD source in `projects/<project_stem>/source/`.
6. Export the STL and required preview images.
7. If the job is reconstruction, use `templates/reconstruction_checklist.md` and `templates/reference_comparison_log.md` during compare-and-revise.
8. Record comparison or mismatch notes for the current version.

## How Task Modes Work

Agents must choose a task mode before modeling:

- `original_product_design`: use for truly new parts.
- `reference_based_reconstruction`: use when measurements, photos, part numbers, reference STLs, purchased STLs, or other known-part references exist.
- `mesh_cleanup_and_remodel`: use when a rough STL, GLB, or OBJ exists but should be treated as seed geometry only.

Reconstruction mode does not require concept matrices or concept scoring by default. Its default path is compare-and-revise until the geometry is acceptable, usually as one corrected model unless the user asks for variants.
Concept generation is usually skipped when the job is reference-based and the target geometry already exists.

## Protected Interfaces

Protected interfaces are the geometry that must stay faithful for fit and function, such as latch faces, hook tips, slots, pivots, mounting faces, bearing seats, and spring contact regions. Define these before reinforcement or cosmetic cleanup.

## References

- `references/measured/`: caliper notes, sketches, dimension tables, marked-up photos.
- `references/public/`: redistributable or openly usable references.
- `references/paid/`: purchased or license-restricted references. Keep these local-only by default and do not commit them unless redistribution is clearly allowed.

Reconstruction notes may mention a paid reference without redistributing it.

## Minimum Deliverables

For completed reconstruction jobs:

- `source/<project_name>_vNN.scad`
- `exports/<project_name>_vNN.stl`
- `notes/<project_name>_vNN_notes.md`
- `previews/<project_name>_vNN_iso.png`
- `previews/<project_name>_vNN_front.png`
- `previews/<project_name>_vNN_side.png`

For completed original design jobs:

- `source/<project_name>_vNN.scad`
- `exports/<project_name>_vNN.stl`
- `notes/<project_name>_vNN_notes.md`
- at least one preview image

STL is not optional for completed modeling work. If export fails for a real technical reason, document the failure clearly in notes or the manifest.

## Naming and Versioning

Use lowercase snake_case project stems and match version suffixes across source, STL, previews, notes, and manifest where applicable. Example: `hinge_clip_v02.scad`, `hinge_clip_v02.stl`, `hinge_clip_v02_iso.png`.

## Future Packaging

3MF or Bambu Studio-ready packaging may be added later. It is a future enhancement target, not a current required artifact.

## Project Structure

Each project should live under `projects/<project_stem>/` with:

- `source/`: editable `.scad` files
- `exports/`: generated STL artifacts
- `notes/`: notes, assumptions, and comparison records
- `previews/`: render views used for review

Use the starter tree in `projects/_template/` when beginning a new job.
