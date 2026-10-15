from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from core.evidence import (
    EvidenceConflictError,
    EvidenceIntegrityError,
    EvidenceValidationError,
    create_fit_coupon_spec,
    create_full_part_spec_from_coupon,
    inspect_project_status,
    record_fit_coupon_result,
    record_physical_fit,
    verify_fit_coupon_result,
    verify_physical_fit,
)
from core.models.artifacts import sha256_file
from core.validation.specification import SpecificationError, load_project_spec
from core.workflow.pipeline import generate_project, prepare_spec_file


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_spec(examples_dir: Path, tmp_path: Path, *, project_id: str) -> Path:
    document = json.loads(
        (examples_dir / "bushing_v110_coupon_example.json").read_text(encoding="utf-8")
    )
    document["project"].update(id=project_id, name="Synthetic Evidence Fixture", version="v01")
    document["generation_mode"] = "full_part"
    document["fit_coupon"] = None
    document["warnings"] = ["Synthetic integration fixture; no physical test is claimed."]
    source = tmp_path / f"{project_id}.json"
    source.write_text(json.dumps(document, indent=2), encoding="utf-8")
    return source


def _generated_coupon(
    examples_dir: Path,
    tmp_path: Path,
    *,
    suffix: str,
) -> tuple[Path, Path, Path]:
    source = _source_spec(examples_dir, tmp_path, project_id=f"full_source_{suffix}")
    coupon_spec = tmp_path / f"coupon_{suffix}.json"
    workspace = tmp_path / f"workspace_{suffix}"
    create_fit_coupon_spec(
        source,
        interface_parameter="inside_diameter",
        candidate_offsets=("-0.15", "0", "0.15"),
        coupon_project_id=f"coupon_{suffix}",
        coupon_project_version="v01",
        output_spec_path=coupon_spec,
    )
    result = generate_project(coupon_spec, workspace_root=workspace)
    return source, workspace, result.manifest_path


def _record_pass(manifest: Path) -> Path:
    return record_fit_coupon_result(
        manifest,
        expected_manifest_sha256=sha256_file(manifest),
        selected_candidate_offset_mm="0.15",
        tested_by="synthetic integration fixture",
        tested_at=_timestamp(),
        acceptance_criterion="Synthetic test criterion; no real print occurred.",
        observed_result="Synthetic passing observation for evidence plumbing only.",
        notes="Automated fixture data, not an owner physical test.",
        passed=True,
        require_passed=True,
    )


