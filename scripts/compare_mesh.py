"""Compare two mesh files with bbox and basic silhouette reporting."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional


VIEW_AXES = {
    "front": (0, 2),
    "side": (1, 2),
    "top": (0, 1),
}

VIEW_LABELS = {
    "front": "X/Z",
    "side": "Y/Z",
    "top": "X/Y",
}


def format_extents(extents: object) -> str:
    try:
        values = [float(value) for value in extents]  # type: ignore[arg-type]
    except TypeError:
        return str(extents)
    return ", ".join(f"{value:.3f} mm" for value in values)


def format_2d_extents(extents: object) -> str:
    try:
        values = [float(value) for value in extents]  # type: ignore[arg-type]
    except TypeError:
        return str(extents)
    if len(values) != 2:
        return format_extents(values)
    return f"{values[0]:.3f} mm x {values[1]:.3f} mm"


def load_mesh(mesh_path: Path):
    try:
        import trimesh
    except ImportError:
        print("trimesh is not installed. Install it with: pip install trimesh")
        return None

    try:
        mesh = trimesh.load(mesh_path, force="mesh")
    except Exception as exc:  # pragma: no cover - defensive CLI handling
        print(f"Could not load '{mesh_path}': {exc}")
        return None

    if isinstance(mesh, trimesh.Scene):
        geometries = [geometry for geometry in mesh.geometry.values() if hasattr(geometry, "faces")]
        if not geometries:
            print(f"Could not find any mesh geometry in '{mesh_path}'.")
            return None
        mesh = trimesh.util.concatenate(tuple(geometries))

    return mesh


def watertight_status(mesh: object) -> str:
    value: Optional[bool] = getattr(mesh, "is_watertight", None)
    if value is None:
        return "unknown"
    return "yes" if value else "no"


def centered_vertices(np_module, mesh):
    vertices = np_module.asarray(mesh.vertices, dtype=float)
    bounds = np_module.asarray(mesh.bounds, dtype=float)
    center = bounds.mean(axis=0)
    return vertices - center


def projected_extents(np_module, vertices, axes: tuple[int, int]):
    projected = vertices[:, axes]
    return projected.max(axis=0) - projected.min(axis=0)


def triangle_mask(np_module, points, triangle):
    signs = []
    for index in range(3):
        point_a = triangle[index]
        point_b = triangle[(index + 1) % 3]
        cross = (
            (points[..., 0] - point_a[0]) * (point_b[1] - point_a[1])
            - (points[..., 1] - point_a[1]) * (point_b[0] - point_a[0])
        )
        signs.append(cross)
    sign_stack = np_module.stack(signs, axis=0)
    has_negative = (sign_stack < 0).any(axis=0)
    has_positive = (sign_stack > 0).any(axis=0)
    return ~(has_negative & has_positive)


def rasterize_triangles(np_module, triangles, grid_size: int):
    canvas = np_module.zeros((grid_size, grid_size), dtype=bool)
    if len(triangles) == 0:
        return canvas

    all_points = triangles.reshape(-1, 2)
    mins = all_points.min(axis=0)
    maxs = all_points.max(axis=0)
    span = maxs - mins
    span[span == 0] = 1.0
    margin = 3.0

    scaled = (triangles - mins) / span
    scaled = scaled * (grid_size - 1 - (2 * margin)) + margin
    scaled[..., 1] = (grid_size - 1) - scaled[..., 1]

    for triangle in scaled:
        min_x = max(int(np_module.floor(triangle[:, 0].min())), 0)
        max_x = min(int(np_module.ceil(triangle[:, 0].max())), grid_size - 1)
        min_y = max(int(np_module.floor(triangle[:, 1].min())), 0)
        max_y = min(int(np_module.ceil(triangle[:, 1].max())), grid_size - 1)
        if min_x > max_x or min_y > max_y:
            continue

        xs = np_module.arange(min_x, max_x + 1) + 0.5
        ys = np_module.arange(min_y, max_y + 1) + 0.5
        grid_x, grid_y = np_module.meshgrid(xs, ys)
        points = np_module.stack((grid_x, grid_y), axis=-1)
        mask = triangle_mask(np_module, points, triangle)
        canvas[min_y : max_y + 1, min_x : max_x + 1] |= mask

    return canvas


def silhouette_stats(np_module, mesh_a, mesh_b, view_name: str, grid_size: int):
    axes = VIEW_AXES[view_name]
    vertices_a = centered_vertices(np_module, mesh_a)
    vertices_b = centered_vertices(np_module, mesh_b)
    faces_a = np_module.asarray(mesh_a.faces, dtype=int)
    faces_b = np_module.asarray(mesh_b.faces, dtype=int)

    triangles_a = vertices_a[faces_a][:, :, axes]
    triangles_b = vertices_b[faces_b][:, :, axes]
    mask_a = rasterize_triangles(np_module, triangles_a, grid_size)
    mask_b = rasterize_triangles(np_module, triangles_b, grid_size)

    area_a = int(mask_a.sum())
    area_b = int(mask_b.sum())
    overlap = int((mask_a & mask_b).sum())
    union = int((mask_a | mask_b).sum())
    a_only = int((mask_a & ~mask_b).sum())
    b_only = int((mask_b & ~mask_a).sum())
    iou = float(overlap / union) if union else 1.0

    return {
        "view": view_name,
        "axes_label": VIEW_LABELS[view_name],
        "extents_a": projected_extents(np_module, vertices_a, axes),
        "extents_b": projected_extents(np_module, vertices_b, axes),
        "area_a": area_a,
        "area_b": area_b,
        "overlap": overlap,
        "union": union,
        "a_only": a_only,
        "b_only": b_only,
        "iou": iou,
    }


def print_mesh_summary(label: str, mesh_path: Path, mesh) -> None:
    extents = getattr(mesh, "extents", None)
    print(f"{label}: {mesh_path}")
    print(f"  extents: {format_extents(extents)}")
    print(f"  watertight: {watertight_status(mesh)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two mesh files by bbox and projected silhouettes."
    )
    parser.add_argument("mesh_a", help="Path to the first mesh")
    parser.add_argument("mesh_b", help="Path to the second mesh")
    parser.add_argument(
        "--views",
        nargs="+",
        choices=tuple(VIEW_AXES.keys()),
        default=["front", "side", "top"],
        help="Projection views to compare. Defaults to front side top.",
    )
    parser.add_argument(
        "--grid-size",
        type=int,
        default=256,
        help="Silhouette raster grid size. Higher values are slower but more detailed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    path_a = Path(args.mesh_a)
    path_b = Path(args.mesh_b)

    missing = [str(path) for path in (path_a, path_b) if not path.is_file()]
    if missing:
        print("FAIL")
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

    try:
        import numpy as np
    except ImportError:
        print("numpy is not installed. Install it with: pip install numpy")
        return 1

    extents_a = getattr(mesh_a, "extents", None)
    extents_b = getattr(mesh_b, "extents", None)

    print("=== Mesh Comparison ===")
    print_mesh_summary("Mesh A", path_a, mesh_a)
    print_mesh_summary("Mesh B", path_b, mesh_b)

    print("")
    print("=== Bounding Box Delta (B - A) ===")
    if extents_a is not None and extents_b is not None:
        delta = [float(b) - float(a) for a, b in zip(extents_a, extents_b)]
        print(f"- overall extents delta: {format_extents(delta)}")
    else:
        print("- overall extents delta: unavailable")

    print("")
    print("=== Silhouette Comparison ===")
    for view_name in args.views:
        stats = silhouette_stats(np, mesh_a, mesh_b, view_name, args.grid_size)
        print(f"- {view_name} view ({stats['axes_label']})")
        print(f"  Mesh A projected extents: {format_2d_extents(stats['extents_a'])}")
        print(f"  Mesh B projected extents: {format_2d_extents(stats['extents_b'])}")
        print(f"  silhouette IoU: {stats['iou']:.4f}")
        print(f"  overlap pixels: {stats['overlap']} / {stats['union']}")
        print(f"  Mesh A only pixels: {stats['a_only']}")
        print(f"  Mesh B only pixels: {stats['b_only']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
