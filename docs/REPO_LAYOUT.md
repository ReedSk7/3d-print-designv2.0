# Repo Layout

`AGENTS.md` is the main instruction hub and source of truth for coding agents. If scripts, templates, standards, skills, lower-level notes, or generated instructions conflict with root `AGENTS.md`, follow root `AGENTS.md`.

`README.md` is the human orientation and quick-start entrypoint. It should stay concise and point to the repeatable workflow.

## `docs/`

Workflow docs and operational guidance.

Do not store per-project notes, measurements, references, or exported artifacts here.

## `standards/`

Reusable conventions for naming, versioning, previews, fits, hardware starter values, protected interfaces, printability, printer limits, materials, and project requests.

Do not store one-off project decisions here.

## `templates/`

Starter notes, manifests, checklists, review reports, comparison logs, and SCAD templates.

Do not store completed job records here. Copy templates into the project `notes/` folder and version them.

## `scripts/`

Small utilities for project bootstrap, SCAD validation, STL export, preview rendering, mesh comparison, output verification, and versioning.

Scripts must fail plainly and must not print fake success when artifacts are missing.

## `references/`

Reference inputs are organized by trust and rights:

- `references/measured/`
- `references/public/`
- `references/paid/`

Do not store final exports in `references/`. Paid references stay local-only unless redistribution rights are clear.

## `projects/`

Active and archived project workspaces. Do not store shared standards in project folders.

## `projects/_template/`

Starter folder structure for new projects:

- `source/`
- `exports/`
- `notes/`
- `previews/`

## Project Pattern

```text
projects/<project_stem>/
  source/
    <project_stem>_v01.scad
  exports/
    <project_stem>_v01.stl
  previews/
    <project_stem>_v01_iso.png
    <project_stem>_v01_front.png
    <project_stem>_v01_side.png
  notes/
    <project_stem>_v01_notes.md
    <project_stem>_v01_manifest.md
    <project_stem>_v01_measurement_notes.md
    <project_stem>_v01_printability_review.md
    <project_stem>_v01_release_notes.md
    <project_stem>_v01_reference_comparison_log.md
    <project_stem>_v01_review_report.md
```

Use lowercase snake_case stems and `_vNN` version suffixes. Never overwrite old versions.