@pytest.mark.integration
def test_owner_evidence_chain_status_before_and_after_each_state(
    repo_root: Path, examples_dir: Path, tmp_path: Path
) -> None:
    source, workspace, coupon_manifest = _generated_coupon(
        examples_dir, tmp_path, suffix="complete"
    )
    coupon_directory = coupon_manifest.parent
    generated_status = inspect_project_status(coupon_directory)
    assert generated_status["highest_defensible_workflow_state"] == "fit_coupon_generated"
    assert generated_status["coupon_evidence_state"] == "not_recorded"
    assert generated_status["physical_fit_claim_allowed"] is False
    assert "physically verified" not in json.dumps(generated_status).lower()
    status_cli = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "inspect_project_status.py"),
            "--project-version-dir",
            str(coupon_directory),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert status_cli.returncode == 0, status_cli.stdout + status_cli.stderr
    assert 'Phrase "physically verified" allowed: false' in status_cli.stdout
    assert "is physically verified" not in status_cli.stdout.lower()

    result_evidence = coupon_directory / "fit-result.evidence.json"
    record_cli = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "record_fit_coupon_result.py"),
            "--manifest",
            str(coupon_manifest),
            "--manifest-sha256",
            sha256_file(coupon_manifest),
            "--selected-offset-mm",
            "0.15",
            "--tester",
            "synthetic CLI fixture",
            "--tested-at",
            _timestamp(),
            "--acceptance-criterion",
            "Synthetic criterion; no real print occurred.",
            "--observed-result",
            "Synthetic passing observation for CLI wiring only.",
            "--notes",
            "Automated fixture, not an owner test.",
            "--passed",
            "--require-passed",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert record_cli.returncode == 0, record_cli.stdout + record_cli.stderr
    assert "Reached state: fit_coupon_passed" in record_cli.stdout
    assert f"Evidence SHA-256: {sha256_file(result_evidence)}" in record_cli.stdout
    assert result_evidence.is_file()
    unanchored_status = inspect_project_status(coupon_directory)
    assert unanchored_status["highest_defensible_workflow_state"] == "fit_coupon_generated"
    assert unanchored_status["coupon_evidence_state"] == "unanchored"
    passed_status = inspect_project_status(
        coupon_directory,
        expected_fit_evidence_sha256=sha256_file(result_evidence),
    )
    assert passed_status["highest_defensible_workflow_state"] == "fit_coupon_passed"
    assert passed_status["coupon_evidence_state"] == "passed"
    assert passed_status["physical_fit_claim_allowed"] is False
    assert "physically verified" not in json.dumps(passed_status).lower()

    linked_spec = tmp_path / "linked_full_v02.json"
    create_full_cli = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "create_full_part_from_coupon.py"),
            "--source-spec",
            str(source),
            "--coupon-evidence",
            str(result_evidence),
            "--coupon-evidence-sha256",
            sha256_file(result_evidence),
            "--new-version",
            "v02",
            "--output-spec",
            str(linked_spec),
            "--workspace-root",
            str(workspace),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert create_full_cli.returncode == 0, create_full_cli.stdout + create_full_cli.stderr
    assert "Reached state: draft" in create_full_cli.stdout
    linked = load_project_spec(linked_spec)
    assert linked.workflow_state.value == "draft"
    assert linked.fit_coupon_evidence is not None
    assert linked.fit_coupon_evidence.coupon_result_evidence_sha256 == sha256_file(
        result_evidence
    )
    assert linked.fit_coupon_evidence.candidate_offset_mm == Decimal("0.15")
    assert linked.fit_coupon_evidence.source_project_id == load_project_spec(source).project.id
    assert linked.fit_coupon_evidence.source_project_version == "v01"
    assert linked.fit_coupon_evidence.source_spec_sha256 == sha256_file(source)
    assert linked.fit_coupon_evidence.calibration_profile_sha256 is not None

    full_result = generate_project(linked_spec, workspace_root=workspace)
    unanchored_full_status = inspect_project_status(full_result.output_directory)
    assert unanchored_full_status["coupon_evidence_state"] == "linked_passed"
    full_status = inspect_project_status(
        full_result.output_directory,
        expected_fit_evidence_sha256=sha256_file(result_evidence),
    )
    assert full_status["highest_defensible_workflow_state"] == "full_part_exported"
    assert full_status["coupon_evidence_state"] == "linked_passed"
    assert full_status["physical_fit_evidence_state"] == "not_recorded"
    assert full_status["physical_fit_claim_allowed"] is False
    assert "physically verified" not in json.dumps(full_status).lower()
    with pytest.raises(EvidenceConflictError, match="existing full-part"):
        create_full_part_spec_from_coupon(
            source,
            passed_coupon_evidence_path=result_evidence,
            expected_coupon_evidence_sha256=sha256_file(result_evidence),
            new_project_version="v02",
            output_spec_path=tmp_path / "duplicate_linked_full.json",
            workspace_root=workspace,
        )

    interface_results_path = tmp_path / "physical_interface_results.json"
    interface_results_path.write_text(
        json.dumps(
            [
                {
                "interface_parameter": "inside_diameter",
                "acceptance_criterion": "Synthetic inside criterion.",
                "observed_result": "Synthetic passing observation; no real print occurred.",
                "passed": True,
                "notes": "Test fixture only.",
            },
            {
                "interface_parameter": "outside_diameter",
                "acceptance_criterion": "Synthetic outside criterion.",
                "observed_result": "Synthetic passing observation; no real print occurred.",
                "passed": True,
                "notes": "Test fixture only.",
            },
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    measured_dimensions_path = tmp_path / "physical_measured_dimensions.json"
    measured_dimensions_path.write_text(
        json.dumps(
            [
                {
                    "parameter_name": "inside_diameter",
                    "measured_value": 20.01,
                    "units": "mm",
                    "measurement_source": "synthetic CLI fixture",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    physical_cli = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "record_physical_fit.py"),
            "--manifest",
            str(full_result.manifest_path),
            "--manifest-sha256",
            sha256_file(full_result.manifest_path),
            "--confirmed-by",
            "synthetic CLI fixture",
            "--confirmed-at",
            _timestamp(),
            "--interface-results-json",
            str(interface_results_path),
            "--measured-dimensions-json",
            str(measured_dimensions_path),
            "--notes",
            "Automated evidence-chain fixture; not a physical test.",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert physical_cli.returncode == 0, physical_cli.stdout + physical_cli.stderr
    assert "Reached state: physical_fit_confirmed" in physical_cli.stdout
    physical_evidence = full_result.output_directory / "physical-fit.evidence.json"
    assert physical_evidence.name == "physical-fit.evidence.json"
    assert f"Evidence SHA-256: {sha256_file(physical_evidence)}" in physical_cli.stdout
    physical_unanchored = inspect_project_status(
        full_result.output_directory,
        expected_fit_evidence_sha256=sha256_file(result_evidence),
    )
    assert physical_unanchored["highest_defensible_workflow_state"] == "full_part_exported"
    assert physical_unanchored["physical_fit_evidence_state"] == "unanchored"
    confirmed_status = inspect_project_status(
        full_result.output_directory,
        expected_fit_evidence_sha256=sha256_file(result_evidence),
        expected_physical_evidence_sha256=sha256_file(physical_evidence),
    )
    assert confirmed_status["highest_defensible_workflow_state"] == "physical_fit_confirmed"
    assert confirmed_status["physical_fit_evidence_state"] == "confirmed"
    assert confirmed_status["physical_fit_claim_allowed"] is True


@pytest.mark.integration
def test_coupon_evidence_rejects_manifest_stl_candidate_failure_and_duplicates(
    examples_dir: Path, tmp_path: Path
) -> None:
    _, _, manifest = _generated_coupon(examples_dir, tmp_path, suffix="reject")
    expected_manifest_sha = sha256_file(manifest)
    original_manifest_bytes = manifest.read_bytes()
    manifest.write_bytes(original_manifest_bytes + b" ")
    with pytest.raises(EvidenceIntegrityError, match="owner-supplied expected digest"):
        record_fit_coupon_result(
            manifest,
            expected_manifest_sha256=expected_manifest_sha,
            selected_candidate_offset_mm="0",
            tested_by="synthetic fixture",
            tested_at=_timestamp(),
            acceptance_criterion="Synthetic criterion.",
            observed_result="Synthetic observation.",
            notes="Test only.",
            passed=True,
        )
    manifest.write_bytes(original_manifest_bytes)
    tampered_profile = json.loads(original_manifest_bytes.decode("utf-8"))
    tampered_profile["checks"]["calibration_profile"]["sha256"] = "0" * 64
    manifest.write_text(json.dumps(tampered_profile, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceIntegrityError, match="profile content"):
        record_fit_coupon_result(
            manifest,
            expected_manifest_sha256=sha256_file(manifest),
            selected_candidate_offset_mm="0",
            tested_by="synthetic fixture",
            tested_at=_timestamp(),
            acceptance_criterion="Synthetic criterion.",
            observed_result="Synthetic observation.",
            notes="Test only.",
            passed=True,
        )
    manifest.write_bytes(original_manifest_bytes)
    tampered_map = json.loads(original_manifest_bytes.decode("utf-8"))
    tampered_map["checks"]["normalized_parameters_mm"]["coupon_candidate_map"][0][
        "offset_mm"
    ] = "0.15"
    manifest.write_text(json.dumps(tampered_map, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceIntegrityError, match="candidate map offsets"):
        record_fit_coupon_result(
            manifest,
            expected_manifest_sha256=sha256_file(manifest),
            selected_candidate_offset_mm="0",
            tested_by="synthetic fixture",
            tested_at=_timestamp(),
            acceptance_criterion="Synthetic criterion.",
            observed_result="Synthetic observation.",
            notes="Test only.",
            passed=True,
        )
    manifest.write_bytes(original_manifest_bytes)
    with pytest.raises(EvidenceValidationError, match="not present"):
        record_fit_coupon_result(
            manifest,
            expected_manifest_sha256=expected_manifest_sha,
            selected_candidate_offset_mm="0.99",
            tested_by="synthetic fixture",
            tested_at=_timestamp(),
            acceptance_criterion="Synthetic criterion.",
            observed_result="Synthetic observation.",
            notes="Test only.",
            passed=True,
        )
    with pytest.raises(EvidenceValidationError, match="requested.*failed"):
        record_fit_coupon_result(
            manifest,
            expected_manifest_sha256=expected_manifest_sha,
            selected_candidate_offset_mm="0",
            tested_by="synthetic fixture",
            tested_at=_timestamp(),
            acceptance_criterion="Synthetic criterion.",
            observed_result="Synthetic failed observation.",
            notes="Test only.",
            passed=False,
            require_passed=True,
        )
    failed = record_fit_coupon_result(
        manifest,
        expected_manifest_sha256=expected_manifest_sha,
        selected_candidate_offset_mm="0",
        tested_by="synthetic fixture",
        tested_at=_timestamp(),
        acceptance_criterion="Synthetic criterion.",
        observed_result="Synthetic failed observation.",
        notes="Test only.",
        passed=False,
    )
    assert inspect_project_status(manifest.parent)["highest_defensible_workflow_state"] == (
        "fit_coupon_generated"
    )
    with pytest.raises(EvidenceConflictError, match="already exists"):
        record_fit_coupon_result(
            manifest,
            expected_manifest_sha256=expected_manifest_sha,
            selected_candidate_offset_mm="0.15",
            tested_by="synthetic fixture",
            tested_at=_timestamp(),
            acceptance_criterion="Synthetic criterion.",
            observed_result="Synthetic passing observation.",
            notes="Test only.",
            passed=True,
        )
    source = _source_spec(examples_dir, tmp_path, project_id="failed_source")
    with pytest.raises(EvidenceValidationError, match="Failed"):
        create_full_part_spec_from_coupon(
            source,
            passed_coupon_evidence_path=failed,
            expected_coupon_evidence_sha256=sha256_file(failed),
            new_project_version="v02",
            output_spec_path=tmp_path / "should_not_exist.json",
        )
    original_failed_bytes = failed.read_bytes()
    original_failed_sha = sha256_file(failed)
    promoted_result = json.loads(original_failed_bytes.decode("utf-8"))
    promoted_result["result"]["passed"] = True
    promoted_result["defensible_workflow_state"] = "fit_coupon_passed"
    failed.write_text(json.dumps(promoted_result, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceIntegrityError, match="owner-supplied expected digest"):
        create_full_part_spec_from_coupon(
            source,
            passed_coupon_evidence_path=failed,
            expected_coupon_evidence_sha256=original_failed_sha,
            new_project_version="v02",
            output_spec_path=tmp_path / "promoted_failed_output.json",
        )
    failed.write_bytes(original_failed_bytes)
    mutated_offset = json.loads(original_failed_bytes.decode("utf-8"))
    mutated_offset["configuration"]["selected_candidate_offset_mm"] = "0.15"
    failed.write_text(json.dumps(mutated_offset, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceIntegrityError, match="owner-supplied expected digest"):
        create_full_part_spec_from_coupon(
            source,
            passed_coupon_evidence_path=failed,
            expected_coupon_evidence_sha256=original_failed_sha,
            new_project_version="v02",
            output_spec_path=tmp_path / "mutated_offset_output.json",
        )
    failed.write_bytes(original_failed_bytes)
    malformed_result = json.loads(failed.read_text(encoding="utf-8"))
    malformed_result["unexpected_field"] = "must be rejected"
    failed.write_text(json.dumps(malformed_result, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceIntegrityError, match="Additional properties"):
        verify_fit_coupon_result(failed)

    _, workspace, stl_manifest = _generated_coupon(examples_dir, tmp_path, suffix="stl")
    stl_document = json.loads(stl_manifest.read_text(encoding="utf-8"))
    stl_record = next(
        item for item in stl_document["artifacts"] if item["role"] == "fit_coupon_stl"
    )
    stl_path = workspace / stl_record["path"]
    damaged = bytearray(stl_path.read_bytes())
    damaged[0] ^= 1
    stl_path.write_bytes(damaged)
    with pytest.raises(EvidenceIntegrityError, match="SHA-256"):
        record_fit_coupon_result(
            stl_manifest,
            expected_manifest_sha256=sha256_file(stl_manifest),
            selected_candidate_offset_mm="0",
            tested_by="synthetic fixture",
            tested_at=_timestamp(),
            acceptance_criterion="Synthetic criterion.",
            observed_result="Synthetic observation.",
            notes="Test only.",
            passed=True,
        )


@pytest.mark.integration
def test_linked_full_part_and_physical_evidence_reject_mismatch_missing_and_wrong_stl(
    examples_dir: Path, tmp_path: Path
) -> None:
    source, workspace, manifest = _generated_coupon(examples_dir, tmp_path, suffix="physical")
    result_evidence = _record_pass(manifest)

    mismatched = json.loads(source.read_text(encoding="utf-8"))
    mismatched["generator"]["version"] = "1.0.0"
    mismatched["generator"]["parameters"] = {
        "inside_diameter": 20,
        "outside_diameter": 30,
        "length": 25,
        "chamfer": 1,
        "fit_class": "nominal",
        "split": False,
        "minimum_wall_thickness": 1.2,
    }
    mismatched_path = tmp_path / "mismatched_version.json"
    mismatched_path.write_text(json.dumps(mismatched, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceValidationError, match="different or edited"):
        create_full_part_spec_from_coupon(
            mismatched_path,
            passed_coupon_evidence_path=result_evidence,
            expected_coupon_evidence_sha256=sha256_file(result_evidence),
            new_project_version="v02",
            output_spec_path=tmp_path / "wrong_version_output.json",
        )

    linked = tmp_path / "physical_full.json"
    create_full_part_spec_from_coupon(
        source,
        passed_coupon_evidence_path=result_evidence,
        expected_coupon_evidence_sha256=sha256_file(result_evidence),
        new_project_version="v02",
        output_spec_path=linked,
    )
    full = generate_project(linked, workspace_root=workspace)
    with pytest.raises(EvidenceValidationError, match="missing protected interface"):
        record_physical_fit(
            full.manifest_path,
            expected_manifest_sha256=sha256_file(full.manifest_path),
            confirmed_by="synthetic fixture",
            confirmed_at=_timestamp(),
            interface_results=(
                {
                    "interface_parameter": "inside_diameter",
                    "acceptance_criterion": "Synthetic criterion.",
                    "observed_result": "Synthetic passing observation.",
                    "passed": True,
                },
            ),
            notes="Test only.",
        )

    physical = record_physical_fit(
        full.manifest_path,
        expected_manifest_sha256=sha256_file(full.manifest_path),
        confirmed_by="synthetic fixture",
        confirmed_at=_timestamp(),
        interface_results=(
            {
                "interface_parameter": interface,
                "acceptance_criterion": "Synthetic criterion.",
                "observed_result": "Synthetic passing observation; no print occurred.",
                "passed": True,
            }
            for interface in ("inside_diameter", "outside_diameter")
        ),
        notes="Automated fixture only.",
    )
    document = json.loads(physical.read_text(encoding="utf-8"))
    document["bindings"]["stl"]["sha256"] = "0" * 64
    physical.write_text(json.dumps(document, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceIntegrityError, match="Full-part STL binding"):
        verify_physical_fit(physical)


@pytest.fixture(scope="module")
def _configuration_mismatch_chain(
    examples_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> tuple[Path, Path]:
    directory = tmp_path_factory.mktemp("owner_config_mismatch")
    source, _, manifest = _generated_coupon(
        examples_dir, directory, suffix="configuration"
    )
    return source, _record_pass(manifest)


@pytest.mark.integration
@pytest.mark.parametrize(
    ("field", "changed_value"),
    (
        ("printer_profile", "different_printer"),
        ("material", "PLA"),
        ("nozzle_diameter", 0.6),
        ("fit_profile", "different_profile"),
    ),
    ids=("printer", "material", "nozzle", "calibration_profile"),
)
def test_linked_full_part_rejects_each_configuration_mismatch(
    _configuration_mismatch_chain: tuple[Path, Path],
    tmp_path: Path,
    field: str,
    changed_value: object,
) -> None:
    source, evidence = _configuration_mismatch_chain
    document = json.loads(source.read_text(encoding="utf-8"))
    document[field] = changed_value
    changed_source = tmp_path / f"changed_{field}.json"
    changed_source.write_text(json.dumps(document, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceValidationError, match="different or edited"):
        create_full_part_spec_from_coupon(
            changed_source,
            passed_coupon_evidence_path=evidence,
            expected_coupon_evidence_sha256=sha256_file(evidence),
            new_project_version="v02",
            output_spec_path=tmp_path / f"changed_{field}_output.json",
            workspace_root=tmp_path / "workspace",
        )


@pytest.mark.integration
def test_linked_full_part_rejects_cross_unit_raw_parameter_match(
    _configuration_mismatch_chain: tuple[Path, Path], tmp_path: Path
) -> None:
    source, evidence = _configuration_mismatch_chain
    document = json.loads(source.read_text(encoding="utf-8"))
    document["input_units"] = "inch"
    document["nozzle_diameter"] = 0.015748031496062992
    cross_unit_source = tmp_path / "cross_unit_source.json"
    cross_unit_source.write_text(json.dumps(document, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceValidationError, match="different or edited"):
        create_full_part_spec_from_coupon(
            cross_unit_source,
            passed_coupon_evidence_path=evidence,
            expected_coupon_evidence_sha256=sha256_file(evidence),
            new_project_version="v02",
            output_spec_path=tmp_path / "cross_unit_output.json",
            workspace_root=tmp_path / "workspace",
        )


@pytest.mark.integration
@pytest.mark.parametrize(
    "stale_field",
    ("intent", "measurement_contract", "verification_policy"),
)
def test_linked_full_part_rejects_stale_source_contract_or_policy(
    _configuration_mismatch_chain: tuple[Path, Path],
    tmp_path: Path,
    stale_field: str,
) -> None:
    source, evidence = _configuration_mismatch_chain
    document = json.loads(source.read_text(encoding="utf-8"))
    if stale_field == "intent":
        document["project"]["intent"] = "replacement"
    elif stale_field == "measurement_contract":
        document["measurement_contract"] = [
            {
                "parameter_name": "inside_diameter",
                "measured_value": 20,
                "units": "mm",
                "measurement_source": "synthetic fixture only",
                "authority": "authoritative",
                "confidence_level": "high",
                "tolerance": 0.01,
                "protected_interface": True,
                "verification_notes": "Automated fixture, not an owner measurement."
            }
        ]
    else:
        document["verification_policy"]["mesh_bounds_tolerance_mm"] = 0.1
    changed = tmp_path / f"stale_{stale_field}.json"
    changed.write_text(json.dumps(document, indent=2), encoding="utf-8")
    with pytest.raises(EvidenceValidationError, match="different or edited"):
        create_full_part_spec_from_coupon(
            changed,
            passed_coupon_evidence_path=evidence,
            expected_coupon_evidence_sha256=sha256_file(evidence),
            new_project_version="v02",
            output_spec_path=tmp_path / f"stale_{stale_field}_output.json",
            workspace_root=tmp_path / "workspace",
        )


@pytest.mark.integration
@pytest.mark.parametrize("replay_kind", ("different_project", "edited_source_bytes"))
def test_linked_full_part_rejects_origin_replay(
    _configuration_mismatch_chain: tuple[Path, Path],
    tmp_path: Path,
    replay_kind: str,
) -> None:
    source, evidence = _configuration_mismatch_chain
    replay_source = tmp_path / f"{replay_kind}.json"
    if replay_kind == "different_project":
        document = json.loads(source.read_text(encoding="utf-8"))
        document["project"]["id"] = "different_source_project"
        replay_source.write_text(json.dumps(document, indent=2), encoding="utf-8")
    else:
        replay_source.write_bytes(source.read_bytes() + b"\n")
    with pytest.raises(EvidenceValidationError, match="different or edited"):
        create_full_part_spec_from_coupon(
            replay_source,
            passed_coupon_evidence_path=evidence,
            expected_coupon_evidence_sha256=sha256_file(evidence),
            new_project_version="v02",
            output_spec_path=tmp_path / f"{replay_kind}_output.json",
        )


@pytest.mark.integration
def test_generation_rejects_a_tampered_linked_full_part_project_identity(
    _configuration_mismatch_chain: tuple[Path, Path], tmp_path: Path
) -> None:
    source, evidence = _configuration_mismatch_chain
    workspace_root = evidence.parents[2]
    linked = tmp_path / "linked_before_identity_tamper.json"
    create_full_part_spec_from_coupon(
        source,
        passed_coupon_evidence_path=evidence,
        expected_coupon_evidence_sha256=sha256_file(evidence),
        new_project_version="v02",
        output_spec_path=linked,
        workspace_root=workspace_root,
    )
    document = json.loads(linked.read_text(encoding="utf-8"))
    document["project"]["id"] = "replayed_under_another_project"
    tampered = tmp_path / "tampered_linked_project.json"
    tampered.write_text(json.dumps(document, indent=2), encoding="utf-8")

    with pytest.raises(SpecificationError, match="project ID"):
        prepare_spec_file(tampered, workspace_root=workspace_root)


@pytest.mark.integration
def test_linked_full_part_rejects_a_different_workspace_root(
    _configuration_mismatch_chain: tuple[Path, Path], tmp_path: Path
) -> None:
    source, evidence = _configuration_mismatch_chain
    with pytest.raises(EvidenceValidationError, match="exactly match"):
        create_full_part_spec_from_coupon(
            source,
            passed_coupon_evidence_path=evidence,
            expected_coupon_evidence_sha256=sha256_file(evidence),
            new_project_version="v02",
            output_spec_path=tmp_path / "wrong_workspace_output.json",
            workspace_root=tmp_path / "different_workspace",
        )


@pytest.mark.integration
@pytest.mark.parametrize("tampered_role", ("spec_snapshot", "fit_coupon_stl"))
def test_status_degrades_conservatively_for_tampered_base_artifacts(
    examples_dir: Path,
    tmp_path: Path,
    tampered_role: str,
) -> None:
    _, workspace, manifest = _generated_coupon(
        examples_dir, tmp_path, suffix=f"status_{tampered_role}"
    )
    manifest_document = json.loads(manifest.read_text(encoding="utf-8"))
    record = next(
        item
        for item in manifest_document["artifacts"]
        if item["role"] == tampered_role
    )
    artifact = workspace / record["path"]
    damaged = bytearray(artifact.read_bytes())
    damaged[0] ^= 1
    artifact.write_bytes(damaged)

    status = inspect_project_status(manifest.parent)
    assert status["base_artifact_integrity_valid"] is False
    assert status["highest_defensible_workflow_state"] == "draft"
    assert status["openscad_passed"] is False
    assert status["mesh_passed"] is False
    assert status["dimensions_reviewed"] is False
    assert status["physical_fit_claim_allowed"] is False
    assert status["evidence_errors"]
    if tampered_role == "spec_snapshot":
        assert status["specification_valid"] is False
    else:
        assert status["specification_valid"] is True
