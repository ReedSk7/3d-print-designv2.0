# Preview Conventions

- Generate an isometric preview by default.
- For reconstruction jobs, `iso`, `front`, and `side` previews are mandatory.
- Add a `top` view when footprint or asymmetry matters. If asymmetry matters to fit or orientation, show it.
- Add a detail preview when hooks, tabs, snaps, pivots, lock faces, or other critical local features need verification.
- Detail previews are mandatory when failure-sensitive local features exist.
- Keep preview names version-matched to the source and export files.

Naming examples:

- `project_v01_iso.png`
- `project_v01_front.png`
- `project_v01_side.png`
- `project_v01_top.png`
- `project_v01_detail_hook.png`
