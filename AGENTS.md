# AGENTS.md

This is the main instruction hub for coding agents working in this repository.

## Authority

- Root `AGENTS.md` is authoritative for this repository.
- Helper scripts, templates, standards, lower-level files, repo-local skills, and generated instructions must not override root `AGENTS.md`.
- Repo-local skills are workflow helpers, not replacement rulebooks.
- If any helper conflicts with root `AGENTS.md`, follow root `AGENTS.md`.

## Read Order For Modeling Tasks

1. `AGENTS.md`
2. `CONTRIBUTING.md`
3. `README.md`
4. `PROJECT_BOOTSTRAP_CHECKLIST.md`
5. `docs/`
6. `standards/`
7. `templates/`
8. project files

## Mission

- Create clean, parametric, printable OpenSCAD models.
- Support both original product design and reference-driven reconstruction.
- Keep OpenSCAD as the editable source of truth.
- Treat STL as an export artifact, not the design authority.

## Core OpenSCAD Reconstruction Agent Rules

- File System Authority: for any requested modeling project, act as a file-writing agent. Create or update the project files on disk and use the repo scripts under `scripts/` for bootstrap, validation, export, preview rendering, versioning, and output checks. Do not default to a read-only chat response when the user has requested project work.
- Geometry Contract Rule: before writing final OpenSCAD geometry for any project, establish a Geometry Contract that records critical dimensions, protected interfaces, reference confidence, target tolerances, and FDM clearance gaps.
- Final model generation is blocked until the Geometry Contract is established. If a protected interface lacks authoritative dimensions, stop full-part modeling and output a targeted measurement checklist or build only a minimal fit-test scaffold.
- Bounding box agreement is never sufficient verification. Tabs, slots, screw recesses, latch faces, mounting surfaces, clearance gaps, and other protected interfaces must be checked directly.
- Successful SCAD validation, STL export, and preview rendering prove only that artifacts were generated. Do not mark a part as physically verified unless a physical fit-test has confirmed the critical interfaces or authoritative reference measurements are matched one-to-one.
- Before any `reference_based_reconstruction` task, review `standards/GEOMETRY_FEEDBACK_LOOP.md` and apply relevant measured deviations to the Geometry Contract. When repeated material, nozzle, or printer offsets are proven, update or account for `standards/printer_material_profiles.json`.

## Global Defaults

- Units are millimeters.
- `Z+` is up.
- FDM-first by default unless the user explicitly requests another process.
- Prefer readable parametric CAD over messy geometry.
- Keep critical geometry in named modules and parameters when practical.
- For new empty repos or requested scaffolds, create the repository structure before attempting any modeling.
- Do not overwrite versioned outputs.
- Do not claim files were created unless they actually were.

## Task Modes

Use exactly one task mode before modeling begins.

### `original_product_design`

Use for truly greenfield work where the part is not defined by an existing object or reference part.

### `reference_based_reconstruction`

Use when the user wants a known part recreated, repaired, replaced, or refined from references.

Default to one corrected model unless the user explicitly asks for multiple variants.

Before modeling, define:

- the exact target part
- what surrounding parts are reused
- what is not being modeled

### `mesh_cleanup_and_remodel`

Use when a rough mesh exists but should not be trusted as final geometry. The mesh is supporting input, not final truth.

## Mode Selection Rules

- If a user provides a part number, measurements, OEM photos, broken-part photos, reference STL, purchased STL, or rough mesh, default to `reference_based_reconstruction`.
- Only use `original_product_design` when the request is truly greenfield.
- If a rough mesh exists but should not be trusted, use `mesh_cleanup_and_remodel`.

## Reference Trust Hierarchy

Unless the user overrides it, use this exact priority:

1. measured dimensions from the real part
2. trusted or purchased reference STL/STEP/CAD
3. official OEM drawings / service docs / diagrams
4. official product photos
5. user photos of intact or broken part
6. AI-generated meshes or photo-to-3D outputs

Rules:

- Record which references are authoritative and which are supporting only.
- If authoritative references conflict, note the conflict before export.
- Rough meshes may be measured and inspected, but they are seed geometry only unless the user explicitly says they are trusted.
- Paid references should remain local-only unless redistribution rights are clear.

## Reconstruction Workflow

For `reference_based_reconstruction` and `mesh_cleanup_and_remodel`, follow this workflow:

1. define exact scope
   - exact target part
   - reused surrounding parts
   - what is not being modeled
