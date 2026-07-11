# Codex Workflow for 3D Print Design Repo

This guide explains how to use Codex safely and efficiently in this OpenSCAD 3D printing repository.

## Quick Reference

**Do:**
- Ask about task mode selection, SCAD syntax, parametric design patterns
- Request validation of specific SCAD files
- Ask for STL exports, preview generation, or project structure setup
- Reference AGENTS.md or standards/ for modeling guidance
- Work with source/ and notes/ folders

**Safe to inspect when relevant:**
- `projects/*/source/`
- `projects/*/notes/`
- `scripts/`
- `docs/`, `standards/`, and `templates/`
- small config files such as `app/package.json`, `app/vite.config.ts`, and `app/data/*.json`

**Don't ask Codex to:**
- Dump any file from exports/, previews/, or app/dist/
- Dump reference media/CAD files from references/, especially references/paid/
- Dump app/node_modules/, app/package-lock.json, app/.logs/, or app/.screenshots/
- List large directories with `ls -R` or unlimited recursion
- Show full logs, full build output, or full git diffs
- Read binary files (STL, PNG, 3MF, GCode, etc.)
- Commit or share paid references (references/paid/)
- Run full test suites after small changes

## Task Modes

Codex must choose exactly one task mode before modeling begins:

### original_product_design
For new, greenfield parts with no reference.

Ask: *"Create a [part description] for 3D printing. Units in mm, Z+ is up, assume FDM on Bambu Lab P2S with PETG."*

### reference_based_reconstruction
For known parts: part numbers, photos, measurements, CAD, purchased STL.

Ask: *"Reconstruct the [part name] from [reference]. Here are measured dimensions: [...]. Protect these interfaces: [...]."*

### mesh_cleanup_and_remodel
For rough STL, scan outputs, or AI-generated meshes that need rebuild.

Ask: *"Clean up and remodel this mesh as parametric OpenSCAD: [reference or measurements]."*

Codex will ask you to define exact scope before starting.

## Safe Workflows

### 1. Inspecting a Project

**Safe:**
```
"What's in projects/simple_wall_bracket_example/source/?"
"Show me projects/simple_wall_bracket_example/source/simple_wall_bracket_example_v01.scad (lines 1-50)"
"Search for all SCAD files that use module 'hook_slot'"
```

**Unsafe (Codex will refuse):**
```
"Dump all files in projects/"
"Show me projects/*/exports/ (contains binary STL files)"
"List -R projects/ (too much output)"
"Show me the full contents of app/package-lock.json"
```

### 2. Creating a Project

**Do this:**
```powershell
# Codex will help you run this:
py -3 scripts\new_project.py --name "wall bracket" --task-mode original_product_design --printer "Bambu Lab P2S" --material PETG
```

Then ask: *"I created wall bracket project. Help me fill in the SCAD file with [requirements]."*

### 3. Validating SCAD

**Do this:**
```
"Validate my SCAD file: projects/wall_bracket/source/wall_bracket_v01.scad"
```

Codex will run the validation and cap output automatically.

### 4. Exporting Results

**Do this:**
```
"Export STL for projects/wall_bracket/source/wall_bracket_v01.scad to exports/"
"Generate preview images (iso, front, side) for projects/wall_bracket/source/wall_bracket_v01.scad"
"Check final outputs for wall_bracket project v01"
```

Codex will run the scripts and report results without dumping binary files.

### 5. Debugging SCAD Issues

**Do this:**
```
"My SCAD won't render. Here's the error: [error message]. What's wrong?"
"How do I create a parametric slot that's [dimension] wide?"
"Show me the pattern for creating a locking tab in OpenSCAD"
```

**Avoid:**
```
"Show me the full error log" (cap it first)
"Dump the entire SCAD file" (ask for specific lines or functions)
```

### 6. Referencing Documentation

