# Repository Layout

The active Phase 1 layout is defined in
`docs/rebuild/TARGET_ARCHITECTURE.md`.

```text
core/          shared models, units, validation, workflow, and profiles
generators/    deterministic family packages and registry
schemas/       versioned project-specification schema
scripts/       thin command-line entrypoints
examples/      source-controlled specifications
tests/         unit and OpenSCAD-backed integration tests
workspace/     ignored local generated artifacts; only .gitkeep is tracked
docs/rebuild/  audit, architecture, migration, and verification decisions
```

`projects/`, `templates/`, older standards, and older modeling workflow
documents are legacy evidence. They are not the v3 generation path and must not
be bulk-normalized during Phase 1.

Routine SCAD, STL, PNG, 3MF, temporary meshes, logs, and manifests belong under
`workspace/<project_id>/<version>/` and are not source controlled.
