# Preview Conventions

- Generate an iso preview by default.
- Reconstruction requires `iso`, `front`, and `side` previews.
- Add a `top` preview when footprint, asymmetry, or orientation matters.
- Add detail previews for hooks, tabs, snaps, pivots, lock faces, spring contacts, and other critical local features.
- Detail previews are mandatory when failure-sensitive local features exist.
- Keep preview names version-matched to the source and export files.
- Mark missing preview outputs as `NOT VERIFIED`.

Example names:

- `project_v01_iso.png`
- `project_v01_front.png`
- `project_v01_side.png`
- `project_v01_top.png`
- `project_v01_detail_hook.png`

Preferred OpenSCAD CLI pattern:

```powershell
py -3 scripts\export_preview.py --input source\project_v01.scad --output previews\project_v01_iso.png --view iso
```
