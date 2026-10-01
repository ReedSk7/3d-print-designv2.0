"""Regression tests for demonstrated discovery/publication/dimension defects."""
from decimal import Decimal
from pathlib import Path
import struct
import subprocess
import zlib

import pytest
import core.workflow.openscad as openscad
from core.validation.mesh import inspect_mesh
from core.workflow.preview import render_png, validate_png
from core.workflow.review import publish_bundle


def png_bytes(width=64, height=64):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\x00' + b'\x88\x77\x66' * width) * height)) + chunk(b'IEND', b''))


def test_invalid_explicit_openscad_does_not_fallback(monkeypatch, tmp_path):
    monkeypatch.setenv('OPENSCAD_PATH', str(tmp_path / 'missing.exe'))
    monkeypatch.setattr(openscad.shutil, 'which', lambda _: '/usr/bin/openscad')
    with pytest.raises(openscad.OpenSCADNotFound, match='not a file'):
        openscad.find_openscad()


def test_missing_openscad_is_required(monkeypatch):
    monkeypatch.delenv('OPENSCAD_PATH', raising=False)
    monkeypatch.setattr(openscad.shutil, 'which', lambda _: None)
    monkeypatch.setattr(openscad, 'WINDOWS_CANDIDATES', ())
    with pytest.raises(openscad.OpenSCADNotFound):
        openscad.find_openscad()


@pytest.mark.parametrize('failure', [subprocess.TimeoutExpired('openscad', 30), PermissionError('denied')])
def test_version_probe_errors_are_actionable(monkeypatch, failure):
    def fail(*a, **kw):
        raise failure
    monkeypatch.setattr(openscad.subprocess, 'run', fail)
    with pytest.raises(openscad.OpenSCADExecutionError):
        openscad.openscad_version(Path('path with spaces/openscad.com'))


def fake_compiler(monkeypatch, tmp_path, output, *, collide=False, error=False):
    executable = tmp_path / 'Program Files' / 'OpenSCAD' / 'openscad.com'
    executable.parent.mkdir(parents=True)
    executable.write_text('fixture')
    monkeypatch.setenv('OPENSCAD_PATH', str(executable))
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        assert kwargs['shell'] is False and kwargs['timeout'] > 0
        if '--version' in command:
            return subprocess.CompletedProcess(command, 0, 'OpenSCAD test', '')
        Path(command[command.index('-o') + 1]).write_bytes(b'\0' * 134)
        if collide:
            output.write_bytes(b'concurrent owner artifact')
        return subprocess.CompletedProcess(command, 0, '', 'ERROR: bad source' if error else '')
    monkeypatch.setattr(openscad.subprocess, 'run', run)
    return calls, executable


def test_stl_race_never_overwrites_other_file(tmp_path, monkeypatch):
    source, output = tmp_path / 'source with spaces.scad', tmp_path / 'output.stl'
    source.write_text('cube(1);')
    fake_compiler(monkeypatch, tmp_path, output, collide=True)
    with pytest.raises(FileExistsError):
        openscad.compile_binary_stl(source, output)
    assert output.read_bytes() == b'concurrent owner artifact'
    assert not list(tmp_path.glob('*.tmp.stl'))


def test_compile_paths_with_spaces_and_error_diagnostics(tmp_path, monkeypatch):
    source, output = tmp_path / 'source with spaces.scad', tmp_path / 'mesh with spaces.stl'
    source.write_text('cube(1);')
    calls, executable = fake_compiler(monkeypatch, tmp_path, output, error=True)
    with pytest.raises(openscad.OpenSCADExecutionError, match='bad source'):
        openscad.compile_binary_stl(source, output)
    assert calls[-1][0] == str(executable) and calls[-1][-1] == str(source)
    assert not output.exists()


@pytest.mark.parametrize('bounds,tolerance', [
    ((), '0.05'), (('1','2'), '0.05'), (('1','2','NaN'), '0.05'),
    (('1','2','3'), 'Infinity'), (('1','2','3'), '-0.1'), (('0','2','3'), '0.05'),
])
def test_malformed_dimension_policy_blocks_even_before_mesh_load(tmp_path, bounds, tolerance):
    with pytest.raises(ValueError):
        inspect_mesh(tmp_path / 'irrelevant.stl', expected_extents_mm=tuple(map(Decimal, bounds)),
                     bounds_tolerance_mm=Decimal(tolerance))


@pytest.mark.parametrize('damage', ['truncated', 'crc', 'dimensions'])
def test_png_validation_rejects_malformed_files(tmp_path, damage):
    data = png_bytes()
    if damage == 'truncated': data = data[:-6]
    if damage == 'crc': data = data[:50] + bytes([data[50] ^ 1]) + data[51:]
    path = tmp_path / 'render.png'; path.write_bytes(data)
    with pytest.raises(ValueError):
        validate_png(path, (128, 64) if damage == 'dimensions' else (64, 64))


@pytest.mark.parametrize('behavior', ['missing', 'error', 'timeout'])
def test_render_failure_cannot_publish_stale_image(tmp_path, monkeypatch, behavior):
    import core.workflow.preview as preview
    source = tmp_path / 'source.scad'; source.write_text('cube(1);')
    output = tmp_path / 'view.png'
    monkeypatch.setattr(preview, 'find_openscad', lambda: Path('OpenSCAD path/openscad'))
    monkeypatch.setattr(preview, 'openscad_version', lambda _: 'fixture')
    def run(command, **kw):
        if behavior == 'timeout': raise openscad.OpenSCADExecutionError('timed out')
        if behavior == 'error': Path(command[command.index('-o')+1]).write_bytes(png_bytes())
        return subprocess.CompletedProcess(command, 0, '', 'ERROR: fixture failure' if behavior == 'error' else '')
    monkeypatch.setattr(preview, 'run_openscad_command', run)
    with pytest.raises(openscad.OpenSCADExecutionError):
        render_png(source, output, view='top', size=(64,64))
    assert not output.exists()
    output.write_bytes(b'old image')
    with pytest.raises(FileExistsError): render_png(source, output, view='top')
    assert output.read_bytes() == b'old image'


def test_bundle_cannot_replace_even_empty_competing_directory(tmp_path):
    staging, target = tmp_path/'stage', tmp_path/'out'
    staging.mkdir(); target.mkdir()
    (staging/'manifest.json').write_text('{}')
    with pytest.raises(FileExistsError): publish_bundle(staging, target, manifest_name='manifest.json')
    assert list(target.iterdir()) == []
