# Reconstruction-First OpenSCAD Repo

This is a reconstruction-first OpenSCAD 3D printing workspace for replacement parts, functional parts, mesh cleanup and remodel, and original product design when the job is truly greenfield.

OpenSCAD is the editable source of truth. STL is an export artifact, not the design authority. Root `AGENTS.md` is authoritative for agent behavior in this repo.

## Codex OpenSCAD Agent Workflow

The value of this repo is a disciplined pipeline:

request -> classify task mode -> bootstrap project -> record references -> protect interfaces -> generate clean OpenSCAD -> validate -> export STL -> render previews -> check outputs -> record notes and manifests -> create the next version when needed.

Use root scripts for bootstrap, validation, STL export, preview export, output verification, and versioning. Skill files are workflow helpers. If a skill conflicts with root `AGENTS.md`, follow root `AGENTS.md`.

## Task Modes

Agents must choose exactly one task mode before modeling:

- `original_product_design`: truly new parts.
- `reference_based_reconstruction`: known parts from measurements, photos, part numbers, product links, reference STL/CAD, or other references.
- `mesh_cleanup_and_remodel`: rough STL, GLB, OBJ, scan output, AI mesh, or photo-to-3D output that must be rebuilt as clean OpenSCAD.

Reconstruction defaults to one corrected model unless the user asks for variants. Concept scoring is not required for reconstruction jobs.

## Quick Start

```powershell
# Create a project
py -3 scripts\new_project.py --name "simple wall bracket example" --task-mode original_product_design --printer "Bambu Lab P2S" --material PETG

# Validate SCAD
py -3 scripts\validate_scad.py projects\simple_wall_bracket_example\source\simple_wall_bracket_example_v01.scad

# Export STL
py -3 scripts\export_stl.py --input projects\simple_wall_bracket_example\source\simple_wall_bracket_example_v01.scad --output projects\simple_wall_bracket_example\exports\simple_wall_bracket_example_v01.stl

# Export previews
py -3 scripts\export_preview.py --input projects\simple_wall_bracket_example\source\simple_wall_bracket_example_v01.scad --output projects\simple_wall_bracket_example\previews\simple_wall_bracket_example_v01_iso.png --view iso
py -3 scripts\export_preview.py --input projects\simple_wall_bracket_example\source\simple_wall_bracket_example_v01.scad --output projects\simple_wall_bracket_example\previews\simple_wall_bracket_example_v01_front.png --view front
py -3 scripts\export_preview.py --input projects\simple_wall_bracket_example\source\simple_wall_bracket_example_v01.scad --output projects\simple_wall_bracket_example\previews\simple_wall_bracket_example_v01_side.png --view side

# Check outputs
py -3 scripts\check_project_outputs.py --project projects\simple_wall_bracket_example --task-mode original_product_design --version v01

# Create next version
py -3 scripts\next_version.py --project projects\simple_wall_bracket_example --copy-scad
```

## References

- `references/measured/`: caliper notes, sketches, dimension tables, marked-up photos.
- `references/public/`: redistributable or openly usable references.
- `references/paid/`: purchased or license-restricted references. Keep these local-only by default unless redistribution is clearly allowed.

## Minimum Deliverables

Completed reconstruction jobs require:

- `source/<project_stem>_vNN.scad`
- `exports/<project_stem>_vNN.stl`
- `notes/<project_stem>_vNN_notes.md`
- `notes/<project_stem>_vNN_manifest.md`
- `notes/<project_stem>_vNN_reference_comparison_log.md`
- `notes/<project_stem>_vNN_review_report.md`
- `previews/<project_stem>_vNN_iso.png`
- `previews/<project_stem>_vNN_front.png`
- `previews/<project_stem>_vNN_side.png`

Completed original design jobs require source, STL, notes, manifest, and at least one preview image.

Missing outputs must be reported as `NOT VERIFIED`. Do not claim STL export or preview render success unless the files exist and were generated.

## Project Structure

Each project lives under `projects/<project_stem>/`:

- `source/`: editable `.scad` files
- `exports/`: generated STL artifacts
- `notes/`: notes, manifests, review reports, and comparison records
- `previews/`: render views used for review

Use `projects/_template/` or `scripts/new_project.py` when beginning a new job.

## Local Dashboard App

`app/` contains the local-only **3D Print Design Studio Dashboard**. It wraps the existing reconstruction-first OpenSCAD workflow without replacing it. Root `AGENTS.md` remains authoritative, OpenSCAD remains the editable source of truth, and STL files remain export artifacts.

What it does:

- tracks project intake records in `app/data/projects.json`
- lists existing `projects/` folders and detects source, STL, notes, manifests, review reports, and previews
- generates Codex/OpenSCAD prompts for original design, reconstruction, and mesh cleanup jobs
- calls the repo scripts for bootstrap, validation, STL export, preview export, output checks, and next-version creation
- provides printability, quote-note, release-checklist, and customer-request organization

Install and run:

```powershell
cd app
npm install
npm run dev
```

Open the dashboard at `http://127.0.0.1:5173`. The local API runs at `http://127.0.0.1:4177`.

Required local commands:

- `npm install`
- `npm run dev`
- `npm run build`

Windows notes:

- The backend calls repo scripts with `py -3`.
- OpenSCAD export and preview buttons require OpenSCAD to be installed locally and discoverable by the repo scripts.
- The app is local-only and does not use cloud login, paid services, or external API keys.

Files it creates:

- `app/data/projects.json`
- `app/data/settings.json`
- project records and bootstrap output under `projects/<project_stem>/` only when requested

Current limitations:

- no database in v01
- no payment processing
- no direct STL viewer
- no automatic upload or customer portal
- missing outputs are shown as `NOT VERIFIED` until file detection confirms them
