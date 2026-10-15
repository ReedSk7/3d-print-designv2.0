# Pull Request Checklist

## Task mode

Required. State one of:

- `original_product_design`
- `reference_based_reconstruction`
- `mesh_cleanup_and_remodel`
- `workshop_maintenance` (setup, reliability, CI or documentation; no owner part)

## Project stem

Required for a design change. For workshop maintenance, state `not applicable`
and confirm that existing project identifiers and model files are preserved.

## Version

For a design change, record the explicit project version. For workshop
maintenance, record the starting commit and proposed branch instead.

## Files created

List changed source responsibilities. Generated owner data, evidence, previews
and routine print artifacts remain local and ignored.

## Previews included

For a design change, identify the version-bound preview bundle and actual
visual review. For workshop maintenance, state which synthetic UI/CAD checks
ran; do not imply a new owner model or physical test.

## STL export status

State the exact computational state reached, or `not applicable` for a change
that exports no model. Record actual failures and skipped/unavailable checks.

## Low-confidence zones

Required. Record any inferred or weakly verified geometry.

## Protected interfaces changed? (yes/no)

Required. If yes, explain why and what reference justified the change.

## Validation and adoption

Record exact test/build/preservation results, remaining Windows checks, and
whether actual Bambu slicing/reopen or physical testing occurred. Blender is
optional. For consolidation, preserve ancestry with a merge commit and keep
owner-PC acceptance separate from hosted CI. Do not retire old worktrees here.
