"""Create a fit-coupon specification, optionally running generation explicitly."""

from __future__ import annotations

import argparse
import sys

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.evidence import create_fit_coupon_spec  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an immutable new fit-coupon specification.")
    parser.add_argument("--source-spec", required=True, help="Existing draft full-part specification.")
    parser.add_argument("--interface", required=True, help="Generator-declared coupon interface path.")
    parser.add_argument(
        "--candidate-offset",
        required=True,
        action="append",
        help="Explicit candidate offset in the source specification input units; repeat 2-12 times.",
    )
    parser.add_argument("--coupon-project-id", required=True)
    parser.add_argument("--coupon-version", required=True)
    parser.add_argument("--output-spec", required=True)
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Explicitly generate the coupon after its specification is created.",
    )
    parser.add_argument(
        "--workspace-root",
        help="Optional collision/generation root; defaults to the ignored repository workspace.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        output = create_fit_coupon_spec(
            args.source_spec,
            interface_parameter=args.interface,
            candidate_offsets=args.candidate_offset,
            coupon_project_id=args.coupon_project_id,
            coupon_project_version=args.coupon_version,
            output_spec_path=args.output_spec,
            generate=args.generate,
            workspace_root=args.workspace_root,
        )
    except Exception as exc:
        print("COUPON SPECIFICATION FAILED", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    print("COUPON SPECIFICATION CREATED")
    print(f"Specification: {output}")
    print(f"Coupon generated: {'yes' if args.generate else 'no'}")
    print("No printed result or complete-part physical fit is implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
