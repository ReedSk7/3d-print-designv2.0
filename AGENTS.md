# AGENTS.md

This file is authoritative for work in this repository. Supporting skills,
templates, scripts, and legacy notes must not override it.

## Approved Print Workshop extension

The owner approved a local React/Vite browser app and localhost bridge around
the existing deterministic Python backend, with selective legacy dashboard
reuse, reversible consolidation and optional Blender 5.2.2 inspection.
This specific approval permits the local app despite the earlier Phase 1 UI
boundary below. Read docs/PRINT_WORKSHOP_SPEC.md and docs/PRINT_WORKSHOP.md.
OpenSCAD remains geometry authority. No printer connections or print start,
automatic mesh repair, online asset downloads, hosted app, or physical-fit
claims without valid actual evidence. Canonical transition and worktree cleanup
remain separate from implementation and require verified preservation.

## Mission and Supported Scope

Build Parametric Part Workbench v3 as a reliable, local-first system for
deterministic, dimension-driven OpenSCAD generators.

The current generator contract supports `bushing`, `round_adapter`, and `flange_plate` through the
Python CLI. Do not add freeform LLM geometry, general photo-to-3D, arbitrary CAD
automation, the React dashboard, customer/quote/payment features, cloud login,
marketplaces, deployment, or a customer portal.

Project modernization may improve setup, verification, reproducible CAD renders,
and a separate slicer handoff without creating an owner model or print job.
Future original-design families and measured reconstruction need explicit scope,
a versioned deterministic generator and tests; Phase 1's family limit is a
roadmap boundary, while measurement/privacy/physical-fit rules endure.

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
- Keep owner-filled validation specifications and notes under the ignored
  `owner-validation/local/` path. Fit-result and physical-fit evidence records
  are immutable local artifacts and must not be committed.
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

Use the existing `openscad-3d-print-agent` skill and its focused references for
setup, dimension-driven CAD, visual review, and artifact/Bambu handoff. Check for
`AGENTS.override.md` and nearer instructions before each task. One independent
read-only reviewer is useful for difficult changes; no orchestration app is needed.
Project execution safeguards are in `.codex/config.toml`. Model and reasoning
are the user's choices in the Codex chat/session; this repository requires
neither a particular model nor a reasoning level. Do not restore model/effort
pins or override the user's selection. Model availability and any automatic
selection are controlled by the client/account, not repository instructions.
Confirm active settings in the client. Never change global auth/providers or
loosen permissions.

Primary commands:

```powershell
python scripts/check_environment.py
python scripts/validate_spec.py --spec <spec.json>
python scripts/generate_part.py --spec <spec.json>
python scripts/verify_mesh.py --manifest <manifest.json>
python scripts/inspect_project_status.py --project-version-dir <project/version>
python scripts/export_preview.py --manifest <artifact-manifest.json>
python scripts/prepare_bambu_handoff.py --manifest <artifact-manifest.json>
python -m pytest
```

## Git and Legacy Boundaries

- PR #2 supplies the V3 foundation; PR #3 adds the owner fit-evidence loop. The
  modernization branch starts at verified PR #3, not old main. Recheck ancestry
  and refs before continuing. PR #1 remains read-only salvage material.
- Do not normalize every legacy project in Phase 1. Follow
  `docs/rebuild/MIGRATION_MAP.md` and salvage individual files only with a
  documented reason.
- Do not merge to `main`, deploy, publish releases, delete history, rewrite
  commits, force-push, or modify restricted references as part of ordinary
  implementation.
- Preserve unrelated work and never claim a test, artifact, CI result, physical
  print, or deployment succeeded unless it actually did.
