---
name: openscad-3d-print-agent
description: Deterministic Parametric Part Workbench v3 setup, dimension-driven CAD, visual review, fit-evidence, and Bambu handoff workflow.
---

# Parametric Part Workbench v3 Helper

Read and follow root `AGENTS.md` first. This helper does not override the root
rules or authorize legacy project workflows.

## Choose the relevant procedure

- Approved local Print Workshop app: read `docs/PRINT_WORKSHOP.md`. The UI uses
  the existing backend and exact evidence states. Blender 5.2.2 inspection is
  optional; OpenSCAD remains source authority. No automatic mesh repair or print
  controls. Canonical transition/cleanup remain gated on verified preservation.

- Environment/configuration/dependencies: read [setup](references/setup.md).
- Dimensions/specification/generator selection: use the workflow below.
- CAD images and critical features: read [visual review](references/visual-review.md).
- Hashes, fit evidence and slicer transfer: read [artifact handoff](references/artifact-handoff.md).

Do not load every procedure for a simple task. No duplicate personal installation
is needed; this skill stays versioned with the repository.

## Dimension-driven CAD

1. Identify the supported generator: `bushing`, `round_adapter`, or
   `flange_plate`.
2. Record explicit dimensions and units in a v1 project specification.
3. For replacement work, complete authoritative Measurement Contract entries
   for every generator-declared protected interface. Never infer a missing
   protected dimension from a photo or generic default.
4. Select a printer/material/nozzle calibration profile. Treat the bundled
   neutral profile as an unverified starter.
5. If nominal geometry is known but fit clearance is uncertain, generate a
   candidate fit coupon and record its printed result before relying on the
   full part.
6. Validate the specification, generate deterministic OpenSCAD, compile with
   mandatory OpenSCAD, run mesh QA, and compare expected and actual bounds.
7. Keep routine SCAD/STL/manifests under
   `workspace/<project_id>/<version>/`; do not commit them.
8. Report the exact workflow state, assumptions, unresolved interfaces, and
   failed checks. Computational success never confirms physical fit.

## Commands

```powershell
python scripts\validate_spec.py --spec <spec.json>
python scripts\generate_part.py --spec <spec.json>
python scripts\verify_mesh.py --manifest <artifact-manifest.json>
python -m pytest
```

Do not route new work through `new_project.py`, `next_version.py`, legacy
templates or file-presence checks. For version-bound previews use
`export_preview.py --manifest`; its single-input mode is only a legacy export.
Keep generator 1.0.0 and 1.1.0 contracts intact. New families require separate
scope and tests, not arbitrary geometry generated from an unbounded prompt.
