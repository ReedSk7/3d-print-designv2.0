"""Deterministic hollow cylindrical bushing generator."""

from __future__ import annotations

import math
from decimal import Decimal
from typing import Any, Mapping

from generators.base import (
    GenerationContext,
    GenerationResult,
    GeneratorMetadata,
    GeneratorValidationError,
    PartGenerator,
    diameter_with_calibration,
    input_length_mm,
    load_template,
    scad_number,
    scale_statement,
    scaled_bounds,
)


SCAD_FACETS = 96


def _split_outer_extent_x(outside_diameter: Decimal, split_width: Decimal) -> Decimal:
    """Return the X extent left by the radial split in the faceted SCAD circle."""

    radius = outside_diameter / Decimal("2")
    cut_y = split_width / Decimal("2")
    step = (2 * math.pi) / SCAD_FACETS
    angle = math.asin(float(cut_y / radius))
    sector = min(int(math.floor(angle / step)), (SCAD_FACETS // 4) - 1)
    angle_a = sector * step
    angle_b = (sector + 1) * step
    y_a = radius * Decimal(str(math.sin(angle_a)))
    y_b = radius * Decimal(str(math.sin(angle_b)))
    x_a = radius * Decimal(str(math.cos(angle_a)))
    x_b = radius * Decimal(str(math.cos(angle_b)))
    interpolation = (cut_y - y_a) / (y_b - y_a)
    positive_x = x_a + interpolation * (x_b - x_a)
    return radius + positive_x


class BushingGenerator(PartGenerator):
    metadata = GeneratorMetadata(
        generator_id="bushing",
        version="1.0.0",
        name="Bushing",
        description="Hollow cylindrical bushing with optional edge chamfer and split.",
    )
    defaults = {"chamfer": Decimal("0"), "fit_class": "nominal", "split": False}
    parameter_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["inside_diameter", "outside_diameter", "length"],
        "properties": {
            "inside_diameter": {"type": "number", "exclusiveMinimum": 0},
            "outside_diameter": {"type": "number", "exclusiveMinimum": 0},
            "length": {"type": "number", "exclusiveMinimum": 0},
            "chamfer": {"type": "number", "minimum": 0, "default": 0},
            "fit_class": {
                "type": "string",
                "enum": ["nominal", "slip", "press"],
                "default": "nominal",
            },
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
        errors: list[str] = []

        try:
            nominal_inside = input_length_mm(
                values["inside_diameter"], context.input_units, "inside_diameter"
            )
            outside = input_length_mm(
                values["outside_diameter"], context.input_units, "outside_diameter"
            )
            length = input_length_mm(values["length"], context.input_units, "length")
            chamfer = input_length_mm(values["chamfer"], context.input_units, "chamfer")
        except KeyError as exc:
            raise GeneratorValidationError([f"Missing bushing parameter: {exc.args[0]}"]) from exc

        fit_class = str(values["fit_class"])
        if fit_class != context.fit_class:
            errors.append(
                "bushing fit_class must match the project fit_profile class to avoid ambiguous offsets."
            )
        inside = diameter_with_calibration(
            nominal_inside, interface="hole", fit_class=fit_class, context=context
        )
        if context.accepted_coupon_parameter is not None:
            if context.accepted_coupon_parameter != "inside_diameter":
                errors.append("Bushing accepted fit coupons support only inside_diameter.")
            else:
                inside += context.accepted_coupon_offset_mm
        radial_wall = (outside - inside) / Decimal("2")
        minimum_wall = context.nozzle_diameter_mm * Decimal("2")
        if "minimum_wall_thickness" in values:
            minimum_wall = max(
                minimum_wall,
                input_length_mm(
                    values["minimum_wall_thickness"],
                    context.input_units,
                    "minimum_wall_thickness",
                ),
            )

        if inside <= 0:
            errors.append("Resolved inside diameter must be greater than zero.")
        if outside <= inside:
            errors.append("outside_diameter must exceed the calibrated inside_diameter.")
        if length <= 0:
            errors.append("length must be greater than zero.")
        if radial_wall < minimum_wall:
            errors.append(
                f"Radial wall {radial_wall} mm is below the required {minimum_wall} mm "
                "(at least two nozzle diameters)."
            )
        if chamfer < 0 or chamfer >= min(radial_wall, length / Decimal("2")):
            if chamfer != 0:
                errors.append("chamfer must be smaller than both radial wall and half the length.")

        split = bool(values["split"])
        split_width = Decimal("0")
        if split:
            if "split_width" not in values:
                errors.append("split_width is required when split is enabled.")
            else:
                split_width = input_length_mm(
                    values["split_width"], context.input_units, "split_width"
                )
                if split_width <= 0 or split_width >= outside:
                    errors.append("split_width must be positive and smaller than outside_diameter.")

        if context.generation_mode not in self.metadata.supported_artifacts:
            errors.append(f"Unsupported generation mode: {context.generation_mode}")
        if context.generation_mode == "fit_coupon" and context.coupon_parameter not in {
            "inside_diameter",
            None,
        }:
            errors.append("Bushing fit coupons support only inside_diameter.")
        if errors:
            raise GeneratorValidationError(errors)

        resolved = {
            "inside_diameter": inside,
            "outside_diameter": outside,
            "length": length,
            "chamfer": chamfer,
            "fit_class": fit_class,
            "split": split,
            "split_width": split_width,
            "minimum_wall_thickness": minimum_wall,
        }
        warnings: list[str] = []
        if context.generation_mode == "fit_coupon":
            offsets = context.coupon_offsets_mm or (Decimal("0"),)
            candidate_diameters = tuple(inside + offset for offset in offsets)
            if any(diameter <= 0 for diameter in candidate_diameters):
                raise GeneratorValidationError(
                    ["Every bushing coupon candidate diameter must remain positive."]
                )
            margin = max(context.nozzle_diameter_mm * Decimal("5"), Decimal("2"))
            coupon_cell = max(candidate_diameters) + (margin * Decimal("2"))
            coupon_width = coupon_cell * Decimal(len(candidate_diameters))
            coupon_depth = coupon_cell
            coupon_thickness = max(context.nozzle_diameter_mm * Decimal("5"), Decimal("2"))
            parameter_block = "\n".join(
                [
                    "coupon_hole_diameters = ["
                    + ", ".join(scad_number(value) for value in candidate_diameters)
                    + "];",
                    f"coupon_cell = {scad_number(coupon_cell)};",
                    f"coupon_width = {scad_number(coupon_width)};",
                    f"coupon_depth = {scad_number(coupon_depth)};",
                    f"coupon_thickness = {scad_number(coupon_thickness)};",
                ]
            )
            geometry_block = """module generated_artifact() {
    difference() {
        translate([-coupon_width / 2, -coupon_depth / 2, 0])
            cube([coupon_width, coupon_depth, coupon_thickness]);
        for (index = [0 : len(coupon_hole_diameters) - 1])
            translate([
                -coupon_width / 2 + coupon_cell / 2 + index * coupon_cell,
                0,
                -epsilon
            ])
                cylinder(
                    h = coupon_thickness + 2 * epsilon,
                    d = coupon_hole_diameters[index]
                );
    }
}"""
            bounds = scaled_bounds(
                (coupon_width, coupon_depth, coupon_thickness), context
            )
            resolved["coupon_candidate_diameters"] = candidate_diameters
            warnings.append(
                "Fit coupon geometry is computationally checked only; a printed result must be recorded manually."
            )
            artifact_kind = "fit_coupon"
        else:
            parameter_block = "\n".join(
                [
                    f"inside_diameter = {scad_number(inside)};",
                    f"outside_diameter = {scad_number(outside)};",
                    f"part_length = {scad_number(length)};",
                    f"edge_chamfer = {scad_number(chamfer)};",
                    f"split_enabled = {'true' if split else 'false'};",
                    f"split_width = {scad_number(split_width)};",
                ]
            )
            geometry_block = """module bushing_body() {
    assert(outside_diameter > inside_diameter, "outside diameter must exceed inside diameter");
    if (edge_chamfer > 0) {
        rotate_extrude(convexity = 10)
            polygon(points = [
                [inside_diameter / 2, 0],
                [outside_diameter / 2 - edge_chamfer, 0],
                [outside_diameter / 2, edge_chamfer],
                [outside_diameter / 2, part_length - edge_chamfer],
                [outside_diameter / 2 - edge_chamfer, part_length],
                [inside_diameter / 2, part_length]
            ]);
    } else {
        difference() {
            cylinder(h = part_length, d = outside_diameter);
            translate([0, 0, -epsilon])
                cylinder(h = part_length + 2 * epsilon, d = inside_diameter);
        }
    }
}

module generated_artifact() {
    difference() {
        bushing_body();
        if (split_enabled)
            translate([0, -split_width / 2, -epsilon])
                cube([outside_diameter / 2 + epsilon, split_width, part_length + 2 * epsilon]);
    }
}"""
            x_extent = (
                _split_outer_extent_x(outside, split_width) if split else outside
            )
            bounds = scaled_bounds((x_extent, outside, length), context)
            artifact_kind = "full_part"

        source = load_template(__file__).substitute(
            generator_version=self.metadata.version,
            artifact_kind=artifact_kind,
            parameter_block=parameter_block,
            geometry_block=geometry_block,
            scale_vector=scale_statement(context),
            facets=SCAD_FACETS,
        )
        return GenerationResult(
            source=source,
            expected_bounds_mm=bounds,
            resolved_parameters_mm=resolved,
            nominal_protected_dimensions_mm={
                "inside_diameter": nominal_inside,
                "outside_diameter": outside,
                "length": length,
            },
            warnings=tuple(warnings),
            expected_body_count=self.metadata.expected_body_count,
            artifact_kind=artifact_kind,
        )
