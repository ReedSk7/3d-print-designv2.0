"""Compare two mesh files with basic extent and watertight reporting."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional


def format_extents(extents: object) -> str:
    try:
        values = [float(value) for value in extents]  # type: ignore[arg-type]
    except TypeError:
        return str(extents)
    return ", ".join(f"{value:.3f} mm" for value in values)


def load_mesh(mesh_path: Path):
    try:
        import trimesh
    except ImportError:
        print("trimesh is not installed. Install it with: pip install trimesh")
        return None

    try:
        return trimesh.load(mesh_path, force="mesh")
    except Exception as exc:  # pragma: no cover - defensive CLI handling
        print(f"Could not load '{mesh_path}': {exc}")
        return None


def watertight_status(mesh: object) -> str:
    value: Optional[bool] = getattr(mesh, "is_watertight", None)
    if value is None:
        return "unknown"
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two mesh files by overall extents."
    )
    parser.add_argument("mesh_a", help="Path to the first mesh")
    parser.add_argument("mesh_b", help="Path to the second mesh")
    args = parser.parse_args()

    path_a = Path(args.mesh_a)
    path_b = Path(args.mesh_b)

    missing = [str(path) for path in (path_a, path_b) if not path.is_file()]
    if missing:
        print("Missing mesh file(s):")
        for path in missing:
            print(f"- {path}")
        return 1

    mesh_a = load_mesh(path_a)
    if mesh_a is None:
        return 1

    mesh_b = load_mesh(path_b)
    if mesh_b is None:
        return 1

    extents_a = getattr(mesh_a, "extents", None)
    extents_b = getattr(mesh_b, "extents", None)

    print(f"Mesh A: {path_a}")
    print(f"  extents: {format_extents(extents_a)}")
    print(f"  watertight: {watertight_status(mesh_a)}")

    print(f"Mesh B: {path_b}")
    print(f"  extents: {format_extents(extents_b)}")
    print(f"  watertight: {watertight_status(mesh_b)}")

    if extents_a is not None and extents_b is not None:
        delta = [float(b) - float(a) for a, b in zip(extents_a, extents_b)]
        print(f"Extent delta (B - A): {format_extents(delta)}")
    else:
        print("Extent delta (B - A): unavailable")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
