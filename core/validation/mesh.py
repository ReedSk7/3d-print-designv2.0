"""Structured mesh quality and expected-bounds checks."""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable


AXIS_NAMES = ("x", "y", "z")


class MeshDependencyError(RuntimeError):
    pass


class MeshValidationError(ValueError):
    def __init__(self, report: "MeshReport") -> None:
        self.report = report
        super().__init__("; ".join(report.errors))


@dataclass(frozen=True, slots=True)
class MeshReport:
    path: Path
    vertex_count: int
    face_count: int
    body_count: int
    volume_mm3: float
    area_mm2: float
    extents_mm: tuple[Decimal, Decimal, Decimal]
    watertight: bool
    winding_consistent: bool
    is_volume: bool
    degenerate_face_count: int
    expected_extents_mm: tuple[Decimal, Decimal, Decimal] | None
    bounds_delta_mm: tuple[Decimal, Decimal, Decimal] | None
    bounds_tolerance_mm: Decimal | None
    errors: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path.as_posix(),
            "vertex_count": self.vertex_count,
            "face_count": self.face_count,
            "body_count": self.body_count,
            "volume_mm3": self.volume_mm3,
            "area_mm2": self.area_mm2,
            "extents_mm": [str(value) for value in self.extents_mm],
            "watertight": self.watertight,
            "winding_consistent": self.winding_consistent,
            "is_volume": self.is_volume,
            "degenerate_face_count": self.degenerate_face_count,
            "expected_extents_mm": (
                [str(value) for value in self.expected_extents_mm]
                if self.expected_extents_mm is not None
                else None
            ),
            "bounds_delta_mm": (
                [str(value) for value in self.bounds_delta_mm]
                if self.bounds_delta_mm is not None
                else None
            ),
            "bounds_tolerance_mm": (
                str(self.bounds_tolerance_mm)
                if self.bounds_tolerance_mm is not None
                else None
            ),
            "passed": self.passed,
            "errors": list(self.errors),
        }


def _decimal_tuple(values: Iterable[object]) -> tuple[Decimal, Decimal, Decimal]:
    converted = tuple(Decimal(str(float(value))) for value in values)
    if len(converted) != 3:
        raise ValueError("Mesh extents must contain exactly three axes.")
    return converted  # type: ignore[return-value]


