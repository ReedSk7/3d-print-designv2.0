"""Optional version-bound Blender inspection; never changes source geometry."""
import ctypes
import hashlib
import json
import math
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from core.workflow.review import snapshot_generation, revision_directory
from core.workflow.publication import publish_bundle
from core.workshop.ownership import WorkerContainment

TARGET = '5.2.2'
PROBE_TIMEOUT_SECONDS = 15
INSPECTION_TIMEOUT_SECONDS = 120
MAX_RESULT_BYTES = 16384


def compatibility(version):
    match = re.search(r'Blender\s+(\d+\.\d+\.\d+)', version)
    return {'target': TARGET, 'version': match.group(1) if match else None,
            'compatible': bool(match and match.group(1) == TARGET), 'optional': True}


def _completion(path, request):
    try:
        with path.open('rb') as stream:
            payload = stream.read(MAX_RESULT_BYTES + 1)
        if len(payload) > MAX_RESULT_BYTES:
            raise ValueError('record too large')
        record = json.loads(payload)
        version = record.get('runtime_version')
        if (not isinstance(record, dict) or type(record.get('protocol')) is not int
                or record['protocol'] != 1
                or any(record.get(key) != request[key] for key in ('request_id', 'operation', 'job_name'))
                or record.get('status') not in {'started', 'success', 'error'}
                or type(record.get('pid')) is not int or record['pid'] <= 0
                or not isinstance(version, list) or len(version) != 3
                or any(type(value) is not int or not 0 <= value <= 9999 for value in version)
                or not isinstance(record.get('runtime_path'), str)
                or len(record['runtime_path']) > 4096):
            raise ValueError('invalid identity, status or runtime')
        if record['status'] == 'error' and (not isinstance(record.get('error'), str)
                                            or len(record['error']) > 2000):
            raise ValueError('invalid failure detail')
        return record
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        raise RuntimeError(f'Invalid Blender completion record: {exc}') from None


def _runtime_handle(pid):
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x100000, False, pid)
    return kernel, handle


