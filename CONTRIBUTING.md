# Contributing

Root `AGENTS.md` is authoritative. Phase 1 changes must stay within the
deterministic generator core and command-line workflow.

## Change Workflow

1. Start from a verified branch and inspect the working tree.
2. Keep generator-specific geometry inside one generator package.
3. Update the generator metadata, parameter schema, defaults, validation,
   expected bounds, documented example, and tests together.
4. Keep all internal calculations in millimeters and retain explicit source
   units in the specification.
5. Add authoritative Measurement Contract requirements for new protected
   interfaces. Never fill a missing interface with an inferred value.
6. Use candidate coupons when nominal geometry is known but clearance remains
   uncertain.
7. Run unit tests, integration tests, the relevant CLI slice, and the output
   policy check.
8. Report the exact computational state reached and state plainly that physical
   fit remains unconfirmed unless real-world evidence exists.

## Generator Package Contract

Each supported generator owns:

- stable ID and semantic version
- metadata and supported artifact kinds
- JSON parameter schema and defaults
- semantic/impossible-geometry checks
- protected-interface dimension map
- deterministic OpenSCAD template/rendering
- expected millimeter bounds
- fit-coupon behavior where applicable
- one source-controlled example specification
- unit and OpenSCAD-backed integration tests

The CLI and workflow resolve generators through `generators/registry.py`; do
not add generator-ID conditionals to those layers.

## Source-Control Boundaries

Track specifications, Python/OpenSCAD templates, tests, documentation, and
small intentional fixtures. Do not commit routine generated SCAD, STL, PNG,
3MF, temporary meshes, logs, or workspace data. Never add ASCII STL.

Do not commit customer/private data, paid references, or ambiguously licensed
photos and meshes. Draft PR #1 is read-only salvage material and must not be
merged or copied wholesale.

## Required Checks

```powershell
& .\.venv\Scripts\python.exe -m compileall -q core generators scripts tests
& .\.venv\Scripts\python.exe -m pytest tests\unit -q
& .\.venv\Scripts\python.exe -m pytest tests\integration -q
& .\.venv\Scripts\python.exe scripts\check_output_policy.py
```

OpenSCAD absence must fail the integration suite.
