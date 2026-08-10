"""Make repository packages importable for direct ``python scripts/...`` use."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def add_repo_root() -> Path:
    root_text = str(REPO_ROOT)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    return REPO_ROOT
