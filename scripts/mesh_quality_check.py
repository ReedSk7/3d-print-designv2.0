"""Run strict mesh quality checks on an exported STL file."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check exported STL mesh quality.")
    parser.add_argument("stl_path", help="Path to the STL file to inspect.")
    parser.add_argument(
        "--allow-multiple-bodies",
        action="store_true",
        help="Allow more than one disconnected mesh body.",
    )
    parser.add_argument(
        "--max-body-count",
        type=int,
        default=1,
        help="Maximum disconnected body count when multiple bodies are not allowed.",
    )
    parser.add_argument(
        "--min-volume",
        type=float,
        default=0.001,
        help="Minimum absolute mesh volume in cubic millimeters.",
    )
    parser.add_argument(
        "--min-axis",
        type=float,
        default=0.01,
        help="Minimum nonzero bounding-box axis in millimeters.",
    )
    parser.add_argument(
        "--degenerate-area",
        type=float,
        default=1e-9,
        help="Face area at or below this threshold is treated as degenerate.",
    )
    return parser.parse_args()


def load_trimesh():
    try:
        import trimesh
    except ImportError:
        print("FAIL")
        print("Missing dependency: trimesh")
        print("Install with: py -3 -m pip install trimesh")
        return None
    return trimesh


def load_mesh(trimesh_module, stl_path: Path):
    try:
        loaded = trimesh_module.load(stl_path, force="mesh")
    except Exception as exc:
        print("FAIL")
        print(f"Could not load STL: {stl_path}")
        print(str(exc))
        return None

    if isinstance(loaded, trimesh_module.Scene):
        geometries = [geometry for geometry in loaded.geometry.values() if hasattr(geometry, "faces")]
        if not geometries:
            print("FAIL")
            print(f"No mesh geometry found in scene: {stl_path}")
            return None
        return trimesh_module.util.concatenate(tuple(geometries))

    return loaded


def finite_values(values: object) -> bool:
    try:
        return all(math.isfinite(float(value)) for value in values)  # type: ignore[arg-type]
    except TypeError:
        return False


def format_extents(extents: object) -> str:
    try:
        return " x ".join(f"{float(value):.3f}" for value in extents)  # type: ignore[arg-type]
    except TypeError:
        return str(extents)


def body_count(mesh) -> int:
    try:
        bodies = mesh.split(only_watertight=False)
    except Exception:
        return 0
    return len([body for body in bodies if len(getattr(body, "faces", [])) > 0])


def degenerate_face_count(mesh, area_threshold: float) -> int:
    areas = getattr(mesh, "area_faces", None)
    if areas is None:
        return 0
    return sum(1 for area in areas if float(area) <= area_threshold)


def run_mesh_quality_check(
    stl_path: Path,
    *,
    allow_multiple_bodies: bool = False,
    max_body_count: int = 1,
    min_volume: float = 0.001,
    min_axis: float = 0.01,
    degenerate_area: float = 1e-9,
) -> int:
    if not stl_path.is_file():
        print("FAIL")
        print(f"STL file not found: {stl_path}")
        return 1

    trimesh_module = load_trimesh()
    if trimesh_module is None:
        return 2

    mesh = load_mesh(trimesh_module, stl_path)
    if mesh is None:
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    vertex_count = len(getattr(mesh, "vertices", []))
    face_count = len(getattr(mesh, "faces", []))
    if getattr(mesh, "is_empty", False) or vertex_count == 0 or face_count == 0:
        errors.append("Mesh is empty or has no faces.")

    extents = getattr(mesh, "extents", None)
    if extents is None or not finite_values(extents):
        errors.append("Mesh extents are missing or non-finite.")
    elif any(float(axis) <= min_axis for axis in extents):
        errors.append(f"Mesh has a near-zero bounding-box axis: {format_extents(extents)} mm.")

    volume = float(getattr(mesh, "volume", 0.0) or 0.0)
    if not math.isfinite(volume) or abs(volume) <= min_volume:
        errors.append(f"Mesh volume is zero, non-finite, or below {min_volume} mm^3.")

    if not bool(getattr(mesh, "is_watertight", False)):
        errors.append("Mesh is not watertight; non-manifold or open edges are present.")

    if not bool(getattr(mesh, "is_winding_consistent", False)):
        errors.append("Mesh triangle winding is not consistent.")

    bodies = body_count(mesh)
    if bodies == 0:
        errors.append("Could not identify any connected mesh body.")
    elif not allow_multiple_bodies and bodies > max_body_count:
        errors.append(f"Mesh has {bodies} disconnected bodies; expected at most {max_body_count}.")

    degenerate_faces = degenerate_face_count(mesh, degenerate_area)
    if degenerate_faces:
        errors.append(f"Mesh contains {degenerate_faces} degenerate or near-zero-area faces.")

    if face_count < 4:
        errors.append("Mesh has too few faces to represent a closed printable solid.")

    print("PASS" if not errors else "FAIL")
    print(f"STL checked: {stl_path}")
    print(f"- vertices: {vertex_count}")
    print(f"- faces: {face_count}")
    print(f"- extents: {format_extents(extents)} mm")
    print(f"- volume: {volume:.6f} mm^3")
    print(f"- watertight: {bool(getattr(mesh, 'is_watertight', False))}")
    print(f"- winding_consistent: {bool(getattr(mesh, 'is_winding_consistent', False))}")
    print(f"- disconnected_bodies: {bodies}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    return 0 if not errors else 1


def main() -> int:
    args = parse_args()
    return run_mesh_quality_check(
        Path(args.stl_path),
        allow_multiple_bodies=args.allow_multiple_bodies,
        max_body_count=args.max_body_count,
        min_volume=args.min_volume,
        min_axis=args.min_axis,
        degenerate_area=args.degenerate_area,
    )


if __name__ == "__main__":
    raise SystemExit(main())
