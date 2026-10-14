"""Store launchers may finish before their owned Blender runtime does."""
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

import core.workshop.blender as blender


pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Windows Store process ownership')
REPO = Path(__file__).resolve().parents[2]


def wait_for_exit(pid):
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x100000, False, pid)
    if handle:
        try:
            assert kernel.WaitForSingleObject(handle, 5000) == 0, 'Owned Blender child survived cleanup'
        finally:
            kernel.CloseHandle(handle)


@pytest.fixture
def launcher(tmp_path, monkeypatch):
    """Replace only the Blender executable with a real asynchronous Python launcher."""
    executable = tmp_path/'Microsoft/WindowsApps/blender-launcher.exe'
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b'synthetic test alias')
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    monkeypatch.setenv('BLENDER_PATH', str(executable))
    pid_log = tmp_path/'child-pids.jsonl'
    child = tmp_path/'fake_blender_child.py'
    child.write_text('''import hashlib,json,os,sys,time,types
from pathlib import Path
repo,request_path,mode,pid_log=sys.argv[1:]
sys.path.insert(0,repo)
sys.path.insert(0,str(Path(repo)/'scripts'))
request=json.loads(Path(request_path).read_text())
sys.argv=['fake-blender','--',request_path]
with Path(pid_log).open('a') as stream: stream.write(json.dumps({'pid':os.getpid(),'mode':mode})+'\\n')
version=(5,2,1) if mode=='mismatch' else (5,2,2)
sys.modules['bpy']=types.SimpleNamespace(app=types.SimpleNamespace(version=version,binary_path='fake-runtime-blender.exe'))
if mode in {'malformed','wrong_nonce','wrong_hash','no_completion'}:
    from core.workshop.ownership import join_worker_job
    join_worker_job(request['job_name'])
    if mode=='no_completion': time.sleep(30)
    else:
        record={'protocol':1,'request_id':request['request_id'],'operation':request['operation'],'job_name':request['job_name'],'pid':os.getpid(),'runtime_version':list(version),'runtime_path':'fake-runtime-blender.exe','status':'success','outputs':{}}
        if mode=='wrong_nonce': record['request_id']='another-request'
        if mode=='wrong_hash':
            for name,path in request['outputs'].items(): Path(path).write_text('untrusted output'); record['outputs'][name]='0'*64
        Path(request['result']).write_text('{invalid' if mode=='malformed' else json.dumps(record))
        time.sleep(30)
else:
    from blender_runtime import run
    def action(request):
        time.sleep(.2)
        if mode=='child_failure': raise RuntimeError('synthetic child failure')
        if mode=='child_crash': os._exit(7)
        if request['operation']=='inspection':
            Path(request['scene']).write_bytes(b'synthetic scene bytes')
            actual=[10,12,14] if mode!='bad_bounds' else [float('nan'),12,14]
            Path(request['report']).write_text(json.dumps({'scale_verified':True,'actual_extents_mm':actual,'expected_extents_mm':[10,12,14],'meters_per_stl_unit':.001}))
            if mode=='modified_input': Path(request['input']).write_bytes(b'modified STL')
    run(action)
''', encoding='utf-8')
    script = tmp_path/'fake_store_launcher.py'
    script.write_text('''import subprocess,sys
repo,child,mode,pid_log,*args=sys.argv[1:]
if mode=='launcher_failure':
    print('synthetic launcher failure',file=sys.stderr); raise SystemExit(7)
if '--version' in args:
    print('Blender 5.2.2'); raise SystemExit(0)
if mode=='silent_exit': raise SystemExit(0)
request=args[args.index('--')+1]
subprocess.Popen([sys.executable,'-B',child,repo,request,mode,pid_log],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
''', encoding='utf-8')
    real_popen = subprocess.Popen
    mode = {'value':'success'}
    def popen(arguments, *args, **kwargs):
        if str(arguments[0]) == str(executable):
            arguments = [sys.executable, '-B', str(script), str(REPO), str(child), mode['value'], str(pid_log), *arguments[1:]]
        return real_popen(arguments, *args, **kwargs)
    monkeypatch.setattr(blender.subprocess, 'Popen', popen)
    yield mode, executable, pid_log


@pytest.fixture
def version(tmp_path, monkeypatch, launcher):
    workspace = tmp_path/'workspace'; directory = workspace/'synthetic/v01'
    directory.mkdir(parents=True)
    manifest = directory/'artifact-manifest.json'; manifest.write_text('{"fixture": true}')
    generation = SimpleNamespace(workspace_root=workspace, version_directory=directory,
        manifest_binding=SimpleNamespace(sha256=hashlib.sha256(manifest.read_bytes()).hexdigest()),
        spec=SimpleNamespace(verification_policy=SimpleNamespace(mesh_bounds_tolerance_mm=.05)))
    monkeypatch.setattr(blender, 'snapshot_generation', lambda path: (generation,b'scad',b'original immutable stl',b'spec',SimpleNamespace(extents_mm=(10,12,14))))
    monkeypatch.setattr(blender, 'probe_blender', lambda: {'target':'5.2.2','version':'5.2.2','compatible':True,'optional':True,'path':str(launcher[1]),'detail':'synthetic executable'})
    return manifest, directory


