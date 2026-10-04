"""Legacy structural validation with a mandatory-by-default OpenSCAD check."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

from _openscad_cli import OpenSCADNotFound, print_failure, run_openscad


ASSIGNMENT_RE = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=.+")
MODULE_RE = re.compile(r"module\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{\s*\}", re.DOTALL)
MAGIC_NUMBER_RE = re.compile(
    r"\b(?:cube|translate|rotate|scale|cylinder|sphere)\s*\(\s*(?:\[)?\s*-?\d+(?:\.\d+)?"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate OpenSCAD source.")
    parser.add_argument("input", help="Path to the .scad file")
    parser.add_argument(
        "--no-openscad",
        action="store_true",
        help=(
            "Run structural checks only. This cannot establish the scad_compiled "
            "workflow state."
        ),
    )
    return parser.parse_args()


def strip_comments_and_strings(text: str) -> str:
    result: list[str] = []
    index = 0
    in_block = False
    in_line = False
    in_string = False
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if in_line:
            if char == "\n":
                in_line = False
                result.append(char)
            else:
                result.append(" ")
            index += 1
            continue

        if in_block:
            if char == "*" and next_char == "/":
                in_block = False
                result.extend("  ")
                index += 2
            else:
                result.append("\n" if char == "\n" else " ")
                index += 1
            continue

        if in_string:
            if char == "\\":
                result.extend("  ")
                index += 2
                continue
            if char == '"':
                in_string = False
            result.append(" ")
            index += 1
            continue

        if char == "/" and next_char == "/":
            in_line = True
            result.extend("  ")
            index += 2
            continue
        if char == "/" and next_char == "*":
            in_block = True
            result.extend("  ")
            index += 2
            continue
        if char == '"':
            in_string = True
            result.append(" ")
            index += 1
            continue

        result.append(char)
        index += 1

    return "".join(result)


def balance_issues(text: str) -> list[str]:
    pairs = {"(": ")", "[": "]", "{": "}"}
    labels = {"(": "parentheses", "[": "brackets", "{": "braces"}
    stack: list[tuple[str, int]] = []
    issues: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for char in line:
            if char in pairs:
                stack.append((char, line_number))
            elif char in pairs.values():
                if not stack:
                    issues.append(f"Unmatched closing {char} on line {line_number}")
                    continue
                opener, opener_line = stack.pop()
                if pairs[opener] != char:
                    issues.append(
                        f"Mismatched {labels[opener]} opened on line {opener_line} and closed with {char} on line {line_number}"
                    )
    for opener, opener_line in stack:
        issues.append(f"Unclosed {labels[opener]} opened on line {opener_line}")
    return issues


def missing_semicolon_issues(text: str) -> list[str]:
    issues: list[str] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(("module ", "function ", "if ", "for ", "let ")):
            continue
        if line.endswith(("[", "(", ",")):
            continue
        if ASSIGNMENT_RE.match(line) and not line.endswith(";"):
            issues.append(f"Likely missing semicolon on assignment line {line_number}")
    return issues


def structural_checks(original: str, stripped: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(balance_issues(stripped))
    errors.extend(missing_semicolon_issues(stripped))

    for match in MODULE_RE.finditer(stripped):
        errors.append(f"Empty module detected: {match.group(1)}")

    lowered = original.lower()
    if "todo export later" in lowered or "export later" in lowered:
        errors.append("Source contains TODO/export-later claim.")

    placeholder_tokens = ("placeholder-only", "placeholder geometry", "example_project")
    if any(token in lowered for token in placeholder_tokens):
        errors.append("Source appears to contain placeholder-only geometry markers.")

    geometry_tokens = ("cube(", "cylinder(", "sphere(", "polyhedron(", "linear_extrude(")
    if not any(token in lowered.replace(" ", "") for token in geometry_tokens):
        errors.append("No obvious geometry primitives found.")

    if "stl export status" in lowered and "success" in lowered:
        warnings.append("SCAD source appears to contain artifact status claims; keep artifact claims in notes/manifest.")

    magic_hits = MAGIC_NUMBER_RE.findall(stripped)
    if len(magic_hits) >= 8:
        warnings.append("Many direct numeric geometry calls found; prefer named parameters for critical dimensions.")

    if re.search(r"d\s*=\s*\d+(?:\.\d+)?", stripped) and "screw_diameter" not in stripped:
        warnings.append("Direct hole diameter values found; consider named screw or clearance variables.")

    return errors, warnings


def openscad_compile_check(input_path: Path) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="scad_validate_") as temp_dir:
        output_path = Path(temp_dir) / "validate.csg"
        result = run_openscad(["-o", str(output_path), str(input_path)])
        if result.returncode != 0:
            print_failure(result)
            return ["OpenSCAD compile check failed."]
    return []


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)

    if not input_path.is_file():
        print("SCAD CHECK FAILED")
        print(f"SCAD file not found: {input_path}")
        return 1

    text = input_path.read_text(encoding="utf-8-sig")
    stripped = strip_comments_and_strings(text)
    errors, warnings = structural_checks(text, stripped)

    if not args.no_openscad:
        try:
            errors.extend(openscad_compile_check(input_path))
        except OpenSCADNotFound:
            errors.append("OpenSCAD not found; compile check is required.")

    print("SCAD CHECK PASSED" if not errors else "SCAD CHECK FAILED")
    print(f"SCAD checked: {input_path}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if args.no_openscad and not errors:
        print("NOTICE: Structural checks only; workflow state scad_compiled was not reached.")
    print("Physical fit: NOT CONFIRMED")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
