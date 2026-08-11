"""Create a new draft full-part spec from passed coupon evidence."""

from __future__ import annotations

import argparse
import sys

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.evidence import create_full_part_spec_from_coupon  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new draft full-part version linked to immutable passed coupon evidence."
    )
    parser.add_argument("--source-spec", required=True, help="Original draft full-part specification.")
    parser.add_argument("--coupon-evidence", required=True, help="fit-result.evidence.json path.")
    parser.add_argument(
        "--coupon-evidence-sha256",
        required=True,
        help="Owner-recorded expected SHA-256 printed when the result evidence was created.",
    )
    parser.add_argument("--new-version", required=True)
    parser.add_argument("--output-spec", required=True)
    parser.add_argument(
        "--workspace-root",
        help=(
            "Optional target collision-check root; it must be the same workspace "
            "that contains the verified coupon and otherwise defaults to that root."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        output = create_full_part_spec_from_coupon(
            args.source_spec,
            passed_coupon_evidence_path=args.coupon_evidence,
            expected_coupon_evidence_sha256=args.coupon_evidence_sha256,
            new_project_version=args.new_version,
            output_spec_path=args.output_spec,
            workspace_root=args.workspace_root,
        )
    except Exception as exc:
        print("LINKED FULL-PART SPECIFICATION FAILED", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    print("LINKED FULL-PART SPECIFICATION CREATED")
    print(f"Specification: {output}")
    print("Reached state: draft")
    print("Run the ordinary generation pipeline; no computational gate was skipped.")
    print("Complete-part physical fit is not confirmed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
