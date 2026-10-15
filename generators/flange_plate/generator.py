"""Deterministic rectangular flange plate generator."""

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


def _rounded_rectangle_signed_distance(
    x: Decimal,
    y: Decimal,
    width: Decimal,
    height: Decimal,
    corner_radius: Decimal,
) -> Decimal:
    """Signed 2D distance to a centered rounded rectangle (negative inside)."""

    qx = abs(x) - (width / Decimal("2") - corner_radius)
    qy = abs(y) - (height / Decimal("2") - corner_radius)
    outside_x = max(qx, Decimal("0"))
    outside_y = max(qy, Decimal("0"))
    outside_distance = (outside_x * outside_x + outside_y * outside_y).sqrt()
    inside_distance = min(max(qx, qy), Decimal("0"))
    return outside_distance + inside_distance - corner_radius


def _distance_to_center_rectangle(
    x: Decimal,
    y: Decimal,
    opening_width: Decimal,
    opening_height: Decimal,
) -> Decimal:
    dx = max(abs(x) - opening_width / Decimal("2"), Decimal("0"))
    dy = max(abs(y) - opening_height / Decimal("2"), Decimal("0"))
    return (dx * dx + dy * dy).sqrt()


class FlangePlateGenerator(PartGenerator):
    metadata = GeneratorMetadata(
        generator_id="flange_plate",
        version="1.0.0",
        name="Flange Plate",
        description="Rounded rectangular plate with center opening and mounting holes.",
        protected_interfaces=(
            "center_opening.diameter",
            "center_opening.width",
            "center_opening.height",
            "mounting_hole_diameter",
        ),
        fit_coupon_interfaces=("mounting_hole_diameter",),
    )

    def applicable_protected_interfaces(
        self, parameters: Mapping[str, Any]
    ) -> tuple[str, ...]:
        interfaces: list[str] = []
        opening = parameters.get("center_opening")
        if isinstance(opening, Mapping):
            if opening.get("type") == "circle":
                interfaces.append("center_opening.diameter")
            elif opening.get("type") == "rectangle":
                interfaces.extend(("center_opening.width", "center_opening.height"))
        pattern = parameters.get("mounting_hole_pattern")
        if isinstance(pattern, Mapping) and pattern.get("type") != "none":
            interfaces.append("mounting_hole_diameter")
        return tuple(interfaces)

    def applicable_coupon_interfaces(
        self, parameters: Mapping[str, Any]
    ) -> tuple[str, ...]:
        return (
            ("mounting_hole_diameter",)
            if "mounting_hole_diameter"
            in self.applicable_protected_interfaces(parameters)
            else ()
        )

    defaults = {"hole_finish": {"type": "none"}, "fit_class": "nominal"}
    parameter_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": [
            "outer_width",
            "outer_height",
            "plate_thickness",
            "center_opening",
            "corner_radius",
            "mounting_hole_pattern",
            "mounting_hole_diameter",
        ],
        "properties": {
            "outer_width": {"type": "number", "exclusiveMinimum": 0},
            "outer_height": {"type": "number", "exclusiveMinimum": 0},
            "plate_thickness": {"type": "number", "exclusiveMinimum": 0},
            "corner_radius": {"type": "number", "minimum": 0},
            "center_opening": {
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["type"],
                        "properties": {"type": {"const": "none"}},
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["type", "diameter"],
                        "properties": {
                            "type": {"const": "circle"},
                            "diameter": {"type": "number", "exclusiveMinimum": 0},
                        },
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["type", "width", "height"],
                        "properties": {
                            "type": {"const": "rectangle"},
                            "width": {"type": "number", "exclusiveMinimum": 0},
                            "height": {"type": "number", "exclusiveMinimum": 0},
                        },
                        "additionalProperties": False,
                    },
                ]
            },
            "mounting_hole_pattern": {
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["type"],
                        "properties": {"type": {"const": "none"}},
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["type", "x_spacing", "y_spacing"],
                        "properties": {
                            "type": {"const": "rectangular"},
                            "x_spacing": {"type": "number", "exclusiveMinimum": 0},
                            "y_spacing": {"type": "number", "exclusiveMinimum": 0},
                        },
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["type", "count", "bolt_circle_diameter"],
                        "properties": {
                            "type": {"const": "bolt_circle"},
                            "count": {"type": "integer", "minimum": 2, "maximum": 24},
                            "bolt_circle_diameter": {
                                "type": "number",
                                "exclusiveMinimum": 0,
                            },
                        },
                        "additionalProperties": False,
                    },
                ]
            },
            "mounting_hole_diameter": {"type": "number", "exclusiveMinimum": 0},
            "fit_class": {
                "type": "string",
                "enum": ["nominal", "slip", "press"],
                "default": "nominal",
            },
            "hole_finish": {
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["type"],
                        "properties": {"type": {"const": "none"}},
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["type", "diameter", "depth"],
                        "properties": {
                            "type": {"const": "counterbore"},
                            "diameter": {"type": "number", "exclusiveMinimum": 0},
                            "depth": {"type": "number", "exclusiveMinimum": 0},
                        },
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "required": ["type", "head_diameter", "angle"],
                        "properties": {
                            "type": {"const": "countersink"},
                            "head_diameter": {"type": "number", "exclusiveMinimum": 0},
                            "angle": {"type": "number", "minimum": 60, "maximum": 120},
                        },
                        "additionalProperties": False,
                    },
                ],
                "default": {"type": "none"},
            },
        },
        "additionalProperties": False,
    }

    def generate(
        self, parameters: Mapping[str, Any], context: GenerationContext
    ) -> GenerationResult:
        values = {"hole_finish": {"type": "none"}, "fit_class": "nominal"}
        values.update(parameters)
        fit_class = str(values["fit_class"])
        if fit_class != context.fit_class:
            raise GeneratorValidationError(
                ["flange_plate fit_class must match the generation context fit class."]
            )
        try:
            width = input_length_mm(values["outer_width"], context.input_units, "outer_width")
            height = input_length_mm(values["outer_height"], context.input_units, "outer_height")
            thickness = input_length_mm(
                values["plate_thickness"], context.input_units, "plate_thickness"
            )
            corner_radius = input_length_mm(
                values["corner_radius"], context.input_units, "corner_radius"
            )
            nominal_hole = input_length_mm(
                values["mounting_hole_diameter"],
                context.input_units,
                "mounting_hole_diameter",
            )
        except KeyError as exc:
            raise GeneratorValidationError(
                [f"Missing flange_plate parameter: {exc.args[0]}"]
            ) from exc

        errors: list[str] = []
        minimum_wall = context.nozzle_diameter_mm * Decimal("2")
        if thickness < minimum_wall:
            errors.append(
                f"plate_thickness {thickness} mm is below two nozzle diameters ({minimum_wall} mm)."
            )
        if corner_radius < 0 or corner_radius > min(width, height) / Decimal("2"):
            errors.append("corner_radius must fit within half the shorter plate side.")

        opening = values["center_opening"]
        opening_type = str(opening["type"])
        opening_values: dict[str, Decimal] = {}
        protected: dict[str, Decimal] = {
            "outer_width": width,
            "outer_height": height,
            "plate_thickness": thickness,
        }
        if opening_type == "circle":
            nominal_opening = input_length_mm(
                opening["diameter"], context.input_units, "center_opening.diameter"
            )
            opening_diameter = diameter_with_calibration(
                nominal_opening,
                interface="hole",
                fit_class=context.fit_class,
                context=context,
            )
            opening_values["diameter"] = opening_diameter
            protected["center_opening.diameter"] = nominal_opening
            if opening_diameter <= 0:
                errors.append(
                    "Resolved circular center-opening diameter must remain positive after calibration."
                )
            if opening_diameter + Decimal("2") * minimum_wall >= min(width, height):
                errors.append("Circular center opening leaves less than the minimum plate wall.")
        elif opening_type == "rectangle":
            opening_width = input_length_mm(
                opening["width"], context.input_units, "center_opening.width"
            )
            opening_height = input_length_mm(
                opening["height"], context.input_units, "center_opening.height"
            )
            opening_values.update(width=opening_width, height=opening_height)
            protected["center_opening.width"] = opening_width
            protected["center_opening.height"] = opening_height
            if opening_width + Decimal("2") * minimum_wall >= width:
                errors.append("Rectangular center opening leaves insufficient side wall.")
            if opening_height + Decimal("2") * minimum_wall >= height:
                errors.append("Rectangular center opening leaves insufficient top/bottom wall.")
            opening_corner_distance = _rounded_rectangle_signed_distance(
                opening_width / Decimal("2"),
                opening_height / Decimal("2"),
                width,
                height,
                corner_radius,
            )
            if opening_corner_distance + minimum_wall > 0:
                errors.append(
                    "Rectangular center opening violates the rounded-corner minimum wall."
                )
        elif opening_type != "none":
            errors.append("center_opening.type must be none, circle, or rectangle.")

        pattern = values["mounting_hole_pattern"]
        pattern_type = str(pattern["type"])
        pattern_values: dict[str, Any] = {"type": pattern_type}
        if pattern_type == "rectangular":
            x_spacing = input_length_mm(
                pattern["x_spacing"], context.input_units, "mounting_hole_pattern.x_spacing"
            )
            y_spacing = input_length_mm(
                pattern["y_spacing"], context.input_units, "mounting_hole_pattern.y_spacing"
            )
            pattern_values.update(x_spacing=x_spacing, y_spacing=y_spacing, count=4)
            protected["mounting_hole_pattern.x_spacing"] = x_spacing
            protected["mounting_hole_pattern.y_spacing"] = y_spacing
        elif pattern_type == "bolt_circle":
            bolt_circle = input_length_mm(
                pattern["bolt_circle_diameter"],
                context.input_units,
                "mounting_hole_pattern.bolt_circle_diameter",
            )
            count = int(pattern["count"])
            pattern_values.update(bolt_circle_diameter=bolt_circle, count=count)
            protected["mounting_hole_pattern.bolt_circle_diameter"] = bolt_circle
        elif pattern_type == "none":
            pattern_values["count"] = 0
        else:
            errors.append("mounting_hole_pattern.type must be none, rectangular, or bolt_circle.")

        mounting_hole = diameter_with_calibration(
            nominal_hole,
            interface="hole",
            fit_class=context.fit_class,
            context=context,
        )
        if context.accepted_coupon_parameter is not None:
            if context.accepted_coupon_parameter != "mounting_hole_diameter":
                errors.append(
                    "flange_plate accepted fit coupons support only mounting_hole_diameter."
                )
            else:
                mounting_hole += context.accepted_coupon_offset_mm
        protected["mounting_hole_diameter"] = nominal_hole
        if mounting_hole <= 0:
            errors.append(
                "Resolved mounting-hole diameter must remain positive after calibration."
            )

        finish = values.get("hole_finish") or {"type": "none"}
        finish_type = str(finish["type"])
        finish_diameter = mounting_hole
        finish_depth = Decimal("0")
        finish_angle = Decimal("0")
        if finish_type == "counterbore":
            finish_diameter = input_length_mm(
                finish["diameter"], context.input_units, "hole_finish.diameter"
            )
            finish_depth = input_length_mm(
                finish["depth"], context.input_units, "hole_finish.depth"
            )
            protected["hole_finish.diameter"] = finish_diameter
            protected["hole_finish.depth"] = finish_depth
        elif finish_type == "countersink":
            finish_diameter = input_length_mm(
                finish["head_diameter"], context.input_units, "hole_finish.head_diameter"
            )
            finish_angle = Decimal(str(finish["angle"]))
            half_angle_radians = math.radians(float(finish_angle) / 2)
            finish_depth = (
                (finish_diameter - mounting_hole)
                / (Decimal("2") * Decimal(str(math.tan(half_angle_radians))))
            )
            protected["hole_finish.head_diameter"] = finish_diameter
        elif finish_type != "none":
            errors.append("hole_finish.type must be none, counterbore, or countersink.")

        if finish_diameter < mounting_hole:
            errors.append("hole-finish diameter cannot be smaller than the through-hole diameter.")
        if finish_depth >= thickness and finish_type != "none":
            errors.append("hole-finish depth must be smaller than plate thickness.")
        edge_diameter = max(mounting_hole, finish_diameter)
        edge_clearance = edge_diameter / Decimal("2") + minimum_wall
        hole_centers: list[tuple[Decimal, Decimal]] = []
        if pattern_type == "rectangular":
            half_x = pattern_values["x_spacing"] / Decimal("2")
            half_y = pattern_values["y_spacing"] / Decimal("2")
            hole_centers = [
                (x, y)
                for x in (-half_x, half_x)
                for y in (-half_y, half_y)
            ]
        elif pattern_type == "bolt_circle":
            radius = pattern_values["bolt_circle_diameter"] / Decimal("2")
            for index in range(pattern_values["count"]):
                angle = math.radians(index * 360 / pattern_values["count"])
                hole_centers.append(
                    (
                        radius * Decimal(str(math.cos(angle))),
                        radius * Decimal(str(math.sin(angle))),
                    )
                )

        for hole_x, hole_y in hole_centers:
            boundary_distance = _rounded_rectangle_signed_distance(
                hole_x, hole_y, width, height, corner_radius
            )
            if boundary_distance + edge_clearance > 0:
                errors.append(
                    "Mounting-hole pattern violates the rounded plate edge wall."
                )
                break

        for hole_x, hole_y in hole_centers:
            if opening_type == "circle":
                center_distance = (hole_x * hole_x + hole_y * hole_y).sqrt()
                required_distance = (
                    opening_values["diameter"] / Decimal("2") + edge_clearance
                )
            elif opening_type == "rectangle":
                center_distance = _distance_to_center_rectangle(
                    hole_x,
                    hole_y,
                    opening_values["width"],
                    opening_values["height"],
                )
                required_distance = edge_clearance
            else:
                continue
            if center_distance < required_distance:
                errors.append(
                    "Mounting-hole pattern overlaps the center opening or its minimum wall."
                )
                break

        coupon_parameter = context.coupon_parameter or "mounting_hole_diameter"
        if context.generation_mode == "fit_coupon" and coupon_parameter != "mounting_hole_diameter":
            errors.append("flange_plate fit coupons support only mounting_hole_diameter.")
        if context.generation_mode not in self.metadata.supported_artifacts:
            errors.append(f"Unsupported generation mode: {context.generation_mode}")
        if errors:
            raise GeneratorValidationError(errors)

        resolved = {
            "outer_width": width,
            "outer_height": height,
            "plate_thickness": thickness,
            "corner_radius": corner_radius,
            "center_opening": {"type": opening_type, **opening_values},
            "mounting_hole_pattern": pattern_values,
            "mounting_hole_diameter": mounting_hole,
            "hole_finish": {
                "type": finish_type,
                "diameter": finish_diameter,
                "depth": finish_depth,
                "angle": finish_angle,
            },
            "fit_class": fit_class,
        }
        warnings: list[str] = []
        if context.generation_mode == "fit_coupon":
            offsets = context.coupon_offsets_mm or (Decimal("0"),)
            candidate_diameters = tuple(mounting_hole + offset for offset in offsets)
            if any(diameter <= 0 for diameter in candidate_diameters):
                raise GeneratorValidationError(
                    ["Every flange coupon candidate diameter must remain positive."]
                )
            margin = max(context.nozzle_diameter_mm * Decimal("5"), Decimal("2"))
            coupon_cell = max(max(candidate_diameters), finish_diameter) + Decimal("2") * margin
            coupon_width = coupon_cell * Decimal(len(candidate_diameters))
            coupon_depth = coupon_cell
            parameter_block = "\n".join(
                [
                    "coupon_diameters = ["
                    + ", ".join(scad_number(value) for value in candidate_diameters)
                    + "];",
                    f"coupon_cell = {scad_number(coupon_cell)};",
                    f"coupon_width = {scad_number(coupon_width)};",
                    f"coupon_depth = {scad_number(coupon_depth)};",
                    f"plate_thickness = {scad_number(thickness)};",
                    f"finish_type = \"{finish_type}\";",
                    f"finish_diameter = {scad_number(finish_diameter)};",
                    f"finish_depth = {scad_number(finish_depth)};",
                ]
            )
            geometry_block = """module generated_artifact() {
    difference() {
        translate([-coupon_width / 2, -coupon_depth / 2, 0])
            cube([coupon_width, coupon_depth, plate_thickness]);
        for (index = [0 : len(coupon_diameters) - 1]) {
            x = -coupon_width / 2 + coupon_cell / 2 + index * coupon_cell;
            translate([x, 0, -epsilon])
                cylinder(h = plate_thickness + 2 * epsilon, d = coupon_diameters[index]);
            if (finish_type == "counterbore")
                translate([x, 0, plate_thickness - finish_depth])
                    cylinder(h = finish_depth + epsilon, d = finish_diameter);
            if (finish_type == "countersink")
                translate([x, 0, plate_thickness - finish_depth])
                    cylinder(h = finish_depth + epsilon, d1 = coupon_diameters[index], d2 = finish_diameter);
        }
    }
}"""
            bounds = scaled_bounds((coupon_width, coupon_depth, thickness), context)
            artifact_kind = "fit_coupon"
            resolved["coupon_candidate_diameters"] = candidate_diameters
            warnings.append(
                "Fit coupon geometry is computationally checked only; a printed result must be recorded manually."
            )
        else:
            if pattern_type == "rectangular":
                pattern_block = """for (x = [-hole_x_spacing / 2, hole_x_spacing / 2])
        for (y = [-hole_y_spacing / 2, hole_y_spacing / 2])
            mounting_hole_at(x, y);"""
            elif pattern_type == "bolt_circle":
                pattern_block = """for (index = [0 : hole_count - 1])
        rotate([0, 0, index * 360 / hole_count])
            mounting_hole_at(bolt_circle_diameter / 2, 0);"""
            else:
                pattern_block = "// no mounting holes requested"

            if opening_type == "circle":
                opening_block = "cylinder(h = plate_thickness + 2 * epsilon, d = opening_diameter);"
            elif opening_type == "rectangle":
                opening_block = "translate([-opening_width / 2, -opening_height / 2, 0]) cube([opening_width, opening_height, plate_thickness + 2 * epsilon]);"
            else:
                opening_block = "// no center opening requested"

            parameter_block = "\n".join(
                [
                    f"outer_width = {scad_number(width)};",
                    f"outer_height = {scad_number(height)};",
                    f"plate_thickness = {scad_number(thickness)};",
                    f"corner_radius = {scad_number(corner_radius)};",
                    f"opening_type = \"{opening_type}\";",
                    f"opening_diameter = {scad_number(opening_values.get('diameter', 0))};",
                    f"opening_width = {scad_number(opening_values.get('width', 0))};",
                    f"opening_height = {scad_number(opening_values.get('height', 0))};",
                    f"pattern_type = \"{pattern_type}\";",
                    f"hole_x_spacing = {scad_number(pattern_values.get('x_spacing', 0))};",
                    f"hole_y_spacing = {scad_number(pattern_values.get('y_spacing', 0))};",
                    f"bolt_circle_diameter = {scad_number(pattern_values.get('bolt_circle_diameter', 0))};",
                    f"hole_count = {int(pattern_values.get('count', 0))};",
                    f"mounting_hole_diameter = {scad_number(mounting_hole)};",
                    f"finish_type = \"{finish_type}\";",
                    f"finish_diameter = {scad_number(finish_diameter)};",
                    f"finish_depth = {scad_number(finish_depth)};",
                ]
            )
            geometry_block = """module plate_body() {
    if (corner_radius > 0)
        hull()
            for (x = [-outer_width / 2 + corner_radius, outer_width / 2 - corner_radius])
                for (y = [-outer_height / 2 + corner_radius, outer_height / 2 - corner_radius])
                    translate([x, y, 0])
                        cylinder(h = plate_thickness, r = corner_radius);
    else
        translate([-outer_width / 2, -outer_height / 2, 0])
            cube([outer_width, outer_height, plate_thickness]);
}

module mounting_hole_at(x, y) {
    translate([x, y, -epsilon])
        cylinder(h = plate_thickness + 2 * epsilon, d = mounting_hole_diameter);
    if (finish_type == "counterbore")
        translate([x, y, plate_thickness - finish_depth])
            cylinder(h = finish_depth + epsilon, d = finish_diameter);
    if (finish_type == "countersink")
        translate([x, y, plate_thickness - finish_depth])
            cylinder(h = finish_depth + epsilon, d1 = mounting_hole_diameter, d2 = finish_diameter);
}

module generated_artifact() {
    difference() {
        plate_body();
        translate([0, 0, -epsilon]) {
            OPENING_BLOCK
        }
        PATTERN_BLOCK
    }
}""".replace("OPENING_BLOCK", opening_block).replace("PATTERN_BLOCK", pattern_block)
            bounds = scaled_bounds((width, height, thickness), context)
            artifact_kind = "full_part"

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
