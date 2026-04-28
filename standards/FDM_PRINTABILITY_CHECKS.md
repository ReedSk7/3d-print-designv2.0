# FDM Printability Checks

FDM is the default process assumption unless the user explicitly requests another process.

## Geometry Checks

- Keep walls at least two nozzle widths.
- 0.4 mm nozzle baseline: 0.8 mm minimum wall, 1.2 mm safer for durable parts.
- Use a conservative 45 degree unsupported overhang default.
- Keep bridge spans limited; long bridges need support, split geometry, or redesign.
- Printed holes often come out undersized. Critical holes, pins, and insert seats need compensation or test-fit notes.
- Snap-fit layer direction matters. Avoid placing flexing snap arms so layer lines become the likely fracture path.
- Reinforce non-interface regions first.
- Do not thicken, chamfer, or reshape protected interfaces unless the user explicitly asks for interface changes.

## Printer Limits

- Bambu Lab P2S: 256 x 256 x 256 mm
- Qidi XPlus 3: 280 x 280 x 270 mm
- Qidi XPlus 3 Pro: treat as 280 x 280 x 270 mm unless verified in repo standards

If a part exceeds the intended printer volume:

- warn
- split into interlocking pieces
- support exporting one part at a time

## Tolerance Defaults

- loose fit: 0.4 to 0.6 mm clearance
- normal slip fit: 0.2 to 0.35 mm clearance
- tight fit: 0.1 to 0.2 mm clearance
- screw holes should be adjustable by variable
- measured test-fit results override defaults
- hardware library values are starters, not final authority

## Material Defaults

- PLA: indoor cosmetic or simple parts
- PETG: heat, outdoor, impact, or functional parts
- TPU: flexible parts only
- ASA/ABS: heat or outdoor durability when the printer and ventilation setup support it

## Print Plan Fields

Record these in project notes:

- support plan
- brim plan
- wall count
- layer height
- infill
- heat exposure
- outdoor exposure
- screw loads
- risk rating: Low, Medium, High
