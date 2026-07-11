"""Create a standard versioned project workspace."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


TASK_MODES = (
    "original_product_design",
    "reference_based_reconstruction",
    "mesh_cleanup_and_remodel",
)
ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
TEMPLATES_DIR = ROOT / "templates"


def snake_case(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        raise ValueError("Project name must contain at least one letter or number.")
    return value


def normalize_version(value: str) -> str:
    value = value.strip().lower()
    if re.fullmatch(r"\d+", value):
        return f"v{int(value):02d}"
    if re.fullmatch(r"v\d+", value):
        return f"v{int(value[1:]):02d}"
    raise ValueError("Version must look like v01 or 1.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new OpenSCAD project.")
    parser.add_argument("--name", required=True, help="Project name or stem")
    parser.add_argument("--task-mode", required=True, choices=TASK_MODES)
    parser.add_argument("--printer", default="NOT SPECIFIED")
    parser.add_argument("--material", default="NOT SPECIFIED")
    parser.add_argument("--version", default="v01")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting generated starter files in an existing project.",
    )
    return parser.parse_args()


def copy_template_tree(project_dir: Path) -> None:
    template_dir = PROJECTS_DIR / "_template"
    if template_dir.is_dir() and not project_dir.exists():
        shutil.copytree(template_dir, project_dir)
        return

    for folder in ("source", "exports", "notes", "previews"):
        (project_dir / folder).mkdir(parents=True, exist_ok=True)


def read_template(name: str, fallback: str) -> str:
    path = TEMPLATES_DIR / name
    if path.is_file():
        return path.read_text(encoding="utf-8-sig")
    return fallback


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    if path.exists() and force:
        print(f"Overwriting generated file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_common_tokens(text: str, stem: str, version: str, task_mode: str, printer: str, material: str) -> str:
    replacements = {
        "example_project": stem,
        "example_multi_part": stem,
        "<project_stem>": stem,
        'project_stem = "example_project";': f'project_stem = "{stem}";',
        'project_stem = "example_multi_part";': f'project_stem = "{stem}";',
        'version = "v01";': f'version = "{version}";',
        'printer_name = "Bambu Lab P2S";': f'printer_name = "{printer}";',
        'material = "PETG";': f'material = "{material}";',
        'material = "petg";': f'material = "{material.lower()}";',
        "// project_stem: example_project": f"// project_stem: {stem}",
        "// project_stem: example_multi_part": f"// project_stem: {stem}",
        "// version: v01": f"// version: {version}",
        "// printer_name: Bambu Lab P2S": f"// printer_name: {printer}",
        "// material: PETG": f"// material: {material}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def set_frontmatter_value(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^{re.escape(key)}:.*$")
    replacement = f"{key}: {value}"
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return text


def manifest_text(stem: str, version: str, task_mode: str) -> str:
    body = read_template("project_manifest.md", "# Project Manifest\n")
    body = replace_common_tokens(body, stem, version, task_mode, "NOT SPECIFIED", "NOT SPECIFIED")
    for key, value in {
        "project_stem": stem,
        "version": version,
        "task_mode": task_mode,
        "status": "bootstrap draft",
        "source_file": f"source/{stem}_{version}.scad",
        "export_file": f"exports/{stem}_{version}.stl",
        "notes_file": f"notes/{stem}_{version}_notes.md",
        "review_report": f"notes/{stem}_{version}_review_report.md",
    }.items():
        body = set_frontmatter_value(body, key, value)
    return body


def notes_text(task_mode: str) -> str:
    if task_mode == "original_product_design":
        return read_template("original_design_notes.md", "# Original Design Notes\n")
    return read_template("reconstruction_notes.md", "# Reconstruction Notes\n").replace(
        "`reference_based_reconstruction`", f"`{task_mode}`"
    )


def create_files(project_dir: Path, stem: str, version: str, task_mode: str, printer: str, material: str, force: bool) -> None:
    scad_template = read_template("parametric_part_template.scad", "// OpenSCAD template\ncube([10, 10, 10]);\n")
    scad_text = replace_common_tokens(scad_template, stem, version, task_mode, printer, material)
    write_file(project_dir / "source" / f"{stem}_{version}.scad", scad_text, force)

    notes = notes_text(task_mode)
    notes = replace_common_tokens(notes, stem, version, task_mode, printer, material)
    notes = notes.replace("- printer:", f"- printer: {printer}")
    notes = notes.replace("- material:", f"- material: {material}")
    write_file(project_dir / "notes" / f"{stem}_{version}_notes.md", notes, force)

    manifest = manifest_text(stem, version, task_mode)
    manifest = manifest.replace("status: bootstrap draft", "status: bootstrap draft")
    manifest = manifest.replace("preview_files: []", "preview_files: []")
    write_file(project_dir / "notes" / f"{stem}_{version}_manifest.md", manifest, force)

    extra_templates = [
        ("measurement_notes_template.md", f"{stem}_{version}_measurement_notes.md"),
        ("printability_review_template.md", f"{stem}_{version}_printability_review.md"),
        ("release_notes_template.md", f"{stem}_{version}_release_notes.md"),
        ("review_report.md", f"{stem}_{version}_review_report.md"),
    ]
    for template_name, output_name in extra_templates:
        content = replace_common_tokens(
            read_template(template_name, f"# {output_name}\n"),
            stem,
            version,
            task_mode,
            printer,
            material,
        )
        write_file(project_dir / "notes" / output_name, content, force)

    if task_mode in {"reference_based_reconstruction", "mesh_cleanup_and_remodel"}:
        for template_name, output_name in [
            ("reconstruction_checklist.md", f"{stem}_{version}_reconstruction_checklist.md"),
            ("reference_comparison_log.md", f"{stem}_{version}_reference_comparison_log.md"),
        ]:
            content = replace_common_tokens(
                read_template(template_name, f"# {output_name}\n"),
                stem,
                version,
                task_mode,
                printer,
                material,
            )
            write_file(project_dir / "notes" / output_name, content, force)

        bootstrap_note = (
            "# Bootstrap Notes\n\n"
            "This reconstruction project is a bootstrap draft. Do not begin final fit geometry "
            "until target part, reused parts, not-modeled items, authoritative references, "
            "anchor dimensions, protected interfaces, and low-confidence zones are recorded.\n"
        )
        write_file(project_dir / "notes" / f"{stem}_{version}_bootstrap_notes.md", bootstrap_note, force)


def main() -> int:
    args = parse_args()
    try:
        stem = snake_case(args.name)
        version = normalize_version(args.version)
    except ValueError as exc:
        print("FAIL")
        print(str(exc))
        return 1

    project_dir = PROJECTS_DIR / stem
    if project_dir.exists() and not args.force:
        print("FAIL")
        print(f"Project already exists: {project_dir}")
        print("Use --force only if you intend to overwrite generated starter files.")
        return 1

    try:
        copy_template_tree(project_dir)
        create_files(project_dir, stem, version, args.task_mode, args.printer, args.material, args.force)
    except FileExistsError as exc:
        print("FAIL")
        print(str(exc))
        return 1

    print("PASS")
    print(f"Project created: {project_dir}")
    print(f"Stem: {stem}")
    print(f"Version: {version}")
    print(f"Task mode: {args.task_mode}")
    print(f"Source: {project_dir / 'source' / f'{stem}_{version}.scad'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
