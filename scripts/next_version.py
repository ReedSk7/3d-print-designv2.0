"""Find or create the next version number for a project."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


VERSION_RE = re.compile(r"_v(?P<number>\d{2,})(?:_|\.|$)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Suggest or create the next project version.")
    parser.add_argument("--project", required=True, help="Path to projects/<project_stem>")
    parser.add_argument("--copy-scad", action="store_true", help="Copy latest SCAD source forward.")
    parser.add_argument("--copy-notes", action="store_true", help="Copy latest notes and manifest forward as drafts.")
    return parser.parse_args()


def find_versions(project_dir: Path) -> list[int]:
    versions: set[int] = set()
    for path in project_dir.rglob("*"):
        if not path.is_file():
            continue
        match = VERSION_RE.search(path.name)
        if match:
            versions.add(int(match.group("number")))
    return sorted(versions)


def latest_file(directory: Path, stem: str, version: str, suffix: str) -> Path | None:
    candidate = directory / f"{stem}_{version}{suffix}"
    return candidate if candidate.is_file() else None


def copy_no_overwrite(source: Path, destination: Path) -> None:
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing versioned file: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def draft_copy(source: Path, destination: Path, old_version: str, new_version: str) -> None:
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing versioned file: {destination}")
    text = source.read_text(encoding="utf-8-sig")
    text = text.replace(old_version, new_version)
    text = text.replace("verification_status: verified", "verification_status: NOT VERIFIED")
    text = text.replace("stl_export_status: success", "stl_export_status: NOT VERIFIED")
    text = text.replace("preview_export_status: success", "preview_export_status: NOT VERIFIED")
    text = text.replace("status: complete", "status: draft")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project)
    if not project_dir.is_dir():
        print("FAIL")
        print(f"Project directory not found: {project_dir}")
        return 1

    stem = project_dir.name
    versions = find_versions(project_dir)
    latest_number = versions[-1] if versions else 0
    old_version = f"v{latest_number:02d}" if latest_number else "v00"
    new_version = f"v{latest_number + 1:02d}"

    created: list[Path] = []
    try:
        if args.copy_scad and latest_number:
            source = latest_file(project_dir / "source", stem, old_version, ".scad")
            if source is None:
                raise FileNotFoundError(f"Latest SCAD not found for {old_version}")
            destination = project_dir / "source" / f"{stem}_{new_version}.scad"
            copy_no_overwrite(source, destination)
            created.append(destination)

        if args.copy_notes and latest_number:
            for suffix in ("_notes.md", "_manifest.md"):
                source = latest_file(project_dir / "notes", stem, old_version, suffix)
                if source is None:
                    continue
                destination = project_dir / "notes" / f"{stem}_{new_version}{suffix}"
                draft_copy(source, destination, old_version, new_version)
                created.append(destination)
    except (FileExistsError, FileNotFoundError) as exc:
        print("FAIL")
        print(str(exc))
        return 1

    print("VERSION PLAN COMPLETE")
    print(f"Project: {project_dir}")
    print(f"Highest existing version: {old_version if latest_number else 'none'}")
    print(f"Next version: {new_version}")
    print(f"Suggested source path: {project_dir / 'source' / f'{stem}_{new_version}.scad'}")
    print(f"Suggested STL path: {project_dir / 'exports' / f'{stem}_{new_version}.stl'}")
    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
