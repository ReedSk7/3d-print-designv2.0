"""Portable read-only check of the built browser app, independent of workers."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.workshop.app_build import app_build_check

if __name__ == '__main__':
    result = app_build_check(Path(__file__).resolve().parents[1])
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'pass' else 1)
