# Naming And Versioning

- Use lowercase snake_case only for project folders, project stems, file stems, OpenSCAD variables, functions, and modules.
- Keep one project stem per part or design.
- Do not use kebab-case, spaces, mixedCase, PascalCase, uppercase names, or descriptive punctuation in new or touched project paths or OpenSCAD identifiers.
- Use `_vNN` version suffixes: `_v01`, `_v02`, `_v03`.
- Match the version suffix across SCAD, STL, previews, notes, manifest, review report, and comparison logs.
- Never overwrite old versions. Create the next version instead.
- Variant exports must keep the same lowercase snake_case stem and add lowercase snake_case variant labels before the version only when the user explicitly requests separate deliverables.
- Legacy nonconforming paths may remain for historical reference, but any new version or touched artifact must move back to strict lowercase snake_case.

## OpenSCAD Identifier Rules

- Variables, modules, and functions must be lowercase snake_case.
- Use named parameters for all functional dimensions, tolerances, offsets, radii, hole sizes, and cut overlaps.
- Do not place unexplained numeric literals directly inside geometry calls when a named variable can carry the intent.
- Code templates under `templates/` must stay fully parametric and must not teach hardcoded magic numbers.

Correct stems:

- `simple_wall_bracket`
- `hinge_clip`
- `ac_hose_adapter`

Incorrect stems:

- `simple-wall-bracket`
- `hinge-clip`
- `ac-hose-adapter`

Example version set:

```text
source/hinge_clip_v02.scad
exports/hinge_clip_v02.stl
previews/hinge_clip_v02_iso.png
previews/hinge_clip_v02_front.png
previews/hinge_clip_v02_side.png
notes/hinge_clip_v02_notes.md
notes/hinge_clip_v02_manifest.md
notes/hinge_clip_v02_reference_comparison_log.md
notes/hinge_clip_v02_review_report.md
```
