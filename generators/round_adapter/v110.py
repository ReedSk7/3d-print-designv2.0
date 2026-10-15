"""Round-adapter generator 1.1.0 with per-interface fit controls."""

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
    scale_statement,
    scaled_bounds,
)
from generators.round_adapter.generator import RoundAdapterGenerator
from generators.v110_common import (
    FIT_SCHEMA,
    circular_coupon_geometry,
    neutral_legacy_context,
    retag_legacy_result,
    validate_fit_class,
    value_from_mm,
)


MOUNTING_HOLE_INTERFACE = "mounting_flange.screw_hole_pattern.hole_diameter"


class RoundAdapterGeneratorV110(RoundAdapterGenerator):
    metadata = GeneratorMetadata(
        generator_id="round_adapter",
        version="1.1.0",
        name="Round Adapter",
        description=(
            "Straight or tapered adapter with independent end and mounting-hole fits."
        ),
        protected_interfaces=(
            "end_a.diameter",
            "end_b.diameter",
            MOUNTING_HOLE_INTERFACE,
        ),
        fit_coupon_interfaces=(
            "end_a.diameter",
            "end_b.diameter",
            MOUNTING_HOLE_INTERFACE,
        ),
    )
    defaults = {
        "transition": "tapered",
        "end_a_fit": "nominal",
        "end_b_fit": "nominal",
        "mounting_hole_fit": "nominal",
        "hose_retaining_bead": {"enabled": False},
        "mounting_flange": {"enabled": False},
    }
    parameter_schema = deepcopy(RoundAdapterGenerator.parameter_schema)
    parameter_schema["properties"].pop("fit_class")
    parameter_schema["properties"].update(
        {
            "end_a_fit": FIT_SCHEMA,
            "end_b_fit": FIT_SCHEMA,
            "mounting_hole_fit": FIT_SCHEMA,
        }
    )

    @staticmethod
    def _has_mounting_holes(parameters: Mapping[str, Any]) -> bool:
        flange = parameters.get("mounting_flange")
        if not isinstance(flange, Mapping) or not flange.get("enabled"):
            return False
        pattern = flange.get("screw_hole_pattern")
        return isinstance(pattern, Mapping) and bool(pattern.get("enabled"))

    def applicable_protected_interfaces(
        self, parameters: Mapping[str, Any]
    ) -> tuple[str, ...]:
        result = ["end_a.diameter", "end_b.diameter"]
        if self._has_mounting_holes(parameters):
            result.append(MOUNTING_HOLE_INTERFACE)
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
        try:
            end_a = values["end_a"]
            end_b = values["end_b"]
            if not isinstance(end_a, Mapping) or not isinstance(end_b, Mapping):
                raise TypeError
            nominal_a = input_length_mm(
                end_a["diameter"], context.input_units, "end_a.diameter"
            )
            nominal_b = input_length_mm(
                end_b["diameter"], context.input_units, "end_b.diameter"
            )
            type_a = str(end_a["diameter_type"])
            type_b = str(end_b["diameter_type"])
        except (KeyError, TypeError) as exc:
            label = exc.args[0] if isinstance(exc, KeyError) else "end_a/end_b"
            raise GeneratorValidationError(
                [f"Missing round_adapter parameter: {label}"]
            ) from exc
        if type_a not in {"inside", "outside"} or type_b not in {"inside", "outside"}:
            raise GeneratorValidationError(
                ["Each end diameter_type must be 'inside' or 'outside'."]
            )

        end_a_fit = validate_fit_class(values["end_a_fit"], "end_a_fit")
        end_b_fit = validate_fit_class(values["end_b_fit"], "end_b_fit")
        mounting_fit = validate_fit_class(
            values["mounting_hole_fit"], "mounting_hole_fit"
        )
        resolved_a = diameter_with_directional_fit(
            nominal_a,
            interface="hole" if type_a == "inside" else "shaft",
            fit_class=end_a_fit,
            context=context,
        )
        resolved_b = diameter_with_directional_fit(
            nominal_b,
            interface="hole" if type_b == "inside" else "shaft",
            fit_class=end_b_fit,
            context=context,
        )

        holes_present = self._has_mounting_holes(values)
        nominal_mounting_hole: Decimal | None = None
        resolved_mounting_hole: Decimal | None = None
        if holes_present:
            pattern = values["mounting_flange"]["screw_hole_pattern"]
            nominal_mounting_hole = input_length_mm(
                pattern["hole_diameter"], context.input_units, MOUNTING_HOLE_INTERFACE
            )
            resolved_mounting_hole = diameter_with_directional_fit(
                nominal_mounting_hole,
                interface="hole",
                fit_class=mounting_fit,
                context=context,
            )

        coupon_parameter = context.coupon_parameter or "end_a.diameter"
        applicable = set(self.applicable_coupon_interfaces(values))
        errors: list[str] = []
        if context.generation_mode == "fit_coupon" and coupon_parameter not in applicable:
            errors.append(
                "Round-adapter 1.1.0 coupon interface is unsupported or absent from this configuration."
            )
        if (
            context.accepted_coupon_parameter is not None
            and context.accepted_coupon_parameter not in applicable
        ):
            errors.append(
                "Round-adapter 1.1.0 accepted coupon interface is unsupported or absent."
            )
        if errors:
            raise GeneratorValidationError(errors)
        if context.accepted_coupon_parameter == "end_a.diameter":
            resolved_a += context.accepted_coupon_offset_mm
        elif context.accepted_coupon_parameter == "end_b.diameter":
            resolved_b += context.accepted_coupon_offset_mm
        elif context.accepted_coupon_parameter == MOUNTING_HOLE_INTERFACE:
            assert resolved_mounting_hole is not None
            resolved_mounting_hole += context.accepted_coupon_offset_mm
        legacy_parameters = deepcopy(values)
        for name in ("end_a_fit", "end_b_fit", "mounting_hole_fit"):
            legacy_parameters.pop(name, None)
        legacy_parameters["fit_class"] = "nominal"
        legacy_parameters["end_a"]["diameter"] = value_from_mm(
            resolved_a, context.input_units
        )
        legacy_parameters["end_b"]["diameter"] = value_from_mm(
            resolved_b, context.input_units
        )
        if holes_present:
            legacy_parameters["mounting_flange"]["screw_hole_pattern"][
                "hole_diameter"
            ] = value_from_mm(resolved_mounting_hole, context.input_units)  # type: ignore[arg-type]

        if context.generation_mode != "fit_coupon":
            legacy_result = super().generate(
                legacy_parameters,
                neutral_legacy_context(context, coupon_parameter=None),
            )
            resolved = deepcopy(dict(legacy_result.resolved_parameters_mm))
            resolved.pop("fit_class", None)
            resolved.update(
                end_a_fit=end_a_fit,
                end_b_fit=end_b_fit,
                mounting_hole_fit=mounting_fit,
            )
            nominal_protected = dict(legacy_result.nominal_protected_dimensions_mm)
            nominal_protected["end_a.diameter"] = nominal_a
            nominal_protected["end_b.diameter"] = nominal_b
            if nominal_mounting_hole is not None:
                nominal_protected[MOUNTING_HOLE_INTERFACE] = nominal_mounting_hole
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
        if coupon_parameter == "end_a.diameter":
            base_diameter = resolved_a
            interface_kind = "hole" if type_a == "inside" else "shaft"
        elif coupon_parameter == "end_b.diameter":
            base_diameter = resolved_b
            interface_kind = "hole" if type_b == "inside" else "shaft"
        else:
            assert resolved_mounting_hole is not None
            base_diameter = resolved_mounting_hole
            interface_kind = "hole"
        coupon = circular_coupon_geometry(
            base_diameter_mm=base_diameter,
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
        )
        resolved = deepcopy(dict(validated.resolved_parameters_mm))
        resolved.pop("fit_class", None)
        resolved.update(
            end_a_fit=end_a_fit,
            end_b_fit=end_b_fit,
            mounting_hole_fit=mounting_fit,
            coupon_interface_kind=interface_kind,
            coupon_candidate_diameters=coupon.candidate_diameters_mm,
            coupon_candidate_map=coupon.candidate_map,
        )
        nominal_protected = dict(validated.nominal_protected_dimensions_mm)
        nominal_protected["end_a.diameter"] = nominal_a
        nominal_protected["end_b.diameter"] = nominal_b
        if nominal_mounting_hole is not None:
            nominal_protected[MOUNTING_HOLE_INTERFACE] = nominal_mounting_hole
        return GenerationResult(
            source=source,
            expected_bounds_mm=scaled_bounds(coupon.raw_bounds_mm, context),
            resolved_parameters_mm=resolved,
            nominal_protected_dimensions_mm=nominal_protected,
            warnings=(
                "Numbered interface fit coupon is computationally checked only; a printed result must be recorded manually.",
            ),
            expected_body_count=1,
            artifact_kind="fit_coupon",
        )
