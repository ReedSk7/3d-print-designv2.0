"""Shared OpenSCAD CLI discovery and execution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


from _repo_bootstrap import add_repo_root
add_repo_root()
from core.workflow.openscad import (
    ERROR_DIAGNOSTIC, OpenSCADNotFound, OpenSCADExecutionError,
    checked_locations, find_openscad, run_openscad_command,
)


@dataclass
class OpenSCADResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def define_args(defines: Iterable[str] | None) -> list[str]:
    args: list[str] = []
    for item in defines or []:
        if "=" not in item:
            raise ValueError(f"Define must be KEY=VALUE: {item}")
        args.extend(["-D", item])
    return args


def run_openscad(arguments: list[str]) -> OpenSCADResult:
    """Run OpenSCAD with argument-list subprocess execution."""

    executable = find_openscad()
    command = [str(executable), *arguments]
    try:
        completed = run_openscad_command(command)
    except OpenSCADExecutionError as exc:
        return OpenSCADResult(command=command, returncode=1, stdout="", stderr=str(exc))
    return OpenSCADResult(
        command=command,
        returncode=completed.returncode or (1 if ERROR_DIAGNOSTIC.search(completed.stdout + "\n" + completed.stderr) else 0),
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def print_missing_openscad_error(exc: OpenSCADNotFound) -> None:
    print("FAIL")
    print("OpenSCAD was not found.")
    print("Checked locations:")
    for location in exc.checked_locations:
        print(f"- {location}")
    print("")
    print("Install OpenSCAD or add its install folder to PATH, for example:")
    print(r'$env:Path += ";C:\Program Files\OpenSCAD"')


def print_failure(result: OpenSCADResult) -> None:
    print("OpenSCAD command failed.")
    print("Command:")
    print(" ".join(result.command))
    print(f"Return code: {result.returncode}")
    if result.stdout.strip():
        print("")
        print("stdout:")
        print(result.stdout.rstrip())
    if result.stderr.strip():
        print("")
        print("stderr:")
        print(result.stderr.rstrip())
