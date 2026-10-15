"""Evidence-chain services used by thin owner-facing CLI adapters."""

from __future__ import annotations

import json
import os
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Sequence

from jsonschema import Draft202012Validator

from core.models.artifacts import (
    ArtifactRecord,
    ArtifactRole,
    read_and_verify_artifact,
    sha256_bytes,
)
from core.models.evidence import (
    FileBinding,
    FitConfiguration,
    FitCouponOutcome,
    FitCouponResultEvidence,
    GeneratorBinding,
    InterfaceFitResult,
    MeasuredDimension,
    PhysicalFitEvidence,
)
from core.models.spec import GenerationMode, ProjectSpec
from core.profiles.repository import (
    load_calibration_profile_record,
)
from core.units.conversion import as_decimal
from core.validation.specification import load_project_spec_bytes
from core.workflow.states import WorkflowState
from generators.registry import get_generator


FIT_RESULT_FILENAME = "fit-result.evidence.json"
PHYSICAL_FIT_FILENAME = "physical-fit.evidence.json"
MANIFEST_FILENAME = "artifact-manifest.json"
_DIGEST_LENGTH = 64
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_WORKSPACE_ROOT = _REPOSITORY_ROOT / "workspace"


class EvidenceValidationError(ValueError):
    """Raised when supplied owner input cannot form defensible evidence."""


class EvidenceIntegrityError(EvidenceValidationError):
    """Raised when recorded bytes do not match a required digest or binding."""


class EvidenceConflictError(FileExistsError):
    """Raised when an immutable output already exists."""


@dataclass(frozen=True, slots=True)
class VerifiedGeneration:
    manifest_path: Path
    workspace_root: Path
    version_directory: Path
    manifest_document: Mapping[str, object]
    manifest_binding: FileBinding
    spec: ProjectSpec
    specification_binding: FileBinding
    stl_binding: FileBinding
    scad_binding: FileBinding | None
    calibration_profile_id: str
    calibration_profile_version: str
    calibration_profile_sha256: str | None


@dataclass(frozen=True, slots=True)
class VerifiedFitCouponResult:
    evidence_path: Path
    evidence_binding: FileBinding
    evidence: FitCouponResultEvidence
    generation: VerifiedGeneration


@dataclass(frozen=True, slots=True)
class VerifiedPhysicalFit:
    evidence_path: Path
    evidence_binding: FileBinding
    evidence: PhysicalFitEvidence
    generation: VerifiedGeneration


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceValidationError(f"{label} must be an ISO-8601 date-time.") from exc
    if parsed.tzinfo is None:
        raise EvidenceValidationError(f"{label} must include a timezone.")
    return parsed


def _require_digest(value: str, label: str) -> str:
    digest = value.strip()
    if len(digest) != _DIGEST_LENGTH or any(
        character not in "0123456789abcdef" for character in digest
    ):
        raise EvidenceValidationError(f"{label} must be a lowercase SHA-256 digest.")
    return digest


def _read_once(path: Path, label: str) -> tuple[Path, bytes]:
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_file():
            raise OSError("not a file")
        return resolved, resolved.read_bytes()
    except OSError as exc:
        raise EvidenceIntegrityError(f"Could not read {label}: {path}") from exc


def _parse_object(data: bytes, label: str) -> dict[str, object]:
    try:
        document = json.loads(data.decode("utf-8"), parse_float=Decimal)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceIntegrityError(f"Invalid JSON in {label}: {exc}") from exc
    if not isinstance(document, dict):
        raise EvidenceIntegrityError(f"{label} must contain a JSON object.")
    return document


@lru_cache(maxsize=2)
def _evidence_validator(schema_filename: str) -> Draft202012Validator:
    schema_path = _REPOSITORY_ROOT / "schemas" / schema_filename
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceIntegrityError(f"Could not load evidence schema {schema_path}: {exc}") from exc
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _validate_evidence_document(document: Mapping[str, object], schema_filename: str) -> None:
    errors = sorted(
        _evidence_validator(schema_filename).iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        messages = []
        for error in errors:
            path = "$" + "".join(
                f"[{part}]" if isinstance(part, int) else f".{part}"
                for part in error.absolute_path
            )
            messages.append(f"{path}: {error.message}")
        raise EvidenceIntegrityError("Evidence schema validation failed: " + "; ".join(messages))


def parse_fit_coupon_result_bytes(
    data: bytes, *, source: str = "fit-result evidence bytes"
) -> FitCouponResultEvidence:
    """Strictly schema/domain-validate one already-read fit-result byte buffer."""

    document = _parse_object(data, source)
    _validate_evidence_document(document, "fit-result-evidence-v1.schema.json")
    try:
        return FitCouponResultEvidence.from_dict(document)
    except (KeyError, TypeError, ValueError) as exc:
        raise EvidenceIntegrityError(f"Fit-result evidence is invalid: {exc}") from exc


def parse_physical_fit_bytes(
    data: bytes, *, source: str = "physical-fit evidence bytes"
) -> PhysicalFitEvidence:
    """Strictly schema/domain-validate one already-read physical evidence buffer."""

    document = _parse_object(data, source)
    _validate_evidence_document(document, "physical-fit-evidence-v1.schema.json")
    try:
        return PhysicalFitEvidence.from_dict(document)
    except (KeyError, TypeError, ValueError) as exc:
        raise EvidenceIntegrityError(f"Physical-fit evidence is invalid: {exc}") from exc


def _json_text(value: object, level: int = 0) -> str:
    """Serialize JSON without converting Decimal values through binary floats."""

    indent = "  " * level
    child_indent = "  " * (level + 1)
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("JSON numeric values must be finite.")
        return format(value, "f")
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return format(as_decimal(value), "f")
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, Mapping):
        if not value:
            return "{}"
        items = []
        for key in sorted(value, key=str):
            rendered = _json_text(value[key], level + 1)
            items.append(f"{child_indent}{json.dumps(str(key), ensure_ascii=False)}: {rendered}")
        return "{\n" + ",\n".join(items) + f"\n{indent}" + "}"
    if isinstance(value, (tuple, list)):
        if not value:
            return "[]"
        items = [f"{child_indent}{_json_text(item, level + 1)}" for item in value]
        return "[\n" + ",\n".join(items) + f"\n{indent}]"
    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


def _json_bytes(document: Mapping[str, object]) -> bytes:
    return (_json_text(document) + "\n").encode("utf-8")


def _validated_evidence_bytes(
    document: Mapping[str, object], schema_filename: str
) -> bytes:
    _validate_evidence_document(document, schema_filename)
    return _json_bytes(document)


