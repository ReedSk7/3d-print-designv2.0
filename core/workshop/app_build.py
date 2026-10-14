"""Validate local Vite output against current source and every emitted byte.

The build record detects stale/incomplete output; it is not a signing authority.
Both source and output inventories are independently enumerated, so manifest
paths never choose files to read outside the app directory.
"""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

BUILD_RECORD = 'workshop-build.json'
VITE_RECORD = '.vite/manifest.json'
SOURCE_EXCLUDES = {'dist', 'node_modules'}
REBUILD_ACTION = 'Run .\\scripts\\setup.ps1, or run npm ci followed by npm run build in app/.'


def _safe_relative(value: str) -> bool:
    return (isinstance(value, str) and bool(value) and '\\' not in value and ':' not in value
            and not value.startswith('/') and all(part not in ('', '.', '..') for part in value.split('/'))
            and PurePosixPath(value).as_posix() == value)


def _plain_path(path: Path) -> None:
    if path.is_symlink() or path.is_junction():
        raise ValueError('App source and output must not contain symlinks or junctions.')


def _snapshot(directory: Path, *, excluded: set[str]) -> dict[str, str]:
    _plain_path(directory)
    if not directory.is_dir():
        raise ValueError('App source or build directory is missing.')
    result = {}

    def visit(folder: Path) -> None:
        for path in sorted(folder.iterdir()):
            relative = path.relative_to(directory).as_posix()
            if relative in excluded:
                continue
            _plain_path(path)
            if not _safe_relative(relative):
                raise ValueError('App files must use safe relative paths.')
            if path.is_dir():
                visit(path)
            elif path.is_file():
                result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                raise ValueError('App source and output must contain only regular files.')

    visit(directory)
    return result


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Build metadata contains duplicate keys.')
        result[key] = value
    return result


def _read_json(path: Path):
    _plain_path(path)
    if path.stat().st_size > 1024 * 1024:
        raise ValueError('Build metadata exceeds 1 MiB.')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)


def _validate_inventory(record, actual: dict[str, str], label: str) -> None:
    if not isinstance(record, dict) or not record:
        raise ValueError(f'Build {label} inventory is missing or empty.')
    if any(not _safe_relative(name) or not isinstance(digest, str)
           or not re.fullmatch(r'[0-9a-f]{64}', digest) for name, digest in record.items()):
        raise ValueError(f'Build {label} inventory contains an invalid path or SHA-256.')
    if record != actual:
        raise ValueError(f'Build {label} changed, are missing, or include unrecorded files; rebuild the app.')


class _HTMLAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.module_scripts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'script':
            source = attributes.get('src')
            if source:
                self.references.append(source)
                if attributes.get('type') == 'module':
                    self.module_scripts.append(source)
        elif tag == 'link' and attributes.get('href'):
            source = attributes['href']
            if not (attributes.get('rel') == 'icon' and source.startswith('data:')):
                self.references.append(source)


def _html_asset_path(reference: str) -> str:
    url = urlsplit(reference)
    path = unquote(url.path)
    if url.scheme or url.netloc or path.startswith('//'):
        raise ValueError('Built HTML must reference local app assets only.')
    path = path.removeprefix('/')
    if not _safe_relative(path):
        raise ValueError('Built HTML has an unsafe asset reference.')
    return path


def _validate_references(dist: Path, assets: dict[str, str]) -> None:
    if 'index.html' not in assets or VITE_RECORD not in assets:
        raise ValueError('Build is missing index.html or the Vite asset graph.')
    graph = _read_json(dist / VITE_RECORD)
    if not isinstance(graph, dict) or not graph:
        raise ValueError('Vite asset graph is invalid.')
    for record in graph.values():
        if not isinstance(record, dict) or record.get('file') not in assets:
            raise ValueError('Vite asset graph references a missing output file.')
        for field in ('css', 'assets'):
            values = record.get(field, [])
            if not isinstance(values, list) or any(not isinstance(name, str) or name not in assets for name in values):
                raise ValueError('Vite asset graph references missing CSS or media.')
        for field in ('imports', 'dynamicImports'):
            values = record.get(field, [])
            if not isinstance(values, list) or any(not isinstance(name, str) or name not in graph for name in values):
                raise ValueError('Vite asset graph references a missing chunk.')
    entry = graph.get('index.html')
    if not isinstance(entry, dict) or entry.get('isEntry') is not True:
        raise ValueError('Vite asset graph has no app entry.')
    html = _HTMLAssets()
    html.feed((dist / 'index.html').read_text(encoding='utf-8'))
    if any(_html_asset_path(reference) not in assets for reference in html.references):
        raise ValueError('Built HTML references a missing asset.')
    if entry['file'] not in {_html_asset_path(reference) for reference in html.module_scripts}:
        raise ValueError('Built HTML does not load the Vite app entry.')


def validate_app_build(root: Path) -> dict[str, str]:
    """Raise on a stale, incomplete or redirected build; never install anything."""
    app = root / 'app'
    dist = app / 'dist'
    _plain_path(app)
    _plain_path(dist)
    record = _read_json(dist / BUILD_RECORD)
    if not isinstance(record, dict) or set(record) != {'schema_version', 'inputs', 'assets'} or type(record['schema_version']) is not int or record['schema_version'] != 1:
        raise ValueError('Unsupported or malformed app build record.')
    inputs = _snapshot(app, excluded=SOURCE_EXCLUDES)
    for required in ('index.html', 'package.json', 'package-lock.json', 'build.mjs'):
        if required not in inputs:
            raise ValueError('Required app build input is missing.')
    _validate_inventory(record['inputs'], inputs, 'inputs')
    assets = _snapshot(dist, excluded={BUILD_RECORD})
    _validate_inventory(record['assets'], assets, 'assets')
    _validate_references(dist, assets)
    return assets


def app_build_check(root: Path) -> dict:
    result = {'name': 'app assets', 'required': True, 'corrective_action': REBUILD_ACTION}
    try:
        assets = validate_app_build(root)
        return {**result, 'status': 'pass', 'detail': f'Current app inputs and {len(assets)} emitted files match the build SHA-256 record.'}
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        return {**result, 'status': 'fail', 'detail': f'App build is unavailable, stale or incomplete: {exc}'}
