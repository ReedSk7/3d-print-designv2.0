# Parametric Part Workbench v3 Target Architecture

## Product Boundary

Phase 1 is a local-first Python command-line system for deterministic,
dimension-driven OpenSCAD generators. It supports exactly these initial
families:

- `bushing`
- `round_adapter`
- `flange_plate`

It is not a photo-to-3D service, arbitrary CAD agent, freeform LLM geometry
generator, React dashboard, customer/quote system, cloud login, marketplace,
payment flow, deployment target, or customer portal.

## Proposed Structure

```text
core/
  models/
    spec.py         ProjectSpec and versioned policy/identity selections
    measurements.py MeasurementContract and its release gate
    artifacts.py    ArtifactRecord and ArtifactManifest
  units/
    conversion.py   explicit inch/mm conversion; millimeters internally
  validation/
    specification.py schema and parameter-document validation
    mesh.py          structured mesh QA and expected-bounds checks
  workflow/
    states.py       legal WorkflowState transitions
    ...             generation, OpenSCAD, mesh, and manifest orchestration
  profiles/
    models.py       typed starter/proven calibration records
    repository.py   profile loading and selection
    data/
      neutral_unverified_starter.json
generators/
  base.py          common PartGenerator contract and generation context
  registry.py      generator discovery by stable ID
  bushing/
  round_adapter/
  flange_plate/
scripts/
  generate_part.py
  validate_spec.py
  verify_mesh.py
examples/
  specs/
tests/
  unit/
  integration/
workspace/
  .gitkeep
schemas/
  project-spec-v1.schema.json
```

The exact filenames may evolve, but these responsibility boundaries must not be
collapsed into one CLI script or embedded in generator templates.

## Responsibilities

| Area | Owns | Must not own |
| --- | --- | --- |
| `core.models` | `ProjectSpec`, project/generator selections, verification/coupon policy, `MeasurementContract` and its protected-interface release gate, `ArtifactRecord`, and `ArtifactManifest` | OpenSCAD subprocess calls or generator-specific geometry |
| `core.units` | Loss-aware conversion of supported inch/mm inputs to millimeters | Fit compensation or display-only rounding |
| `core.validation` | Portable project/parameter schema validation and generic mesh/bounds validation | Generator-specific geometry rules, Measurement Contract policy, or physical-fit claims |
| `core.workflow` | Orchestration of registry resolution, versioned workspace paths, SCAD generation, OpenSCAD invocation, calls to mesh/bounds validators, atomic manifest publication, and state transitions | Mesh-validation formulas, generator-specific formulas, or UI state |
| `core.profiles` | Typed printer/material/nozzle identity, starter-versus-proven calibration evidence, and profile repository lookup | Invented values labeled calibrated |
| `generators.registry` | Stable ID lookup and duplicate/unknown-ID rejection | Hard-coded branching across the application |
| `generators.base` and each generator package | Common `PartGenerator`/generation-result contract plus metadata, generator version, parameter schema, impossible-dimension and wall rules, deterministic SCAD rendering, expected bounds, and example spec | Network calls, freeform model generation, global workflow state |
| `schemas/project-spec-v1.schema.json` | Portable JSON shape and version boundary for input specifications | Generator-specific semantic rules or runtime state mutation |
| `scripts/` | Thin CLI adapters with machine-usable exit codes and concise reports | Business logic duplicated from `core/` |
| `workspace/` | Local generated SCAD, STL, manifests, temporary files, and optional coupons | Source-controlled routine artifacts |

## Project Specification

One versioned JSON schema is the source request for a generation run. It must
represent:

- schema version
- project ID and human-readable name
- generator ID and generator version
- input units (`mm` or `inch`)
- generator parameters
- printer profile, material, and nozzle diameter
- fit/clearance profile
- Measurement Contract entries
- physical verification state
- created and updated timestamps
- generated-artifact manifest reference or embedded manifest data
- optional hash-linked passed fit-coupon evidence for a later full-part run
- warnings and unresolved assumptions

The typed model keeps `ProjectIdentity`, `GeneratorSelection`,
`VerificationPolicy`, `FitCouponRequest`, and `PhysicalVerification` separate
inside `ProjectSpec`; those concepts must not be collapsed into a single
freeform status or notes field.

Input values retain useful precision during conversion. Calculations and
expected bounds use millimeters. Rounding is explicit and limited to display or
serialization precision; it must not silently alter geometry.

## Measurement Contract

Each dimensional input used for replacement fit records:

- parameter name
- measured value and units
- measurement source
- confidence level
- tolerance
- protected-interface flag
- verification notes

A required protected interface must resolve to an authoritative dimension
before full-part generation. Photos, inferred proportions, rough meshes, and
generic defaults do not satisfy that gate. If the protected dimension is known
and only printer clearance is uncertain, the workflow may generate a bounded
fit-test coupon instead of the full part.

## Generator Contract and Registry

Generators are resolved through one registry by `generator_id`. Every entry
provides:

- stable generator ID and explicit generator version
- human-readable metadata
- parameter definitions and defaults
- validation rules and protected-interface requirements
- deterministic OpenSCAD source rendering
- expected bounding dimensions in millimeters
- one documented example specification
- unit and OpenSCAD-backed integration tests
- optional fit-coupon rendering for relevant interfaces

An unknown ID, duplicate ID, unsupported version, or invalid parameter set is a
hard failure. Application code must not contain scattered `if generator == ...`
branches.

## End-to-End Data Flow

```text
versioned JSON spec
  -> schema and semantic validation
  -> unit normalization to millimeters
  -> Measurement Contract/protected-interface gate
  -> registry lookup
  -> generator validation and expected bounds
  -> versioned SCAD under workspace/<project_id>/<version>/
  -> OpenSCAD compilation/export (fatal when unavailable)
  -> mesh-quality checks
  -> actual-versus-expected bounds comparison
  -> machine-readable artifact manifest and exact reached state
```

The CLI reports that physical fit is unconfirmed unless a separate real-world
record has legally advanced the project to `physical_fit_confirmed`.

## Calibration Profiles

Profiles are keyed by printer, material, and nozzle diameter. They may record
hole, shaft, press-fit, slip-fit, and dimensional-scale corrections.

Every value is one of:

- **unverified starter**: a transparent initial value that requires a coupon;
- **proven**: backed by recorded coupon geometry, nominal and measured results,
  printer/material/nozzle identity, date, method, and notes.

Missing proven calibration remains unknown; the system must not manufacture a
proven value from a generic rule.

Nozzle applicability uses a documented `0.000001 mm` comparison tolerance so
an exact inch-to-millimeter conversion residue cannot reject the same physical
nozzle setting. Geometry values themselves are not rounded to that tolerance.

## Workspace and Artifact Policy

A generation version writes beneath:

```text
workspace/<project_id>/<version>/
```

The directory may contain generated SCAD, STL, manifest JSON, temporary meshes,
logs, and optional coupons. These are ordinary local artifacts and are ignored
by Git. Versioned source specifications, generator source, tests,
documentation, and small intentional fixtures remain tracked. ASCII STL is not
a source-controlled fixture format.

## Phase 1 Quality Gates

- Unit tests cover units, schemas, invalid dimensions, wall thickness, fit
  profiles, registry lookup, state transitions, and manifests.
- Each initial generator has an integration test that generates SCAD, invokes
  OpenSCAD, exports STL, runs mesh QA, and checks bounds within documented
  tolerance.
- OpenSCAD absence fails locally and in CI.
- CI generates into a temporary directory and proves routine workspace outputs
  are not staged.
- Passing these gates establishes computational validation only, never physical
  fit.
