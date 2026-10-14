import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

def test_workspace_lock_excludes_second_bridge(tmp_path):
    from core.workshop.ownership import WorkspaceLock
    first=WorkspaceLock(tmp_path/'bridge.lock')
    try:
        with pytest.raises(RuntimeError,match='already running'): WorkspaceLock(tmp_path/'bridge.lock')
    finally: first.close()
    second=WorkspaceLock(tmp_path/'bridge.lock'); second.close()

@pytest.mark.windows_worker
def test_bridge_job_close_kills_worker_and_descendant(tmp_path):
    from core.workshop.ownership import WorkerContainment
    owner=WorkerContainment()
    ready=tmp_path/'ready'
    script="from core.workshop.ownership import join_worker_job; import subprocess,sys,time; from pathlib import Path; join_worker_job(sys.argv[1]); child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); Path(sys.argv[2]).write_text(str(child.pid)); time.sleep(30)"
    process=subprocess.Popen([sys.executable,'-B','-c',script,owner.name,str(ready)])
    try:
        import time
        deadline=time.monotonic()+10
        while not ready.exists() and time.monotonic()<deadline:
            if process.poll() is not None: pytest.fail('Worker failed before ownership handshake')
            time.sleep(.05)
        assert ready.exists()
        child_pid=int(ready.read_text())
        owner.close()
        process.wait(timeout=5)
        # Opening the descendant for waiting establishes it also terminated.
        import ctypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.restype=ctypes.c_void_p
        handle=kernel.OpenProcess(0x100000,False,child_pid)
        if handle:
            kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
            kernel.CloseHandle.argtypes=[ctypes.c_void_p]
            assert kernel.WaitForSingleObject(handle,5000)==0
            kernel.CloseHandle(handle)
    finally:
        owner.close()
        if process.poll() is None: process.kill()

def test_recording_propagates_recording_time_hash(tmp_path,monkeypatch):
    from core.workshop.service import Workshop
    import core.evidence.service as evidence
    output=tmp_path/'workspace/sample/v01/physical-fit.json'; output.parent.mkdir(parents=True); output.write_text('{}')
    monkeypatch.setattr(evidence,'record_physical_fit',lambda *args,**kwargs:output)
    anchors={}
    def inspect(directory,**kwargs): anchors.update(kwargs); return {'physical_fit_claim_allowed':True}
    monkeypatch.setattr(evidence,'inspect_project_status',inspect)
    result=Workshop(tmp_path).action('record_physical',{'manifest':'workspace/sample/v01/artifact-manifest.json','owner_performed_actual_test':True,'record':dict(expected_manifest_sha256='x',confirmed_by='Owner',confirmed_at='2026-10-04',interface_results=[],notes='Actual test')})
    assert anchors['expected_physical_evidence_sha256']==result['evidence_sha256']

def test_visual_review_requires_actual_inspection(tmp_path):
    from core.workshop.service import Workshop
    with pytest.raises(ValueError,match='inspected'):
        Workshop(tmp_path).action('record_visual',{})

def test_startup_checks_expose_missing_assets(tmp_path,monkeypatch):
    import core.workshop.readiness as readiness
    monkeypatch.setattr(readiness,'dependency_checks',lambda root:[])
    report=readiness.check_readiness(tmp_path)
    assert not report['ready']
    assert any(item['name']=='app assets' and item['status']=='fail' for item in report['checks'])
