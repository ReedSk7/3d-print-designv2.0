# Environment and maintenance

Inspect root, branch, status, worktrees, remote refs, unpushed commits and ignored
owner-data locations without printing private contents. Preserve local work; use
a new branch/worktree. Read `docs/QUICK_START.md` and root instructions.

Run `python scripts/check_environment.py` from the project virtual environment.
It is read-only. Missing OpenSCAD blocks generation/integration; missing Bambu or
headless display is reported separately. Correct explicit tool overrides rather
than silently falling back. Run `scripts/setup.ps1` only for project dependencies;
system CAD/client installations and restart decisions are separate.

Before changing behavior run the existing tests. Keep exact dependency pins and
record purposeful upgrades. Inspect `.codex/config.toml` for execution safeguards;
leave model and reasoning to the user's Codex chat/session selection. Do not
require Astra, High reasoning, or a replacement model/effort default. Written
TOML, client-accepted configuration and active settings are separate facts;
repository instructions cannot enable automatic model switching.
Never assume laptop versions, nozzle, material, plate or AMS from old notes.
