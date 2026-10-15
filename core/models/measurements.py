"""Measurement contracts and protected-interface enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Iterable, Mapping, Sequence

from core.units.conversion import DecimalLike, LengthUnit, as_decimal, normalize_unit, to_mm


class MeasurementAuthority(str, Enum):
    AUTHORITATIVE = "authoritative"
    SUPPORTING = "supporting"
    INFERRED = "inferred"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class MeasurementContract:
    parameter_name: str
    measured_value: Decimal
    units: LengthUnit
    measurement_source: str
    authority: MeasurementAuthority
    confidence_level: ConfidenceLevel
    tolerance: Decimal
    protected_interface: bool
    verification_notes: str

    def __post_init__(self) -> None:
        name = self.parameter_name.strip()
        source = self.measurement_source.strip()
        if not name:
            raise ValueError("Measurement parameter_name cannot be empty.")
        if not source:
            raise ValueError(f"Measurement source cannot be empty for {name!r}.")
        tolerance = as_decimal(self.tolerance)
        if tolerance < 0:
            raise ValueError(f"Measurement tolerance cannot be negative for {name!r}.")
        object.__setattr__(self, "parameter_name", name)
        object.__setattr__(self, "measurement_source", source)
        object.__setattr__(self, "measured_value", as_decimal(self.measured_value))
        object.__setattr__(self, "tolerance", tolerance)
        object.__setattr__(self, "units", normalize_unit(self.units))
        object.__setattr__(self, "authority", MeasurementAuthority(self.authority))
        object.__setattr__(self, "confidence_level", ConfidenceLevel(self.confidence_level))

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "MeasurementContract":
        return cls(
            parameter_name=str(document["parameter_name"]),
            measured_value=as_decimal(document["measured_value"]),  # type: ignore[arg-type]
            units=normalize_unit(str(document["units"])),
            measurement_source=str(document["measurement_source"]),
            authority=MeasurementAuthority(str(document["authority"])),
            confidence_level=ConfidenceLevel(str(document["confidence_level"])),
            tolerance=as_decimal(document["tolerance"]),  # type: ignore[arg-type]
            protected_interface=bool(document["protected_interface"]),
            verification_notes=str(document["verification_notes"]),
        )

    @property
    def measured_value_mm(self) -> Decimal:
        return to_mm(self.measured_value, self.units)

    @property
    def tolerance_mm(self) -> Decimal:
        return to_mm(self.tolerance, self.units)

    def to_dict(self) -> dict[str, object]:
        return {
            "parameter_name": self.parameter_name,
            "measured_value": self.measured_value,
            "units": self.units.value,
            "measurement_source": self.measurement_source,
            "authority": self.authority.value,
            "confidence_level": self.confidence_level.value,
            "tolerance": self.tolerance,
            "protected_interface": self.protected_interface,
            "verification_notes": self.verification_notes,
        }


@dataclass(frozen=True, slots=True)
class MeasurementIssue:
    code: str
    parameter_name: str
    message: str


class MeasurementContractError(ValueError):
    def __init__(self, issues: Sequence[MeasurementIssue]) -> None:
        self.issues = tuple(issues)
        super().__init__("; ".join(issue.message for issue in self.issues))


def _is_replacement(project_intent: object) -> bool:
    value = getattr(project_intent, "value", project_intent)
    return str(value).strip().lower() == "replacement"


def measurement_contract_issues(
    measurements: Sequence[MeasurementContract],
    project_intent: object,
    *,
    required_protected_parameters: Iterable[str] = (),
    parameter_values: Mapping[str, DecimalLike] | None = None,
    parameter_units: LengthUnit | str | None = None,
    enforce_authoritative: bool = True,
) -> tuple[MeasurementIssue, ...]:
    """Return safety issues for a measurement contract.

    For replacement work, the required set is the union of generator-declared
    protected parameters and measurements explicitly marked as protected.
    Each must have an authoritative, protected measurement.  When nominal
    parameter values are supplied, at least one authoritative measurement must
    agree with that nominal value within the recorded tolerance.
    """

    if not (_is_replacement(project_intent) and enforce_authoritative):
        return ()

    by_parameter: dict[str, list[MeasurementContract]] = {}
    for measurement in measurements:
        by_parameter.setdefault(measurement.parameter_name, []).append(measurement)

    required = {str(name).strip() for name in required_protected_parameters if str(name).strip()}
    required.update(
        measurement.parameter_name for measurement in measurements if measurement.protected_interface
    )

    issues: list[MeasurementIssue] = []
    for parameter_name in sorted(required):
        authoritative = [
            measurement
            for measurement in by_parameter.get(parameter_name, ())
            if measurement.protected_interface
            and measurement.authority is MeasurementAuthority.AUTHORITATIVE
        ]
        if not authoritative:
            issues.append(
                MeasurementIssue(
                    code="authoritative_protected_measurement_required",
                    parameter_name=parameter_name,
                    message=(
                        f"Replacement-part protected interface {parameter_name!r} requires "
                        "an authoritative measured dimension."
                    ),
                )
            )
            continue

        if parameter_values is None:
            continue
        if parameter_name not in parameter_values:
            issues.append(
                MeasurementIssue(
                    code="protected_parameter_value_missing",
                    parameter_name=parameter_name,
                    message=f"Protected parameter {parameter_name!r} is absent from generator parameters.",
                )
            )
            continue
        if parameter_units is None:
            raise ValueError("parameter_units is required when parameter_values are supplied.")

        parameter_mm = to_mm(parameter_values[parameter_name], parameter_units)
        if not any(
            abs(parameter_mm - measurement.measured_value_mm) <= measurement.tolerance_mm
            for measurement in authoritative
        ):
            issues.append(
                MeasurementIssue(
                    code="protected_parameter_outside_tolerance",
                    parameter_name=parameter_name,
                    message=(
                        f"Protected parameter {parameter_name!r} does not match an authoritative "
                        "measurement within its recorded tolerance."
                    ),
                )
            )

    return tuple(issues)


def validate_measurement_contract(
    measurements: Sequence[MeasurementContract],
    project_intent: object,
    *,
    required_protected_parameters: Iterable[str] = (),
    parameter_values: Mapping[str, DecimalLike] | None = None,
    parameter_units: LengthUnit | str | None = None,
    enforce_authoritative: bool = True,
) -> None:
    """Raise ``MeasurementContractError`` when a contract is unsafe to use."""

    issues = measurement_contract_issues(
        measurements,
        project_intent,
        required_protected_parameters=required_protected_parameters,
        parameter_values=parameter_values,
        parameter_units=parameter_units,
        enforce_authoritative=enforce_authoritative,
    )
    if issues:
        raise MeasurementContractError(issues)
