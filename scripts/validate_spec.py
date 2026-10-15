"""Validate a Parametric Part Workbench project specification."""

from __future__ import annotations

import argparse

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.workflow.pipeline import prepare_spec_file  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a deterministic Parametric Part Workbench specification."
    )
    parser.add_argument("--spec", required=True, help="Path to a v1 JSON project specification.")
    parser.add_argument(
        "--workspace-root",
        help="Workspace containing any fit-coupon evidence linked by the specification.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        prepared = prepare_spec_file(args.spec, workspace_root=args.workspace_root)
    except Exception as exc:
        print("SPECIFICATION INVALID")
        print(str(exc))
        return 1

    print("SPECIFICATION VALID")
    print(f"Project: {prepared.spec.project.id} ({prepared.spec.project.version})")
    print(
        "Generator: "
        f"{prepared.generator.metadata.generator_id} {prepared.generator.metadata.version}"
    )
    print(f"Generation mode: {prepared.spec.generation_mode.value}")
    print("Eligible next state: measurement_contract_complete")
    for warning in prepared.warnings:
        print(f"WARNING: {warning}")
    print("Physical fit: NOT CONFIRMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
