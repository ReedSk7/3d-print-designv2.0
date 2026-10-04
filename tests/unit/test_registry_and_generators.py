from decimal import Decimal

import pytest

from generators.base import GenerationContext, GeneratorValidationError
from generators.registry import GeneratorNotFoundError, discover_generators, get_generator


def context(*, fit_class: str = "nominal", hole_offset: str = "0", fit_offset: str = "0") -> GenerationContext:
    return GenerationContext(
        input_units="mm",
        nozzle_diameter_mm=Decimal("0.4"),
        fit_class=fit_class,
        calibration_offsets_mm={
            "hole_offset_mm": Decimal(hole_offset),
            "shaft_offset_mm": Decimal("0"),
            "slip_fit_offset_mm": Decimal(fit_offset),
            "press_fit_offset_mm": Decimal(fit_offset),
        },
    )


def test_registry_discovers_initial_generators_by_id() -> None:
    assert set(discover_generators()) == {"bushing", "round_adapter", "flange_plate"}
    assert get_generator("bushing", "1.0.0").metadata.name == "Bushing"


def test_registry_rejects_unknown_id_and_version() -> None:
    with pytest.raises(GeneratorNotFoundError, match="Unknown generator ID"):
        get_generator("freeform_magic")
    with pytest.raises(GeneratorNotFoundError, match="unavailable"):
        get_generator("bushing", "9.9.9")


def test_bushing_rejects_impossible_diameters() -> None:
    generator = get_generator("bushing")
    with pytest.raises(GeneratorValidationError, match="outside_diameter"):
        generator.generate(
            {
                "inside_diameter": 20,
                "outside_diameter": 18,
                "length": 10,
                "fit_class": "nominal",
            },
            context(),
        )


def test_bushing_enforces_two_nozzle_minimum_wall() -> None:
    generator = get_generator("bushing")
    with pytest.raises(GeneratorValidationError, match="two nozzle diameters"):
        generator.generate(
            {
                "inside_diameter": 9,
                "outside_diameter": 10,
                "length": 10,
                "fit_class": "nominal",
            },
            context(),
        )


def test_split_bushing_reports_reduced_x_extent() -> None:
    result = get_generator("bushing").generate(
        {
            "inside_diameter": 20,
            "outside_diameter": 30,
            "length": 10,
            "fit_class": "nominal",
            "split": True,
            "split_width": 20,
        },
        context(),
    )
    assert result.expected_bounds_mm[0] == pytest.approx(
        Decimal("26.1747"), abs=Decimal("0.001")
    )
    assert result.expected_bounds_mm[1:] == (Decimal("30"), Decimal("10"))


def test_fit_profile_offsets_are_explicit_and_signed() -> None:
    generator = get_generator("bushing")
    result = generator.generate(
        {
            "inside_diameter": 20,
            "outside_diameter": 30,
            "length": 10,
            "fit_class": "slip",
        },
        context(fit_class="slip", hole_offset="0.2", fit_offset="0.1"),
    )
    assert result.resolved_parameters_mm["inside_diameter"] == Decimal("20.3")
    assert result.expected_bounds_mm == (
        Decimal("30"),
        Decimal("30"),
        Decimal("10"),
    )


def test_round_adapter_rejects_mismatched_straight_ends() -> None:
    generator = get_generator("round_adapter")
    with pytest.raises(GeneratorValidationError, match="straight transition"):
        generator.generate(
            {
                "end_a": {"diameter_type": "inside", "diameter": 40},
                "end_b": {"diameter_type": "inside", "diameter": 45},
                "length": 30,
                "wall_thickness": 2,
                "transition": "straight",
                "fit_class": "nominal",
            },
            context(),
        )


def test_flange_plate_rejects_holes_outside_plate() -> None:
    generator = get_generator("flange_plate")
    with pytest.raises(GeneratorValidationError, match="edge wall"):
        generator.generate(
            {
                "outer_width": 50,
                "outer_height": 40,
                "plate_thickness": 4,
                "center_opening": {"type": "none"},
                "corner_radius": 3,
                "mounting_hole_pattern": {
                    "type": "rectangular",
                    "x_spacing": 48,
                    "y_spacing": 38,
                },
                "mounting_hole_diameter": 5,
                "fit_class": "nominal",
            },
            context(),
        )


