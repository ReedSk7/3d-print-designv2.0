# Current workspace quick start

## Bring the upgrade home safely

This upgrade is stacked on PR #3 (which is stacked on PR #2). It does not change
main. A normal pull of main will not select it. Your laptop's ignored files and
unpushed work were unavailable during this remote task.

In the existing repository, inspect before switching anything:

```powershell
git status --short --branch
git remote -v
git worktree list
git branch -vv
git log --all --not --remotes --oneline
git ls-files --others --ignored --exclude-standard
# Confirm origin is ReedSk7/3d-print-designv2.0; keep private filenames local.
git fetch origin
git worktree add ..\3d-print-astra-upgrade -b local/astra-upgrade origin/upgrade/astra-workspace-20260930
cd ..\3d-print-astra-upgrade
```

This leaves the old worktree and local owner evidence untouched. If the local
branch/folder already exists, inspect it instead of overwriting it. Review newer
local commits before applying them. Ignored owner data is NOT copied to the new
worktree: keep its existing location and plan any selective migration separately.
Do not stash, clean, reset, merge old PRs, or replace local data automatically.

## Set up and check

Use an installed Python 3.12 or 3.13. The baseline was tested with 3.12.14;
CI checks both versions. No activation or execution-policy bypass is needed.

```powershell
.\scripts\setup.ps1 -PythonVersion 3.12
& .\.venv\Scripts\python.exe scripts\check_environment.py
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe scripts\check_output_policy.py
```

If PowerShell policy blocks the script, follow your machine's normal policy or
run its two dependency steps directly; do not weaken policy:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip --isolated --require-virtualenv install -r requirements-lock.txt
```

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
