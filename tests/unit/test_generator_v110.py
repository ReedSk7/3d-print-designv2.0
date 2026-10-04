from __future__ import annotations

from decimal import Decimal

import pytest

from generators.base import (
    GenerationContext,
    GeneratorValidationError,
    diameter_with_directional_fit,
)
from generators.registry import available_generator_versions, get_generator
from core.profiles.repository import load_calibration_profile


def context(
    *,
    mode: str = "full_part",
    coupon_parameter: str | None = None,
    offsets: tuple[str, ...] = (),
    accepted_parameter: str | None = None,
    accepted_offset: str = "0",
    calibration: dict[str, str] | None = None,
) -> GenerationContext:
    values = {
        "hole_dimensional_correction_mm": "0",
        "shaft_dimensional_correction_mm": "0",
        "hole_slip_allowance_mm": "0",
        "shaft_slip_allowance_mm": "0",
        "hole_press_allowance_mm": "0",
        "shaft_press_allowance_mm": "0",
    }
    values.update(calibration or {})
    return GenerationContext(
        input_units="mm",
        nozzle_diameter_mm=Decimal("0.4"),
        fit_class="nominal",
        calibration_offsets_mm={key: Decimal(value) for key, value in values.items()},
        generation_mode=mode,
        coupon_parameter=coupon_parameter,
        coupon_offsets_mm=tuple(Decimal(value) for value in offsets),
        accepted_coupon_parameter=accepted_parameter,
        accepted_coupon_offset_mm=Decimal(accepted_offset),
    )


def test_registry_keeps_legacy_default_and_resolves_both_versions() -> None:
    for generator_id in ("bushing", "round_adapter", "flange_plate"):
        assert available_generator_versions(generator_id) == ("1.0.0", "1.1.0")
        assert get_generator(generator_id).metadata.version == "1.0.0"
        assert get_generator(generator_id, "1.0.0").metadata.version == "1.0.0"
        assert get_generator(generator_id, "1.1.0").metadata.version == "1.1.0"


def test_profile_exposes_directional_proof_fields_without_changing_legacy_aggregate() -> None:
    profile = load_calibration_profile("neutral_unverified_starter")
    assert "hole_slip_allowance_mm" in profile.directional_unverified_fields
    assert "hole_slip_allowance_mm" not in profile.unverified_fields
    assert not profile.is_directional_fit_fully_proven
    assert "hole_slip_allowance_mm" not in profile.unverified_fields_for_generator_version(
        "1.0.0"
    )
    assert "hole_slip_allowance_mm" in profile.unverified_fields_for_generator_version(
        "1.1.0"
    )


def test_hole_and_shaft_allowances_have_opposite_fit_directions() -> None:
    fit_context = context(
        calibration={
            "hole_dimensional_correction_mm": "0.1",
            "shaft_dimensional_correction_mm": "0.1",
            "hole_slip_allowance_mm": "0.2",
            "shaft_slip_allowance_mm": "0.2",
            "hole_press_allowance_mm": "0.2",
            "shaft_press_allowance_mm": "0.2",
        }
    )
    nominal = Decimal("10")
    assert diameter_with_directional_fit(
        nominal, interface="hole", fit_class="slip", context=fit_context
    ) == Decimal("10.3")
    assert diameter_with_directional_fit(
        nominal, interface="shaft", fit_class="slip", context=fit_context
    ) == Decimal("9.9")
    assert diameter_with_directional_fit(
        nominal, interface="hole", fit_class="press", context=fit_context
    ) == Decimal("9.9")
    assert diameter_with_directional_fit(
        nominal, interface="shaft", fit_class="press", context=fit_context
    ) == Decimal("10.3")


def test_directional_allowance_rejects_negative_magnitude() -> None:
    with pytest.raises(GeneratorValidationError, match="non-negative"):
        diameter_with_directional_fit(
            Decimal("10"),
            interface="hole",
            fit_class="slip",
            context=context(calibration={"hole_slip_allowance_mm": "-0.1"}),
        )


def test_bushing_v110_has_independent_inside_and_outside_fit() -> None:
    result = get_generator("bushing", "1.1.0").generate(
        {
            "inside_diameter": 20,
            "outside_diameter": 30,
            "length": 10,
            "inside_fit": "slip",
            "outside_fit": "press",
        },
        context(
            calibration={
                "hole_slip_allowance_mm": "0.2",
                "shaft_press_allowance_mm": "0.3",
            }
        ),
    )
    assert result.resolved_parameters_mm["inside_diameter"] == Decimal("20.2")
    assert result.resolved_parameters_mm["outside_diameter"] == Decimal("30.3")
    assert result.resolved_parameters_mm["inside_fit"] == "slip"
    assert result.resolved_parameters_mm["outside_fit"] == "press"


