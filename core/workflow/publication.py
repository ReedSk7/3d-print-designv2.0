"""Exclusive publication of staged version directories, manifest last."""
import os
from pathlib import Path


def publish_bundle(staging: Path, target: Path, *, manifest_name: str) -> None:
    """Reserve exclusively; publish manifest last so incomplete bundles cannot pass.

    Completed files are linked atomically. An unsupported filesystem fails closed.
    Never replace a target directory (including an empty competing directory).
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir(exist_ok=False)
    created = []
    try:
        for path in sorted(staging.iterdir(), key=lambda p: p.name == manifest_name):
            destination = target / path.name
            os.link(path, destination)
            created.append(destination)
    except Exception:
        for path in reversed(created):
            path.unlink()
        target.rmdir()
        raise
