# Print Workshop — build and consolidation specification

Status: design approved in principle; this document is for review before implementation.
Date: 2026-10-04

## Outcome

One familiar project folder, one existing GitHub repository, and one Windows launcher opening a local Print Workshop app. Reed can find old designs, record measurements, revise parametric parts, review actual CAD artifacts, test fit coupons, and hand a reviewed STL to Bambu Studio for final P2S slicing.

Canonical folder: the local repository root
Repository: https://github.com/ReedSk7/3d-print-designv2.0

OpenSCAD stays the editable geometry authority. The app reuses the Python backend from the PR #4 foundation and selectively reuses the older React dashboard. It does not introduce another CAD engine, hosted service, login, or automatic printer operation.

## Observed starting state

- Canonical checkout: main at 47ea856, one local commit beyond cached origin/main (65b8ae6). The unique commit adds the hex-bit-holder smoke model and artifacts.
- Canonical untracked content: app build/dependency/log/screenshot remnants; .codex-remote-attachments with three images; projects/vevor_packout_single_drawer_organizer with SCAD, fit-strip source, preview and STL files.
- Modernization folder: 3d-print-astra-upgrade is a linked worktree, not an independent repository. Its .git points into the canonical repository. HEAD e414b8b includes PR #3 and PR #2.
- Seven modernization edits: AGENTS.md; .codex/config.toml; core/environment.py; docs/QUICK_START.md; docs/UPGRADE_2026-09-30.md; .agents/skills/openscad-3d-print-agent/references/setup.md; tests/unit/test_environment.py. These remove mandatory model/effort selection and preserve client choice.
- Modernization ignored local content includes workspace/shocker_stopper_estimate/ and owner-validation/local/shocker_stopper/. Treat their contents as owner data; inventory without publishing.
- Clean linked worktrees exist for PR #2 and PR #3 under .codex/worktrees.
- Older agent/consolidate-3d-workspace branch contains dashboard source; canonical app/ currently has only generated remnants. Its backend uses legacy scripts/statuses and must not become the new authority.
- PR #2, #3 and #4 are open drafts and unmerged. Recheck live refs before implementation; do not assume cached origin refs are current.
- Read-only doctor passed using the modernization .venv: Python 3.12.14, required pinned dependencies, Git 2.52.0 and OpenSCAD 2021.01. Bambu Studio is installed, but P2S profiles, packaging and exported-project reopening are unverified. No tests, renders, slices or physical fit tests were performed by this discovery task.

## Preservation and consolidation

1. Reinspect all checkout statuses, worktree relationships, refs, overrides and owner-data locations. Record the exact state and tool versions in a local migration inventory.
2. Before modifying any existing checkout, create a dated recoverable archive outside the active project folder. Preserve Git history/refs in a verified Git bundle, tracked-file working copies and binary-capable patches, all untracked projects/attachments/app remnants, and ignored workspace/owner-validation data. Include needed archive files explicitly; never mistake git status or a Git bundle for a backup of ignored files. Credentials, global authentication and unrelated user folders are outside scope.
3. Hash preserved files and verify archive copies. Demonstrate Git-bundle verification and restoration of representative source, binary artifact, edit and owner-data files into a temporary location. Record exclusions such as reproducible dependency caches. Keep this archive local and report its exact path.
4. Use an authorized isolated implementation checkout based on the verified PR #4 tree. Reapply the seven modernization edits after diff review; preserve Reed's model/effort choice. Do not modify the original dirty worktree during development.
5. Preserve 47ea856 and its artifacts in history/archive; selectively retain its design in the project library. Do not blanket-import generated outputs into the modern tracked tree.
6. Salvage dashboard layout/components from the old consolidation branch individually. Do not merge PR #1 wholesale or import its reference collections and large generated-output tree.
7. Preserve legacy projects as local, explicitly labelled legacy records. Keep original bytes/paths recoverable and record provenance. The Vevor project appeared as a gitlink on the older branch; verify its independent provenance/licensing and preserve its actual local files without pretending it is a modern generator project.
8. After app and migration acceptance, prepare a canonical-folder transition preserving its Git directory, unique work and recoverable archive. Any checkout change, merge or publication must follow then-current user authorization; no reset, force push or wholesale overwrite.
9. Retire obsolete worktrees only after verified migration and explicit cleanup approval. Use Git-aware worktree operations; never delete the canonical .git or a linked worktree by guessing folder relationships. Keep archives and clearly identify the canonical launcher. No cleanup is part of spec-writing.

## Application architecture

