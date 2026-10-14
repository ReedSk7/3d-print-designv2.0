# Canonical Print Workshop adoption

Updated 2026-10-14. This status supplements the dated October 4 acceptance and
transition documents; it does not replace their historical evidence.

## Intended daily workflow

Reed describes the desired part or change. Codex inspects the existing project,
reuses its dimensions and decisions, chooses the appropriate tool, creates an
explicit revision, performs computational checks, inspects actual previews and
prepares the manual Bambu Lab P2S handoff. Reed supplies physical measurements
or actual fit observations when they cannot be established from available
evidence. OpenSCAD remains authoritative. Codex chooses optional scripted
Blender inspection only when useful and verifies it before relying on it.
Blender is not a normal-operation or canonical-adoption gate.

## Source and preservation

- Repository remains `ReedSk7/3d-print-designv2.0`; keep the existing canonical
  Windows folder and all project identifiers.
- Candidate: `feature/print-workshop-canonical-20261014`, descended from
  `ee7c481986aca888053e653de1b95859259d0610`.
- Original integration parents remain `47ea856f60a010239352fe965ba19c050c991c4c`
  and `e414b8bddc18101b76006f8ba7cdcce2d5ecb55c`.
- PRs #2–#4 are already ancestors. Use one consolidation PR to main; do not
  merge that old stack separately or squash/rebase away integration ancestry.
- PR #1 is unique salvage history. Preserve its ref and separately inventory
  its sources, variants and VEVOR gitlink; no wholesale import or deletion.
- All 26 original tracked project files and the six historical STL/PNG
  artifacts must retain their Git blobs. Ignore new generated outputs.

## Repairs in this candidate

- Publish immutable saved specifications and their context together; isolate
  damaged catalog records so other projects remain accessible.
- Keep divergent same-name legacy sources visible with their original IDs and
  source locations. Collapse only proven identical editable source sets.
- Validate exact historical Git blobs and approved working-copy line endings;
  preserve the artifact files themselves and retrieve ancestry for CI.
- Provide explicit one-command project setup and a normal launcher that does
  not install dependencies. Detect stale/incomplete frontend builds.
- Run Windows worker checks on Windows, portable geometry checks on Linux with
  real OpenSCAD/display support, and a reproducible interface smoke check.
- Record the current source route and Reed/Codex responsibilities in root
  instructions and onboarding.

## Evidence and remaining gates

Local verification on 2026-10-14 (Python 3.12.14, locked dependencies,
OpenSCAD 2021.01):

- Unit suite: 221 passed; one Windows process-containment test skipped on Linux.
- Full portable integration suite: 51 passed; three Windows worker tests
  deliberately excluded here and required in Windows CI.
- Actual OpenSCAD previews generated under an authenticated Xvfb display.
  The synthetic bushing's isometric, front and top views were inspected.
- All 26 original tracked project files match the original project commit's
  bytes. No changes to generators, schemas, example specifications or the
  core model/evidence/workflow foundation. Preservation policy passes 6/6.
- Independent final review found no material issues and reran 77 targeted
  catalog, readiness and preservation tests successfully.
- Browser execution in this local environment is blocked by its Unix-socket
  restriction. The production UI smoke must pass on GitHub's browser runner;
  a local browser pass is not claimed.

The first hosted run passed both portable Python jobs and exposed two further
issues: multiple Windows npm installations were combined into one command
path, and the synthetic browser fixture held a buffered stdin lock during
shutdown. Both were repaired without relaxing the checks. The latter has a
regression that reproduced the actual abort before the fix; the Windows setup
is exercised with duplicate executable names on PATH. Use the latest PR check
results, not the initial failed run, for hosted acceptance.

Tests and browser fixtures use small synthetic designs only; synthetic
evidence does not establish real physical fit. Hosted Windows and browser
checks are recorded on the consolidation PR and must pass before adoption.

The connected device `Reeds-Laptop` reported offline during this task. No
operation on its canonical checkout, owner data or backups was attempted.
Current Windows acceptance remains pending even if hosted Windows CI passes.

Before promoting the candidate and updating the existing canonical folder:

1. Inspect current HEAD/branch, local-only commits, tracked edits, untracked and
   ignored files, linked worktrees and submodule state. Reuse/reverify existing
   preservation archives and back up subsequent changes. Verify hashes and
   representative restoration. A Git bundle excludes ignored files and does
   not embed submodule history.
2. Validate the candidate in an isolated Windows acceptance worktree. The
   one-time setup builds its own environment/assets; no ignored owner data is
   copied automatically. Any deliberate data copy needs a path/hash inventory.
3. Verify the real desktop launcher, port collision/duplicate launch behavior,
   fresh assets, save/reload/stop/restart, legacy source access, previews and
   immutable handoff. Exercise cancellation and interrupted-job/save recovery
   with synthetic fixtures. Preserve browser evidence anchors independently.
4. Import a synthetic handoff into the actual Bambu P2S setup at 100% in
   millimeters; check installed nozzle/material/plate/process and alignment,
   slice, save a separate project and reopen it. Do not change master profiles
   or start a print as a consolidation test.
5. If all source and adoption checks pass, merge the reviewed consolidation PR
   using a normal merge commit, then reconcile the existing canonical folder.
   Use a fast-forward-only update only when its actual state permits it.
   Preserve newer owner work; do not automatically reset, stash, clean or
   replace anything. Rebuild the app in the final canonical checkout.
6. Close/supersede #2–#4 only after adoption succeeds. Retain PR #1 and all
   preservation refs/archives. Retiring worktrees is a later explicit cleanup.

Actual Blender execution remains optional and unclaimed. Physical printing and
fit acceptance are separate from source adoption and computational validity.
Only actual recorded owner evidence can establish physical fit.

## Recovery

Until adoption, the current canonical checkout remains the fallback. Keep the
candidate independent. After adoption, preserve new owner data before any
reviewed revert or checkout change; never force-reset shared main or restore an
old archive over newer work. A malformed catalog entry must remain on disk for
inspection/recovery rather than being silently removed.
