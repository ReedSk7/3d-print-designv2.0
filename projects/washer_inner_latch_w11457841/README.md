# Washer inner latch W11457841 migration note

This legacy reconstruction project was moved intact from
`3d-print-design-studio` during the July 2026 workspace consolidation. The
original versioned project remains under `v01/` so its source, references,
renders, exports, notes, and manifest stay together.

The SCAD predates the current V2 policy parameters (`wall_thickness`,
`fit_clearance`, `nozzle_diameter`, and `material`), so the repository's policy
validator reports expected schema errors. The migration does not alter the
safety-interlock geometry. Use the OpenSCAD compiler for syntax/export checks,
and treat all fit claims as unverified until the documented physical fit tests
are completed.