def _atomic_exclusive_create(path: Path, data: bytes) -> None:
    """Publish complete bytes atomically while refusing every existing target."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise EvidenceConflictError(f"Refusing to overwrite immutable output: {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise EvidenceConflictError(f"Refusing to overwrite immutable output: {path}") from exc
    finally:
        temporary.unlink(missing_ok=True)


def _binding(path: Path, data: bytes, *, root: Path) -> FileBinding:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise EvidenceIntegrityError(f"Evidence-bound file is outside workspace root: {path}") from exc
    return FileBinding(relative.as_posix(), sha256_bytes(data), len(data))


def _artifact_records(document: Mapping[str, object]) -> dict[ArtifactRole, ArtifactRecord]:
    artifacts = document.get("artifacts")
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        raise EvidenceIntegrityError("Artifact manifest has no valid artifacts array.")
    records: dict[ArtifactRole, ArtifactRecord] = {}
    for item in artifacts:
        if not isinstance(item, Mapping):
            raise EvidenceIntegrityError("Artifact manifest contains a non-object record.")
        try:
            record = ArtifactRecord.from_dict(item)
        except (KeyError, TypeError, ValueError) as exc:
            raise EvidenceIntegrityError(f"Invalid artifact record: {exc}") from exc
        if record.role in records:
            raise EvidenceIntegrityError(f"Artifact manifest repeats role {record.role.value}.")
        records[record.role] = record
    return records


def _manifest_generator(document: Mapping[str, object]) -> tuple[str, str]:
    generator = document.get("generator")
    if not isinstance(generator, Mapping):
        raise EvidenceIntegrityError("Artifact manifest generator must be an object.")
    try:
        return str(generator["id"]), str(generator["version"])
    except KeyError as exc:
        raise EvidenceIntegrityError("Artifact manifest generator binding is incomplete.") from exc


def _calibration_binding(
    document: Mapping[str, object]
) -> tuple[str, str, str | None]:
    checks = document.get("checks")
    if not isinstance(checks, Mapping):
        raise EvidenceIntegrityError("Artifact manifest checks must be an object.")
    calibration = checks.get("calibration_profile")
    if not isinstance(calibration, Mapping):
        raise EvidenceIntegrityError("Artifact manifest calibration check is missing.")
    try:
        digest = calibration.get("sha256")
        if digest is not None:
            digest = _require_digest(str(digest), "Manifest calibration profile SHA-256")
        return str(calibration["id"]), str(calibration["version"]), digest
    except KeyError as exc:
        raise EvidenceIntegrityError("Artifact manifest calibration binding is incomplete.") from exc


def _require_successful_computational_checks(document: Mapping[str, object]) -> None:
    checks = document.get("checks")
    if not isinstance(checks, Mapping):
        raise EvidenceIntegrityError("Artifact manifest checks must be an object.")
    specification = checks.get("specification")
    openscad = checks.get("openscad")
    mesh = checks.get("mesh")
    if not all(isinstance(item, Mapping) for item in (specification, openscad, mesh)):
        raise EvidenceIntegrityError("Artifact manifest is missing computational checks.")
    if specification.get("valid") is not True:  # type: ignore[union-attr]
        raise EvidenceIntegrityError("Artifact manifest does not record a valid specification.")
    if openscad.get("returncode") != 0:  # type: ignore[union-attr]
        raise EvidenceIntegrityError("Artifact manifest does not record successful OpenSCAD compilation.")
    if mesh.get("passed") is not True:  # type: ignore[union-attr]
        raise EvidenceIntegrityError("Artifact manifest does not record a passing mesh/dimensions check.")


def _require_coupon_generation_evidence(
    document: Mapping[str, object], spec: ProjectSpec
) -> None:
    """Bind a coupon record to the interface/candidates actually rendered."""

    if spec.fit_coupon is None:
        raise EvidenceIntegrityError("Coupon specification has no fit-coupon request.")
    checks = document.get("checks")
    if not isinstance(checks, Mapping):
        raise EvidenceIntegrityError("Coupon manifest checks must be an object.")
    history = checks.get("workflow_history")
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        raise EvidenceIntegrityError("Coupon manifest workflow history is missing.")
    generated_transitions = []
    for transition in history:
        if isinstance(transition, Mapping) and transition.get("to_state") == (
            WorkflowState.FIT_COUPON_GENERATED.value
        ):
            generated_transitions.append(transition)
    if len(generated_transitions) != 1 or history[-1] is not generated_transitions[0]:
        raise EvidenceIntegrityError(
            "Coupon manifest must end with exactly one fit_coupon_generated transition."
        )
    transition_evidence = generated_transitions[0].get("evidence")
    if not isinstance(transition_evidence, Mapping):
        raise EvidenceIntegrityError("fit_coupon_generated transition evidence is missing.")
    if transition_evidence.get("interface_parameter") != spec.fit_coupon.interface_parameter:
        raise EvidenceIntegrityError(
            "Generated coupon interface does not match the specification snapshot."
        )
    generated_offsets = transition_evidence.get("candidate_offsets_mm")
    if not isinstance(generated_offsets, Sequence) or isinstance(
        generated_offsets, (str, bytes)
    ):
        raise EvidenceIntegrityError("Generated coupon candidate offsets are missing.")
    try:
        normalized_offsets = tuple(as_decimal(value) for value in generated_offsets)
    except (TypeError, ValueError) as exc:
        raise EvidenceIntegrityError("Generated coupon candidate offsets are invalid.") from exc
    spec_offsets = spec.fit_coupon.candidate_offsets_mm(spec.input_units)
    if normalized_offsets != spec_offsets:
        raise EvidenceIntegrityError(
            "Generated coupon candidate offsets do not match the specification snapshot."
        )
    if spec.generator.version != "1.1.0":
        return
    normalized_parameters = checks.get("normalized_parameters_mm")
    if not isinstance(normalized_parameters, Mapping):
        raise EvidenceIntegrityError("Coupon normalized parameters are missing.")
    candidate_map = normalized_parameters.get("coupon_candidate_map")
    if not isinstance(candidate_map, Sequence) or isinstance(candidate_map, (str, bytes)):
        raise EvidenceIntegrityError("Generator 1.1.0 coupon candidate map is missing.")
    if len(candidate_map) != len(spec_offsets):
        raise EvidenceIntegrityError(
            "Generator 1.1.0 coupon candidate map length does not match candidates."
        )
    for expected_index, (entry, expected_offset) in enumerate(
        zip(candidate_map, spec_offsets), start=1
    ):
        if not isinstance(entry, Mapping):
            raise EvidenceIntegrityError("Coupon candidate map entries must be objects.")
        if type(entry.get("index")) is not int or entry.get("index") != expected_index:
            raise EvidenceIntegrityError(
                "Coupon candidate map indexes must be sequential and one-based."
            )
        if str(entry.get("label")) != str(expected_index):
            raise EvidenceIntegrityError(
                "Coupon candidate map labels must match their sequential indexes."
            )
        try:
            mapped_offset = as_decimal(entry["offset_mm"])  # type: ignore[arg-type]
        except (KeyError, TypeError, ValueError) as exc:
            raise EvidenceIntegrityError(
                "Coupon candidate map offsets are missing or invalid."
            ) from exc
        if mapped_offset != expected_offset:
            raise EvidenceIntegrityError(
                "Coupon candidate map offsets do not match generated candidates."
            )


def _resolve_coupon_candidate_label(
    generation: VerifiedGeneration, selected_offset_mm: Decimal
) -> str | None:
    """Resolve the printed one-based label for a selected v1.1 candidate."""

    if generation.spec.generator.version != "1.1.0":
        return None
    checks = generation.manifest_document.get("checks")
    normalized = checks.get("normalized_parameters_mm") if isinstance(checks, Mapping) else None
    candidate_map = normalized.get("coupon_candidate_map") if isinstance(normalized, Mapping) else None
    if not isinstance(candidate_map, Sequence) or isinstance(candidate_map, (str, bytes)):
        raise EvidenceIntegrityError("Generator 1.1.0 coupon candidate map is missing.")
    matching_labels = [
        str(entry["label"])
        for entry in candidate_map
        if isinstance(entry, Mapping)
        and "offset_mm" in entry
        and as_decimal(entry["offset_mm"]) == selected_offset_mm  # type: ignore[arg-type]
    ]
    if len(matching_labels) != 1:
        raise EvidenceIntegrityError(
            "Selected coupon offset does not resolve to exactly one printed candidate label."
        )
    return matching_labels[0]


def _verify_generation_manifest(
    manifest_path: str | Path,
    *,
    expected_manifest_sha256: str | None,
) -> VerifiedGeneration:
    resolved_manifest, manifest_bytes = _read_once(Path(manifest_path), "artifact manifest")
    actual_manifest_sha = sha256_bytes(manifest_bytes)
    if expected_manifest_sha256 is not None:
        expected = _require_digest(expected_manifest_sha256, "Expected manifest SHA-256")
        if actual_manifest_sha != expected:
            raise EvidenceIntegrityError(
                "Artifact manifest SHA-256 does not match the owner-supplied expected digest."
            )
    document = _parse_object(manifest_bytes, "artifact manifest")
    try:
        project_id = str(document["project_id"])
        project_version = str(document["project_version"])
        generation_mode = str(document["generation_mode"])
        workflow_state = str(document["workflow_state"])
    except KeyError as exc:
        raise EvidenceIntegrityError("Artifact manifest identity is incomplete.") from exc
    version_directory = resolved_manifest.parent
    if (
        resolved_manifest.name != MANIFEST_FILENAME
        or version_directory.name != project_version
        or version_directory.parent.name != project_id
    ):
        raise EvidenceIntegrityError(
            "Artifact manifest path does not match its project/version identity."
        )
    workspace_root = version_directory.parent.parent.resolve()
    manifest_binding = _binding(resolved_manifest, manifest_bytes, root=workspace_root)
    records = _artifact_records(document)
    expected_stl_role = (
        ArtifactRole.FIT_COUPON_STL
        if generation_mode == GenerationMode.FIT_COUPON.value
        else ArtifactRole.STL_MESH
    )
    expected_scad_role = (
        ArtifactRole.FIT_COUPON_SCAD
        if generation_mode == GenerationMode.FIT_COUPON.value
        else ArtifactRole.SCAD_SOURCE
    )
    try:
        spec_record = records[ArtifactRole.SPEC_SNAPSHOT]
        stl_record = records[expected_stl_role]
        scad_record = records[expected_scad_role]
    except KeyError as exc:
        raise EvidenceIntegrityError(f"Artifact manifest is missing required role: {exc}") from exc
    try:
        spec_path, spec_bytes = read_and_verify_artifact(spec_record, workspace_root=workspace_root)
        stl_path, stl_bytes = read_and_verify_artifact(stl_record, workspace_root=workspace_root)
        scad_path, scad_bytes = read_and_verify_artifact(scad_record, workspace_root=workspace_root)
    except ValueError as exc:
        raise EvidenceIntegrityError(f"Artifact failed size/SHA-256 verification: {exc}") from exc
    if any(path.parent != version_directory for path in (spec_path, stl_path, scad_path)):
        raise EvidenceIntegrityError("Manifest artifacts are not beside the project/version manifest.")
    try:
        spec = load_project_spec_bytes(spec_bytes, source=f"specification snapshot {spec_path}")
    except ValueError as exc:
        raise EvidenceIntegrityError(f"Specification snapshot is invalid: {exc}") from exc
    generator_id, generator_version = _manifest_generator(document)
    if (
        spec.project.id != project_id
        or spec.project.version != project_version
        or spec.generator.id != generator_id
        or spec.generator.version != generator_version
        or spec.generation_mode.value != generation_mode
    ):
        raise EvidenceIntegrityError(
            "Specification snapshot identity/configuration does not match the manifest."
        )
    if generation_mode == GenerationMode.FIT_COUPON.value:
        if workflow_state != WorkflowState.FIT_COUPON_GENERATED.value:
            raise EvidenceIntegrityError("Coupon manifest must be at fit_coupon_generated.")
    elif generation_mode == GenerationMode.FULL_PART.value:
        if workflow_state != WorkflowState.FULL_PART_EXPORTED.value:
            raise EvidenceIntegrityError("Full-part manifest must be at full_part_exported.")
    else:
        raise EvidenceIntegrityError(f"Unsupported manifest generation mode: {generation_mode!r}.")
    _require_successful_computational_checks(document)
    if generation_mode == GenerationMode.FIT_COUPON.value:
        _require_coupon_generation_evidence(document, spec)
    checks = document["checks"]
    specification_check = checks["specification"]  # type: ignore[index]
    if specification_check.get("source_sha256") != spec_record.sha256:  # type: ignore[union-attr]
        raise EvidenceIntegrityError("Manifest specification check is not bound to the snapshot SHA-256.")
    calibration_id, calibration_version, calibration_sha256 = _calibration_binding(document)
    if spec.fit_profile != calibration_id:
        raise EvidenceIntegrityError("Specification calibration profile does not match the manifest.")
    try:
        installed_record = load_calibration_profile_record(calibration_id)
        installed_profile = installed_record.profile
    except (KeyError, ValueError) as exc:
        raise EvidenceIntegrityError(f"Bound calibration profile is unavailable: {exc}") from exc
    if installed_profile.version != calibration_version:
        raise EvidenceIntegrityError("Installed calibration profile version does not match the manifest.")
    if spec.generator.version == "1.1.0" and calibration_sha256 is None:
        raise EvidenceIntegrityError(
            "Generator 1.1.0 manifest lacks a calibration-profile content SHA-256."
        )
    if (
        calibration_sha256 is not None
        and installed_record.content_sha256 != calibration_sha256
    ):
        raise EvidenceIntegrityError(
            "Installed calibration profile content does not match the manifest SHA-256."
        )
    return VerifiedGeneration(
        manifest_path=resolved_manifest,
        workspace_root=workspace_root,
        version_directory=version_directory,
        manifest_document=document,
        manifest_binding=manifest_binding,
        spec=spec,
        specification_binding=_binding(spec_path, spec_bytes, root=workspace_root),
        stl_binding=_binding(stl_path, stl_bytes, root=workspace_root),
        scad_binding=_binding(scad_path, scad_bytes, root=workspace_root),
        calibration_profile_id=calibration_id,
        calibration_profile_version=calibration_version,
        calibration_profile_sha256=calibration_sha256,
    )


def verify_generation_manifest(manifest_path: str | Path, *, expected_manifest_sha256: str | None = None) -> VerifiedGeneration:
    """Verify immutable source, mesh, spec and profile bindings without recording evidence.

    This checks integrity and historical computational records; callers re-run
    mesh checks separately. It never establishes a physical result.
    """
    return _verify_generation_manifest(manifest_path, expected_manifest_sha256=expected_manifest_sha256)


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


def _load_source_spec(path: str | Path) -> tuple[Path, bytes, dict[str, object], ProjectSpec]:
    resolved, data = _read_once(Path(path), "source specification")
    document = _parse_object(data, "source specification")
    try:
        spec = load_project_spec_bytes(data, source=f"source specification {resolved}")
    except ValueError as exc:
        raise EvidenceValidationError(f"Source specification is invalid: {exc}") from exc
    return resolved, data, document, spec


def _require_draft_full_part(spec: ProjectSpec) -> None:
    if spec.generation_mode is not GenerationMode.FULL_PART:
        raise EvidenceValidationError("Source specification must describe a full part.")
    if spec.workflow_state is not WorkflowState.DRAFT:
        raise EvidenceValidationError("Source full-part specification must be at draft.")
    if spec.fit_coupon is not None:
        raise EvidenceValidationError("Source full-part specification cannot contain a coupon request.")


def _set_new_version_common(document: dict[str, object], *, now: str) -> None:
    document["workflow_state"] = WorkflowState.DRAFT.value
    document["generated_artifacts"] = []
    document["physical_verification"] = {
        "status": "not_confirmed",
        "confirmed_at": None,
        "confirmed_by": None,
        "evidence": [],
        "notes": "No complete-part physical-fit confirmation has been recorded.",
    }
    document["timestamps"] = {"created_at": now, "updated_at": now}


def create_fit_coupon_spec(
    source_spec_path: str | Path,
    *,
    interface_parameter: str,
    candidate_offsets: Sequence[Decimal | int | float | str],
    coupon_project_id: str,
    coupon_project_version: str,
    output_spec_path: str | Path,
    generate: bool = False,
    workspace_root: str | Path | None = None,
) -> Path:
    """Create, and optionally generate, a new coupon spec without overwriting."""

    _, source_bytes, source_document, source_spec = _load_source_spec(source_spec_path)
    _require_draft_full_part(source_spec)
    if source_spec.fit_coupon_evidence is not None:
        raise EvidenceValidationError("Source specification already cites coupon evidence.")
    generator = get_generator(source_spec.generator.id, source_spec.generator.version)
    parameters = _plain(source_spec.generator.parameters)
    if not isinstance(parameters, Mapping):
        raise EvidenceValidationError("Source generator parameters must be an object.")
    if not generator.supports_coupon_interface(interface_parameter, parameters):
        supported = ", ".join(generator.applicable_coupon_interfaces(parameters)) or "none"
        raise EvidenceValidationError(
            f"Generator {generator.metadata.generator_id} {generator.metadata.version} does not "
            f"support coupon interface {interface_parameter!r}; supported: {supported}."
        )
    offsets = tuple(as_decimal(value) for value in candidate_offsets)
    if not 2 <= len(offsets) <= 12 or len(set(offsets)) != len(offsets):
        raise EvidenceValidationError("Candidate offsets require 2-12 unique explicit values.")
    project_id = coupon_project_id.strip()
    version = coupon_project_version.strip()
    if not project_id or not version:
        raise EvidenceValidationError("Coupon project ID and version cannot be empty.")
    if project_id == source_spec.project.id:
        raise EvidenceValidationError(
            "Coupon project ID must be new and different from the source project ID."
        )
    output = Path(output_spec_path).resolve()
    if output.exists():
        raise EvidenceConflictError(f"Refusing to overwrite coupon specification: {output}")
    effective_workspace_root = (
        Path(workspace_root).resolve()
        if workspace_root is not None
        else _DEFAULT_WORKSPACE_ROOT.resolve()
    )
    workspace_version = effective_workspace_root / project_id / version
    if workspace_version.exists():
        raise EvidenceConflictError(
            f"Refusing an existing coupon project/version workspace: {workspace_version}"
        )
    now = _now()
    document = deepcopy(source_document)
    project = document.get("project")
    if not isinstance(project, dict):
        raise EvidenceValidationError("Source specification project must be an object.")
    project["id"] = project_id
    project["version"] = version
    project["name"] = f"{source_spec.project.name} Fit Coupon - {interface_parameter}"
    document["generation_mode"] = GenerationMode.FIT_COUPON.value
    document["fit_coupon"] = {
        "interface_parameter": interface_parameter,
        "candidate_offsets": list(offsets),
        "notes": "Explicit owner-supplied candidate offsets; no printed result is implied.",
        "source_project_id": source_spec.project.id,
        "source_project_version": source_spec.project.version,
        "source_spec_sha256": sha256_bytes(source_bytes),
    }
    document["fit_coupon_evidence"] = None
    _set_new_version_common(document, now=now)
    data = _json_bytes(document)
    try:
        coupon_spec = load_project_spec_bytes(
            data, source=f"new coupon specification {output}"
        )
        from core.workflow.pipeline import prepare_generation

        prepare_generation(coupon_spec, workspace_root=effective_workspace_root)
    except Exception as exc:
        raise EvidenceValidationError(
            f"New coupon specification failed semantic validation: {exc}"
        ) from exc
    _atomic_exclusive_create(output, data)
    if generate:
        from core.workflow.pipeline import generate_project

        generate_project(output, workspace_root=effective_workspace_root)
    return output


def _creation_time_floor(generation: VerifiedGeneration) -> datetime:
    times = [_parse_time(str(generation.manifest_document["created_at"]), "Manifest created_at")]
    records = _artifact_records(generation.manifest_document)
    times.extend(_parse_time(record.created_at, f"{record.role.value} created_at") for record in records.values())
    return max(times)


def record_fit_coupon_result(
    manifest_path: str | Path,
    *,
    expected_manifest_sha256: str,
    selected_candidate_offset_mm: Decimal | int | float | str,
    tested_by: str,
    tested_at: str,
    acceptance_criterion: str,
    observed_result: str,
    notes: str,
    passed: bool,
    require_passed: bool = False,
) -> Path:
    """Verify a coupon chain and append one immutable manual result record."""

    generation = _verify_generation_manifest(
        manifest_path, expected_manifest_sha256=expected_manifest_sha256
    )
    if generation.spec.generation_mode is not GenerationMode.FIT_COUPON:
        raise EvidenceValidationError("Fit-coupon evidence requires a fit_coupon manifest.")
    if generation.spec.fit_coupon is None:
        raise EvidenceIntegrityError("Coupon specification snapshot has no fit_coupon request.")
    output = generation.version_directory / FIT_RESULT_FILENAME
    if output.exists():
        raise EvidenceConflictError(
            f"A fit result already exists for this coupon project/version: {output}"
        )
    if type(passed) is not bool:
        raise EvidenceValidationError("passed must be true or false.")
    if require_passed and not passed:
        raise EvidenceValidationError("Passed evidence was requested, but the recorded result failed.")
    selected = as_decimal(selected_candidate_offset_mm)
    candidates = generation.spec.fit_coupon.candidate_offsets_mm(generation.spec.input_units)
    if selected not in candidates:
        raise EvidenceValidationError(
            "Selected candidate offset was not present in the generated coupon specification."
        )
    _resolve_coupon_candidate_label(generation, selected)
    generator = get_generator(
        generation.spec.generator.id, generation.spec.generator.version
    )
    parameters = _plain(generation.spec.generator.parameters)
    if not isinstance(parameters, Mapping) or not generator.supports_coupon_interface(
        generation.spec.fit_coupon.interface_parameter, parameters
    ):
        raise EvidenceIntegrityError("Coupon interface is unsupported by the bound generator version.")
    source_request = generation.spec.fit_coupon
    if generator.metadata.version == "1.1.0" and not source_request.has_source_binding:
        raise EvidenceIntegrityError(
            "Generator 1.1.0 owner evidence requires an exact originating-source binding."
        )
    now = _now()
    tested_time = _parse_time(tested_at, "tested_at")
    if tested_time < _creation_time_floor(generation):
        raise EvidenceValidationError("tested_at cannot predate the coupon manifest or artifacts.")
    if tested_time > _parse_time(now, "record creation time"):
        raise EvidenceValidationError("tested_at cannot be later than the evidence recording time.")
    evidence = FitCouponResultEvidence(
        coupon_project_id=generation.spec.project.id,
        coupon_project_version=generation.spec.project.version,
        generator=GeneratorBinding(
            generation.spec.generator.id, generation.spec.generator.version
        ),
        manifest=generation.manifest_binding,
        stl=generation.stl_binding,
        specification_snapshot=generation.specification_binding,
        configuration=FitConfiguration(
            interface_parameter=generation.spec.fit_coupon.interface_parameter,
            candidate_offsets_mm=candidates,
            selected_candidate_offset_mm=selected,
            printer_profile=generation.spec.printer_profile,
            material=generation.spec.material,
            nozzle_diameter_mm=generation.spec.nozzle_diameter_mm,
            calibration_profile_id=generation.calibration_profile_id,
            calibration_profile_version=generation.calibration_profile_version,
            calibration_profile_sha256=generation.calibration_profile_sha256,
        ),
        result=FitCouponOutcome(
            tested_by=tested_by,
            tested_at=tested_at,
            acceptance_criterion=acceptance_criterion,
            observed_result=observed_result,
            passed=passed,
            notes=notes,
        ),
        created_at=now,
        source_project_id=source_request.source_project_id,
        source_project_version=source_request.source_project_version,
        source_spec_sha256=source_request.source_spec_sha256,
    )
    _atomic_exclusive_create(
        output,
        _validated_evidence_bytes(
            evidence.to_dict(), "fit-result-evidence-v1.schema.json"
        ),
    )
    return output


def _assert_file_binding(actual: FileBinding, expected: FileBinding, label: str) -> None:
    if actual != expected:
        raise EvidenceIntegrityError(f"{label} binding does not match the verified artifact bytes.")


def verify_fit_coupon_result(
    evidence_path: str | Path,
    *,
    expected_evidence_sha256: str | None = None,
) -> VerifiedFitCouponResult:
    """Reverify a stored fit result and every byte/configuration binding it cites."""

    resolved, evidence_bytes = _read_once(Path(evidence_path), "fit-result evidence")
    if expected_evidence_sha256 is not None:
        expected = _require_digest(
            expected_evidence_sha256, "Expected fit-result evidence SHA-256"
        )
        if sha256_bytes(evidence_bytes) != expected:
            raise EvidenceIntegrityError(
                "Fit-result evidence SHA-256 does not match the owner-supplied expected digest."
            )
    evidence = parse_fit_coupon_result_bytes(
        evidence_bytes, source=f"fit-result evidence {resolved}"
    )
    version_directory = resolved.parent
    if (
        resolved.name != FIT_RESULT_FILENAME
        or version_directory.name != evidence.coupon_project_version
        or version_directory.parent.name != evidence.coupon_project_id
    ):
        raise EvidenceIntegrityError("Fit-result evidence path does not match coupon identity.")
    workspace_root = version_directory.parent.parent.resolve()
    manifest_path = workspace_root / evidence.manifest.path
    generation = _verify_generation_manifest(
        manifest_path, expected_manifest_sha256=evidence.manifest.sha256
    )
    _assert_file_binding(generation.manifest_binding, evidence.manifest, "Manifest")
    _assert_file_binding(generation.stl_binding, evidence.stl, "Coupon STL")
    _assert_file_binding(
        generation.specification_binding,
        evidence.specification_snapshot,
        "Coupon specification snapshot",
    )
    spec = generation.spec
    if spec.generation_mode is not GenerationMode.FIT_COUPON or spec.fit_coupon is None:
        raise EvidenceIntegrityError("Result evidence does not cite a coupon generation.")
    if (
        spec.project.id != evidence.coupon_project_id
        or spec.project.version != evidence.coupon_project_version
        or spec.generator.id != evidence.generator.generator_id
        or spec.generator.version != evidence.generator.generator_version
    ):
        raise EvidenceIntegrityError("Fit-result identity/generator does not match the coupon.")
    expected_configuration = FitConfiguration(
        interface_parameter=spec.fit_coupon.interface_parameter,
        candidate_offsets_mm=spec.fit_coupon.candidate_offsets_mm(spec.input_units),
        selected_candidate_offset_mm=evidence.configuration.selected_candidate_offset_mm,
        printer_profile=spec.printer_profile,
        material=spec.material,
        nozzle_diameter_mm=spec.nozzle_diameter_mm,
        calibration_profile_id=generation.calibration_profile_id,
        calibration_profile_version=generation.calibration_profile_version,
        calibration_profile_sha256=generation.calibration_profile_sha256,
    )
    if evidence.configuration != expected_configuration:
        raise EvidenceIntegrityError("Fit-result configuration does not match the coupon snapshot.")
    source_request = spec.fit_coupon
    evidence_origin = (
        evidence.source_project_id,
        evidence.source_project_version,
        evidence.source_spec_sha256,
    )
    request_origin = (
        source_request.source_project_id,
        source_request.source_project_version,
        source_request.source_spec_sha256,
    )
    if spec.generator.version == "1.1.0" and not source_request.has_source_binding:
        raise EvidenceIntegrityError(
            "Generator 1.1.0 result evidence lacks an originating-source binding."
        )
    if evidence_origin != request_origin:
        raise EvidenceIntegrityError(
            "Fit-result originating-source binding does not match the coupon snapshot."
        )
    if _parse_time(evidence.result.tested_at, "tested_at") < _creation_time_floor(generation):
        raise EvidenceIntegrityError("Fit-result tested_at predates the coupon manifest or artifacts.")
    if _parse_time(evidence.created_at, "created_at") < _parse_time(
        evidence.result.tested_at, "tested_at"
    ):
        raise EvidenceIntegrityError("Fit-result evidence was created before the recorded test.")
    evidence_binding = _binding(resolved, evidence_bytes, root=workspace_root)
    return VerifiedFitCouponResult(resolved, evidence_binding, evidence, generation)


def create_full_part_spec_from_coupon(
    source_spec_path: str | Path,
    *,
    passed_coupon_evidence_path: str | Path,
    expected_coupon_evidence_sha256: str,
    new_project_version: str,
    output_spec_path: str | Path,
    workspace_root: str | Path | None = None,
) -> Path:
    """Create a new draft full-part version linked to passed immutable coupon evidence."""

    _, source_bytes, source_document, source_spec = _load_source_spec(source_spec_path)
    _require_draft_full_part(source_spec)
    verified = verify_fit_coupon_result(
        passed_coupon_evidence_path,
        expected_evidence_sha256=expected_coupon_evidence_sha256,
    )
    evidence = verified.evidence
    if not evidence.result.passed:
        raise EvidenceValidationError("Failed fit-coupon evidence cannot create a linked full part.")
    source_digest = sha256_bytes(source_bytes)
    evidence_origin = (
        evidence.source_project_id,
        evidence.source_project_version,
        evidence.source_spec_sha256,
    )
    expected_origin = (
        source_spec.project.id,
        source_spec.project.version,
        source_digest,
    )
    if source_spec.generator.version == "1.1.0" and any(
        value is None for value in evidence_origin
    ):
        raise EvidenceValidationError(
            "Generator 1.1.0 requires exact originating-source evidence."
        )
    if evidence.source_project_id is not None and evidence_origin != expected_origin:
        raise EvidenceValidationError(
            "Coupon evidence originated from a different or edited source specification."
        )
    if (
        source_spec.generator.id != evidence.generator.generator_id
        or source_spec.generator.version != evidence.generator.generator_version
    ):
        raise EvidenceValidationError("Coupon generator ID/version does not match the full-part source.")
    if source_spec.input_units is not verified.generation.spec.input_units:
        raise EvidenceValidationError(
            "Coupon input units do not match the full-part source specification."
        )
    if source_spec.project.intent is not verified.generation.spec.project.intent:
        raise EvidenceValidationError("Coupon project intent is stale or does not match the source.")
    if source_spec.measurement_contract != verified.generation.spec.measurement_contract:
        raise EvidenceValidationError(
            "Coupon measurement contract is stale or does not match the source."
        )
    if source_spec.verification_policy != verified.generation.spec.verification_policy:
        raise EvidenceValidationError(
            "Coupon verification policy is stale or does not match the source."
        )
    if source_spec.generator.parameters != verified.generation.spec.generator.parameters:
        raise EvidenceValidationError("Coupon generator parameters are stale or do not match the source.")
    config = evidence.configuration
    if (
        source_spec.printer_profile != config.printer_profile
        or source_spec.material.lower() != config.material.lower()
        or abs(source_spec.nozzle_diameter_mm - config.nozzle_diameter_mm) > Decimal("0.000001")
        or source_spec.fit_profile != config.calibration_profile_id
    ):
        raise EvidenceValidationError(
            "Coupon printer/material/nozzle/calibration configuration does not match the source."
        )
    installed_record = load_calibration_profile_record(source_spec.fit_profile)
    installed_profile = installed_record.profile
    if installed_profile.version != config.calibration_profile_version:
        raise EvidenceValidationError("Coupon calibration profile version is stale.")
    if source_spec.generator.version == "1.1.0" and config.calibration_profile_sha256 is None:
        raise EvidenceValidationError(
            "Generator 1.1.0 coupon evidence lacks a calibration-profile content SHA-256."
        )
    if (
        config.calibration_profile_sha256 is not None
        and config.calibration_profile_sha256 != installed_record.content_sha256
    ):
        raise EvidenceValidationError("Coupon calibration profile content is stale.")
    generator = get_generator(source_spec.generator.id, source_spec.generator.version)
    parameters = _plain(source_spec.generator.parameters)
    if not isinstance(parameters, Mapping) or not generator.supports_coupon_interface(
        config.interface_parameter, parameters
    ):
        raise EvidenceValidationError("Coupon interface is unsupported by the full-part generator.")
    version = new_project_version.strip()
    if not version or version == source_spec.project.version:
        raise EvidenceValidationError("A distinct new full-part project version is required.")
    output = Path(output_spec_path).resolve()
    if output.exists():
        raise EvidenceConflictError(f"Refusing to overwrite full-part specification: {output}")
    coupon_workspace_root = verified.generation.workspace_root.resolve()
    if workspace_root is not None and Path(workspace_root).resolve() != coupon_workspace_root:
        raise EvidenceValidationError(
            "Full-part workspace root must exactly match the verified coupon workspace root."
        )
    effective_workspace_root = coupon_workspace_root
    target_workspace = (
        effective_workspace_root / source_spec.project.id / version
    )
    if target_workspace.exists():
        raise EvidenceConflictError(
            f"Refusing an existing full-part project/version workspace: {target_workspace}"
        )
    now = _now()
    document = deepcopy(source_document)
    project = document.get("project")
    if not isinstance(project, dict):
        raise EvidenceValidationError("Source specification project must be an object.")
    project["version"] = version
    document["generation_mode"] = GenerationMode.FULL_PART.value
    document["fit_coupon"] = None
    linked_evidence: dict[str, object] = {
        "coupon_project_id": evidence.coupon_project_id,
        "coupon_project_version": evidence.coupon_project_version,
        "coupon_manifest_sha256": evidence.manifest.sha256,
        "coupon_artifact_sha256": evidence.stl.sha256,
        "coupon_result_evidence_path": verified.evidence_binding.path,
        "coupon_result_evidence_sha256": verified.evidence_binding.sha256,
        "coupon_result_evidence_size_bytes": verified.evidence_binding.size_bytes,
        "coupon_spec_sha256": evidence.specification_snapshot.sha256,
        "interface_parameter": config.interface_parameter,
        "candidate_offset_mm": config.selected_candidate_offset_mm,
        "tested_at": evidence.result.tested_at,
        "tested_by": evidence.result.tested_by,
        "printer_profile": config.printer_profile,
        "material": config.material,
        "nozzle_diameter_mm": config.nozzle_diameter_mm,
        "calibration_profile_id": config.calibration_profile_id,
        "calibration_profile_version": config.calibration_profile_version,
        "acceptance_criterion": evidence.result.acceptance_criterion,
        "measured_result": evidence.result.observed_result,
        "passed": True,
        "notes": evidence.result.notes,
    }
    if evidence.source_project_id is not None:
        linked_evidence.update(
            {
                "source_project_id": evidence.source_project_id,
                "source_project_version": evidence.source_project_version,
                "source_spec_sha256": evidence.source_spec_sha256,
            }
        )
    if config.calibration_profile_sha256 is not None:
        linked_evidence["calibration_profile_sha256"] = (
            config.calibration_profile_sha256
        )
    document["fit_coupon_evidence"] = linked_evidence
    _set_new_version_common(document, now=now)
    data = _json_bytes(document)
    try:
        load_project_spec_bytes(data, source=f"linked full-part specification {output}")
    except ValueError as exc:
        raise EvidenceValidationError(f"Linked full-part specification is invalid: {exc}") from exc
    _atomic_exclusive_create(output, data)
    return output


def record_physical_fit(
    manifest_path: str | Path,
    *,
    expected_manifest_sha256: str,
    confirmed_by: str,
    confirmed_at: str,
    interface_results: Sequence[InterfaceFitResult | Mapping[str, object]],
    notes: str,
    measured_dimensions: Sequence[MeasuredDimension | Mapping[str, object]] = (),
) -> Path:
    """Record immutable complete-part fit evidence after every protected interface passes."""

    generation = _verify_generation_manifest(
        manifest_path, expected_manifest_sha256=expected_manifest_sha256
    )
    if generation.spec.generation_mode is not GenerationMode.FULL_PART:
        raise EvidenceValidationError("Physical-fit evidence requires a full-part manifest.")
    output = generation.version_directory / PHYSICAL_FIT_FILENAME
    if output.exists():
        raise EvidenceConflictError(
            f"Physical-fit evidence already exists for this project/version: {output}"
        )
    results = tuple(
        item if isinstance(item, InterfaceFitResult) else InterfaceFitResult.from_dict(item)
        for item in interface_results
    )
    dimensions = tuple(
        item if isinstance(item, MeasuredDimension) else MeasuredDimension.from_dict(item)
        for item in measured_dimensions
    )
    generator = get_generator(
        generation.spec.generator.id, generation.spec.generator.version
    )
    parameters = _plain(generation.spec.generator.parameters)
    if not isinstance(parameters, Mapping):
        raise EvidenceIntegrityError("Full-part generator parameters must be an object.")
    required = set(generator.applicable_protected_interfaces(parameters))
    recorded = {item.interface_parameter for item in results}
    missing = sorted(required - recorded)
    unexpected = sorted(recorded - required)
    if missing:
        raise EvidenceValidationError(
            "Physical-fit evidence is missing protected interface result(s): " + ", ".join(missing)
        )
    if unexpected:
        raise EvidenceValidationError(
            "Physical-fit evidence contains non-applicable interface result(s): "
            + ", ".join(unexpected)
        )
    if not required:
        raise EvidenceValidationError("Generator declares no applicable protected interfaces.")
    if not all(item.passed for item in results):
        raise EvidenceValidationError(
            "Physical-fit confirmation requires every protected interface result to pass."
        )
    now = _now()
    confirmation_time = _parse_time(confirmed_at, "confirmed_at")
    if confirmation_time < _creation_time_floor(generation):
        raise EvidenceValidationError(
            "confirmed_at cannot predate the full-part manifest or artifacts."
        )
    if confirmation_time > _parse_time(now, "record creation time"):
        raise EvidenceValidationError("confirmed_at cannot be later than the evidence recording time.")
    if generation.scad_binding is None:
        raise EvidenceIntegrityError("Full-part manifest has no verified OpenSCAD source.")
    evidence = PhysicalFitEvidence(
        project_id=generation.spec.project.id,
        project_version=generation.spec.project.version,
        generator=GeneratorBinding(
            generation.spec.generator.id, generation.spec.generator.version
        ),
        manifest=generation.manifest_binding,
        stl=generation.stl_binding,
        scad=generation.scad_binding,
        specification_snapshot=generation.specification_binding,
        confirmed_by=confirmed_by,
        confirmed_at=confirmed_at,
        interface_results=results,
        measured_dimensions=dimensions,
        notes=notes,
        created_at=now,
    )
    _atomic_exclusive_create(
        output,
        _validated_evidence_bytes(
            evidence.to_dict(), "physical-fit-evidence-v1.schema.json"
        ),
    )
    return output


def verify_physical_fit(
    evidence_path: str | Path,
    *,
    expected_evidence_sha256: str | None = None,
) -> VerifiedPhysicalFit:
    """Reverify physical-fit evidence against the exact full-part artifacts."""

    resolved, evidence_bytes = _read_once(Path(evidence_path), "physical-fit evidence")
    if expected_evidence_sha256 is not None:
        expected = _require_digest(
            expected_evidence_sha256, "Expected physical-fit evidence SHA-256"
        )
        if sha256_bytes(evidence_bytes) != expected:
            raise EvidenceIntegrityError(
                "Physical-fit evidence SHA-256 does not match the owner-supplied expected digest."
            )
    evidence = parse_physical_fit_bytes(
        evidence_bytes, source=f"physical-fit evidence {resolved}"
    )
    version_directory = resolved.parent
    if (
        resolved.name != PHYSICAL_FIT_FILENAME
        or version_directory.name != evidence.project_version
        or version_directory.parent.name != evidence.project_id
    ):
        raise EvidenceIntegrityError("Physical-fit evidence path does not match full-part identity.")
    workspace_root = version_directory.parent.parent.resolve()
    generation = _verify_generation_manifest(
        workspace_root / evidence.manifest.path,
        expected_manifest_sha256=evidence.manifest.sha256,
    )
    _assert_file_binding(generation.manifest_binding, evidence.manifest, "Manifest")
    _assert_file_binding(generation.stl_binding, evidence.stl, "Full-part STL")
    _assert_file_binding(generation.specification_binding, evidence.specification_snapshot, "Specification")
    if generation.scad_binding is None:
        raise EvidenceIntegrityError("Full-part OpenSCAD source is missing.")
    _assert_file_binding(generation.scad_binding, evidence.scad, "Full-part OpenSCAD source")
    spec = generation.spec
    if (
        spec.generation_mode is not GenerationMode.FULL_PART
        or spec.project.id != evidence.project_id
        or spec.project.version != evidence.project_version
        or spec.generator.id != evidence.generator.generator_id
        or spec.generator.version != evidence.generator.generator_version
    ):
        raise EvidenceIntegrityError("Physical-fit identity/generator does not match the full part.")
    generator = get_generator(spec.generator.id, spec.generator.version)
    parameters = _plain(spec.generator.parameters)
    if not isinstance(parameters, Mapping):
        raise EvidenceIntegrityError("Full-part generator parameters must be an object.")
    required = set(generator.applicable_protected_interfaces(parameters))
    recorded = {item.interface_parameter for item in evidence.interface_results}
    if required != recorded or not all(item.passed for item in evidence.interface_results):
        raise EvidenceIntegrityError(
            "Physical-fit evidence does not contain passing results for every protected interface."
        )
    if _parse_time(evidence.confirmed_at, "confirmed_at") < _creation_time_floor(generation):
        raise EvidenceIntegrityError("Physical-fit confirmation predates full-part generation.")
    if _parse_time(evidence.created_at, "created_at") < _parse_time(
        evidence.confirmed_at, "confirmed_at"
    ):
        raise EvidenceIntegrityError("Physical-fit evidence was created before confirmation.")
    binding = _binding(resolved, evidence_bytes, root=workspace_root)
    return VerifiedPhysicalFit(resolved, binding, evidence, generation)


def _status_from_generation(
    generation: VerifiedGeneration,
    *,
    coupon_evidence_state: str,
    physical_evidence_state: str,
    highest_state: WorkflowState,
    evidence_errors: Sequence[str] = (),
) -> dict[str, object]:
    checks = generation.manifest_document.get("checks")
    openscad = checks.get("openscad", {}) if isinstance(checks, Mapping) else {}
    mesh = checks.get("mesh", {}) if isinstance(checks, Mapping) else {}
    return {
        "specification_valid": True,
        "base_artifact_integrity_valid": True,
        "project_id": generation.spec.project.id,
        "project_version": generation.spec.project.version,
        "generator": {
            "id": generation.spec.generator.id,
            "version": generation.spec.generator.version,
        },
        "artifact_hashes": {
            "manifest": generation.manifest_binding.to_dict(),
            "specification_snapshot": generation.specification_binding.to_dict(),
            "scad": generation.scad_binding.to_dict() if generation.scad_binding else None,
            "stl": generation.stl_binding.to_dict(),
        },
        "openscad_passed": isinstance(openscad, Mapping) and openscad.get("returncode") == 0,
        "mesh_passed": isinstance(mesh, Mapping) and mesh.get("passed") is True,
        "dimensions_reviewed": (
            isinstance(mesh, Mapping)
            and mesh.get("passed") is True
            and mesh.get("expected_extents_mm") is not None
            and mesh.get("bounds_delta_mm") is not None
        ),
        "coupon_evidence_state": coupon_evidence_state,
        "physical_fit_evidence_state": physical_evidence_state,
        "highest_defensible_workflow_state": highest_state.value,
        "unresolved_assumptions": list(generation.spec.unresolved_assumptions),
        "physical_fit_claim_allowed": highest_state is WorkflowState.PHYSICAL_FIT_CONFIRMED,
        "evidence_errors": list(evidence_errors),
    }


def _invalid_project_status(
    directory: Path,
    *,
    error: str,
    coupon_evidence_state: str,
    physical_evidence_state: str,
) -> dict[str, object]:
    """Return a conservative diagnostic when the base artifact chain is broken."""

    spec_path = directory / "spec.snapshot.json"
    specification_valid = False
    project_id = directory.parent.name
    project_version = directory.name
    generator: dict[str, str] = {"id": "unknown", "version": "unknown"}
    unresolved: list[str] = []
    artifact_hashes: dict[str, object] = {}
    if spec_path.is_file():
        try:
            resolved_spec, spec_bytes = _read_once(spec_path, "specification snapshot")
            artifact_hashes["specification_snapshot"] = {
                "path": resolved_spec.name,
                "sha256": sha256_bytes(spec_bytes),
                "size_bytes": len(spec_bytes),
            }
            spec = load_project_spec_bytes(
                spec_bytes, source=f"diagnostic specification {resolved_spec}"
            )
            specification_valid = True
            project_id = spec.project.id
            project_version = spec.project.version
            generator = {"id": spec.generator.id, "version": spec.generator.version}
            unresolved = list(spec.unresolved_assumptions)
        except (OSError, ValueError):
            specification_valid = False
    for label, pattern in (("scad", "*.scad"), ("stl", "*.stl")):
        matches = tuple(directory.glob(pattern))
        if len(matches) == 1 and matches[0].is_file():
            try:
                resolved, data = _read_once(matches[0], label)
                artifact_hashes[label] = {
                    "path": resolved.name,
                    "sha256": sha256_bytes(data),
                    "size_bytes": len(data),
                }
            except EvidenceIntegrityError:
                pass
    manifest = directory / MANIFEST_FILENAME
    if manifest.is_file():
        try:
            resolved, data = _read_once(manifest, "artifact manifest")
            artifact_hashes["manifest"] = {
                "path": resolved.name,
                "sha256": sha256_bytes(data),
                "size_bytes": len(data),
            }
        except EvidenceIntegrityError:
            pass
    return {
        "specification_valid": specification_valid,
        "base_artifact_integrity_valid": False,
        "project_id": project_id,
        "project_version": project_version,
        "generator": generator,
        "artifact_hashes": artifact_hashes,
        "openscad_passed": False,
        "mesh_passed": False,
        "dimensions_reviewed": False,
        "coupon_evidence_state": coupon_evidence_state,
        "physical_fit_evidence_state": physical_evidence_state,
        "highest_defensible_workflow_state": WorkflowState.DRAFT.value,
        "unresolved_assumptions": unresolved,
        "physical_fit_claim_allowed": False,
        "evidence_errors": [error],
    }


def inspect_project_status(
    project_version_directory: str | Path,
    *,
    expected_fit_evidence_sha256: str | None = None,
    expected_physical_evidence_sha256: str | None = None,
) -> dict[str, object]:
    """Reverify a project/version and report only its highest defensible state."""

    directory = Path(project_version_directory).resolve()
    manifest_path = directory / MANIFEST_FILENAME
    fit_path = directory / FIT_RESULT_FILENAME
    physical_path = directory / PHYSICAL_FIT_FILENAME
    errors: list[str] = []
    physical_state = "not_recorded"
    coupon_state = "not_recorded"
    if physical_path.exists() and expected_physical_evidence_sha256 is not None:
        try:
            verified_physical = verify_physical_fit(
                physical_path,
                expected_evidence_sha256=expected_physical_evidence_sha256,
            )
            linked_coupon_state, linked_errors = _linked_coupon_status(
                verified_physical.generation,
                expected_fit_evidence_sha256=expected_fit_evidence_sha256,
            )
            return _status_from_generation(
                verified_physical.generation,
                coupon_evidence_state=linked_coupon_state,
                physical_evidence_state="confirmed",
                highest_state=WorkflowState.PHYSICAL_FIT_CONFIRMED,
                evidence_errors=linked_errors,
            )
        except EvidenceValidationError as exc:
            errors.append(str(exc))
            physical_state = "invalid"
    elif physical_path.exists():
        physical_state = "unanchored"
        errors.append(
            "Physical-fit evidence exists but no owner-supplied expected SHA-256 was provided."
        )
    elif expected_physical_evidence_sha256 is not None:
        physical_state = "invalid"
        errors.append("Expected physical-fit evidence SHA-256 was supplied, but no evidence file exists.")
    if fit_path.exists() and expected_fit_evidence_sha256 is not None:
        try:
            verified_coupon = verify_fit_coupon_result(
                fit_path,
                expected_evidence_sha256=expected_fit_evidence_sha256,
            )
            return _status_from_generation(
                verified_coupon.generation,
                coupon_evidence_state=(
                    "passed" if verified_coupon.evidence.result.passed else "failed"
                ),
                physical_evidence_state="not_applicable",
                highest_state=verified_coupon.evidence.defensible_workflow_state,
            )
        except EvidenceValidationError as exc:
            errors.append(str(exc))
            coupon_state = "invalid"
    elif fit_path.exists():
        coupon_state = "unanchored"
        errors.append(
            "Fit-result evidence exists but no owner-supplied expected SHA-256 was provided."
        )
    try:
        generation = _verify_generation_manifest(
            manifest_path, expected_manifest_sha256=None
        )
    except EvidenceValidationError as exc:
        return _invalid_project_status(
            directory,
            error=str(exc),
            coupon_evidence_state=coupon_state,
            physical_evidence_state=physical_state,
        )
    if (
        expected_fit_evidence_sha256 is not None
        and not fit_path.exists()
        and generation.spec.generation_mode is GenerationMode.FIT_COUPON
    ):
        coupon_state = "invalid"
        errors.append(
            "Expected fit-result evidence SHA-256 was supplied, but no coupon evidence file exists."
        )
    base_state = WorkflowState(str(generation.manifest_document["workflow_state"]))
    linked_coupon_state, linked_errors = _linked_coupon_status(
        generation,
        expected_fit_evidence_sha256=expected_fit_evidence_sha256,
    )
    errors.extend(linked_errors)
    return _status_from_generation(
        generation,
        coupon_evidence_state=(
            coupon_state if fit_path.exists() or coupon_state == "invalid" else linked_coupon_state
        ),
        physical_evidence_state=physical_state,
        highest_state=base_state,
        evidence_errors=errors,
    )


def _linked_coupon_status(
    generation: VerifiedGeneration,
    *,
    expected_fit_evidence_sha256: str | None,
) -> tuple[str, tuple[str, ...]]:
    """Reverify an immutable coupon link embedded in a full-part snapshot."""

    link = generation.spec.fit_coupon_evidence
    if link is None:
        return (
            "not_applicable"
            if generation.spec.generation_mode is GenerationMode.FULL_PART
            else "not_recorded"
        ), ()
    if not link.coupon_result_evidence_path:
        return "legacy_embedded", ()
    pinned_digest = link.coupon_result_evidence_sha256
    if pinned_digest is None:
        return "invalid", ("Linked fit-result evidence has no pinned SHA-256.",)
    if (
        expected_fit_evidence_sha256 is not None
        and expected_fit_evidence_sha256 != pinned_digest
    ):
        return "invalid", (
            "Owner-supplied fit-result evidence SHA-256 does not match the linked specification.",
        )
    try:
        verified = verify_fit_coupon_result(
            generation.workspace_root / link.coupon_result_evidence_path,
            expected_evidence_sha256=pinned_digest,
        )
        mismatches = []
        expected = {
            "result path": (
                verified.evidence_binding.path,
                link.coupon_result_evidence_path,
            ),
            "result SHA-256": (
                verified.evidence_binding.sha256,
                link.coupon_result_evidence_sha256,
            ),
            "result size": (
                verified.evidence_binding.size_bytes,
                link.coupon_result_evidence_size_bytes,
            ),
            "coupon manifest SHA-256": (
                verified.evidence.manifest.sha256,
                link.coupon_manifest_sha256,
            ),
            "coupon STL SHA-256": (
                verified.evidence.stl.sha256,
                link.coupon_artifact_sha256,
            ),
            "coupon specification SHA-256": (
                verified.evidence.specification_snapshot.sha256,
                link.coupon_spec_sha256,
            ),
            "coupon project ID": (
                verified.evidence.coupon_project_id,
                link.coupon_project_id,
            ),
            "coupon project version": (
                verified.evidence.coupon_project_version,
                link.coupon_project_version,
            ),
            "interface": (
                verified.evidence.configuration.interface_parameter,
                link.interface_parameter,
            ),
            "selected offset": (
                verified.evidence.configuration.selected_candidate_offset_mm,
                link.candidate_offset_mm,
            ),
            "tester": (verified.evidence.result.tested_by, link.tested_by),
            "test time": (verified.evidence.result.tested_at, link.tested_at),
            "printer profile": (
                verified.evidence.configuration.printer_profile,
                link.printer_profile,
            ),
            "material": (
                verified.evidence.configuration.material.lower(),
                link.material.lower(),
            ),
            "nozzle diameter": (
                verified.evidence.configuration.nozzle_diameter_mm,
                link.nozzle_diameter_mm,
            ),
            "calibration profile ID": (
                verified.evidence.configuration.calibration_profile_id,
                link.calibration_profile_id,
            ),
            "calibration profile version": (
                verified.evidence.configuration.calibration_profile_version,
                link.calibration_profile_version,
            ),
            "calibration profile SHA-256": (
                verified.evidence.configuration.calibration_profile_sha256,
                link.calibration_profile_sha256,
            ),
            "acceptance criterion": (
                verified.evidence.result.acceptance_criterion,
                link.acceptance_criterion,
            ),
            "observed result": (
                verified.evidence.result.observed_result,
                link.measured_result,
            ),
            "passed result": (verified.evidence.result.passed, link.passed),
            "notes": (verified.evidence.result.notes, link.notes),
            "source project ID": (
                verified.evidence.source_project_id,
                link.source_project_id,
            ),
            "source project version": (
                verified.evidence.source_project_version,
                link.source_project_version,
            ),
            "source specification SHA-256": (
                verified.evidence.source_spec_sha256,
                link.source_spec_sha256,
            ),
        }
        mismatches = [name for name, values in expected.items() if values[0] != values[1]]
        if mismatches or not verified.evidence.result.passed:
            raise EvidenceIntegrityError(
                "Linked coupon evidence mismatch: " + ", ".join(mismatches or ["failed result"])
            )
        return "linked_passed", ()
    except (OSError, ValueError) as exc:
        return "invalid", (str(exc),)
