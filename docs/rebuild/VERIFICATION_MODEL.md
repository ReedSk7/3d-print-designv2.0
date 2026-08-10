# Parametric Part Workbench v3 Verification Model

## Core Rule

A file is not a fit result. V3 records separate evidence for specification
validity, SCAD compilation, mesh validity, dimensional review, coupon testing,
and real-world fit.

Only `physical_fit_confirmed` may be described to a user as **physically
verified**. All earlier states must be named exactly and must include remaining
warnings or assumptions.

## Evidence Layers

| Layer | What it establishes | What it does not establish |
| --- | --- | --- |
| Specification validity | Required schema fields, supported versions/units, valid types, legal parameter combinations, and complete required measurements | That OpenSCAD can compile or the dimensions fit a real object |
| SCAD compilation | OpenSCAD is installed, ran successfully, and emitted the requested artifact | Watertightness, correct bounds, printability, or fit |
| Mesh validity | Non-empty finite geometry, valid volume, watertight/winding/body/degeneracy requirements | Dimensional correctness or physical fit |
| Dimensional review | Actual mesh bounds match generator-computed expected bounds within documented tolerance; protected values remain traceable | Printer compensation, insertion force, retention, or installed function |
| Fit-test result | A purpose-built coupon was printed, measured/tested, and its result was recorded for the exact printer/material/nozzle/profile | Full-part assembly or service performance |
| Physical fit confirmation | The full printed part was checked against the real reused parts and required protected interfaces, with notes | Broader certification, durability, or safety claims not explicitly tested |

## Workflow States

The state value is singular for one immutable specification/artifact version.
Every version uses the shared computational prefix, then follows either the
coupon branch or the full-part branch:

1. `draft`
2. `measurement_contract_complete`
3. `generated`
4. `scad_compiled`
5. `mesh_valid`
6. `dimensions_reviewed`
7. coupon branch: `fit_coupon_generated` -> `fit_coupon_passed`
8. full-part branch: `full_part_exported` -> `physical_fit_confirmed`

`generated` means deterministic SCAD source was generated. It does not mean an
STL exists. `full_part_exported` means the complete STL passed the preceding
computational gates; it is still not physically verified.

## Legal Transitions

| From | Allowed next state | Required evidence |
| --- | --- | --- |
| `draft` | `measurement_contract_complete` | Valid schema and parameters; all required protected interfaces have authoritative dimensions |
| `measurement_contract_complete` | `generated` | Registry resolved exact generator ID/version and wrote deterministic versioned SCAD |
| `generated` | `scad_compiled` | OpenSCAD returned success and created the expected output |
| `scad_compiled` | `mesh_valid` | Mesh-QA checks passed with structured results |
| `mesh_valid` | `dimensions_reviewed` | Expected and actual bounds are within the documented tolerance and required dimensions are traceable |
| `dimensions_reviewed` | `fit_coupon_generated` | Clearance remains uncertain and a bounded coupon was generated for the protected interface |
| `dimensions_reviewed` | `full_part_exported` | No unresolved fit/clearance requires a coupon; the full-part artifact and manifest exist |
| `fit_coupon_generated` | `fit_coupon_passed` | Human-recorded printed coupon result for the exact profile passes the stated acceptance criterion |
| `full_part_exported` | `physical_fit_confirmed` | Human-recorded full-part fit against the real assembly/protected interfaces |

All other within-version transitions are illegal. `fit_coupon_passed` is
terminal for the coupon version. A later full-part specification starts at
`draft`, hash-links the passed coupon, matches its
printer/material/nozzle/profile, applies the selected candidate offset, and
runs every full-part computational gate before `full_part_exported`.

A failed validation does not advance state.
A failed coupon or physical fit does not rewrite or move a version backward;
record the failure and create a revised specification/artifact version beginning
at `draft`. This preserves evidence instead of erasing it.

## Measurement Gate

For replacement-part work, full-part generation is blocked when any required
protected interface:

- has no Measurement Contract entry;
- lacks an authoritative source;
- has missing units or tolerance;
- is marked unresolved; or
- relies only on a photo, inferred proportion, rough mesh, generic default, or
  unverified calibration value.

Confidence does not override authority. A high-confidence guess is still not an
authoritative protected dimension.

When nominal protected geometry is authoritative but printer fit/clearance is
the only uncertainty, the workflow may create a small coupon. A coupon must not
be used to invent the nominal mating dimension.

Advancing a coupon to `fit_coupon_passed` requires structured evidence: coupon
project/version and STL SHA-256, protected interface, selected offset, tester,
exact printer/material/nozzle/profile, acceptance criterion, measured result,
and `passed=true`. A later full-part run begins at `draft` as a new immutable
version and may carry this evidence; mismatched configuration or unsupported interface
fails before generation.

## Calibration Evidence

Starter profiles are explicitly `unverified`. A correction becomes `proven`
only when its record includes:

- printer/profile identity
- material and nozzle diameter
- fit type (hole, shaft, press, slip, or scale)
- nominal coupon geometry
- printed/measured result and units
- measurement/test method
- acceptance criterion and result
- date and notes

Applying a starter profile must produce a warning. Applying a proven profile to
a different printer/material/nozzle combination is not allowed without a new
record.

## Artifact Manifest

Every generation run writes machine-readable evidence under its workspace
version. At minimum the manifest records:

- manifest/schema version
- project and generator ID/version
- normalized millimeter parameters
- source specification identity
- generated paths, sizes, and hashes
- OpenSCAD/tool versions and command outcome
- mesh-QA measurements
- expected and actual bounds plus tolerance/delta
- starting and reached workflow state
- warnings and unresolved assumptions
- calibration profile status
- fit-coupon record when applicable
- physical-fit status, which defaults to unconfirmed
- timestamps

The source specification is not silently rewritten to claim physical success.
Physical evidence is an explicit later record and state transition.
`verify_mesh.py` rechecks the recorded STL byte size and SHA-256 before mesh or
bounds inspection, so a changed artifact cannot inherit an earlier result.

## Reporting Vocabulary

Allowed examples:

- `specification valid`
- `SCAD compiled`
- `mesh valid`
- `dimensions reviewed within 0.05 mm tolerance`
- `fit coupon generated; print result pending`
- `fit coupon passed for <printer/material/nozzle>`
- `full part exported; physical fit not confirmed`
- `physical fit confirmed` with the associated test record

Disallowed examples before the final state:

- `VERIFIED`
- `fit verified`
- `ready for installation`
- `guaranteed fit`
- any implication that compilation, watertightness, bounds, previews, or file
  completeness establish physical correctness

## CLI Completion Statement

The Phase 1 vertical slice ends no later than `full_part_exported`. A successful
example run must report the exact state reached and include this meaning:

> Computational checks passed. Physical fit is not confirmed.

Integration tests can prove deterministic generation and computational
validation; they cannot advance test fixtures to `physical_fit_confirmed`.
