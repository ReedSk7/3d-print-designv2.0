from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.workflow.pipeline import generate_project
from core.workflow.states import WorkflowState


@pytest.mark.integration
@pytest.mark.parametrize(
    ("spec_name", "source_marker"),
    [
        ("bushing_v110_coupon_example.json", "post_height"),
        ("round_adapter_v110_coupon_example.json", "coupon_diameters"),
        ("flange_plate_v110_coupon_example.json", "coupon_widths"),
    ],
    ids=["bushing-outside-shaft", "adapter-mounting-hole", "flange-rectangle"],
)
def test_v110_numbered_fit_coupon_vertical_slices(
    examples_dir: Path,
    tmp_path: Path,
    spec_name: str,
    source_marker: str,
) -> None:
    result = generate_project(examples_dir / spec_name, workspace_root=tmp_path)

    assert result.reached_state is WorkflowState.FIT_COUPON_GENERATED
    assert result.mesh_report.passed
    assert result.scad_path.is_file()
    assert result.stl_path.is_file()
    source = result.scad_path.read_text(encoding="utf-8")
    assert "generator:" in source and "1.1.0" in source
    assert source_marker in source
    assert 'text(str(index + 1)' in source

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["generator"]["version"] == "1.1.0"
    assert manifest["workflow_state"] == "fit_coupon_generated"
    assert manifest["physical_fit_confirmed"] is False
    candidate_map = manifest["checks"]["normalized_parameters_mm"][
        "coupon_candidate_map"
    ]
    assert [item["index"] for item in candidate_map] == list(
        range(1, len(candidate_map) + 1)
    )
    assert [item["label"] for item in candidate_map] == [
        str(index) for index in range(1, len(candidate_map) + 1)
    ]


@pytest.mark.integration
def test_v100_examples_remain_available_after_v110_registration(
    examples_dir: Path, tmp_path: Path
) -> None:
    for spec_name in (
        "bushing_example.json",
        "round_adapter_example.json",
        "flange_plate_example.json",
    ):
        result = generate_project(
            examples_dir / spec_name, workspace_root=tmp_path / spec_name
        )
        assert result.reached_state is WorkflowState.FULL_PART_EXPORTED
        assert "1.0.0" in result.scad_path.read_text(encoding="utf-8")
