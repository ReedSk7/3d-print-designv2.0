"""Inspect the highest defensible state for one generated project/version."""

from __future__ import annotations

import argparse
import json
import sys

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.evidence import inspect_project_status  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reverify a generated project/version status.")
    parser.add_argument("--project-version-dir", required=True)
    parser.add_argument(
        "--fit-evidence-sha256",
        help="Owner-recorded expected SHA-256 for fit-result.evidence.json.",
    )
    parser.add_argument(
        "--physical-evidence-sha256",
        help="Owner-recorded expected SHA-256 for physical-fit.evidence.json.",
    )
    parser.add_argument("--json", action="store_true", help="Print only machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        status = inspect_project_status(
            args.project_version_dir,
            expected_fit_evidence_sha256=args.fit_evidence_sha256,
            expected_physical_evidence_sha256=args.physical_evidence_sha256,
        )
    except Exception as exc:
        print("STATUS INSPECTION FAILED", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0
    print(f"Project: {status['project_id']} ({status['project_version']})")
    generator = status["generator"]
    print(f"Generator: {generator['id']} {generator['version']}")
    print(f"Specification valid: {str(status['specification_valid']).lower()}")
    print(
        "Base artifact integrity valid: "
        f"{str(status['base_artifact_integrity_valid']).lower()}"
    )
    print(f"OpenSCAD passed: {str(status['openscad_passed']).lower()}")
    print(f"Mesh passed: {str(status['mesh_passed']).lower()}")
    print(f"Dimensions reviewed: {str(status['dimensions_reviewed']).lower()}")
    print(f"Coupon evidence: {status['coupon_evidence_state']}")
    print(f"Physical-fit evidence: {status['physical_fit_evidence_state']}")
    print(f"Highest defensible state: {status['highest_defensible_workflow_state']}")
    print(
        'Phrase "physically verified" allowed: '
        f"{str(status['physical_fit_claim_allowed']).lower()}"
    )
    print("Artifact hashes:")
    for label, binding in status["artifact_hashes"].items():
        if binding is not None:
            print(f"  {label}: {binding['sha256']} ({binding['size_bytes']} bytes)")
    assumptions = status["unresolved_assumptions"]
    print("Unresolved assumptions: " + ("; ".join(assumptions) if assumptions else "none"))
    for error in status["evidence_errors"]:
        print(f"EVIDENCE ERROR: {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
