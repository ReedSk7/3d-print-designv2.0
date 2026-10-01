"""Re-run mesh QA and expected-bounds checks from an artifact manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.workflow.review import snapshot_generation  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check an exported mesh against its machine-readable manifest."
    )
    parser.add_argument("--manifest", required=True, help="Path to artifact-manifest.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    try:
        generation, _, _, _, report = snapshot_generation(manifest_path)
        document = generation.manifest_document
        tolerance = report.bounds_tolerance_mm
    except Exception as exc:
        print("MESH CHECK FAILED")
        print(str(exc))
        print("Physical fit: NOT CONFIRMED")
        return 1

    print("MESH VALID")
    print(
        "Dimensions reviewed: actual bounds are within "
        f"{tolerance} mm computational tolerance."
    )
    print("Actual bounds (mm): " + " x ".join(str(value) for value in report.extents_mm))
    print(f"Manifest state: {document['workflow_state']}")
    print("Physical fit: NOT CONFIRMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
