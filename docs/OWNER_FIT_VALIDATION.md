# Owner Fit Validation: Bambu Lab P2S, PETG, Bushing 1.1.0

This is the first owner-operated validation loop for Parametric Part Workbench
v3. It uses a smooth drill-bit shank or gauge pin to select a bushing
`inside_diameter` correction for one exact printer, material, installed nozzle,
profile, slicer setup, and print process.

Codex has not measured the pin, identified the installed nozzle, printed a
coupon, or tested a finished bushing. Do not substitute a labeled nominal drill
size for a measurement. Do not describe any output as physically verified until
the completed full part has its own valid physical-fit evidence record.

## Local-only files

The tracked file
`owner-validation/templates/bambu_p2s_petg_bushing_inside_fit.template.json`
is deliberately invalid. It contains required `OWNER MUST ENTER` placeholders
instead of plausible numbers. Copy it to the ignored local directory before
entering owner data:

```powershell
New-Item -ItemType Directory -Force owner-validation\local | Out-Null
Copy-Item `
  owner-validation\templates\bambu_p2s_petg_bushing_inside_fit.template.json `
  owner-validation\local\p2s_petg_bushing_source.json
Copy-Item `
  owner-validation\templates\bambu_p2s_petg_bushing_coupon_inputs.template.json `
  owner-validation\local\p2s_petg_bushing_coupon_inputs.json
Copy-Item `
  owner-validation\templates\bushing_physical_interface_results.template.json `
  owner-validation\local\p2s_petg_bushing_interfaces_v02.json
```

The copied specification, notes, generated SCAD/STL/manifest, coupon-result
evidence, and physical-fit evidence must remain local. `owner-validation/local/`
and `workspace/` are ignored, and the output-policy check rejects forced-added
owner-local or routine artifact files.

## 1. Measure the test pin

Use the smooth shank, not the drill flutes, cutting edge, or a damaged end.
Clean the pin and caliper jaws. Confirm the caliper reads zero when closed, then:

1. Hold the jaws square to the shank and use consistent, light pressure.
2. Measure at several axial locations and at least two rotations.
3. Record every reading in local notes. If they differ, record the spread; do
   not hide it by silently averaging.
4. Enter the selected authoritative diameter and an honest tolerance in the
   Measurement Contract. Identify the pin and measurement tool in
   `measurement_source` and explain repeatability in `verification_notes`.

Millimeters are the simplest choice. Inch values are allowed when the spec says
`"input_units": "inch"`; conversion uses exactly 25.4 mm per inch.

## 2. Complete and validate the local source specification

In `owner-validation/local/p2s_petg_bushing_source.json`:

- replace the nozzle placeholder with the diameter of the nozzle actually
  installed in the Bambu Lab P2S; do not assume a standard size;
- enter the caliper-measured pin diameter in both the generator's
  `inside_diameter` and its matching Measurement Contract entry;
- enter the intended full bushing outside diameter, length, chamfer, and minimum
  wall thickness;
- keep generator `bushing` version `1.1.0` and coupon interface
  `inside_diameter`;
- choose `inside_fit` and `outside_fit` independently;
- choose whether the full bushing is split and enter the computational mesh
  bounds tolerance; when `split` is `true`, also add the measured or intentionally
  designed numeric `split_width`; and
- replace timestamps and every remaining `OWNER MUST ENTER` value. Replace the
  unresolved-assumption placeholder with honest text or an empty list.

The separate `p2s_petg_bushing_coupon_inputs.json` file is a command-input
worksheet, not a project specification. Replace all five candidate-offset
placeholders with five distinct numeric offsets chosen by the owner, and replace
its coupon project ID. Copy those values into the coupon-creation command in the
next step. Do not add the worksheet keys to the source specification.

For the `inside_diameter` hole coupon, a positive dimensional correction makes
the hole larger and increases clearance; a negative correction makes it smaller
and increases interference. For an `outside_diameter` shaft coupon, the same
sign has the opposite fit effect: a positive correction makes the shaft larger
and increases interference, while a negative correction makes it smaller and
increases clearance. Hole and shaft allowances are distinct; never transfer a
selected hole correction to an outside diameter or another interface.

Calibration profiles encode that distinction explicitly. Signed
`hole_dimensional_correction_mm` and `shaft_dimensional_correction_mm` adjust
the corresponding finished dimension. Non-negative `hole_slip_allowance_mm`
adds to a hole and `shaft_slip_allowance_mm` subtracts from a shaft. Non-negative
`hole_press_allowance_mm` subtracts from a hole and `shaft_press_allowance_mm`
adds to a shaft. All bundled starter values remain zero and unverified; these
field names define direction, not a proven amount.

Find any missed placeholders and validate the draft full-part specification:

```powershell
Select-String -Path owner-validation\local\p2s_petg_bushing_source.json `
  -Pattern 'OWNER MUST ENTER'
& .\.venv\Scripts\python.exe scripts\validate_spec.py `
  --spec owner-validation\local\p2s_petg_bushing_source.json
```

Do not continue if either command reports a placeholder, invalid schema,
missing authoritative interface, or impossible wall thickness.