**Do this:**
```
"Per AGENTS.md, what are the protected interfaces I must preserve?"
"What's the naming convention in standards/NAMING_AND_VERSIONING.md?"
"Show me the reconstruction checklist template"
```

**Avoid:**
```
"Dump AGENTS.md" (Codex will reference it without dumping)
"Show me all of standards/" (ask for specific files)
```

## Common Commands You'll Use

| Task | Command |
|------|---------|
| Create project | `py -3 scripts\new_project.py --name "project name" --task-mode original_product_design` |
| Validate SCAD | `py -3 scripts\validate_scad.py projects/project_name/source/project_name_v01.scad` |
| Export STL | `py -3 scripts\export_stl.py --input projects/project_name/source/project_name_v01.scad --output projects/project_name/exports/project_name_v01.stl` |
| Preview (ISO) | `py -3 scripts\export_preview.py --input projects/project_name/source/project_name_v01.scad --output projects/project_name/previews/project_name_v01_iso.png --view iso` |
| Check outputs | `py -3 scripts\check_project_outputs.py --project projects/project_name --task-mode original_product_design --version v01` |
| Next version | `py -3 scripts\next_version.py --project projects/project_name --copy-scad` |

Codex will help you construct or run these without dumping their output.

## Context Protection Strategy

Codex follows these rules to protect token budget:

1. **No file dumps** - Uses targeted search before reading files
2. **Capped output** - All commands output is capped at ~4000 characters
3. **No binary inspection** - Never opens STL, PNG, 3MF, GCode, etc.
4. **No logs** - Skips full logs, uses only error/summary lines
5. **No git archaeology** - Won't do `git log` or `git diff` without path limits
6. **No node_modules** - Never inspects dependencies or lockfiles
7. **No build artifacts** - Avoids dist/, __pycache__, .pytest_cache, etc.

## Preferred Final Response Format

At the end of repo work, Codex should summarize only:

- **What changed**
- **Files touched**
- **Validation run**, or why validation was skipped
- **Remaining risk**
- **Next step**, only if something is incomplete

## Troubleshooting

**"Codex asked about file size before reading"**
This is good. Codex protects context by checking before dumping.

**"Codex capped a command's output"**
This is expected. Use a more specific query if you need the full result (e.g., search for a specific error, validate a specific file, etc.).

**"I got an error that starts with 'Avoid dumping'**
This means your request would waste context. Rephrase to be more specific:
- Instead of "show me all logs", ask "why is X failing?"
- Instead of "dump the exports folder", ask "did exports/file.stl get created?"
- Instead of "ls -R projects", ask "which projects have reconstruction notes?"

**"I need to see a full file"**
Codex will read it in sections:
- Ask for specific line ranges: *"Show me lines 50-100 of simple_wall_bracket_example_v01.scad"*
- Ask for specific functions: *"Show me the 'hook_slot' module in wall_bracket_v01.scad"*
- Ask for imports or parameters: *"What are the top-level parameters in wall_bracket_v01.scad?"*

## Reference Hierarchy

When working with reconstructions, Codex respects this order (from most to least trusted):

1. **Measured dimensions** from the real part (most authoritative)
2. **Purchased/trusted reference STL/STEP/CAD**
3. **Official OEM drawings or service docs**
4. **Official product photos**
5. **User photos** of intact or broken part
6. **AI-generated meshes** or photo-to-3D outputs (least authoritative)

Codex will ask you to clarify which references are authoritative for your task.

## Final Notes

- **AGENTS.md is authoritative.** If Codex behavior conflicts with AGENTS.md, AGENTS.md wins.
- **Ask before doing.** Codex will ask clarifying questions rather than guess.
- **Validation is cheap.** Codex validates specific files, not the whole repo.
- **Task mode first.** Codex picks the right task mode before generating any geometry.
- **Exports are outputs.** STL, PNG, and 3MF files are artifacts, not source.

For questions about modeling workflows, reference conventions, or protected interfaces, see [AGENTS.md](../AGENTS.md).
