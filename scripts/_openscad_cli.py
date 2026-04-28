"""Shared OpenSCAD CLI discovery and execution helpers."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EXECUTABLE_NAMES = ("openscad", "openscad.com", "openscad.exe")
WINDOWS_CANDIDATES = (
    Path(r"C:\Program Files\OpenSCAD\openscad.exe"),
    Path(r"C:\Program Files\OpenSCAD\openscad.com"),
    Path(r"C:\Program Files (x86)\OpenSCAD\openscad.exe"),
    Path(r"C:\Program Files (x86)\OpenSCAD\openscad.com"),
)


class OpenSCADNotFound(RuntimeError):
    """Raised when OpenSCAD cannot be found."""

    def __init__(self, checked_locations: list[str]) -> None:
        self.checked_locations = checked_locations
        super().__init__("OpenSCAD executable was not found.")


@dataclass
class OpenSCADResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def checked_locations() -> list[str]:
    locations = [f"PATH:{name}" for name in EXECUTABLE_NAMES]
    locations.extend(str(path) for path in WINDOWS_CANDIDATES)
    return locations


def find_openscad() -> Path:
    """Find OpenSCAD from PATH or common Windows install paths."""

    for executable_name in EXECUTABLE_NAMES:
        found = shutil.which(executable_name)
        if found:
            return Path(found)

    for candidate in WINDOWS_CANDIDATES:
        if candidate.is_file():
            return candidate

    raise OpenSCADNotFound(checked_locations())


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
    completed = subprocess.run(
        command,
        shell=False,
        text=True,
        capture_output=True,
    )
    return OpenSCADResult(
        command=command,
        returncode=completed.returncode,
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
