import pytest

from core.workflow.states import (
    IllegalWorkflowTransition,
    WorkflowEvidenceRequired,
    WorkflowState,
    WorkflowStateMachine,
)


def test_full_part_legal_state_path() -> None:
    machine = WorkflowStateMachine()
    for state in (
        WorkflowState.MEASUREMENT_CONTRACT_COMPLETE,
        WorkflowState.GENERATED,
        WorkflowState.SCAD_COMPILED,
        WorkflowState.MESH_VALID,
        WorkflowState.DIMENSIONS_REVIEWED,
        WorkflowState.FULL_PART_EXPORTED,
    ):
        machine.advance(state, occurred_at="2026-08-10T00:00:00Z", evidence={"test": True})
    assert machine.state is WorkflowState.FULL_PART_EXPORTED
    assert not machine.is_physically_verified


def test_fit_coupon_manual_pass_requires_evidence() -> None:
    machine = WorkflowStateMachine(WorkflowState.FIT_COUPON_GENERATED)
    with pytest.raises(WorkflowEvidenceRequired):
        machine.advance(
            WorkflowState.FIT_COUPON_PASSED,
            occurred_at="2026-08-10T00:00:00Z",
        )

    with pytest.raises(WorkflowEvidenceRequired, match="evidence is missing"):
        machine.advance(
            WorkflowState.FIT_COUPON_PASSED,
            occurred_at="2026-08-10T00:00:00Z",
            evidence={"anything": True},
        )


def test_fit_coupon_pass_requires_structured_positive_result() -> None:
    machine = WorkflowStateMachine(WorkflowState.FIT_COUPON_GENERATED)
    evidence = {
        "coupon_project_id": "bushing_coupon_test",
        "coupon_project_version": "v01",
        "coupon_manifest_sha256": "b" * 64,
        "coupon_artifact_sha256": "a" * 64,
        "interface_parameter": "inside_diameter",
        "tested_at": "2026-08-10T12:00:00Z",
        "tested_by": "test owner",
        "printer_profile": "generic_fdm",
        "material": "PETG",
        "nozzle_diameter_mm": "0.4",
        "calibration_profile_id": "coupon_profile_v1",
        "calibration_profile_version": "1.0.0",
        "candidate_offset_mm": "0.1",
        "acceptance_criterion": "Printed gauge enters without force and has no visible play.",
        "measured_result": "Candidate +0.1 mm met the stated criterion.",
        "passed": True,
        "notes": "Synthetic state-machine fixture only.",
    }
    transition = machine.advance(
        WorkflowState.FIT_COUPON_PASSED,
        occurred_at="2026-08-10T00:00:00Z",
        evidence=evidence,
    )
    assert transition.to_state is WorkflowState.FIT_COUPON_PASSED
    assert not machine.can_transition(WorkflowState.FULL_PART_EXPORTED)


def test_illegal_state_skip_is_rejected() -> None:
    machine = WorkflowStateMachine()
    with pytest.raises(IllegalWorkflowTransition):
        machine.advance(
            WorkflowState.MESH_VALID,
            occurred_at="2026-08-10T00:00:00Z",
            evidence={"test": True},
        )


def test_only_final_state_is_physically_verified() -> None:
    machine = WorkflowStateMachine(WorkflowState.FULL_PART_EXPORTED)
    machine.advance(
        WorkflowState.PHYSICAL_FIT_CONFIRMED,
        occurred_at="2026-08-10T00:00:00Z",
        evidence={
            "confirmed_by": "test owner",
            "confirmation_method": "installed fit check",
            "notes": "Synthetic state-machine evidence only.",
        },
    )
    assert machine.is_physically_verified
