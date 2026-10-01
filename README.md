# Parametric Part Workbench v3

Parametric Part Workbench v3 is a local-first command-line system for creating
common functional 3D-printable parts from explicit dimensions. Phase 1 uses
deterministic Python generators that emit OpenSCAD; it does not use freeform AI
geometry, photos, or autonomous arbitrary-CAD generation.

Supported generator IDs:

- `bushing`
- `round_adapter`
- `flange_plate`

## Verification Promise

The workbench keeps different kinds of evidence separate:

`specification valid` -> `SCAD compiled` -> `mesh valid` ->
`dimensions reviewed`, followed by either a coupon result or a full-part
export. A passed coupon is linked into a new full-part version; it is not a
shortcut around that version's computational checks.

A successful CLI run ends at `full_part_exported` (or
`fit_coupon_generated`). It means deterministic computational checks passed.
It does **not** mean the part physically fits. Only a recorded real-world test
may advance a version to `physical_fit_confirmed`.

See [docs/rebuild/VERIFICATION_MODEL.md](docs/rebuild/VERIFICATION_MODEL.md).

## Setup and daily commands

Start with [Quick Start](docs/QUICK_START.md) for safe laptop checkout, Windows
virtual-environment setup, project Codex settings, VS Code tasks, version-bound
previews and manual Bambu Studio handoff. See [Upgrade Report](docs/UPGRADE_2026-09-30.md)
for the tested environment and remaining limitations.

- Python 3.12 or 3.13 with `requirements-lock.txt` in the project `.venv`.
- OpenSCAD is mandatory for generation/integration. Optional Bambu and graphics
  capabilities are reported separately by `scripts/check_environment.py`.
- The current printer is Bambu Lab P2S; installed nozzle, filament, plate and AMS
  remain owner-confirmed details, not defaults inferred from example specs.

## Generate a Part

```powershell
& .\.venv\Scripts\python.exe scripts\generate_part.py --spec examples\specs\bushing_example.json
```

Equivalent cross-platform command after activating the environment:

```text
python scripts/generate_part.py --spec examples/specs/bushing_example.json
```

The command validates the specification, converts dimensions to millimeters,
resolves the generator by ID/version, writes versioned SCAD, compiles a binary
STL with OpenSCAD, runs mesh QA, compares actual and expected bounds, and writes
an artifact manifest.

Routine outputs are local and ignored:

```text
workspace/<project_id>/<version>/
```

The workflow refuses to overwrite an existing project version.

Other CLIs:

```powershell
& .\.venv\Scripts\python.exe scripts\validate_spec.py --spec examples\specs\flange_plate_example.json
& .\.venv\Scripts\python.exe scripts\verify_mesh.py --manifest workspace\flange_plate_example\v01\artifact-manifest.json
```

## Owner Fit-evidence Loop

Phase 1.1 keeps generation and human evidence as separate immutable steps:

`measured full-part draft` -> `generated fit coupon` -> `recorded printed coupon result` ->
`new linked full-part draft` -> `full_part_exported` -> `recorded completed-part result`.

The focused commands are:

- `scripts/create_fit_coupon.py` creates a coupon specification and does not
  print, test, or imply a pass;
- `scripts/record_fit_coupon_result.py` records an owner's real coupon outcome
  against verified manifest/STL/spec hashes;
- `scripts/create_full_part_from_coupon.py` creates a fresh full-part spec from
  a valid passed coupon chain without skipping generation gates;
- `scripts/record_physical_fit.py` records results for every protected interface
  against an exact exported full-part artifact; and
- `scripts/inspect_project_status.py` reports the highest defensible state and
  whether physical-verification wording is allowed.

Owner-filled inputs and evidence remain ignored local files. Start with
[Owner Fit Validation](docs/OWNER_FIT_VALIDATION.md), which deliberately leaves
the installed Bambu Lab P2S nozzle, measured pin diameter, and five candidate
offsets blank for the owner to enter.

## Project Specifications

`schemas/project-spec-v1.schema.json` is the versioned input contract. A spec
records project/generator identity, units, printer/material/nozzle selection,
generator parameters, a calibration/fit profile, Measurement Contract entries,
workflow and physical-fit states, timestamps, warnings, assumptions, and
artifact records.

All internal calculations use millimeters. Inch input uses the exact
`25.4 mm/in` definition and is not silently rounded for geometry.

Replacement-part full generation is blocked until every generator-declared
protected interface has a matching authoritative Measurement Contract entry.
If the nominal interface is known but print clearance is uncertain, request a
small candidate-based fit coupon instead of the full part.

A passed coupon is recorded as structured `fit_coupon_evidence` containing the
coupon manifest and STL SHA-256 digests, selected candidate offset, acceptance
result, tester, and exact printer/material/nozzle/profile. A later full-part
specification may link that evidence; the generator applies the selected offset
only when the complete cited evidence package and those identities match.

The bundled `neutral_unverified_starter` profile applies zero offsets and unit
scale. Those neutral values are explicitly unverified; they are not claimed as
proven calibration.

Fit direction is explicit: hole slip allowance enlarges a hole, shaft slip
allowance reduces a shaft, hole press allowance reduces a hole, and shaft press
allowance enlarges a shaft. Hole and shaft dimensional corrections are separate
signed values; a positive correction enlarges the corresponding feature. The
legacy global slip/press offsets remain compatibility inputs for generator
version `1.0.0`; version `1.1.0` does not apply them across unrelated interfaces.

Generator version `1.0.0` remains available for existing specifications and
manifests. Version `1.1.0` adds independent fit controls and interface-specific
coupon behavior; selecting it is an explicit specification change rather than
a silent change to legacy geometry.

## Tests

```powershell
& .\.venv\Scripts\python.exe -m pytest tests\unit -q
& .\.venv\Scripts\python.exe -m pytest tests\integration -q
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe scripts\check_output_policy.py
```

Integration tests invoke real OpenSCAD for all three generators and fail if it
is unavailable.

## Architecture and Migration

- [Audit](docs/rebuild/AUDIT.md)
- [Target architecture](docs/rebuild/TARGET_ARCHITECTURE.md)
- [Migration map](docs/rebuild/MIGRATION_MAP.md)
- [Verification model](docs/rebuild/VERIFICATION_MODEL.md)

The legacy `projects/`, `templates/`, and reconstruction documents remain
historical evidence only. Phase 1 does not normalize those projects or import
the dashboard, generated-output collection, or reference-photo collection from
draft PR #1.
