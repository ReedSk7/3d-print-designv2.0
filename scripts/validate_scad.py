"""Static and optional OpenSCAD validation for a .scad file."""

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
DIRECT_CYLINDER_RE = re.compile(r"\bcylinder\s*\((?P<args>[^;{}]*?)\)", re.DOTALL)
DIRECT_NUMERIC_DIAMETER_RE = re.compile(r"\b(?:d|d1|d2|r|r1|r2)\s*=\s*-?\d+(?:\.\d+)?\b")
SCREW_FEATURE_RE = re.compile(
    r"\b(?:screw|bolt|fastener|counterbore|countersink|washer|insert|thread)\b",
    re.IGNORECASE,
)
REQUIRED_PROJECT_PARAMETERS = ("wall_thickness", "fit_clearance", "nozzle_diameter", "material")
HARDWARE_LIBRARY_MARKERS = (
    "hardware_library.scad",
    "clearance_hole_d(",
    "clearance_hole(",
    "pilot_hole_d(",
    "pilot_hole(",
    "counterbore_d(",
    "counterbore_pocket(",
    "countersink_head_d(",
    "countersink_pocket(",
    "heat_set_insert_bore_d(",
    "heat_set_insert_pocket(",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate OpenSCAD source.")
    parser.add_argument("input", help="Path to the .scad file")
    parser.add_argument(
        "--no-openscad",
        action="store_true",
        help="Skip optional OpenSCAD compile check.",
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


def is_shared_hardware_library(input_path: Path) -> bool:
    return input_path.name == "hardware_library.scad" and input_path.parent.name == "standards"


def top_level_assignment_exists(text: str, name: str) -> bool:
    return re.search(rf"(?m)^\s*{re.escape(name)}\s*=", text) is not None


def hardware_library_used(original: str, stripped: str) -> bool:
    combined = f"{original}\n{stripped}"
    return any(marker in combined for marker in HARDWARE_LIBRARY_MARKERS)


def project_parameter_issues(stripped: str, input_path: Path) -> list[str]:
    if is_shared_hardware_library(input_path):
        return []

    issues: list[str] = []
    for parameter in REQUIRED_PROJECT_PARAMETERS:
        if not top_level_assignment_exists(stripped, parameter):
            issues.append(
                f"Missing required global parameter '{parameter}'. "
                "Declare it as a named project parameter or derive it from a profile before geometry."
            )
    return issues


def hardware_lint_issues(original: str, stripped: str, input_path: Path) -> list[str]:
    if is_shared_hardware_library(input_path):
        return []

    issues: list[str] = []
    uses_hardware = hardware_library_used(original, stripped)

    if SCREW_FEATURE_RE.search(stripped) and not uses_hardware:
        issues.append(
            "Screw/fastener feature names found, but standards/hardware_library.scad "
            "or its clearance/counterbore/countersink functions are not used."
        )

    for match in DIRECT_CYLINDER_RE.finditer(stripped):
        call_args = match.group("args")
        if DIRECT_NUMERIC_DIAMETER_RE.search(call_args):
            issues.append(
                "Direct numeric cylinder diameter/radius found. "
                "Use named parameters; for screw, bolt, insert, or clearance features use standards/hardware_library.scad."
            )
            break

    numeric_hardware_assignment = re.search(
        r"(?m)^\s*(?:screw|bolt|fastener|counterbore|countersink|insert|washer)[a-z0-9_]*"
        r"(?:diameter|depth|d|r)?\s*=\s*-?\d+(?:\.\d+)?\s*;",
        stripped,
    )
    if numeric_hardware_assignment and not uses_hardware:
        issues.append(
            "Numeric screw/fastener hardware assignment found without using standards/hardware_library.scad."
        )

    return issues


def structural_checks(original: str, stripped: str, input_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(balance_issues(stripped))
    errors.extend(missing_semicolon_issues(stripped))
    errors.extend(project_parameter_issues(stripped, input_path))
    errors.extend(hardware_lint_issues(original, stripped, input_path))

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

    if re.search(r"d\s*=\s*\d+(?:\.\d+)?", stripped):
        warnings.append("Direct hole diameter values found; use named variables or hardware library functions.")

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
        print("FAIL")
        print(f"SCAD file not found: {input_path}")
        return 1

    text = input_path.read_text(encoding="utf-8-sig")
    stripped = strip_comments_and_strings(text)
    errors, warnings = structural_checks(text, stripped, input_path)

    if not args.no_openscad:
        try:
            errors.extend(openscad_compile_check(input_path))
        except OpenSCADNotFound:
            warnings.append("OpenSCAD not found; skipped compile check.")

    print("PASS" if not errors else "FAIL")
    print(f"SCAD checked: {input_path}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