def _run_blender(path, request, *, operation, timeout, workspace_root=None):
    """Wait for the actual child, and stop only this invocation's owned processes."""
    if operation not in {'probe', 'inspection'}:
        raise ValueError('Unsupported Blender operation.')
    root = Path(workspace_root) if workspace_root is not None else Path(__file__).resolve().parents[2]/'workspace'
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.blender-runtime-', dir=root) as temporary:
        directory = Path(temporary)
        containment = WorkerContainment()
        process = None
        runtime = None
        runtime_identity = None
        record = None
        request = {**request, 'request_id': secrets.token_hex(32), 'operation': operation,
                   'job_name': containment.name, 'result': str(directory/'result.json')}
        request.setdefault('outputs', {})
        try:
            request_path = directory/'request.json'
            request_path.write_text(json.dumps(request, allow_nan=False), encoding='utf-8')
            script_name = 'blender_runtime.py' if operation == 'probe' else 'blender_inspect.py'
            script = Path(__file__).resolve().parents[2]/'scripts'/script_name
            deadline = time.monotonic() + timeout
            process = subprocess.Popen(
                [str(path), '--background', '--factory-startup', '--disable-autoexec',
                 '--python-exit-code', '1', '--python', str(script), '--', str(request_path)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            while True:
                code = process.poll()
                if code is not None and code != 0:
                    raise RuntimeError(f'Blender launcher failed with exit code {code}; no inspection bundle published.')
                result_path = Path(request['result'])
                if result_path.is_file():
                    record = _completion(result_path, request)
                    identity = (record['pid'], tuple(record['runtime_version']), record['runtime_path'])
                    if runtime_identity is not None and identity != runtime_identity:
                        raise RuntimeError('Invalid Blender completion record: child identity changed.')
                    runtime_identity = identity
                    if runtime is None:
                        runtime = _runtime_handle(record['pid'])
                    if record['status'] == 'error':
                        raise RuntimeError('Blender child failed; no inspection bundle published. '+record['error'])
                    if record['status'] == 'success':
                        break
                    if runtime[1] and runtime[0].WaitForSingleObject(runtime[1], 0) == 0:
                        # The atomic terminal write may have raced the started read.
                        latest = _completion(result_path, request)
                        if latest['status'] == 'started':
                            raise RuntimeError('Blender child exited without completion; no inspection bundle published.')
                        continue
                if time.monotonic() >= deadline:
                    raise RuntimeError('Blender timed out without child completion; no inspection bundle published.')
                time.sleep(min(.05, max(0, deadline - time.monotonic())))
        finally:
            # Close before cleanup or publication, including when the launcher exited early.
            containment.close()
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            if runtime is not None and runtime[1]:
                kernel, handle = runtime
                try:
                    if kernel.WaitForSingleObject(handle, 5000) != 0:
                        raise RuntimeError('Owned Blender child did not stop during cleanup.')
                finally:
                    kernel.CloseHandle(handle)
        outputs = record.get('outputs')
        if not isinstance(outputs, dict) or set(outputs) != set(request['outputs']):
            raise RuntimeError('Invalid Blender completion output hashes.')
        for name, output in request['outputs'].items():
            digest = outputs[name]
            if (not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
                    or not Path(output).is_file()
                    or hashlib.sha256(Path(output).read_bytes()).hexdigest() != digest):
                raise RuntimeError('Blender completion output hash mismatch; no inspection bundle published.')
        return record


def _candidates():
    explicit = os.environ.get('BLENDER_PATH')
    if explicit:
        return [Path(explicit)]
    paths = []
    for name in ('blender', 'blender.exe', 'blender-launcher.exe'):
        found = shutil.which(name)
        if found:
            paths.append(Path(found))
    program_files = os.environ.get('ProgramFiles')
    if program_files:
        paths.extend(sorted((Path(program_files)/'Blender Foundation').glob('*/blender.exe')))
    local_appdata = os.environ.get('LOCALAPPDATA')
    if local_appdata:
        paths.append(Path(local_appdata)/'Microsoft/WindowsApps/blender-launcher.exe')
    # Keep alias paths intact: resolving one can point at an inaccessible package binary.
    unique = {}
    for path in paths:
        if path.is_file():
            unique.setdefault(os.path.normcase(os.path.abspath(path)), path.absolute())
    return list(unique.values())


def probe_blender():
    explicit = os.environ.get('BLENDER_PATH')
    if explicit and not Path(explicit).is_file():
        return {**compatibility(''), 'detail': 'Explicit BLENDER_PATH is unavailable; correct it without installing automatically.'}
    paths = _candidates()
    if not paths:
        return {**compatibility(''), 'detail': 'Blender not found. OpenSCAD previews remain available.'}
    deadline = time.monotonic() + PROBE_TIMEOUT_SECONDS
    result = None
    for path in paths:
        try:
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                raise RuntimeError('Blender probe timed out.')
            runtime = _run_blender(path, {}, operation='probe', timeout=remaining)
            version = '.'.join(map(str, runtime['runtime_version']))
            detected = {**compatibility('Blender '+version), 'path': str(path.absolute()),
                        'runtime_path': runtime['runtime_path'],
                        'detail': 'Actual Blender runtime checked; exact target required for automated inspection. No install or downgrade.'}
            if detected['compatible']:
                return detected
            # Report a real mismatched runtime ahead of an unavailable fallback.
            result = detected
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            if result is None or result.get('version') is None:
                result = {**compatibility(''), 'path': str(path.absolute()),
                          'detail': f'Blender runtime probe failed: {exc}'}
    return result


def _scale_report(path, expected, tolerance):
    try:
        report = json.loads(path.read_text(encoding='utf-8'))
        actual = report['actual_extents_mm']
        stated = report['expected_extents_mm']
        def vector(value):
            return (isinstance(value, list) and len(value) == 3
                    and all(type(number) in (int, float) and math.isfinite(number) for number in value))
        if (report.get('scale_verified') is not True or not vector(actual) or not vector(stated)
                or stated != expected or report.get('meters_per_stl_unit') != .001
                or any(abs(a-b) > tolerance for a,b in zip(actual, expected))):
            raise ValueError('untrusted scale or bounds')
        return report
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ValueError('Blender imported bounds failed millimeter-scale verification.') from None


def inspect_blender(manifest: Path, *, revision='r01'):
    tool = probe_blender()
    if not tool['compatible']:
        raise ValueError(tool['detail']+f" Target {TARGET}; detected {tool.get('version')}.")
    generation, scad, stl, spec, mesh = snapshot_generation(manifest)
    target = revision_directory(generation, 'blender', revision)
    manifest_hash = generation.manifest_binding.sha256
    with tempfile.TemporaryDirectory(prefix='.blender-inspection-', dir=generation.workspace_root) as temporary:
        staging = Path(temporary)
        (staging/'inspection.stl').write_bytes(stl)
        expected = [float(value) for value in mesh.extents_mm]
        tolerance = float(generation.spec.verification_policy.mesh_bounds_tolerance_mm)
        outputs = {name: str(staging/name) for name in ('inspection.stl', 'inspection.blend', 'scale-check.json')}
        request = {'input': outputs['inspection.stl'], 'scene': outputs['inspection.blend'],
                   'report': outputs['scale-check.json'], 'outputs': outputs,
                   'input_sha256': hashlib.sha256(stl).hexdigest(),
                   'expected_extents_mm': expected, 'tolerance_mm': tolerance,
                   'required_version': [5, 2, 2]}
        runtime = _run_blender(tool['path'], request, operation='inspection',
                               timeout=INSPECTION_TIMEOUT_SECONDS, workspace_root=generation.workspace_root)
        if runtime['runtime_version'] != [5, 2, 2]:
            raise ValueError('Blender runtime changed; exact target required for inspection.')
        if hashlib.sha256((staging/'inspection.stl').read_bytes()).hexdigest() != request['input_sha256']:
            raise ValueError('Inspection STL changed; no inspection bundle published.')
        report = _scale_report(staging/'scale-check.json', expected, tolerance)
        if hashlib.sha256(manifest.read_bytes()).hexdigest() != manifest_hash:
            raise ValueError('Source manifest changed during Blender inspection; no inspection bundle published.')
        current, current_scad, current_stl, current_spec, _ = snapshot_generation(manifest)
        if current.manifest_binding.sha256 != manifest_hash or (current_scad, current_stl, current_spec) != (scad, stl, spec):
            raise ValueError('Source artifacts changed during Blender inspection; no inspection bundle published.')
        tool = {**tool, 'version': '.'.join(map(str, runtime['runtime_version'])),
                'runtime_path': runtime['runtime_path']}
        record = {'blender': tool, 'source_manifest_sha256': manifest_hash,
                  'stl_sha256': request['input_sha256'], 'scale': report,
                  'visual_review': 'pending', 'physical_fit': 'not_confirmed',
                  'files': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in staging.iterdir()}}
        (staging/'inspection-manifest.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
        publish_bundle(staging, target, manifest_name='inspection-manifest.json')
    return target
