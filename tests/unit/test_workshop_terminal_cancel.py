"""Accepted cancellation wins over a concurrently finishing worker result."""
import json
import subprocess
import threading
import time
import urllib.request
from pathlib import Path
import pytest
from core.workshop.server import make_server

@pytest.mark.parametrize('read_fails',[False,True])
def test_cancel_during_result_read_remains_cancelled(tmp_path,monkeypatch,read_fails):
    import core.workshop.server as module
    class Containment:
        name='Local\\PrintWorkshop-synthetic-race-test'
        def close(self): pass
    class Worker:
        pid=-1
        def __init__(self,args,**kwargs): Path(args[-1]).write_text(json.dumps({'result':{'output':'synthetic worker result'}}))
        def wait(self,timeout=None): return 0
        def terminate(self): pass
    monkeypatch.setattr(module,'WorkerContainment',Containment)
    monkeypatch.setattr(module.subprocess,'Popen',Worker)
    original_run=module.subprocess.run
    monkeypatch.setattr(module.subprocess,'run',lambda args,**kwargs:subprocess.CompletedProcess(args,0,b'',b'') if args[0]=='taskkill' else original_run(args,**kwargs))
    server=make_server(tmp_path,0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    token=json.load(urllib.request.urlopen(base+'/api/session'))['token']
    def post(path,payload):
        return json.load(urllib.request.urlopen(urllib.request.Request(base+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','X-Workshop-Token':token})))
    original_read=Path.read_text;cancel_responses=[]
    def read(path,*args,**kwargs):
        content=original_read(path,*args,**kwargs)
        if path.name=='result.json' and path.parent.parent.name=='jobs':
            cancel_responses.append(post('/api/cancel',{'job_id':path.parent.name}))
            if read_fails: raise OSError('synthetic result read failure')
        return content
    monkeypatch.setattr(Path,'read_text',read)
    try:
        job=post('/api/actions',{'action':'blender','payload':{}})
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            status=json.load(urllib.request.urlopen(base+'/api/jobs/'+job['job_id']))
            if status['status'] not in {'queued','running','cancel_requested'}: break
            time.sleep(.01)
        assert cancel_responses==[{'cancel_requested':True,'note':'Inspect project status afterward; publication may have completed just before cancellation.'}]
        assert status['status']=='cancelled',status
        assert 'result' not in status
    finally:
        server.shutdown();server.server_close();thread.join()
