"""Check required legacy project-file presence without making fit claims."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TASK_MODES = (
    "original_product_design",
    "reference_based_reconstruction",
    "mesh_cleanup_and_remodel",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check project output artifacts.")
    parser.add_argument("--project", required=True, help="Path to projects/<project_stem>")
    parser.add_argument("--task-mode", required=True, choices=TASK_MODES)
    parser.add_argument("--version", required=True, help="Version suffix, for example v01")
    return parser.parse_args()


def normalize_version(value: str) -> str:
    value = value.strip().lower()
    if re.fullmatch(r"\d+", value):
        return f"v{int(value):02d}"
    if re.fullmatch(r"v\d+", value):
        return f"v{int(value[1:]):02d}"
    raise ValueError("Version must look like v01 or 1.")


def read_manifest(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data: dict[str, str] = {}
    for raw_line in parts[1].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def required_preview_names(stem: str, version: str, task_mode: str) -> list[str]:
    views = ["iso"] if task_mode == "original_product_design" else ["iso", "front", "side"]
    return [f"{stem}_{version}_{view}.png" for view in views]


def missing_files(paths: list[Path]) -> list[Path]:
    return [path for path in paths if not path.is_file()]


def manifest_claims_completion(manifest: dict[str, str]) -> bool:
    completion_tokens = ("verified", "success", "succeeded", "complete", "completed", "exported", "released")
    for key in ("status", "stl_export_status", "preview_export_status", "verification_status"):
        value = manifest.get(key, "").lower()
        if any(token in value for token in completion_tokens) and "not verified" not in value:
            return True
    return False


def main() -> int:
    args = parse_args()
    try:
        version = normalize_version(args.version)
    except ValueError as exc:
        print("FAIL")
        print(str(exc))
        return 1

    project_dir = Path(args.project)
    if not project_dir.is_dir():
        print("FAIL")
        print(f"Project directory not found: {project_dir}")
        return 1

    stem = project_dir.name
    source = project_dir / "source" / f"{stem}_{version}.scad"
    stl = project_dir / "exports" / f"{stem}_{version}.stl"
    notes = project_dir / "notes" / f"{stem}_{version}_notes.md"
    manifest_path = project_dir / "notes" / f"{stem}_{version}_manifest.md"
    printability = project_dir / "notes" / f"{stem}_{version}_printability_review.md"
    release_notes = project_dir / "notes" / f"{stem}_{version}_release_notes.md"

    required = [source, stl, notes, manifest_path, printability, release_notes]
    for preview_name in required_preview_names(stem, version, args.task_mode):
        required.append(project_dir / "previews" / preview_name)

    if args.task_mode in {"reference_based_reconstruction", "mesh_cleanup_and_remodel"}:
        required.extend(
            [
                project_dir / "notes" / f"{stem}_{version}_reference_comparison_log.md",
                project_dir / "notes" / f"{stem}_{version}_review_report.md",
            ]
        )

    manifest = read_manifest(manifest_path)
    missing = missing_files(required)

    errors: list[str] = []
    if missing:
        errors.append("Missing outputs:")
        errors.extend(f"MISSING: {path}" for path in missing)

    if manifest:
        if manifest.get("project_stem") and manifest["project_stem"] != stem:
            errors.append(f"Manifest project_stem mismatch: {manifest['project_stem']} != {stem}")
        if manifest.get("version") and manifest["version"] != version:
            errors.append(f"Manifest version mismatch: {manifest['version']} != {version}")
        if manifest.get("task_mode") and manifest["task_mode"] != args.task_mode:
            errors.append(f"Manifest task_mode mismatch: {manifest['task_mode']} != {args.task_mode}")
        if manifest_claims_completion(manifest) and missing:
            errors.append("Manifest claims a completion/export status but required files are missing.")
    elif manifest_path.is_file():
        errors.append("Manifest exists but YAML frontmatter was not parsed.")

    print("FILE PRESENCE CHECK PASSED" if not errors else "FILE PRESENCE CHECK FAILED")
    print(f"Project: {project_dir}")
    print(f"Task mode: {args.task_mode}")
    print(f"Version: {version}")
    if errors:
        for error in errors:
            print(f"- {error}")
    else:
        print("- Required legacy output files are present.")
        print("- Physical fit is not confirmed by file presence.")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
