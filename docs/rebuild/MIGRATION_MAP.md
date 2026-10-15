# Parametric Part Workbench v3 Migration Map

## Migration Rule

V3 starts from the verified `main` SHA and implements a clean deterministic
core. PR #1 is not merged. A legacy item is copied only when its source-level
behavior has a named v3 owner, its provenance is acceptable, and its claims are
rewritten using the v3 verification model.

Generated STL, PNG, 3MF, temporary meshes, logs, project workspaces, and photo
collections are intentionally not migrated.

## Candidate Examples and Manual Migrations

| Legacy item | Category | Migration decision |
| --- | --- | --- |
| `projects/ac_flange_plate_adapter` | manual migration candidate | Source may inform `flange_plate` and `round_adapter` edge cases. Its notes say key dimensions are inferred and hose fit is untested, so it cannot become a normative example without a new specification and authoritative interfaces. |
| `projects/hisense_ap1219cr1w_5in_coupling` | manual migration candidate | Useful tapered adapter/flange and lock-tab case. Real-machine engagement remains unverified; migrate formulas only after protected-interface review. |
| `projects/hisense_k1983844_dummy_coupling` | manual migration candidate | Useful round reducer case, but depends on reference STL/photo material and still requires physical hose testing. |
| `projects/simple_wall_bracket_example` | historical example | Retain only as legacy CI mechanics; it is not a Phase 1 generator family. Do not carry its STL/PNG into v3 examples. |
| `projects/agent_smoke_test_hex_bit_holder` | archive | Deterministic but outside supported generator families; its committed ASCII STL is specifically not a v3 pattern. |
| `projects/kobalt_81798_socket_organizer` | regression example | Preserve selected notes/source references only to explain verification failures. It is not a Phase 1 generator. |

New `examples/specs/` files for bushing, round adapter, and flange plate should
be purpose-built, bounded, non-private specifications rather than renamed
legacy manifests.

## Legacy Project Inventory

| Project/path | Inventory finding | Classification |
| --- | --- | --- |
| `projects/_template` | Empty legacy four-folder scaffold | archive |
| `projects/ac_flange_plate_adapter` | Inferred/reference-driven adapter | manual migration candidate |
| `projects/agent_smoke_test_hex_bit_holder` | Small smoke model outside v3 families | archive |
| `projects/battery_strap_holder` | Same target as hyphenated folder; reports physical fit unverified | investigate/manual |
| `projects/battery-strap-holder` | Same target; different dimensions; manifest says verified before required fit test | investigate/manual |
| `projects/cat_ct660_fog_light_housing` | Photo-derived, approximate, and includes broad PASS language | investigate/manual |
| `projects/example_bracket` | Second bracket example with generated outputs | archive |
| `projects/hisense_ap1219cr1w_5in_coupling` | Potential round-adapter case with unresolved lock interface | manual |
| `projects/hisense_k1983844_dummy_coupling` | Potential round-adapter case using local references | manual/investigate |
| `projects/international_workstar_fog_light_housing` | Photo-derived and shares duplicated CAT reference images | investigate |
| `projects/kobalt_81798_socket_organizer` | 107 files, bespoke tools, 54 STL, 12 PNG, 2 3MF | regression/archive |
| `projects/mastercraft_prostar_190_mini` | Product miniature outside supported functional families | archive |
| `projects/peg_hook_6p8mm_fit_petg` | Python edit workflow, imported analysis SCAD, STL/3MF outputs | investigate/manual |
| `projects/perko_1247_high_torque_deck_plate_key` | Protected fit and torque remain explicitly unverified | manual |
| `projects/shoebox_corner_waterfall` | Multiple speculative source/export variants outside v3 families | archive/manual |
| `projects/simple_wall_bracket_example` | Existing main example; legacy generated deliverables | archive as CI history |
| `projects/softball_A_chain_pendant` | Decorative multicolor/export-presets workflow | archive/out of scope |
| `projects/thumb_guard_youth` | Wearable/safety-sensitive part with no v3 family mapping | investigate/archive |
| `projects/vevor_65pc_half_drive_packout_4drawer_organizer` | Large organizer with multiple STL/3MF outputs | archive/regression |
| `projects/vevor_packout_single_drawer_organizer` | Gitlink to a separate repository at `5cd444d...` | investigate separately; do not import |
| `projects/washer_inner_latch_w11457841` | Noncanonical version subtree with source photos and broad pass statuses | investigate/manual |
| `metric_to_standard_chart_output/` | Root-level source mixed with very large generated STL/PNG/log files | remove from active workflow |

## Duplicate and Noncanonical Layouts

### Duplicate projects

- `battery_strap_holder/` and `battery-strap-holder/` describe the same part but
  use different measurements and status language (`74.0` versus `74.1` mm is
  one visible conflict). Do not merge parameters automatically.
