from __future__ import annotations

from pathlib import Path
import os

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def examples_dir(repo_root: Path) -> Path:
    return repo_root / "examples" / "specs"


def pytest_collection_modifyitems(items):
    if os.name == "nt":
        return
    marker = pytest.mark.skip(reason="Windows worker containment; required coverage runs in the Windows OpenSCAD CI job")
    for item in items:
        if item.get_closest_marker("windows_worker"):
            item.add_marker(marker)
