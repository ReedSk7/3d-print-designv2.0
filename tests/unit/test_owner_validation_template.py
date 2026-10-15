from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = (
    ROOT
    / "owner-validation"
    / "templates"
    / "bambu_p2s_petg_bushing_inside_fit.template.json"
)
COUPON_INPUTS_TEMPLATE = (
    ROOT
    / "owner-validation"
    / "templates"
    / "bambu_p2s_petg_bushing_coupon_inputs.template.json"
)
PHYSICAL_RESULTS_TEMPLATE = (
    ROOT
    / "owner-validation"
    / "templates"
    / "bushing_physical_interface_results.template.json"
)
OWNER_GUIDE = ROOT / "docs" / "OWNER_FIT_VALIDATION.md"


def test_owner_template_requires_real_measurements_and_five_offsets() -> None:
    document = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    schema = json.loads(
        (ROOT / "schemas" / "project-spec-v1.schema.json").read_text(encoding="utf-8")
    )

    assert set(document).issubset(schema["properties"])
    assert set(schema["required"]).issubset(document)
    assert document["generator"]["id"] == "bushing"
    assert document["generator"]["version"] == "1.1.0"
    assert document["printer_profile"] == "bambu_lab_p2s_owner_local"
    assert document["material"] == "PETG"
    assert document["fit_profile"] == "neutral_unverified_starter"

    nozzle = document["nozzle_diameter"]
    measured = document["measurement_contract"][0]["measured_value"]
    coupon_inputs = json.loads(COUPON_INPUTS_TEMPLATE.read_text(encoding="utf-8"))
    offsets = coupon_inputs["candidate_offsets_mm"]

    assert isinstance(nozzle, str) and nozzle.startswith("OWNER MUST ENTER")
    assert isinstance(measured, str) and measured.startswith("OWNER MUST ENTER")
    assert coupon_inputs["interface_parameter"] == "inside_diameter"
    assert len(offsets) == 5
    assert all(
        isinstance(offset, str) and offset.startswith("OWNER MUST ENTER")
        for offset in offsets
    )


def test_owner_template_contains_no_claim_of_completed_physical_fit() -> None:
    document = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    assert document["workflow_state"] == "draft"
    assert document["physical_verification"]["status"] == "not_confirmed"
    assert document["physical_verification"]["confirmed_at"] is None
    assert document["physical_verification"]["confirmed_by"] is None


def test_physical_results_template_requires_both_bushing_interfaces() -> None:
    results = json.loads(PHYSICAL_RESULTS_TEMPLATE.read_text(encoding="utf-8"))

    assert {result["interface_parameter"] for result in results} == {
        "inside_diameter",
        "outside_diameter",
    }
    assert all(
        isinstance(result["passed"], str)
        and result["passed"].startswith("OWNER MUST ENTER")
        for result in results
    )


def test_owner_guide_carries_external_evidence_digests_through_the_loop() -> None:
    guide = OWNER_GUIDE.read_text(encoding="utf-8")

    assert "external integrity anchor" in guide
    assert "$couponEvidenceSha" in guide
    assert "--coupon-evidence-sha256 $couponEvidenceSha" in guide
    assert "--fit-evidence-sha256 $couponEvidenceSha" in guide
    assert "$physicalEvidenceSha" in guide
    assert "--physical-evidence-sha256 $physicalEvidenceSha" in guide
