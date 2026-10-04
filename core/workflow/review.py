"""Read and recheck one immutable version for previews and slicer handoff."""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from core.evidence.service import verify_generation_manifest
from core.models.artifacts import sha256_bytes
from core.validation.mesh import require_valid_mesh
from core.workflow.pipeline import prepare_generation
from core.workflow.publication import publish_bundle


def read_binding(binding, root: Path) -> bytes:
    path = (root / binding.path).resolve(strict=True)
    path.relative_to(root.resolve())
    data = path.read_bytes()
    if len(data) != binding.size_bytes or sha256_bytes(data) != binding.sha256:
        raise ValueError(f"Artifact changed during review: {binding.path}")
    return data


def snapshot_generation(manifest: Path):
    """Return verified bytes, never reopen unchecked mutable paths for export."""
    generation = verify_generation_manifest(manifest)
    prepared = prepare_generation(generation.spec, workspace_root=generation.workspace_root)
    scad = read_binding(generation.scad_binding, generation.workspace_root)
    stl = read_binding(generation.stl_binding, generation.workspace_root)
    spec = read_binding(generation.specification_binding, generation.workspace_root)
    if scad != prepared.generation.source.encode("utf-8"):
        raise ValueError("SCAD does not match the selected deterministic generator/version.")
    checks = generation.manifest_document["checks"]
    # Reconstruct policy from the spec, rather than trusting editable manifest values.
    from decimal import Decimal
    expected = tuple(Decimal(str(v)) for v in checks["expected_bounds_mm"])
    tolerance = Decimal(str(checks["mesh"]["bounds_tolerance_mm"]))
    body_count = checks["mesh"]["expected_body_count"]
    if expected != prepared.generation.expected_bounds_mm:
        raise ValueError("Manifest expected bounds disagree with the source specification.")
    if tolerance != generation.spec.verification_policy.mesh_bounds_tolerance_mm:
        raise ValueError("Manifest tolerance disagrees with the source specification.")
    if body_count != prepared.generation.expected_body_count or isinstance(body_count, bool):
        raise ValueError("Manifest body count disagrees with the generator.")
    with tempfile.TemporaryDirectory(prefix=".ppw3-review-", dir=generation.workspace_root) as directory:
        mesh = Path(directory) / "mesh.stl"
        mesh.write_bytes(stl)
        report = require_valid_mesh(mesh, expected_extents_mm=expected,
                                    bounds_tolerance_mm=tolerance, expected_body_count=body_count)
    return generation, scad, stl, spec, report


def revision_directory(generation, kind: str, revision: str) -> Path:
    if not re.fullmatch(r"r[0-9]{2,4}", revision):
        raise ValueError("Revision must be r01 through r9999.")
    target = generation.version_directory / kind / revision
    target.resolve().relative_to(generation.version_directory)
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Refusing to overwrite review/handoff revision: {target}")
    return target


def write_json(path: Path, document: dict) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")




def file_record(path: Path) -> dict:
    data = path.read_bytes()
    return {"path": path.name, "sha256": sha256_bytes(data), "size_bytes": len(data)}
