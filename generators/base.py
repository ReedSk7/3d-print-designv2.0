"""Shared contracts for deterministic part generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from string import Template
from typing import Any, Mapping


MM_PER_INCH = Decimal("25.4")


class GeneratorValidationError(ValueError):
    """Raised when generator parameters cannot produce safe deterministic geometry."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(errors))


@dataclass(frozen=True)
class GeneratorMetadata:
    generator_id: str
    version: str
    name: str
    description: str
    expected_body_count: int = 1
    supported_artifacts: tuple[str, ...] = ("full_part", "fit_coupon")


@dataclass(frozen=True)
class GenerationContext:
    """Resolved non-geometry inputs shared by all generators.

    Calibration offsets are signed CAD diameter additions in millimeters. Scale
    corrections are multiplicative XYZ factors. The bundled starter profile is
    neutral and explicitly unverified.
    """

    input_units: str
    nozzle_diameter_mm: Decimal
    fit_class: str
    calibration_offsets_mm: Mapping[str, Decimal] = field(default_factory=dict)
    scale_correction: tuple[Decimal, Decimal, Decimal] = (
        Decimal("1"),
        Decimal("1"),
        Decimal("1"),
    )
    generation_mode: str = "full_part"
    coupon_parameter: str | None = None
    coupon_offsets_mm: tuple[Decimal, ...] = ()
    accepted_coupon_parameter: str | None = None
    accepted_coupon_offset_mm: Decimal = Decimal("0")


@dataclass(frozen=True)
class GenerationResult:
    source: str
    expected_bounds_mm: tuple[Decimal, Decimal, Decimal]
    resolved_parameters_mm: Mapping[str, Any]
    nominal_protected_dimensions_mm: Mapping[str, Decimal]
    warnings: tuple[str, ...] = ()
    expected_body_count: int = 1
    artifact_kind: str = "full_part"


def as_decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool):
        raise GeneratorValidationError([f"{label} must be a number, not a boolean."])
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise GeneratorValidationError([f"{label} must be a finite decimal number."]) from exc
    if not number.is_finite():
        raise GeneratorValidationError([f"{label} must be finite."])
    return number


def input_length_mm(value: Any, units: str, label: str) -> Decimal:
    number = as_decimal(value, label)
    normalized = units.strip().lower()
    if normalized in {"mm", "millimeter", "millimeters"}:
        return number
    if normalized in {"in", "inch", "inches"}:
        return number * MM_PER_INCH
    raise GeneratorValidationError([f"Unsupported input units for {label}: {units}"])


def scad_number(value: Any) -> str:
    number = as_decimal(value, "OpenSCAD value")
    if number == 0:
        return "0"
    text = format(number.normalize(), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def nested_value(mapping: Mapping[str, Any], path: str) -> Any:
    current: Any = mapping
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(path)
        current = current[part]
    return current


def load_template(module_file: str) -> Template:
    template_path = Path(module_file).with_name("template.scad")
    return Template(template_path.read_text(encoding="utf-8"))


def diameter_with_calibration(
    nominal_mm: Decimal,
    *,
    interface: str,
    fit_class: str,
    context: GenerationContext,
) -> Decimal:
    """Apply explicit signed calibration values without inventing defaults."""

    if interface not in {"hole", "shaft"}:
        raise ValueError(f"Unsupported interface kind: {interface}")
    offset = context.calibration_offsets_mm.get(f"{interface}_offset_mm", Decimal("0"))
    if fit_class == "slip":
        offset += context.calibration_offsets_mm.get("slip_fit_offset_mm", Decimal("0"))
    elif fit_class == "press":
        offset += context.calibration_offsets_mm.get("press_fit_offset_mm", Decimal("0"))
    elif fit_class != "nominal":
        raise GeneratorValidationError([f"Unsupported fit class: {fit_class}"])
    return nominal_mm + offset


def scaled_bounds(
    bounds: tuple[Decimal, Decimal, Decimal], context: GenerationContext
) -> tuple[Decimal, Decimal, Decimal]:
    return tuple(value * scale for value, scale in zip(bounds, context.scale_correction))  # type: ignore[return-value]


def scale_statement(context: GenerationContext) -> str:
    return "[{}]".format(
        ", ".join(scad_number(value) for value in context.scale_correction)
    )


class PartGenerator(ABC):
    metadata: GeneratorMetadata
    parameter_schema: Mapping[str, Any]
    defaults: Mapping[str, Any]

    @abstractmethod
    def generate(
        self, parameters: Mapping[str, Any], context: GenerationContext
    ) -> GenerationResult:
        """Validate parameters and render deterministic OpenSCAD source."""
