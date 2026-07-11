"""Render simple preview images from an STL file.

Dependencies:
- trimesh
- matplotlib

Install with:
    pip install trimesh matplotlib
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


VIEW_ANGLES = {
    "iso": {"elev": 28, "azim": -55},
    "front": {"elev": 0, "azim": -90},
    "side": {"elev": 0, "azim": 0},
    "top": {"elev": 90, "azim": -90},
}


def load_dependencies():
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        import numpy as np
        import trimesh
    except ImportError as exc:  # pragma: no cover - CLI dependency guard
        missing = getattr(exc, "name", "required package")
        raise SystemExit(
            f"Missing dependency '{missing}'. Install with: pip install trimesh matplotlib"
        ) from exc
    return plt, Poly3DCollection, np, trimesh


def resolve_output_dir(stl_path: Path, output_dir: Path | None) -> Path:
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    if stl_path.parent.name == "exports" and stl_path.parent.parent.exists():
        previews_dir = stl_path.parent.parent / "previews"
    else:
        previews_dir = stl_path.parent

    previews_dir.mkdir(parents=True, exist_ok=True)
    return previews_dir


def load_mesh(trimesh_module, stl_path: Path):
    mesh = trimesh_module.load(stl_path, force="mesh")
    if isinstance(mesh, trimesh_module.Scene):
        geometries = [
            geometry for geometry in mesh.geometry.values() if hasattr(geometry, "faces")
        ]
        if not geometries:
            raise SystemExit(f"No mesh geometry found in '{stl_path}'.")
        mesh = trimesh_module.util.concatenate(tuple(geometries))

    if mesh.is_empty:
        raise SystemExit(f"Loaded mesh is empty: '{stl_path}'.")

    return mesh


def normalized_vertices(np_module, mesh) -> tuple[object, object]:
    vertices = np_module.asarray(mesh.vertices, dtype=float)
    faces = np_module.asarray(mesh.faces, dtype=int)

    center = vertices.mean(axis=0)
    centered = vertices - center
    extents = centered.max(axis=0) - centered.min(axis=0)
    scale = float(extents.max()) or 1.0

    return centered / scale, faces


def face_collection(vertices, faces, poly_collection_class):
    triangles = vertices[faces]
    collection = poly_collection_class(
        triangles,
        facecolors="#bfc8cf",
        edgecolors="#4a535a",
        linewidths=0.15,
        alpha=1.0,
    )
    return collection


def render_view(
    plt,
    np_module,
    poly_collection_class,
    vertices,
    faces,
    view_name: str,
    destination: Path,
) -> None:
    figure = plt.figure(figsize=(6, 6), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    axis.add_collection3d(face_collection(vertices, faces, poly_collection_class))

    limit = float(np_module.abs(vertices).max()) + 0.1
    axis.set_xlim(-limit, limit)
    axis.set_ylim(-limit, limit)
    axis.set_zlim(-limit, limit)
    axis.set_box_aspect((1, 1, 1))
    axis.set_axis_off()

    angles = VIEW_ANGLES[view_name]
    axis.view_init(elev=angles["elev"], azim=angles["azim"])

    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    figure.tight_layout(pad=0)
    figure.savefig(destination, bbox_inches="tight", pad_inches=0.02)
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render simple preview images from STL.")
    parser.add_argument("stl_path", help="Path to the STL file to render")
    parser.add_argument(
        "--output-dir",
        help="Directory for preview images. Defaults to the project's previews/ folder.",
    )
    parser.add_argument(
        "--top",
        action="store_true",
        help="Also render a top preview image.",
    )
    return parser.parse_args()


def selected_views(include_top: bool) -> Iterable[str]:
    views = ["iso", "front", "side"]
    if include_top:
        views.append("top")
    return views


def main() -> int:
    args = parse_args()
    stl_path = Path(args.stl_path).resolve()
    if not stl_path.is_file():
        raise SystemExit(f"STL file not found: '{stl_path}'")

    output_dir = resolve_output_dir(
        stl_path, Path(args.output_dir).resolve() if args.output_dir else None
    )
    plt, poly_collection_class, np_module, trimesh_module = load_dependencies()
    mesh = load_mesh(trimesh_module, stl_path)
    vertices, faces = normalized_vertices(np_module, mesh)

    created_files: list[Path] = []
    for view_name in selected_views(args.top):
        destination = output_dir / f"{stl_path.stem}_{view_name}.png"
        render_view(
            plt,
            np_module,
            poly_collection_class,
            vertices,
            faces,
            view_name,
            destination,
        )
        created_files.append(destination)

    print("Created preview images:")
    for created_file in created_files:
        print(f"- {created_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
