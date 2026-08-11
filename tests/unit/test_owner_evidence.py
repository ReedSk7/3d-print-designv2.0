from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from core.evidence import (
    EvidenceConflictError,
    EvidenceValidationError,
    create_fit_coupon_spec,
    parse_fit_coupon_result_bytes,
)
from core.models.evidence import (
    FileBinding,
    FitConfiguration,
    FitCouponOutcome,
    FitCouponResultEvidence,
    GeneratorBinding,
    InterfaceFitResult,
    PhysicalFitEvidence,
)
from core.models.artifacts import sha256_file
from core.validation.specification import load_project_spec


def _full_bushing_v110(examples_dir: Path, tmp_path: Path) -> Path:
    document = json.loads(
        (examples_dir / "bushing_v110_coupon_example.json").read_text(encoding="utf-8")
    )
    document["project"].update(
        id="owner_evidence_source", name="Owner Evidence Source", version="v01"
    )
    document["generation_mode"] = "full_part"
    document["fit_coupon"] = None
    document["warnings"] = ["Synthetic unit fixture; no printed result is claimed."]
    source = tmp_path / "source.json"
    source.write_text(json.dumps(document, indent=2), encoding="utf-8")
    return source


def test_create_coupon_preserves_exact_configuration_and_refuses_overwrite(
    examples_dir: Path, tmp_path: Path
) -> None:
    source = _full_bushing_v110(examples_dir, tmp_path)
    output = tmp_path / "coupon.json"
    created = create_fit_coupon_spec(
        source,
        interface_parameter="inside_diameter",
        candidate_offsets=("-0.20", "-0.10", "0", "0.10", "0.20"),
        coupon_project_id="owner_coupon",
        coupon_project_version="v01",
        output_spec_path=output,
    )

    source_spec = load_project_spec(source)
    coupon_spec = load_project_spec(created)
    assert coupon_spec.generator.parameters == source_spec.generator.parameters
    assert coupon_spec.generator.version == "1.1.0"
    assert coupon_spec.printer_profile == source_spec.printer_profile
    assert coupon_spec.material == source_spec.material
    assert coupon_spec.nozzle_diameter == source_spec.nozzle_diameter
    assert coupon_spec.fit_profile == source_spec.fit_profile
    assert coupon_spec.fit_coupon is not None
    assert coupon_spec.fit_coupon.source_project_id == source_spec.project.id
    assert coupon_spec.fit_coupon.source_project_version == source_spec.project.version
    assert coupon_spec.fit_coupon.source_spec_sha256 == sha256_file(source)
    assert coupon_spec.fit_coupon.candidate_offsets == (
        Decimal("-0.20"),
        Decimal("-0.10"),
        Decimal("0"),
        Decimal("0.10"),
        Decimal("0.20"),
    )
    with pytest.raises(EvidenceConflictError, match="overwrite"):
        create_fit_coupon_spec(
            source,
            interface_parameter="inside_diameter",
            candidate_offsets=("-0.1", "0", "0.1"),
            coupon_project_id="owner_coupon",
            coupon_project_version="v01",
            output_spec_path=output,
        )


def test_create_coupon_rejects_unsupported_interface(
    examples_dir: Path, tmp_path: Path
) -> None:
    source = _full_bushing_v110(examples_dir, tmp_path)
    with pytest.raises(EvidenceValidationError, match="does not support"):
        create_fit_coupon_spec(
            source,
            interface_parameter="length",
            candidate_offsets=("-0.1", "0", "0.1"),
            coupon_project_id="unsupported_coupon",
            coupon_project_version="v01",
            output_spec_path=tmp_path / "unsupported.json",
        )


def test_create_coupon_requires_a_distinct_project_id(
    examples_dir: Path, tmp_path: Path
) -> None:
    source = _full_bushing_v110(examples_dir, tmp_path)
    with pytest.raises(EvidenceValidationError, match="new and different"):
        create_fit_coupon_spec(
            source,
            interface_parameter="inside_diameter",
            candidate_offsets=("-0.1", "0", "0.1"),
            coupon_project_id="owner_evidence_source",
            coupon_project_version="v02",
            output_spec_path=tmp_path / "same_project.json",
            workspace_root=tmp_path / "workspace",
        )


def test_create_coupon_semantically_rejects_impossible_wall(
    examples_dir: Path, tmp_path: Path
) -> None:
    source = _full_bushing_v110(examples_dir, tmp_path)
    document = json.loads(source.read_text(encoding="utf-8"))
    document["generator"]["parameters"]["inside_diameter"] = 29
    source.write_text(json.dumps(document, indent=2), encoding="utf-8")
    output = tmp_path / "impossible_coupon.json"
    with pytest.raises(EvidenceValidationError, match="semantic validation"):
        create_fit_coupon_spec(
            source,
            interface_parameter="inside_diameter",
            candidate_offsets=("-0.1", "0", "0.1"),
            coupon_project_id="impossible_coupon",
            coupon_project_version="v01",
            output_spec_path=output,
            workspace_root=tmp_path / "workspace",
        )
    assert not output.exists()


def test_create_coupon_rejects_missing_authoritative_replacement_measurements(
    examples_dir: Path, tmp_path: Path
) -> None:
    source = _full_bushing_v110(examples_dir, tmp_path)
    document = json.loads(source.read_text(encoding="utf-8"))
    document["project"]["intent"] = "replacement"
    source.write_text(json.dumps(document, indent=2), encoding="utf-8")
    output = tmp_path / "unmeasured_coupon.json"
    with pytest.raises(EvidenceValidationError, match="authoritative|measurement"):
        create_fit_coupon_spec(
            source,
            interface_parameter="inside_diameter",
            candidate_offsets=("-0.1", "0", "0.1"),
            coupon_project_id="unmeasured_coupon",
            coupon_project_version="v01",
            output_spec_path=output,
            workspace_root=tmp_path / "workspace",
        )
    assert not output.exists()