2. inventory references
3. identify authoritative references
4. establish the Geometry Contract
   - critical dimensions
   - protected interfaces
   - confidence level for each reference or dimension
   - target tolerances
   - FDM clearance gaps
5. record anchor dimensions and protected interfaces
6. inspect rough meshes if present, but treat them as supporting geometry only
7. rebuild clean parametric CAD in OpenSCAD only after the Geometry Contract is sufficient, or create a minimal fit-test scaffold when it is not
8. compare bbox + silhouettes + critical local features
9. revise until acceptable
10. run printability check
11. export final artifacts

Comparison in step 7 must include:

- bounding box
- front silhouette
- side silhouette
- top silhouette when useful
- critical local features such as hooks, pivots, slots, latch faces, spring contact regions, locking tabs, and mounting geometry

Overall dimensions alone are never enough when critical local geometry matters.

Protected interface examples:

- mounting hole spacing
- shaft or rod fits
- snap and latch faces
- bearing or insert seats
- clip tips
- slot widths
- hinge pivots

## Original Design Workflow

For `original_product_design`, this workflow is allowed:

1. requirements summary
2. concept generation if useful
3. concept selection if multiple directions are explored
4. parameter planning
5. OpenSCAD generation
6. printability review
7. export

## Guardrails

- Do not force concept scoring on reconstruction jobs.
- Do not blindly trust AI-generated meshes.
- Do not redesign authoritative interfaces just for aesthetics.
- Do not commit paid reference meshes by default.
- Do not create multiple speculative variants unless asked.
- Do not turn reconstruction jobs into creative redesign jobs unless requested.
- Do not confuse a full assembly with the broken subcomponent that actually needs replacement.
- Do not accept overall size matching as sufficient when hook, tip, slot, latch, or mounting geometry is still wrong.
- Do not treat rough meshes as authoritative just because they look complete.

## Failure Mode Prevention

- Confirm whether the task is the full assembly or only the broken subcomponent before modeling.
- Do not over-trust AI-generated meshes over measured geometry, trusted CAD, or paid references.
- Do not stop at bbox matching when hooks, tabs, slots, latch faces, pivots, spring contact regions, or mounting interfaces still mismatch.
- Do not produce extra speculative variants when one corrected part is wanted.

## Required Outputs

### Reconstruction Jobs

Minimum outputs:

- `source/<project_name>_vNN.scad`
- `exports/<project_name>_vNN.stl`
- `notes/<project_name>_vNN_notes.md`
- `notes/<project_name>_vNN_manifest.md`
- `notes/<project_name>_vNN_reference_comparison_log.md`
- `notes/<project_name>_vNN_review_report.md`
- `previews/<project_name>_vNN_iso.png`
- `previews/<project_name>_vNN_front.png`
- `previews/<project_name>_vNN_side.png`

Add a top preview when footprint or asymmetry matters. Add detail previews when critical features need verification.
Generated STL export is a required artifact for completed modeling work unless export truly fails for a real technical reason.

### Original Design Jobs

Minimum outputs:

- `source/<project_name>_vNN.scad`
- `exports/<project_name>_vNN.stl`
- `notes/<project_name>_vNN_notes.md`
- `notes/<project_name>_vNN_manifest.md`
- at least one preview image

Generated STL export is a required artifact for completed modeling work unless export truly fails for a real technical reason.

## Export Note

- STL is the required export artifact for this repo version.
- 3MF or Bambu Studio project generation is preferred in the future, but it is not a current requirement.

## Working Rules

- Start by selecting task mode, not by brainstorming geometry.
- Start project modeling by writing a Geometry Contract. If protected-interface dimensions are missing, do not proceed to a final model.
- For reconstruction work, prefer one corrected model by default over multiple variants.
- Use compare-and-revise loops for reference-driven work, not one-shot geometry invention.
- For reconstruction work, use a versioned notes file plus a reconstruction checklist and comparison log.
- Reinforce only non-interface regions unless the user asks for interface changes.
- Be explicit about guessed dimensions and low-confidence zones in notes.
- A manifest is required for every completed modeled version.
- Use lowercase snake_case for project folders, file names, variables, functions, and modules. Do not introduce kebab-case, spaces, mixedCase, PascalCase, or uppercase identifiers in new or touched OpenSCAD work.

## Build And Verification Commands