def test_flange_plate_rejects_holes_lost_in_rounded_corners() -> None:
    generator = get_generator("flange_plate")
    with pytest.raises(GeneratorValidationError, match="rounded plate edge wall"):
        generator.generate(
            {
                "outer_width": 40,
                "outer_height": 40,
                "plate_thickness": 4,
                "center_opening": {"type": "none"},
                "corner_radius": 20,
                "mounting_hole_pattern": {
                    "type": "rectangular",
                    "x_spacing": 30,
                    "y_spacing": 30,
                },
                "mounting_hole_diameter": 2,
                "fit_class": "nominal",
            },
            context(),
        )


def test_flange_plate_rejects_mounting_holes_overlapping_center_opening() -> None:
    generator = get_generator("flange_plate")
    with pytest.raises(GeneratorValidationError, match="overlaps the center opening"):
        generator.generate(
            {
                "outer_width": 60,
                "outer_height": 60,
                "plate_thickness": 4,
                "center_opening": {"type": "circle", "diameter": 30},
                "corner_radius": 4,
                "mounting_hole_pattern": {
                    "type": "rectangular",
                    "x_spacing": 20,
                    "y_spacing": 20,
                },
                "mounting_hole_diameter": 5,
                "fit_class": "nominal",
            },
            context(),
        )


def test_flange_plate_rejects_rectangular_opening_through_rounded_wall() -> None:
    generator = get_generator("flange_plate")
    with pytest.raises(GeneratorValidationError, match="rounded-corner minimum wall"):
        generator.generate(
            {
                "outer_width": 40,
                "outer_height": 40,
                "plate_thickness": 4,
                "center_opening": {"type": "rectangle", "width": 28, "height": 28},
                "corner_radius": 20,
                "mounting_hole_pattern": {"type": "none"},
                "mounting_hole_diameter": 4,
                "fit_class": "nominal",
            },
            context(),
        )


def test_calibration_cannot_erase_flange_or_adapter_holes() -> None:
    bad_context = context(hole_offset="-10")
    with pytest.raises(GeneratorValidationError, match="must remain positive"):
        get_generator("flange_plate").generate(
            {
                "outer_width": 80,
                "outer_height": 80,
                "plate_thickness": 4,
                "center_opening": {"type": "circle", "diameter": 5},
                "corner_radius": 5,
                "mounting_hole_pattern": {"type": "none"},
                "mounting_hole_diameter": 4,
                "fit_class": "nominal",
            },
            bad_context,
        )

    with pytest.raises(GeneratorValidationError, match="screw-hole diameter"):
        get_generator("round_adapter").generate(
            {
                "end_a": {"diameter_type": "inside", "diameter": 20},
                "end_b": {"diameter_type": "inside", "diameter": 20},
                "length": 30,
                "wall_thickness": 2,
                "transition": "straight",
                "fit_class": "nominal",
                "mounting_flange": {
                    "enabled": True,
                    "outer_diameter": 60,
                    "thickness": 4,
                    "screw_hole_pattern": {
                        "enabled": True,
                        "count": 4,
                        "bolt_circle_diameter": 45,
                        "hole_diameter": 4,
                    },
                },
            },
            bad_context,
        )


def test_bushing_coupon_contains_every_requested_candidate() -> None:
    generator = get_generator("bushing")
    coupon_context = GenerationContext(
        input_units="mm",
        nozzle_diameter_mm=Decimal("0.4"),
        fit_class="nominal",
        generation_mode="fit_coupon",
        coupon_parameter="inside_diameter",
        coupon_offsets_mm=(Decimal("-0.1"), Decimal("0"), Decimal("0.1")),
    )
    result = generator.generate(
        {
            "inside_diameter": 20,
            "outside_diameter": 30,
            "length": 10,
            "fit_class": "nominal",
        },
        coupon_context,
    )
    assert result.artifact_kind == "fit_coupon"
    assert result.resolved_parameters_mm["coupon_candidate_diameters"] == (
        Decimal("19.9"),
        Decimal("20"),
        Decimal("20.1"),
    )
    assert result.expected_bounds_mm[0] > result.expected_bounds_mm[1]