def inspect_mesh(
    path: Path,
    *,
    expected_extents_mm: tuple[Decimal, Decimal, Decimal] | None = None,
    bounds_tolerance_mm: Decimal | None = None,
    expected_body_count: int = 1,
    min_volume_mm3: float = 0.001,
    min_axis_mm: float = 0.01,
    degenerate_area_mm2: float = 1e-9,
) -> MeshReport:
    """Inspect a mesh and return every computational failure found."""

    try:
        import numpy as np
        import trimesh
    except ImportError as exc:  # pragma: no cover - exercised by dependency gate
        raise MeshDependencyError(
            "Mesh checks require numpy, trimesh, and networkx from requirements.txt."
        ) from exc

    mesh_path = path.resolve()
    if not mesh_path.is_file():
        raise FileNotFoundError(f"Mesh file not found: {mesh_path}")
    try:
        loaded = trimesh.load(mesh_path, force="mesh")
    except Exception as exc:
        raise MeshValidationError(
            MeshReport(
                path=mesh_path,
                vertex_count=0,
                face_count=0,
                body_count=0,
                volume_mm3=0,
                area_mm2=0,
                extents_mm=(Decimal("0"), Decimal("0"), Decimal("0")),
                watertight=False,
                winding_consistent=False,
                is_volume=False,
                degenerate_face_count=0,
                expected_extents_mm=expected_extents_mm,
                bounds_delta_mm=None,
                bounds_tolerance_mm=bounds_tolerance_mm,
                errors=(f"Could not load mesh: {exc}",),
            )
        ) from exc

    if isinstance(loaded, trimesh.Scene):
        geometries = [
            geometry
            for geometry in loaded.geometry.values()
            if len(getattr(geometry, "faces", ())) > 0
        ]
        if not geometries:
            raise ValueError(f"No mesh geometry found in scene: {mesh_path}")
        mesh = trimesh.util.concatenate(tuple(geometries))
    else:
        mesh = loaded

    errors: list[str] = []
    vertices = np.asarray(getattr(mesh, "vertices", ()), dtype=float)
    faces = np.asarray(getattr(mesh, "faces", ()), dtype=int)
    vertex_count = len(vertices)
    face_count = len(faces)
    if getattr(mesh, "is_empty", False) or vertex_count == 0 or face_count == 0:
        errors.append("Mesh is empty or has no faces.")
    if vertex_count and not bool(np.isfinite(vertices).all()):
        errors.append("Mesh contains non-finite vertex coordinates.")

    raw_extents = getattr(mesh, "extents", (0, 0, 0))
    try:
        extents = _decimal_tuple(raw_extents)
    except (TypeError, ValueError):
        extents = (Decimal("0"), Decimal("0"), Decimal("0"))
        errors.append("Mesh extents are missing or malformed.")
    if any(not value.is_finite() or value <= Decimal(str(min_axis_mm)) for value in extents):
        errors.append(f"Mesh has a non-finite or near-zero axis: {extents} mm.")

    volume = float(getattr(mesh, "volume", 0.0) or 0.0)
    area = float(getattr(mesh, "area", 0.0) or 0.0)
    if not math.isfinite(volume) or volume <= min_volume_mm3:
        errors.append(f"Mesh volume must exceed {min_volume_mm3} mm^3 and be positive.")
    if not math.isfinite(area) or area <= 0:
        errors.append("Mesh area must be finite and positive.")

    watertight = bool(getattr(mesh, "is_watertight", False))
    winding = bool(getattr(mesh, "is_winding_consistent", False))
    is_volume = bool(getattr(mesh, "is_volume", False))
    if not watertight:
        errors.append("Mesh is not watertight.")
    if not winding:
        errors.append("Mesh triangle winding is inconsistent.")
    if not is_volume:
        errors.append("Mesh does not represent a consistently oriented positive volume.")

    try:
        bodies = [body for body in mesh.split(only_watertight=False) if len(body.faces) > 0]
        body_count = len(bodies)
    except Exception as exc:
        raise MeshDependencyError(f"Could not split mesh into connected bodies: {exc}") from exc
    if body_count != expected_body_count:
        errors.append(
            f"Mesh has {body_count} connected bodies; expected exactly {expected_body_count}."
        )

    face_areas = np.asarray(getattr(mesh, "area_faces", ()), dtype=float)
    if len(face_areas) and not bool(np.isfinite(face_areas).all()):
        errors.append("Mesh contains non-finite face areas.")
    degenerate_count = int(np.count_nonzero(face_areas <= degenerate_area_mm2))
    if degenerate_count:
        errors.append(f"Mesh contains {degenerate_count} degenerate faces.")
    if face_count < 4:
        errors.append("Mesh has too few faces for a closed solid.")

    delta: tuple[Decimal, Decimal, Decimal] | None = None
    if expected_extents_mm is not None:
        if bounds_tolerance_mm is None:
            raise ValueError("bounds_tolerance_mm is required with expected extents.")
        delta = tuple(
            actual - expected for actual, expected in zip(extents, expected_extents_mm)
        )  # type: ignore[assignment]
        for axis, difference in zip(AXIS_NAMES, delta):
            if abs(difference) > bounds_tolerance_mm:
                errors.append(
                    f"{axis.upper()} extent delta {difference} mm exceeds computational "
                    f"tolerance {bounds_tolerance_mm} mm."
                )

    return MeshReport(
        path=mesh_path,
        vertex_count=vertex_count,
        face_count=face_count,
        body_count=body_count,
        volume_mm3=volume,
        area_mm2=area,
        extents_mm=extents,
        watertight=watertight,
        winding_consistent=winding,
        is_volume=is_volume,
        degenerate_face_count=degenerate_count,
        expected_extents_mm=expected_extents_mm,
        bounds_delta_mm=delta,
        bounds_tolerance_mm=bounds_tolerance_mm,
        errors=tuple(errors),
    )


def require_valid_mesh(*args: object, **kwargs: object) -> MeshReport:
    report = inspect_mesh(*args, **kwargs)  # type: ignore[arg-type]
    if not report.passed:
        raise MeshValidationError(report)
    return report