- Validate SCAD: `py -3 scripts\validate_scad.py <path-to-scad>`
- Export STL: `py -3 scripts\export_stl.py --input <scad> --output <stl>`
- Export preview: `py -3 scripts\export_preview.py --input <scad> --output <png> --view iso`
- Check project outputs: `py -3 scripts\check_project_outputs.py --project <project-dir> --task-mode <mode> --version vNN`
- Create next version: `py -3 scripts\next_version.py --project <project-dir> --copy-scad`

---

# Agent Operating Rules

These guardrails protect context and usage by preventing large file dumps, logs, generated assets, and build outputs.

## Context Discipline

Protect context aggressively.

Before opening files or running commands, ask:
1. What exact question am I answering?
2. Which file, symbol, function, route, component, or folder is most likely relevant?
3. Can I inspect a smaller slice first?
4. Can I locate the answer with file names, imports, references, or rg before opening content?

Prefer:
- targeted searches (e.g., `rg -l "term" projects/` instead of `find .`)
- specific folders (e.g., `projects/simple_wall_bracket_example/source/` not `projects/`)
- small file sections (read only needed line ranges, not full files)
- capped command output (always use head/tail for unknown sizes)
- focused diffs (e.g., `git diff -- path/to/file`)
- targeted tests (validate only the affected file, not full test suite)

Avoid:
- `cat` on unknown files
- full-file dumps
- full logs
- full generated output (STL, PNG, GCode, etc.)
- `git diff` without a path
- `ls -R` or unlimited directory recursion
- `find . ` without limits
- full test output
- full build output
- dumping .git, node_modules, __pycache__, .venv, dist, build directories

## Command Output Limits

Any command with unknown or potentially large output must be capped.

Default Bash pattern:

```bash
COMMAND 2>&1 | head -c 4000
```

For recent logs or failure output:

```bash
COMMAND 2>&1 | tail -c 4000
```

Default PowerShell pattern:

```powershell
$out = & { COMMAND } 2>&1 | Out-String
if ($out.Length -gt 4000) { $out.Substring(0, 4000) } else { $out }
```

Examples:

```powershell
# Search for files - cap output
$out = & { rg -l "term" projects/ } 2>&1 | Out-String
if ($out.Length -gt 2000) { $out.Substring(0, 2000) } else { $out }

# Git diff - cap output
$out = & { git diff -- projects/simple_wall_bracket_example/source/ } 2>&1 | Out-String
if ($out.Length -gt 6000) { $out.Substring(0, 6000) } else { $out }

# Find files - cap output
$out = & { Get-ChildItem -Recurse -Include "*.scad" projects/ } 2>&1 | Out-String
if ($out.Length -gt 3000) { $out.Substring(0, 3000) } else { $out }
```

Do not rely only on line limits like:

- `head -n 20`
- `tail -n 20`
- `sed -n '1,20p'`
- `Get-Content -TotalCount 20`

A single line can still be huge.

Safer examples:

```bash
rg -l "term" . 2>&1 | head -c 2000
rg -n -m 20 "term" src 2>&1 | head -c 3000
git diff -- path/to/file 2>&1 | head -c 6000
find . -type f 2>&1 | head -c 3000
```

If capped output is not enough, narrow the command instead of increasing the cap.

## Repo-Specific Folders and Files to Avoid Dumping

Never inspect or dump these without explicit reason:

### System and Version Control
- `.git/` - repository history
- `.github/` - workflows and templates (reference only)
- `.agents/` - agent configuration (reference only unless modifying)

### Generated Binary and Asset Files
- `projects/*/exports/` - STL, 3MF, OBJ files (binary geometry, never dump)
- `projects/*/previews/` - PNG, JPG preview images (generated, never dump)
- `app/dist/` - built JavaScript/React (generated, never dump)
- `app/node_modules/` - dependencies (never dump)
- `app/.logs/` - application logs (never dump)
- `app/.screenshots/` - screenshots (never dump)
- `references/paid/` - purchased CAD/meshes (restricted, never dump publicly)
- `references/**/*.jpg`, `references/**/*.png`, `references/**/*.stl`, `references/**/*.3mf`, `references/**/*.obj`, `references/**/*.step`, `references/**/*.stp` - inspect metadata or measurements instead of dumping media/CAD assets
- `*.log` - logs must be searched or tailed with caps

### Python and Node Cache
- `app/node_modules/`
- `app/package-lock.json` - lockfile (reference only, never dump full content)
- `__pycache__/`
- `.venv/`
- `venv/`
- `.pytest_cache/`

