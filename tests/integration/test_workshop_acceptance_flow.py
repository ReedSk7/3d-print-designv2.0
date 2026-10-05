"""Actual OpenSCAD fixtures; optional Blender runtime is simulated explicitly."""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
import pytest
from core.workshop.service import Workshop
ROOT=Path(__file__).parents[2]

@pytest.fixture
def generated(tmp_path):
    workshop=Workshop(tmp_path)
    document=json.loads((ROOT/'examples/specs/bushing_example.json').read_text())
    saved=workshop.save_spec(document)
    result=workshop.action('generate',saved)
    return workshop,result

def test_visual_review_is_bound_immutable_and_not_fit(generated):
    workshop,result=generated
    preview=workshop.action('preview',{**result,'revision':'r01'})
    payload=dict(preview_manifest=preview['output'],expected_preview_manifest_sha256=preview['preview_manifest_sha256'],personally_inspected_images=True,reviewer_kind='agent',reviewed_by='Synthetic test harness',observations='Automated fixture only; no actual human review asserted.',remaining_concerns='Physical fit remains unverified.')
    # This test validates the record protocol, never asserts actual visual acceptance.
    review=workshop.action('record_visual',payload)
    assert review['physical_fit']=='not_confirmed'
    with pytest.raises(FileExistsError): workshop.action('record_visual',payload)
    payload['reviewer_kind']='owner'; payload['expected_preview_manifest_sha256']='0'*64
    with pytest.raises(ValueError,match='SHA-256'): workshop.action('record_visual',payload)

def test_optional_blender_scale_failure_never_publishes(generated,monkeypatch):
    import core.workshop.blender as blender
    workshop,result=generated
    monkeypatch.setattr(blender,'probe_blender',lambda:{'compatible':True,'path':'simulated','version':'5.2.2'})
    def fake_run(path,request,*,operation,**kwargs):
        assert operation=='inspection'
        Path(request['scene']).write_bytes(b'simulated scene')
        Path(request['report']).write_text(json.dumps({'scale_verified':False}))
        return {'protocol':1,'request_id':'synthetic-test-boundary','operation':operation,
                'job_name':'synthetic-invocation','pid':os.getpid(),'runtime_version':[5,2,2],
                'runtime_path':'synthetic-runtime','status':'success',
                'outputs':{name:hashlib.sha256(Path(output).read_bytes()).hexdigest() for name,output in request['outputs'].items()}}
    monkeypatch.setattr(blender,'_run_blender',fake_run)
    with pytest.raises(ValueError,match='scale'): workshop.action('blender',{**result,'revision':'r01'})
    assert not (workshop.workspace/'bushing_example/v01/blender/r01').exists()

def test_optional_blender_no_overwrite_and_source_tamper(generated,monkeypatch):
    import core.workshop.blender as blender
    workshop,result=generated
    monkeypatch.setattr(blender,'probe_blender',lambda:{'compatible':True,'path':'simulated','version':'5.2.2'})
    def fake_run(path,request,*,operation,**kwargs):
        assert operation=='inspection'
        Path(request['scene']).write_bytes(b'simulated scene')
        Path(request['report']).write_text(json.dumps({'scale_verified':True,
            'actual_extents_mm':request['expected_extents_mm'],
            'expected_extents_mm':request['expected_extents_mm'],'meters_per_stl_unit':.001}))
        return {'protocol':1,'request_id':'synthetic-test-boundary','operation':operation,
                'job_name':'synthetic-invocation','pid':os.getpid(),'runtime_version':[5,2,2],
                'runtime_path':'synthetic-runtime','status':'success',
                'outputs':{name:hashlib.sha256(Path(output).read_bytes()).hexdigest() for name,output in request['outputs'].items()}}
    monkeypatch.setattr(blender,'_run_blender',fake_run)
    workshop.action('blender',{**result,'revision':'r01'})
    with pytest.raises(FileExistsError): workshop.action('blender',{**result,'revision':'r01'})
    source=next((workshop.workspace/'bushing_example/v01').glob('*.scad'))
    source.write_text(source.read_text()+'\n// changed')
    with pytest.raises(ValueError): workshop.action('blender',{**result,'revision':'r02'})

@pytest.mark.skipif(os.name!='nt',reason='Windows bridge ownership')
def test_bridge_termination_during_generation_cannot_publish_after_restart(tmp_path):
    # Real bridge/worker startup. Publication before termination is legitimate;
    # publication after restarted ownership is acquired must never occur.
    script=tmp_path/'bridge.py'
    script.write_text("import sys,threading,json; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from core.workshop.server import make_server; server=make_server(Path(sys.argv[2]),0); print(server.server_port,flush=True); server.serve_forever()")
    process=subprocess.Popen([sys.executable,'-B',str(script),str(ROOT),str(tmp_path/'project')],stdout=subprocess.PIPE,text=True)
    server=None
    try:
        port=int(process.stdout.readline()); base=f'http://127.0.0.1:{port}'
        session=json.load(urllib.request.urlopen(base+'/api/session')); token=session['token']
        def post(path,data): return json.load(urllib.request.urlopen(urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Workshop-Token':token})))
        document=json.loads((ROOT/'examples/specs/bushing_example.json').read_text())
        saved=post('/api/specs',{'document':document}); job=post('/api/actions',{'action':'generate','payload':saved})
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            state=json.load(urllib.request.urlopen(base+'/api/jobs/'+job['job_id']))
            if state['status']=='running': break
            time.sleep(.01)
        assert state['status']=='running'
        # Venv Windows Python can be a wrapper: terminate the actual launched
        # bridge PID, deliberately without /T to exercise kill-on-close ownership.
        subprocess.run(['taskkill','/PID',str(session['pid']),'/F'],capture_output=True,check=True)
        process.wait(timeout=5)
        # A restarted bridge reacquires the OS-released lock and exposes interruption.
        from core.workshop.server import make_server
        server=make_server(tmp_path/'project',0)
        from core.workshop.jobs import JobStore
        state=JobStore(tmp_path/'project/owner-validation/local/workshop/jobs.json').records[job['job_id']]
        assert state['status']=='interrupted'
        before=list((tmp_path/'project/workspace').glob('**/artifact-manifest.json'))
        time.sleep(1)
        assert list((tmp_path/'project/workspace').glob('**/artifact-manifest.json'))==before
    finally:
        if process.poll() is None: process.kill(); process.wait(timeout=5)
        if server: server.server_close()