def test_bushing_outside_coupon_is_numbered_male_geometry_and_applies_only_outside() -> None:
    result = get_generator("bushing", "1.1.0").generate(
        {
            "inside_diameter": 20,
            "outside_diameter": 30,
            "length": 10,
            "inside_fit": "nominal",
            "outside_fit": "nominal",
        },
        context(
            mode="fit_coupon",
            coupon_parameter="outside_diameter",
            offsets=("-0.1", "0", "0.1"),
        ),
    )
    assert result.artifact_kind == "fit_coupon"
    assert result.resolved_parameters_mm["coupon_interface_kind"] == "shaft"
    assert result.resolved_parameters_mm["inside_diameter"] == Decimal("20")
    assert result.resolved_parameters_mm["coupon_candidate_diameters"] == (
        Decimal("29.9"),
        Decimal("30"),
        Decimal("30.1"),
    )
    candidate_map = result.resolved_parameters_mm["coupon_candidate_map"]
    assert [item["offset_mm"] for item in candidate_map] == [
        Decimal("-0.1"),
        Decimal("0"),
        Decimal("0.1"),
    ]
    assert "post_height" in result.source
    assert 'text(str(index + 1)' in result.source


def test_bushing_inside_coupon_is_numbered_hole_geometry() -> None:
    result = get_generator("bushing", "1.1.0").generate(
        {
            "inside_diameter": 20,
            "outside_diameter": 30,
            "length": 10,
            "inside_fit": "slip",
            "outside_fit": "nominal",
        },
        context(
            mode="fit_coupon",
            coupon_parameter="inside_diameter",
            offsets=("-0.1", "0", "0.1"),
        ),
    )
    assert result.resolved_parameters_mm["coupon_interface_kind"] == "hole"
    assert "difference()" in result.source
    assert 'text(str(index + 1)' in result.source


def test_selected_bushing_outside_offset_changes_only_outside_and_rechecks_wall() -> None:
    generator = get_generator("bushing", "1.1.0")
    result = generator.generate(
        {
            "inside_diameter": 20,
            "outside_diameter": 30,
            "length": 10,
            "inside_fit": "nominal",
            "outside_fit": "nominal",
        },
        context(accepted_parameter="outside_diameter", accepted_offset="0.2"),
    )
    assert result.resolved_parameters_mm["inside_diameter"] == Decimal("20")
    assert result.resolved_parameters_mm["outside_diameter"] == Decimal("30.2")

    with pytest.raises(GeneratorValidationError, match="Radial wall"):
        generator.generate(
            {
                "inside_diameter": 20,
                "outside_diameter": 22,
                "length": 10,
                "inside_fit": "nominal",
                "outside_fit": "nominal",
            },
            context(accepted_parameter="outside_diameter", accepted_offset="-0.5"),
        )


def test_round_adapter_fits_do_not_leak_across_interfaces() -> None:
    result = get_generator("round_adapter", "1.1.0").generate(
        {
            "end_a": {"diameter_type": "inside", "diameter": 40},
            "end_b": {"diameter_type": "outside", "diameter": 30},
            "length": 30,
            "wall_thickness": 2,
            "transition": "tapered",
            "end_a_fit": "slip",
            "end_b_fit": "nominal",
            "mounting_hole_fit": "press",
            "mounting_flange": {
                "enabled": True,
                "outer_diameter": 70,
                "thickness": 4,
                "screw_hole_pattern": {
                    "enabled": True,
                    "count": 4,
                    "bolt_circle_diameter": 56,
                    "hole_diameter": 5,
                },
            },
        },
        context(
            calibration={
                "hole_slip_allowance_mm": "0.2",
                "shaft_slip_allowance_mm": "0.9",
                "hole_press_allowance_mm": "0.1",
            }
        ),
    )
    assert result.resolved_parameters_mm["end_a"]["inside_diameter"] == Decimal("40.2")
    assert result.resolved_parameters_mm["end_b"]["outside_diameter"] == Decimal("30")
    assert result.resolved_parameters_mm["mounting_flange"]["screw_hole_pattern"][
        "hole_diameter"
    ] == Decimal("4.9")


def test_round_adapter_end_coupon_geometry_matches_end_interface_kind() -> None:
    generator = get_generator("round_adapter", "1.1.0")
    parameters = {
        "end_a": {"diameter_type": "inside", "diameter": 40},
        "end_b": {"diameter_type": "outside", "diameter": 30},
        "length": 30,
        "wall_thickness": 2,
        "transition": "tapered",
        "end_a_fit": "nominal",
        "end_b_fit": "nominal",
        "mounting_hole_fit": "nominal",
    }
    inside_coupon = generator.generate(
        parameters,
        context(
            mode="fit_coupon",
            coupon_parameter="end_a.diameter",
            offsets=("-0.1", "0", "0.1"),
        ),
    )
    outside_coupon = generator.generate(
        parameters,
        context(
            mode="fit_coupon",
            coupon_parameter="end_b.diameter",
            offsets=("-0.1", "0", "0.1"),
        ),
    )
    assert inside_coupon.resolved_parameters_mm["coupon_interface_kind"] == "hole"
    assert outside_coupon.resolved_parameters_mm["coupon_interface_kind"] == "shaft"
    assert "post_height" in outside_coupon.source