- CAT image blobs are duplicated under `references/cat660/` and
  `references/measured/cat_ct660_fog_light_housing/`; two are also reused under
  `references/measured/international_workstar_fog_light_housing/`.

### Noncanonical layouts

- `washer_inner_latch_w11457841/v01/{scad,stl,renders,references}` nests the
  version above responsibility folders.
- `peg_hook_6p8mm_fit_petg` lacks a canonical editable SCAD source and mixes a
  Python editor with imported analysis geometry.
- Kobalt includes project-local build and validation scripts that duplicate
  repository workflow responsibilities.
- `metric_to_standard_chart_output/` is a project at repository root with
  source and generated output mixed together.
- The VEVOR single-drawer project is a submodule, not an ordinary project tree.

Phase 1 does not normalize these layouts. Any later migration creates a new
versioned JSON specification and leaves the legacy path as history.

## Restricted or Private Reference Inventory

Potentially private or redistribution-restricted material exists at:

- `references/measured/**`
- `references/cat660/**`
- `projects/washer_inner_latch_w11457841/v01/references/source_images/**`
- Hisense `IMG_*.jpg` reference files
- any locally held purchased/free organizer meshes used by Kobalt analysis

Filenames and blob identity were audited, not image contents. None of this
material is copied into v3. `references/paid/.gitkeep` is harmless, but the
presence of a paid folder does not authorize reference redistribution.

## Generated Output Inventory

PR #1 contains approximately 335 MB of STL data plus PNG and 3MF collections.
Most changed STLs are text/ASCII. These artifacts remain historical and are
excluded from the rebuild branch's active workflow.

| Artifact | Treatment |
| --- | --- |
| STL | Generate locally under `workspace/`; do not commit routinely |
| PNG | Optional future review output under `workspace/`; not Phase 1 proof |
| 3MF | Not a Phase 1 requirement; ignore routine local files |
| temporary mesh/log | Generate only under ignored workspace/temp paths |
| small fixture | Track only when deliberately authored, documented, and not ASCII STL |

## PASS Claims Without Physical-Fit Evidence

| Evidence | Problem |
| --- | --- |
| Kobalt v01 manifest: `verification_status: PASS split-module local verification` | Pocket dimensions were estimated; no physical fit result. |
| Kobalt v02 review report | Compilation, exports, label checks, and fit-plate export pass; coupon export is not coupon success. |
| Kobalt v04 review report: `Status: PASS` | The report covers counts, watertightness, and build bounds; the separate notes still warn against assuming first-print fit. |
| `battery-strap-holder` manifest: `verification_status: verified` | Its next action is to print the fit-test and confirm screw alignment. |
| CAT CT660 v03 notes: overall `PASS` | The judgment is photo/silhouette based and includes approximate dimensions. |
| Washer latch manifest/design notes: corrective `pass` statuses | No installed physical-fit evidence is recorded. |

Projects that clearly state `physical fit NOT VERIFIED`, such as the Perko key,
still need migration because their generic export `PASS` vocabulary does not
map to the v3 state machine.

## Kobalt Regression Lessons

The Kobalt organizer is the primary negative regression example:

1. **Every physical item needs its own authoritative interface dimension.**
   V03 states that all pocket diameters are estimated. V04 replaces many values
   with circular candidates extracted from other organizer STLs, not caliper
   measurements of the actual Kobalt sockets.
2. **A populated field is not a valid measurement.** The inventory contains an
   item-level `pocket_diameter`, but provenance and confidence determine whether
   the value may release a full part.
3. **Labels must carry the real readable value.** Values such as `5/8` are
   transformed to `5_8`. The validator checks uppercase-safe characters,
   minimum size, and collision only; it does not prove semantic equality or
   human readability.
4. **Modular sections require functional interlocks.** V04 adds named seam
   geometry, but its validator checks source tokens and mesh bounds, not whether
   printed modules mate at the stated clearance.
5. **Coupon presence is not coupon success.** V04 contains fit-test modules, but
   its required STL lists omit them and no v04 coupon-pass record exists.
6. **Mesh success is computational evidence only.** Watertightness, build-volume
   compliance, counts, and aligned labels do not prove socket retention,
   clearance, seam engagement, or physical fit.

V3 tests should preserve these lessons as assertions around Measurement
Contracts, label/spec traceability, fit-coupon states, interlock parameters, and
truthful reporting—not by importing the Kobalt output collection.

## Intentionally Not Migrated in Phase 1

- React dashboard and local dashboard data
- customer, quote, delivery, payment, or portal concepts
- generated output collections and previews
- photo-to-3D or AI-generated mesh workflows
- paid, private, or ambiguous reference media
- project-specific build/validation script forks
- legacy PASS/VERIFIED status strings
- wholesale project-folder normalization
