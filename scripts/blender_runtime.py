"""Blender-side ownership and atomic completion for a single local invocation."""
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.workshop.ownership import join_worker_job


def _write_result(path, record):
    temporary = path.with_suffix('.new')
    temporary.write_text(json.dumps(record, allow_nan=False), encoding='utf-8')
    os.replace(temporary, path)


def run(action=None):
    request_path = Path(sys.argv[sys.argv.index('--') + 1])
    request = json.loads(request_path.read_text(encoding='utf-8'))
    # The broker child may not inherit its launcher's job. Join before any work.
    # join_worker_job closes the child handle; only the adapter owns the lifetime.
    join_worker_job(request['job_name'])
    import bpy
    record = {
        'protocol': 1, 'request_id': request['request_id'],
        'operation': request['operation'], 'job_name': request['job_name'],
        'pid': os.getpid(), 'runtime_version': list(bpy.app.version),
        'runtime_path': bpy.app.binary_path, 'status': 'started',
    }
    result = Path(request['result'])
    _write_result(result, record)
    try:
        expected = request.get('required_version')
        if expected is not None and list(bpy.app.version) != expected:
            raise RuntimeError('Blender runtime version changed; exact target required.')
        if action is not None:
            action(request)
        # Save operations have returned. Hash every finalized file before success.
        outputs = {name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                   for name, path in request.get('outputs', {}).items()}
        _write_result(result, {**record, 'status': 'success', 'outputs': outputs})
    except Exception as exc:
        _write_result(result, {**record, 'status': 'error',
                               'error': f'{type(exc).__name__}: {exc}'[:2000]})
        raise


if __name__ == '__main__':
    run()
