from decimal import Decimal

import pytest

from core.units.conversion import from_mm, scad_number, to_mm


def test_millimeters_are_unchanged() -> None:
    assert to_mm(Decimal("12.3456789"), "mm") == Decimal("12.3456789")


def test_inches_use_exact_definition_without_rounding() -> None:
    assert to_mm(Decimal("0.001"), "inch") == Decimal("0.0254")
    assert to_mm(Decimal("1"), "inch") == Decimal("25.4")


def test_mm_inch_round_trip_retains_decimal_precision() -> None:
    original = Decimal("31.7500001")
    round_trip = to_mm(from_mm(original, "inch"), "inch")
    assert abs(round_trip - original) < Decimal("1e-24")


def test_scad_number_avoids_scientific_notation() -> None:
    assert scad_number(Decimal("0.0000100")) == "0.00001"
    assert scad_number(Decimal("25.4000")) == "25.4"


def test_unknown_unit_fails() -> None:
    with pytest.raises(ValueError, match="Unsupported length unit"):
        to_mm(1, "cm")
