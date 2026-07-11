from __future__ import annotations
import json
import os
from pathlib import Path
import trimesh
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
src = Path(
    os.environ.get("PEG_HOOK_SOURCE_STL", project_dir / "references" / "MP25.stl")
)
out_stl = project_dir / "exports" / "peg_hook_6p8mm_fit_petg.stl"
out_3mf = project_dir / "exports" / "peg_hook_6p8mm_fit_petg.3mf"
out_report = project_dir / "notes" / "peg_hook_6p8mm_fit_petg_report.json"

mesh = trimesh.load_mesh(src, force="mesh")
verts = mesh.vertices.copy()
center_x = 3.2199859619140625
orig_width = 6.439971923828125
scale_x = 1.0559052244994669
full_y_max = 5.4
fade_y_max = 6.2
full_x_radius = 3.25
fade_x_radius = 4.2

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

x = verts[:,0]
y = verts[:,1]
dx = np.abs(x - center_x)
wx = np.where(dx <= full_x_radius, 1.0, np.where(dx >= fade_x_radius, 0.0, 1.0 - smoothstep(full_x_radius, fade_x_radius, dx)))
wy = np.where(y <= full_y_max, 1.0, np.where(y >= fade_y_max, 0.0, 1.0 - smoothstep(full_y_max, fade_y_max, y)))
weight = wx * wy
verts[:,0] = center_x + (x - center_x) * (1.0 + weight * (scale_x - 1.0))
mesh.vertices = verts
mesh.merge_vertices()
mesh.remove_unreferenced_vertices()
mesh.fix_normals()
mesh.export(out_stl)
out_3mf.write_bytes(trimesh.exchange.threemf.export_3MF(mesh))
report = {
    "source_file": str(src),
    "output_stl": str(out_stl.relative_to(project_dir)),
    "output_3mf": str(out_3mf.relative_to(project_dir)),
    "editable_source": str(Path(__file__).relative_to(project_dir)),
    "edit_method": "local_x_axis_scaling_on_lower_clip_region_only",
    "dimension_changed": "lower peg/tab effective clip width",
    "target_fit_dimension_mm": 6.8,
    "measured_original_fit_width_mm": round(orig_width, 2),
    "measured_final_fit_width_mm": round(orig_width * scale_x, 2),
    "overall_extents_mm": [round(float(value), 3) for value in mesh.extents],
    "mesh_validation": {
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
        "euler_number": int(mesh.euler_number),
    },
}
out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(out_stl)
