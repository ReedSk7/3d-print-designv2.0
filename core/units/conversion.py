"""Length conversion without implicit precision loss.

JSON floating-point values are loaded as :class:`~decimal.Decimal` by the
specification loader.  These helpers also accept strings and ordinary Python
numbers so generator code has one conversion boundary.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import TypeAlias


DecimalLike: TypeAlias = Decimal | int | float | str
MM_PER_INCH = Decimal("25.4")


class LengthUnit(str, Enum):
    MILLIMETER = "mm"
    INCH = "inch"


_UNIT_ALIASES = {
    "mm": LengthUnit.MILLIMETER,
    "millimeter": LengthUnit.MILLIMETER,
    "millimeters": LengthUnit.MILLIMETER,
    "in": LengthUnit.INCH,
    "inch": LengthUnit.INCH,
    "inches": LengthUnit.INCH,
}


def as_decimal(value: DecimalLike) -> Decimal:
    """Return a finite ``Decimal`` without converting through binary float math."""

    if isinstance(value, bool):
        raise TypeError("Boolean values are not valid dimensions.")
    try:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid numeric value: {value!r}") from exc
    if not decimal_value.is_finite():
        raise ValueError(f"Dimension must be finite: {value!r}")
    return decimal_value


def normalize_unit(units: LengthUnit | str) -> LengthUnit:
    if isinstance(units, LengthUnit):
        return units
    normalized = _UNIT_ALIASES.get(str(units).strip().lower())
    if normalized is None:
        raise ValueError(f"Unsupported length unit: {units!r}. Use 'mm' or 'inch'.")
    return normalized


def to_mm(value: DecimalLike, units: LengthUnit | str) -> Decimal:
    """Convert a length to millimeters using the exact 25.4 mm/in definition."""

    decimal_value = as_decimal(value)
    return decimal_value if normalize_unit(units) is LengthUnit.MILLIMETER else decimal_value * MM_PER_INCH


def from_mm(value: DecimalLike, units: LengthUnit | str) -> Decimal:
    """Convert a millimeter length to ``units`` without applying rounding."""

    decimal_value = as_decimal(value)
    return decimal_value if normalize_unit(units) is LengthUnit.MILLIMETER else decimal_value / MM_PER_INCH


def scad_number(value: DecimalLike) -> str:
    """Format a finite number as a plain OpenSCAD decimal literal.

    Scientific notation and insignificant trailing zeroes are removed.  This
    keeps generated source stable while retaining every significant decimal
    digit supplied to the domain layer.
    """

    decimal_value = as_decimal(value)
    if decimal_value == 0:
        return "0"
    rendered = format(decimal_value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered
