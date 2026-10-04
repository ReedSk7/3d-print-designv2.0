"""Bushing generator 1.1.0 with independent hole and shaft fit semantics."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping

from generators.base import (
    GenerationContext,
    GenerationResult,
    GeneratorMetadata,
    GeneratorValidationError,
    diameter_with_directional_fit,
    input_length_mm,
    load_template,
    scale_statement,
    scaled_bounds,
)
from generators.bushing.generator import BushingGenerator, SCAD_FACETS
from generators.v110_common import (
    FIT_SCHEMA,
    circular_coupon_geometry,
    neutral_legacy_context,
    retag_legacy_result,
    validate_fit_class,
    value_from_mm,
)


class BushingGeneratorV110(BushingGenerator):
    metadata = GeneratorMetadata(
        generator_id="bushing",
        version="1.1.0",
        name="Bushing",
        description=(
            "Hollow cylindrical bushing with independent inside-hole and "
            "outside-shaft fit controls."
        ),
        protected_interfaces=("inside_diameter", "outside_diameter"),
        fit_coupon_interfaces=("inside_diameter", "outside_diameter"),
    )
    defaults = {
        "chamfer": Decimal("0"),
        "inside_fit": "nominal",
        "outside_fit": "nominal",
        "split": False,
    }
    parameter_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["inside_diameter", "outside_diameter", "length"],
        "properties": {
            "inside_diameter": {"type": "number", "exclusiveMinimum": 0},
            "outside_diameter": {"type": "number", "exclusiveMinimum": 0},
            "length": {"type": "number", "exclusiveMinimum": 0},
            "chamfer": {"type": "number", "minimum": 0, "default": 0},
            "inside_fit": FIT_SCHEMA,
            "outside_fit": FIT_SCHEMA,
            "split": {"type": "boolean", "default": False},
            "split_width": {"type": "number", "exclusiveMinimum": 0},
            "minimum_wall_thickness": {"type": "number", "exclusiveMinimum": 0},
        },
        "allOf": [
            {
                "if": {"properties": {"split": {"const": True}}, "required": ["split"]},
                "then": {"required": ["split_width"]},
            }
        ],
        "additionalProperties": False,
    }

    def generate(
        self, parameters: Mapping[str, Any], context: GenerationContext
    ) -> GenerationResult:
        values = dict(self.defaults)
        values.update(parameters)
        try:
            nominal_inside = input_length_mm(
                values["inside_diameter"], context.input_units, "inside_diameter"
            )
            nominal_outside = input_length_mm(
                values["outside_diameter"], context.input_units, "outside_diameter"
            )
            nominal_length = input_length_mm(
                values["length"], context.input_units, "length"
            )
        except KeyError as exc:
            raise GeneratorValidationError(
                [f"Missing bushing parameter: {exc.args[0]}"]
            ) from exc

        inside_fit = validate_fit_class(values["inside_fit"], "inside_fit")
        outside_fit = validate_fit_class(values["outside_fit"], "outside_fit")
        inside = diameter_with_directional_fit(
            nominal_inside,
            interface="hole",
            fit_class=inside_fit,
            context=context,
        )
        outside = diameter_with_directional_fit(
            nominal_outside,
            interface="shaft",
            fit_class=outside_fit,
            context=context,
        )

        supported = set(self.metadata.fit_coupon_interfaces)
        coupon_parameter = context.coupon_parameter or "inside_diameter"
        errors: list[str] = []
        if context.generation_mode == "fit_coupon" and coupon_parameter not in supported:
            errors.append(
                "Bushing 1.1.0 fit coupons support inside_diameter or outside_diameter."
            )
        if (
            context.accepted_coupon_parameter is not None
            and context.accepted_coupon_parameter not in supported
        ):
            errors.append(
                "Bushing 1.1.0 accepted coupon interface must be inside_diameter or outside_diameter."
            )
        if context.accepted_coupon_parameter == "inside_diameter":
            inside += context.accepted_coupon_offset_mm
        elif context.accepted_coupon_parameter == "outside_diameter":
            outside += context.accepted_coupon_offset_mm
        if errors:
            raise GeneratorValidationError(errors)

        legacy_parameters = dict(values)
        legacy_parameters.pop("inside_fit", None)
        legacy_parameters.pop("outside_fit", None)
        legacy_parameters["inside_diameter"] = value_from_mm(inside, context.input_units)
        legacy_parameters["outside_diameter"] = value_from_mm(outside, context.input_units)
        legacy_parameters["fit_class"] = "nominal"
        nominal_protected = {
            "inside_diameter": nominal_inside,
            "outside_diameter": nominal_outside,
            "length": nominal_length,
        }

        if context.generation_mode != "fit_coupon":
            legacy_result = super().generate(
                legacy_parameters,
                neutral_legacy_context(context, coupon_parameter=None),
            )
            resolved = dict(legacy_result.resolved_parameters_mm)
            resolved.pop("fit_class", None)
            resolved.update(inside_fit=inside_fit, outside_fit=outside_fit)
            return retag_legacy_result(
                legacy_result,
                metadata=self.metadata,
                resolved_parameters_mm=resolved,
                nominal_protected_dimensions_mm=nominal_protected,
            )

        # Validate complete-part geometry (including radial wall) before
        # rendering a smaller purpose-built interface coupon.
        validated = super().generate(
            legacy_parameters,
            neutral_legacy_context(
                context, generation_mode="full_part", coupon_parameter=None
            ),
        )
        interface_kind = "hole" if coupon_parameter == "inside_diameter" else "shaft"
        coupon = circular_coupon_geometry(
            base_diameter_mm=inside if interface_kind == "hole" else outside,
            candidate_offsets_mm=context.coupon_offsets_mm,
            context=context,
            interface_kind=interface_kind,
        )
        source = load_template(__file__).substitute(
            generator_version=self.metadata.version,
            artifact_kind="fit_coupon",
            parameter_block=coupon.parameter_block,
            geometry_block=coupon.geometry_block,
            scale_vector=scale_statement(context),
            facets=SCAD_FACETS,
        )
        resolved = dict(validated.resolved_parameters_mm)
        resolved.pop("fit_class", None)
        resolved.update(
            inside_fit=inside_fit,
            outside_fit=outside_fit,
            coupon_interface_kind=interface_kind,
            coupon_candidate_diameters=coupon.candidate_diameters_mm,
            coupon_candidate_map=coupon.candidate_map,
        )
        return GenerationResult(
            source=source,
            expected_bounds_mm=scaled_bounds(coupon.raw_bounds_mm, context),
            resolved_parameters_mm=resolved,
            nominal_protected_dimensions_mm=nominal_protected,
            warnings=(
                "Numbered fit coupon is computationally checked only; a printed result must be recorded manually.",
            ),
            expected_body_count=1,
            artifact_kind="fit_coupon",
        )
