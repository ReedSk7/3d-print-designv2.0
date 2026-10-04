"""Executed only by Blender for immutable STL inspection; no mesh operations."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

request=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.0
bpy.context.scene.unit_settings.length_unit='MILLIMETERS'
# STL stores millimeter numbers without units; convert once to Blender meters.
properties=bpy.ops.wm.stl_import.get_rna_type().properties
if 'use_mesh_validate' not in properties:
    raise RuntimeError('Importer cannot explicitly disable mesh validation; inspection stopped.')
bpy.ops.wm.stl_import(filepath=request['input'],global_scale=0.001,use_mesh_validate=False)
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
points=[o.matrix_world@Vector(corner) for o in objects for corner in o.bound_box]
actual=[(max(p[axis] for p in points)-min(p[axis] for p in points))*1000 for axis in range(3)]
passed=all(abs(a-b)<=request['tolerance_mm'] for a,b in zip(actual,request['expected_extents_mm']))
if not passed: raise RuntimeError('Imported bounds disagree with original STL.')
for obj in objects: obj['inspection_only']=True
bpy.ops.wm.save_as_mainfile(filepath=request['scene'])
Path(request['report']).write_text(json.dumps({'scale_verified':passed,'actual_extents_mm':actual,'expected_extents_mm':request['expected_extents_mm'],'meters_per_stl_unit':0.001}))
