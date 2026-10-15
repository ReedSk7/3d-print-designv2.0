"""Shared implementation helpers for additive generator version 1.1.0."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Any, Mapping

from generators.base import (
    GenerationContext,
    GenerationResult,
    GeneratorMetadata,
    GeneratorValidationError,
    MM_PER_INCH,
    scad_number,
)


FIT_CLASSES = ("nominal", "slip", "press")
FIT_SCHEMA = {
    "type": "string",
    "enum": list(FIT_CLASSES),
    "default": "nominal",
}


def validate_fit_class(value: Any, label: str) -> str:
    fit_class = str(value)
    if fit_class not in FIT_CLASSES:
        raise GeneratorValidationError(
            [f"{label} must be nominal, slip, or press."]
        )
    return fit_class


def value_from_mm(value_mm: Decimal, input_units: str) -> Decimal:
    normalized = input_units.strip().lower()
    if normalized in {"mm", "millimeter", "millimeters"}:
        return value_mm
    if normalized in {"in", "inch", "inches"}:
        return value_mm / MM_PER_INCH
    raise GeneratorValidationError([f"Unsupported input units: {input_units}"])


def neutral_legacy_context(
    context: GenerationContext,
    *,
    generation_mode: str | None = None,
    coupon_parameter: str | None = None,
) -> GenerationContext:
    """Build a context that lets v1.0 geometry render pre-resolved dimensions.

    Legacy offsets are zeroed so v1.1's per-interface resolution is never
    applied twice. Scale and coupon candidate offsets remain unchanged.
    """

    return GenerationContext(
        input_units=context.input_units,
        nozzle_diameter_mm=context.nozzle_diameter_mm,
        fit_class="nominal",
        calibration_offsets_mm={
            "hole_offset_mm": Decimal("0"),
            "shaft_offset_mm": Decimal("0"),
            "slip_fit_offset_mm": Decimal("0"),
            "press_fit_offset_mm": Decimal("0"),
        },
        scale_correction=context.scale_correction,
        generation_mode=generation_mode or context.generation_mode,
        coupon_parameter=coupon_parameter,
        coupon_offsets_mm=context.coupon_offsets_mm,
        accepted_coupon_parameter=None,
        accepted_coupon_offset_mm=Decimal("0"),
    )


def retag_legacy_result(
    result: GenerationResult,
    *,
    metadata: GeneratorMetadata,
    resolved_parameters_mm: Mapping[str, Any],
    nominal_protected_dimensions_mm: Mapping[str, Decimal],
) -> GenerationResult:
    old_tag = f"generator: {metadata.generator_id} 1.0.0"
    new_tag = f"generator: {metadata.generator_id} {metadata.version}"
    if new_tag in result.source:
        source = result.source
    elif old_tag in result.source:
        source = result.source.replace(old_tag, new_tag, 1)
    else:
        raise RuntimeError(
            f"Expected generator source tag was not rendered: {old_tag} or {new_tag}"
        )
    return replace(
        result,
        source=source,
        resolved_parameters_mm=resolved_parameters_mm,
        nominal_protected_dimensions_mm=nominal_protected_dimensions_mm,
    )


@dataclass(frozen=True)
class CircularCouponGeometry:
    parameter_block: str
    geometry_block: str
    raw_bounds_mm: tuple[Decimal, Decimal, Decimal]
    candidate_diameters_mm: tuple[Decimal, ...]
    candidate_map: tuple[Mapping[str, Any], ...]


def circular_coupon_geometry(
    *,
    base_diameter_mm: Decimal,
    candidate_offsets_mm: tuple[Decimal, ...],
    context: GenerationContext,
    interface_kind: str,
    coupon_thickness_mm: Decimal | None = None,
    finish_type: str = "none",
    finish_diameter_mm: Decimal = Decimal("0"),
    finish_depth_mm: Decimal = Decimal("0"),
) -> CircularCouponGeometry:
    """Build labeled hole or male-cylinder coupon geometry.

    Every cell carries a shallow debossed one-based index. The returned map
    binds that printable index to its exact signed candidate offset and
    resolved diameter, avoiding reliance on left/right interpretation.
    """

    if interface_kind not in {"hole", "shaft"}:
        raise ValueError(f"Unsupported coupon interface kind: {interface_kind}")
    offsets = candidate_offsets_mm or (Decimal("0"),)
    candidates = tuple(base_diameter_mm + offset for offset in offsets)
    if any(candidate <= 0 for candidate in candidates):
        raise GeneratorValidationError(
            ["Every fit-coupon candidate diameter must remain positive."]
        )
    if finish_type not in {"none", "counterbore", "countersink"}:
        raise GeneratorValidationError([f"Unsupported coupon hole finish: {finish_type}"])

    margin = max(context.nozzle_diameter_mm * Decimal("5"), Decimal("2"))
    label_size = max(context.nozzle_diameter_mm * Decimal("8"), Decimal("3.2"))
    label_band = label_size + Decimal("2") * context.nozzle_diameter_mm
    plate_thickness = coupon_thickness_mm or max(
        context.nozzle_diameter_mm * Decimal("5"), Decimal("2")
    )
    if plate_thickness <= 0:
        raise GeneratorValidationError(["Coupon thickness must remain positive."])
    label_depth = min(context.nozzle_diameter_mm, plate_thickness / Decimal("2"))
    max_cut_diameter = max(max(candidates), finish_diameter_mm)
    cell = max_cut_diameter + Decimal("2") * margin
    width = cell * Decimal(len(candidates))
    depth = cell + label_band
    feature_y = label_band / Decimal("2")
    label_y = -depth / Decimal("2") + context.nozzle_diameter_mm
    post_height = max(context.nozzle_diameter_mm * Decimal("8"), Decimal("3"))
    candidate_map = tuple(
        {
            "index": index,
            "label": str(index),
            "offset_mm": offset,
            "resolved_diameter_mm": diameter,
        }
        for index, (offset, diameter) in enumerate(zip(offsets, candidates), start=1)
    )
    parameter_lines = [
        "coupon_diameters = ["
        + ", ".join(scad_number(value) for value in candidates)
        + "];",
        f"coupon_cell = {scad_number(cell)};",
        f"coupon_width = {scad_number(width)};",
        f"coupon_depth = {scad_number(depth)};",
        f"feature_y = {scad_number(feature_y)};",
        f"label_y = {scad_number(label_y)};",
        f"label_size = {scad_number(label_size)};",
        f"label_depth = {scad_number(label_depth)};",
        f"base_thickness = {scad_number(plate_thickness)};",
        f"post_height = {scad_number(post_height)};",
        f'finish_type = "{finish_type}";',
        f"finish_diameter = {scad_number(finish_diameter_mm)};",
        f"finish_depth = {scad_number(finish_depth_mm)};",
    ]
    labels = """for (index = [0 : len(coupon_diameters) - 1])
            translate([
                -coupon_width / 2 + coupon_cell / 2 + index * coupon_cell,
                label_y,
                base_thickness - label_depth
            ])
                linear_extrude(height = label_depth + epsilon)
                    text(str(index + 1), size = label_size, halign = "center", valign = "bottom");"""
    if interface_kind == "hole":
        feature_cut = """for (index = [0 : len(coupon_diameters) - 1]) {
            x = -coupon_width / 2 + coupon_cell / 2 + index * coupon_cell;
            translate([x, feature_y, -epsilon])
                cylinder(h = base_thickness + 2 * epsilon, d = coupon_diameters[index]);
            if (finish_type == "counterbore")
                translate([x, feature_y, base_thickness - finish_depth])
                    cylinder(h = finish_depth + epsilon, d = finish_diameter);
            if (finish_type == "countersink")
                translate([x, feature_y, base_thickness - finish_depth])
                    cylinder(h = finish_depth + epsilon, d1 = coupon_diameters[index], d2 = finish_diameter);
        }"""
        geometry = f"""module generated_artifact() {{
    difference() {{
        translate([-coupon_width / 2, -coupon_depth / 2, 0])
            cube([coupon_width, coupon_depth, base_thickness]);
        {feature_cut}
        {labels}
    }}
}}"""
        bounds = (width, depth, plate_thickness)
    else:
        posts = """for (index = [0 : len(coupon_diameters) - 1])
                translate([
                    -coupon_width / 2 + coupon_cell / 2 + index * coupon_cell,
                    feature_y,
                    base_thickness - epsilon
                ])
                    cylinder(h = post_height + epsilon, d = coupon_diameters[index]);"""
        geometry = f"""module generated_artifact() {{
    difference() {{
        union() {{
            translate([-coupon_width / 2, -coupon_depth / 2, 0])
                cube([coupon_width, coupon_depth, base_thickness]);
            {posts}
        }}
        {labels}
    }}
}}"""
        bounds = (width, depth, plate_thickness + post_height)
    return CircularCouponGeometry(
        parameter_block="\n".join(parameter_lines),
        geometry_block=geometry,
        raw_bounds_mm=bounds,
        candidate_diameters_mm=candidates,
        candidate_map=candidate_map,
    )
