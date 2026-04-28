---
name: openscad-3d-print-agent
description: OpenSCAD reconstruction, replacement-part remodeling, project bootstrap, validation, STL export, preview rendering, and printability review for this repo. Use for 3D-print modeling tasks.
---

# OpenSCAD 3D Print Agent

Follow root `AGENTS.md` first. This skill is a workflow helper, not a replacement rulebook.

## Required Workflow

1. Read root `AGENTS.md`.
2. Select exactly one task mode before modeling:
   - `original_product_design`
   - `reference_based_reconstruction`
   - `mesh_cleanup_and_remodel`
3. Use root docs, standards, templates, and scripts.
4. Use reconstruction workflow when references exist.
5. Treat OpenSCAD as the source of truth.
6. Treat STL as an export artifact.
7. Ask for missing critical measurements only when required.
8. Make safe assumptions only when reasonable.
9. List assumptions.
10. Prioritize functional fit over looks.
11. Protect interfaces.
12. Use compare-and-revise loops for reconstruction.
13. Avoid unsupported overhangs where practical.
14. Add chamfers and fillets where useful while keeping OpenSCAD editable.
15. For replacement parts, create a measurement checklist before final geometry if critical dimensions are missing.
16. For curved mating surfaces, approximate parametrically and mark assumed radius.
17. Never invent exact fit dimensions.
18. Never claim STL export succeeded unless `scripts/export_stl.py` actually created the STL.
19. Never claim previews rendered unless PNG files exist.
20. Mark uncertain outputs as `NOT VERIFIED`.
21. Record measured versus inferred dimensions.
22. Record low-confidence zones.
23. Record failed checks honestly.

## Script Pattern

Use the root scripts:

```powershell
py -3 scripts\new_project.py --name "<name>" --task-mode <mode> --printer "<printer>" --material <material>
py -3 scripts\validate_scad.py <path-to-scad>
py -3 scripts\export_stl.py --input <scad> --output <stl>
py -3 scripts\export_preview.py --input <scad> --output <png> --view iso
py -3 scripts\check_project_outputs.py --project <project-dir> --task-mode <mode> --version vNN
py -3 scripts\next_version.py --project <project-dir> --copy-scad
```
