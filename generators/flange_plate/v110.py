"""Flange-plate generator 1.1.0 with independent opening and hole fits."""

from __future__ import annotations

from copy import deepcopy
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
    scad_number,
    scale_statement,
    scaled_bounds,
)
from generators.flange_plate.generator import FlangePlateGenerator
from generators.v110_common import (
    FIT_SCHEMA,
    circular_coupon_geometry,
    neutral_legacy_context,
    retag_legacy_result,
    validate_fit_class,
    value_from_mm,
)


class FlangePlateGeneratorV110(FlangePlateGenerator):
    metadata = GeneratorMetadata(
        generator_id="flange_plate",
        version="1.1.0",
        name="Flange Plate",
        description=(
            "Rounded flange plate with independent center-opening and mounting-hole fits."
        ),
        protected_interfaces=(
            "center_opening.diameter",
            "center_opening.width",
            "center_opening.height",
            "mounting_hole_diameter",
        ),
        fit_coupon_interfaces=(
            "center_opening.diameter",
            "center_opening.width",
            "center_opening.height",
            "mounting_hole_diameter",
        ),
    )
    defaults = {
        "hole_finish": {"type": "none"},
        "center_opening_fit": "nominal",
        "mounting_hole_fit": "nominal",
    }
    parameter_schema = deepcopy(FlangePlateGenerator.parameter_schema)
    parameter_schema["properties"].pop("fit_class")
    parameter_schema["properties"].update(
        {
            "center_opening_fit": FIT_SCHEMA,
            "mounting_hole_fit": FIT_SCHEMA,
        }
    )

    def applicable_protected_interfaces(
        self, parameters: Mapping[str, Any]
    ) -> tuple[str, ...]:
        result: list[str] = []
        opening = parameters.get("center_opening")
        if isinstance(opening, Mapping):
            if opening.get("type") == "circle":
                result.append("center_opening.diameter")
            elif opening.get("type") == "rectangle":
                result.extend(("center_opening.width", "center_opening.height"))
        pattern = parameters.get("mounting_hole_pattern")
        if isinstance(pattern, Mapping) and pattern.get("type") != "none":
            result.append("mounting_hole_diameter")
        return tuple(result)

    def applicable_coupon_interfaces(
        self, parameters: Mapping[str, Any]
    ) -> tuple[str, ...]:
        return self.applicable_protected_interfaces(parameters)

    def generate(
        self, parameters: Mapping[str, Any], context: GenerationContext
    ) -> GenerationResult:
        values: dict[str, Any] = deepcopy(self.defaults)
        values.update(deepcopy(dict(parameters)))
        center_fit = validate_fit_class(
            values["center_opening_fit"], "center_opening_fit"
        )
        mounting_fit = validate_fit_class(
            values["mounting_hole_fit"], "mounting_hole_fit"
        )
        try:
            opening = values["center_opening"]
            pattern = values["mounting_hole_pattern"]
            if not isinstance(opening, Mapping) or not isinstance(pattern, Mapping):
                raise TypeError
            opening_type = str(opening["type"])
            pattern_type = str(pattern["type"])
            nominal_mounting = input_length_mm(
                values["mounting_hole_diameter"],
                context.input_units,
                "mounting_hole_diameter",
            )
        except (KeyError, TypeError) as exc:
            label = exc.args[0] if isinstance(exc, KeyError) else "center_opening/pattern"
            raise GeneratorValidationError(
                [f"Missing flange_plate parameter: {label}"]
            ) from exc

        nominal_opening: dict[str, Decimal] = {}
        resolved_opening: dict[str, Decimal] = {}
        if opening_type == "circle":
            nominal_opening["diameter"] = input_length_mm(
                opening["diameter"], context.input_units, "center_opening.diameter"
            )
            resolved_opening["diameter"] = diameter_with_directional_fit(
                nominal_opening["diameter"],
                interface="hole",
                fit_class=center_fit,
                context=context,
            )
        elif opening_type == "rectangle":
            for dimension in ("width", "height"):
                nominal_opening[dimension] = input_length_mm(
                    opening[dimension],
                    context.input_units,
                    f"center_opening.{dimension}",
                )
                resolved_opening[dimension] = diameter_with_directional_fit(
                    nominal_opening[dimension],
                    interface="hole",
                    fit_class=center_fit,
                    context=context,
                )
        elif opening_type != "none":
            raise GeneratorValidationError(
                ["center_opening.type must be none, circle, or rectangle."]
            )

        holes_present = pattern_type != "none"
        resolved_mounting = nominal_mounting
        if holes_present:
            resolved_mounting = diameter_with_directional_fit(
                nominal_mounting,
                interface="hole",
                fit_class=mounting_fit,
                context=context,
            )

        coupon_parameter = context.coupon_parameter or "mounting_hole_diameter"
        applicable = set(self.applicable_coupon_interfaces(values))
        errors: list[str] = []
        if context.generation_mode == "fit_coupon" and coupon_parameter not in applicable:
            errors.append(
                "Flange-plate 1.1.0 coupon interface is unsupported or absent from this configuration."
            )
        if (
            context.accepted_coupon_parameter is not None
            and context.accepted_coupon_parameter not in applicable
        ):
            errors.append(
                "Flange-plate 1.1.0 accepted coupon interface is unsupported or absent."
            )
        if errors:
            raise GeneratorValidationError(errors)
        if context.accepted_coupon_parameter == "center_opening.diameter":
            resolved_opening["diameter"] += context.accepted_coupon_offset_mm
        elif context.accepted_coupon_parameter == "center_opening.width":
            resolved_opening["width"] += context.accepted_coupon_offset_mm
        elif context.accepted_coupon_parameter == "center_opening.height":
            resolved_opening["height"] += context.accepted_coupon_offset_mm
        elif context.accepted_coupon_parameter == "mounting_hole_diameter":
            resolved_mounting += context.accepted_coupon_offset_mm
        legacy_parameters = deepcopy(values)
        legacy_parameters.pop("center_opening_fit", None)
        legacy_parameters.pop("mounting_hole_fit", None)
        legacy_parameters["fit_class"] = "nominal"
        for dimension, value in resolved_opening.items():
            legacy_parameters["center_opening"][dimension] = value_from_mm(
                value, context.input_units
            )
        legacy_parameters["mounting_hole_diameter"] = value_from_mm(
            resolved_mounting, context.input_units
        )

        if context.generation_mode != "fit_coupon":
            legacy_result = super().generate(
                legacy_parameters,
                neutral_legacy_context(context, coupon_parameter=None),
            )
            resolved = deepcopy(dict(legacy_result.resolved_parameters_mm))
            resolved.pop("fit_class", None)
            resolved.update(
                center_opening_fit=center_fit,
                mounting_hole_fit=mounting_fit,
            )
            nominal_protected = dict(legacy_result.nominal_protected_dimensions_mm)
            for dimension, value in nominal_opening.items():
                nominal_protected[f"center_opening.{dimension}"] = value
            if holes_present:
                nominal_protected["mounting_hole_diameter"] = nominal_mounting
            else:
                nominal_protected.pop("mounting_hole_diameter", None)
            return retag_legacy_result(
                legacy_result,
                metadata=self.metadata,
                resolved_parameters_mm=resolved,
                nominal_protected_dimensions_mm=nominal_protected,
            )

        validated = super().generate(
            legacy_parameters,
            neutral_legacy_context(
                context, generation_mode="full_part", coupon_parameter=None
            ),
        )
        offsets = context.coupon_offsets_mm or (Decimal("0"),)
        margin = max(context.nozzle_diameter_mm * Decimal("5"), Decimal("2"))
        thickness = validated.resolved_parameters_mm["plate_thickness"]
        if not isinstance(thickness, Decimal):
            raise RuntimeError("Resolved flange plate thickness is not a decimal.")

        if coupon_parameter in {
            "center_opening.diameter",
            "mounting_hole_diameter",
        }:
            finish_type = "none"
            finish_diameter = Decimal("0")
            finish_depth = Decimal("0")
            base_diameter = resolved_opening.get("diameter", resolved_mounting)
            if coupon_parameter == "mounting_hole_diameter":
                finish = validated.resolved_parameters_mm["hole_finish"]
                if not isinstance(finish, Mapping):
                    raise RuntimeError("Resolved flange hole finish is not a mapping.")
                finish_type = str(finish["type"])
                finish_diameter = finish["diameter"]  # type: ignore[assignment]
                finish_depth = finish["depth"]  # type: ignore[assignment]
                base_diameter = resolved_mounting
            coupon = circular_coupon_geometry(
                base_diameter_mm=base_diameter,
                candidate_offsets_mm=context.coupon_offsets_mm,
                context=context,
                interface_kind="hole",
                coupon_thickness_mm=thickness,
                finish_type=finish_type,
                finish_diameter_mm=finish_diameter,
                finish_depth_mm=finish_depth,
            )
            source = load_template(__file__).substitute(
                generator_version=self.metadata.version,
                artifact_kind="fit_coupon",
                parameter_block=coupon.parameter_block,
                geometry_block=coupon.geometry_block,
                scale_vector=scale_statement(context),
            )
            resolved = deepcopy(dict(validated.resolved_parameters_mm))
            resolved.pop("fit_class", None)
            resolved.update(
                center_opening_fit=center_fit,
                mounting_hole_fit=mounting_fit,
                coupon_interface_kind="hole",
                coupon_candidate_diameters=coupon.candidate_diameters_mm,
                coupon_candidate_map=coupon.candidate_map,
            )
            nominal_protected = dict(validated.nominal_protected_dimensions_mm)
            for dimension, value in nominal_opening.items():
                nominal_protected[f"center_opening.{dimension}"] = value
            if holes_present:
                nominal_protected["mounting_hole_diameter"] = nominal_mounting
            else:
                nominal_protected.pop("mounting_hole_diameter", None)
            return GenerationResult(
                source=source,
                expected_bounds_mm=scaled_bounds(coupon.raw_bounds_mm, context),
                resolved_parameters_mm=resolved,
                nominal_protected_dimensions_mm=nominal_protected,
                warnings=(
                    "Numbered hole fit coupon is computationally checked only; a printed result must be recorded manually.",
                ),
                expected_body_count=1,
                artifact_kind="fit_coupon",
            )
        else:
            dimension = coupon_parameter.rsplit(".", 1)[1]
            candidates = tuple(resolved_opening[dimension] + offset for offset in offsets)
            if any(candidate <= 0 for candidate in candidates):
                raise GeneratorValidationError(
                    [f"Every rectangular-opening {dimension} candidate must remain positive."]
                )
            candidate_widths = (
                candidates if dimension == "width" else tuple(
                    resolved_opening["width"] for _ in candidates
                )
            )
            candidate_heights = (
                candidates if dimension == "height" else tuple(
                    resolved_opening["height"] for _ in candidates
                )
            )
            cell_width = max(candidate_widths) + Decimal("2") * margin
            label_size = max(
                context.nozzle_diameter_mm * Decimal("8"), Decimal("3.2")
            )
            label_band = label_size + Decimal("2") * context.nozzle_diameter_mm
            cell_depth = max(candidate_heights) + Decimal("2") * margin
            depth = cell_depth + label_band
            feature_y = label_band / Decimal("2")
            label_y = -depth / Decimal("2") + context.nozzle_diameter_mm
            label_depth = min(context.nozzle_diameter_mm, thickness / Decimal("2"))
            opening_array = "\n".join(
                [
                    "coupon_widths = ["
                    + ", ".join(scad_number(value) for value in candidate_widths)
                    + "];",
                    "coupon_heights = ["
                    + ", ".join(scad_number(value) for value in candidate_heights)
                    + "];",
                ]
            )
            cut_block = """translate([
                    -coupon_widths[index] / 2,
                    -coupon_heights[index] / 2,
                    0
                ])
                    cube([
                        coupon_widths[index],
                        coupon_heights[index],
                        coupon_thickness + 2 * epsilon
                    ]);"""
            candidate_record = tuple(
                {
                    "index": index,
                    "label": str(index),
                    "offset_mm": offset,
                    "width_mm": width,
                    "height_mm": height,
                }
                for index, (offset, width, height) in enumerate(
                    zip(offsets, candidate_widths, candidate_heights), start=1
                )
            )

        width = cell_width * Decimal(len(candidates))
        parameter_block = "\n".join(
            [
                opening_array,
                f"coupon_cell_width = {scad_number(cell_width)};",
                f"coupon_width = {scad_number(width)};",
                f"coupon_depth = {scad_number(depth)};",
                f"coupon_thickness = {scad_number(thickness)};",
                f"feature_y = {scad_number(feature_y)};",
                f"label_y = {scad_number(label_y)};",
                f"label_size = {scad_number(label_size)};",
                f"label_depth = {scad_number(label_depth)};",
            ]
        )
        geometry_block = """module generated_artifact() {
    difference() {
        translate([-coupon_width / 2, -coupon_depth / 2, 0])
            cube([coupon_width, coupon_depth, coupon_thickness]);
        for (index = [0 : CANDIDATE_COUNT - 1])
            translate([
                -coupon_width / 2 + coupon_cell_width / 2 + index * coupon_cell_width,
                feature_y,
                -epsilon
            ])
                CUT_BLOCK
        for (index = [0 : CANDIDATE_COUNT - 1])
            translate([
                -coupon_width / 2 + coupon_cell_width / 2 + index * coupon_cell_width,
                label_y,
                coupon_thickness - label_depth
            ])
                linear_extrude(height = label_depth + epsilon)
                    text(str(index + 1), size = label_size, halign = "center", valign = "bottom");
    }
}""".replace("CANDIDATE_COUNT", str(len(candidates))).replace(
            "CUT_BLOCK", cut_block
        )
        source = load_template(__file__).substitute(
            generator_version=self.metadata.version,
            artifact_kind="fit_coupon",
            parameter_block=parameter_block,
            geometry_block=geometry_block,
            scale_vector=scale_statement(context),
        )
        resolved = deepcopy(dict(validated.resolved_parameters_mm))
        resolved.pop("fit_class", None)
        resolved.update(
            center_opening_fit=center_fit,
            mounting_hole_fit=mounting_fit,
            coupon_interface_kind="hole",
            coupon_candidate_dimensions=candidate_record,
            coupon_candidate_map=candidate_record,
        )
        nominal_protected = dict(validated.nominal_protected_dimensions_mm)
        for dimension, value in nominal_opening.items():
            nominal_protected[f"center_opening.{dimension}"] = value
        if holes_present:
            nominal_protected["mounting_hole_diameter"] = nominal_mounting
        else:
            nominal_protected.pop("mounting_hole_diameter", None)
        return GenerationResult(
            source=source,
            expected_bounds_mm=scaled_bounds((width, depth, thickness), context),
            resolved_parameters_mm=resolved,
            nominal_protected_dimensions_mm=nominal_protected,
            warnings=(
                "Center-opening fit coupon is computationally checked only; a printed result must be recorded manually.",
            ),
            expected_body_count=1,
            artifact_kind="fit_coupon",
        )
