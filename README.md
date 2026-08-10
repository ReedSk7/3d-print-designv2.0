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

## Prerequisites

- Python 3.13 or newer supported by the pinned dependencies
- OpenSCAD available on `PATH`, through `OPENSCAD_PATH`, or in the standard
  Windows installation directory

OpenSCAD is mandatory. Missing OpenSCAD is a failure, not a skipped warning.

Windows setup:

```powershell
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& 'C:\Program Files\OpenSCAD\openscad.com' --version
```

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
coupon artifact SHA-256, selected candidate offset, acceptance result, tester,
and exact printer/material/nozzle/profile. A later full-part specification may
link that evidence; the generator applies the selected offset only when those
identities match.

The bundled `neutral_unverified_starter` profile applies zero offsets and unit
scale. Those neutral values are explicitly unverified; they are not claimed as
proven calibration.

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
