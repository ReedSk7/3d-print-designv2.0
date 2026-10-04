"""Fixed local action worker; subprocess boundary permits safe job cancellation."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.workshop.service import Workshop
from core.workshop.ownership import join_worker_job

if __name__=='__main__':
    root,request_path,result_path=map(Path,sys.argv[1:])
    request=json.loads(request_path.read_text())
    join_worker_job(request.pop('_worker_job'))
    try:
        result=Workshop(root).action(request['action'],request.get('payload',{}))
        result_path.write_text(json.dumps({'result':result},default=str),encoding='utf-8')
    except Exception as exc:
        result_path.write_text(json.dumps({'error':str(exc)}),encoding='utf-8')
        raise SystemExit(1)
