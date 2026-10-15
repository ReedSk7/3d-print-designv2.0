# Print Workshop Implementation Plan

> For agentic workers: use superpowers:executing-plans inline, with a fresh final reviewer. Steps use checkbox syntax.

**Goal:** Deliver the approved local application in isolation and prepare a reversible canonical transition.
**Architecture:** React/Vite browser UI calls a localhost Python bridge. Existing workflow/evidence modules remain authoritative; optional Blender uses immutable manifest-bound snapshots.
**Tech Stack:** Existing Python 3.12 environment, stdlib HTTP server, React 19, Vite 6, OpenSCAD 2021.01; optional Blender target 5.2.2.
**Spec:** ../../PRINT_WORKSHOP_SPEC.md

## Global Constraints
- One existing canonical repository; original folders remain untouched until migration acceptance.
- Preserve local-only commit, seven edits, untracked/ignored owner content and restricted references locally.
- No public pushes, merges, worktree retirement, printer controls, asset downloads or automatic mesh repair.
- OpenSCAD remains authority; Blender absent/mismatched never blocks the app.
- Only actual immutable evidence establishes physical fit.

## Review Focus
- Paths escaping allowed roots through junctions or symlinks must fail.
- Other browser origins must not mutate local data.
- Concurrent jobs and repeated version publication must not overwrite artifacts.
- Old PASS labels and example dimensions must not become physical-fit claims.
- Optional Blender mismatch must fail only Blender inspection.

### Task 1: Preserve and establish isolated baseline
Files: local preservation inventory/bundle outside implementation; docs/PRINT_WORKSHOP_SPEC.md.
Interface: verified backup inventory and independent feature checkout.
- [ ] Verify bundle and copied source/artifact/edit/owner hashes, representative restore.
- [ ] Reapply seven edits in isolated feature checkout; run existing suite with task-local temp root.
- [ ] Record isolation/archive status and any unavailable file.

### Task 2: Workshop service and request boundary
Files: core/workshop/service.py, core/workshop/server.py, tests/unit/test_workshop.py.
Interfaces: Workshop(root).catalog(), save_spec(document), action(action,payload); HTTP token/Host/Origin guards.
- [ ] Write tests rejecting traversal, unauthorized origin/token, duplicate spec version and protected-interface change without acceptance; observe RED.
- [ ] Implement ignored local catalog/spec storage, fixed backend actions, conservative reports and serialized jobs; observe GREEN.
- [ ] Run backend regression suite and localhost API tests.

### Task 3: Optional Blender inspection
Files: core/workshop/blender.py, scripts/blender_inspect.py, tests/unit/test_blender_inspection.py.
Interfaces: probe_blender(), inspect_blender(manifest, revision); optional compatibility status and immutable derivative bundle.
- [ ] Write absent/mismatch/tampered-source/no-overwrite/scale tests; observe RED.
- [ ] Implement bounded executable probe and manifest-bound STL inspection scene with millimeter units, measured bounds and no repair; observe GREEN.
- [ ] Real installed Blender test only if target executable exists; otherwise report unavailable. OpenSCAD previews remain functional.

### Task 4: Local app and launcher
Files: app/package.json, app/src/App.jsx, app/src/styles.css, scripts/start_workshop.ps1, scripts/serve_workshop.py.
Interfaces: localhost catalog/spec/actions endpoints, guarded artifact viewer.
- [ ] Test API contract required by UI before bridge behavior; observe RED/GREEN.
- [ ] Build project library, editable dimensional intake, revision protection, generation/report/previews, coupon input/evidence handoff, optional Blender and manual Bambu controls.
- [ ] Use a quiet workshop palette: paper #eef2f5, steel #314859, blue #146ab2, warning #8a5300, white #ffffff; Segoe UI body and numeric tables; left-aligned library/workbench split.
- [ ] Launcher chooses project Python or explicit interpreter, starts readiness-checked localhost server and opens browser; stop through authenticated endpoint.
- [ ] Build and test actual browser intake/generate/preview/error workflow and inspect screenshot.

### Task 5: Feature review, documentation and final review
Files: core/workshop/features.py, tests/integration/test_workshop_flow.py, docs/PRINT_WORKSHOP.md, root AGENTS.md/README.md.
Interfaces: per-feature report bound to supported generator/source/STL; legacy library remains separate.
- [ ] Write synthetic same-bounds/wrong-hole checks before implementing feature checker; observe RED/GREEN.
- [ ] Exercise actual exports, previews, coupon specification and manual handoff; run suite/build/output-policy audit.
- [ ] Fresh independent review; reproduce and fix important findings with RED/GREEN tests.
- [ ] Report exact acceptance gaps and canonical transition still pending. No deletion/publication.

## Ledger rulings
- User explicitly said then begin: execute without repeating design approval.
- Use independent local clone in authorized task root rather than linked worktree: original Git metadata is outside writable roots; prevents shared mutation.
- Native shell skill helpers are adapted to a plain progress ledger on Windows; preserve ledger and artifacts rather than delete them.
- No commits/publication until complete reviewable checkpoint; original instructions prohibit publication and dirty work must remain visible.
