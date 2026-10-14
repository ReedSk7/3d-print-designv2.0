"""Enforce source-control boundaries for generated part artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
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
    ".fit-result.json",
    ".fit-evidence.json",
    ".physical-fit.json",
    ".physical-fit-evidence.json",
    ".evidence.json",
}
FIXTURE_ROOT = "tests/fixtures/"
RESTRICTED_LOCAL_ROOTS = ("owner-validation/local/",)
MAX_FIXTURE_BYTES = 1024 * 1024
LEGACY_COMMIT = '47ea856f60a010239352fe965ba19c050c991c4c'
LEGACY_ARTIFACTS = {
    'projects/agent_smoke_test_hex_bit_holder/exports/agent_smoke_test_hex_bit_holder_v01.stl': '25ed32bd3564238515b981f7c3d74ea83f7b19b26a4cd8376994cf3899da336a',
    'projects/agent_smoke_test_hex_bit_holder/previews/agent_smoke_test_hex_bit_holder_v01_iso.png': '3ff89717e86a73aa632dc5ccf76c21a3048804b27e9d35dd46ce69e45cb83e02',
    'projects/simple_wall_bracket_example/exports/simple_wall_bracket_example_v01.stl': '6fd1e81293f17f87170e9eae5ef44ce39014d4b0e62f81b2846d4b1346fb5af0',
    'projects/simple_wall_bracket_example/previews/simple_wall_bracket_example_v01_front.png': '11c92689930f3c683071fad78fb633ef15bc73d931601bd669af7af054f6c39c',
    'projects/simple_wall_bracket_example/previews/simple_wall_bracket_example_v01_iso.png': '5a630b92d5f688a0fa311f0004738d681cf950c85a218dd82218b8db3cc0ab42',
    'projects/simple_wall_bracket_example/previews/simple_wall_bracket_example_v01_side.png': '6bce2bf07685a9c655358cdb055dbef88ef945e4f1be1a7f221761edb205c0b4',
}

def byte_record(content: bytes) -> dict:
    return {"sha256": hashlib.sha256(content).hexdigest(), "size_bytes": len(content)}


def inspect_legacy_preservation() -> tuple[set[str], list[str]]:
    """Check all six paths, including removed ones, against immutable Git history.

    The original Windows hashes are pinned above. Only the two named ASCII STL
    files permit LF and its exact CRLF expansion; files are never normalized.
    The JSON baseline records both representations for review, but cannot expand
    the fixed allowlist, select another source commit, or bless changed blobs.
    """
    preserved: set[str] = set()
    errors: list[str] = []
    if run_git("merge-base", "--is-ancestor", LEGACY_COMMIT, "HEAD").returncode:
        return preserved, [
            "Historical preservation requires the original source ancestor "
            f"{LEGACY_COMMIT}. Fetch full history (CI checkout fetch-depth: 0; "
            "for a shallow clone, git fetch --unshallow) and verify branch ancestry."
        ]
    try:
        manifest = json.loads((ROOT / "docs/legacy-artifact-preservation.json").read_text(encoding="utf-8"))
        records = manifest["files"]
        paths = [item["path"] for item in records]
        if manifest["source_commit"] != LEGACY_COMMIT:
            raise ValueError("source_commit differs from the pinned original commit")
        if len(paths) != len(LEGACY_ARTIFACTS) or set(paths) != set(LEGACY_ARTIFACTS):
            raise ValueError("files must contain exactly the six pinned historical paths")
        baseline = {item["path"]: item for item in records}
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return preserved, [f"Historical preservation baseline is invalid: {exc}"]

    for path, windows_sha256 in LEGACY_ARTIFACTS.items():
        try:
            original = run_git("show", f"{LEGACY_COMMIT}:{path}")
            tree = run_git("ls-tree", "-z", LEGACY_COMMIT, "--", path)
            if original.returncode or tree.returncode or not tree.stdout:
                raise ValueError("original Git blob is unavailable")
            metadata, tree_path = tree.stdout.rstrip(b"\0").split(b"\t", 1)
            mode, kind, blob = metadata.decode("ascii").split()
            if mode != "100644" or kind != "blob" or tree_path.decode() != path:
                raise ValueError("original is not the expected regular Git file")
            content = original.stdout
            if path.endswith(".stl"):
                if b"\r" in content or b"\n" not in content:
                    raise ValueError("original ASCII STL is not the pinned LF representation")
                representations = {"lf": content, "crlf": content.replace(b"\n", b"\r\n")}
                windows_bytes = representations["crlf"]
            else:
                representations = {"exact": content}
                windows_bytes = content
            if hashlib.sha256(windows_bytes).hexdigest() != windows_sha256:
                raise ValueError("original blob differs from the pinned historical bytes")
            expected = {
                "path": path,
                "git_blob": blob,
                "git": byte_record(content),
                "working_tree": {name: byte_record(data) for name, data in representations.items()},
            }
            if baseline[path] != expected:
                raise ValueError("recorded baseline does not match the original Git blob/representations")
            index = run_git("ls-files", "--stage", "-z", "--", path)
            expected_index = f"{mode} {blob} 0\t{path}\0".encode()
            if index.returncode or index.stdout != expected_index:
                raise ValueError("index entry is missing, unresolved, or differs from the original Git blob")
            indexed = run_git("show", f":{path}")
            if indexed.returncode or indexed.stdout != content:
                raise ValueError("index bytes differ from the original Git blob")
            artifact = ROOT / path
            for entry in (artifact, *artifact.parents):
                if entry == ROOT:
                    break
                if entry.is_symlink() or getattr(entry, "is_junction", lambda: False)():
                    raise ValueError("checkout path uses a symlink or junction")
            if artifact.read_bytes() not in representations.values():
                raise ValueError("checkout bytes are not an exact allowed representation")
            preserved.add(path)
        except (OSError, ValueError) as exc:
            errors.append(f"Historical artifact is not preserved: {path}: {exc}")
    return preserved, errors


def is_preserved_historical_artifact(relative_path: str) -> bool:
    if relative_path not in LEGACY_ARTIFACTS:
        return False
    preserved, _ = inspect_legacy_preservation()
    return relative_path in preserved


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

    preserved, preservation_errors = inspect_legacy_preservation()
    errors.extend(preservation_errors)

    workspace_tracked = [
        path for path in tracked if path.startswith("workspace/") and path != "workspace/.gitkeep"
    ]
    for path in workspace_tracked:
        errors.append(f"Routine workspace output is tracked: {path}")

    for path in tracked:
        if path.startswith(RESTRICTED_LOCAL_ROOTS):
            errors.append(f"Owner-local validation input or evidence is tracked: {path}")

    for path in tracked:
        if not is_generated_path(path):
            continue
        if is_allowed_fixture(path, errors):
            continue
        if path in preserved:
            continue
        errors.append(f"Routine generated output is tracked: {path}")

    for path in staged:
        if path.startswith("workspace/") and path != "workspace/.gitkeep":
            errors.append(f"Routine workspace output is staged: {path}")
        elif path.startswith(RESTRICTED_LOCAL_ROOTS):
            errors.append(f"Owner-local validation input or evidence is staged: {path}")
        elif is_generated_path(path):
            if not path.startswith(FIXTURE_ROOT) and path not in preserved:
                errors.append(f"Routine generated output is staged: {path}")

    ignore_probes = (
        "workspace/policy-probe/generated.scad",
        "workspace/policy-probe/manifest.json",
        "owner-validation/local/owner-filled-spec.json",
        "owner-validation/local/owner-notes.txt",
        "owner-validation/local/result.fit-evidence.json",
        "owner-validation/local/result.physical-fit-evidence.json",
        "owner-validation/local/fit-result.evidence.json",
        "owner-validation/local/physical-fit.evidence.json",
        "policy-probe/generated.stl",
        "policy-probe/generated.png",
        "policy-probe/generated.3mf",
        "policy-probe/generated.sl1",
        "policy-probe/generated.photon",
        "policy-probe/generated.ctb",
        "policy-probe/generation.log",
        "policy-probe/result.fit-result.json",
        "policy-probe/result.fit-evidence.json",
        "policy-probe/result.physical-fit.json",
        "policy-probe/result.physical-fit-evidence.json",
        "policy-probe/fit-result.evidence.json",
        "policy-probe/physical-fit.evidence.json",
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
    print(f"Unchanged preexisting historical artifacts retained: {len(preserved)} / {len(LEGACY_ARTIFACTS)}")
    print(f"Workspace artifacts inspected: {len(workspace_artifacts)}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
