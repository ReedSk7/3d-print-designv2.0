# AGENTS.md

This file is authoritative for work in this repository. Supporting skills,
templates, scripts, and legacy notes must not override it.

## Mission and Phase 1 Scope

Build Parametric Part Workbench v3 as a reliable, local-first system for
deterministic, dimension-driven OpenSCAD generators.

Phase 1 supports `bushing`, `round_adapter`, and `flange_plate` through the
Python CLI. Do not add freeform LLM geometry, general photo-to-3D, arbitrary CAD
automation, the React dashboard, customer/quote/payment features, cloud login,
marketplaces, deployment, or a customer portal.

## Modeling Contract

- All internal geometry calculations use millimeters; accept only explicit
  supported input units and preserve useful precision.
- Resolve generators through the registry by ID and version. Do not scatter
  generator-specific conditionals through the application.
- Keep generator metadata, parameter schema, defaults, validation, deterministic
  SCAD rendering, expected bounds, example spec, and tests together.
- OpenSCAD is the editable/generated geometry source. STL is an artifact.
- Never use freeform model-generated geometry for supported part families.

## Measurement Before Reconstruction

- Record every fit-relevant value in the Measurement Contract with value,
  units, source, confidence, tolerance, protected-interface flag, and notes.
- Never invent, conceal, or upgrade a guessed dimension into a measurement.
- Measured real-part dimensions and trusted drawings/CAD outrank photos and
  rough meshes. Record conflicts and unresolved assumptions.
- Block full replacement-part generation when a required protected interface
  lacks an authoritative dimension.
- If nominal geometry is authoritative and only clearance is uncertain,
  generate and test a small fit coupon before the full print.
- Calibration defaults are unverified starters. Label a value proven only when
  a printer/material/nozzle-specific test record supports it.

## Verification Language

Use the exact staged model in `docs/rebuild/VERIFICATION_MODEL.md`:

Every artifact version follows the shared prefix:

`draft` -> `measurement_contract_complete` -> `generated` ->
`scad_compiled` -> `mesh_valid` -> `dimensions_reviewed`.

A coupon version then ends at `fit_coupon_generated` or
`fit_coupon_passed`. A full-part version ends at `full_part_exported` and may
later reach `physical_fit_confirmed`. A full-part version that relies on a
coupon starts again at `draft` and hash-links the prior passed-coupon evidence.

- Enforce only documented legal transitions.
- File existence, SCAD compilation, STL export, watertightness, expected bounds,
  previews, and manifests are computational evidence only.
- Only `physical_fit_confirmed` may be described as physically verified.
- Report the exact state reached, failed checks, assumptions, and unresolved
  interfaces. Never use bare `VERIFIED` for generated artifacts.

## Files and Privacy

- Write routine generated SCAD, STL, PNG, 3MF, temporary meshes, logs, and local
  project data under `workspace/<project_id>/<version>/`.
- Do not commit routine generated artifacts or ASCII STL.
- Track versioned source specs, generator code/templates, tests, documentation,
  and small intentional fixtures only.
- Never commit paid, private, customer, or ambiguously licensed references.
- Do not copy PR #1's generated-output or reference-photo collections.

## Engineering Workflow

1. Inspect the authoritative branch, repository status, relevant docs, and
   existing implementation before editing.
2. Make the smallest change that preserves responsibility boundaries in
   `docs/rebuild/TARGET_ARCHITECTURE.md`.
3. Add or update unit tests and OpenSCAD-backed integration tests.
4. Run the most relevant local checks. OpenSCAD absence is a failure, not a
   warning-only success.
5. Review the diff for generated artifacts, restricted data, unrelated edits,
   and misleading verification language.
6. Report exact commands, results, reached states, and remaining physical/manual
   work.

Primary commands:

```powershell
python scripts/validate_spec.py --spec <spec.json>
python scripts/generate_part.py --spec <spec.json>
python scripts/verify_mesh.py --manifest <manifest.json>
python -m pytest
```

## Git and Legacy Boundaries

- The rebuild branch starts from verified `main`; PR #1 is read-only salvage
  material and must not be merged or copied wholesale.
- Do not normalize every legacy project in Phase 1. Follow
  `docs/rebuild/MIGRATION_MAP.md` and salvage individual files only with a
  documented reason.
- Do not merge to `main`, deploy, publish releases, delete history, rewrite
  commits, force-push, or modify restricted references as part of ordinary
  implementation.
- Preserve unrelated work and never claim a test, artifact, CI result, physical
  print, or deployment succeeded unless it actually did.
