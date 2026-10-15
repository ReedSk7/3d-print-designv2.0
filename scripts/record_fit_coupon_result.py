"""Record one immutable printed fit-coupon result."""

from __future__ import annotations

import argparse
import sys

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.evidence import record_fit_coupon_result, verify_fit_coupon_result  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bind a printed coupon result to exact artifacts.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--selected-offset-mm", required=True)
    parser.add_argument("--tester", required=True)
    parser.add_argument("--tested-at", required=True, help="Timezone-aware ISO-8601 date-time.")
    parser.add_argument("--acceptance-criterion", required=True)
    parser.add_argument("--observed-result", required=True)
    parser.add_argument("--notes", default="")
    outcome = parser.add_mutually_exclusive_group(required=True)
    outcome.add_argument("--passed", action="store_true")
    outcome.add_argument("--failed", action="store_true")
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Reject rather than write when the supplied outcome is failed.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        output = record_fit_coupon_result(
            args.manifest,
            expected_manifest_sha256=args.manifest_sha256,
            selected_candidate_offset_mm=args.selected_offset_mm,
            tested_by=args.tester,
            tested_at=args.tested_at,
            acceptance_criterion=args.acceptance_criterion,
            observed_result=args.observed_result,
            notes=args.notes,
            passed=args.passed,
            require_passed=args.require_passed,
        )
        verified = verify_fit_coupon_result(output)
    except Exception as exc:
        print("FIT RESULT RECORDING FAILED", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    print("FIT RESULT RECORDED")
    print(f"Evidence: {output}")
    print(f"Evidence SHA-256: {verified.evidence_binding.sha256}")
    print(f"Reached state: {verified.evidence.defensible_workflow_state.value}")
    if verified.evidence.result.passed:
        print("The coupon passed its recorded criterion.")
    else:
        print("The coupon failed; this evidence cannot be used to create a linked full part.")
    print("A coupon result does not confirm complete-part physical fit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
