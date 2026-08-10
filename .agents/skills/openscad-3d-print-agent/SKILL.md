---
name: openscad-3d-print-agent
description: Deterministic Parametric Part Workbench v3 specification, generation, fit-coupon, and computational verification workflow.
---

# Parametric Part Workbench v3 Helper

Read and follow root `AGENTS.md` first. This helper does not override the root
rules or authorize legacy project workflows.

## Required Workflow

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
templates, preview requirements, or legacy file-presence checks. Those remain
historical compatibility tools only.
