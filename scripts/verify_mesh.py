"""Re-run mesh QA and expected-bounds checks from an artifact manifest."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.models.artifacts import (  # noqa: E402
    ArtifactRecord,
    resolve_and_verify_artifact,
)
from core.validation.mesh import require_valid_mesh  # noqa: E402


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
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifacts = document["artifacts"]
        mesh_artifact_document = next(
            item for item in artifacts if item["role"] in {"stl_mesh", "fit_coupon_stl"}
        )
        mesh_artifact = ArtifactRecord.from_dict(mesh_artifact_document)
        workspace_root = manifest_path.parents[2].resolve()
        mesh_path = resolve_and_verify_artifact(
            mesh_artifact, workspace_root=workspace_root
        )
        expected = tuple(
            Decimal(str(value)) for value in document["checks"]["expected_bounds_mm"]
        )
        tolerance = Decimal(str(document["checks"]["mesh"]["bounds_tolerance_mm"]))
        body_count = int(document["checks"]["mesh"]["expected_body_count"])
        report = require_valid_mesh(
            mesh_path,
            expected_extents_mm=expected,
            bounds_tolerance_mm=tolerance,
            expected_body_count=body_count,
        )
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
