# Metric To Standard Chart

Portrait 3D printable wall reference sign for shop use.

## Files

- `metric_to_standard_chart.scad` - editable OpenSCAD source.
- `metric_to_standard_chart_combined.stl` - single combined model.
- `base_and_grid.stl` - base, border, holes, and raised grid.
- `title_and_headers.stl` - white title, header labels, and footer note.
- `metric_text_red.stl` - metric-size column text.
- `standard_text_green.stl` - closest-standard column text.
- `decimal_text_blue.stl` - decimal-equivalent column text.
- `difference_text_orange.stl` - signed-difference column text.
- `all_text_white.stl` - all raised text as one AMS-friendly white part.
- `table_validation_log.txt` - calculated row log used before export.

## Print Notes

- For a black-and-white AMS print, import `base_and_grid.stl` and `all_text_white.stl` together as one assembly, then assign black to the base and white to the text.
- The older column-split STLs are still available if you want separate text colors instead.
- Import all split STLs together as one assembly, then assign colors/materials in the slicer.
- Do not auto-drop the individual text STLs to the build plate; they are already Z-positioned to sit on the base.
- Suggested colors: dark base, white title/header/footer, red metric text, green standard text, blue decimal text, orange/yellow difference text.
- Print flat on the back face with no supports.
- The raised frame and grid are 1.0 mm above the 3.0 mm base.
- The raised text is 1.4 mm above the 3.0 mm base, so letters protrude 0.4 mm above the grid/background for better AMS color separation.
- Four mounting holes are 5.0 mm diameter with centers 10.0 mm from the edges.
- Designed for a normal 0.4 mm FDM nozzle. Use fine layer height if you want crisper text.

## Geometry Contract

- Task mode: `original_product_design`.
- Overall size: 250 mm wide x 360 mm tall.
- Base thickness: 3.0 mm.
- Raised frame/grid target: 1.0 mm above base.
- Raised text target: 1.4 mm above base.
- Minimum raised line width: 0.9 mm.
- Protected interfaces: four 5.0 mm mounting through-holes at 10.0 mm corner inset.
- Physical print/fit status: not physically verified.

## Regenerate

Run from the repository root:

```powershell
py -3 scripts\validate_scad.py metric_to_standard_chart_output\metric_to_standard_chart.scad
py -3 scripts\export_stl.py --input metric_to_standard_chart_output\metric_to_standard_chart.scad --output metric_to_standard_chart_output\metric_to_standard_chart_combined.stl --allow-multiple-bodies
py -3 scripts\export_stl.py --input metric_to_standard_chart_output\metric_to_standard_chart.scad --output metric_to_standard_chart_output\base_and_grid.stl --define 'export_part="base_and_grid"' --allow-multiple-bodies
py -3 scripts\export_stl.py --input metric_to_standard_chart_output\metric_to_standard_chart.scad --output metric_to_standard_chart_output\title_and_headers.stl --define 'export_part="title_and_headers"' --allow-multiple-bodies
py -3 scripts\export_stl.py --input metric_to_standard_chart_output\metric_to_standard_chart.scad --output metric_to_standard_chart_output\metric_text_red.stl --define 'export_part="metric_text_red"' --allow-multiple-bodies
py -3 scripts\export_stl.py --input metric_to_standard_chart_output\metric_to_standard_chart.scad --output metric_to_standard_chart_output\standard_text_green.stl --define 'export_part="standard_text_green"' --allow-multiple-bodies
py -3 scripts\export_stl.py --input metric_to_standard_chart_output\metric_to_standard_chart.scad --output metric_to_standard_chart_output\decimal_text_blue.stl --define 'export_part="decimal_text_blue"' --allow-multiple-bodies
py -3 scripts\export_stl.py --input metric_to_standard_chart_output\metric_to_standard_chart.scad --output metric_to_standard_chart_output\difference_text_orange.stl --define 'export_part="difference_text_orange"' --allow-multiple-bodies
py -3 scripts\export_stl.py --input metric_to_standard_chart_output\metric_to_standard_chart.scad --output metric_to_standard_chart_output\all_text_white.stl --define 'export_part="all_text_white"' --allow-multiple-bodies
```