## 3. Create and generate the coupon

First create a new coupon specification from the validated draft. Supply all
five owner-selected offsets and a new coupon project ID/version. Coupon-spec
creation does not generate geometry unless the explicit generation option is
present. `--candidate-offset` values use the source specification's input units;
this owner template uses millimeters.

```powershell
& .\.venv\Scripts\python.exe scripts\create_fit_coupon.py `
  --source-spec owner-validation\local\p2s_petg_bushing_source.json `
  --interface inside_diameter `
  --candidate-offset <OFFSET_1> `
  --candidate-offset <OFFSET_2> `
  --candidate-offset <OFFSET_3> `
  --candidate-offset <OFFSET_4> `
  --candidate-offset <OFFSET_5> `
  --coupon-project-id <NEW_COUPON_PROJECT_ID> `
  --coupon-version v01 `
  --output-spec owner-validation\local\p2s_petg_bushing_coupon_v01.json `
  --workspace-root workspace
```

Review and validate the created coupon specification. Then generate it as a
separate, explicit action:

```powershell
& .\.venv\Scripts\python.exe scripts\generate_part.py `
  --spec owner-validation\local\p2s_petg_bushing_coupon_v01.json
```

The expected state is `fit_coupon_generated`, not a fit pass. Record the exact
manifest path printed by the command.

## 4. Keep slicing and printing conditions consistent

Use the same Bambu Lab P2S, the same installed nozzle, PETG stock and condition,
and the same intended full-part process. Keep these slicer and process choices
constant between coupon and full part, or record and justify any difference:

- slicer and profile version;
- orientation, layer height, line width, wall count/order, and top/bottom setup;
- flow/extrusion multiplier and any X-Y or hole compensation;
- speed, acceleration, temperatures, cooling, chamber/ambient conditions, and
  filament drying state;
- first-layer settings and elephant-foot compensation; and
- support, brim, cleanup, reaming, sanding, or other post-processing.

Do not change X-Y or hole compensation between candidates. Do not ream or sand
only the winning hole unless the full bushing will receive the identical,
documented process. Confirm each candidate label is legible before testing.

## 5. Select and record the coupon result

Define the acceptance criterion before choosing a candidate—for example, the
owner's required insertion/removal behavior with no visible damage. Identify a
candidate from its real printed label and confirm the label maps to an offset in
the manifest at
`checks.normalized_parameters_mm.coupon_candidate_map`. Labels are numbered
`1` through `N`; use the exact label/index/offset/dimension mapping rather than
inferring an offset from physical position. Test consistently and record
observed behavior, including a failure rather than forcing a pass.

Compute the digest of the immutable manifest bytes immediately before recording
the result:

```powershell
$couponManifest = 'workspace\<COUPON_PROJECT_ID>\v01\artifact-manifest.json'
$couponManifestSha = `
  (Get-FileHash -Algorithm SHA256 -LiteralPath $couponManifest).Hash.ToLowerInvariant()
```

```powershell
& .\.venv\Scripts\python.exe scripts\record_fit_coupon_result.py `
  --manifest $couponManifest `
  --manifest-sha256 $couponManifestSha `
  --selected-offset-mm <PRINTED_CANDIDATE_OFFSET> `
  --tester <OWNER_NAME_OR_LOCAL_IDENTIFIER> `
  --tested-at <ISO_8601_DATE_TIME> `
  --acceptance-criterion <QUOTED_CRITERION> `
  --observed-result <QUOTED_OBSERVATION> `
  --notes <QUOTED_NOTES> `
  --passed `
  --require-passed
```

Use `--failed` instead of `--passed --require-passed` when the
criterion was not met. A failed record must never be reused as passed evidence.
The command verifies the manifest, coupon STL, specification snapshot, selected
candidate, and exact configuration before writing a new immutable record. It
does not rewrite the generation manifest, and it refuses duplicate or
conflicting results for that coupon version. Use a new coupon version for a new
trial. A valid `fit-result.evidence.json` raises the highest defensible status to
`fit_coupon_passed`; it means only that this printed coupon met the stated coupon
criterion.

Immediately retain the exact evidence digest printed by the command. This is
the external integrity anchor that prevents a later edit from turning a failed
result into a passed result or changing the selected offset. You may recompute
it immediately after creation and record it in local owner notes:

```powershell
$couponEvidence = `
  'workspace\<COUPON_PROJECT_ID>\v01\fit-result.evidence.json'
$couponEvidenceSha = `
  (Get-FileHash -Algorithm SHA256 -LiteralPath $couponEvidence).Hash.ToLowerInvariant()

& .\.venv\Scripts\python.exe scripts\inspect_project_status.py `
  --project-version-dir workspace\<COUPON_PROJECT_ID>\v01 `
  --fit-evidence-sha256 $couponEvidenceSha
