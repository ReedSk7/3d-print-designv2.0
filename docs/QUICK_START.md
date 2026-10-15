# Current workspace quick start

## Daily canonical workspace

Use `C:\Users\reeds\Documents\Codex\3d-print-designV2.0` for future design work.
After PR #5's normal merge, `main` contains the original project history, PRs
#2–#4 and the reconciled local work. Do not merge that older stack separately.
Acceptance worktrees and backups remain preserved; they are not additional
master workspaces. See [Windows adoption](WINDOWS_ADOPTION_2026-10-14.md) and
the owner-local adoption record for exact final refs, backup paths and pending
manual Bambu acceptance.

Double-click `Open Print Workshop.cmd` in this folder. Before a later code
update, inspect and preserve any new work:

```powershell
git status --short --branch
git remote -v
git worktree list
git branch -vv
git log --all --not --remotes --oneline
git ls-files --others --exclude-standard
git ls-files --others --ignored --exclude-standard
# Confirm origin is ReedSk7/3d-print-designv2.0; keep private filenames local.
git fetch origin
```

Before changing the canonical checkout, verify recoverable backups of its
tracked edits, untracked/ignored owner files and linked worktrees. A Git bundle
alone excludes ignored data and submodule contents. Inspect any existing
acceptance worktree before creating another one. Test future updates in a
separate worktree so the working project remains intact. Select a unique branch
and path rather than reusing the preserved acceptance checkout, for example:

```powershell
git worktree add ..\print-workshop-next-acceptance -b local/print-workshop-next-acceptance origin/main
cd ..\print-workshop-next-acceptance
```

Ignored owner data is not copied to a new worktree. Keep it at its current
location; any necessary test copy must be explicit and hash-checked. Do not
stash, clean, reset, or replace local data automatically. After acceptance,
reconcile the existing canonical folder without changing its identifiers;
worktree retirement is a separate reviewed cleanup.

## Set up and check

Use Windows, PowerShell 7 (`pwsh`), installed Python 3.12 or 3.13, a Node version
supported by the app lockfile, npm, Git and OpenSCAD. The setup command prepares
only this checkout's Python dependencies and frontend. It does not install CAD
tools or configure the printer. No activation or execution-policy bypass is needed.

```powershell
pwsh -NoProfile -File .\scripts\setup.ps1 -PythonVersion 3.12
& .\.venv\Scripts\python.exe scripts\check_environment.py
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe scripts\check_output_policy.py
```

If PowerShell policy blocks the script, follow your machine's normal policy or
run the project dependency and build steps directly; do not weaken policy:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip --isolated --require-virtualenv install -r requirements-lock.txt
npm --prefix app ci
npm --prefix app run build
```

For daily use, double-click `Open Print Workshop.cmd`. The launcher installs
nothing and checks the exact current app source/build hashes before starting.
After frontend changes, rebuild with `npm --prefix app run build`. Use
`Open Print Workshop.cmd -Port 8766` for a different free port. Stop the workshop
through its app after active jobs finish. A different port is a different
browser storage origin, so keep independently retained evidence hashes.

The browser worker requires Windows process containment. The Python generator
CLI remains portable; on headless Linux run preview/integration checks under
`xvfb-run -a` with OpenSCAD available.

Existing `.venv` is checked and reused by setup, never removed. For dependency
rollback preserve that directory first or use a new worktree. OpenSCAD, Bambu
Studio, Git and Codex are separate installations. The diagnostic installs nothing.
For a nonstandard compiler location, use the actual executable, for example:

```powershell
$env:OPENSCAD_PATH = 'C:\Program Files\OpenSCAD\openscad.com'
```

An invalid explicit path now fails; correct/unset it instead of relying on fallback.
For optional Bambu discovery, set `BAMBUSTUDIO_PATH` to its real CLI executable.

## Codex configuration

`.codex/config.toml` sets `workspace-write` and `on-request` approvals only.
It does not set or require a model or reasoning level. Choose those in the Codex
chat/session controls; existing user defaults apply when the client has no
explicit session choice. No global providers, auth or configuration are edited.

The environment doctor checks TOML and execution safeguards without requiring
Astra, High reasoning, or any alternative. Client support and account availability
determine which choices are offered. Automatic model selection is available only
if the client supports it; repository configuration cannot add it or switch the
model of a running chat.

After updating, confirm the desired model, reasoning and permissions in the
client's status/settings. Start a new trusted-project session or reload the IDE
if needed to reload project configuration. Written settings, client acceptance
and active session state are separate facts; the doctor verifies disk settings.

Official references: [models](https://learn.chatgpt.com/docs/models),
[configuration](https://learn.chatgpt.com/docs/config-file/config-reference).

## Normal work (after choosing a measured specification)

VS Code **Run Task → Workbench** provides the same commands with the local venv.
Replace the example paths below with the exact version you intend to work on.

```powershell
$py = '.\.venv\Scripts\python.exe'
& $py scripts\validate_spec.py --spec 'path\to\spec.json'
& $py scripts\generate_part.py --spec 'path\to\spec.json'
& $py scripts\verify_mesh.py --manifest 'workspace\project_id\v01\artifact-manifest.json'
& $py scripts\inspect_project_status.py --project-version-dir 'workspace\project_id\v01'
& $py scripts\export_preview.py --manifest 'workspace\project_id\v01\artifact-manifest.json'
& $py scripts\verify_preview.py --preview-manifest 'workspace\project_id\v01\previews\r01\preview-manifest.json'
& $py scripts\prepare_bambu_handoff.py --manifest 'workspace\project_id\v01\artifact-manifest.json'
```

Generation refuses an existing part version. Review/handoff outputs likewise use
new revisions (`--revision r02`) rather than overwriting earlier files. All these
outputs remain ignored. Absolute script/input paths work from another directory;
relative input paths resolve from your current directory.

Open the actual CAD images to review them. Optional detail view:
`--detail-camera "0,0,10,90,0,0,40"` (position/angles/distance in OpenSCAD's camera
format); choose numbers for the critical feature rather than treating these as a
universal camera. Headless Linux needs a display context, normally `xvfb-run -a`.
A preview manifest and automated PNG check never stand in for visual inspection.

Read the generated `bambu-handoff/r01/IMPORT_IN_BAMBU.md`. Confirm P2S/nozzle/
material/plate/process/AMS details, duplicate compatible real presets, import at
100% in millimeters, preserve alignment, save a new project and reopen it.
The handoff is STL plus source, not a generic 3MF and not a verified Bambu project.
Automated packaging is unavailable until real tooling/profiles and reopening can
be tested. Nothing here sends a print or establishes physical fit.
