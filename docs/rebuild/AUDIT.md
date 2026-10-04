# Parametric Part Workbench v3 Audit

Audit date: 2026-08-10

## Scope and Method

This audit compares the verified `main` baseline with draft PR #1 as read-only
salvage material. It inspects Git metadata, source, scripts, specifications, and
notes. Binary models and reference images were inventoried by path, size, and
blob identity; their contents were not dumped or treated as design authority.

The classifications used here are:

- **keep**: suitable for continued use with its present responsibility.
- **refactor**: contains useful behavior, but its API, output, or verification
  semantics must change for v3.
- **archive**: retain as historical context, not as an active v3 dependency.
- **remove from active workflow**: do not invoke or migrate into the Phase 1
  path; Git history remains intact.
- **investigate**: provenance, privacy, duplication, measurements, or physical
  evidence must be resolved before reuse.

No audited legacy item qualifies for `keep` unchanged. Every useful behavior
requires v3 semantics or remains historical/investigative material.

## Verified Starting Points

| Item | Verified value | Decision |
| --- | --- | --- |
| Current `origin/main` | `65b8ae6b8d9d19719f4f2e6a3a565eb2edd881e1` | v3 branch starts here |
| Rebuild branch | `rebuild/parametric-part-workbench-v3-001` | isolated implementation branch |
| PR #1 | Open draft; do not merge | salvage individual text/source files only |
| PR #1 head | `agent/consolidate-3d-workspace` at `53a934c59bb13f21d6cbee9d4a7b4a0279c94eeb` | read-only comparison point |
| Merge base | `65b8ae6b8d9d19719f4f2e6a3a565eb2edd881e1` | confirms PR branch descends from the audited main |

PR #1 changes 477 files (`465` added, `12` modified) with 13,800,073
reported additions and 66 deletions. Its tree contains 527 files versus 62 on
`main`. This scale is primarily generated output, not a coherent v3
architecture.

## Required Item Classification

| Item | Classification | Evidence and v3 action |
| --- | --- | --- |
| `scripts/_openscad_cli.py` | refactor | Safe argument-list execution, Windows discovery, and explicit OpenSCAD-not-found failure are useful. Move the capability behind the workflow layer, add structured results/tool version/timeout handling, and keep OpenSCAD absence fatal. |
| `scripts/export_stl.py` | refactor | The baseline correctly checks that OpenSCAD returned success and produced a file, but forced `--export-format=asciistl`, accepted arbitrary output paths, and printed generic `PASS`. The compatibility script now emits binary STL with an explicit non-fit statement; the v3 workflow additionally confines routine artifacts to `workspace/`, hashes them, and reports exact states. |
| `scripts/export_preview.py` | archive | Its camera presets are useful later, but PNG generation is not part of the Phase 1 vertical slice and cannot prove dimensional or physical correctness. Keep out of the active generator path. |
| `scripts/mesh_quality_check.py` from PR #1 | refactor | Useful checks include non-empty geometry, finite bounds, volume, watertightness, winding, connected bodies, and degenerate faces. Re-expose them as structured mesh-QA data used by `verify_mesh.py`; a mesh `PASS` must mean only `mesh_valid`. |
| `scripts/compare_mesh.py` | refactor | Bounding-box and projected-silhouette calculations are useful review tools. The v3 gate needs deterministic expected-versus-actual bounds with a documented tolerance and must not equate silhouette similarity with fit. |
| `scripts/next_version.py` | remove from active workflow | It discovers versions by scanning legacy project folders and copies SCAD/Markdown while replacing status strings. V3 versions are driven by immutable specifications and manifests under a deterministic workspace path. |
| `scripts/validate_scad.py` | refactor | Preserve useful source and OpenSCAD invocation checks, but separate specification validation, SCAD compilation, mesh QA, and dimensional review into distinct results. Its former warning-only missing-OpenSCAD path is now a default failure with an explicit structural-only opt-out. |
| `scripts/check_project_outputs.py` / `scripts/validate_project.py` | remove from active workflow | These inspect only the legacy folder/file contract. Their output now says file presence cannot confirm fit, and new automation is directed to `validate_spec.py` and `generate_part.py`. |
| `.agents/skills/openscad-3d-print-agent` | refactor | The baseline helper routed new work through legacy task modes, templates, preview/file-presence checks, and ambiguous status language. Its v3 replacement now points only to the specification, registry, workspace, exact-state CLI workflow, and root `AGENTS.md`. |
| `standards/hardware_library.scad` from PR #1 | investigate | The shared functions are a useful pattern, but material/nozzle offsets and fit dimensions are starter assumptions. They must not enter v3 as proven calibration without traceable coupon evidence. |
| `standards/printer_material_profiles.json` from PR #1 | investigate | It mixes generic values with a record labeled calibrated. Proven status, source measurements, printer/material/nozzle identity, and coupon result require explicit validation before migration. Otherwise values must be labeled unverified starters. |
| `templates/` | archive | The templates assume the legacy `projects/<stem>/{source,exports,notes,previews}` workflow and extensive generated deliverables. Do not use them to generate v3 projects; retain only as historical guidance. |
| `app/` from PR #1 | remove from active workflow | Phase 1 excludes the React dashboard. More importantly, `app/server/index.js` labels a project `VERIFIED` when expected files merely exist. Customer, quote, delivery, and dashboard state are also outside scope. |
| `projects/simple_wall_bracket_example` | archive | Useful as historical CLI/CI mechanics, but it is not one of the three supported v3 generator families. Its committed STL/PNG files are not a v3 completion model. |
| PR #1 legacy projects | archive | Do not copy the collection. Individual source or notes remain separate `investigate` candidates under the migration map; generated outputs and reference media are excluded. |

