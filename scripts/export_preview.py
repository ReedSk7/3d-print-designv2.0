"""Export a PNG preview from an OpenSCAD source file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from _openscad_cli import (
    OpenSCADNotFound,
    define_args,
    print_failure,
    print_missing_openscad_error,
    run_openscad,
)


CAMERA_PRESETS = {
    "iso": "0,0,0,55,0,35,220",
    "front": "0,0,0,90,0,0,220",
    "side": "0,0,0,90,0,90,220",
    "top": "0,0,0,0,0,0,220",
}


def parse_imgsize(value: str) -> str:
    if not re.fullmatch(r"\d+x\d+", value):
        raise argparse.ArgumentTypeError("imgsize must use WIDTHxHEIGHT, for example 1200x900")
    width, height = value.lower().split("x", 1)
    return f"{width},{height}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export OpenSCAD PNG preview.")
    parser.add_argument("--input", required=True, help="Path to the .scad file")
    parser.add_argument("--output", required=True, help="Path to the output .png file")
    parser.add_argument("--view", required=True, choices=tuple(CAMERA_PRESETS.keys()))
    parser.add_argument(
        "--imgsize",
        default="1200x900",
        type=parse_imgsize,
        help="Preview size as WIDTHxHEIGHT. Defaults to 1200x900.",
    )
    parser.add_argument(
        "--define",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="OpenSCAD -D override. Repeat for multiple values.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_file():
        print("FAIL")
        print(f"SCAD input not found: {input_path}")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        extra_defines = define_args(args.define)
    except ValueError as exc:
        print("FAIL")
        print(str(exc))
        return 1

    command_args = [
        *extra_defines,
        "--projection=o",
        "--autocenter",
        "--viewall",
        "--imgsize",
        args.imgsize,
        "--camera",
        CAMERA_PRESETS[args.view],
        "-o",
        str(output_path),
        str(input_path),
    ]

    try:
        result = run_openscad(command_args)
    except OpenSCADNotFound as exc:
        print_missing_openscad_error(exc)
        return 1

    if result.returncode != 0:
        print("FAIL")
        print_failure(result)
        return result.returncode or 1

    if not output_path.is_file():
        print("FAIL")
        print(f"OpenSCAD completed but preview PNG was not created: {output_path}")
        if result.stdout.strip():
            print(result.stdout.rstrip())
        if result.stderr.strip():
            print(result.stderr.rstrip())
        return 1

    print("PREVIEW EXPORT COMPLETE")
    print(f"Preview exported: {output_path}")
    print("Physical fit: NOT CONFIRMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
