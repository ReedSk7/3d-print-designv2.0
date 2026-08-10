"""Deterministic straight or tapered round adapter generator."""

from __future__ import annotations

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


DISABLED_FEATURE = {"enabled": False}


class RoundAdapterGenerator(PartGenerator):
    metadata = GeneratorMetadata(
        generator_id="round_adapter",
        version="1.0.0",
        name="Round Adapter",
        description="Straight or tapered hollow adapter with optional bead and mounting flange.",
    )
    defaults = {
        "transition": "tapered",
        "fit_class": "nominal",
        "hose_retaining_bead": DISABLED_FEATURE,
        "mounting_flange": DISABLED_FEATURE,
    }
    _end_schema = {
        "type": "object",
        "required": ["diameter_type", "diameter"],
        "properties": {
            "diameter_type": {"type": "string", "enum": ["inside", "outside"]},
            "diameter": {"type": "number", "exclusiveMinimum": 0},
        },
        "additionalProperties": False,
    }
    parameter_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["end_a", "end_b", "length", "wall_thickness", "transition"],
        "properties": {
            "end_a": _end_schema,
            "end_b": _end_schema,
            "length": {"type": "number", "exclusiveMinimum": 0},
            "wall_thickness": {"type": "number", "exclusiveMinimum": 0},
            "transition": {"type": "string", "enum": ["straight", "tapered"]},
            "fit_class": {
                "type": "string",
                "enum": ["nominal", "slip", "press"],
                "default": "nominal",
            },
            "hose_retaining_bead": {
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["enabled"],
                        "properties": {"enabled": {"const": False}},
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["enabled", "height", "width"],
                        "properties": {
                            "enabled": {"const": True},
                            "height": {"type": "number", "exclusiveMinimum": 0},
                            "width": {"type": "number", "exclusiveMinimum": 0},
                        },
                        "additionalProperties": False,
                    },
                ],
                "default": {"enabled": False},
            },
            "mounting_flange": {
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["enabled"],
                        "properties": {"enabled": {"const": False}},
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["enabled", "outer_diameter", "thickness"],
                        "properties": {
                            "enabled": {"const": True},
                            "outer_diameter": {"type": "number", "exclusiveMinimum": 0},
                            "thickness": {"type": "number", "exclusiveMinimum": 0},
                            "screw_hole_pattern": {
                                "oneOf": [
                                    {
                                        "type": "object",
                                        "required": ["enabled"],
                                        "properties": {"enabled": {"const": False}},
                                        "additionalProperties": False,
                                    },
                                    {
                                        "type": "object",
                                        "required": [
                                            "enabled",
                                            "count",
                                            "bolt_circle_diameter",
                                            "hole_diameter",
                                        ],
                                        "properties": {
                                            "enabled": {"const": True},
                                            "count": {"type": "integer", "minimum": 2, "maximum": 16},
                                            "bolt_circle_diameter": {
                                                "type": "number",
                                                "exclusiveMinimum": 0,
                                            },
                                            "hole_diameter": {
                                                "type": "number",
                                                "exclusiveMinimum": 0,
                                            },
                                        },
                                        "additionalProperties": False,
                                    },
                                ]
                            },
                        },
                        "additionalProperties": False,
                    },
                ],
                "default": {"enabled": False},
            },
        },
        "additionalProperties": False,
    }

    def _resolve_end(
        self,
        end: Mapping[str, Any],
        wall: Decimal,
        context: GenerationContext,
        label: str,
    ) -> tuple[Decimal, Decimal, Decimal, str]:
        diameter_type = str(end["diameter_type"])
        nominal = input_length_mm(end["diameter"], context.input_units, f"{label}.diameter")
        if diameter_type == "inside":
            inside = diameter_with_calibration(
                nominal, interface="hole", fit_class=context.fit_class, context=context
            )
            if context.accepted_coupon_parameter == f"{label}.diameter":
                inside += context.accepted_coupon_offset_mm
            outside = inside + (Decimal("2") * wall)
        elif diameter_type == "outside":
            outside = diameter_with_calibration(
                nominal, interface="shaft", fit_class=context.fit_class, context=context
            )
            if context.accepted_coupon_parameter == f"{label}.diameter":
                outside += context.accepted_coupon_offset_mm
            inside = outside - (Decimal("2") * wall)
        else:
            raise GeneratorValidationError(
                [f"{label}.diameter_type must be 'inside' or 'outside'."]
            )
        return inside, outside, nominal, diameter_type

    def generate(
        self, parameters: Mapping[str, Any], context: GenerationContext
    ) -> GenerationResult:
        values: dict[str, Any] = {
            "transition": "tapered",
            "fit_class": "nominal",
            "hose_retaining_bead": {"enabled": False},
            "mounting_flange": {"enabled": False},
        }
        values.update(parameters)
        fit_class = str(values["fit_class"])
        if fit_class != context.fit_class:
            raise GeneratorValidationError(
                ["round_adapter fit_class must match the generation context fit class."]
            )
        try:
            wall = input_length_mm(
                values["wall_thickness"], context.input_units, "wall_thickness"
            )
            length = input_length_mm(values["length"], context.input_units, "length")
            inside_a, outside_a, nominal_a, type_a = self._resolve_end(
                values["end_a"], wall, context, "end_a"
            )
            inside_b, outside_b, nominal_b, type_b = self._resolve_end(
                values["end_b"], wall, context, "end_b"
            )
        except KeyError as exc:
            raise GeneratorValidationError(
                [f"Missing round_adapter parameter: {exc.args[0]}"]
            ) from exc

        errors: list[str] = []
        minimum_wall = context.nozzle_diameter_mm * Decimal("2")
        if wall < minimum_wall:
            errors.append(
                f"wall_thickness {wall} mm is below two nozzle diameters ({minimum_wall} mm)."
            )
        if length <= 0:
            errors.append("length must be greater than zero.")
        if min(inside_a, inside_b) <= 0:
            errors.append("Resolved inside diameters must remain positive after wall and calibration.")

        transition = str(values["transition"])
        if transition == "straight" and (inside_a != inside_b or outside_a != outside_b):
            errors.append("straight transition requires equal resolved end diameters.")
        if transition not in {"straight", "tapered"}:
            errors.append("transition must be 'straight' or 'tapered'.")

        bead = values.get("hose_retaining_bead") or {"enabled": False}
        bead_enabled = bool(bead.get("enabled", False))
        bead_height = Decimal("0")
        bead_width = Decimal("0")
        if bead_enabled:
            try:
                bead_height = input_length_mm(
                    bead["height"], context.input_units, "hose_retaining_bead.height"
                )
                bead_width = input_length_mm(
                    bead["width"], context.input_units, "hose_retaining_bead.width"
                )
            except KeyError as exc:
                errors.append(f"Missing hose-retaining bead parameter: {exc.args[0]}")
            if bead_width > length:
                errors.append("hose-retaining bead width cannot exceed adapter length.")

        flange = values.get("mounting_flange") or {"enabled": False}
        flange_enabled = bool(flange.get("enabled", False))
        flange_outer = Decimal("0")
        flange_thickness = Decimal("0")
        holes_enabled = False
        hole_count = 0
        bolt_circle = Decimal("0")
        nominal_hole = Decimal("0")
        hole_diameter = Decimal("0")
        if flange_enabled:
            try:
                flange_outer = input_length_mm(
                    flange["outer_diameter"], context.input_units, "mounting_flange.outer_diameter"
                )
                flange_thickness = input_length_mm(
                    flange["thickness"], context.input_units, "mounting_flange.thickness"
                )
            except KeyError as exc:
                errors.append(f"Missing mounting flange parameter: {exc.args[0]}")
            if flange_outer <= outside_a:
                errors.append("mounting flange outer diameter must exceed end A outside diameter.")
            if flange_thickness <= 0 or flange_thickness > length:
                errors.append("mounting flange thickness must be positive and no greater than length.")

            pattern = flange.get("screw_hole_pattern") or {"enabled": False}
            holes_enabled = bool(pattern.get("enabled", False))
            if holes_enabled:
                try:
                    hole_count = int(pattern["count"])
                    bolt_circle = input_length_mm(
                        pattern["bolt_circle_diameter"],
                        context.input_units,
                        "mounting_flange.screw_hole_pattern.bolt_circle_diameter",
                    )
                    nominal_hole = input_length_mm(
                        pattern["hole_diameter"],
                        context.input_units,
                        "mounting_flange.screw_hole_pattern.hole_diameter",
                    )
                    hole_diameter = diameter_with_calibration(
                        nominal_hole,
                        interface="hole",
                        fit_class=context.fit_class,
                        context=context,
                    )
                    if hole_diameter <= 0:
                        errors.append(
                            "Resolved screw-hole diameter must remain positive after calibration."
                        )
                except KeyError as exc:
                    errors.append(f"Missing screw-hole pattern parameter: {exc.args[0]}")
                if hole_count < 2:
                    errors.append("screw-hole pattern requires at least two holes.")
                edge_wall = minimum_wall
                if (bolt_circle + hole_diameter) / Decimal("2") + edge_wall > flange_outer / Decimal("2"):
                    errors.append("screw holes violate the flange outer edge wall requirement.")
                if (bolt_circle - hole_diameter) / Decimal("2") - edge_wall < outside_a / Decimal("2"):
                    errors.append("screw holes overlap the adapter body or its minimum wall.")

        supported_coupon_parameters = {"end_a.diameter", "end_b.diameter"}
        coupon_parameter = context.coupon_parameter or "end_a.diameter"
        if context.generation_mode == "fit_coupon" and coupon_parameter not in supported_coupon_parameters:
            errors.append(
                "round_adapter fit coupon parameter must be end_a.diameter or end_b.diameter."
            )
        if (
            context.accepted_coupon_parameter is not None
            and context.accepted_coupon_parameter not in supported_coupon_parameters
        ):
            errors.append(
                "round_adapter accepted fit coupon parameter must be end_a.diameter or end_b.diameter."
            )
        if context.generation_mode not in self.metadata.supported_artifacts:
            errors.append(f"Unsupported generation mode: {context.generation_mode}")
        if errors:
            raise GeneratorValidationError(errors)

        resolved = {
            "end_a": {"inside_diameter": inside_a, "outside_diameter": outside_a, "diameter_type": type_a},
            "end_b": {"inside_diameter": inside_b, "outside_diameter": outside_b, "diameter_type": type_b},
            "length": length,
            "wall_thickness": wall,
            "transition": transition,
            "fit_class": fit_class,
            "hose_retaining_bead": {
                "enabled": bead_enabled,
                "height": bead_height,
                "width": bead_width,
            },
            "mounting_flange": {
                "enabled": flange_enabled,
                "outer_diameter": flange_outer,
                "thickness": flange_thickness,
                "screw_hole_pattern": {
                    "enabled": holes_enabled,
                    "count": hole_count,
                    "bolt_circle_diameter": bolt_circle,
                    "hole_diameter": hole_diameter,
                },
            },
        }
        protected = {
            "end_a.diameter": nominal_a,
            "end_b.diameter": nominal_b,
            "length": length,
        }
        if flange_enabled:
            protected["mounting_flange.outer_diameter"] = flange_outer
            if holes_enabled:
                protected[
                    "mounting_flange.screw_hole_pattern.bolt_circle_diameter"
                ] = bolt_circle
                protected["mounting_flange.screw_hole_pattern.hole_diameter"] = nominal_hole

        warnings: list[str] = []
        if context.generation_mode == "fit_coupon":
            use_a = coupon_parameter == "end_a.diameter"
            inside = inside_a if use_a else inside_b
            outside = outside_a if use_a else outside_b
            diameter_type = type_a if use_a else type_b
            offsets = context.coupon_offsets_mm or (Decimal("0"),)
            base_interface_diameter = inside if diameter_type == "inside" else outside
            candidate_diameters = tuple(
                base_interface_diameter + offset for offset in offsets
            )
            if any(diameter <= 0 for diameter in candidate_diameters):
                raise GeneratorValidationError(
                    ["Every round-adapter coupon candidate diameter must remain positive."]
                )
            margin = max(context.nozzle_diameter_mm * Decimal("5"), Decimal("2"))
            coupon_height = max(context.nozzle_diameter_mm * Decimal("8"), Decimal("3"))
            base_thickness = max(context.nozzle_diameter_mm * Decimal("3"), Decimal("1.2"))
            coupon_cell = max(candidate_diameters) + Decimal("2") * margin
            coupon_width = coupon_cell * Decimal(len(candidate_diameters))
            coupon_depth = coupon_cell
            if diameter_type == "inside":
                parameter_block = "\n".join(
                    [
                        "coupon_diameters = ["
                        + ", ".join(scad_number(value) for value in candidate_diameters)
                        + "];",
                        f"coupon_cell = {scad_number(coupon_cell)};",
                        f"coupon_width = {scad_number(coupon_width)};",
                        f"coupon_depth = {scad_number(coupon_depth)};",
                        f"coupon_height = {scad_number(coupon_height)};",
                    ]
                )
                geometry_block = """module generated_artifact() {
    difference() {
        translate([-coupon_width / 2, -coupon_depth / 2, 0])
            cube([coupon_width, coupon_depth, coupon_height]);
        for (index = [0 : len(coupon_diameters) - 1])
            translate([
                -coupon_width / 2 + coupon_cell / 2 + index * coupon_cell,
                0,
                -epsilon
            ])
                cylinder(h = coupon_height + 2 * epsilon, d = coupon_diameters[index]);
    }
}"""
                raw_bounds = (coupon_width, coupon_depth, coupon_height)
            else:
                parameter_block = "\n".join(
                    [
                        "coupon_diameters = ["
                        + ", ".join(scad_number(value) for value in candidate_diameters)
                        + "];",
                        f"coupon_cell = {scad_number(coupon_cell)};",
                        f"coupon_width = {scad_number(coupon_width)};",
                        f"coupon_depth = {scad_number(coupon_depth)};",
                        f"base_thickness = {scad_number(base_thickness)};",
                        f"coupon_height = {scad_number(coupon_height)};",
                    ]
                )
                geometry_block = """module generated_artifact() {
    union() {
        translate([-coupon_width / 2, -coupon_depth / 2, 0])
            cube([coupon_width, coupon_depth, base_thickness]);
        for (index = [0 : len(coupon_diameters) - 1])
            translate([
                -coupon_width / 2 + coupon_cell / 2 + index * coupon_cell,
                0,
                0
            ])
                cylinder(
                    h = base_thickness + coupon_height,
                    d = coupon_diameters[index]
                );
    }
}"""
                raw_bounds = (
                    coupon_width,
                    coupon_depth,
                    base_thickness + coupon_height,
                )
            artifact_kind = "fit_coupon"
            bounds = scaled_bounds(raw_bounds, context)
            warnings.append(
                "Fit coupon geometry is computationally checked only; a printed result must be recorded manually."
            )
            resolved["coupon_candidate_diameters"] = candidate_diameters
        else:
            bead_outer = outside_b + Decimal("2") * bead_height if bead_enabled else Decimal("0")
            overall_diameter = max(outside_a, outside_b, bead_outer, flange_outer)
            parameter_block = "\n".join(
                [
                    f"inside_a = {scad_number(inside_a)};",
                    f"outside_a = {scad_number(outside_a)};",
                    f"inside_b = {scad_number(inside_b)};",
                    f"outside_b = {scad_number(outside_b)};",
                    f"adapter_length = {scad_number(length)};",
                    f"bead_enabled = {'true' if bead_enabled else 'false'};",
                    f"bead_height = {scad_number(bead_height)};",
                    f"bead_width = {scad_number(bead_width)};",
                    f"flange_enabled = {'true' if flange_enabled else 'false'};",
                    f"flange_outer_diameter = {scad_number(flange_outer)};",
                    f"flange_thickness = {scad_number(flange_thickness)};",
                    f"holes_enabled = {'true' if holes_enabled else 'false'};",
                    f"hole_count = {hole_count};",
                    f"bolt_circle_diameter = {scad_number(bolt_circle)};",
                    f"mounting_hole_diameter = {scad_number(hole_diameter)};",
                ]
            )
            geometry_block = """module outside_solid() {
    union() {
        cylinder(h = adapter_length, d1 = outside_a, d2 = outside_b);
        if (bead_enabled)
            translate([0, 0, adapter_length - bead_width])
                cylinder(h = bead_width, d = outside_b + 2 * bead_height);
        if (flange_enabled)
            cylinder(h = flange_thickness, d = flange_outer_diameter);
    }
}

module generated_artifact() {
    assert(outside_a > inside_a && outside_b > inside_b, "adapter walls must be positive");
    difference() {
        outside_solid();
        translate([0, 0, -epsilon])
            cylinder(h = adapter_length + 2 * epsilon, d1 = inside_a, d2 = inside_b);
        if (flange_enabled && holes_enabled)
            for (index = [0 : hole_count - 1])
                rotate([0, 0, index * 360 / hole_count])
                    translate([bolt_circle_diameter / 2, 0, -epsilon])
                        cylinder(h = flange_thickness + 2 * epsilon, d = mounting_hole_diameter);
    }
}"""
            artifact_kind = "full_part"
            bounds = scaled_bounds((overall_diameter, overall_diameter, length), context)

        source = load_template(__file__).substitute(
            generator_version=self.metadata.version,
            artifact_kind=artifact_kind,
            parameter_block=parameter_block,
            geometry_block=geometry_block,
            scale_vector=scale_statement(context),
        )
        return GenerationResult(
            source=source,
            expected_bounds_mm=bounds,
            resolved_parameters_mm=resolved,
            nominal_protected_dimensions_mm=protected,
            warnings=tuple(warnings),
            expected_body_count=self.metadata.expected_body_count,
            artifact_kind=artifact_kind,
        )
