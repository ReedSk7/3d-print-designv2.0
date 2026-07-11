"""Run the full repo verification chain for a versioned OpenSCAD project."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


TASK_MODES = (
    "original_product_design",
    "reference_based_reconstruction",
    "mesh_cleanup_and_remodel",
)

ROOT = Path(__file__).resolve().parents[1]


def normalize_version(value: str) -> str:
    value = value.strip().lower()
    if value.isdigit():
        return f"v{int(value):02d}"
    if value.startswith("v") and value[1:].isdigit():
        return f"v{int(value[1:]):02d}"
    raise ValueError("Version must look like v01 or 1.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a project from SCAD through checked outputs.")
    parser.add_argument("--project", required=True, help="Path to projects/<project_stem>.")
    parser.add_argument("--task-mode", required=True, choices=TASK_MODES)
    parser.add_argument("--version", required=True, help="Version suffix, for example v01.")
    parser.add_argument(
        "--view",
        action="append",
        choices=("iso", "front", "side", "top"),
        help="Preview view to render. Repeat for multiple views. Defaults to required views for the task mode.",
    )
    parser.add_argument(
        "--define",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="OpenSCAD -D override passed to export and preview commands. Repeat for multiple values.",
    )
    parser.add_argument(
        "--allow-multiple-bodies",
        action="store_true",
        help="Pass through to export_stl.py for intentionally disconnected exports.",
    )
    return parser.parse_args()


def required_views(task_mode: str) -> list[str]:
    if task_mode == "original_product_design":
        return ["iso"]
    return ["iso", "front", "side"]


def run_step(label: str, command: list[str]) -> int:
    print("")
    print(f"=== {label} ===")
    print("Command:")
    print(" ".join(command))
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.stdout.strip():
        print(completed.stdout.rstrip())
    if completed.stderr.strip():
        print(completed.stderr.rstrip())
    if completed.returncode != 0:
        print("")
        print(f"FAIL bottleneck: {label}")
        print(f"Exit code: {completed.returncode}")
    return completed.returncode


def with_defines(base_command: list[str], defines: list[str]) -> list[str]:
    command = list(base_command)
    for item in defines:
        command.extend(["--define", item])
    return command


def main() -> int:
    args = parse_args()
    try:
        version = normalize_version(args.version)
    except ValueError as exc:
        print("FAIL")
        print(str(exc))
        return 1

    project_dir = Path(args.project)
    if not project_dir.is_absolute():
        project_dir = ROOT / project_dir
    if not project_dir.is_dir():
        print("FAIL")
        print(f"Project directory not found: {project_dir}")
        return 1

    stem = project_dir.name
    source = project_dir / "source" / f"{stem}_{version}.scad"
    stl = project_dir / "exports" / f"{stem}_{version}.stl"
    preview_dir = project_dir / "previews"

    if not source.is_file():
        print("FAIL")
        print(f"SCAD source not found: {source}")
        return 1

    python = sys.executable
    export_command = [
        python,
        str(ROOT / "scripts" / "export_stl.py"),
        "--input",
        str(source),
        "--output",
        str(stl),
    ]
    if args.allow_multiple_bodies:
        export_command.append("--allow-multiple-bodies")

    steps: list[tuple[str, list[str]]] = [
        (
            "Validate SCAD",
            [python, str(ROOT / "scripts" / "validate_scad.py"), str(source)],
        ),
        (
            "Export STL And Mesh QA",
            with_defines(export_command, args.define),
        ),
    ]

    for view in args.view or required_views(args.task_mode):
        preview = preview_dir / f"{stem}_{version}_{view}.png"
        steps.append(
            (
                f"Render Preview {view}",
                with_defines(
                    [
                        python,
                        str(ROOT / "scripts" / "export_preview.py"),
                        "--input",
                        str(source),
                        "--output",
                        str(preview),
                        "--view",
                        view,
                    ],
                    args.define,
                ),
            )
        )

    steps.append(
        (
            "Check Project Outputs",
            [
                python,
                str(ROOT / "scripts" / "check_project_outputs.py"),
                "--project",
                str(project_dir),
                "--task-mode",
                args.task_mode,
                "--version",
                version,
            ],
        )
    )

    for label, command in steps:
        exit_code = run_step(label, command)
        if exit_code != 0:
            return exit_code

    print("")
    print("PASS")
    print(f"Project verification completed: {project_dir}")
    print(f"Version: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
