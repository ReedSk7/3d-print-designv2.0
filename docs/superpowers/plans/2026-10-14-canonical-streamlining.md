# Print Workshop consolidation and streamlined operation

Approved scope: implement the October 14 audit recommendations while preserving the existing repository, integration ancestry, project identifiers, original models, measurements, artifacts and owner data. Reed describes the desired design/change; Codex selects tools, implements and verifies. Blender is optional and selected by Codex only when useful; it is not an adoption gate. OpenSCAD remains authoritative. No printer actions or invented physical evidence.

Base: ee7c481986aca888053e653de1b95859259d0610, descendant branch feature/print-workshop-canonical-20261014. Main remains 65b8ae6. PRs 2–4 are ancestors; PR1 remains unique salvage history. The connected Windows PC is offline; owner-local backup/launch/slicing acceptance cannot be claimed or bypassed.

## Task 1: Immutable saves and resilient catalog

Own core/workshop/service.py, related new helper modules, app/src/App.jsx and relevant service/catalog tests. Reproduce interrupted context write, corrupt spec poisoning the catalog, and differing same-name legacy sources. Stage and exclusively publish a complete version using existing publication safeguards; never overwrite a destination or original damaged record. Return individual invalid records as actionable diagnostics, retaining unaffected records and sources. Deduplicate only proven identical source sets; expose differing locations without changing stored project IDs. UI must distinguish records by location and display errors without enabling invalid operations. Regression tests must fail first and then pass; run existing workshop and evidence tests. Preserve source paths and generated artifacts.

## Task 2: Reproducible setup and truthful readiness

Own scripts/setup.ps1, scripts/start_workshop.ps1, Open Print Workshop.cmd, core/workshop/readiness.py, new app build validation module/script, app/package.json and lock if needed, setup/readiness tests. Provide one explicit setup command that installs exact project Python dependencies and builds the locked app. Normal launcher installs nothing. Validate build freshness/completeness against current inputs/assets rather than index.html existence. Forward launcher arguments and produce useful missing-pwsh diagnostics. Keep Windows process containment; mark unsupported runtime accurately. Reproduce stale/incomplete build first. Avoid new frameworks, global configuration, auto-installing CAD tools or touching owner data.

## Task 3: Preservation policy and actual platform CI

Own scripts/check_output_policy.py, docs/legacy-artifact-preservation.json, tests/unit/test_legacy_output_preservation.py, workflow, platform test markers and self-contained browser smoke tests. Preserve all six historical files exactly; validate baseline/index Git blobs and exact LF/CRLF representations without broad normalizing exemptions. Include regression cases for stale baseline, altered index/files and shallow history. Fetch full history in CI. Route Windows worker/generation/cancellation tests to actual Windows with OpenSCAD; keep portable generator validation on Linux under Xvfb for real preview tests. Build UI from lock and run a bounded synthetic browser smoke. Do not silently skip the only coverage for a required behavior.

## Task 4: Working agreement, current onboarding, verification and publication

Root owns AGENTS.md, README.md, docs/QUICK_START.md, docs/PRINT_WORKSHOP.md and current acceptance/status documentation. Retain October 4 historical evidence. Document designer/agent workflow, current candidate branch, one-time setup and normal launch, preservation and exact validation limits. Do not alter existing repo-local skill files unnecessarily. Run combined tests/build/policy, inspect actual preview images when generated, compare all original project blobs and unchanged generator foundation, and obtain an independent review. Address material findings with regression evidence. Publish one draft consolidation PR to main from the tested descendant. Do not merge/retire worktrees while current owner-PC preservation and adoption checks remain unavailable.

## Interfaces and review focus

- Catalog remains a JSON list. Invalid entries need explicit kind/status; UI must render safely and not pass them as saved specifications.
- App build contract from task 2 is consumed by task 3 CI; coordinate build command/manifest paths.
- Worker Windows-only marker must leave portable direct-service tests running in Linux.
- Audit original ee7c481 project blobs after every combined edit. Tests use only temporary small synthetic fixtures; evidence records from tests never imply actual owner testing.
- Review concurrency, no-overwrite semantics, symlink/path handling, catalog identity collisions, malicious/stale build manifests, exact artifact allowlists and CI command correctness.

## Execution record

- Initial live fetch unchanged; audit checkout clean; isolated linked worktree created. Known prior baseline: unit 145 passed/1 Windows skip; selected OpenSCAD integration 34 passed; two Linux HTTP tests fail on Windows containment; policy fails on two LF STLs. These are authorized repair targets.
- Windows device Reeds-Laptop reported offline. No owner checkout operation was attempted.
- Implemented immutable specification/context and derived coupon/full-part publication, per-record catalog recovery, location-aware legacy listing, build freshness, explicit one-command setup, argument forwarding, exact historical blob preservation, platform-correct CI, and the working agreement.
- New regressions were observed failing before their fixes. Combined final local unit suite: 219 passed, 1 Windows skip. Full portable integration suite under authenticated Xvfb/actual OpenSCAD: 51 passed, 3 Windows worker deselections. Original 26 project files remain byte-identical and the six historical artifacts pass preservation policy. The protected generator/schema/model/evidence/workflow foundation has no diff.
- Inspected actual synthetic bushing isometric, front and top OpenSCAD previews. No actual owner design, Blender execution, printer slicing, printing or physical fit was claimed.
- Local browser execution is blocked by the runtime's Unix-socket restriction; hosted browser CI is required. No sandbox settings or global tools were changed.
- Independent final review found no material issues; 77 targeted catalog/readiness/preservation tests independently passed. Publication is one descendant draft PR; no merge, branch retirement, archive removal or owner-PC modification.
