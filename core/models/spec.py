"""Immutable domain model for project specification schema version 1.0."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Mapping, Sequence

from core.units.conversion import LengthUnit, as_decimal, normalize_unit, to_mm
from core.workflow.states import WorkflowState

from .artifacts import ArtifactRecord
from .measurements import MeasurementContract, validate_measurement_contract


class ProjectIntent(str, Enum):
    ORIGINAL = "original"
    REPLACEMENT = "replacement"


class GenerationMode(str, Enum):
    FULL_PART = "full_part"
    FIT_COUPON = "fit_coupon"


class PhysicalFitStatus(str, Enum):
    NOT_CONFIRMED = "not_confirmed"
    CONFIRMED = "confirmed"


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class ProjectIdentity:
    id: str
    name: str
    version: str
    intent: ProjectIntent

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "ProjectIdentity":
        return cls(
            id=str(document["id"]),
            name=str(document["name"]),
            version=str(document["version"]),
            intent=ProjectIntent(str(document["intent"])),
        )


@dataclass(frozen=True, slots=True)
class GeneratorSelection:
    id: str
    version: str
    parameters: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", _freeze(self.parameters))

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "GeneratorSelection":
        parameters = document["parameters"]
        if not isinstance(parameters, Mapping):
            raise TypeError("generator.parameters must be an object.")
        return cls(
            id=str(document["id"]),
            version=str(document["version"]),
            parameters=parameters,
        )


@dataclass(frozen=True, slots=True)
class FitCouponRequest:
    interface_parameter: str
    candidate_offsets: tuple[Decimal, ...]
    notes: str

    def __post_init__(self) -> None:
        name = self.interface_parameter.strip()
        offsets = tuple(as_decimal(value) for value in self.candidate_offsets)
        if not name:
            raise ValueError("fit_coupon.interface_parameter cannot be empty.")
        if not 2 <= len(offsets) <= 12:
            raise ValueError("fit_coupon requires between 2 and 12 candidate offsets.")
        if len(set(offsets)) != len(offsets):
            raise ValueError("fit_coupon candidate offsets must be unique.")
        object.__setattr__(self, "interface_parameter", name)
        object.__setattr__(self, "candidate_offsets", offsets)

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "FitCouponRequest":
        offsets = document["candidate_offsets"]
        if not isinstance(offsets, Sequence) or isinstance(offsets, (str, bytes)):
            raise TypeError("fit_coupon.candidate_offsets must be an array.")
        return cls(
            interface_parameter=str(document["interface_parameter"]),
            candidate_offsets=tuple(as_decimal(value) for value in offsets),  # type: ignore[arg-type]
            notes=str(document["notes"]),
        )

    def candidate_offsets_mm(self, input_units: LengthUnit | str) -> tuple[Decimal, ...]:
        return tuple(to_mm(value, input_units) for value in self.candidate_offsets)


@dataclass(frozen=True, slots=True)
class FitCouponEvidence:
    coupon_project_id: str
    coupon_project_version: str
    coupon_manifest_sha256: str
    coupon_artifact_sha256: str
    interface_parameter: str
    candidate_offset_mm: Decimal
    tested_at: str
    tested_by: str
    printer_profile: str
    material: str
    nozzle_diameter_mm: Decimal
    calibration_profile_id: str
    calibration_profile_version: str
    acceptance_criterion: str
    measured_result: str
    passed: bool
    notes: str

    def __post_init__(self) -> None:
        required_text = (
            "coupon_project_id",
            "coupon_project_version",
            "interface_parameter",
            "tested_by",
            "printer_profile",
            "material",
            "calibration_profile_id",
            "calibration_profile_version",
            "acceptance_criterion",
            "measured_result",
        )
        for field_name in required_text:
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"Fit-coupon evidence {field_name} cannot be empty.")
        for digest_name in ("coupon_manifest_sha256", "coupon_artifact_sha256"):
            digest = str(getattr(self, digest_name))
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(
                    "Fit-coupon evidence requires lowercase SHA-256 manifest and artifact digests."
                )
        object.__setattr__(self, "candidate_offset_mm", as_decimal(self.candidate_offset_mm))
        nozzle = as_decimal(self.nozzle_diameter_mm)
        if nozzle <= 0:
            raise ValueError("Fit-coupon evidence nozzle_diameter_mm must be positive.")
        object.__setattr__(self, "nozzle_diameter_mm", nozzle)
        if self.passed is not True:
            raise ValueError("Stored fit-coupon evidence must record a passed result.")
        try:
            tested = datetime.fromisoformat(self.tested_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Fit-coupon evidence tested_at must be an ISO-8601 date-time.") from exc
        if tested.tzinfo is None:
            raise ValueError("Fit-coupon evidence tested_at must include a timezone.")

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "FitCouponEvidence":
        return cls(
            coupon_project_id=str(document["coupon_project_id"]),
            coupon_project_version=str(document["coupon_project_version"]),
            coupon_manifest_sha256=str(document["coupon_manifest_sha256"]),
            coupon_artifact_sha256=str(document["coupon_artifact_sha256"]),
            interface_parameter=str(document["interface_parameter"]),
            candidate_offset_mm=as_decimal(document["candidate_offset_mm"]),  # type: ignore[arg-type]
            tested_at=str(document["tested_at"]),
            tested_by=str(document["tested_by"]),
            printer_profile=str(document["printer_profile"]),
            material=str(document["material"]),
            nozzle_diameter_mm=as_decimal(document["nozzle_diameter_mm"]),  # type: ignore[arg-type]
            calibration_profile_id=str(document["calibration_profile_id"]),
            calibration_profile_version=str(document["calibration_profile_version"]),
            acceptance_criterion=str(document["acceptance_criterion"]),
            measured_result=str(document["measured_result"]),
            passed=document["passed"] is True,
            notes=str(document["notes"]),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "coupon_project_id": self.coupon_project_id,
            "coupon_project_version": self.coupon_project_version,
            "coupon_manifest_sha256": self.coupon_manifest_sha256,
            "coupon_artifact_sha256": self.coupon_artifact_sha256,
            "interface_parameter": self.interface_parameter,
            "candidate_offset_mm": self.candidate_offset_mm,
            "tested_at": self.tested_at,
            "tested_by": self.tested_by,
            "printer_profile": self.printer_profile,
            "material": self.material,
            "nozzle_diameter_mm": self.nozzle_diameter_mm,
            "calibration_profile_id": self.calibration_profile_id,
            "calibration_profile_version": self.calibration_profile_version,
            "acceptance_criterion": self.acceptance_criterion,
            "measured_result": self.measured_result,
            "passed": self.passed,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class VerificationPolicy:
    require_authoritative_protected_interfaces: bool
    require_proven_calibration_for_full_part: bool
    mesh_bounds_tolerance_mm: Decimal
    physical_fit_required_for_verified_claim: bool

    def __post_init__(self) -> None:
        tolerance = as_decimal(self.mesh_bounds_tolerance_mm)
        if tolerance < 0:
            raise ValueError("mesh_bounds_tolerance_mm cannot be negative.")
        if not self.require_authoritative_protected_interfaces:
            raise ValueError("Authoritative protected-interface measurements cannot be disabled.")
        if not self.physical_fit_required_for_verified_claim:
            raise ValueError("Physical fit is required for any physically verified claim.")
        object.__setattr__(self, "mesh_bounds_tolerance_mm", tolerance)

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "VerificationPolicy":
        return cls(
            require_authoritative_protected_interfaces=bool(
                document["require_authoritative_protected_interfaces"]
            ),
            require_proven_calibration_for_full_part=bool(
                document["require_proven_calibration_for_full_part"]
            ),
            mesh_bounds_tolerance_mm=as_decimal(document["mesh_bounds_tolerance_mm"]),  # type: ignore[arg-type]
            physical_fit_required_for_verified_claim=bool(
                document["physical_fit_required_for_verified_claim"]
            ),
        )


@dataclass(frozen=True, slots=True)
class PhysicalVerification:
    status: PhysicalFitStatus
    confirmed_at: str | None
    confirmed_by: str | None
    evidence: tuple[str, ...]
    notes: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", PhysicalFitStatus(self.status))
        if self.status is PhysicalFitStatus.CONFIRMED:
            if not self.confirmed_at or not self.confirmed_by or not self.evidence:
                raise ValueError(
                    "Confirmed physical fit requires confirmed_at, confirmed_by, and evidence."
                )
        elif self.confirmed_at is not None or self.confirmed_by is not None:
            raise ValueError("Unconfirmed physical fit cannot include confirmation metadata.")

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "PhysicalVerification":
        evidence = document["evidence"]
        if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)):
            raise TypeError("physical_verification.evidence must be an array.")
        return cls(
            status=PhysicalFitStatus(str(document["status"])),
            confirmed_at=(
                str(document["confirmed_at"]) if document.get("confirmed_at") is not None else None
            ),
            confirmed_by=(
                str(document["confirmed_by"]) if document.get("confirmed_by") is not None else None
            ),
            evidence=tuple(str(item) for item in evidence),
            notes=str(document["notes"]),
        )


@dataclass(frozen=True, slots=True)
class SpecificationTimestamps:
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "SpecificationTimestamps":
        return cls(created_at=str(document["created_at"]), updated_at=str(document["updated_at"]))


@dataclass(frozen=True, slots=True)
class ProjectSpec:
    schema_version: str
    project: ProjectIdentity
    generator: GeneratorSelection
    input_units: LengthUnit
    printer_profile: str
    material: str
    nozzle_diameter: Decimal
    fit_profile: str
    generation_mode: GenerationMode
    fit_coupon: FitCouponRequest | None
    fit_coupon_evidence: FitCouponEvidence | None
    measurement_contract: tuple[MeasurementContract, ...]
    verification_policy: VerificationPolicy
    workflow_state: WorkflowState
    physical_verification: PhysicalVerification
    timestamps: SpecificationTimestamps
    generated_artifacts: tuple[ArtifactRecord, ...]
    warnings: tuple[str, ...]
    unresolved_assumptions: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "input_units", normalize_unit(self.input_units))
        object.__setattr__(self, "nozzle_diameter", as_decimal(self.nozzle_diameter))
        object.__setattr__(self, "generation_mode", GenerationMode(self.generation_mode))
        object.__setattr__(self, "workflow_state", WorkflowState(self.workflow_state))
        if self.nozzle_diameter <= 0:
            raise ValueError("nozzle_diameter must be positive.")
        if self.generation_mode is GenerationMode.FIT_COUPON and self.fit_coupon is None:
            raise ValueError("fit_coupon is required when generation_mode is fit_coupon.")
        if self.generation_mode is GenerationMode.FULL_PART and self.fit_coupon is not None:
            raise ValueError("fit_coupon must be null when generation_mode is full_part.")
        if (
            self.generation_mode is GenerationMode.FIT_COUPON
            and self.workflow_state is not WorkflowState.FIT_COUPON_PASSED
            and self.fit_coupon_evidence is not None
        ):
            raise ValueError(
                "Fit-coupon evidence may be attached to a coupon only after fit_coupon_passed."
            )
        if self.workflow_state is WorkflowState.FIT_COUPON_PASSED:
            if self.generation_mode is not GenerationMode.FIT_COUPON:
                raise ValueError("fit_coupon_passed requires generation_mode fit_coupon.")
            if self.fit_coupon_evidence is None:
                raise ValueError("fit_coupon_passed requires structured fit-coupon evidence.")
        if self.fit_coupon_evidence is not None:
            evidence = self.fit_coupon_evidence
            if evidence.printer_profile != self.printer_profile:
                raise ValueError("Fit-coupon evidence printer profile does not match the spec.")
            if evidence.material.lower() != self.material.lower():
                raise ValueError("Fit-coupon evidence material does not match the spec.")
            if evidence.calibration_profile_id != self.fit_profile:
                raise ValueError("Fit-coupon evidence calibration profile does not match the spec.")
            if abs(evidence.nozzle_diameter_mm - self.nozzle_diameter_mm) > Decimal("0.000001"):
                raise ValueError("Fit-coupon evidence nozzle diameter does not match the spec.")
        physical_state = self.physical_verification.status is PhysicalFitStatus.CONFIRMED
        workflow_physical = self.workflow_state is WorkflowState.PHYSICAL_FIT_CONFIRMED
        if physical_state != workflow_physical:
            raise ValueError(
                "physical_verification.status and workflow_state physical confirmation must agree."
            )
        if physical_state and self.generation_mode is not GenerationMode.FULL_PART:
            raise ValueError("A fit coupon cannot confirm physical fit of the full part.")

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "ProjectSpec":
        def object_at(key: str) -> Mapping[str, object]:
            value = document[key]
            if not isinstance(value, Mapping):
                raise TypeError(f"{key} must be an object.")
            return value

        measurement_documents = document["measurement_contract"]
        artifact_documents = document["generated_artifacts"]
        if not isinstance(measurement_documents, Sequence) or isinstance(
            measurement_documents, (str, bytes)
        ):
            raise TypeError("measurement_contract must be an array.")
        if not isinstance(artifact_documents, Sequence) or isinstance(
            artifact_documents, (str, bytes)
        ):
            raise TypeError("generated_artifacts must be an array.")

        fit_coupon_document = document["fit_coupon"]
        fit_coupon = None
        if fit_coupon_document is not None:
            if not isinstance(fit_coupon_document, Mapping):
                raise TypeError("fit_coupon must be an object or null.")
            fit_coupon = FitCouponRequest.from_dict(fit_coupon_document)

        fit_coupon_evidence_document = document["fit_coupon_evidence"]
        fit_coupon_evidence = None
        if fit_coupon_evidence_document is not None:
            if not isinstance(fit_coupon_evidence_document, Mapping):
                raise TypeError("fit_coupon_evidence must be an object or null.")
            fit_coupon_evidence = FitCouponEvidence.from_dict(
                fit_coupon_evidence_document
            )

        spec = cls(
            schema_version=str(document["schema_version"]),
            project=ProjectIdentity.from_dict(object_at("project")),
            generator=GeneratorSelection.from_dict(object_at("generator")),
            input_units=normalize_unit(str(document["input_units"])),
            printer_profile=str(document["printer_profile"]),
            material=str(document["material"]),
            nozzle_diameter=as_decimal(document["nozzle_diameter"]),  # type: ignore[arg-type]
            fit_profile=str(document["fit_profile"]),
            generation_mode=GenerationMode(str(document["generation_mode"])),
            fit_coupon=fit_coupon,
            fit_coupon_evidence=fit_coupon_evidence,
            measurement_contract=tuple(
                MeasurementContract.from_dict(item)  # type: ignore[arg-type]
                for item in measurement_documents
            ),
            verification_policy=VerificationPolicy.from_dict(object_at("verification_policy")),
            workflow_state=WorkflowState(str(document["workflow_state"])),
            physical_verification=PhysicalVerification.from_dict(
                object_at("physical_verification")
            ),
            timestamps=SpecificationTimestamps.from_dict(object_at("timestamps")),
            generated_artifacts=tuple(
                ArtifactRecord.from_dict(item)  # type: ignore[arg-type]
                for item in artifact_documents
            ),
            warnings=tuple(str(item) for item in document["warnings"]),  # type: ignore[union-attr]
            unresolved_assumptions=tuple(
                str(item) for item in document["unresolved_assumptions"]  # type: ignore[union-attr]
            ),
        )
        # Drafts are intentionally loadable while measurements are still being
        # gathered.  Once a specification claims a later workflow state, every
        # protected record it declares must already have authoritative support.
        # Generator-declared required interfaces are enforced separately by
        # validate_generator_measurements[_mm] before generation.
        if spec.workflow_state is not WorkflowState.DRAFT:
            spec.validate_declared_measurements()
        return spec

    @property
    def nozzle_diameter_mm(self) -> Decimal:
        return to_mm(self.nozzle_diameter, self.input_units)

    @property
    def project_id(self) -> str:
        return self.project.id

    @property
    def project_version(self) -> str:
        return self.project.version

    @property
    def generator_id(self) -> str:
        return self.generator.id

    @property
    def generator_version(self) -> str:
        return self.generator.version

    @property
    def parameters(self) -> Mapping[str, object]:
        return self.generator.parameters

    @property
    def is_physically_verified(self) -> bool:
        return (
            self.workflow_state is WorkflowState.PHYSICAL_FIT_CONFIRMED
            and self.physical_verification.status is PhysicalFitStatus.CONFIRMED
        )

    def validate_declared_measurements(self) -> None:
        """Validate protected records already declared in the specification."""

        validate_measurement_contract(
            self.measurement_contract,
            self.project.intent,
            enforce_authoritative=self.verification_policy.require_authoritative_protected_interfaces,
        )

    def validate_generator_measurements(
        self,
        required_protected_parameters: Iterable[str],
        *,
        parameter_values: Mapping[str, object] | None = None,
        parameter_units: LengthUnit | str | None = None,
    ) -> None:
        """Apply generator-declared protected-interface requirements.

        ``parameter_values`` may contain raw specification values or resolved
        millimeter values.  Raw callers can omit ``parameter_units``; callers
        with normalized values must pass ``parameter_units="mm"`` to avoid
        converting an inch specification twice.
        """

        validate_measurement_contract(
            self.measurement_contract,
            self.project.intent,
            required_protected_parameters=required_protected_parameters,
            parameter_values=parameter_values,  # type: ignore[arg-type]
            parameter_units=(parameter_units or self.input_units)
            if parameter_values is not None
            else None,
            enforce_authoritative=self.verification_policy.require_authoritative_protected_interfaces,
        )

    def validate_generator_measurements_mm(
        self,
        required_protected_parameters: Iterable[str],
        parameter_values_mm: Mapping[str, object],
    ) -> None:
        """Validate a generator's already-normalized millimeter parameters."""

        self.validate_generator_measurements(
            required_protected_parameters,
            parameter_values=parameter_values_mm,
            parameter_units=LengthUnit.MILLIMETER,
        )
