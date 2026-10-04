"""Optional version-bound Blender inspection; never changes source geometry."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from core.workflow.review import snapshot_generation, revision_directory
from core.workflow.publication import publish_bundle

TARGET='5.2.2'
def compatibility(version):
    match=re.search(r'Blender\s+(\d+\.\d+\.\d+)',version)
    return {'target':TARGET,'version':match.group(1) if match else None,'compatible':bool(match and match.group(1)==TARGET),'optional':True}

def probe_blender():
    explicit=os.environ.get('BLENDER_PATH')
    path=Path(explicit) if explicit else None
    if explicit and not path.is_file(): return {**compatibility(''),'detail':'Explicit BLENDER_PATH is unavailable; correct it without installing automatically.'}
    if not path:
        found=shutil.which('blender') or shutil.which('blender.exe')
        candidates=sorted(Path(r'C:\Program Files\Blender Foundation').glob('*/blender.exe'))
        path=Path(found) if found else next(iter(candidates),None)
    if not path: return {**compatibility(''),'detail':'Blender not found. OpenSCAD previews remain available.'}
    try:
        result=subprocess.run([str(path),'--version'],capture_output=True,text=True,timeout=15,check=True)
        return {**compatibility(result.stdout),'path':str(path.resolve()),'detail':'Exact target required for automated inspection; no install or downgrade.'}
    except (OSError,subprocess.SubprocessError) as exc:
        return {**compatibility(''),'detail':f'Blender version probe failed: {exc}'}

def inspect_blender(manifest: Path,*,revision='r01'):
    tool=probe_blender()
    if not tool['compatible']: raise ValueError(tool['detail']+f" Target {TARGET}; detected {tool.get('version')}.")
    generation,scad,stl,spec,mesh=snapshot_generation(manifest)
    target=revision_directory(generation,'blender',revision)
    with tempfile.TemporaryDirectory(prefix='.blender-inspection-',dir=generation.workspace_root) as temporary:
        staging=Path(temporary); (staging/'inspection.stl').write_bytes(stl)
        request={'input':str(staging/'inspection.stl'),'scene':str(staging/'inspection.blend'),
                 'report':str(staging/'scale-check.json'),'expected_extents_mm':[float(v) for v in mesh.extents_mm],
                 'tolerance_mm':float(generation.spec.verification_policy.mesh_bounds_tolerance_mm)}
        request_path=staging/'request.json'; request_path.write_text(json.dumps(request))
        script=Path(__file__).resolve().parents[2]/'scripts/blender_inspect.py'
        completed=subprocess.run([tool['path'],'--background','--factory-startup','--disable-autoexec','--python',str(script),'--',str(request_path)],capture_output=True,text=True,timeout=120)
        if completed.returncode or not (staging/'scale-check.json').is_file() or not (staging/'inspection.blend').is_file():
            raise RuntimeError('Blender inspection failed; no inspection bundle published. '+completed.stderr[-2000:])
        report=json.loads((staging/'scale-check.json').read_text())
        if report.get('scale_verified') is not True: raise ValueError('Blender imported bounds failed millimeter-scale verification.')
        request_path.unlink()
        record={'blender':tool,'source_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
                'stl_sha256':hashlib.sha256(stl).hexdigest(),'scale':report,'visual_review':'pending','physical_fit':'not_confirmed',
                'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in staging.iterdir()}}
        (staging/'inspection-manifest.json').write_text(json.dumps(record,indent=2))
        publish_bundle(staging,target,manifest_name='inspection-manifest.json')
    return target
