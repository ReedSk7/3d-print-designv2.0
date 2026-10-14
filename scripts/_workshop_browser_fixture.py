"""Serve the real built Workshop against disposable, explicitly synthetic data.

Private helper for smoke_workshop_browser.mjs. Never starts generation workers,
reads owner data, or records visual/physical evidence. The caller owns cleanup.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import threading

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))

from core.workshop.server import make_server
from core.workshop.service import Workshop
from core.workshop.app_build import validate_app_build


def prepare(root: Path) -> None:
    if root.is_symlink() or not root.is_dir() or any(root.iterdir()):
        raise ValueError("Browser fixture requires a new, empty temporary directory.")
    build = REPOSITORY / "app/dist"
    validate_app_build(REPOSITORY)
    shutil.copytree(build, root / "app/dist")
    templates = root / "examples/specs"
    templates.mkdir(parents=True)
    for family in ("bushing", "round_adapter", "flange_plate"):
        shutil.copyfile(
            REPOSITORY / f"examples/specs/{family}_example.json",
            templates / f"{family}_example.json",
        )

    document = json.loads((templates / "bushing_example.json").read_text())
    document["project"].update(
        id="synthetic_browser_saved", name="Synthetic browser saved design", version="v01"
    )
    document["physical_verification"]["notes"] = (
        "Synthetic browser fixture only; no physical test or owner measurement."
    )
    Workshop(root).save_spec(
        document,
        intake_context={"exact_target": "Synthetic browser fixture; no physical-fit claim."},
    )
    corrupt = root / "owner-validation/local/workshop/synthetic_browser_corrupt/v01/spec.json"
    corrupt.parent.mkdir(parents=True)
    corrupt.write_text('{"synthetic_corrupt_fixture":', encoding="utf-8")

    for base, size in ((root / "projects", 1), (root / "owner-validation/local/workshop/legacy", 2)):
        source = base / "synthetic_browser_legacy/source/synthetic.scad"
        source.parent.mkdir(parents=True)
        source.write_text(
            f"// Synthetic browser fixture only; no physical-fit claim.\ncube({size});\n",
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    prepare(root)
    # Keep optional tool discovery deterministic without launching installed tools.
    os.environ["BLENDER_PATH"] = str(root / "synthetic-blender-unavailable")
    server = make_server(root, port=0, instance_id="synthetic-browser-smoke")
    # EOF from the parent and a separate lifetime bound both stop the bridge.
    def stop_on_eof() -> None:
        sys.stdin.buffer.read()
        server.shutdown()

    threading.Thread(target=stop_on_eof, daemon=True).start()
    lifetime = threading.Timer(100, server.shutdown)
    lifetime.daemon = True
    lifetime.start()
    print(json.dumps({"url": f"http://127.0.0.1:{server.server_port}"}), flush=True)
    try:
        server.serve_forever(poll_interval=0.1)
    finally:
        lifetime.cancel()
        server.server_close()


if __name__ == "__main__":
    main()
