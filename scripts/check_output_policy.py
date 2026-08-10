"""Enforce source-control boundaries for generated part artifacts."""

from __future__ import annotations

import argparse
import struct
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
GENERATED_ENDINGS = {
    ".3mf",
    ".3mf.cache",
    ".bgcode",
    ".gcode",
    ".glb",
    ".log",
    ".obj",
    ".photon",
    ".png",
    ".sl1",
    ".stl",
    ".ctb",
}
FIXTURE_ROOT = "tests/fixtures/"
MAX_FIXTURE_BYTES = 1024 * 1024

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that routine generated outputs stay out of source control."
    )
    parser.add_argument(
        "--require-workspace-artifacts",
        action="store_true",
        help="Fail unless the CLI has generated at least one workspace artifact.",
    )
    return parser.parse_args()


def run_git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )


def nul_paths(result: subprocess.CompletedProcess[bytes]) -> list[str]:
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or "git command failed")
    return [
        item.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for item in result.stdout.split(b"\0")
        if item
    ]


def is_binary_stl(path: Path) -> bool:
    """Recognize binary STL by its fixed 84 + 50*n byte structure."""

    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            header = handle.read(84)
    except OSError:
        return False
    if len(header) != 84:
        return False
    triangle_count = struct.unpack("<I", header[80:84])[0]
    return size == 84 + (50 * triangle_count)


def is_allowed_fixture(relative_path: str, errors: list[str]) -> bool:
    if not relative_path.startswith(FIXTURE_ROOT):
        return False

    fixture = ROOT / relative_path
    if not fixture.is_file():
        errors.append(f"Tracked fixture is missing: {relative_path}")
        return True
    if fixture.stat().st_size > MAX_FIXTURE_BYTES:
        errors.append(
            f"Generated fixture exceeds {MAX_FIXTURE_BYTES} bytes: {relative_path}"
        )
    if fixture.suffix.lower() == ".stl" and not is_binary_stl(fixture):
        errors.append(f"Source-controlled STL fixture is not binary: {relative_path}")
    return True


def is_ignored(relative_path: str) -> bool:
    result = run_git("check-ignore", "--no-index", "--quiet", "--", relative_path)
    return result.returncode == 0


def is_generated_path(relative_path: str) -> bool:
    lowered = relative_path.lower()
    return any(lowered.endswith(ending) for ending in GENERATED_ENDINGS) or ".log." in lowered


def main() -> int:
    args = parse_args()
    errors: list[str] = []

    keep_file = WORKSPACE / ".gitkeep"
    if not keep_file.is_file():
        errors.append("workspace/.gitkeep is missing.")

    try:
        tracked = nul_paths(run_git("ls-files", "-z"))
        staged = nul_paths(
            run_git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
        )
    except RuntimeError as exc:
        print("FAIL")
        print(f"Could not inspect Git state: {exc}")
        return 2

    workspace_tracked = [
        path for path in tracked if path.startswith("workspace/") and path != "workspace/.gitkeep"
    ]
    for path in workspace_tracked:
        errors.append(f"Routine workspace output is tracked: {path}")

    for path in tracked:
        if not is_generated_path(path):
            continue
        if is_allowed_fixture(path, errors):
            continue
        errors.append(f"Routine generated output is tracked: {path}")

    for path in staged:
        if path.startswith("workspace/") and path != "workspace/.gitkeep":
            errors.append(f"Routine workspace output is staged: {path}")
        elif is_generated_path(path):
            if not path.startswith(FIXTURE_ROOT):
                errors.append(f"Routine generated output is staged: {path}")

    ignore_probes = (
        "workspace/policy-probe/generated.scad",
        "workspace/policy-probe/manifest.json",
        "policy-probe/generated.stl",
        "policy-probe/generated.png",
        "policy-probe/generated.3mf",
        "policy-probe/generated.sl1",
        "policy-probe/generated.photon",
        "policy-probe/generated.ctb",
        "policy-probe/generation.log",
    )
    for probe in ignore_probes:
        if not is_ignored(probe):
            errors.append(f"Expected generated path is not ignored: {probe}")

    workspace_artifacts = []
    if WORKSPACE.is_dir():
        workspace_artifacts = [
            path for path in WORKSPACE.rglob("*") if path.is_file() and path.name != ".gitkeep"
        ]
    if args.require_workspace_artifacts and not workspace_artifacts:
        errors.append("No generated workspace artifacts were found after CLI vertical slices.")
    for artifact in workspace_artifacts:
        relative = artifact.relative_to(ROOT).as_posix()
        if not is_ignored(relative):
            errors.append(f"Workspace artifact is not ignored: {relative}")

    print("PASS" if not errors else "FAIL")
    tracked_fixtures = sum(path.startswith(FIXTURE_ROOT) for path in tracked)
    print(f"Tracked generated-output exceptions: {tracked_fixtures} intentional fixtures")
    print(f"Workspace artifacts inspected: {len(workspace_artifacts)}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
