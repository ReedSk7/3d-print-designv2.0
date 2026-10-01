"""End-to-end deterministic generation workflow."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from core.models.artifacts import (
    ArtifactManifest,
    ArtifactRecord,
    ArtifactRole,
    read_and_verify_artifact,
    resolve_and_verify_artifact,
    sha256_bytes,
    sha256_file,
)
from core.evidence import parse_fit_coupon_result_bytes
from core.models.spec import GenerationMode, ProjectSpec
from core.profiles.models import CalibrationStatus
from core.profiles.repository import load_calibration_profile_record
from core.validation.mesh import MeshReport, require_valid_mesh
from core.validation.specification import (
    SpecificationError,
    load_project_spec,
    load_project_spec_bytes,
    validate_parameter_document,
)
from generators.base import GenerationContext, GenerationResult, PartGenerator
from generators.registry import get_generator

from .openscad import OpenSCADCompileResult, compile_binary_stl
from .states import WorkflowState, WorkflowStateMachine
from .publication import publish_bundle


@dataclass(frozen=True, slots=True)
class PreparedGeneration:
    spec: ProjectSpec
    generator: PartGenerator
    context: GenerationContext
    generation: GenerationResult
    warnings: tuple[str, ...]
    calibration_profile_id: str
    calibration_profile_version: str
    calibration_profile_sha256: str
    unverified_calibration_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PipelineResult:
    spec: ProjectSpec
    output_directory: Path
    scad_path: Path
    stl_path: Path
    manifest_path: Path
    reached_state: WorkflowState
    mesh_report: MeshReport
    warnings: tuple[str, ...]


def _plain(value: object) -> object:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (Mapping, MappingProxyType)):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


def _json_ready(value: object) -> object:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_ready(item) for item in value]
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _aware_timestamp(value: object, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise SpecificationError(f"{label} must be an ISO-8601 date-time.") from exc
    if parsed.tzinfo is None:
        raise SpecificationError(f"{label} must include a timezone.")
    return parsed


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _staged_artifact_record(
    staged_path: Path,
    final_path: Path,
    *,
    role: ArtifactRole,
    workspace_root: Path,
    created_at: str,
    media_type: str,
) -> ArtifactRecord:
    final_relative = final_path.resolve().relative_to(workspace_root.resolve())
    return ArtifactRecord(
        role=role,
        path=final_relative.as_posix(),
        sha256=sha256_file(staged_path),
        size_bytes=staged_path.stat().st_size,
        created_at=created_at,
        media_type=media_type,
    )


def _manifest_artifact(
    document: Mapping[str, object], roles: set[ArtifactRole]
) -> ArtifactRecord:
    artifacts = document.get("artifacts")
    if not isinstance(artifacts, list):
        raise SpecificationError("Coupon artifact manifest has no artifact list.")
    matches = []
    seen = set()
    for item in artifacts:
        if not isinstance(item, Mapping):
            continue
        try:
            record = ArtifactRecord.from_dict(item)
        except (KeyError, TypeError, ValueError) as exc:
            raise SpecificationError(f"Coupon artifact record is invalid: {exc}") from exc
        if record.role in seen:
            raise SpecificationError(f"Coupon artifact manifest repeats role {record.role.value}.")
        seen.add(record.role)
        if record.role in roles:
            matches.append(record)
    if len(matches) == 1:
        return matches[0]
    expected = ", ".join(sorted(role.value for role in roles))
    raise SpecificationError(f"Coupon artifact manifest is missing role: {expected}.")


def _verify_coupon_generation_binding(
    manifest_document: Mapping[str, object], coupon_spec: ProjectSpec
) -> None:
    """Confirm the manifest describes the candidates actually rendered."""

    request = coupon_spec.fit_coupon
    if request is None:
        raise SpecificationError("Referenced coupon specification has no fit-coupon request.")
    checks = manifest_document.get("checks")
    if not isinstance(checks, Mapping):
        raise SpecificationError("Fit-coupon manifest checks are missing.")
    history = checks.get("workflow_history")
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        raise SpecificationError("Fit-coupon manifest workflow history is missing.")
    transitions = [
        item
        for item in history
        if isinstance(item, Mapping)
        and item.get("to_state") == WorkflowState.FIT_COUPON_GENERATED.value
    ]
    if len(transitions) != 1 or not history or history[-1] is not transitions[0]:
        raise SpecificationError(
            "Fit-coupon manifest must end with one fit_coupon_generated transition."
        )
    transition_evidence = transitions[0].get("evidence")
    if not isinstance(transition_evidence, Mapping):
        raise SpecificationError("Fit-coupon generation transition evidence is missing.")
    if transition_evidence.get("interface_parameter") != request.interface_parameter:
        raise SpecificationError(
            "Fit-coupon manifest interface does not match the coupon specification."
        )
    generated_offsets = transition_evidence.get("candidate_offsets_mm")
    if not isinstance(generated_offsets, Sequence) or isinstance(
        generated_offsets, (str, bytes)
    ):
        raise SpecificationError("Fit-coupon manifest candidate offsets are missing.")
    try:
        normalized_offsets = tuple(Decimal(str(value)) for value in generated_offsets)
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise SpecificationError(
            "Fit-coupon manifest candidate offsets are invalid."
        ) from exc
    spec_offsets = request.candidate_offsets_mm(coupon_spec.input_units)
    if normalized_offsets != spec_offsets:
        raise SpecificationError(
            "Fit-coupon manifest candidate offsets do not match the coupon specification."
        )

    if coupon_spec.generator.version != "1.1.0":
        return
    normalized_parameters = checks.get("normalized_parameters_mm")
    if not isinstance(normalized_parameters, Mapping):
        raise SpecificationError("Generator 1.1.0 normalized coupon parameters are missing.")
    candidate_map = normalized_parameters.get("coupon_candidate_map")
    if not isinstance(candidate_map, Sequence) or isinstance(
        candidate_map, (str, bytes)
    ):
        raise SpecificationError("Generator 1.1.0 coupon candidate map is missing.")
    if len(candidate_map) != len(spec_offsets):
        raise SpecificationError(
            "Generator 1.1.0 coupon candidate map length does not match the specification."
        )
    for expected_index, (entry, expected_offset) in enumerate(
        zip(candidate_map, spec_offsets), start=1
    ):
        if not isinstance(entry, Mapping):
            raise SpecificationError("Coupon candidate map entries must be objects.")
        if (
            type(entry.get("index")) is not int
            or entry.get("index") != expected_index
            or str(entry.get("label")) != str(expected_index)
        ):
            raise SpecificationError(
                "Coupon candidate map indexes and labels must be sequential and one-based."
            )
        try:
            mapped_offset = Decimal(str(entry["offset_mm"]))
        except (ArithmeticError, KeyError, TypeError, ValueError) as exc:
            raise SpecificationError(
                "Coupon candidate map offsets are missing or invalid."
            ) from exc
        if mapped_offset != expected_offset:
            raise SpecificationError(
                "Coupon candidate map offsets do not match the coupon specification."
            )


def _verify_fit_coupon_evidence(
    spec: ProjectSpec,
    *,
    workspace_root: Path,
    generator: PartGenerator,
    calibration_version: str,
    calibration_sha256: str,
) -> None:
    evidence = spec.fit_coupon_evidence
    if evidence is None:
        return

    root = workspace_root.resolve()
    coupon_directory = (
        root / evidence.coupon_project_id / evidence.coupon_project_version
    ).resolve()
    try:
        coupon_directory.relative_to(root)
    except ValueError as exc:
        raise SpecificationError("Fit-coupon evidence escaped the workspace root.") from exc
    if (
        evidence.coupon_project_id == spec.project.id
        and evidence.coupon_project_version == spec.project.version
    ):
        raise SpecificationError("A full-part version cannot cite itself as fit-coupon evidence.")

    manifest_path = coupon_directory / "artifact-manifest.json"
    if not manifest_path.is_file():
        raise SpecificationError(
            f"Referenced fit-coupon manifest was not found: {manifest_path}"
        )
    try:
        manifest_bytes = manifest_path.read_bytes()
    except OSError as exc:
        raise SpecificationError(f"Could not read fit-coupon manifest: {exc}") from exc
    if sha256_bytes(manifest_bytes) != evidence.coupon_manifest_sha256:
        raise SpecificationError(
            "Fit-coupon evidence manifest SHA-256 does not match the cited manifest."
        )
    try:
        manifest_document = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        raise SpecificationError(f"Could not read fit-coupon manifest: {exc}") from exc
    if not isinstance(manifest_document, dict):
        raise SpecificationError("Fit-coupon manifest root must be an object.")

    try:
        manifest_generator = manifest_document["generator"]
        checks = manifest_document["checks"]
        if not isinstance(manifest_generator, Mapping) or not isinstance(checks, Mapping):
            raise TypeError("generator/checks must be objects")
        calibration_check = checks["calibration_profile"]
        mesh_check = checks["mesh"]
        if not isinstance(calibration_check, Mapping) or not isinstance(mesh_check, Mapping):
            raise TypeError("calibration_profile/mesh checks must be objects")
        manifest_values = {
            "project_id": str(manifest_document["project_id"]),
            "project_version": str(manifest_document["project_version"]),
            "generation_mode": str(manifest_document["generation_mode"]),
            "workflow_state": str(manifest_document["workflow_state"]),
            "generator_id": str(manifest_generator["id"]),
            "generator_version": str(manifest_generator["version"]),
            "calibration_id": str(calibration_check["id"]),
            "calibration_version": str(calibration_check["version"]),
            "calibration_sha256": (
                str(calibration_check["sha256"])
                if calibration_check.get("sha256") is not None
                else None
            ),
            "mesh_passed": mesh_check["passed"] is True,
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise SpecificationError(f"Fit-coupon manifest is incomplete: {exc}") from exc

    expected_values = {
        "project_id": evidence.coupon_project_id,
        "project_version": evidence.coupon_project_version,
        "generation_mode": "fit_coupon",
        "workflow_state": "fit_coupon_generated",
        "generator_id": generator.metadata.generator_id,
        "generator_version": generator.metadata.version,
        "calibration_id": evidence.calibration_profile_id,
        "calibration_version": evidence.calibration_profile_version,
        "mesh_passed": True,
    }
    if (
        evidence.calibration_profile_sha256 is not None
        or generator.metadata.version == "1.1.0"
    ):
        expected_values["calibration_sha256"] = evidence.calibration_profile_sha256
    mismatches = [
        name
        for name, expected in expected_values.items()
        if manifest_values[name] != expected
    ]
    if mismatches:
        raise SpecificationError(
            "Fit-coupon manifest does not match accepted evidence: "
            + ", ".join(mismatches)
        )
    if evidence.calibration_profile_version != calibration_version:
        raise SpecificationError(
            "Fit-coupon evidence calibration profile version does not match the loaded profile."
        )
    if generator.metadata.version == "1.1.0" and evidence.calibration_profile_sha256 is None:
        raise SpecificationError(
            "Generator 1.1.0 fit-coupon evidence requires a calibration-profile content SHA-256."
        )
    if (
        evidence.calibration_profile_sha256 is not None
        and evidence.calibration_profile_sha256 != calibration_sha256
    ):
        raise SpecificationError(
            "Fit-coupon evidence calibration profile content does not match the loaded profile."
        )

    scad_record = _manifest_artifact(manifest_document, {ArtifactRole.FIT_COUPON_SCAD})
    try:
        coupon_scad_path, _ = read_and_verify_artifact(scad_record, workspace_root=root)
    except ValueError as exc:
        raise SpecificationError(f"Referenced fit-coupon SCAD failed integrity checks: {exc}") from exc
    if coupon_scad_path.parent != coupon_directory:
        raise SpecificationError("Referenced fit-coupon SCAD is not in the cited coupon version directory.")

    stl_record = _manifest_artifact(
        manifest_document, {ArtifactRole.FIT_COUPON_STL}
    )
    try:
        coupon_stl_path = resolve_and_verify_artifact(stl_record, workspace_root=root)
    except ValueError as exc:
        raise SpecificationError(f"Referenced fit-coupon STL failed integrity checks: {exc}") from exc
    if coupon_stl_path.parent != coupon_directory:
        raise SpecificationError(
            "Referenced fit-coupon STL is not in the cited coupon version directory."
        )
    if stl_record.sha256 != evidence.coupon_artifact_sha256:
        raise SpecificationError(
            "Fit-coupon evidence SHA-256 does not match the referenced coupon STL."
        )

    spec_record = _manifest_artifact(
        manifest_document, {ArtifactRole.SPEC_SNAPSHOT}
    )
    try:
        coupon_spec_path, coupon_spec_bytes = read_and_verify_artifact(
            spec_record, workspace_root=root
        )
    except ValueError as exc:
        raise SpecificationError(
            f"Referenced fit-coupon specification failed integrity checks: {exc}"
        ) from exc
    if coupon_spec_path.parent != coupon_directory:
        raise SpecificationError(
            "Referenced fit-coupon specification is not in the cited coupon version directory."
        )
    coupon_spec = load_project_spec_bytes(
        coupon_spec_bytes,
        source=f"fit-coupon specification {coupon_spec_path}",
    )
    if coupon_spec.generation_mode is not GenerationMode.FIT_COUPON or coupon_spec.fit_coupon is None:
        raise SpecificationError("Referenced coupon specification is not a fit-coupon request.")
    _verify_coupon_generation_binding(manifest_document, coupon_spec)
    if coupon_spec.project.id != evidence.coupon_project_id or coupon_spec.project.version != evidence.coupon_project_version:
        raise SpecificationError("Referenced coupon specification identity does not match evidence.")
    if coupon_spec.generator.id != spec.generator.id or coupon_spec.generator.version != spec.generator.version:
        raise SpecificationError("Referenced coupon generator does not match the full-part generator.")
    if coupon_spec.input_units is not spec.input_units:
        raise SpecificationError(
            "Referenced coupon input units do not match the full-part specification."
        )
    if coupon_spec.generator.parameters != spec.generator.parameters:
        raise SpecificationError(
            "Referenced coupon generator parameters do not match the full-part specification."
        )
    if coupon_spec.fit_coupon.interface_parameter != evidence.interface_parameter:
        raise SpecificationError("Referenced coupon interface does not match accepted evidence.")
    if evidence.candidate_offset_mm not in coupon_spec.fit_coupon.candidate_offsets_mm(
        coupon_spec.input_units
    ):
        raise SpecificationError("Accepted coupon offset was not one of the generated candidates.")
    if coupon_spec.printer_profile != evidence.printer_profile:
        raise SpecificationError("Referenced coupon printer profile does not match evidence.")
    if coupon_spec.material.lower() != evidence.material.lower():
        raise SpecificationError("Referenced coupon material does not match evidence.")
    if abs(coupon_spec.nozzle_diameter_mm - evidence.nozzle_diameter_mm) > Decimal("0.000001"):
        raise SpecificationError("Referenced coupon nozzle diameter does not match evidence.")
    if coupon_spec.fit_profile != evidence.calibration_profile_id:
        raise SpecificationError("Referenced coupon calibration profile does not match evidence.")
    request_origin = (
        coupon_spec.fit_coupon.source_project_id,
        coupon_spec.fit_coupon.source_project_version,
        coupon_spec.fit_coupon.source_spec_sha256,
    )
    linked_origin = (
        evidence.source_project_id,
        evidence.source_project_version,
        evidence.source_spec_sha256,
    )
    if generator.metadata.version == "1.1.0" and any(
        value is None for value in request_origin + linked_origin
    ):
        raise SpecificationError(
            "Generator 1.1.0 fit-coupon evidence requires an exact originating-source binding."
        )
    if request_origin != linked_origin:
        raise SpecificationError(
            "Fit-coupon originating-source binding does not match the linked specification."
        )
    if evidence.source_project_id is not None:
        if spec.project.id != evidence.source_project_id:
            raise SpecificationError(
                "Linked full-part project ID does not match the coupon's originating project."
            )
        if spec.project.version == evidence.source_project_version:
            raise SpecificationError(
                "Linked full-part version must differ from the coupon's originating source version."
            )
    if coupon_spec.project.intent is not spec.project.intent:
        raise SpecificationError(
            "Referenced coupon project intent does not match the linked full-part specification."
        )
    if coupon_spec.measurement_contract != spec.measurement_contract:
        raise SpecificationError(
            "Referenced coupon measurement contract does not match the linked full-part specification."
        )
    if coupon_spec.verification_policy != spec.verification_policy:
        raise SpecificationError(
            "Referenced coupon verification policy does not match the linked full-part specification."
        )

    result_binding_present = evidence.coupon_result_evidence_path is not None
    if generator.metadata.version == "1.1.0" and not result_binding_present:
        raise SpecificationError(
            "Generator 1.1.0 requires an immutable fit-result evidence binding; "
            "legacy embedded coupon evidence is insufficient."
        )
    if not result_binding_present:
        return

    try:
        result_path = (root / evidence.coupon_result_evidence_path).resolve(strict=True)
    except (OSError, ValueError) as exc:
        raise SpecificationError(
            "Linked fit-result evidence is missing or cannot be resolved."
        ) from exc
    try:
        result_relative = result_path.relative_to(root)
    except ValueError as exc:
        raise SpecificationError(
            "Fit-result evidence escaped the workspace root."
        ) from exc
    if result_path.parent != coupon_directory:
        raise SpecificationError(
            "Fit-result evidence is not beside the cited coupon artifacts."
        )
    if result_relative.as_posix() != evidence.coupon_result_evidence_path:
        raise SpecificationError(
            "Fit-result evidence path does not resolve to its exact workspace-relative path."
        )
    try:
        result_bytes = result_path.read_bytes()
    except OSError as exc:
        raise SpecificationError(f"Could not read fit-result evidence: {exc}") from exc
    if len(result_bytes) != evidence.coupon_result_evidence_size_bytes:
        raise SpecificationError("Fit-result evidence size does not match the linked specification.")
    if sha256_bytes(result_bytes) != evidence.coupon_result_evidence_sha256:
        raise SpecificationError(
            "Fit-result evidence SHA-256 does not match the linked specification."
        )
    try:
        result_evidence = parse_fit_coupon_result_bytes(
            result_bytes,
            source=f"linked fit-result evidence {result_path}",
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SpecificationError(f"Fit-result evidence is invalid: {exc}") from exc

    if not result_evidence.result.passed:
        raise SpecificationError("A failed fit-coupon result cannot authorize a full part.")
    expected_manifest_relative = manifest_path.relative_to(root).as_posix()
    expected_values = {
        "coupon project ID": (
            result_evidence.coupon_project_id,
            evidence.coupon_project_id,
        ),
        "coupon project version": (
            result_evidence.coupon_project_version,
            evidence.coupon_project_version,
        ),
        "generator ID": (
            result_evidence.generator.generator_id,
            generator.metadata.generator_id,
        ),
        "generator version": (
            result_evidence.generator.generator_version,
            generator.metadata.version,
        ),
        "source project ID": (
            result_evidence.source_project_id,
            evidence.source_project_id,
        ),
        "source project version": (
            result_evidence.source_project_version,
            evidence.source_project_version,
        ),
        "source specification SHA-256": (
            result_evidence.source_spec_sha256,
            evidence.source_spec_sha256,
        ),
        "manifest path": (
            result_evidence.manifest.path,
            expected_manifest_relative,
        ),
        "manifest SHA-256": (
            result_evidence.manifest.sha256,
            evidence.coupon_manifest_sha256,
        ),
        "manifest size": (result_evidence.manifest.size_bytes, len(manifest_bytes)),
        "STL path": (result_evidence.stl.path, stl_record.path),
        "STL SHA-256": (result_evidence.stl.sha256, stl_record.sha256),
        "STL size": (result_evidence.stl.size_bytes, stl_record.size_bytes),
        "specification path": (
            result_evidence.specification_snapshot.path,
            spec_record.path,
        ),
        "specification SHA-256": (
            result_evidence.specification_snapshot.sha256,
            spec_record.sha256,
        ),
        "specification size": (
            result_evidence.specification_snapshot.size_bytes,
            spec_record.size_bytes,
        ),
        "linked specification SHA-256": (
            evidence.coupon_spec_sha256,
            spec_record.sha256,
        ),
        "interface": (
            result_evidence.configuration.interface_parameter,
            evidence.interface_parameter,
        ),
        "selected candidate": (
            result_evidence.configuration.selected_candidate_offset_mm,
            evidence.candidate_offset_mm,
        ),
        "printer profile": (
            result_evidence.configuration.printer_profile,
            evidence.printer_profile,
        ),
        "material": (
            result_evidence.configuration.material.lower(),
            evidence.material.lower(),
        ),
        "nozzle diameter": (
            result_evidence.configuration.nozzle_diameter_mm,
            evidence.nozzle_diameter_mm,
        ),
        "calibration profile ID": (
            result_evidence.configuration.calibration_profile_id,
            evidence.calibration_profile_id,
        ),
        "calibration profile version": (
            result_evidence.configuration.calibration_profile_version,
            evidence.calibration_profile_version,
        ),
        "calibration profile SHA-256": (
            result_evidence.configuration.calibration_profile_sha256,
            evidence.calibration_profile_sha256,
        ),
        "tested by": (result_evidence.result.tested_by, evidence.tested_by),
        "tested at": (result_evidence.result.tested_at, evidence.tested_at),
        "acceptance criterion": (
            result_evidence.result.acceptance_criterion,
            evidence.acceptance_criterion,
        ),
        "observed result": (
            result_evidence.result.observed_result,
            evidence.measured_result,
        ),
        "notes": (result_evidence.result.notes, evidence.notes),
    }
    mismatches = [
        label for label, (actual, expected) in expected_values.items() if actual != expected
    ]
    if mismatches:
        raise SpecificationError(
            "Fit-result evidence does not match linked coupon provenance: "
            + ", ".join(mismatches)
        )
    if result_evidence.configuration.candidate_offsets_mm != (
        coupon_spec.fit_coupon.candidate_offsets_mm(coupon_spec.input_units)
    ):
        raise SpecificationError(
            "Fit-result evidence candidate offsets do not match the generated coupon specification."
        )
    artifact_documents = manifest_document.get("artifacts")
    if not isinstance(artifact_documents, list):
        raise SpecificationError("Fit-coupon manifest has no artifact creation records.")
    creation_times = [
        _aware_timestamp(manifest_document.get("created_at"), "Coupon manifest created_at")
    ]
    for artifact_document in artifact_documents:
        if not isinstance(artifact_document, Mapping):
            raise SpecificationError("Fit-coupon manifest artifact record is invalid.")
        creation_times.append(
            _aware_timestamp(
                artifact_document.get("created_at"),
                "Coupon artifact created_at",
            )
        )
    tested_at = _aware_timestamp(result_evidence.result.tested_at, "Coupon tested_at")
    evidence_created_at = _aware_timestamp(
        result_evidence.created_at, "Fit-result evidence created_at"
    )
    if tested_at < max(creation_times):
        raise SpecificationError(
            "Fit-result evidence tested_at predates the coupon manifest or artifacts."
        )
    if evidence_created_at < tested_at:
        raise SpecificationError(
            "Fit-result evidence was created before the recorded coupon test."
        )


def prepare_generation(
    spec: ProjectSpec,
    *,
    workspace_root: str | Path | None = None,
) -> PreparedGeneration:
    """Resolve and semantically validate a spec without writing artifacts."""

    if spec.workflow_state is not WorkflowState.DRAFT:
        raise SpecificationError(
            f"Generation requires workflow_state 'draft'; got '{spec.workflow_state.value}'."
        )
    if spec.is_physically_verified:
        raise SpecificationError("A physically confirmed specification cannot be regenerated in place.")

    generator = get_generator(spec.generator.id, spec.generator.version)
    parameters = _plain(spec.generator.parameters)
    if not isinstance(parameters, dict):
        raise SpecificationError("generator.parameters must resolve to an object.")
    validate_parameter_document(generator.parameter_schema, parameters)

    calibration_record = load_calibration_profile_record(spec.fit_profile)
    calibration = calibration_record.profile
    unverified_calibration_fields = (
        calibration.unverified_fields_for_generator_version(
            generator.metadata.version
        )
    )
    if not calibration.applies_to(
        spec.printer_profile, spec.material, spec.nozzle_diameter_mm
    ):
        raise SpecificationError(
            f"Calibration profile '{calibration.profile_id}' does not apply to "
            f"printer={spec.printer_profile}, material={spec.material}, "
            f"nozzle={spec.nozzle_diameter_mm} mm."
        )
    if spec.fit_coupon_evidence is not None:
        coupon_root = (
            Path(workspace_root).resolve()
            if workspace_root is not None
            else Path(__file__).resolve().parents[2] / "workspace"
        )
        _verify_fit_coupon_evidence(
            spec,
            workspace_root=coupon_root,
            generator=generator,
            calibration_version=calibration.version,
            calibration_sha256=calibration_record.content_sha256,
        )
    if (
        spec.generation_mode is GenerationMode.FULL_PART
        and spec.verification_policy.require_proven_calibration_for_full_part
        and unverified_calibration_fields
    ):
        raise SpecificationError(
            "Full-part policy requires a proven calibration profile, but the selected "
            "generator-version fields are unverified: "
            f"{', '.join(unverified_calibration_fields)}."
        )

    fit_class = str(parameters.get("fit_class", "nominal"))
    coupon_parameter = (
        spec.fit_coupon.interface_parameter if spec.fit_coupon is not None else None
    )
    coupon_offsets = (
        spec.fit_coupon.candidate_offsets_mm(spec.input_units)
        if spec.fit_coupon is not None
        else ()
    )
    context = GenerationContext(
        input_units=spec.input_units.value,
        nozzle_diameter_mm=spec.nozzle_diameter_mm,
        fit_class=fit_class,
        calibration_offsets_mm={
            "hole_offset_mm": calibration.hole_offset_mm.value,
            "shaft_offset_mm": calibration.shaft_offset_mm.value,
            "press_fit_offset_mm": calibration.press_fit_offset_mm.value,
            "slip_fit_offset_mm": calibration.slip_fit_offset_mm.value,
            "hole_dimensional_correction_mm": (
                calibration.hole_dimensional_correction_mm.value
            ),
            "shaft_dimensional_correction_mm": (
                calibration.shaft_dimensional_correction_mm.value
            ),
            "hole_slip_allowance_mm": calibration.hole_slip_allowance_mm.value,
            "shaft_slip_allowance_mm": calibration.shaft_slip_allowance_mm.value,
            "hole_press_allowance_mm": calibration.hole_press_allowance_mm.value,
            "shaft_press_allowance_mm": calibration.shaft_press_allowance_mm.value,
        },
        scale_correction=(
            calibration.scale_x.value,
            calibration.scale_y.value,
            calibration.scale_z.value,
        ),
        generation_mode=spec.generation_mode.value,
        coupon_parameter=coupon_parameter,
        coupon_offsets_mm=coupon_offsets,
        accepted_coupon_parameter=(
            spec.fit_coupon_evidence.interface_parameter
            if spec.fit_coupon_evidence is not None
            else None
        ),
        accepted_coupon_offset_mm=(
            spec.fit_coupon_evidence.candidate_offset_mm
            if spec.fit_coupon_evidence is not None
            else Decimal("0")
        ),
    )
    generation = generator.generate(parameters, context)

    if (
        spec.fit_coupon_evidence is not None
        and spec.fit_coupon_evidence.interface_parameter
        not in generation.nominal_protected_dimensions_mm
    ):
        raise SpecificationError(
            "Accepted fit-coupon interface is not a protected parameter for the selected generator."
        )

    # This gate applies to both a full part and a coupon. A coupon may resolve
    # clearance uncertainty; it may not replace a missing nominal measurement.
    spec.validate_generator_measurements_mm(
        generation.nominal_protected_dimensions_mm.keys(),
        generation.nominal_protected_dimensions_mm,
    )

    warnings = list(spec.warnings)
    warnings.extend(generation.warnings)
    if unverified_calibration_fields:
        warnings.append(
            "Calibration profile is an unverified starter; neutral values are not proven fit corrections."
        )
    return PreparedGeneration(
        spec=spec,
        generator=generator,
        context=context,
        generation=generation,
        warnings=tuple(dict.fromkeys(warnings)),
        calibration_profile_id=calibration.profile_id,
        calibration_profile_version=calibration.version,
        calibration_profile_sha256=calibration_record.content_sha256,
        unverified_calibration_fields=unverified_calibration_fields,
    )


def prepare_spec_file(
    spec_path: str | Path,
    *,
    workspace_root: str | Path | None = None,
) -> PreparedGeneration:
    return prepare_generation(
        load_project_spec(spec_path), workspace_root=workspace_root
    )


def generate_project(
    spec_path: str | Path,
    *,
    workspace_root: str | Path | None = None,
) -> PipelineResult:
    """Run the full local vertical slice and write a machine-readable manifest."""

    source_spec_path = Path(spec_path).resolve()
    root = (
        Path(workspace_root).resolve()
        if workspace_root is not None
        else Path(__file__).resolve().parents[2] / "workspace"
    )
    try:
        source_spec_bytes = source_spec_path.read_bytes()
    except OSError as exc:
        raise SpecificationError(
            f"Could not read project specification {source_spec_path}: {exc}"
        ) from exc
    spec_from_bytes = load_project_spec_bytes(
        source_spec_bytes,
        source=f"project specification {source_spec_path}",
    )
    prepared = prepare_generation(spec_from_bytes, workspace_root=root)
    spec = prepared.spec
    root.mkdir(parents=True, exist_ok=True)
    version_directory = (root / spec.project.id / spec.project.version).resolve()
    try:
        version_directory.relative_to(root.resolve())
    except ValueError as exc:
        raise SpecificationError("Resolved workspace path escaped the workspace root.") from exc
    if version_directory.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing project version workspace: {version_directory}"
        )

    artifact_suffix = "_fit_coupon" if prepared.generation.artifact_kind == "fit_coupon" else ""
    stem = f"{spec.project.id}_{spec.project.version}{artifact_suffix}"
    scad_path = version_directory / f"{stem}.scad"
    stl_path = version_directory / f"{stem}.stl"
    spec_snapshot = version_directory / "spec.snapshot.json"
    manifest_path = version_directory / "artifact-manifest.json"
    now = utc_now()

    with tempfile.TemporaryDirectory(prefix=".ppw3-build-", dir=root) as staging_parent:
        staging_directory = Path(staging_parent) / "payload"
        staging_directory.mkdir()
        staged_scad = staging_directory / scad_path.name
        staged_stl = staging_directory / stl_path.name
        staged_spec = staging_directory / spec_snapshot.name
        staged_manifest = staging_directory / manifest_path.name

        _atomic_write(staged_spec, source_spec_bytes)
        state = WorkflowStateMachine(spec.workflow_state)
        state.advance(
            WorkflowState.MEASUREMENT_CONTRACT_COMPLETE,
            occurred_at=now,
            evidence={
                "schema_version": spec.schema_version,
                "protected_parameters": sorted(
                    prepared.generation.nominal_protected_dimensions_mm
                ),
                "measurement_count": len(spec.measurement_contract),
            },
        )

        _atomic_write(staged_scad, prepared.generation.source.encode("utf-8"))
        state.advance(
            WorkflowState.GENERATED,
            occurred_at=utc_now(),
            evidence={
                "generator_id": prepared.generator.metadata.generator_id,
                "generator_version": prepared.generator.metadata.version,
                "source": scad_path.name,
            },
        )

        compile_result = compile_binary_stl(staged_scad, staged_stl)
        state.advance(
            WorkflowState.SCAD_COMPILED,
            occurred_at=utc_now(),
            evidence={
                "openscad_version": compile_result.version,
                "stl": stl_path.name,
            },
        )

        quality_report = require_valid_mesh(
            staged_stl,
            expected_body_count=prepared.generation.expected_body_count,
        )
        state.advance(
            WorkflowState.MESH_VALID,
            occurred_at=utc_now(),
            evidence={
                "watertight": quality_report.watertight,
                "body_count": quality_report.body_count,
                "volume_mm3": quality_report.volume_mm3,
            },
        )

        dimension_report = require_valid_mesh(
            staged_stl,
            expected_extents_mm=prepared.generation.expected_bounds_mm,
            bounds_tolerance_mm=spec.verification_policy.mesh_bounds_tolerance_mm,
            expected_body_count=prepared.generation.expected_body_count,
        )
        state.advance(
            WorkflowState.DIMENSIONS_REVIEWED,
            occurred_at=utc_now(),
            evidence={
                "expected_extents_mm": [
                    str(value) for value in prepared.generation.expected_bounds_mm
                ],
                "actual_extents_mm": [str(value) for value in dimension_report.extents_mm],
                "delta_mm": [
                    str(value) for value in dimension_report.bounds_delta_mm or ()
                ],
                "tolerance_mm": str(spec.verification_policy.mesh_bounds_tolerance_mm),
            },
        )

        if spec.generation_mode is GenerationMode.FIT_COUPON:
            state.advance(
                WorkflowState.FIT_COUPON_GENERATED,
                occurred_at=utc_now(),
                evidence={
                    "interface_parameter": spec.fit_coupon.interface_parameter,  # type: ignore[union-attr]
                    "candidate_offsets_mm": [
                        str(value) for value in prepared.context.coupon_offsets_mm
                    ],
                    "artifact": stl_path.name,
                },
            )
        else:
            state.advance(
                WorkflowState.FULL_PART_EXPORTED,
                occurred_at=utc_now(),
                evidence={"artifact": stl_path.name},
            )

        scad_role = (
            ArtifactRole.FIT_COUPON_SCAD
            if spec.generation_mode is GenerationMode.FIT_COUPON
            else ArtifactRole.SCAD_SOURCE
        )
        stl_role = (
            ArtifactRole.FIT_COUPON_STL
            if spec.generation_mode is GenerationMode.FIT_COUPON
            else ArtifactRole.STL_MESH
        )
        records = (
            _staged_artifact_record(
                staged_spec,
                spec_snapshot,
                role=ArtifactRole.SPEC_SNAPSHOT,
                workspace_root=root,
                created_at=now,
                media_type="application/json",
            ),
            _staged_artifact_record(
                staged_scad,
                scad_path,
                role=scad_role,
                workspace_root=root,
                created_at=now,
                media_type="text/plain",
            ),
            _staged_artifact_record(
                staged_stl,
                stl_path,
                role=stl_role,
                workspace_root=root,
                created_at=now,
                media_type="model/stl",
            ),
        )
        compile_check = compile_result.to_dict()
        compile_check["output_path"] = stl_path.relative_to(root).as_posix()
        mesh_check = dimension_report.to_dict()
        mesh_check["path"] = stl_path.relative_to(root).as_posix()
        mesh_check["expected_body_count"] = prepared.generation.expected_body_count
        manifest = ArtifactManifest(
            project_id=spec.project.id,
            project_version=spec.project.version,
            generator_id=prepared.generator.metadata.generator_id,
            generator_version=prepared.generator.metadata.version,
            generation_mode=spec.generation_mode.value,
            workflow_state=state.state.value,
            created_at=now,
            artifacts=records,
            checks={
                "specification": {
                    "valid": True,
                    "schema_version": spec.schema_version,
                    "source_sha256": records[0].sha256,
                },
                "normalized_parameters_mm": prepared.generation.resolved_parameters_mm,
                "expected_bounds_mm": prepared.generation.expected_bounds_mm,
                "calibration_profile": {
                    "id": prepared.calibration_profile_id,
                    "version": prepared.calibration_profile_version,
                    "sha256": prepared.calibration_profile_sha256,
                    "status": (
                        CalibrationStatus.PROVEN.value
                        if not prepared.unverified_calibration_fields
                        else CalibrationStatus.UNVERIFIED_STARTER.value
                    ),
                    "unverified_fields": prepared.unverified_calibration_fields,
                },
                "accepted_fit_coupon": (
                    spec.fit_coupon_evidence.to_dict()
                    if spec.fit_coupon_evidence is not None
                    else None
                ),
                "openscad": compile_check,
                "mesh": mesh_check,
                "workflow_history": [item.to_dict() for item in state.history],
            },
            warnings=prepared.warnings,
            unresolved_assumptions=spec.unresolved_assumptions,
            physical_fit_confirmed=False,
        )
        manifest_document = _json_ready(manifest.to_dict())
        _atomic_write(
            staged_manifest,
            (json.dumps(manifest_document, indent=2, sort_keys=True) + "\n").encode(
                "utf-8"
            ),
        )

        version_directory.parent.mkdir(parents=True, exist_ok=True)
        if version_directory.exists():
            raise FileExistsError(
                f"Refusing to overwrite existing project version workspace: {version_directory}"
            )
        publish_bundle(staging_directory, version_directory, manifest_name="artifact-manifest.json")

    final_report = replace(dimension_report, path=stl_path)
    return PipelineResult(
        spec=spec,
        output_directory=version_directory,
        scad_path=scad_path,
        stl_path=stl_path,
        manifest_path=manifest_path,
        reached_state=state.state,
        mesh_report=final_report,
        warnings=prepared.warnings,
    )
