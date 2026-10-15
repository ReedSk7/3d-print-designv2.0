# Windows adoption acceptance - 2026-10-14

The October 14 laptop run supersedes the offline-laptop note in
`CANONICAL_ADOPTION.md`. The canonical folder remains
`C:\Users\reeds\Documents\Codex\3d-print-designV2.0`. Daily design work belongs
there; acceptance worktrees and preservation archives are retained as evidence,
not additional master workspaces.

## Source and preservation

The reviewed candidate `5d55d41` and the newer local work `197f258` were
reconciled with normal merge commit `d1aee333`. This retains the Microsoft Store
Blender runtime and cancellation fixes, both original integration parents, and
the PR #2-#4 ancestry. PR #5 must use a normal merge commit to main. PR #1 remains
preserved salvage history; do not merge it wholesale or delete its ref.

Before canonical adoption, independently verify the external file snapshot,
main-repository bundle, independent VEVOR bundle and representative restores.
Owner models, measurements, ignored data and the older worktrees remain local.
Detailed paths, hashes, final branch/commit and post-adoption preservation checks
are recorded in ignored `owner-validation/local/adoption-20261014/` and the
external preservation archive. A bundle alone is not an owner-data backup.

## Laptop evidence

- Fresh setup used the existing bundled Python 3.12.14 executable explicitly:
  the system `py` launcher has no registered 3.12 interpreter. The supported
  project environment, locked dependencies and `pip check` passed.
- Actual OpenSCAD: `C:\Program Files\OpenSCAD\openscad.com`, version 2021.01.
  Production app inputs and all four emitted asset files matched their hashes.
- The reconciled Python suite passed **292 tests**, with five symlink tests
  skipped because Windows symlink privileges are unavailable. Those cases are
  covered by Linux CI. Windows worker ownership/recovery tests ran locally.
- The production browser smoke passed catalog diagnostics, distinct legacy
  source access, immutable revision save, context reload and clean shutdown.
- A synthetic bushing was saved/generated through the actual desktop-launched
  app. Its state is `full_part_exported`; actual source/STL downloads matched
  local bytes. All four OpenSCAD views were opened and an immutable agent visual
  note was recorded. Cancellation, restart, retained context and unchanged v01
  bytes were checked; cancelled v02 published no artifact manifest.
- A separate checkout path containing spaces exercised fresh duplicate-PATH
  setup and the real `.cmd` wrapper with forwarded port/Python/no-browser
  arguments, duplicate launches and occupied ports.

Acceptance found two startup defects: an unbounded readiness request against a
silent occupied port, and an optional Blender probe delaying the core library.
The fixes bound readiness requests and load optional Blender independently.
Both reproduced their original failures, then passed focused regressions. The
launcher/readiness checks passed 33 tests (three symlink-privilege skips), and
the updated real-browser smoke passed delayed and failed optional discovery
without blocking the catalog, save/reload or job history. The build dependency
`source-map-js` was updated from 1.2.1 to 1.2.2; the locked install/build and npm
audit passed with zero findings.

## Bambu and physical work still pending

The owner explicitly allowed completing other adoption steps if reliable native
UI control is unavailable. Bambu Studio 02.08.02.61 was found, but native window
activation/capture failed after recovery. **No import, slice, test-project save
or reopen is claimed.** No master profiles or printer controls were changed.

Read the local `BAMBU_MANUAL_ACCEPTANCE_PENDING.md` for the exact synthetic STL,
its hash and the separate test-project path. Check the actual P2S nozzle,
material, plate and process; import in millimeters at 100%, confirm 30 x 30 x
25 mm with a 20 mm vertical bore and flat base, slice locally, save a new 3MF,
and reopen it. Saved software presets do not prove installed hardware/material.
Do not print or send a job as part of this check.

Optional Blender inspection is not an adoption gate. Earlier October 5 records
describe a historical Store-runtime execution; this run makes no new Blender
scene-inspection claim. Printing, owner visual review and physical fit remain
unconfirmed.

## Daily launch and future designs

Double-click `Open Print Workshop.cmd` in the canonical folder. For another
free port, run `& '.\Open Print Workshop.cmd' -Port 8766`. Stop through the app.
The normal launcher installs nothing. After code/dependency changes, use
`pwsh -NoProfile -File .\scripts\setup.ps1`; it reuses a valid project `.venv`.
For a fresh checkout on this laptop, supply the supported Python executable
with `-PythonExecutable` as described in `QUICK_START.md`.

Reed describes the part or requested change. Codex first reads existing designs,
dimensions and decisions, preserves originals, creates explicit revisions,
uses OpenSCAD as geometry authority, performs computational checks, inspects
actual previews and prepares the P2S handoff. Ask only for essential missing
measurements/decisions or actual test observations. Only valid actual evidence
can establish `physical_fit_confirmed`.