def test_flange_rectangular_opening_fit_and_coupon_are_independent_and_labeled() -> None:
    generator = get_generator("flange_plate", "1.1.0")
    parameters = {
        "outer_width": 100,
        "outer_height": 80,
        "plate_thickness": 5,
        "center_opening": {"type": "rectangle", "width": 50, "height": 30},
        "corner_radius": 8,
        "mounting_hole_pattern": {
            "type": "rectangular",
            "x_spacing": 80,
            "y_spacing": 60,
        },
        "mounting_hole_diameter": 5,
        "center_opening_fit": "slip",
        "mounting_hole_fit": "press",
    }
    fit_context = context(
        calibration={
            "hole_dimensional_correction_mm": "0.1",
            "hole_slip_allowance_mm": "0.2",
            "hole_press_allowance_mm": "0.05",
        }
    )
    full = generator.generate(parameters, fit_context)
    assert full.resolved_parameters_mm["center_opening"]["width"] == Decimal("50.3")
    assert full.resolved_parameters_mm["center_opening"]["height"] == Decimal("30.3")
    assert full.resolved_parameters_mm["mounting_hole_diameter"] == Decimal("5.05")

    coupon = generator.generate(
        parameters,
        context(
            mode="fit_coupon",
            coupon_parameter="center_opening.height",
            offsets=("-0.2", "0", "0.2"),
        ),
    )
    candidate_map = coupon.resolved_parameters_mm["coupon_candidate_map"]
    assert [item["height_mm"] for item in candidate_map] == [
        Decimal("29.8"),
        Decimal("30"),
        Decimal("30.2"),
    ]
    assert all(item["width_mm"] == Decimal("50") for item in candidate_map)
    assert "coupon_widths" in coupon.source
    assert 'text(str(index + 1)' in coupon.source


def test_flange_circular_center_opening_coupon_is_supported() -> None:
    result = get_generator("flange_plate", "1.1.0").generate(
        {
            "outer_width": 80,
            "outer_height": 70,
            "plate_thickness": 5,
            "center_opening": {"type": "circle", "diameter": 30},
            "corner_radius": 6,
            "mounting_hole_pattern": {"type": "none"},
            "mounting_hole_diameter": 5,
            "center_opening_fit": "nominal",
            "mounting_hole_fit": "nominal",
        },
        context(
            mode="fit_coupon",
            coupon_parameter="center_opening.diameter",
            offsets=("-0.1", "0", "0.1"),
        ),
    )
    assert result.resolved_parameters_mm["coupon_candidate_diameters"] == (
        Decimal("29.9"),
        Decimal("30"),
        Decimal("30.1"),
    )
    assert result.resolved_parameters_mm["coupon_interface_kind"] == "hole"


def test_v110_coupon_interface_applicability_tracks_optional_holes() -> None:
    adapter = get_generator("round_adapter", "1.1.0")
    parameters = {
        "end_a": {"diameter_type": "inside", "diameter": 40},
        "end_b": {"diameter_type": "inside", "diameter": 30},
        "length": 30,
        "wall_thickness": 2,
        "transition": "tapered",
    }
    assert adapter.applicable_coupon_interfaces(parameters) == (
        "end_a.diameter",
        "end_b.diameter",
    )
    assert not adapter.supports_coupon_interface(
        "mounting_flange.screw_hole_pattern.hole_diameter", parameters
    )
    with pytest.raises(GeneratorValidationError, match="unsupported or absent"):
        adapter.generate(
            parameters,
            context(
                mode="fit_coupon",
                coupon_parameter="mounting_flange.screw_hole_pattern.hole_diameter",
                offsets=("-0.1", "0", "0.1"),
            ),
        )


def test_v100_legacy_global_fit_behavior_is_unchanged() -> None:
    legacy_context = GenerationContext(
        input_units="mm",
        nozzle_diameter_mm=Decimal("0.4"),
        fit_class="slip",
        calibration_offsets_mm={
            "hole_offset_mm": Decimal("0.2"),
            "shaft_offset_mm": Decimal("0"),
            "slip_fit_offset_mm": Decimal("0.1"),
            "press_fit_offset_mm": Decimal("0"),
        },
    )
    result = get_generator("bushing", "1.0.0").generate(
        {
            "inside_diameter": 20,
            "outside_diameter": 30,
            "length": 10,
            "fit_class": "slip",
        },
        legacy_context,
    )
    assert result.resolved_parameters_mm["inside_diameter"] == Decimal("20.3")
    assert "generator: bushing 1.0.0" in result.source
