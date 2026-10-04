"""Start the local Print Workshop with an explicit project environment."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.workshop.server import make_server
from core.workshop.readiness import check_readiness
import json

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--instance-id')
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args(); root=Path(__file__).resolve().parents[1]
    readiness=check_readiness(root)
    if args.check_only or not readiness['ready']:
        print(json.dumps(readiness,indent=2)); raise SystemExit(0 if readiness['ready'] else 1)
    server=make_server(root,args.port,instance_id=args.instance_id)
    print(f'Print Workshop ready at http://127.0.0.1:{server.server_port}',flush=True)
    try: server.serve_forever()
    finally: server.server_close(); server.executor.shutdown(wait=True,cancel_futures=True)
