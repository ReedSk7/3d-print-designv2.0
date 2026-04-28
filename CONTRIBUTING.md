# Contributing

## Project Purpose

This repository produces clean, parametric, printable OpenSCAD models with OpenSCAD kept as the editable source of truth and STL treated as an export artifact.

Root `AGENTS.md` is authoritative. Supporting docs, templates, standards, scripts, and skills must align with it.

## Task Mode Selection

Task mode selection is mandatory and is the first step on every job.

- Use `original_product_design` for true greenfield work.
- Use `reference_based_reconstruction` when a known part is being recreated, repaired, replaced, or refined from references.
- Use `mesh_cleanup_and_remodel` when a rough mesh exists but must be rebuilt as clean OpenSCAD.

Do not begin geometry work before the task mode is recorded.

## Project Bootstrap

Prefer `scripts/new_project.py` for new projects once available. Manual copy from `projects/_template/` is the fallback.

Before modeling:

1. Choose a lowercase snake_case project stem.
2. Select the version number, usually `v01`.
3. Select the task mode.
4. Define the exact target part.
5. Define reused surrounding parts.
6. Define what is not being modeled.
7. Categorize references as measured, public, paid, or supporting.
8. Identify authoritative and supporting references.
9. Record anchor dimensions.
10. Separate measured dimensions from inferred dimensions.
11. Define protected interfaces.
12. List low-confidence zones.
13. Select the output artifact plan and required previews.
14. Consider printer bed fit and printability risks.

Reconstruction jobs must satisfy `PROJECT_BOOTSTRAP_CHECKLIST.md` before modeling. If critical fit data is missing, create measurement notes and a checklist instead of guessing final fit geometry.

## Reference Handling Rules

- Use the trust order from `AGENTS.md`.
- Record which references are authoritative and which are supporting only.
- Keep paid references local-only unless redistribution rights are clear.
- Treat AI-generated or rough meshes as supporting geometry unless the user explicitly says they are trusted.
- If authoritative references conflict, note the conflict before export.

## Modeling Workflow

- Reconstruction and mesh-cleanup jobs: define scope, inventory references, record anchor dimensions and protected interfaces, rebuild in OpenSCAD, compare bbox plus silhouettes plus critical local features, revise, run printability review, export, render previews, and check outputs.
- Original design jobs: summarize requirements, plan parameters, build in OpenSCAD, run printability review, export, render at least an iso preview, and check outputs.

Do not turn reconstruction work into creative redesign unless the user asks for it.

## Required Outputs

New outputs must not overwrite existing `_vNN` files. Create the next version instead.

Completed jobs need verified:

- versioned source
- versioned STL
- versioned notes
- versioned manifest
- required previews
- review or printability record

Missing outputs must be reported as `NOT VERIFIED`.

Use `scripts/check_project_outputs.py` as the completion gate:

```powershell
py -3 scripts\check_project_outputs.py --project projects\<project_stem> --task-mode <mode> --version vNN
```

## Truthfulness Reporting Requirements

- Do not claim an STL export succeeded unless the `.stl` file exists and was actually generated.
- Do not claim previews were rendered unless the image files exist and were actually generated.
- Mark unverified outputs as `NOT VERIFIED`.
- Record what is measured versus inferred.
- Record low-confidence zones and failed checks.
- If export or render fails, state the failure plainly and keep the notes factual.

## What Not To Do

- Do not skip task mode selection.
- Do not blindly trust rough meshes.
- Do not redesign protected interfaces without explicit instruction.
- Do not accept overall size matching as sufficient when local fit-critical geometry is still wrong.
- Do not create speculative variants unless asked.
- Do not claim files were created, exported, or rendered when they were not.
