# Protected Interfaces

Protected interfaces are fit-critical or function-critical surfaces and dimensions that must remain faithful for the part to work.

Define protected interfaces before remodeling, reinforcement, chamfering, thickening, or cosmetic cleanup.

Protected interfaces must be included in the project Geometry Contract before final OpenSCAD geometry begins.

## Common Examples

- mounting hole spacing
- mounting faces
- latch faces
- hook tips
- snap faces
- clip faces
- slot widths
- tabs
- pivots
- shaft fits
- rod fits
- bearing seats
- insert seats
- spring contact regions
- locking tabs
- curved mating surfaces

## Rules

- Compare protected interfaces directly against authoritative references.
- Document protected interfaces in notes, manifest, comparison logs, and review reports.
- If a protected interface lacks authoritative dimensions, block final model generation and produce a measurement checklist or minimal fit-test scaffold.
- Do not modify protected interfaces without explicit instruction.
- Do not redesign protected interfaces for looks.
- Reinforce non-interface regions first.
- If an interface change is required for strength, record the reason and expected fit impact before export.