```

Without that owner-supplied digest, the standalone coupon status is reported as
`unanchored` and cannot advance beyond `fit_coupon_generated`.

## 6. Create and generate the linked full bushing

Use the original full-part specification and the new passed-evidence file to
create a fresh full-part version. The command copies the accepted offset and
provenance; it does not edit the original spec or bypass generation checks.

```powershell
& .\.venv\Scripts\python.exe scripts\create_full_part_from_coupon.py `
  --source-spec owner-validation\local\p2s_petg_bushing_source.json `
  --coupon-evidence $couponEvidence `
  --coupon-evidence-sha256 $couponEvidenceSha `
  --new-version v02 `
  --output-spec owner-validation\local\p2s_petg_bushing_full_v02.json `
  --workspace-root workspace

& .\.venv\Scripts\python.exe scripts\generate_part.py `
  --spec owner-validation\local\p2s_petg_bushing_full_v02.json
```

Use the exact printer, PETG, installed nozzle, calibration profile, generator
version, and unchanged generator parameters bound into the coupon chain. A
mismatch must be corrected by a new coupon/version, not by editing evidence.
The expected computational state after generation is `full_part_exported`.

## 7. Test and record the completed bushing

Print the full bushing under the recorded process. Test every protected
interface declared by bushing 1.1.0, not only the inside diameter. Record the
inside interface against the measured pin and the outside interface against its
real mating housing or an explicitly identified authoritative gauge.

Prepare a local JSON interface-results file in the format accepted by
`record_physical_fit.py`, with one result and acceptance criterion per declared
protected interface. Optional measured dimensions must include their real units
and source; omit them when none were measured. Then bind the observations to the
exact exported version:

```json
[
  {
    "interface_parameter": "inside_diameter",
    "acceptance_criterion": "OWNER MUST ENTER",
    "observed_result": "OWNER MUST ENTER",
    "passed": "OWNER MUST ENTER true or false",
    "notes": "OWNER MUST ENTER OR USE AN EMPTY STRING"
  },
  {
    "interface_parameter": "outside_diameter",
    "acceptance_criterion": "OWNER MUST ENTER",
    "observed_result": "OWNER MUST ENTER",
    "passed": "OWNER MUST ENTER true or false",
    "notes": "OWNER MUST ENTER OR USE AN EMPTY STRING"
  }
]
```

Replace every placeholder; `passed` must become a JSON Boolean without quotes.
An optional measured-dimensions JSON file is an array of objects with
`parameter_name`, numeric `measured_value`, `units` (`mm` or `inch`),
`measurement_source`, and optional `notes`.

```powershell
$fullManifest = 'workspace\<FULL_PROJECT_ID>\v02\artifact-manifest.json'
$fullManifestSha = `
  (Get-FileHash -Algorithm SHA256 -LiteralPath $fullManifest).Hash.ToLowerInvariant()
```

```powershell
& .\.venv\Scripts\python.exe scripts\record_physical_fit.py `
  --manifest $fullManifest `
  --manifest-sha256 $fullManifestSha `
  --confirmed-by <OWNER_NAME_OR_LOCAL_IDENTIFIER> `
  --confirmed-at <ISO_8601_DATE_TIME> `
  --interface-results-json owner-validation\local\p2s_petg_bushing_interfaces_v02.json `
  --notes <QUOTED_NOTES>
```

The command must verify the full-part manifest plus exact STL, SCAD, and spec
snapshot hashes and require a result for every protected interface. Only a valid
immutable `physical-fit.evidence.json` record may report
`physical_fit_confirmed`. A duplicate or conflicting record requires a new full
part version. The original spec and generation manifest remain immutable.

Retain the new physical-evidence digest printed by the command. As with coupon
evidence, status inspection requires this external anchor before it permits the
physical-fit claim:

```powershell
$physicalEvidence = `
  'workspace\<FULL_PROJECT_ID>\v02\physical-fit.evidence.json'
$physicalEvidenceSha = `
  (Get-FileHash -Algorithm SHA256 -LiteralPath $physicalEvidence).Hash.ToLowerInvariant()
```

Inspect the evidence chain at any point:

```powershell
& .\.venv\Scripts\python.exe scripts\inspect_project_status.py `
  --project-version-dir workspace\<FULL_PROJECT_ID>\v02 `
  --fit-evidence-sha256 $couponEvidenceSha `
  --physical-evidence-sha256 $physicalEvidenceSha
```

Before valid full-part evidence exists, the status must say that the phrase
`physically verified` is not allowed.

Useful checkpoints are: `fit_coupon_generated` immediately after coupon
generation, `fit_coupon_passed` only after a valid passed coupon record,
`full_part_exported` after the linked part clears every computational gate, and
`physical_fit_confirmed` only after a valid completed-part record covers every
protected interface. A recorded failed coupon remains immutable evidence of its
failure and never advances the state. Any failed full-part interface blocks
physical-fit confirmation; retain the raw observation in local notes and make a
new part version after correction.

## 8. What the result proves—and does not prove

A valid coupon result supports one interface correction for the exact recorded
configuration and criterion. A valid completed-bushing record confirms only the
interfaces and observations actually documented for that exact artifact.

It does not establish durability, wear life, load rating, impact resistance,
temperature or chemical resistance, pressure capability, safety, regulatory
compliance, certification, interchangeability with other printers/materials/
nozzles, or future-batch consistency. Those claims require their own defined
tests and evidence. Computational success alone never proves physical fit.
