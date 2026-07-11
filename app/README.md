# 3D Print Design Studio Dashboard

Local-only dashboard for the reconstruction-first OpenSCAD workflow in this repo.

## What It Does

- Tracks project intake records in `app/data/projects.json`.
- Detects SCAD, STL, notes, manifests, review reports, and preview files in `projects/`.
- Generates copy-ready Codex/OpenSCAD prompts that remind the agent to follow root `AGENTS.md`.
- Calls the repo scripts for project bootstrap, SCAD validation, STL export, preview rendering, output checks, and next-version creation.
- Keeps paid references and customer data local.

## Install

```powershell
cd app
npm install
```

## Run

```powershell
npm run dev
```

The React app runs through Vite at `http://127.0.0.1:5173`.
The local API runs at `http://127.0.0.1:4177`.

## Files Created

- `app/data/projects.json`: local project records.
- `app/data/settings.json`: dashboard defaults.
- Project bootstrap uses the existing repo script and writes under `projects/<project_stem>/`.

## Current Limits

- No database.
- No login.
- No cloud sync.
- No payment processing.
- No direct STL viewer in v01.
- Commands run locally and report stdout, stderr, exit code, and expected-file checks.