def test_store_alias_discovery_uses_actual_runtime(launcher, monkeypatch):
    monkeypatch.delenv('BLENDER_PATH')
    monkeypatch.setattr(blender.shutil, 'which', lambda _: None)
    monkeypatch.setenv('ProgramFiles', str(launcher[1].parents[2]/'empty-program-files'))
    result = blender.probe_blender()
    assert result['compatible'], result
    assert result['version'] == '5.2.2'
    assert result['path'] == str(launcher[1])
    assert result['runtime_path'] == 'fake-runtime-blender.exe'


def test_runtime_version_outranks_launcher_version_text(launcher):
    launcher[0]['value'] = 'mismatch'
    result = blender.probe_blender()
    assert not result['compatible'], result
    assert result['version'] == '5.2.1'


def test_async_launcher_waits_for_finalized_scene(version, launcher):
    manifest, directory = version
    output = blender.inspect_blender(manifest)
    record = json.loads((output/'inspection-manifest.json').read_text())
    assert (output/'inspection.blend').read_bytes() == b'synthetic scene bytes'
    assert record['files'] == {name: hashlib.sha256((output/name).read_bytes()).hexdigest() for name in ('inspection.stl','inspection.blend','scale-check.json')}
    assert record['stl_sha256'] == hashlib.sha256(b'original immutable stl').hexdigest()
    assert record['blender']['version'] == '5.2.2'
    assert record['visual_review'] == 'pending'
    assert record['physical_fit'] == 'not_confirmed'
    assert not list(output.glob('*request*'))
    wait_for_exit(json.loads(launcher[2].read_text().splitlines()[-1])['pid'])


@pytest.mark.parametrize('mode,match', [
    ('launcher_failure','launcher'), ('child_failure','synthetic child failure'),
    ('malformed','completion'), ('wrong_nonce','completion'), ('wrong_hash','hash'),
    ('bad_bounds','bounds'),
    ('modified_input','STL changed'), ('mismatch','exact target'),
])
def test_failed_child_never_publishes(version, launcher, mode, match):
    launcher[0]['value'] = mode
    manifest, directory = version
    with pytest.raises((ValueError, RuntimeError), match=match): blender.inspect_blender(manifest)
    assert not (directory/'blender/r01').exists()
    if launcher[2].exists(): wait_for_exit(json.loads(launcher[2].read_text().splitlines()[-1])['pid'])


def test_probe_timeout_terminates_owned_child(launcher, monkeypatch):
    launcher[0]['value'] = 'no_completion'
    monkeypatch.setattr(blender, 'PROBE_TIMEOUT_SECONDS', .5, raising=False)
    result = blender.probe_blender()
    assert not result['compatible'], result
    assert 'timed out' in result['detail'].lower()
    wait_for_exit(json.loads(launcher[2].read_text().splitlines()[-1])['pid'])


def test_inspection_timeout_terminates_owned_child(version, launcher, monkeypatch):
    launcher[0]['value'] = 'no_completion'
    monkeypatch.setattr(blender, 'INSPECTION_TIMEOUT_SECONDS', .5, raising=False)
    manifest, directory = version
    with pytest.raises(RuntimeError, match='timed out'): blender.inspect_blender(manifest)
    assert not (directory/'blender/r01').exists()
    wait_for_exit(json.loads(launcher[2].read_text().splitlines()[-1])['pid'])


def test_completed_revision_cannot_be_overwritten(version, launcher):
    manifest, _ = version
    output = blender.inspect_blender(manifest)
    before = {path.name: path.read_bytes() for path in output.iterdir()}
    with pytest.raises(FileExistsError): blender.inspect_blender(manifest)
    assert {path.name: path.read_bytes() for path in output.iterdir()} == before


def test_zero_launcher_exit_without_child_is_not_success(version, launcher, monkeypatch):
    launcher[0]['value'] = 'silent_exit'
    monkeypatch.setattr(blender, 'INSPECTION_TIMEOUT_SECONDS', .5, raising=False)
    manifest, directory = version
    with pytest.raises(RuntimeError, match='timed out'): blender.inspect_blender(manifest)
    assert not (directory/'blender/r01').exists()


def test_started_child_crash_is_reported_without_waiting_for_timeout(version, launcher, monkeypatch):
    launcher[0]['value'] = 'child_crash'
    monkeypatch.setattr(blender, 'INSPECTION_TIMEOUT_SECONDS', .75, raising=False)
    manifest, directory = version
    with pytest.raises(RuntimeError, match='child exited without completion'): blender.inspect_blender(manifest)
    assert not (directory/'blender/r01').exists()


def test_manifest_changed_during_async_inspection_is_not_published(version):
    import threading
    manifest, directory = version
    def mutate(): manifest.write_text('{"fixture": "changed during inspection"}')
    mutation = threading.Timer(.1, mutate); mutation.start()
    try:
        with pytest.raises(ValueError, match='Source manifest changed'): blender.inspect_blender(manifest)
    finally:
        mutation.join()
    assert not (directory/'blender/r01').exists()


def test_changed_generation_stops_before_blender_launch(version, launcher, monkeypatch):
    manifest, directory = version
    def changed(path): raise ValueError('Artifact changed during review: inspection.stl')
    monkeypatch.setattr(blender, 'snapshot_generation', changed)
    with pytest.raises(ValueError, match='Artifact changed'): blender.inspect_blender(manifest)
    assert not launcher[2].exists()
    assert not (directory/'blender/r01').exists()