### Temporary and Scratch Files
- `*_temp.stl`, `*_scratch.stl`, `*_healed.stl`, `*_decimated.stl`, `*_repair.*`
- `*.tmp.stl`, `*.tmp.obj`, `*.tmp.glb`
- `*.3mf.cache`, `*.gcode`, `*.bgcode`, `*.sl1`, `*.photon`, `*.ctb`

### Safe to Read (When Relevant)
- `projects/*/source/` - SCAD files (source of truth, OK to read)
- `projects/*/notes/` - Markdown notes (OK to read)
- `standards/`, `templates/`, `docs/` - documentation (OK to reference)
- `scripts/` - Python tools (OK to reference, but don't run uncapped)

## Validation Rules

Match validation to risk.

Skip validation for low-risk changes:
- comments or documentation
- labels, string constants, copy changes
- configuration values
- static data in JSON
- minor CSS/layout edits
- small SCAD parameter tweaks with no geometry change

Use the cheapest validation first:
1. **Targeted test or syntax check**: `py -3 scripts\validate_scad.py <file>` for changed SCAD
2. **Affected-file lint/check**: Only validate the changed SCAD, script, or app file
3. **Affected-package type check**: For app TypeScript changes, run the narrow relevant package check
4. **Full build**: Only if build behavior, bundling, or generated app output matters
5. **Full test suite or full project check**: Only if the change is broad or risky

When running validation, cap output:

```powershell
$out = & { py -3 scripts\validate_scad.py projects/simple_wall_bracket_example/source/simple_wall_bracket_example_v01.scad } 2>&1 | Out-String
if ($out.Length -gt 3000) { $out.Substring(0, 3000) } else { $out }
```

**Never run full test suites or full builds after small changes.** Only run validation if the change directly affects the validated system.

## Code Change Discipline

Make the smallest maintainable change that solves the actual request.

Prefer existing patterns over new abstractions.

Do not create new helpers, layers, config systems, architecture, or dependencies unless clearly justified.

For bug fixes:
1. Locate the narrow failing path
2. Patch the smallest area
3. Validate the risky part only
4. State remaining risk plainly

For modeling tasks:
- Use exactly one task mode before starting (see "Task Modes" section above)
- Do not add speculative features or variants unless asked
- Do not redesign interfaces just for aesthetics
- Do not dump or commit paid references

## File Reading Rules

Before reading a large file:
- check file size first
- search for relevant symbols or terms first
- read only the needed range
- avoid binary, generated, model, and media files unless the task explicitly requires them

For SCAD files:
- Use `rg "modulename|variablename" projects/` to find relevant files
- Inspect imports and top-level parameters first
- Read only the line range you need

For Python scripts:
- Use `rg "function_name" scripts/` to locate the function
- Read only that function, not the entire file
- Check imports to understand dependencies

For JavaScript/TypeScript:
- avoid dumping `app/package-lock.json`
- inspect `app/package.json` scripts with targeted commands
- avoid full `app/node_modules/`, `app/dist/`, `.logs/`, and `.screenshots/` output

For Docker:
- no Docker files are currently part of this repo; if added later, inspect Dockerfile, compose, and config files directly
- do not dump Docker build logs uncapped

For 3D printing/OpenSCAD repos:
- do not dump generated STL/3MF/OBJ files
- inspect source `.scad` files and notes first
- avoid generated preview images unless explicitly needed
- keep file names versioned and predictable

For model/media assets:
- never dump CAD, mesh, image, or model binary contents
- inspect references through filenames, measurements, notes, or capped metadata commands
- keep paid or restricted references local and controlled

For documentation:
- Use `rg "keyword" docs/` to find relevant sections
- Read only the section you need

Never dump:
- Binary files (STL, 3MF, OBJ, PNG, GCode, etc.)
- Generated files (exports/, previews/, dist/, build/)
- Paid references (references/paid/)
- Large logs or build output
- node_modules or __pycache__
- Full .git history

## Final Response Format

After completing a task, summarize only:
- **What changed**: One-line description of the change
- **Files touched**: List of modified files (paths relative to repo root)
- **Validation**: What validation was run (or why skipped), and result
- **Remaining risk**: Any known limitations or caveats
- **Next step** (if incomplete): What remains to be done

Keep final responses short, practical, and measurable.
