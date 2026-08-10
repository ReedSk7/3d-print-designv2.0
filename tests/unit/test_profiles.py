from dataclasses import replace
from decimal import Decimal

import pytest

from core.profiles.models import (
    CalibrationEvidence,
    CalibrationProfileError,
    CalibrationStatus,
    CalibrationTestResult,
    CalibrationValue,
)
from core.profiles.repository import load_calibration_profile


def test_neutral_profile_is_explicitly_unverified() -> None:
    profile = load_calibration_profile("neutral_unverified_starter")
    assert not profile.is_fully_proven
    assert profile.hole_offset_mm.value == Decimal("0")
    assert "hole_offset_mm" in profile.unverified_fields


def test_proven_value_requires_evidence() -> None:
    with pytest.raises(ValueError, match="requires recorded measurement evidence"):
        CalibrationValue(value=Decimal("0.1"), status=CalibrationStatus.PROVEN)


def test_proven_value_requires_a_passing_tolerance_checked_record() -> None:
    failed = CalibrationEvidence(
        evidence_id="coupon-001",
        source_ref="workspace/coupon-001/result.json",
        recorded_at="2026-08-10T12:00:00Z",
        measurement_tool="digital caliper",
        nominal_mm=Decimal("10"),
        measured_mm=Decimal("10.2"),
        acceptance_tolerance_mm=Decimal("0.05"),
        result=CalibrationTestResult.FAILED,
        notes="Outside tolerance.",
    )
    with pytest.raises(ValueError, match="passed measurement record"):
        CalibrationValue(
            value=Decimal("0.1"),
            status=CalibrationStatus.PROVEN,
            evidence=(failed,),
        )

    with pytest.raises(ValueError, match="exceeds"):
        CalibrationEvidence(
            evidence_id="coupon-002",
            source_ref="workspace/coupon-002/result.json",
            recorded_at="2026-08-10T12:00:00Z",
            measurement_tool="digital caliper",
            nominal_mm=Decimal("10"),
            measured_mm=Decimal("10.2"),
            acceptance_tolerance_mm=Decimal("0.05"),
            result=CalibrationTestResult.PASSED,
            notes="Inconsistent synthetic result.",
        )


def test_neutral_profile_cannot_be_required_as_proven() -> None:
    profile = load_calibration_profile("neutral_unverified_starter")
    with pytest.raises(CalibrationProfileError, match="not proven"):
        profile.require_proven_fields(["hole_offset_mm"])


def test_profile_nozzle_match_allows_exact_inch_conversion_residue() -> None:
    profile = replace(
        load_calibration_profile("neutral_unverified_starter"),
        printer_profile="printer_a",
        material="PETG",
        nozzle_diameter_mm=Decimal("0.4"),
    )
    assert profile.applies_to(
        "printer_a", "PETG", Decimal("0.3999999999999999968")
    )
