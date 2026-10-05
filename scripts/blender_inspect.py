"""Executed only by Blender for immutable STL inspection; no mesh operations."""
import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blender_runtime import run


def inspect(request):
    import bpy
    from mathutils import Vector
    original = Path(request['input']).read_bytes()
    if hashlib.sha256(original).hexdigest() != request['input_sha256']:
        raise RuntimeError('Inspection STL hash mismatch.')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'
    # STL stores millimeter numbers without units; convert once to Blender meters.
    properties = bpy.ops.wm.stl_import.get_rna_type().properties
    if 'use_mesh_validate' not in properties:
        raise RuntimeError('Importer cannot explicitly disable mesh validation; inspection stopped.')
    bpy.ops.wm.stl_import(filepath=request['input'], global_scale=.001, use_mesh_validate=False)
    objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    actual = [(max(point[axis] for point in points)-min(point[axis] for point in points))*1000 for axis in range(3)]
    expected = request['expected_extents_mm']
    passed = all(math.isfinite(a) and abs(a-b) <= request['tolerance_mm'] for a,b in zip(actual, expected))
    if not passed:
        raise RuntimeError('Imported bounds disagree with original STL.')
    if Path(request['input']).read_bytes() != original:
        raise RuntimeError('Inspection STL changed during import.')
    for obj in objects:
        obj['inspection_only'] = True
    bpy.ops.wm.save_as_mainfile(filepath=request['scene'])
    Path(request['report']).write_text(json.dumps({'scale_verified': passed,
        'actual_extents_mm': actual, 'expected_extents_mm': expected,
        'meters_per_stl_unit': .001}, allow_nan=False), encoding='utf-8')


if __name__ == '__main__':
    run(inspect)