def test_create_coupon_rejects_existing_workspace_version(
    examples_dir: Path, tmp_path: Path
) -> None:
    source = _full_bushing_v110(examples_dir, tmp_path)
    workspace = tmp_path / "workspace"
    (workspace / "occupied_coupon" / "v01").mkdir(parents=True)
    with pytest.raises(EvidenceConflictError, match="existing coupon"):
        create_fit_coupon_spec(
            source,
            interface_parameter="inside_diameter",
            candidate_offsets=("-0.1", "0", "0.1"),
            coupon_project_id="occupied_coupon",
            coupon_project_version="v01",
            output_spec_path=tmp_path / "not_created.json",
            workspace_root=workspace,
        )


def test_create_fit_coupon_cli_creates_without_generation(
    repo_root: Path, examples_dir: Path, tmp_path: Path
) -> None:
    source = _full_bushing_v110(examples_dir, tmp_path)
    output = tmp_path / "cli_coupon.json"
    workspace = tmp_path / "cli_workspace"
    completed = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "create_fit_coupon.py"),
            "--source-spec",
            str(source),
            "--interface",
            "inside_diameter",
            "--candidate-offset",
            "-0.1",
            "--candidate-offset",
            "0",
            "--candidate-offset",
            "0.1",
            "--coupon-project-id",
            "cli_coupon",
            "--coupon-version",
            "v01",
            "--output-spec",
            str(output),
            "--workspace-root",
            str(workspace),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Coupon generated: no" in completed.stdout
    assert output.is_file()
    assert not (workspace / "cli_coupon" / "v01").exists()


def test_fit_configuration_rejects_candidate_not_generated() -> None:
    with pytest.raises(ValueError, match="not present"):
        FitConfiguration(
            interface_parameter="inside_diameter",
            candidate_offsets_mm=(Decimal("-0.1"), Decimal("0"), Decimal("0.1")),
            selected_candidate_offset_mm=Decimal("0.2"),
            printer_profile="fixture_printer",
            material="PETG",
            nozzle_diameter_mm=Decimal("0.4"),
            calibration_profile_id="neutral_unverified_starter",
            calibration_profile_version="1.0.0",
        )


def test_tiny_decimal_evidence_round_trips_without_exponent_notation() -> None:
    binding = FileBinding("coupon/v01/file", "0" * 64, 1)
    evidence = FitCouponResultEvidence(
        coupon_project_id="coupon",
        coupon_project_version="v01",
        generator=GeneratorBinding("bushing", "1.1.0"),
        manifest=binding,
        stl=binding,
        specification_snapshot=binding,
        configuration=FitConfiguration(
            interface_parameter="inside_diameter",
            candidate_offsets_mm=(Decimal("0"), Decimal("1E-9")),
            selected_candidate_offset_mm=Decimal("1E-9"),
            printer_profile="fixture",
            material="PETG",
            nozzle_diameter_mm=Decimal("0.4"),
            calibration_profile_id="neutral_unverified_starter",
            calibration_profile_version="1.0.0",
            calibration_profile_sha256="1" * 64,
        ),
        result=FitCouponOutcome(
            tested_by="synthetic fixture",
            tested_at="2026-08-10T12:00:00Z",
            acceptance_criterion="Synthetic criterion.",
            observed_result="Synthetic observation.",
            passed=True,
            notes="Test only.",
        ),
        created_at="2026-08-10T12:01:00Z",
        source_project_id="source",
        source_project_version="v01",
        source_spec_sha256="2" * 64,
    )
    document = evidence.to_dict()
    assert document["configuration"]["selected_candidate_offset_mm"] == "0.000000001"
    encoded = json.dumps(document).encode("utf-8")
    reparsed = parse_fit_coupon_result_bytes(encoded)
    assert reparsed.configuration.selected_candidate_offset_mm == Decimal("1E-9")


def test_interface_result_requires_real_boolean() -> None:
    with pytest.raises(ValueError, match="true or false"):
        InterfaceFitResult(
            interface_parameter="inside_diameter",
            acceptance_criterion="Synthetic fixture criterion.",
            observed_result="Synthetic fixture observation.",
            passed="yes",  # type: ignore[arg-type]
        )


def test_physical_fit_model_does_not_accept_a_failed_interface() -> None:
    # Constructor reaches the all-pass gate before any record could be persisted.
    binding = FileBinding("fixture/file", "0" * 64, 1)
    with pytest.raises(ValueError, match="every protected interface"):
        PhysicalFitEvidence(
            project_id="fixture",
            project_version="v01",
            generator=GeneratorBinding("bushing", "1.1.0"),
            manifest=binding,
            stl=binding,
            scad=binding,
            specification_snapshot=binding,
            confirmed_by="synthetic fixture",
            confirmed_at="2026-08-10T12:00:00Z",
            interface_results=(
                InterfaceFitResult(
                    "inside_diameter",
                    "Synthetic criterion.",
                    "Synthetic failure.",
                    False,
                ),
            ),
            measured_dimensions=(),
            notes="Synthetic data only.",
            created_at="2026-08-10T12:01:00Z",
        )


@pytest.mark.parametrize(
    "script_name",
    (
        "create_fit_coupon.py",
        "record_fit_coupon_result.py",
        "create_full_part_from_coupon.py",
        "record_physical_fit.py",
        "inspect_project_status.py",
    ),
)
def test_owner_evidence_cli_help_is_available(repo_root: Path, script_name: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / script_name), "--help"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "usage:" in completed.stdout.lower()
