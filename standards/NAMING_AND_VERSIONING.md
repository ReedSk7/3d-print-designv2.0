# Naming And Versioning

- Use lowercase snake_case only for project stems and file stems.
- Keep one project stem per part or design.
- Do not use kebab-case.
- Use `_vNN` version suffixes: `_v01`, `_v02`, `_v03`.
- Match the version suffix across SCAD, STL, previews, notes, manifest, review report, and comparison logs.
- Never overwrite old versions. Create the next version instead.

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
