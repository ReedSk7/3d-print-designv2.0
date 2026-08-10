from __future__ import annotations

import json
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

import pytest

from core.models.measurements import MeasurementContractError
from core.validation.specification import SpecificationError, load_project_spec
from core.workflow.pipeline import prepare_generation


def read_example(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_spec(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "spec.json"
    path.write_text(json.dumps(document, indent=2), encoding="utf-8")
    return path


def test_all_example_specs_validate(examples_dir: Path) -> None:
    for path in sorted(examples_dir.glob("*.json")):
        spec = load_project_spec(path)
        assert spec.schema_version == "1.0"
        assert spec.nozzle_diameter_mm > 0


def test_schema_rejects_missing_required_field(examples_dir: Path, tmp_path: Path) -> None:
    document = read_example(examples_dir / "bushing_example.json")
    del document["schema_version"]
    with pytest.raises(SpecificationError, match="schema_version"):
        load_project_spec(write_spec(tmp_path, document))


def test_schema_rejects_invalid_units(examples_dir: Path, tmp_path: Path) -> None:
    document = read_example(examples_dir / "bushing_example.json")
    document["input_units"] = "centimeters"
    with pytest.raises(SpecificationError, match="input_units"):
        load_project_spec(write_spec(tmp_path, document))


def test_replacement_full_part_blocks_missing_authoritative_interfaces(
    examples_dir: Path, tmp_path: Path
) -> None:
    document = deepcopy(read_example(examples_dir / "bushing_example.json"))
    document["project"]["intent"] = "replacement"  # type: ignore[index]
    spec = load_project_spec(write_spec(tmp_path, document))
    with pytest.raises(MeasurementContractError, match="authoritative measured dimension"):
        prepare_generation(spec)


def test_replacement_measurements_must_match_nominal_within_tolerance(
    examples_dir: Path, tmp_path: Path
) -> None:
    document = deepcopy(read_example(examples_dir / "bushing_example.json"))
    document["project"]["intent"] = "replacement"  # type: ignore[index]
    measurements = []
    for name, value in (("inside_diameter", 20), ("outside_diameter", 30), ("length", 25)):
        measurements.append(
            {
                "parameter_name": name,
                "measured_value": value,
                "units": "mm",
                "measurement_source": "caliper measurement record demo-001",
                "authority": "authoritative",
                "confidence_level": "high",
                "tolerance": 0.05,
                "protected_interface": True,
                "verification_notes": "Synthetic unit-test measurement.",
            }
        )
    measurements[0]["measured_value"] = 21
    document["measurement_contract"] = measurements
    spec = load_project_spec(write_spec(tmp_path, document))
    with pytest.raises(MeasurementContractError, match="within its recorded tolerance"):
        prepare_generation(spec)


def test_inch_spec_normalizes_measurement_contract_without_double_conversion(
    examples_dir: Path, tmp_path: Path
) -> None:
    document = deepcopy(read_example(examples_dir / "bushing_example.json"))
    document["project"]["intent"] = "replacement"  # type: ignore[index]
    document["input_units"] = "inch"
    document["nozzle_diameter"] = 0.015748031496062992
    document["generator"]["parameters"].update(  # type: ignore[index,union-attr]
        {
            "inside_diameter": 0.75,
            "outside_diameter": 1.25,
            "length": 1,
            "chamfer": 0.04,
            "minimum_wall_thickness": 0.08,
        }
    )
    document["measurement_contract"] = [
        {
            "parameter_name": name,
            "measured_value": value,
            "units": "inch",
            "measurement_source": "caliper measurement record demo-inch",
            "authority": "authoritative",
            "confidence_level": "high",
            "tolerance": 0.001,
            "protected_interface": True,
            "verification_notes": "Synthetic inch unit-test measurement.",
        }
        for name, value in (
            ("inside_diameter", 0.75),
            ("outside_diameter", 1.25),
            ("length", 1),
        )
    ]
    prepared = prepare_generation(load_project_spec(write_spec(tmp_path, document)))
    assert prepared.generation.nominal_protected_dimensions_mm["inside_diameter"] == Decimal(
        "19.05"
    )


def test_coupon_does_not_bypass_missing_nominal_measurement(
    examples_dir: Path, tmp_path: Path
) -> None:
    document = deepcopy(read_example(examples_dir / "bushing_example.json"))
    document["project"]["intent"] = "replacement"  # type: ignore[index]
    document["generation_mode"] = "fit_coupon"
    document["fit_coupon"] = {
        "interface_parameter": "inside_diameter",
        "candidate_offsets": [-0.1, 0, 0.1],
        "notes": "Synthetic coupon request.",
    }
    spec = load_project_spec(write_spec(tmp_path, document))
    with pytest.raises(MeasurementContractError):
        prepare_generation(spec)


def test_full_part_rejects_nonexistent_fit_coupon_evidence(
    examples_dir: Path, tmp_path: Path
) -> None:
    document = deepcopy(read_example(examples_dir / "bushing_example.json"))
    document["fit_coupon_evidence"] = {
        "coupon_project_id": "bushing_coupon_test",
        "coupon_project_version": "v01",
        "coupon_artifact_sha256": "a" * 64,
        "interface_parameter": "inside_diameter",
        "candidate_offset_mm": 0.1,
        "tested_at": "2026-08-10T12:00:00Z",
        "tested_by": "synthetic test owner",
        "printer_profile": "generic_fdm",
        "material": "PETG",
        "nozzle_diameter_mm": 0.4,
        "calibration_profile_id": "neutral_unverified_starter",
        "calibration_profile_version": "1.0.0",
        "acceptance_criterion": "Synthetic candidate met the stated insertion criterion.",
        "measured_result": "Synthetic result for domain wiring only.",
        "passed": True,
        "notes": "No real physical claim is made by this unit fixture.",
    }
    with pytest.raises(SpecificationError, match="fit-coupon manifest was not found"):
        prepare_generation(
            load_project_spec(write_spec(tmp_path, document)),
            workspace_root=tmp_path / "workspace",
        )


def test_linked_coupon_must_match_printer_material_nozzle_and_profile(
    examples_dir: Path, tmp_path: Path
) -> None:
    document = deepcopy(read_example(examples_dir / "bushing_example.json"))
    document["fit_coupon_evidence"] = {
        "coupon_project_id": "bushing_coupon_test",
        "coupon_project_version": "v01",
        "coupon_artifact_sha256": "b" * 64,
        "interface_parameter": "inside_diameter",
        "candidate_offset_mm": 0.1,
        "tested_at": "2026-08-10T12:00:00Z",
        "tested_by": "synthetic test owner",
        "printer_profile": "different_printer",
        "material": "PETG",
        "nozzle_diameter_mm": 0.4,
        "calibration_profile_id": "neutral_unverified_starter",
        "calibration_profile_version": "1.0.0",
        "acceptance_criterion": "Synthetic criterion.",
        "measured_result": "Synthetic result.",
        "passed": True,
        "notes": "Mismatch fixture.",
    }
    with pytest.raises(SpecificationError, match="printer profile"):
        load_project_spec(write_spec(tmp_path, document))
