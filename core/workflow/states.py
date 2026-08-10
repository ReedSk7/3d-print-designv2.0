"""Legal verification workflow states and transition enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Sequence

from core.units.conversion import as_decimal


class WorkflowState(str, Enum):
    DRAFT = "draft"
    MEASUREMENT_CONTRACT_COMPLETE = "measurement_contract_complete"
    GENERATED = "generated"
    SCAD_COMPILED = "scad_compiled"
    MESH_VALID = "mesh_valid"
    DIMENSIONS_REVIEWED = "dimensions_reviewed"
    FIT_COUPON_GENERATED = "fit_coupon_generated"
    FIT_COUPON_PASSED = "fit_coupon_passed"
    FULL_PART_EXPORTED = "full_part_exported"
    PHYSICAL_FIT_CONFIRMED = "physical_fit_confirmed"


LEGAL_TRANSITIONS: Mapping[WorkflowState, frozenset[WorkflowState]] = MappingProxyType(
    {
        WorkflowState.DRAFT: frozenset({WorkflowState.MEASUREMENT_CONTRACT_COMPLETE}),
        WorkflowState.MEASUREMENT_CONTRACT_COMPLETE: frozenset({WorkflowState.GENERATED}),
        WorkflowState.GENERATED: frozenset({WorkflowState.SCAD_COMPILED}),
        WorkflowState.SCAD_COMPILED: frozenset({WorkflowState.MESH_VALID}),
        WorkflowState.MESH_VALID: frozenset({WorkflowState.DIMENSIONS_REVIEWED}),
        WorkflowState.DIMENSIONS_REVIEWED: frozenset(
            {WorkflowState.FIT_COUPON_GENERATED, WorkflowState.FULL_PART_EXPORTED}
        ),
        WorkflowState.FIT_COUPON_GENERATED: frozenset({WorkflowState.FIT_COUPON_PASSED}),
        WorkflowState.FIT_COUPON_PASSED: frozenset(),
        WorkflowState.FULL_PART_EXPORTED: frozenset({WorkflowState.PHYSICAL_FIT_CONFIRMED}),
        WorkflowState.PHYSICAL_FIT_CONFIRMED: frozenset(),
    }
)


class IllegalWorkflowTransition(ValueError):
    def __init__(self, current: WorkflowState, requested: WorkflowState) -> None:
        self.current = current
        self.requested = requested
        allowed = ", ".join(sorted(state.value for state in LEGAL_TRANSITIONS[current])) or "none"
        super().__init__(
            f"Illegal workflow transition {current.value!r} -> {requested.value!r}; allowed: {allowed}."
        )


class WorkflowEvidenceRequired(ValueError):
    pass


class WorkflowHistoryError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class WorkflowTransition:
    from_state: WorkflowState
    to_state: WorkflowState
    occurred_at: str
    evidence: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "from_state", WorkflowState(self.from_state))
        object.__setattr__(self, "to_state", WorkflowState(self.to_state))
        object.__setattr__(self, "evidence", MappingProxyType(dict(self.evidence)))

    def to_dict(self) -> dict[str, object]:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "occurred_at": self.occurred_at,
            "evidence": dict(self.evidence),
        }


_MANUAL_EVIDENCE_STATES = frozenset(
    {WorkflowState.FIT_COUPON_PASSED, WorkflowState.PHYSICAL_FIT_CONFIRMED}
)

_FIT_COUPON_EVIDENCE_FIELDS = frozenset(
    {
        "coupon_project_id",
        "coupon_project_version",
        "coupon_artifact_sha256",
        "interface_parameter",
        "tested_by",
        "printer_profile",
        "material",
        "nozzle_diameter_mm",
        "calibration_profile_id",
        "calibration_profile_version",
        "candidate_offset_mm",
        "tested_at",
        "acceptance_criterion",
        "measured_result",
        "passed",
        "notes",
    }
)


class WorkflowStateMachine:
    """Mutable state-machine facade with immutable transition records."""

    def __init__(
        self,
        initial_state: WorkflowState | str = WorkflowState.DRAFT,
        history: Sequence[WorkflowTransition] = (),
    ) -> None:
        self._state = WorkflowState(initial_state)
        self._history: list[WorkflowTransition] = []
        for transition in history:
            if transition.from_state is not self._state:
                raise WorkflowHistoryError(
                    f"Workflow history expected from_state {self._state.value!r}, "
                    f"found {transition.from_state.value!r}."
                )
            if transition.to_state not in LEGAL_TRANSITIONS[self._state]:
                raise IllegalWorkflowTransition(self._state, transition.to_state)
            self._require_manual_evidence(transition.to_state, transition.evidence)
            self._history.append(transition)
            self._state = transition.to_state

    @property
    def state(self) -> WorkflowState:
        return self._state

    @property
    def history(self) -> tuple[WorkflowTransition, ...]:
        return tuple(self._history)

    @property
    def is_physically_verified(self) -> bool:
        return self._state is WorkflowState.PHYSICAL_FIT_CONFIRMED

    def can_transition(self, requested: WorkflowState | str) -> bool:
        return WorkflowState(requested) in LEGAL_TRANSITIONS[self._state]

    @staticmethod
    def _require_manual_evidence(
        target: WorkflowState, evidence: Mapping[str, object]
    ) -> None:
        if target in _MANUAL_EVIDENCE_STATES and not evidence:
            raise WorkflowEvidenceRequired(
                f"Transition to {target.value!r} requires recorded manual evidence."
            )
        if target is WorkflowState.FIT_COUPON_PASSED:
            missing = sorted(_FIT_COUPON_EVIDENCE_FIELDS - evidence.keys())
            if missing:
                raise WorkflowEvidenceRequired(
                    "Fit-coupon pass evidence is missing: " + ", ".join(missing)
                )
            text_fields = (
                "coupon_project_id",
                "coupon_project_version",
                "interface_parameter",
                "tested_at",
                "tested_by",
                "printer_profile",
                "material",
                "calibration_profile_id",
                "calibration_profile_version",
                "acceptance_criterion",
                "measured_result",
            )
            if any(not str(evidence[field]).strip() for field in text_fields):
                raise WorkflowEvidenceRequired(
                    "Fit-coupon pass evidence text fields cannot be empty."
                )
            digest = str(evidence["coupon_artifact_sha256"])
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise WorkflowEvidenceRequired(
                    "Fit-coupon evidence requires a lowercase SHA-256 artifact digest."
                )
            try:
                tested_at = datetime.fromisoformat(
                    str(evidence["tested_at"]).replace("Z", "+00:00")
                )
            except ValueError as exc:
                raise WorkflowEvidenceRequired(
                    "Fit-coupon tested_at must be an ISO-8601 date-time."
                ) from exc
            if tested_at.tzinfo is None:
                raise WorkflowEvidenceRequired(
                    "Fit-coupon tested_at must include a timezone."
                )
            try:
                nozzle = as_decimal(evidence["nozzle_diameter_mm"])  # type: ignore[arg-type]
                as_decimal(evidence["candidate_offset_mm"])  # type: ignore[arg-type]
            except (TypeError, ValueError) as exc:
                raise WorkflowEvidenceRequired(
                    "Fit-coupon nozzle and candidate offset must be finite millimeter values."
                ) from exc
            if nozzle <= 0:
                raise WorkflowEvidenceRequired(
                    "Fit-coupon nozzle_diameter_mm must be positive."
                )
            if evidence["passed"] is not True:
                raise WorkflowEvidenceRequired(
                    "Transition to fit_coupon_passed requires passed=true."
                )
        if target is WorkflowState.PHYSICAL_FIT_CONFIRMED:
            required = {"confirmed_by", "confirmation_method", "notes"}
            missing = sorted(required - evidence.keys())
            if missing:
                raise WorkflowEvidenceRequired(
                    "Physical-fit confirmation evidence is missing: " + ", ".join(missing)
                )
            if any(not str(evidence[field]).strip() for field in required):
                raise WorkflowEvidenceRequired(
                    "Physical-fit confirmation evidence fields cannot be empty."
                )

    def advance(
        self,
        requested: WorkflowState | str,
        *,
        occurred_at: str,
        evidence: Mapping[str, object] | None = None,
    ) -> WorkflowTransition:
        target = WorkflowState(requested)
        if not self.can_transition(target):
            raise IllegalWorkflowTransition(self._state, target)

        transition_evidence = dict(evidence or {})
        self._require_manual_evidence(target, transition_evidence)

        transition = WorkflowTransition(
            from_state=self._state,
            to_state=target,
            occurred_at=occurred_at,
            evidence=transition_evidence,
        )
        self._history.append(transition)
        self._state = target
        return transition

    transition_to = advance
    transition = advance

    def require_state(self, expected: WorkflowState | str) -> None:
        expected_state = WorkflowState(expected)
        if self._state is not expected_state:
            raise ValueError(
                f"Workflow state is {self._state.value!r}; expected {expected_state.value!r}."
            )
