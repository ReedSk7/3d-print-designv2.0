"""Readiness must bind a complete build to current inputs, without installing."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.workshop import readiness


def write_manifest(root):
    app = root / 'app'
    dist = app / 'dist'
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        'schema_version': 1,
        'inputs': {path.relative_to(app).as_posix(): digest(path)
                   for path in app.rglob('*') if path.is_file() and dist not in path.parents},
        'assets': {path.relative_to(dist).as_posix(): digest(path)
                   for path in dist.rglob('*') if path.is_file() and path.name != 'workshop-build.json'},
    }
    (dist / 'workshop-build.json').write_text(json.dumps(manifest), encoding='utf-8')


@pytest.fixture
def built_app(tmp_path):
    files = {
        'index.html': '<script type="module" src="/src/App.jsx"></script>',
        'package.json': '{}', 'package-lock.json': '{}', 'build.mjs': '// synthetic builder',
        'src/App.jsx': '// synthetic source',
        'dist/index.html': '<script type="module" src="/assets/app.js"></script><link rel="stylesheet" href="/assets/app.css">',
        'dist/assets/app.js': 'console.log("synthetic app")',
        'dist/assets/app.css': 'body {color:black}',
        'dist/.vite/manifest.json': json.dumps({'index.html': {'file': 'assets/app.js', 'isEntry': True, 'css': ['assets/app.css']}}),
    }
    for relative, content in files.items():
        path = tmp_path / 'app' / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    write_manifest(tmp_path)
    return tmp_path


def app_check(root):
    return next(item for item in readiness.check_readiness(root)['checks'] if item['name'] == 'app assets')


@pytest.fixture(autouse=True)
def isolate_environment(monkeypatch):
    monkeypatch.setattr(readiness, 'dependency_checks', lambda _: [])
    monkeypatch.setattr(readiness, 'find_openscad', lambda: Path('synthetic-openscad'))
    monkeypatch.setattr(readiness, 'openscad_version', lambda _: 'synthetic OpenSCAD')


def test_current_complete_build_passes(built_app):
    assert app_check(built_app)['status'] == 'pass'


@pytest.mark.parametrize('relative', ['src/App.jsx', 'package-lock.json', 'build.mjs'])
def test_changed_build_input_requires_rebuild(built_app, relative):
    (built_app / 'app' / relative).write_text('changed', encoding='utf-8')
    result = app_check(built_app)
    assert result['status'] == 'fail'
    assert 'setup.ps1' in result['corrective_action']


@pytest.mark.parametrize('relative', ['assets/app.js', 'assets/app.css', '.vite/manifest.json'])
def test_incomplete_build_is_not_ready(built_app, relative):
    (built_app / 'app/dist' / relative).unlink()
    assert app_check(built_app)['status'] == 'fail'


def test_index_without_build_manifest_is_not_ready(built_app):
    (built_app / 'app/dist/workshop-build.json').unlink()
    assert app_check(built_app)['status'] == 'fail'


def test_unsupported_worker_runtime_is_required_failure(built_app, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'linux')
    report = readiness.check_readiness(built_app)
    assert not report['ready']
    check = next(item for item in report['checks'] if item['name'] == 'worker runtime')
    assert check['status'] == 'fail'
    assert 'Windows' in check['detail']


@pytest.mark.parametrize('change', ['asset_tamper', 'asset_added', 'source_added', 'source_removed'])
def test_changed_file_inventory_is_not_ready(built_app, change):
    app = built_app / 'app'
    if change == 'asset_tamper':
        (app / 'dist/assets/app.js').write_text('changed bytes', encoding='utf-8')
    elif change == 'asset_added':
        (app / 'dist/assets/unrecorded.js').write_text('new bytes', encoding='utf-8')
    elif change == 'source_added':
        (app / 'src/new.jsx').write_text('// new input', encoding='utf-8')
    else:
        (app / 'src/App.jsx').unlink()
    assert app_check(built_app)['status'] == 'fail'


@pytest.mark.parametrize('text', ['{', '[]', '{"schema_version":1,"schema_version":1}',
                                '{"schema_version":true,"inputs":{},"assets":{}}'])
def test_malformed_build_metadata_fails_actionably(built_app, text):
    (built_app / 'app/dist/workshop-build.json').write_text(text, encoding='utf-8')
    result = app_check(built_app)
    assert result['status'] == 'fail'
    assert result['corrective_action']


@pytest.mark.parametrize('name', ['../outside.js', '/outside.js', r'C:\outside.js', 'assets/../outside.js'])
def test_build_manifest_cannot_choose_paths_to_read(built_app, name):
    path = built_app / 'app/dist/workshop-build.json'
    record = json.loads(path.read_text())
    record['assets'][name] = '0' * 64
    path.write_text(json.dumps(record), encoding='utf-8')
    assert app_check(built_app)['status'] == 'fail'


@pytest.mark.parametrize('relative', ['src/App.jsx', 'dist/assets/app.js', 'dist/workshop-build.json'])
def test_redirected_app_files_are_rejected(built_app, relative):
    target = built_app / 'app' / relative
    outside = built_app / 'outside'
    outside.write_bytes(target.read_bytes())
    target.unlink()
    try:
        target.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f'Symlink creation unavailable: {exc}')
    assert app_check(built_app)['status'] == 'fail'


@pytest.mark.parametrize('metadata', ['html', 'vite', 'entry', 'chunk'])
def test_even_rehashed_build_must_have_complete_asset_references(built_app, metadata):
    dist = built_app / 'app/dist'
    if metadata == 'html':
        (dist / 'index.html').write_text('<script type="module" src="/missing.js"></script>', encoding='utf-8')
    elif metadata == 'entry':
        (dist / 'index.html').write_text('<p>No app entry</p>', encoding='utf-8')
    else:
        path = dist / '.vite/manifest.json'
        graph = json.loads(path.read_text())
        graph['index.html']['css' if metadata == 'vite' else 'imports'] = ['missing']
        path.write_text(json.dumps(graph), encoding='utf-8')
    write_manifest(built_app)
    assert app_check(built_app)['status'] == 'fail'


def test_readiness_cli_reports_missing_dependencies_before_loading_server(repo_root):
    result = subprocess.run([sys.executable, '-S', '-B', str(repo_root / 'scripts/serve_workshop.py'), '--check-only'],
                            text=True, capture_output=True, timeout=30, cwd=repo_root)
    assert result.returncode == 1
    assert 'Traceback' not in result.stderr
    report = json.loads(result.stdout)
    assert not report['ready']
    assert any(item['status'] == 'fail' and 'Missing dependency' in item['detail'] for item in report['checks'])
