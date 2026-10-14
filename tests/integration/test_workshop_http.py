import json
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
import pytest
from core.workshop.server import make_server

def test_readiness_is_bound_to_launch_instance(tmp_path):
    server=make_server(tmp_path,0,instance_id='test-launch')
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        session=json.load(urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/api/session'))
        assert session['instance_id']=='test-launch'
    finally: server.shutdown(); server.server_close(); server.executor.shutdown(); thread.join()

@pytest.mark.windows_worker
def test_http_generate_job_produces_real_artifacts(tmp_path):
    server=make_server(tmp_path,0); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        token=json.load(urllib.request.urlopen(base+'/api/session'))['token']
        def post(path,data):
            return json.load(urllib.request.urlopen(urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Workshop-Token':token})))
        document=json.loads((Path(__file__).parents[2]/'examples/specs/bushing_example.json').read_text())
        saved=post('/api/specs',{'document':document})
        job=post('/api/actions',{'action':'generate','payload':saved})
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            result=json.load(urllib.request.urlopen(base+'/api/jobs/'+job['job_id']))
            if result['status'] in {'complete','failed'}: break
            time.sleep(.1)
        assert result['status']=='complete',result
        assert (tmp_path/result['result']['manifest']).is_file()
        history=json.load(urllib.request.urlopen(base+'/api/jobs'))
        assert history[0]['job_id']==job['job_id']
        assert history[0]['status']=='complete'
    finally: server.shutdown(); server.server_close(); server.executor.shutdown(); thread.join()

@pytest.mark.windows_worker
def test_cancelled_job_is_not_reported_complete(tmp_path):
    server=make_server(tmp_path,0); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        token=json.load(urllib.request.urlopen(base+'/api/session'))['token']
        def post(path,data):
            return json.load(urllib.request.urlopen(urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Workshop-Token':token})))
        document=json.loads((Path(__file__).parents[2]/'examples/specs/bushing_example.json').read_text())
        saved=post('/api/specs',{'document':document})
        job=post('/api/actions',{'action':'generate','payload':saved})
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            result=json.load(urllib.request.urlopen(base+'/api/jobs/'+job['job_id']))
            if result['status']!='queued': break
            time.sleep(.01)
        assert result['status']=='running',result
        post('/api/cancel',job)
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            result=json.load(urllib.request.urlopen(base+'/api/jobs/'+job['job_id']))
            if result['status'] not in {'queued','running','cancel_requested'}: break
            time.sleep(.1)
        assert result['status']=='cancelled',result
    finally: server.shutdown(); server.server_close(); server.executor.shutdown(); thread.join()

def test_changed_source_cannot_be_downloaded(tmp_path):
    from core.workshop.service import Workshop
    workshop=Workshop(tmp_path)
    document=json.loads((Path(__file__).parents[2]/'examples/specs/bushing_example.json').read_text())
    saved=workshop.save_spec(document); generated=workshop.action('generate',saved)
    source=next((tmp_path/'workspace/bushing_example/v01').glob('*.scad'))
    source.write_text(source.read_text()+'\n// changed')
    server=make_server(tmp_path,0); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        url=f'http://127.0.0.1:{server.server_port}/artifact/'+source.relative_to(tmp_path/'workspace').as_posix()
        try: urllib.request.urlopen(url)
        except urllib.error.HTTPError as exc: assert exc.code==400
        else: raise AssertionError('Tampered source was downloadable')
    finally: server.shutdown(); server.server_close(); server.executor.shutdown(); thread.join()

def test_local_http_workflow_and_cross_origin_block(tmp_path):
    server=make_server(tmp_path,0)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        token=json.load(urllib.request.urlopen(base+'/api/session'))['token']
        document=json.loads((Path(__file__).parents[2]/'examples/specs/bushing_example.json').read_text())
        request=urllib.request.Request(base+'/api/specs',data=json.dumps({'document':document}).encode(),headers={'Content-Type':'application/json','X-Workshop-Token':token})
        assert urllib.request.urlopen(request).status==201
        assert json.load(urllib.request.urlopen(base+'/api/projects'))[0]['name']=='Bushing Example'
        request.add_header('Origin','https://evil.example')
        try: urllib.request.urlopen(request)
        except urllib.error.HTTPError as exc: assert exc.code==403
        else: raise AssertionError('Cross-origin mutation allowed')
    finally: server.shutdown(); server.server_close(); server.executor.shutdown(); thread.join()
