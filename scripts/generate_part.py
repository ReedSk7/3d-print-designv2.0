"""Generate, compile, and computationally validate one project specification."""

from __future__ import annotations

import argparse

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.workflow.pipeline import generate_project  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Parametric Part Workbench deterministic generator pipeline."
    )
    parser.add_argument("--spec", required=True, help="Path to a v1 JSON project specification.")
    parser.add_argument(
        "--workspace-root",
        help="Optional output root. Defaults to the ignored repository workspace directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = generate_project(args.spec, workspace_root=args.workspace_root)
    except Exception as exc:
        print("GENERATION FAILED")
        print(str(exc))
        print("Physical fit: NOT CONFIRMED")
        return 1

    print("GENERATION COMPLETE")
    print(f"Project: {result.spec.project.id} ({result.spec.project.version})")
    print(f"SCAD: {result.scad_path}")
    print(f"STL: {result.stl_path}")
    print(f"Artifact manifest: {result.manifest_path}")
    print(f"Reached state: {result.reached_state.value}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    print("Computational checks passed. Physical fit is not confirmed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