Use a small React/Vite interface, a local-only bridge, and the existing Python domain/workflow modules. A Windows PowerShell launcher selects the project Python environment, starts the local service, checks readiness, and opens the default browser. The production launcher serves built assets locally; Vite remains a development tool. Provide a Stop command and useful startup diagnostics without requiring Reed to manage two terminals.

Keep the Python backend authoritative for validation, generator lookup, source/STL bindings, artifact publication, workflow transitions and evidence. The bridge invokes fixed adapters or a narrow worker protocol using argument arrays; it must not duplicate geometry rules in JavaScript or accept arbitrary shell commands. Reuse installed dependencies where possible; select and pin any necessary UI/bridge dependencies during implementation review.

The app binds only to 127.0.0.1. No cloud synchronization, analytics, external model API, printer discovery, printer connection, firmware updates, job sending or print-start controls. Codex remains Reed's separate design collaborator; the app can prepare a copyable context summary and open the project/source, without claiming an embedded AI integration.

## Screens and workflow

### Project library

Show project name, source location, latest version, exact verification state, unresolved measurements and a thumbnail when available. Distinguish modern generator projects from legacy OpenSCAD projects. Legacy records remain fit unverified unless valid evidence establishes otherwise. Search/filter, open source/folder and show provenance. Do not infer physical success from old PASS text, file presence or an exported coupon.

### Intake and measurements

Record exact target, reused surrounding parts, exclusions, intent, references, units and printer/material/nozzle identity. Show each critical value with source, authority, confidence, tolerance and protection status. Separate measured, trusted-reference and estimated values; never silently promote estimates. Required replacement interfaces lacking authoritative data block full replacement generation and produce a measurement checklist.

Initial automated generation supports bushing, round_adapter and flange_plate using existing registered versions. Existing arbitrary SCAD designs remain accessible through Codex/OpenSCAD with versioned source and review records. Additional families or arbitrary-SCAD automated fit validation require a separate scoped generator/feature definition; the UI must state this limitation clearly.

### Design and revisions

Display supported parameters with units and constraints. Save a new immutable project version instead of overwriting prior source/artifacts. Compare protected nominal dimensions and feature relationships with the prior version. Record proposed protected-interface changes explicitly; require deliberate owner acceptance before that revision proceeds. Keep nominal geometry distinct from printer/material-specific clearance corrections. Changed configuration invalidates reliance on prior fit evidence unless the existing backend proves the exact linkage is valid.

### Generate and review

Call existing specification validation, deterministic SCAD generation, mandatory OpenSCAD compilation, mesh QA and manifest checks. Produce source, STL, actual orthographic/isometric/detail previews and a version-bound review report. Include per-feature checks for supported holes, spacing and mating features rather than treating overall bounds as fit proof. Feature algorithms belong in Python and are generator-aware; unsupported checks are reported as pending/unavailable.

A report includes exact reached workflow state, source/spec/profile/artifact hashes, computational results, measured versus estimated inputs, protected-interface changes, unresolved assumptions, failed checks and pending visual/physical review. Opening actual images is required before recording a visual review. Integrity checks alone do not establish visual judgment.

### Fit coupons and evidence

If nominal mating geometry is authoritative but clearance uncertain, use the existing coupon workflow. Candidate offsets are deliberate owner inputs, not claimed calibrated defaults. Record real printed results against the exact coupon/artifact/configuration hashes. Do not invent printer, nozzle, profile, material or print settings. Full-part generation relying on a coupon starts a new version linked to valid passed evidence. Full-part physical confirmation requires its own actual evidence.

### Export and Bambu handoff

Prepare the existing verified source/STL handoff and checklist. Reed opens/imports it in Bambu Studio and selects the actual P2S printer, installed nozzle, material, plate and process. Review scale, component alignment, orientation, walls, supports and final slice manually. Do not substitute another printer profile. No automatic 3MF/Bambu-project claim until a compatible real profile workflow and reopened export are tested. App handoff does not mean sliced, printed or physically fit-confirmed.

## Local data and bridge safeguards

- Modern generated artifacts stay under ignored workspace/<project_id>/<version>/; owner-filled specifications/evidence remain ignored and local. Local app catalog/config lives in a clearly ignored local directory. Tracked files contain code, schemas, documentation and deliberate synthetic fixtures.
- Use atomic writes and existing exclusive no-overwrite publication. Preserve immutable manifests/evidence and record corrections as new records/versions.
- Restrict bridge actions to explicit operations and canonical allowed roots; resolve paths and reject traversal, symlink/junction escapes and arbitrary executable/path requests. Imported references use an explicit reviewed import flow.
- Validate requests on the server and again through existing backend contracts. Never trust UI checkboxes for verification.
- Enforce localhost Host/Origin checks and a per-launch request token for mutations; no wildcard CORS. Serve only allowlisted artifact paths. Prevent other web pages from issuing local file/workflow mutations.
- Bound subprocess runtime/output, queue expensive generation jobs and prevent concurrent publication to the same version. Capture job IDs, progress, exit status and sanitized errors. Cancellation stops pending/active work safely and cannot publish partial success.
- Render owner notes as text or sanitized content; avoid logging private reference contents, environment secrets or credentials. No arbitrary shell endpoint. Browser actions cannot start printing.

