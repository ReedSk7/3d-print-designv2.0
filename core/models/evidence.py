"""Immutable owner-recorded fit evidence models.

These records bind manual observations to exact, computationally generated
artifacts.  They deliberately do not mutate a generation manifest or project
specification and make no claim beyond the interfaces explicitly recorded.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Mapping, Sequence

from core.units.conversion import as_decimal
from core.workflow.states import WorkflowState


def _required_text(value: object, label: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{label} cannot be empty.")
    return text


def _digest(value: object, label: str) -> str:
    digest = str(value)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest.")
    return digest


def _aware_datetime(value: object, label: str) -> str:
    text = _required_text(value, label)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 date-time.") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone.")
    return text


def _decimal_text(value: Decimal) -> str:
    """Render a finite Decimal without exponent notation or float conversion."""

    number = as_decimal(value)
    return format(number, "f")


@dataclass(frozen=True, slots=True)
class FileBinding:
    """Path, byte length, and digest for bytes verified in one read."""

    path: str
    sha256: str
    size_bytes: int

    def __post_init__(self) -> None:
        path = _required_text(self.path, "Evidence file binding path")
        if "\\" in path:
            path = path.replace("\\", "/")
        if path.startswith("/") or ".." in path.split("/"):
            raise ValueError("Evidence file binding paths must be safe relative paths.")
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "sha256", _digest(self.sha256, "Evidence file binding sha256"))
        if isinstance(self.size_bytes, bool) or int(self.size_bytes) < 0:
            raise ValueError("Evidence file binding size_bytes cannot be negative.")
        object.__setattr__(self, "size_bytes", int(self.size_bytes))

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "FileBinding":
        return cls(
            path=str(document["path"]),
            sha256=str(document["sha256"]),
            size_bytes=int(document["size_bytes"]),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True, slots=True)
class GeneratorBinding:
    generator_id: str
    generator_version: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "generator_id", _required_text(self.generator_id, "Generator ID"))
        object.__setattr__(
            self, "generator_version", _required_text(self.generator_version, "Generator version")
        )

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "GeneratorBinding":
        return cls(str(document["id"]), str(document["version"]))

    def to_dict(self) -> dict[str, str]:
        return {"id": self.generator_id, "version": self.generator_version}


@dataclass(frozen=True, slots=True)
class FitConfiguration:
    interface_parameter: str
    candidate_offsets_mm: tuple[Decimal, ...]
    selected_candidate_offset_mm: Decimal
    printer_profile: str
    material: str
    nozzle_diameter_mm: Decimal
    calibration_profile_id: str
    calibration_profile_version: str
    calibration_profile_sha256: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "interface_parameter",
            "printer_profile",
            "material",
            "calibration_profile_id",
            "calibration_profile_version",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), f"Fit configuration {field_name}"),
            )
        offsets = tuple(as_decimal(value) for value in self.candidate_offsets_mm)
        if not 2 <= len(offsets) <= 12 or len(set(offsets)) != len(offsets):
            raise ValueError("Fit configuration requires 2-12 unique candidate offsets.")
        selected = as_decimal(self.selected_candidate_offset_mm)
        if selected not in offsets:
            raise ValueError("Selected candidate offset is not present in the coupon candidates.")
        nozzle = as_decimal(self.nozzle_diameter_mm)
        if nozzle <= 0:
            raise ValueError("Fit configuration nozzle_diameter_mm must be positive.")
        object.__setattr__(self, "candidate_offsets_mm", offsets)
        object.__setattr__(self, "selected_candidate_offset_mm", selected)
        object.__setattr__(self, "nozzle_diameter_mm", nozzle)
        if self.calibration_profile_sha256 is not None:
            object.__setattr__(
                self,
                "calibration_profile_sha256",
                _digest(
                    self.calibration_profile_sha256,
                    "Calibration profile SHA-256",
                ),
            )

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "FitConfiguration":
        candidates = document["candidate_offsets_mm"]
        profile = document["calibration_profile"]
        if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
            raise TypeError("candidate_offsets_mm must be an array.")
        if not isinstance(profile, Mapping):
            raise TypeError("calibration_profile must be an object.")
        return cls(
            interface_parameter=str(document["interface_parameter"]),
            candidate_offsets_mm=tuple(as_decimal(value) for value in candidates),  # type: ignore[arg-type]
            selected_candidate_offset_mm=as_decimal(document["selected_candidate_offset_mm"]),  # type: ignore[arg-type]
            printer_profile=str(document["printer_profile"]),
            material=str(document["material"]),
            nozzle_diameter_mm=as_decimal(document["nozzle_diameter_mm"]),  # type: ignore[arg-type]
            calibration_profile_id=str(profile["id"]),
            calibration_profile_version=str(profile["version"]),
            calibration_profile_sha256=(
                str(profile["sha256"])
                if profile.get("sha256") is not None
                else None
            ),
        )

    def to_dict(self) -> dict[str, object]:
        calibration_profile: dict[str, object] = {
            "id": self.calibration_profile_id,
            "version": self.calibration_profile_version,
        }
        if self.calibration_profile_sha256 is not None:
            calibration_profile["sha256"] = self.calibration_profile_sha256
        return {
            "interface_parameter": self.interface_parameter,
            "candidate_offsets_mm": [
                _decimal_text(value) for value in self.candidate_offsets_mm
            ],
            "selected_candidate_offset_mm": _decimal_text(
                self.selected_candidate_offset_mm
            ),
            "printer_profile": self.printer_profile,
            "material": self.material,
            "nozzle_diameter_mm": _decimal_text(self.nozzle_diameter_mm),
            "calibration_profile": calibration_profile,
        }


@dataclass(frozen=True, slots=True)
class FitCouponOutcome:
    tested_by: str
    tested_at: str
    acceptance_criterion: str
    observed_result: str
    passed: bool
    notes: str

    def __post_init__(self) -> None:
        for field_name in ("tested_by", "acceptance_criterion", "observed_result"):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), f"Fit result {field_name}"),
            )
        object.__setattr__(self, "tested_at", _aware_datetime(self.tested_at, "Fit result tested_at"))
        if type(self.passed) is not bool:
            raise ValueError("Fit result passed must be true or false.")
        object.__setattr__(self, "notes", str(self.notes))

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "FitCouponOutcome":
        return cls(
            tested_by=str(document["tested_by"]),
            tested_at=str(document["tested_at"]),
            acceptance_criterion=str(document["acceptance_criterion"]),
            observed_result=str(document["observed_result"]),
            passed=document["passed"] if type(document["passed"]) is bool else None,  # type: ignore[arg-type]
            notes=str(document["notes"]),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "tested_by": self.tested_by,
            "tested_at": self.tested_at,
            "acceptance_criterion": self.acceptance_criterion,
            "observed_result": self.observed_result,
            "passed": self.passed,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class FitCouponResultEvidence:
    coupon_project_id: str
    coupon_project_version: str
    generator: GeneratorBinding
    manifest: FileBinding
    stl: FileBinding
    specification_snapshot: FileBinding
    configuration: FitConfiguration
    result: FitCouponOutcome
    created_at: str
    source_project_id: str | None = None
    source_project_version: str | None = None
    source_spec_sha256: str | None = None
    schema_version: str = "1.0"
    evidence_kind: str = "fit_coupon_result"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0" or self.evidence_kind != "fit_coupon_result":
            raise ValueError("Unsupported fit-result evidence schema or kind.")
        object.__setattr__(
            self, "coupon_project_id", _required_text(self.coupon_project_id, "Coupon project ID")
        )
        object.__setattr__(
            self,
            "coupon_project_version",
            _required_text(self.coupon_project_version, "Coupon project version"),
        )
        source_binding = (
            self.source_project_id,
            self.source_project_version,
            self.source_spec_sha256,
        )
        if any(value is not None for value in source_binding) and not all(
            value is not None for value in source_binding
        ):
            raise ValueError(
                "Fit-result originating-source fields must be supplied together."
            )
        if self.source_project_id is not None:
            object.__setattr__(
                self,
                "source_project_id",
                _required_text(self.source_project_id, "Source project ID"),
            )
            object.__setattr__(
                self,
                "source_project_version",
                _required_text(self.source_project_version, "Source project version"),
            )
            object.__setattr__(
                self,
                "source_spec_sha256",
                _digest(self.source_spec_sha256, "Source specification SHA-256"),
            )
        object.__setattr__(self, "created_at", _aware_datetime(self.created_at, "Evidence created_at"))

    @property
    def defensible_workflow_state(self) -> WorkflowState:
        return (
            WorkflowState.FIT_COUPON_PASSED
            if self.result.passed
            else WorkflowState.FIT_COUPON_GENERATED
        )

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "FitCouponResultEvidence":
        coupon = document["coupon"]
        bindings = document["bindings"]
        configuration = document["configuration"]
        result = document["result"]
        if not all(isinstance(value, Mapping) for value in (coupon, bindings, configuration, result)):
            raise TypeError("Fit-result evidence sections must be objects.")
        generator = coupon["generator"]  # type: ignore[index]
        if not isinstance(generator, Mapping):
            raise TypeError("Fit-result generator binding must be an object.")
        instance = cls(
            coupon_project_id=str(coupon["project_id"]),  # type: ignore[index]
            coupon_project_version=str(coupon["project_version"]),  # type: ignore[index]
            generator=GeneratorBinding.from_dict(generator),
            manifest=FileBinding.from_dict(bindings["manifest"]),  # type: ignore[arg-type,index]
            stl=FileBinding.from_dict(bindings["stl"]),  # type: ignore[arg-type,index]
            specification_snapshot=FileBinding.from_dict(bindings["specification_snapshot"]),  # type: ignore[arg-type,index]
            configuration=FitConfiguration.from_dict(configuration),  # type: ignore[arg-type]
            result=FitCouponOutcome.from_dict(result),  # type: ignore[arg-type]
            created_at=str(document["created_at"]),
            source_project_id=(
                str(coupon["source_project_id"])  # type: ignore[index]
                if coupon.get("source_project_id") is not None  # type: ignore[union-attr]
                else None
            ),
            source_project_version=(
                str(coupon["source_project_version"])  # type: ignore[index]
                if coupon.get("source_project_version") is not None  # type: ignore[union-attr]
                else None
            ),
            source_spec_sha256=(
                str(coupon["source_spec_sha256"])  # type: ignore[index]
                if coupon.get("source_spec_sha256") is not None  # type: ignore[union-attr]
                else None
            ),
            schema_version=str(document["schema_version"]),
            evidence_kind=str(document["evidence_kind"]),
        )
        if str(document.get("defensible_workflow_state")) != instance.defensible_workflow_state.value:
            raise ValueError("Fit-result evidence workflow state is inconsistent with passed result.")
        return instance

    def to_dict(self) -> dict[str, object]:
        coupon: dict[str, object] = {
            "project_id": self.coupon_project_id,
            "project_version": self.coupon_project_version,
            "generator": self.generator.to_dict(),
            "generation_mode": "fit_coupon",
            "generation_workflow_state": WorkflowState.FIT_COUPON_GENERATED.value,
        }
        if self.source_project_id is not None:
            coupon.update(
                {
                    "source_project_id": self.source_project_id,
                    "source_project_version": self.source_project_version,
                    "source_spec_sha256": self.source_spec_sha256,
                }
            )
        return {
            "schema_version": self.schema_version,
            "evidence_kind": self.evidence_kind,
            "created_at": self.created_at,
            "coupon": coupon,
            "bindings": {
                "manifest": self.manifest.to_dict(),
                "stl": self.stl.to_dict(),
                "specification_snapshot": self.specification_snapshot.to_dict(),
            },
            "configuration": self.configuration.to_dict(),
            "result": self.result.to_dict(),
            "defensible_workflow_state": self.defensible_workflow_state.value,
            "complete_part_physical_fit_confirmed": False,
        }


@dataclass(frozen=True, slots=True)
class InterfaceFitResult:
    interface_parameter: str
    acceptance_criterion: str
    observed_result: str
    passed: bool
    notes: str = ""

    def __post_init__(self) -> None:
        for field_name in ("interface_parameter", "acceptance_criterion", "observed_result"):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), f"Interface result {field_name}"),
            )
        if type(self.passed) is not bool:
            raise ValueError("Interface result passed must be true or false.")
        object.__setattr__(self, "notes", str(self.notes))

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "InterfaceFitResult":
        return cls(
            interface_parameter=str(document["interface_parameter"]),
            acceptance_criterion=str(document["acceptance_criterion"]),
            observed_result=str(document["observed_result"]),
            passed=document["passed"] if type(document["passed"]) is bool else None,  # type: ignore[arg-type]
            notes=str(document.get("notes", "")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "interface_parameter": self.interface_parameter,
            "acceptance_criterion": self.acceptance_criterion,
            "observed_result": self.observed_result,
            "passed": self.passed,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class MeasuredDimension:
    parameter_name: str
    measured_value: Decimal
    units: str
    measurement_source: str
    notes: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameter_name", _required_text(self.parameter_name, "Measured parameter"))
        object.__setattr__(self, "measured_value", as_decimal(self.measured_value))
        if self.units not in {"mm", "inch"}:
            raise ValueError("Measured dimension units must be mm or inch.")
        object.__setattr__(
            self, "measurement_source", _required_text(self.measurement_source, "Measurement source")
        )
        object.__setattr__(self, "notes", str(self.notes))

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "MeasuredDimension":
        return cls(
            parameter_name=str(document["parameter_name"]),
            measured_value=as_decimal(document["measured_value"]),  # type: ignore[arg-type]
            units=str(document["units"]),
            measurement_source=str(document["measurement_source"]),
            notes=str(document.get("notes", "")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "parameter_name": self.parameter_name,
            "measured_value": _decimal_text(self.measured_value),
            "units": self.units,
            "measurement_source": self.measurement_source,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class PhysicalFitEvidence:
    project_id: str
    project_version: str
    generator: GeneratorBinding
    manifest: FileBinding
    stl: FileBinding
    scad: FileBinding
    specification_snapshot: FileBinding
    confirmed_by: str
    confirmed_at: str
    interface_results: tuple[InterfaceFitResult, ...]
    measured_dimensions: tuple[MeasuredDimension, ...]
    notes: str
    created_at: str
    schema_version: str = "1.0"
    evidence_kind: str = "physical_fit_confirmation"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0" or self.evidence_kind != "physical_fit_confirmation":
            raise ValueError("Unsupported physical-fit evidence schema or kind.")
        for field_name in ("project_id", "project_version", "confirmed_by"):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), f"Physical evidence {field_name}"),
            )
        object.__setattr__(
            self, "confirmed_at", _aware_datetime(self.confirmed_at, "Physical confirmation time")
        )
        object.__setattr__(self, "created_at", _aware_datetime(self.created_at, "Evidence created_at"))
        object.__setattr__(self, "interface_results", tuple(self.interface_results))
        object.__setattr__(self, "measured_dimensions", tuple(self.measured_dimensions))
        object.__setattr__(self, "notes", str(self.notes))
        if not self.interface_results:
            raise ValueError("Physical-fit confirmation requires interface results.")
        names = [result.interface_parameter for result in self.interface_results]
        if len(set(names)) != len(names):
            raise ValueError("Physical-fit interface results cannot contain duplicates.")
        if not all(result.passed for result in self.interface_results):
            raise ValueError("Physical-fit confirmation requires every protected interface to pass.")

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "PhysicalFitEvidence":
        part = document["full_part"]
        bindings = document["bindings"]
        confirmation = document["confirmation"]
        if not all(isinstance(value, Mapping) for value in (part, bindings, confirmation)):
            raise TypeError("Physical-fit evidence sections must be objects.")
        generator = part["generator"]  # type: ignore[index]
        interface_results = confirmation["interface_results"]  # type: ignore[index]
        dimensions = confirmation["measured_dimensions"]  # type: ignore[index]
        if not isinstance(generator, Mapping):
            raise TypeError("Physical-fit generator binding must be an object.")
        if not isinstance(interface_results, Sequence) or isinstance(interface_results, (str, bytes)):
            raise TypeError("interface_results must be an array.")
        if not isinstance(dimensions, Sequence) or isinstance(dimensions, (str, bytes)):
            raise TypeError("measured_dimensions must be an array.")
        instance = cls(
            project_id=str(part["project_id"]),  # type: ignore[index]
            project_version=str(part["project_version"]),  # type: ignore[index]
            generator=GeneratorBinding.from_dict(generator),
            manifest=FileBinding.from_dict(bindings["manifest"]),  # type: ignore[arg-type,index]
            stl=FileBinding.from_dict(bindings["stl"]),  # type: ignore[arg-type,index]
            scad=FileBinding.from_dict(bindings["scad"]),  # type: ignore[arg-type,index]
            specification_snapshot=FileBinding.from_dict(bindings["specification_snapshot"]),  # type: ignore[arg-type,index]
            confirmed_by=str(confirmation["confirmed_by"]),  # type: ignore[index]
            confirmed_at=str(confirmation["confirmed_at"]),  # type: ignore[index]
            interface_results=tuple(InterfaceFitResult.from_dict(item) for item in interface_results),  # type: ignore[arg-type]
            measured_dimensions=tuple(MeasuredDimension.from_dict(item) for item in dimensions),  # type: ignore[arg-type]
            notes=str(confirmation["notes"]),  # type: ignore[index]
            created_at=str(document["created_at"]),
            schema_version=str(document["schema_version"]),
            evidence_kind=str(document["evidence_kind"]),
        )
        if str(document.get("defensible_workflow_state")) != WorkflowState.PHYSICAL_FIT_CONFIRMED.value:
            raise ValueError("Physical-fit evidence workflow state must be physical_fit_confirmed.")
        return instance

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "evidence_kind": self.evidence_kind,
            "created_at": self.created_at,
            "full_part": {
                "project_id": self.project_id,
                "project_version": self.project_version,
                "generator": self.generator.to_dict(),
                "generation_mode": "full_part",
                "generation_workflow_state": WorkflowState.FULL_PART_EXPORTED.value,
            },
            "bindings": {
                "manifest": self.manifest.to_dict(),
                "stl": self.stl.to_dict(),
                "scad": self.scad.to_dict(),
                "specification_snapshot": self.specification_snapshot.to_dict(),
            },
            "confirmation": {
                "confirmed_by": self.confirmed_by,
                "confirmed_at": self.confirmed_at,
                "interface_results": [item.to_dict() for item in self.interface_results],
                "measured_dimensions": [item.to_dict() for item in self.measured_dimensions],
                "notes": self.notes,
            },
            "defensible_workflow_state": WorkflowState.PHYSICAL_FIT_CONFIRMED.value,
            "claims": ["physical fit for the recorded protected interfaces"],
            "not_evaluated": [
                "durability",
                "load rating",
                "temperature performance",
                "safety qualification",
                "regulatory or product certification",
            ],
        }
