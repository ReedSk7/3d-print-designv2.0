"""JSON-Schema-first project specification loading and validation."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from core.models.measurements import MeasurementContractError
from core.models.spec import ProjectSpec


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_SPEC_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "project-spec-v1.schema.json"


class SpecificationError(ValueError):
    """Raised when a specification or generator parameter document is invalid."""

    def __init__(self, issues: str | list[str] | tuple[str, ...]) -> None:
        if isinstance(issues, str):
            issues = (issues,)
        self.issues = tuple(issues)
        super().__init__("; ".join(self.issues))


def _json_path(parts: object) -> str:
    rendered = "$"
    for part in parts:  # type: ignore[union-attr]
        if isinstance(part, int):
            rendered += f"[{part}]"
        else:
            rendered += f".{part}"
    return rendered


def _validation_messages(validator: Draft202012Validator, document: object) -> tuple[str, ...]:
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    return tuple(f"{_json_path(error.absolute_path)}: {error.message}" for error in errors)


def validate_parameter_document(schema: Mapping[str, object], data: object) -> None:
    """Validate generator parameters against a Draft 2020-12 JSON Schema.

    Generator packages can call this helper with their own parameter schema.
    It raises ``SpecificationError`` with stable JSON paths on failure.
    """

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise SpecificationError(f"Invalid parameter schema: {exc.message}") from exc
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    issues = _validation_messages(validator, data)
    if issues:
        raise SpecificationError(issues)


@lru_cache(maxsize=1)
def load_project_spec_schema() -> dict[str, object]:
    try:
        document = json.loads(PROJECT_SPEC_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecificationError(
            f"Could not load project specification schema {PROJECT_SPEC_SCHEMA_PATH}: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise SpecificationError("Project specification schema root must be an object.")
    try:
        Draft202012Validator.check_schema(document)
    except SchemaError as exc:
        raise SpecificationError(f"Project specification schema is invalid: {exc.message}") from exc
    return document


def load_decimal_json(path: Path) -> dict[str, object]:
    """Load a JSON object while retaining every written decimal digit."""

    try:
        document = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    except FileNotFoundError as exc:
        raise SpecificationError(f"Project specification not found: {path}") from exc
    except OSError as exc:
        raise SpecificationError(f"Could not read project specification {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SpecificationError(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(document, dict):
        raise SpecificationError("Project specification root must be a JSON object.")
    return document


def validate_project_document(document: Mapping[str, object]) -> None:
    schema = load_project_spec_schema()
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    issues = list(_validation_messages(validator, document))

    timestamps = document.get("timestamps")
    if isinstance(timestamps, Mapping):
        created_at = timestamps.get("created_at")
        updated_at = timestamps.get("updated_at")
        if isinstance(created_at, str) and isinstance(updated_at, str):
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                if updated < created:
                    issues.append("$.timestamps.updated_at: cannot precede created_at")
            except ValueError:
                # FormatChecker reports the detailed date-time issue.
                pass

    artifacts = document.get("generated_artifacts")
    if isinstance(artifacts, list):
        paths = [item.get("path") for item in artifacts if isinstance(item, Mapping)]
        duplicates = sorted({path for path in paths if path is not None and paths.count(path) > 1})
        if duplicates:
            issues.append(
                "$.generated_artifacts: duplicate artifact paths: "
                + ", ".join(str(path) for path in duplicates)
            )

    if issues:
        raise SpecificationError(tuple(issues))


def load_project_spec(path: str | Path) -> ProjectSpec:
    """Load, schema-validate, cross-check, and freeze a v1 project specification."""

    spec_path = Path(path)
    document = load_decimal_json(spec_path)
    validate_project_document(document)
    try:
        return ProjectSpec.from_dict(document)
    except (KeyError, TypeError, ValueError, MeasurementContractError) as exc:
        raise SpecificationError(f"Project specification domain validation failed: {exc}") from exc
