from pathlib import Path

import pytest

from core.models.artifacts import (
    ArtifactManifest,
    ArtifactRole,
    artifact_record_from_path,
    read_and_verify_artifact,
)


def test_artifact_manifest_hashes_files_and_stays_physically_unconfirmed(tmp_path: Path) -> None:
    artifact = tmp_path / "part.scad"
    artifact.write_text("cube([1, 1, 1]);\n", encoding="utf-8")
    record = artifact_record_from_path(
        artifact,
        role=ArtifactRole.SCAD_SOURCE,
        workspace_root=tmp_path,
        created_at="2026-08-10T00:00:00Z",
    )
    manifest = ArtifactManifest(
        project_id="manifest_test",
        project_version="v01",
        generator_id="bushing",
        generator_version="1.0.0",
        generation_mode="full_part",
        workflow_state="full_part_exported",
        created_at="2026-08-10T00:00:00Z",
        artifacts=(record,),
        physical_fit_confirmed=False,
    )
    document = manifest.to_dict()
    assert document["artifacts"][0]["sha256"] == record.sha256
    assert document["physical_fit_confirmed"] is False


def test_manifest_rejects_premature_physical_confirmation() -> None:
    with pytest.raises(ValueError, match="only at workflow state"):
        ArtifactManifest(
            project_id="manifest_test",
            project_version="v01",
            generator_id="bushing",
            generator_version="1.0.0",
            generation_mode="full_part",
            workflow_state="full_part_exported",
            created_at="2026-08-10T00:00:00Z",
            artifacts=(),
            physical_fit_confirmed=True,
        )


def test_verified_artifact_bytes_remain_bound_after_path_changes(tmp_path: Path) -> None:
    artifact = tmp_path / "spec.snapshot.json"
    original = b'{"schema_version":"1.0"}\n'
    artifact.write_bytes(original)
    record = artifact_record_from_path(
        artifact,
        role=ArtifactRole.SPEC_SNAPSHOT,
        workspace_root=tmp_path,
        created_at="2026-08-10T00:00:00Z",
    )

    resolved, verified_bytes = read_and_verify_artifact(
        record, workspace_root=tmp_path
    )
    resolved.write_bytes(b'{"schema_version":"changed"}\n')

    assert verified_bytes == original