## Verification Defect Confirmed

The legacy workflow has multiple independent ways to turn artifact presence into
an overly broad success statement:

- `app/server/index.js` derives `VERIFIED` solely from the presence of SCAD,
  STL, previews, notes, a manifest, and a review report.
- `scripts/check_project_outputs.py` checks completeness of files and status
  text, not whether a printed part fits.
- `scripts/verify_project.py` and project-specific validators print `PASS` after
  computational checks.
- Several manifests use `verified`, `PASS`, or `complete` while their own next
  actions still require a test print.

These tools may establish artifact existence, SCAD compilation, mesh validity,
or bounded dimensions. None can establish physical fit. V3 replaces the single
success label with the staged model in `VERIFICATION_MODEL.md`.

## Layout and Artifact Findings

The PR tree contains 21 project entries with incompatible layouts. Most use
`source/`, `exports/`, `notes/`, and `previews/`; notable exceptions include:

- `projects/washer_inner_latch_w11457841/v01/{scad,stl,renders,references}`
- `projects/peg_hook_6p8mm_fit_petg`, whose editable workflow is Python-based
- `projects/kobalt_81798_socket_organizer/tools`, with bespoke build/validation
- root-level `metric_to_standard_chart_output/`, mixing source and outputs
- `projects/vevor_packout_single_drawer_organizer`, a Git submodule/gitlink
- both `battery_strap_holder/` and `battery-strap-holder/` for the same target

Generated artifacts dominate the PR branch:

| Type | Count in PR tree | Approximate bytes | V3 policy |
| --- | ---: | ---: | --- |
| STL | 112 | 335,252,902 | ignored routine artifact under `workspace/` |
| PNG | 100 | 7,210,509 | ignored routine artifact; not Phase 1 evidence |
| 3MF | 6 | 4,898,162 | ignored; not a Phase 1 requirement |
| JPG references | 22 | 6,049,104 | do not migrate without privacy/rights review |

Git reports line counts rather than binary markers for 107 of the 110 changed
STLs, demonstrating that ASCII STL was committed extensively. The legacy
`.gitignore` does not generally exclude STL, PNG, 3MF, logs, or local project
workspaces. V3 must ignore these outputs and validate that they are not staged.

## Salvage Decision

No generated output or reference-photo collection from PR #1 is migrated.
Potential source-level salvage is limited to individually reviewed behavior:

- OpenSCAD discovery and argument-list execution from `_openscad_cli.py`
- mesh-QA predicates from `mesh_quality_check.py`
- bounds/silhouette calculations from `compare_mesh.py`
- the narrow hardware-library integration pattern in commit `53a934c...`
- selected legacy notes as negative regression evidence

All salvaged behavior must adopt the v3 schema, registry, workspace, manifest,
and verification vocabulary. Historical passing output is not inherited as a
v3 test result.