## Errors and recovery

Startup distinguishes missing Python environment, required OpenSCAD, dependency mismatch, occupied port and optional Bambu availability. Provide exact corrective action without installing automatically or changing global settings. Generation failures retain useful local diagnostics, identify the failed stage, and never advance status. Stale/tampered artifacts block review/export. Missing previews or physical evidence stay pending. Restart can inspect unfinished jobs and distinguish failed/interrupted work from published versions.

## Intended affected areas

- New app/ UI, narrow local bridge and local data policy, selectively salvaging useful old screens.
- New Windows launcher and maintenance/stop helpers under scripts/.
- Existing core/validation for supported feature and revision checks; existing workflow/review integration where necessary.
- Existing repo-local openscad skill plus focused workshop instructions; root AGENTS.md and README updated to explicitly permit the approved app scope while preserving geometry/evidence/privacy rules.
- New Print Workshop/consolidation documentation, migration inventory tooling and meaningful app/backend integration tests.
- No blanket rewrite of generator 1.0.0/1.1.0 contracts, global Codex settings, owner projects or slicer presets.

## Testing and acceptance

Before changes, run the existing backend suite in the isolated environment and record actual results. Then test:

- preservation hashes, bundle verification and representative restoration; inventory accounts for local-only commits, seven edits, untracked and ignored owner content;
- backend regression and all three supported generator flows;
- unit conversion, missing/estimated protected values, invalid geometry and protected-interface revision handling;
- synthetic meshes preserving outer bounds while changing hole diameter, spacing or mating geometry; feature checks must detect these differences;
- tampered source/STL/profile/evidence, stale previews and no-overwrite publication;
- coupon creation, genuine-result recording rules, linked full-part generation and conservative reporting, using synthetic fixtures without fabricated physical results;
- UI build, library/intake persistence, error/progress/cancellation behavior, path restrictions, localhost mutation protection and concurrency;
- real OpenSCAD exports/previews and actual image inspection; optional Bambu handoff reported separately;
- one-click Windows startup/stop and browser workflow from intake to computationally reviewed export;
- migration policy audit: no private/restricted references, owner data or routine generated artifacts included in code publication.

Accept when Reed can launch one app from the canonical workspace, find preserved legacy designs, complete a supported measured workflow, inspect exact version artifacts and pending checks, generate a coupon, and prepare a manual Bambu handoff. No output is physically verified without actual valid physical-fit evidence. Cleanup acceptance additionally requires verified backups, complete migration inventory, successful canonical launch and explicit approval to retire the old worktrees.

## Rollback and implementation boundary

Before canonical transition, originals remain untouched and implementation can be abandoned without affecting them. After transition, retain the pre-transition refs, file snapshots and manifest so the earlier checkout and owner data can be restored deliberately. Never use a destructive reset as an automatic rollback. Stop if preservation verification fails, provenance conflicts remain, paths resolve outside authorized roots, or protected measurements are missing.

This specification authorizes no implementation, dependency installation, checkout changes, moves/deletions, commits, merges or publication. The next step is review of this written spec, then explicit implementation authorization. No unresolved product decision is required to review it; exact archive path and canonical transition mechanics will be made concrete from the refreshed inventory before any migration action.

## Optional Blender integration (approved addition)

Target Blender 5.2.2 LTS initially, verifying the installed executable and version. Preserve OpenSCAD as the editable authority for supported parametric mechanical parts. First deliver version-bound STL inspection with verified scale; add automated inspection renders afterward. Keep original artifacts immutable and generated Blender scenes/previews local. Blender must remain optional, with existing OpenSCAD previews available. Do not add automatic mesh repair, online asset downloads, or printer controls. Any geometry-changing Blender workflow requires separate scope and renewed validation.

Missing or mismatched Blender must not block the main app or trigger installation/downgrade. Verify the actual executable with a bounded version probe; report exact version and compatibility. Inspect immutable manifest-bound copies with millimeter scale and preserved component alignment, and record imported bounds against the original mesh. A Blender scene is an inspection derivative, never parametric design authority or physical-fit evidence.
