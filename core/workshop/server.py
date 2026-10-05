"""Loopback-only server with origin/token guards and one bounded action queue."""
from __future__ import annotations
import json
import mimetypes
import secrets
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .service import Workshop, safe_path
from .jobs import JobStore
from .ownership import WorkspaceLock, WorkerContainment

def authorized(host,origin,supplied,token,port):
    return host==f'127.0.0.1:{port}' and origin in (None,f'http://127.0.0.1:{port}') and bool(supplied) and secrets.compare_digest(supplied,token)

def make_server(root: Path,port=8765,*,instance_id=None):
    workshop=Workshop(root); ownership=WorkspaceLock(safe_path(workshop.local,'bridge.lock'))
    token=secrets.token_urlsafe(32); executor=ThreadPoolExecutor(max_workers=1)
    store=JobStore(safe_path(workshop.local,'jobs.json')); jobs=store.records; lock=threading.RLock(); processes={}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def send(self,status,data,content_type='application/json'):
            body=json.dumps(data,default=str).encode() if content_type=='application/json' else data
            self.send_response(status); self.send_header('Content-Type',content_type)
            self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
            self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        def guarded(self,mutation=False):
            origin=self.headers.get('Origin'); host=self.headers.get('Host')
            if host!=f'127.0.0.1:{self.server.server_port}' or origin not in (None,f'http://127.0.0.1:{self.server.server_port}'):
                self.send(403,{'error':'Local origin required.'}); return False
            if mutation and not authorized(host,origin,self.headers.get('X-Workshop-Token',''),token,self.server.server_port):
                self.send(403,{'error':'Workshop token required.'}); return False
            return True
        def do_GET(self):
            if not self.guarded(): return
            try:
                if self.path=='/api/session': self.send(200,{'token':token,'pid':os.getpid(),'instance_id':instance_id}); return
                if self.path=='/api/projects': self.send(200,workshop.catalog()); return
                if self.path=='/api/jobs':
                    with lock: self.send(200,[{'job_id':key,**value} for key,value in reversed(list(jobs.items()))]); return
                if self.path=='/api/templates':
                    self.send(200,{family:json.loads((root/f'examples/specs/{family}_example.json').read_text()) for family in ('bushing','round_adapter','flange_plate')}); return
                if self.path=='/api/blender':
                    from .blender import probe_blender
                    self.send(200,probe_blender()); return
                if self.path.startswith('/api/jobs/'):
                    with lock: job=jobs.get(self.path.rsplit('/',1)[-1])
                    if not job: raise ValueError('Unknown job.')
                    self.send(200,job); return
                if self.path.startswith('/local-legacy/'):
                    from urllib.parse import unquote
                    path=safe_path(workshop.local/'legacy',unquote(self.path[len('/local-legacy/'):]))
                    if path.suffix.lower()!='.scad': raise ValueError('Legacy access exposes SCAD source only.')
                elif self.path.startswith('/legacy/'):
                    from urllib.parse import unquote
                    path=safe_path(root/'projects',unquote(self.path[len('/legacy/'):]))
                    if path.suffix.lower()!='.scad': raise ValueError('Legacy access exposes SCAD source only.')
                elif self.path.startswith('/artifact/'):
                    from urllib.parse import unquote
                    relative=unquote(self.path[len('/artifact/'):]); path=safe_path(root/'workspace',relative)
                    if path.suffix.lower() not in {'.png','.stl','.scad','.json','.md'}: raise ValueError('Unsupported artifact type.')
                    version=path
                    while version!=root/'workspace' and not (version/'artifact-manifest.json').is_file(): version=version.parent
                    if version==root/'workspace': raise ValueError('Version-bound manifest required.')
                    from core.workflow.review import snapshot_generation
                    generation,scad_bytes,stl_bytes,_,_=snapshot_generation(version/'artifact-manifest.json')
                    if path.suffix.lower() in {'.scad','.stl'}:
                        binding=generation.scad_binding if path.suffix.lower()=='.scad' else generation.stl_binding
                        if path!=safe_path(generation.workspace_root,binding.path): raise ValueError('Download the original manifest-bound artifact.')
                        self.send(200,scad_bytes if path.suffix.lower()=='.scad' else stl_bytes,'application/octet-stream'); return
                    if path.suffix.lower()=='.png':
                        from core.workflow.preview import verify_preview_bundle
                        verify_preview_bundle(path.parent/'preview-manifest.json')
                else:
                    relative='index.html' if self.path=='/' else self.path.lstrip('/')
                    path=safe_path(root/'app/dist',relative)
                self.send(200,path.read_bytes(),mimetypes.guess_type(path)[0] or 'application/octet-stream')
            except Exception as exc: self.send(400,{'error':str(exc)})
        def do_POST(self):
            if not self.guarded(True): return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=1024*1024: raise ValueError('Request must be at most 1 MiB.')
                payload=json.loads(self.rfile.read(length))
                if not isinstance(payload,dict): raise ValueError('Request must be an object.')
                if self.path=='/api/specs':
                    self.send(201,workshop.save_spec(payload['document'],accept_interface_changes=payload.get('accept_interface_changes') is True,intake_context=payload.get('intake_context'))); return
                if self.path=='/api/stop':
                    with lock:
                        if any(j['status'] in {'queued','running','cancel_requested'} for j in jobs.values()): raise ValueError('Wait for the active job before stopping.')
                    self.send(200,{'stopping':True}); threading.Thread(target=self.server.shutdown,daemon=True).start(); return
                if self.path=='/api/cancel':
                    identifier=payload['job_id']
                    with lock:
                        if identifier not in jobs or jobs[identifier]['status'] not in {'queued','running'}: raise ValueError('Job is not active.')
                        store.update(identifier,status='cancel_requested'); process=processes.get(identifier)
                    if process:
                        if os.name=='nt': subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
                        else: process.terminate()
                    self.send(200,{'cancel_requested':True,'note':'Inspect project status afterward; publication may have completed just before cancellation.'}); return
                if self.path!='/api/actions': raise ValueError('Unknown endpoint.')
                with lock:
                    if any(j['status'] in {'queued','running','cancel_requested'} for j in jobs.values()): raise ValueError('Another job is active; wait for its result.')
                    identifier=secrets.token_hex(8); store.update(identifier,status='queued',action=payload['action'],project_manifest=payload.get('payload',{}).get('manifest'),spec_path=payload.get('payload',{}).get('spec_path'))
                def run():
                    containment=None
                    try:
                        job_directory=safe_path(workshop.local,f'jobs/{identifier}'); job_directory.mkdir(parents=True,exist_ok=False)
                        request_path=job_directory/'request.json'; result_path=job_directory/'result.json'
                        containment=WorkerContainment()
                        request_path.write_text(json.dumps({**payload,'_worker_job':containment.name}),encoding='utf-8')
                        script=Path(__file__).resolve().parents[2]/'scripts/workshop_worker.py'
                        with lock:
                            if jobs[identifier]['status']=='cancel_requested': store.update(identifier,status='cancelled'); return
                            log=(job_directory/'worker.log').open('wb')
                            process=subprocess.Popen([sys.executable,'-B',str(script),str(root),str(request_path),str(result_path)],stdout=log,stderr=subprocess.STDOUT,cwd=root,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                            processes[identifier]=process; store.update(identifier,status='running')
                        try: code=process.wait(timeout=900)
                        except subprocess.TimeoutExpired:
                            if os.name=='nt': subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
                            else: process.kill()
                            raise ValueError('Job timed out; inspect project status before retrying.')
                        finally: log.close()
                        with lock:
                            if jobs[identifier]['status']=='cancel_requested': store.update(identifier,status='cancelled',error='Cancelled. Inspect project status before retrying.'); return
                        result=json.loads(result_path.read_text()) if result_path.exists() else {'error':'Worker stopped without a result. Inspect local worker log.'}
                        with lock:
                            if jobs[identifier]['status']=='cancel_requested':
                                store.update(identifier,status='cancelled',error='Cancelled. Inspect project status before retrying.')
                            elif code or 'error' in result: store.update(identifier,status='failed',error=result.get('error','Worker failed.'))
                            else: store.update(identifier,status='complete',result=result['result'])
                    except Exception as exc:
                        with lock:
                            if jobs[identifier]['status']=='cancel_requested':
                                store.update(identifier,status='cancelled',error='Cancelled. Inspect project status before retrying.')
                            else: store.update(identifier,status='failed',error=str(exc))
                    finally:
                        if containment: containment.close()
                        with lock: processes.pop(identifier,None)
                executor.submit(run); self.send(202,{'job_id':identifier})
            except Exception as exc: self.send(400,{'error':str(exc)})
    class OwnedServer(ThreadingHTTPServer):
        def server_close(self):
            try:
                super().server_close()
                executor.shutdown(wait=True,cancel_futures=True)
            finally: ownership.close()
    try: server=OwnedServer(('127.0.0.1',port),Handler)
    except Exception:
        ownership.close(); executor.shutdown(wait=False,cancel_futures=True); raise
    server.workshop=workshop; server.executor=executor
    return server
