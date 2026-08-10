"""Printer/material/nozzle calibration profile models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Sequence

from core.units.conversion import as_decimal


NOZZLE_MATCH_TOLERANCE_MM = Decimal("0.000001")


class CalibrationStatus(str, Enum):
    UNVERIFIED_STARTER = "unverified_starter"
    PROVEN = "proven"


class CalibrationTestResult(str, Enum):
    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class CalibrationEvidence:
    evidence_id: str
    source_ref: str
    recorded_at: str
    measurement_tool: str
    nominal_mm: Decimal
    measured_mm: Decimal
    acceptance_tolerance_mm: Decimal
    result: CalibrationTestResult
    notes: str

    def __post_init__(self) -> None:
        for field_name in ("evidence_id", "source_ref", "recorded_at", "measurement_tool"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"Calibration evidence {field_name} cannot be empty.")
        object.__setattr__(self, "nominal_mm", as_decimal(self.nominal_mm))
        object.__setattr__(self, "measured_mm", as_decimal(self.measured_mm))
        tolerance = as_decimal(self.acceptance_tolerance_mm)
        if tolerance < 0:
            raise ValueError("Calibration acceptance_tolerance_mm cannot be negative.")
        object.__setattr__(self, "acceptance_tolerance_mm", tolerance)
        object.__setattr__(self, "result", CalibrationTestResult(self.result))
        try:
            recorded = datetime.fromisoformat(self.recorded_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Calibration evidence recorded_at must be an ISO-8601 date-time.") from exc
        if recorded.tzinfo is None:
            raise ValueError("Calibration evidence recorded_at must include a timezone.")
        if (
            self.result is CalibrationTestResult.PASSED
            and abs(self.measured_mm - self.nominal_mm) > tolerance
        ):
            raise ValueError(
                "Passed calibration evidence exceeds its recorded acceptance tolerance."
            )

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "CalibrationEvidence":
        return cls(
            evidence_id=str(document["evidence_id"]),
            source_ref=str(document["source_ref"]),
            recorded_at=str(document["recorded_at"]),
            measurement_tool=str(document["measurement_tool"]),
            nominal_mm=as_decimal(document["nominal_mm"]),  # type: ignore[arg-type]
            measured_mm=as_decimal(document["measured_mm"]),  # type: ignore[arg-type]
            acceptance_tolerance_mm=as_decimal(  # type: ignore[arg-type]
                document["acceptance_tolerance_mm"]
            ),
            result=CalibrationTestResult(str(document["result"])),
            notes=str(document["notes"]),
        )


@dataclass(frozen=True, slots=True)
class CalibrationValue:
    value: Decimal
    status: CalibrationStatus
    evidence: tuple[CalibrationEvidence, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", as_decimal(self.value))
        object.__setattr__(self, "status", CalibrationStatus(self.status))
        if self.status is CalibrationStatus.PROVEN:
            if not self.evidence:
                raise ValueError("A proven calibration value requires recorded measurement evidence.")
            if not any(
                item.result is CalibrationTestResult.PASSED for item in self.evidence
            ):
                raise ValueError(
                    "A proven calibration value requires at least one passed measurement record."
                )

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "CalibrationValue":
        evidence_documents = document.get("evidence", [])
        if not isinstance(evidence_documents, Sequence) or isinstance(
            evidence_documents, (str, bytes)
        ):
            raise TypeError("Calibration evidence must be an array.")
        return cls(
            value=as_decimal(document["value"]),  # type: ignore[arg-type]
            status=CalibrationStatus(str(document["status"])),
            evidence=tuple(
                CalibrationEvidence.from_dict(item)  # type: ignore[arg-type]
                for item in evidence_documents
            ),
            notes=str(document.get("notes", "")),
        )

    @property
    def is_proven(self) -> bool:
        return self.status is CalibrationStatus.PROVEN


@dataclass(frozen=True, slots=True)
class CalibrationProfile:
    schema_version: str
    profile_id: str
    version: str
    printer_profile: str
    material: str
    nozzle_diameter_mm: Decimal | None
    hole_offset_mm: CalibrationValue
    shaft_offset_mm: CalibrationValue
    press_fit_offset_mm: CalibrationValue
    slip_fit_offset_mm: CalibrationValue
    scale_x: CalibrationValue
    scale_y: CalibrationValue
    scale_z: CalibrationValue
    notes: str

    def __post_init__(self) -> None:
        if self.nozzle_diameter_mm is not None:
            nozzle = as_decimal(self.nozzle_diameter_mm)
            if nozzle <= 0:
                raise ValueError("Calibration profile nozzle diameter must be positive.")
            object.__setattr__(self, "nozzle_diameter_mm", nozzle)
        for axis_name in ("scale_x", "scale_y", "scale_z"):
            if getattr(self, axis_name).value <= 0:
                raise ValueError(f"Calibration {axis_name} must be greater than zero.")

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "CalibrationProfile":
        corrections = document["corrections"]
        scales = document["scale_corrections"]
        if not isinstance(corrections, Mapping) or not isinstance(scales, Mapping):
            raise TypeError("Calibration corrections and scale_corrections must be objects.")
        nozzle = document.get("nozzle_diameter_mm")
        return cls(
            schema_version=str(document["schema_version"]),
            profile_id=str(document["profile_id"]),
            version=str(document["version"]),
            printer_profile=str(document["printer_profile"]),
            material=str(document["material"]),
            nozzle_diameter_mm=as_decimal(nozzle) if nozzle is not None else None,  # type: ignore[arg-type]
            hole_offset_mm=CalibrationValue.from_dict(corrections["hole_offset_mm"]),  # type: ignore[arg-type]
            shaft_offset_mm=CalibrationValue.from_dict(corrections["shaft_offset_mm"]),  # type: ignore[arg-type]
            press_fit_offset_mm=CalibrationValue.from_dict(corrections["press_fit_offset_mm"]),  # type: ignore[arg-type]
            slip_fit_offset_mm=CalibrationValue.from_dict(corrections["slip_fit_offset_mm"]),  # type: ignore[arg-type]
            scale_x=CalibrationValue.from_dict(scales["x"]),  # type: ignore[arg-type]
            scale_y=CalibrationValue.from_dict(scales["y"]),  # type: ignore[arg-type]
            scale_z=CalibrationValue.from_dict(scales["z"]),  # type: ignore[arg-type]
            notes=str(document["notes"]),
        )

    @property
    def values(self) -> Mapping[str, CalibrationValue]:
        return {
            "hole_offset_mm": self.hole_offset_mm,
            "shaft_offset_mm": self.shaft_offset_mm,
            "press_fit_offset_mm": self.press_fit_offset_mm,
            "slip_fit_offset_mm": self.slip_fit_offset_mm,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "scale_z": self.scale_z,
        }

    @property
    def is_fully_proven(self) -> bool:
        return all(value.is_proven for value in self.values.values())

    @property
    def unverified_fields(self) -> tuple[str, ...]:
        return tuple(name for name, value in self.values.items() if not value.is_proven)

    def require_proven_fields(self, field_names: Sequence[str]) -> None:
        """Reject use of unproven corrections selected by a generator."""

        unknown = sorted(set(field_names) - self.values.keys())
        if unknown:
            raise CalibrationProfileError(
                ["Unknown calibration field(s): " + ", ".join(unknown)]
            )
        unproven = sorted(name for name in field_names if not self.values[name].is_proven)
        if unproven:
            raise CalibrationProfileError(
                ["Required calibration field(s) are not proven: " + ", ".join(unproven)]
            )

    def applies_to(self, printer_profile: str, material: str, nozzle_diameter_mm: Decimal) -> bool:
        printer_matches = self.printer_profile == "*" or self.printer_profile == printer_profile
        material_matches = self.material == "*" or self.material.lower() == material.lower()
        nozzle_matches = (
            self.nozzle_diameter_mm is None
            or abs(self.nozzle_diameter_mm - as_decimal(nozzle_diameter_mm))
            <= NOZZLE_MATCH_TOLERANCE_MM
        )
        return printer_matches and material_matches and nozzle_matches


class CalibrationProfileError(ValueError):
    def __init__(self, issues: Sequence[str]) -> None:
        self.issues = tuple(issues)
        super().__init__("; ".join(self.issues))


def calibration_profile_issues(profile: CalibrationProfile) -> tuple[str, ...]:
    issues: list[str] = []
    if profile.schema_version != "1.0":
        issues.append(f"Unsupported calibration schema version: {profile.schema_version!r}.")

    proven_values = [name for name, value in profile.values.items() if value.is_proven]
    if proven_values:
        if profile.printer_profile == "*" or profile.material == "*" or profile.nozzle_diameter_mm is None:
            issues.append(
                "Profiles containing proven values must identify an exact printer, material, and nozzle."
            )
        for name in proven_values:
            if not profile.values[name].evidence:
                issues.append(f"Proven calibration value {name!r} has no evidence.")
    return tuple(issues)


def validate_calibration_profile(profile: CalibrationProfile) -> None:
    issues = calibration_profile_issues(profile)
    if issues:
        raise CalibrationProfileError(issues)
