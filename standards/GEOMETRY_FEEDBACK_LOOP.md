# Geometry Feedback Loop

This ledger records physical print deviations that must inform future clearance, shrinkage, and fit decisions.

Before starting any `reference_based_reconstruction` task, review this file and apply relevant measured corrections to the Geometry Contract. If a repeated deviation is material-, nozzle-, or printer-specific, update `standards/printer_material_profiles.json` or document why the profile is not changed.

Do not use this ledger for dashboard, app, or workflow bugs. Track only physical geometry calibration and fit feedback.

| Project Name | Date | Target Material | Nozzle Size | Nominal CAD Dim (mm) | Printed Actual Dim (mm) | Delta (mm) | Corrective Action Taken |
|---|---|---|---|---:|---:|---:|---|
| _example_project_ | YYYY-MM-DD | PETG | 0.4 mm | 10.00 | 9.85 | -0.15 | Increase matching clearance/profile offset by 0.15 mm after confirming repeatability. |
| battery_strap_holder | 2026-05-29 | PETG | 0.6 mm | 4.00 | 3.85 | -0.15 | Apply +0.15 mm calibrated PETG/0.6 mm hole compensation for the measured hole diameter in `standards/printer_material_profiles.json`. |
