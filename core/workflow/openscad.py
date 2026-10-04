"""Mandatory OpenSCAD discovery and atomic binary-STL compilation."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


EXECUTABLE_NAMES = ("openscad", "openscad.com", "openscad.exe")
WINDOWS_CANDIDATES = (
    Path(r"C:\Program Files\OpenSCAD\openscad.com"),
    Path(r"C:\Program Files\OpenSCAD\openscad.exe"),
    Path(r"C:\Program Files (x86)\OpenSCAD\openscad.com"),
    Path(r"C:\Program Files (x86)\OpenSCAD\openscad.exe"),
)
ERROR_DIAGNOSTIC = re.compile(r"(?:^|\n)\s*ERROR:", re.IGNORECASE)


class OpenSCADNotFound(RuntimeError):
    def __init__(self, checked_locations: tuple[str, ...]) -> None:
        self.checked_locations = checked_locations
        super().__init__(
            "OpenSCAD is required but was not found. Checked: "
            + ", ".join(checked_locations)
        )


class OpenSCADExecutionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class OpenSCADCompileResult:
    executable: Path
    version: str
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    output_path: Path

    def to_dict(self) -> dict[str, object]:
        return {
            "executable": str(self.executable),
            "version": self.version,
            "command": list(self.command),
            "returncode": self.returncode,
            "duration_seconds": round(self.duration_seconds, 6),
            "stdout": self.stdout,
            "stderr": self.stderr,
            "output_path": self.output_path.as_posix(),
        }


def checked_locations() -> tuple[str, ...]:
    locations = ["OPENSCAD_PATH"]
    locations.extend(f"PATH:{name}" for name in EXECUTABLE_NAMES)
    locations.extend(str(path) for path in WINDOWS_CANDIDATES)
    return tuple(locations)


def find_openscad() -> Path:
    configured = os.environ.get("OPENSCAD_PATH")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return candidate.resolve()
        # An explicit selection must never silently select a different version.
        raise OpenSCADNotFound((f"OPENSCAD_PATH={configured} (not a file)",))
    for name in EXECUTABLE_NAMES:
        located = shutil.which(name)
        if located:
            return Path(located).resolve()
    for candidate in WINDOWS_CANDIDATES:
        if candidate.is_file():
            return candidate.resolve()
    raise OpenSCADNotFound(checked_locations())


def openscad_version(executable: Path | None = None) -> str:
    program = executable or find_openscad()
    completed = run_openscad_command([str(program), "--version"], timeout_seconds=30)
    output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
    if completed.returncode != 0 or not output:
        raise OpenSCADExecutionError(
            f"Could not obtain OpenSCAD version (exit {completed.returncode}): {output}"
        )
    return output.splitlines()[0]


def run_openscad_command(command: list[str] | tuple[str, ...], *, timeout_seconds: int = 180):
    """Run without a shell; normalize launch and timeout failures for every caller."""
    if timeout_seconds <= 0:
        raise ValueError("OpenSCAD timeout must be positive.")
    try:
        return subprocess.run(command, shell=False, text=True, capture_output=True,
                              timeout=timeout_seconds, check=False)
    except subprocess.TimeoutExpired as exc:
        raise OpenSCADExecutionError(
            f"OpenSCAD timed out after {timeout_seconds} seconds."
        ) from exc
    except OSError as exc:
        raise OpenSCADExecutionError(f"Could not launch OpenSCAD: {exc}") from exc


def compile_binary_stl(
    source_path: Path,
    output_path: Path,
    *,
    timeout_seconds: int = 180,
) -> OpenSCADCompileResult:
    """Compile ``source_path`` and atomically publish a new binary STL."""

    source = source_path.resolve()
    output = output_path.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"OpenSCAD source not found: {source}")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing STL: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    executable = find_openscad()
    version = openscad_version(executable)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.stem}-", suffix=".tmp.stl", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    temporary.unlink()
    command = (
        str(executable),
        "--export-format=binstl",
        "-o",
        str(temporary),
        str(source),
    )
    started = time.monotonic()
    try:
        completed = run_openscad_command(command, timeout_seconds=timeout_seconds)
    except OpenSCADExecutionError:
        temporary.unlink(missing_ok=True)
        raise
    duration = time.monotonic() - started
    diagnostics = f"{completed.stdout}\n{completed.stderr}"
    if completed.returncode != 0 or ERROR_DIAGNOSTIC.search(diagnostics):
        temporary.unlink(missing_ok=True)
        raise OpenSCADExecutionError(
            f"OpenSCAD failed with exit {completed.returncode}.\n{diagnostics.strip()}"
        )
    if not temporary.is_file() or temporary.stat().st_size <= 84:
        temporary.unlink(missing_ok=True)
        raise OpenSCADExecutionError(
            "OpenSCAD returned success but did not create a non-empty STL."
        )
    # Linking publishes all completed bytes exclusively, even if another writer
    # created the target while OpenSCAD ran. Fail closed on unsupported filesystems.
    try:
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return OpenSCADCompileResult(
        executable=executable,
        version=version,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        duration_seconds=duration,
        output_path=output,
    )
