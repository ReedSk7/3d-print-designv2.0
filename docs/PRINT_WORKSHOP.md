# Print Workshop

Installed in Reed's canonical `3d-print-designV2.0` folder. Open `Open Print Workshop.cmd` to launch with its project environment. The integration is committed on a local branch; the original Git metadata, projects, linked worktrees and backups are preserved.

Build the local interface with `cd app; npm ci; npm run build`. Start from the repository root:

```powershell
.\scripts\start_workshop.ps1
```

The launcher checks Python, pinned dependency versions/compatibility, OpenSCAD and built assets before opening the local browser app on 127.0.0.1:8765. Use Stop workshop after jobs finish. If the port is occupied, select another `-Port`. Startup logs live under ignored `owner-validation/local/workshop/`. There is no printer connection.

New designs start from clearly illustrative examples. Change the project name/ID, version, dimensions, actual printer/material/nozzle and authoritative measurements before using a replacement design. The full-specification editor exposes the existing Measurement Contract without inventing values. Saved versions are immutable; actions always use saved specifications. Protected dimension/pattern changes need explicit acceptance.

Design context records the exact target, reused surrounding parts, exclusions and references as local notes bound to the saved specification hash. Units are explicit; changing the unit selector changes interpretation of entered numbers, without silently converting them. Measurement records have their own units, source, authority, confidence and tolerance. Notes never establish measurements or fit.

Generate calls the existing deterministic Python/OpenSCAD pipeline. Inspect status rechecks bindings and reports conservative per-feature section probes. These probes are not complete surface checks or physical-fit confirmation. OpenSCAD previews are actual version-bound images; rendering does not mean anyone reviewed them. Prepare Bambu handoff produces local source/STL/checklist files for manual P2S slicing.

Round-adapter probes cover the resolved bore near both ends and through the taper, exposed outer-body sections, and enabled flange mounting holes. They account for cutting-cone extension and XYZ calibration. Bead/flange-obscured outer sections are explicitly unavailable, preventing an all-passed report. These checks apply to generator versions 1.0.0 and 1.1.0; no full-surface or physical-fit claim follows.

The library automatically displays the newest numerically ordered preview revision whose source/version and PNG hashes still verify. A damaged latest preview falls back to an earlier verified revision; changed generation suppresses its thumbnail. Redirected preview paths cannot attach another project's images to this record. Thumbnails are generated-image access, not visual acceptance.

Fit coupon specifications require owner-chosen offsets. Generate, manually print and evaluate them, then use the existing owner evidence workflow in docs/OWNER_FIT_VALIDATION.md. No example is physically confirmed by this app.

Recording an actual owner test retains its evidence SHA-256 in this browser and immediately verifies against that recording-time hash. Supply an independently retained hash in the inspection controls after changing browsers; file presence alone stays unanchored. Confirmation labels explicitly apply to the saved version. Inspecting another version, editing its identity or saving a revision clears that result.

Open verified previews reopens a saved preview revision and checks its version/image bindings. After looking at all four actual images, record reviewer, observations and remaining concerns; the separate immutable note keeps image hashes and does not rewrite the preview manifest or imply physical fit. Local job history survives reload, including interrupted jobs. A Windows job object terminates worker descendants when their bridge exits; an exclusive workspace lock prevents another bridge from running against the same workspace.

Optional Blender targets exactly 5.2.2. Windows desktop installations and registered Microsoft Store execution aliases are discovered locally; BLENDER_PATH can explicitly select an existing executable or alias. The actual running Blender version is checked before enabling inspection, rather than trusting a shortcut label or launcher output. Missing/mismatched Blender disables only that option.

The Blender action waits for the owned runtime to finish saving its scene and scale report, including when a Store launcher returns early. Failure, timeout and accepted cancellation do not become successful jobs; owned background processes are stopped. The adapter snapshots manifest-bound STL, converts millimeter numbers to meters once, checks finite bounds and original hashes, and saves an immutable local inspection derivative. Existing revisions are never overwritten. Visual review remains pending, and this does not establish physical fit. Automated Blender renders are a later checkpoint; OpenSCAD previews are available now. No repair, mesh edits, asset downloads or slicer/printer controls.

Local owner specs live under ignored owner-validation/local/workshop; generated artifacts under ignored workspace. Legacy projects remain separate source records and require Codex/OpenSCAD review. Do not blanket-import restricted references, old PASS labels or generated-output collections into modern source control.

Before cleanup, reverify preservation, migration inventory, startup and owner acceptance. Retire linked worktrees only with explicit cleanup approval and Git-aware operations. Never delete the canonical .git directory to remove apparent duplication.
