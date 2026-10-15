"""Read-only catalog: isolate damaged records and retain original identities."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter
from pathlib import Path

from core.validation.specification import load_project_spec_bytes, validate_parameter_document
from generators.registry import get_generator
from .paths import safe_path, unredirected_path

RECORD_ERRORS = (OSError, ValueError, LookupError, TypeError, RuntimeError)
RECOVERY = ('Keep the original files. Ask Codex to inspect this location and recover from a '
            'known-good copy or save a corrected new version; existing records are never overwritten.')


def validate_finite_numbers(value):
    """Reject numbers that cannot cross the JSON/browser boundary as finite values."""
    if isinstance(value, (int, float)):
        try:
            finite = math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            raise ValueError('Specification and sidecar values must be finite JSON numbers.')
    elif isinstance(value, dict):
        for child in value.values():
            validate_finite_numbers(child)
    elif isinstance(value, list):
        for child in value:
            validate_finite_numbers(child)


def validate_intake_context(context):
    if (not isinstance(context, dict)
            or set(context) - {'exact_target', 'reused_parts', 'exclusions', 'references'}
            or any(not isinstance(value, str) or len(value) > 10000 for value in context.values())):
        raise ValueError('Invalid intake context; use bounded target, reused parts, exclusions and references text.')


def read_saved_document(root: Path, local: Path, path: Path):
    """Validate exact saved bytes and their location before exposing an editor/action."""
    path = unredirected_path(root, path)
    data = path.read_bytes()
    document = json.loads(data)
    validate_finite_numbers(document)
    loaded = load_project_spec_bytes(data, source=path.relative_to(root).as_posix())
    expected = local / loaded.project_id / loaded.project_version / 'spec.json'
    if path != expected:
        raise ValueError('Saved project ID/version does not match its storage location.')
    generator = get_generator(loaded.generator_id, loaded.generator_version)
    validate_parameter_document(generator.parameter_schema, document['generator']['parameters'])
    context = {}
    intake_path = path.parent / 'intake-context.json'
    if intake_path.exists() or intake_path.is_symlink():
        unredirected_path(root, intake_path)
        note = json.loads(intake_path.read_text(encoding='utf-8'))
        validate_finite_numbers(note)
        if not isinstance(note, dict) or note.get('spec_sha256') != hashlib.sha256(data).hexdigest():
            raise ValueError('intake-context.json is not bound to the exact saved specification SHA-256.')
        context = note.get('context')
        validate_intake_context(context)
    changes_path = path.parent / 'accepted-interface-changes.json'
    if changes_path.exists() or changes_path.is_symlink():
        unredirected_path(root, changes_path)
        changes = json.loads(changes_path.read_text(encoding='utf-8'))
        validate_finite_numbers(changes)
        required = {'parameter', 'before', 'after', 'before_units', 'after_units'}
        if (not isinstance(changes, list) or not changes
                or any(not isinstance(change, dict) or not required <= change.keys()
                       or not isinstance(change['parameter'], str)
                       or change['before_units'] not in {'mm', 'inch'}
                       or change['after_units'] not in {'mm', 'inch'} for change in changes)):
            raise ValueError('accepted-interface-changes.json must contain the accepted parameter changes.')
    return document, context


def invalid_record(root, path, exc, *, project_id=None, version='', key=None):
    relative = path.relative_to(root).as_posix()
    identifier = project_id or path.name
    return {'id': identifier, 'name': identifier.replace('_', ' '), 'version': version,
            'kind': 'invalid', 'catalog_status': 'invalid', 'catalog_key': key or 'invalid:' + relative,
            'path': relative, 'physical_fit': 'not_confirmed', 'workflow_state': 'unavailable',
            'diagnostics': [{'path': relative, 'message': str(exc), 'recovery': RECOVERY}]}


def parametric_record(root, local, workspace, path):
    spec, intake = read_saved_document(root, local, path)
    project = spec['project']
    directory = workspace / project['id'] / project['version']
    status = {'workflow_state': 'draft', 'physical_fit': 'not_confirmed'}
    try:
        unredirected_path(root, directory)
        if (directory / 'artifact-manifest.json').is_file():
            from core.evidence.service import inspect_project_status
            try:
                status['report'] = inspect_project_status(directory)
            except Exception as exc:
                status['error'] = str(exc)
            status['workflow_state'] = status.get('report', {}).get('highest_defensible_workflow_state', 'draft')
            from core.workflow.preview import verify_preview_bundle
            candidates = [p for p in (directory / 'previews').glob('r*/preview-manifest.json')
                          if re.fullmatch(r'r\d{2,4}', p.parent.name)]
            for preview in sorted(candidates, key=lambda p: int(p.parent.name[1:]), reverse=True):
                try:
                    declared_revision = preview.parent.name
                    preview = safe_path(workspace, preview.relative_to(workspace).as_posix())
                    if preview.parents[2] != directory.absolute() or preview.parent.name != declared_revision:
                        raise ValueError('Thumbnail revision resolves to another project/version or revision.')
                    verify_preview_bundle(preview)
                    status.update(thumbnail='/artifact/' + (preview.parent / 'iso.png').relative_to(workspace).as_posix(),
                                  preview_revision=preview.parent.name)
                    break
                except RECORD_ERRORS:
                    continue
    except RECORD_ERRORS as exc:
        status['error'] = str(exc)
    if status.get('error'):
        status['diagnostics'] = [{'path': directory.relative_to(root).as_posix(),
                                  'message': status['error'], 'recovery': RECOVERY}]
    relative = path.relative_to(root).as_posix()
    return {**project, **status, 'kind': 'parametric', 'catalog_status': 'ready',
            'catalog_key': 'parametric:' + relative, 'path': relative, 'intake_context': intake,
            'spec_path': relative, 'manifest': (directory / 'artifact-manifest.json').relative_to(root).as_posix(),
            'document': spec}


def _children(root, directory, records):
    try:
        unredirected_path(root, directory)
        return sorted(directory.iterdir()) if directory.exists() else []
    except RECORD_ERRORS as exc:
        records.append(invalid_record(root, directory, exc))
        return []


def _legacy_files(root, directory, *, hash_contents):
    """Hash the whole retained tree; identical SCAD with different dependencies is not a duplicate."""
    sources, hashes, retained_files = [], [], []
    def fail(error):
        raise error
    for current, directories, files in os.walk(directory, followlinks=False, onerror=fail):
        for name in directories:
            unredirected_path(root, Path(current) / name)
        for name in sorted(files):
            path = unredirected_path(root, Path(current) / name)
            retained_files.append(path)
            if path.suffix.lower() == '.scad':
                sources.append(path.relative_to(directory.parent).as_posix())
    # Browsing a unique name never reads its potentially large artifact bytes.
    # Only conflicting names require a fresh byte comparison of dependencies.
    if sources and hash_contents:
        for path in retained_files:
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            hashes.append((path.relative_to(directory).as_posix(), digest))
    return sorted(sources), tuple(sorted(hashes))


def build_catalog(root: Path, local: Path, workspace: Path):
    records = []
    for project in _children(root, local, records):
        if project.name in {'legacy', 'jobs'} or project.name.startswith('.') or not project.is_dir():
            continue
        for version in _children(root, project, records):
            path = version / 'spec.json'
            if not version.is_dir() or (not re.fullmatch(r'v\d{2,4}', version.name) and not path.exists()):
                continue
            try:
                records.append(parametric_record(root, local, workspace, path))
            except RECORD_ERRORS as exc:
                records.append(invalid_record(root, path, exc, project_id=project.name, version=version.name,
                                              key='parametric:' + path.relative_to(root).as_posix()))
    identical = {}
    candidates = []
    for legacy_root, route in [(root / 'projects', '/legacy/'), (local / 'legacy', '/local-legacy/')]:
        candidates.extend((directory, route) for directory in _children(root, legacy_root, records)
                          if directory.name != '_template' and directory.is_dir())
    name_counts = Counter(directory.name for directory, _ in candidates)
    for directory, route in candidates:
        try:
            unredirected_path(root, directory)
            sources, fingerprint = _legacy_files(root, directory, hash_contents=name_counts[directory.name] > 1)
            relative = directory.relative_to(root).as_posix()
            location = {'path': relative, 'source_route': route, 'sources': sources}
            identity = (directory.name, fingerprint)
            if sources and identity in identical:
                identical[identity]['locations'].append(location)
                continue
            record = {'id': directory.name, 'name': directory.name.replace('_', ' '), 'version': 'legacy',
                      'kind': 'legacy', 'catalog_status': 'ready', 'catalog_key': 'legacy:' + relative,
                      'physical_fit': 'not_confirmed', 'workflow_state': 'Legacy; automated generation unavailable',
                      **location, 'locations': [location]}
            records.append(record)
            if sources:
                identical[identity] = record
        except RECORD_ERRORS as exc:
            records.append(invalid_record(root, directory, exc, version='legacy',
                                          key='legacy:' + directory.relative_to(root).as_posix()))
    return records
