"""Recoverable local job history; interrupted work is never reported as success."""
import json
import os
from pathlib import Path
from threading import RLock

class JobStore:
    def __init__(self,path:Path):
        self.path=path; self.lock=RLock(); self.records={}
        if path.exists():
            self.records=json.loads(path.read_text())
            if not isinstance(self.records,dict): raise ValueError('Job history must be an object.')
            for record in self.records.values():
                if record.get('status') in {'queued','running','cancel_requested'}:
                    record.update(status='interrupted',error='Service restarted. Inspect project status before retrying; an artifact may already have been published.')
            self.save()
    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        temporary=self.path.with_suffix('.new')
        temporary.write_text(json.dumps(self.records,indent=2,default=str),encoding='utf-8')
        os.replace(temporary,self.path)
    def update(self,identifier,**values):
        with self.lock:
            self.records.setdefault(identifier,{}).update(values); self.save()
