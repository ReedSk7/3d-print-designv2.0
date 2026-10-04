"""Render exact V3 artifact versions; retain explicit legacy single-image mode."""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from _repo_bootstrap import add_repo_root
add_repo_root()
from core.workflow.preview import CAMERA_PRESETS, export_previews, render_png


def parse_imgsize(value):
    if not re.fullmatch(r"[0-9]+x[0-9]+", value):
        raise argparse.ArgumentTypeError("Use WIDTHxHEIGHT.")
    size = tuple(int(v) for v in value.split("x"))
    if any(not 64 <= v <= 4096 for v in size):
        raise argparse.ArgumentTypeError("Image dimensions must be 64 through 4096.")
    return size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path)
    source.add_argument("--input", type=Path, help="Legacy single-image mode; no V3 review claim")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--view", choices=tuple(CAMERA_PRESETS))
    parser.add_argument("--imgsize", type=parse_imgsize, default=(1200, 900))
    parser.add_argument("--revision", default="r01")
    parser.add_argument("--detail-camera", help="x,y,z,rx,ry,rz,distance; no auto-fit for detail")
    args = parser.parse_args()
    try:
        if args.manifest:
            if args.output or args.view:
                raise ValueError("Manifest mode chooses all views and its version-bound output directory.")
            output = export_previews(args.manifest, revision=args.revision, size=args.imgsize,
                                     detail_camera=args.detail_camera)
        else:
            if not args.input.is_file() or args.output is None or args.view is None:
                raise ValueError("Legacy mode requires existing --input, --output, and --view.")
            render_png(args.input, args.output, view=args.view, size=args.imgsize)
            output = args.output
        print(f"PREVIEW EXPORT COMPLETE: {output}")
        print("Agent visual review: PENDING. Owner review: PENDING. Physical fit: NOT CONFIRMED.")
        return 0
    except Exception as exc:
        print(f"PREVIEW FAILED: {exc}")
        print("No review or physical fit is confirmed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
