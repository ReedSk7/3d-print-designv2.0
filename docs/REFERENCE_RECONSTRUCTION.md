# Reference Reconstruction Workflow

Use reconstruction workflow when the job is about recreating, repairing, or refining an existing part instead of inventing a new one.

Default output is one corrected model unless the user explicitly asks for multiple variants.

## Classify the Task

Treat the task as reconstruction when you have any of these:

- measurements from the real part
- part number or OEM identifier
- OEM or product photos
- broken-part photos
- public or purchased reference STL/CAD
- rough STL, GLB, OBJ, or scan output

## Rank References

Use this order unless the user says otherwise:

1. measured dimensions from the real part
2. trusted or purchased reference STL/STEP/CAD
3. official OEM drawings / service docs / diagrams
4. official product photos
5. user photos of intact or broken part
6. AI-generated meshes or photo-to-3D outputs

## Define Protected Interfaces

Identify the geometry that must stay faithful before any reinforcement or cleanup. Protected interfaces must be defined before reinforcement:

- hole spacing and mounting geometry
- hook tips and latch faces
- pivots, shafts, rods, and bearing seats
- slots, tabs, snaps, and clip faces
- spring contact regions

## What Not to Change

Do not change these by default unless the user explicitly requests it:

- latch faces
- hook tips
- slots
- pivot fits
- mounting faces
- spring contact regions

## Use Rough Meshes Carefully

Use rough STL, GLB, or OBJ files only as seed geometry unless they are explicitly trusted.

- inspect them for overall form, missing regions, and feature placement clues
- measure them if useful for rough sizing or feature spacing
- do not copy their topology into final CAD
- remodel critical interfaces cleanly in OpenSCAD

## Reference Conflicts

- If measurements conflict with photos, measurements win unless they are clearly wrong.
- If paid or trusted reference CAD conflicts with an AI-generated mesh, the paid or trusted reference CAD wins.

## Compare and Revise

After rebuilding the part, compare the current CAD against the best reference using:

- bounding box
- front silhouette
- side silhouette
- top silhouette when useful
- critical local features

If the overall size matches but a hook, tab, slot, latch, or mount still does not, the model is not done.

Use `templates/reconstruction_checklist.md` to track completion and `templates/reference_comparison_log.md` to record revision-by-revision comparisons.

## Reinforcement Rules

Reinforce only non-interface regions by default. Preserve protected interfaces unless the user explicitly requests a changed fit or a durability-driven interface change.

## Low-Confidence Zones

Be honest about low-confidence areas. Note guessed geometry, missing measurements, and places where the current model is a test-fit or best-faith estimate rather than a verified match.

## Reconstruction Completion Checklist

- exact target part defined
- reused surrounding parts defined
- anchor dimensions recorded
- protected interfaces recorded
- bbox and required silhouettes compared
- critical local features checked
- low-confidence zones documented
- STL exported, or export failure documented for a real technical reason
