"""Historical exceptions require unchanged Git objects and exact checkout bytes."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
spec = importlib.util.spec_from_file_location('output_policy', ROOT / 'scripts/check_output_policy.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def digest(data):
    return {'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}


@pytest.fixture
def historical_repo(tmp_path, monkeypatch):
    def git(*args):
        return subprocess.run(['git', *args], cwd=tmp_path, check=True, capture_output=True)

    git('init', '-q')
    git('config', 'user.email', 'synthetic@example.invalid')
    git('config', 'user.name', 'Synthetic preservation test')
    git('config', 'core.autocrlf', 'false')
    originals = {}
    for path in policy.LEGACY_ARTIFACTS:
        content = b'solid synthetic\nendsolid synthetic\n' if path.endswith('.stl') else b'\x89PNG\r\nsynthetic\x00'
        artifact = tmp_path / path
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_bytes(content)
        originals[path] = content
    git('add', 'projects')
    git('commit', '-qm', 'Synthetic original artifacts')
    commit = git('rev-parse', 'HEAD').stdout.decode().strip()
    records = []
    pins = {}
    for path, content in originals.items():
        representations = {'lf': digest(content), 'crlf': digest(content.replace(b'\n', b'\r\n'))} if path.endswith('.stl') else {'exact': digest(content)}
        pins[path] = representations.get('crlf', representations.get('exact'))['sha256']
        records.append({'path': path, 'git_blob': git('rev-parse', f'HEAD:{path}').stdout.decode().strip(), 'git': digest(content), 'working_tree': representations})
    manifest = tmp_path / 'docs/legacy-artifact-preservation.json'
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({'source_commit': commit, 'files': records}))
    monkeypatch.setattr(policy, 'ROOT', tmp_path)
    monkeypatch.setattr(policy, 'WORKSPACE', tmp_path / 'workspace')
    monkeypatch.setattr(policy, 'LEGACY_COMMIT', commit)
    monkeypatch.setattr(policy, 'LEGACY_ARTIFACTS', pins)
    return tmp_path, git, originals, manifest


def test_original_lf_and_windows_crlf_are_both_exact_allowed_representations(historical_repo):
    root, _, originals, _ = historical_repo
    for path, original in originals.items():
        assert policy.is_preserved_historical_artifact(path), path
        if path.endswith('.stl'):
            (root / path).write_bytes(original.replace(b'\n', b'\r\n'))
            assert policy.is_preserved_historical_artifact(path), path


@pytest.mark.parametrize('replacement', [b'solid changed\r\nendsolid synthetic\r\n', b'solid synthetic\r\nendsolid synthetic\n', b'solid synthetic\rendsolid synthetic\r'])
def test_modified_or_mixed_checkout_bytes_are_never_normalized(historical_repo, replacement):
    root, _, originals, _ = historical_repo
    path = next(iter(originals))
    (root / path).write_bytes(replacement)
    assert not policy.is_preserved_historical_artifact(path)


def test_changed_index_cannot_hide_behind_original_working_bytes(historical_repo):
    root, git, originals, _ = historical_repo
    path = next(iter(originals))
    (root / path).write_bytes(b'changed staged content\n')
    git('add', path)
    (root / path).write_bytes(originals[path].replace(b'\n', b'\r\n'))
    assert not policy.is_preserved_historical_artifact(path)


def test_stale_baseline_manifest_is_rejected(historical_repo):
    root, _, originals, manifest = historical_repo
    path = next(iter(originals))
    (root / path).write_bytes(originals[path].replace(b'\n', b'\r\n'))
    document = json.loads(manifest.read_text())
    document['files'][0]['git']['sha256'] = '0' * 64
    manifest.write_text(json.dumps(document))
    assert not policy.is_preserved_historical_artifact(path)


def test_manifest_cannot_change_pinned_source_commit(historical_repo):
    root, _, originals, manifest = historical_repo
    path = next(iter(originals))
    (root / path).write_bytes(originals[path].replace(b'\n', b'\r\n'))
    document = json.loads(manifest.read_text())
    document['source_commit'] = '0' * 40
    manifest.write_text(json.dumps(document))
    assert not policy.is_preserved_historical_artifact(path)


def test_manifest_cannot_expand_the_six_path_allowlist(historical_repo):
    root, _, originals, manifest = historical_repo
    path = next(iter(originals))
    (root / path).write_bytes(originals[path].replace(b'\n', b'\r\n'))
    document = json.loads(manifest.read_text())
    document['files'].append({**document['files'][0], 'path': 'projects/new/exports/new.stl'})
    manifest.write_text(json.dumps(document))
    assert not policy.is_preserved_historical_artifact(path)
    assert not policy.is_preserved_historical_artifact('projects/new/exports/new.stl')


def test_missing_index_entry_is_rejected_even_with_original_checkout(historical_repo):
    root, git, originals, _ = historical_repo
    path = next(iter(originals))
    git('rm', '--cached', path)
    (root / path).write_bytes(originals[path].replace(b'\n', b'\r\n'))
    assert not policy.is_preserved_historical_artifact(path)


def test_main_checks_deleted_historical_paths(historical_repo, monkeypatch, capsys):
    root, git, originals, _ = historical_repo
    (root / 'workspace').mkdir()
    (root / 'workspace/.gitkeep').touch()
    (root / '.gitignore').write_bytes((ROOT / '.gitignore').read_bytes())
    for path in originals:
        git('rm', path)
    monkeypatch.setattr('sys.argv', ['check_output_policy.py'])
    assert policy.main() == 1
    assert 'historical' in capsys.readouterr().out.lower()


def test_shallow_checkout_fails_closed_with_actionable_history_error(historical_repo, monkeypatch, capsys):
    root, git, originals, _ = historical_repo
    (root / 'workspace').mkdir()
    (root / 'workspace/.gitkeep').touch()
    (root / '.gitignore').write_bytes((ROOT / '.gitignore').read_bytes())
    git('commit', '--allow-empty', '-qm', 'Synthetic descendant')
    shallow = root.parent / 'shallow'
    subprocess.run(['git', 'clone', '--depth=1', root.as_uri(), str(shallow)], check=True, capture_output=True)
    (shallow / 'workspace').mkdir()
    (shallow / 'workspace/.gitkeep').touch()
    (shallow / '.gitignore').write_bytes((ROOT / '.gitignore').read_bytes())
    monkeypatch.setattr(policy, 'ROOT', shallow)
    monkeypatch.setattr(policy, 'WORKSPACE', shallow / 'workspace')
    monkeypatch.setattr('sys.argv', ['check_output_policy.py'])
    assert not policy.is_preserved_historical_artifact(next(iter(originals)))
    assert policy.main() == 1
    assert 'full history' in capsys.readouterr().out.lower()


def test_checkout_symlink_cannot_substitute_original_bytes(historical_repo):
    root, _, originals, _ = historical_repo
    path = next(iter(originals))
    target = root / 'synthetic-target.stl'
    target.write_bytes(originals[path].replace(b'\n', b'\r\n'))
    artifact = root / path
    artifact.unlink()
    try:
        artifact.symlink_to(target)
    except OSError:
        pytest.skip('Symlink creation privilege is unavailable; exercised by Linux CI')
    assert not policy.is_preserved_historical_artifact(path)


def test_index_mode_change_is_not_a_preserved_artifact(historical_repo):
    root, git, originals, _ = historical_repo
    path = next(iter(originals))
    git('update-index', '--chmod=+x', path)
    (root / path).write_bytes(originals[path].replace(b'\n', b'\r\n'))
    assert not policy.is_preserved_historical_artifact(path)


def test_unrelated_history_cannot_claim_preservation(historical_repo):
    root, git, originals, _ = historical_repo
    git('checkout', '--orphan', 'unrelated')
    git('commit', '-qm', 'Same files without original ancestry')
    for path, original in originals.items():
        (root / path).write_bytes(original.replace(b'\n', b'\r\n') if path.endswith('.stl') else original)
    assert not policy.is_preserved_historical_artifact(next(iter(originals)))
