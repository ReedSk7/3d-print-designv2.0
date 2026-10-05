"""Store-style broker children must die with their invocation's adapter worker."""
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]


def wait_for_file(path, process, log, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file():
            try:
                json.loads(path.read_text())
            except (ValueError, OSError):
                pass
            else:
                return
        if process.poll() is not None:
            pytest.fail(f'Worker stopped before ownership handshake: {log.read_text()}')
        time.sleep(.02)
    pytest.fail(f'Ownership handshake timed out: {log.read_text()}')


@pytest.mark.skipif(os.name != 'nt', reason='Windows named job ownership')
def test_store_broker_child_dies_when_adapter_worker_is_cancelled(tmp_path):
    # The broker is launched by this test, independently of the worker. Killing
    # the worker's process tree therefore cannot reach the broker's child.
    launch = tmp_path / 'launch.json'
    ready = tmp_path / 'child-ready.json'
    worker_ready = tmp_path / 'worker-ready.json'
    output = tmp_path / 'late-inspection.blend'
    log_path = tmp_path / 'worker.log'
    child_script = tmp_path / 'broker-child.py'
    child_script.write_text('''import json,os,runpy,sys,time,types
from pathlib import Path
runtime,request,ready,output=sys.argv[1:]
bpy=types.ModuleType('bpy')
bpy.app=types.SimpleNamespace(version=(5,2,2),version_string='5.2.2',binary_path=sys.executable)
sys.modules['bpy']=bpy
sys.argv=['blender','--',request]
def delayed_output(*args,**kwargs):
    Path(ready).write_text(json.dumps({'pid':os.getpid()}))
    time.sleep(30)
    Path(output).write_bytes(b'late scene from cancelled invocation')
runpy.run_path(runtime)['run'](delayed_output)
''', encoding='utf-8')
    broker_script = tmp_path / 'broker.py'
    broker_script.write_text('''import json,subprocess,sys,time
from pathlib import Path
launch,child,runtime,ready,output=sys.argv[1:]
while not Path(launch).is_file(): time.sleep(.02)
command=json.loads(Path(launch).read_text())['command']
request=command[command.index('--')+1]
process=subprocess.Popen([sys.executable,'-B',child,runtime,request,ready,output],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
while True: time.sleep(.1)
''', encoding='utf-8')
    worker_script = tmp_path / 'worker.py'
    worker_script.write_text('''import json,os,sys
from pathlib import Path
root,launch,ready,output,workspace=sys.argv[1:]
sys.path.insert(0,root)
import core.workshop.blender as blender
class EarlyAlias:
    returncode=0
    stdout=None
    stderr=None
    def __init__(self,command,**kwargs):
        self.pid=os.getpid()
        pending=Path(launch).with_suffix('.new')
        pending.write_text(json.dumps({'command':command}))
        pending.replace(launch)
    def poll(self): return 0
    def wait(self,timeout=None): return 0
    def terminate(self): pass
    def kill(self): pass
blender.subprocess.Popen=EarlyAlias
Path(ready).write_text(json.dumps({'pid':os.getpid()}))
blender._run_blender('store-alias',{'outputs':{'inspection.blend':output}},operation='probe',timeout=10,workspace_root=Path(workspace))
''', encoding='utf-8')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    kernel.TerminateProcess.restype = ctypes.c_int
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel.WaitForSingleObject.restype = ctypes.c_ulong
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handles = []
    broker = worker = None
    with log_path.open('wb') as log:
        try:
            # Use the base interpreter for the stdlib-only broker and fake bpy
            # child; the worker uses the same dependency environment as pytest.
            broker = subprocess.Popen(
                [sys._base_executable, '-B', str(broker_script), str(launch),
                 str(child_script), str(ROOT / 'scripts/blender_runtime.py'),
                 str(ready), str(output)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW)
            worker = subprocess.Popen(
                [sys.executable, '-B', str(worker_script), str(ROOT), str(launch),
                 str(worker_ready), str(output), str(tmp_path)],
                stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW)
            wait_for_file(worker_ready, worker, log_path)
            wait_for_file(ready, worker, log_path)
            worker_pid = json.loads(worker_ready.read_text())['pid']
            child_pid = json.loads(ready.read_text())['pid']
            worker_handle = kernel.OpenProcess(0x100001, False, worker_pid)
            if worker_handle:
                handles.append(worker_handle)
            child_handle = kernel.OpenProcess(0x100001, False, child_pid)
            if child_handle:
                handles.append(child_handle)
            assert worker_handle and child_handle, 'Capture both real process handles before cancellation.'
            assert not output.exists()
            assert kernel.TerminateProcess(worker_handle, 1)
            assert kernel.WaitForSingleObject(worker_handle, 5000) == 0
            # Closing the invocation owner's handles must kill this independently
            # brokered child; the broker itself remains alive.
            assert kernel.WaitForSingleObject(child_handle, 5000) == 0
            assert broker.poll() is None
            assert not output.exists(), 'Cancelled Blender must not write its delayed output.'
            worker.wait(timeout=5)
        finally:
            for handle in handles:
                if kernel.WaitForSingleObject(handle, 0) != 0:
                    kernel.TerminateProcess(handle, 1)
                    kernel.WaitForSingleObject(handle, 5000)
                kernel.CloseHandle(handle)
            if worker and worker.poll() is None:
                worker.kill()
                worker.wait(timeout=5)
            if broker and broker.poll() is None:
                broker.kill()
                broker.wait(timeout=5)
