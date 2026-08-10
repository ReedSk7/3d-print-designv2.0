from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

import pytest

from core.validation.specification import SpecificationError
from core.workflow.pipeline import generate_project
from core.workflow.states import WorkflowState


def is_binary_stl(path: Path) -> bool:
    data = path.read_bytes()
    if len(data) < 84:
        return False
    triangle_count = struct.unpack("<I", data[80:84])[0]
    return len(data) == 84 + triangle_count * 50


@pytest.mark.integration
@pytest.mark.parametrize(
    ("spec_name", "expected_bounds"),
    [
        ("bushing_example.json", (30.0, 30.0, 25.0)),
        ("round_adapter_example.json", (80.0, 80.0, 60.0)),
        ("flange_plate_example.json", (100.0, 80.0, 5.0)),
    ],
    ids=["bushing", "round_adapter", "flange_plate"],
)
def test_generator_vertical_slice(
    examples_dir: Path,
    tmp_path: Path,
    spec_name: str,
    expected_bounds: tuple[float, float, float],
) -> None:
    result = generate_project(examples_dir / spec_name, workspace_root=tmp_path)

    assert result.reached_state is WorkflowState.FULL_PART_EXPORTED
    assert result.scad_path.is_file()
    assert result.stl_path.is_file()
    assert result.manifest_path.is_file()
    assert is_binary_stl(result.stl_path)
    assert result.mesh_report.passed
    assert tuple(float(value) for value in result.mesh_report.extents_mm) == pytest.approx(
        expected_bounds, abs=0.05
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["workflow_state"] == "full_part_exported"
    assert manifest["physical_fit_confirmed"] is False
    assert manifest["checks"]["mesh"]["passed"] is True
    transitions = [item["to_state"] for item in manifest["checks"]["workflow_history"]]
    assert transitions == [
        "measurement_contract_complete",
        "generated",
        "scad_compiled",
        "mesh_valid",
        "dimensions_reviewed",
        "full_part_exported",
    ]


def test_bushing_fit_coupon_vertical_slice(examples_dir: Path, tmp_path: Path) -> None:
    document = json.loads(
        (examples_dir / "bushing_example.json").read_text(encoding="utf-8")
    )
    document["project"]["id"] = "bushing_coupon_test"
    document["project"]["name"] = "Bushing Coupon Test"
    document["generation_mode"] = "fit_coupon"
    document["fit_coupon"] = {
        "interface_parameter": "inside_diameter",
        "candidate_offsets": [-0.15, 0, 0.15],
        "notes": "Computational integration fixture; print result is not known.",
    }
    spec_path = tmp_path / "bushing_coupon.json"
    spec_path.write_text(json.dumps(document, indent=2), encoding="utf-8")

    result = generate_project(spec_path, workspace_root=tmp_path / "workspace")

    assert result.reached_state is WorkflowState.FIT_COUPON_GENERATED
    assert result.mesh_report.passed
    assert is_binary_stl(result.stl_path)
    assert tuple(float(value) for value in result.mesh_report.extents_mm) == pytest.approx(
        (72.45, 24.15, 2.0), abs=0.05
    )
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["generation_mode"] == "fit_coupon"
    assert manifest["workflow_state"] == "fit_coupon_generated"
    assert manifest["physical_fit_confirmed"] is False


def test_full_part_resolves_and_applies_real_coupon_provenance(
    examples_dir: Path, tmp_path: Path
) -> None:
    workspace = tmp_path / "workspace"
    coupon_document = json.loads(
        (examples_dir / "bushing_example.json").read_text(encoding="utf-8")
    )
    coupon_document["project"]["id"] = "bushing_coupon_link_test"
    coupon_document["project"]["name"] = "Bushing Coupon Link Test"
    coupon_document["generation_mode"] = "fit_coupon"
    coupon_document["fit_coupon"] = {
        "interface_parameter": "inside_diameter",
        "candidate_offsets": [-0.15, 0, 0.15],
        "notes": "Synthetic integration fixture; no physical test is claimed.",
    }
    coupon_spec_path = tmp_path / "linked_coupon.json"
    coupon_spec_path.write_text(
        json.dumps(coupon_document, indent=2), encoding="utf-8"
    )
    coupon_result = generate_project(coupon_spec_path, workspace_root=workspace)
    coupon_manifest = json.loads(
        coupon_result.manifest_path.read_text(encoding="utf-8")
    )
    coupon_stl = next(
        artifact
        for artifact in coupon_manifest["artifacts"]
        if artifact["role"] == "fit_coupon_stl"
    )

    full_document = json.loads(
        (examples_dir / "bushing_example.json").read_text(encoding="utf-8")
    )
    full_document["project"]["id"] = "bushing_linked_full_test"
    full_document["project"]["name"] = "Bushing Linked Full Test"
    full_document["fit_coupon_evidence"] = {
        "coupon_project_id": "bushing_coupon_link_test",
        "coupon_project_version": "v01",
        "coupon_artifact_sha256": coupon_stl["sha256"],
        "interface_parameter": "inside_diameter",
        "candidate_offset_mm": 0.15,
        "tested_at": "2026-08-10T12:00:00Z",
        "tested_by": "synthetic integration fixture",
        "printer_profile": "generic_fdm",
        "material": "PETG",
        "nozzle_diameter_mm": 0.4,
        "calibration_profile_id": "neutral_unverified_starter",
        "calibration_profile_version": "1.0.0",
        "acceptance_criterion": "Synthetic candidate selected to test provenance wiring.",
        "measured_result": "Synthetic pass value; not a real print or fit result.",
        "passed": True,
        "notes": "Test data only; this does not establish physical fit.",
    }
    full_spec_path = tmp_path / "linked_full.json"
    full_spec_path.write_text(json.dumps(full_document, indent=2), encoding="utf-8")

    full_result = generate_project(full_spec_path, workspace_root=workspace)
    full_manifest = json.loads(full_result.manifest_path.read_text(encoding="utf-8"))

    assert full_result.reached_state is WorkflowState.FULL_PART_EXPORTED
    assert full_manifest["checks"]["normalized_parameters_mm"][
        "inside_diameter"
    ] == "20.15"
    assert full_manifest["checks"]["accepted_fit_coupon"][
        "coupon_artifact_sha256"
    ] == coupon_stl["sha256"]
    assert full_manifest["physical_fit_confirmed"] is False

    cross_unit_document = json.loads(json.dumps(full_document))
    cross_unit_document["project"]["id"] = "bushing_cross_unit_link_test"
    cross_unit_document["project"]["name"] = "Bushing Cross-Unit Link Test"
    cross_unit_document["input_units"] = "inch"
    cross_unit_document["nozzle_diameter"] = 0.015748031496062992
    cross_unit_spec_path = tmp_path / "cross_unit_link.json"
    cross_unit_spec_path.write_text(
        json.dumps(cross_unit_document, indent=2), encoding="utf-8"
    )
    with pytest.raises(SpecificationError, match="input units"):
        generate_project(cross_unit_spec_path, workspace_root=workspace)


def test_split_bushing_bounds_and_manifest_integrity(
    repo_root: Path, examples_dir: Path, tmp_path: Path
) -> None:
    document = json.loads(
        (examples_dir / "bushing_example.json").read_text(encoding="utf-8")
    )
    document["project"]["id"] = "split_bushing_test"
    document["project"]["name"] = "Split Bushing Test"
    document["generator"]["parameters"].update(  # type: ignore[union-attr]
        {"split": True, "split_width": 20}
    )
    spec_path = tmp_path / "split_bushing.json"
    spec_path.write_text(json.dumps(document, indent=2), encoding="utf-8")
    result = generate_project(spec_path, workspace_root=tmp_path / "workspace")

    assert result.reached_state is WorkflowState.FULL_PART_EXPORTED
    assert tuple(float(value) for value in result.mesh_report.extents_mm) == pytest.approx(
        (26.1747, 30.0, 25.0), abs=0.05
    )

    verify_command = [
        sys.executable,
        str(repo_root / "scripts" / "verify_mesh.py"),
        "--manifest",
        str(result.manifest_path),
    ]
    verified = subprocess.run(
        verify_command, cwd=repo_root, text=True, capture_output=True, check=False
    )
    assert verified.returncode == 0, verified.stdout + verified.stderr

    damaged = bytearray(result.stl_path.read_bytes())
    damaged[0] ^= 1
    result.stl_path.write_bytes(damaged)
    rejected = subprocess.run(
        verify_command, cwd=repo_root, text=True, capture_output=True, check=False
    )
    assert rejected.returncode == 1
    assert "SHA-256 does not match" in rejected.stdout
