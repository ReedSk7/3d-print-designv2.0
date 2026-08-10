"""Machine-readable artifact records and manifest helpers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence

from core.workflow.states import WorkflowState


class ArtifactRole(str, Enum):
    SPEC_SNAPSHOT = "spec_snapshot"
    SCAD_SOURCE = "scad_source"
    STL_MESH = "stl_mesh"
    FIT_COUPON_SCAD = "fit_coupon_scad"
    FIT_COUPON_STL = "fit_coupon_stl"
    ARTIFACT_MANIFEST = "artifact_manifest"


class ArtifactIntegrityError(ValueError):
    pass


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    role: ArtifactRole
    path: str
    sha256: str
    size_bytes: int
    created_at: str
    media_type: str | None = None

    def __post_init__(self) -> None:
        relative = Path(self.path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Artifact paths must be relative and cannot traverse a parent directory.")
        if len(self.sha256) != 64 or any(character not in "0123456789abcdef" for character in self.sha256):
            raise ValueError("Artifact sha256 must be a lowercase 64-character hexadecimal digest.")
        if self.size_bytes < 0:
            raise ValueError("Artifact size_bytes cannot be negative.")
        object.__setattr__(self, "role", ArtifactRole(self.role))
        object.__setattr__(self, "path", relative.as_posix())

    @classmethod
    def from_dict(cls, document: Mapping[str, object]) -> "ArtifactRecord":
        return cls(
            role=ArtifactRole(str(document["role"])),
            path=str(document["path"]),
            sha256=str(document["sha256"]),
            size_bytes=int(document["size_bytes"]),
            created_at=str(document["created_at"]),
            media_type=str(document["media_type"]) if document.get("media_type") is not None else None,
        )

    def to_dict(self) -> dict[str, object]:
        document: dict[str, object] = {
            "role": self.role.value,
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at,
        }
        if self.media_type is not None:
            document["media_type"] = self.media_type
        return document


def artifact_record_from_path(
    path: Path,
    *,
    role: ArtifactRole | str,
    workspace_root: Path,
    created_at: str,
    media_type: str | None = None,
) -> ArtifactRecord:
    """Build a hashed record for an existing artifact under ``workspace_root``."""

    resolved_path = path.resolve(strict=True)
    resolved_root = workspace_root.resolve(strict=True)
    try:
        relative_path = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Artifact is outside workspace root: {resolved_path}") from exc
    if not resolved_path.is_file():
        raise ValueError(f"Artifact is not a file: {resolved_path}")
    return ArtifactRecord(
        role=ArtifactRole(role),
        path=relative_path.as_posix(),
        sha256=sha256_file(resolved_path),
        size_bytes=resolved_path.stat().st_size,
        created_at=created_at,
        media_type=media_type,
    )


def resolve_and_verify_artifact(
    artifact: ArtifactRecord,
    *,
    workspace_root: Path,
) -> Path:
    """Resolve one recorded artifact and verify containment, byte size, and SHA-256."""

    root = workspace_root.resolve(strict=True)
    try:
        resolved = (root / artifact.path).resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, ValueError) as exc:
        raise ArtifactIntegrityError(
            f"Artifact is missing or outside the workspace root: {artifact.path}"
        ) from exc
    if not resolved.is_file():
        raise ArtifactIntegrityError(f"Artifact is not a file: {artifact.path}")
    if resolved.stat().st_size != artifact.size_bytes:
        raise ArtifactIntegrityError(
            f"Artifact size does not match the manifest: {artifact.path}"
        )
    if sha256_file(resolved) != artifact.sha256:
        raise ArtifactIntegrityError(
            f"Artifact SHA-256 does not match the manifest: {artifact.path}"
        )
    return resolved


def _json_value(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class ArtifactManifest:
    project_id: str
    project_version: str
    generator_id: str
    generator_version: str
    generation_mode: str
    workflow_state: str
    created_at: str
    artifacts: tuple[ArtifactRecord, ...]
    checks: Mapping[str, object] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    unresolved_assumptions: tuple[str, ...] = ()
    physical_fit_confirmed: bool = False
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        mode = getattr(self.generation_mode, "value", self.generation_mode)
        state = WorkflowState(self.workflow_state).value
        if str(mode) not in {"full_part", "fit_coupon"}:
            raise ValueError(f"Unsupported artifact generation mode: {mode!r}.")
        if self.schema_version != "1.0":
            raise ValueError(f"Unsupported artifact manifest schema version: {self.schema_version!r}.")
        object.__setattr__(self, "generation_mode", str(mode))
        object.__setattr__(self, "workflow_state", state)
        object.__setattr__(self, "artifacts", tuple(self.artifacts))
        object.__setattr__(self, "checks", MappingProxyType(dict(self.checks)))
        object.__setattr__(self, "warnings", tuple(self.warnings))
        object.__setattr__(self, "unresolved_assumptions", tuple(self.unresolved_assumptions))
        if self.physical_fit_confirmed and self.workflow_state != WorkflowState.PHYSICAL_FIT_CONFIRMED.value:
            raise ValueError(
                "physical_fit_confirmed may be true only at workflow state physical_fit_confirmed."
            )
        if self.workflow_state == WorkflowState.PHYSICAL_FIT_CONFIRMED.value and not self.physical_fit_confirmed:
            raise ValueError(
                "A physical_fit_confirmed workflow state requires physical_fit_confirmed=true."
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "project_id": self.project_id,
            "project_version": self.project_version,
            "generator": {"id": self.generator_id, "version": self.generator_version},
            "generation_mode": self.generation_mode,
            "workflow_state": self.workflow_state,
            "created_at": self.created_at,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "checks": _json_value(self.checks),
            "warnings": list(self.warnings),
            "unresolved_assumptions": list(self.unresolved_assumptions),
            "physical_fit_confirmed": self.physical_fit_confirmed,
        }
