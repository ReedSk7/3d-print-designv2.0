"""Version-bound OpenSCAD renders. Images never constitute a fit/review result."""
from __future__ import annotations

import math
import struct
import tempfile
import zlib
from pathlib import Path

from core.workflow.openscad import (
    ERROR_DIAGNOSTIC, OpenSCADExecutionError, find_openscad,
    openscad_version, run_openscad_command,
)
from core.workflow.review import (
    file_record, publish_bundle, revision_directory, snapshot_generation, write_json,
)

CAMERA_PRESETS = {
    "iso": "0,0,0,55,0,35,220",
    "front": "0,0,0,90,0,0,220",
    "side": "0,0,0,90,0,90,220",
    "top": "0,0,0,0,0,0,220",
}


def validate_png(path: Path, size: tuple[int, int]) -> None:
    """Check PNG structure, CRCs, dimensions, and complete pixel stream."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Render did not produce a PNG.")
    pos, compressed, header, ended = 8, bytearray(), None, False
    while pos + 12 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        end = pos + 12 + length
        if end > len(data) or zlib.crc32(tag + payload) != struct.unpack(">I", data[end - 4:end])[0]:
            raise ValueError("Corrupt PNG chunk.")
        if header is None and tag != b"IHDR":
            raise ValueError("PNG must start with IHDR.")
        if tag == b"IHDR":
            if header is not None or len(payload) != 13:
                raise ValueError("Malformed PNG header.")
            header = struct.unpack(">IIBBBBB", payload)
        elif tag == b"IDAT":
            compressed.extend(payload)
        elif tag == b"IEND":
            ended = length == 0 and end == len(data)
            break
        pos = end
    if not ended or not header or tuple(header[:2]) != size:
        raise ValueError("Incomplete PNG or unexpected image dimensions.")
    width, height, depth, color, compression, filtering, interlace = header
    if depth != 8 or color not in (2, 6) or (compression, filtering, interlace) != (0, 0, 0):
        raise ValueError("Expected noninterlaced 8-bit RGB/RGBA OpenSCAD PNG.")
    row_bytes = 1 + width * (3 if color == 2 else 4)
    decoder = zlib.decompressobj()
    pixels = decoder.decompress(bytes(compressed), row_bytes * height + 1)
    if (len(pixels) != row_bytes * height or not decoder.eof or decoder.unused_data
            or any(pixels[i] > 4 for i in range(0, len(pixels), row_bytes))):
        raise ValueError("Malformed PNG pixel stream.")


def render_png(source: Path, output: Path, *, view: str, size=(1200, 900),
               camera: str | None = None, timeout_seconds=180) -> dict:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite PNG: {output}")
    if len(size) != 2 or any(isinstance(v, bool) or not isinstance(v, int) or not 64 <= v <= 4096 for v in size):
        raise ValueError("Image dimensions must be integers from 64 to 4096.")
    if camera is not None:
        values = tuple(float(v) for v in camera.split(","))
        if len(values) != 7 or not all(math.isfinite(v) for v in values) or values[-1] <= 0:
            raise ValueError("Detail camera requires seven finite values and positive distance.")
    executable = find_openscad()
    version = openscad_version(executable)
    camera = camera or CAMERA_PRESETS[view]
    args = [str(executable), "--render", "--projection=o", "--imgsize", f"{size[0]},{size[1]}",
            "--camera", camera]
    if view != "detail":
        args.extend(["--autocenter", "--viewall"])
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".render-", dir=output.parent) as temporary:
        png = Path(temporary) / "render.png"
        command = [*args, "-o", str(png), str(source.resolve())]
        result = run_openscad_command(command, timeout_seconds=timeout_seconds)
        diagnostics = result.stdout + "\n" + result.stderr
        if result.returncode or ERROR_DIAGNOSTIC.search(diagnostics) or not png.is_file():
            raise OpenSCADExecutionError(f"OpenSCAD render failed (exit {result.returncode}): {diagnostics.strip()}")
        validate_png(png, size)
        import os
        os.link(png, output)
    return {"view": view, "camera": camera, "projection": "orthographic", "size": list(size),
            "openscad_version": version, "executable": str(executable), "arguments": args[1:],
            "render_mode": "CGAL", "image": file_record(output)}


def export_previews(manifest: Path, *, revision="r01", size=(1200, 900), detail_camera=None) -> Path:
    generation, scad, _, _, _ = snapshot_generation(manifest)
    target = revision_directory(generation, "previews", revision)
    with tempfile.TemporaryDirectory(prefix=".ppw3-preview-", dir=generation.workspace_root) as directory:
        staging = Path(directory)
        source = staging / "source.scad"
        source.write_bytes(scad)
        views = [render_png(source, staging / f"{view}.png", view=view, size=size) for view in CAMERA_PRESETS]
        if detail_camera is not None:
            views.append(render_png(source, staging / "detail.png", view="detail", size=size, camera=detail_camera))
        # Source is already immutable in the version; do not duplicate it in the render bundle.
        source.unlink()
        write_json(staging / "preview-manifest.json", {
            "schema_version": "1.0", "source_manifest": generation.manifest_binding.to_dict(),
            "source_scad": generation.scad_binding.to_dict(), "source_stl": generation.stl_binding.to_dict(),
            "views": views, "automated_checks": "hashes, deterministic source, mesh, bounds, PNG structure",
            "agent_visual_review": "pending", "owner_review": "pending", "physical_fit_confirmed": False,
        })
        publish_bundle(staging, target, manifest_name="preview-manifest.json")
    return target / "preview-manifest.json"


def verify_preview_bundle(preview_manifest: Path) -> dict:
    """Recheck source/version and image hashes; never convert this into human review."""
    import json
    from core.models.artifacts import sha256_bytes
    document = json.loads(preview_manifest.read_text(encoding='utf-8'))
    if not isinstance(document, dict) or document.get('schema_version') != '1.0':
        raise ValueError('Unsupported preview manifest.')
    version_directory = preview_manifest.resolve().parents[2]
    generation, _, _, _, _ = snapshot_generation(version_directory / 'artifact-manifest.json')
    for key, binding in (('source_manifest', generation.manifest_binding),
                         ('source_scad', generation.scad_binding), ('source_stl', generation.stl_binding)):
        if document.get(key) != binding.to_dict():
            raise ValueError(f'Stale preview {key} binding.')
    views = document.get('views')
    if not isinstance(views, list) or not {v for v in CAMERA_PRESETS}.issubset(
            {item.get('view') for item in views if isinstance(item, dict)}):
        raise ValueError('Preview manifest is missing required views.')
    seen = set()
    for view in views:
        name = view['view']
        if name in seen or name not in (*CAMERA_PRESETS, 'detail'):
            raise ValueError('Duplicate or unknown preview view.')
        seen.add(name)
        record = view['image']
        if record['path'] != f'{name}.png':
            raise ValueError('Preview image path does not match its view.')
        path = (preview_manifest.parent / record['path']).resolve(strict=True)
        if path.parent != preview_manifest.parent.resolve():
            raise ValueError('Preview image escapes its bundle.')
        data = path.read_bytes()
        if len(data) != record['size_bytes'] or sha256_bytes(data) != record['sha256']:
            raise ValueError('Preview image size/SHA-256 mismatch.')
        validate_png(path, tuple(view['size']))
    return {'automated_checks': 'passed', 'agent_visual_review': 'not established by this check',
            'owner_review': 'not established by this check', 'physical_fit_confirmed': False}
