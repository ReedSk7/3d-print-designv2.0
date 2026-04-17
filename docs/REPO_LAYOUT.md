# Repo Layout

- `AGENTS.md`: main instruction hub for coding agents. Put repo-level behavior here, not per-project modeling notes.
- `README.md`: quick orientation for humans and agents. Keep startup guidance here, not detailed job history.

## `docs/`

- What goes here: short workflow docs and operational repo guidance.
- What should not go here: per-project notes, measurements, or exported artifacts.
- Common workflow: read the relevant workflow doc before starting a reconstruction or greenfield job.

## `standards/`

- What goes here: reusable conventions for naming, previews, fits, and hardware starter values.
- What should not go here: project-specific dimensions or one-off repair decisions.
- Common workflow: check these files before locking dimensions, filenames, and previews.

## `templates/`

- What goes here: starter notes, manifests, checklists, and comparison logs.
- What should not go here: completed job records.
- Common workflow: copy the appropriate template into the project `notes/` folder and fill it as the job progresses.

## `scripts/`

- What goes here: small utilities that help inspect, compare, or validate work.
- What should not go here: large automation systems, CI logic, or unrelated experiments.
- Common workflow: run helper scripts during compare-and-revise or validation steps.

## `references/`

- What goes here: measurement notes, public references, and local-only paid references.
- What should not go here: final source files, exports, or generalized standards.
- Common workflow: sort inputs into `measured/`, `public/`, or `paid/` before modeling so trust level stays clear.

## `projects/`

- What goes here: active and archived project workspaces.
- What should not go here: shared standards or raw reference libraries that apply repo-wide.
- Common workflow: copy `projects/_template/` to `projects/<project_stem>/`, then work in `source/`, `exports/`, `notes/`, and `previews/`.

## Project Pattern

Each project should use:

- `projects/<project_stem>/source/`
- `projects/<project_stem>/exports/`
- `projects/<project_stem>/notes/`
- `projects/<project_stem>/previews/`

Use `projects/_template/` as the starting point for a new project folder.
