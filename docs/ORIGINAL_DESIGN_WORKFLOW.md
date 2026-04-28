# Original Design Workflow

Use `original_product_design` only for true greenfield parts that are not defined by an existing reference part, product, broken component, OEM identifier, measured sample, or rough mesh.

## Steps

1. Define the use case and functional requirements.
2. Explore concepts only when useful.
3. Choose a concept only if multiple directions were explored.
4. Plan main parameters, clearances, modules, and part selection.
5. Build clean parametric OpenSCAD geometry.
6. Validate FDM printability for the intended printer and material.
7. Export versioned STL output.
8. Render at least an iso preview.
9. Record print orientation, support expectations, assumptions, and risks in notes and manifest.

## Rules

- Keep OpenSCAD as the editable source of truth.
- Keep STL as a generated artifact.
- Use lowercase snake_case project stems.
- Match `_vNN` versions across source, exports, previews, notes, and manifest.
- Do not overwrite old versions.
- If the job becomes reference-driven, switch task mode instead of forcing the original design workflow onto it.

## Completion Gate

Run:

```powershell
py -3 scripts\validate_scad.py <path-to-scad>
py -3 scripts\export_stl.py --input <scad> --output <stl>
py -3 scripts\export_preview.py --input <scad> --output <png> --view iso
py -3 scripts\check_project_outputs.py --project <project-dir> --task-mode original_product_design --version vNN
```
