"""Synthetic save/catalog regressions; these fixtures are never owner evidence."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from core.workshop.service import Workshop
from tests.unit.test_workshop import directory_link, example


def test_failed_context_write_leaves_no_version_and_retry_succeeds(tmp_path, monkeypatch):
    workshop = Workshop(tmp_path)
    original = json.dump

    def fail_context(document, stream, **kwargs):
        if Path(stream.name).name == 'intake-context.json':
            stream.write('{"interrupted":')
            raise OSError('simulated context write interruption')
        return original(document, stream, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(json, 'dump', fail_context)
        with pytest.raises(OSError, match='interruption'):
            workshop.save_spec(example(), intake_context={'exact_target': 'Synthetic fixture'})
    assert not (workshop.local / 'bushing_example/v01').exists()
    workshop.save_spec(example(), intake_context={'exact_target': 'Synthetic fixture'})
    assert workshop.catalog()[0]['intake_context']['exact_target'] == 'Synthetic fixture'


def test_failed_publication_rolls_back_only_new_version(tmp_path, monkeypatch):
    import core.workflow.publication as publication
    workshop = Workshop(tmp_path)
    workshop.save_spec(example())
    first = (workshop.local / 'bushing_example/v01/spec.json').read_bytes()
    revised = example()
    revised['project']['version'] = 'v02'
    revised['generator']['parameters']['inside_diameter'] = 19
    original = publication.os.link

    def fail_spec(source, target):
        if Path(source).name == 'spec.json':
            assert (Path(target).parent / 'intake-context.json').is_file()
            assert (Path(target).parent / 'accepted-interface-changes.json').is_file()
            raise OSError('simulated publication interruption')
        return original(source, target)

    with monkeypatch.context() as patch:
        patch.setattr(publication.os, 'link', fail_spec)
        with pytest.raises(OSError, match='interruption'):
            workshop.save_spec(revised, accept_interface_changes=True, intake_context={'exact_target': 'Revised fixture'})
    assert not (workshop.local / 'bushing_example/v02').exists()
    assert (workshop.local / 'bushing_example/v01/spec.json').read_bytes() == first
    workshop.save_spec(revised, accept_interface_changes=True, intake_context={'exact_target': 'Revised fixture'})


def test_existing_incomplete_version_is_preserved_and_diagnosed(tmp_path):
    workshop = Workshop(tmp_path)
    directory = workshop.local / 'bushing_example/v01'
    directory.mkdir(parents=True)
    original = directory / 'intake-context.json'
    original.write_bytes(b'{"recoverable":"notes"}')
    with pytest.raises(FileExistsError):
        workshop.save_spec(example())
    assert original.read_bytes() == b'{"recoverable":"notes"}'
    assert not (directory / 'spec.json').exists()
    record, = workshop.catalog()
    assert record['kind'] == 'invalid'
    assert 'spec.json' in record['diagnostics'][0]['message']


def test_concurrent_saves_publish_one_consistent_bundle(tmp_path):
    def save(target):
        try:
            return Workshop(tmp_path).save_spec(example(), intake_context={'exact_target': target})
        except FileExistsError:
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(save, ['first', 'second']))
    assert sum(result is not None for result in results) == 1
    record, = Workshop(tmp_path).catalog()
    assert record['intake_context']['exact_target'] in {'first', 'second'}
    assert record['catalog_status'] == 'ready'


@pytest.mark.parametrize('damage', ['json', 'schema', 'generator', 'identity', 'context_json', 'context_hash', 'context_shape'])
def test_one_damaged_record_does_not_hide_other_records_or_change_files(tmp_path, damage):
    workshop = Workshop(tmp_path)
    workshop.save_spec(example(), intake_context={'exact_target': 'Good fixture'})
    bad = example()
    bad['project']['id'] = 'damaged'
    saved = workshop.save_spec(bad, intake_context={'exact_target': 'Recoverable fixture'})
    path = tmp_path / saved['spec_path']
    if damage == 'json': path.write_bytes(b'{broken')
    elif damage == 'schema': path.write_text('{}')
    elif damage == 'generator':
        bad['generator']['version'] = '99.0.0'; path.write_text(json.dumps(bad))
    elif damage == 'identity':
        bad['project']['id'] = 'bushing_example'; path.write_text(json.dumps(bad))
    elif damage == 'context_json': (path.parent / 'intake-context.json').write_bytes(b'{broken')
    elif damage == 'context_hash':
        note = json.loads((path.parent / 'intake-context.json').read_text())
        note['spec_sha256'] = '0' * 64
        (path.parent / 'intake-context.json').write_text(json.dumps(note))
    elif damage == 'context_shape':
        note = json.loads((path.parent / 'intake-context.json').read_text())
        note['context'] = ['not an object']
        (path.parent / 'intake-context.json').write_text(json.dumps(note))
    before = {file: file.read_bytes() for file in path.parent.iterdir()}
    records = workshop.catalog()
    assert len(records) == 2
    good = next(record for record in records if record['id'] == 'bushing_example')
    invalid = next(record for record in records if record['id'] == 'damaged')
    assert good['kind'] == 'parametric'
    assert invalid['kind'] == 'invalid'
    assert invalid['catalog_status'] == 'invalid'
    assert invalid['diagnostics'][0]['path'].startswith('owner-validation/local/workshop/damaged/v01')
    assert invalid['diagnostics'][0]['recovery']
    assert not {'document', 'spec_path', 'manifest'} & invalid.keys()
    assert {file: file.read_bytes() for file in path.parent.iterdir()} == before


@pytest.mark.parametrize('local_source', ['cube(2);', 'cube(1);\n'])
def test_differing_same_name_legacy_sources_keep_both_locations(tmp_path, local_source):
    for base, source in [('projects', 'cube(1);'), ('owner-validation/local/workshop/legacy', local_source)]:
        path = tmp_path / base / 'same_name/source.scad'
        path.parent.mkdir(parents=True)
        path.write_text(source)
    records = Workshop(tmp_path).catalog()
    assert len(records) == 2
    assert {record['id'] for record in records} == {'same_name'}
    assert len({record['catalog_key'] for record in records}) == 2
    assert {record['source_route'] for record in records} == {'/legacy/', '/local-legacy/'}


def test_identical_legacy_sources_retain_all_locations(tmp_path):
    for base in ['projects', 'owner-validation/local/workshop/legacy']:
        path = tmp_path / base / 'same_name/source.scad'
        path.parent.mkdir(parents=True)
        path.write_text('cube(1);')
    record, = Workshop(tmp_path).catalog()
    assert {location['path'] for location in record['locations']} == {
        'projects/same_name', 'owner-validation/local/workshop/legacy/same_name'}


def test_empty_legacy_source_sets_do_not_prove_duplicates(tmp_path):
    for base in ['projects', 'owner-validation/local/workshop/legacy']:
        (tmp_path / base / 'same_name').mkdir(parents=True)
    assert len(Workshop(tmp_path).catalog()) == 2


def test_redirected_spec_becomes_diagnostic_without_hiding_good_spec(tmp_path):
    workshop = Workshop(tmp_path)
    workshop.save_spec(example())
    directory_link(workshop.local / 'redirected', workshop.local / 'bushing_example')
    records = workshop.catalog()
    assert len(records) == 2
    assert sum(record['kind'] == 'parametric' for record in records) == 1
    assert sum(record['kind'] == 'invalid' for record in records) == 1


def test_legacy_source_escape_is_diagnostic_and_preserves_other_sources(tmp_path):
    outside = tmp_path.parent / f'{tmp_path.name}-outside'
    outside.mkdir()
    (outside / 'private.scad').write_text('cube(9);')
    bad = tmp_path / 'projects/bad'
    bad.mkdir(parents=True)
    directory_link(bad / 'external', outside)
    good = tmp_path / 'projects/good/source.scad'
    good.parent.mkdir()
    good.write_text('cube(1);')
    records = Workshop(tmp_path).catalog()
    assert len(records) == 2
    invalid = next(record for record in records if record['id'] == 'bad')
    assert invalid['kind'] == 'invalid'
    assert not invalid.get('sources')
    assert next(record for record in records if record['id'] == 'good')['sources'] == ['good/source.scad']


def test_identical_scad_with_different_imported_assets_is_not_deduplicated(tmp_path):
    for base, data in [('projects', b'first asset'), ('owner-validation/local/workshop/legacy', b'second asset')]:
        directory = tmp_path / base / 'same_name'
        directory.mkdir(parents=True)
        (directory / 'source.scad').write_text('import("profile.dxf");')
        (directory / 'profile.dxf').write_bytes(data)
    assert len(Workshop(tmp_path).catalog()) == 2


def test_incomplete_previous_version_blocks_unreviewed_revision(tmp_path):
    workshop = Workshop(tmp_path)
    directory = workshop.local / 'bushing_example/v01'
    directory.mkdir(parents=True)
    (directory / 'intake-context.json').write_text('recoverable notes')
    revised = example()
    revised['project']['version'] = 'v02'
    with pytest.raises(ValueError, match='prior saved version'):
        workshop.save_spec(revised)
    assert not (workshop.local / 'bushing_example/v02').exists()


def test_corrupt_context_blocks_generation_before_pipeline_runs(tmp_path, monkeypatch):
    workshop = Workshop(tmp_path)
    saved = workshop.save_spec(example(), intake_context={'exact_target': 'Fixture'})
    (tmp_path / saved['spec_path']).with_name('intake-context.json').write_text('{broken')
    def unexpected(*args, **kwargs):
        pytest.fail('An invalid record entered the generation pipeline')
    monkeypatch.setattr('core.workflow.pipeline.generate_project', unexpected)
    with pytest.raises(ValueError): workshop.action('generate', saved)


def test_redirected_source_cannot_enter_generation(tmp_path, monkeypatch):
    workshop = Workshop(tmp_path)
    workshop.save_spec(example())
    directory_link(workshop.local / 'alias', workshop.local / 'bushing_example')
    def unexpected(*args, **kwargs):
        pytest.fail('A redirected record entered the generation pipeline')
    monkeypatch.setattr('core.workflow.pipeline.generate_project', unexpected)
    with pytest.raises(ValueError):
        workshop.action('generate', {'spec_path': 'owner-validation/local/workshop/alias/v01/spec.json'})


def test_symlink_loop_is_one_catalog_diagnostic(tmp_path):
    workshop = Workshop(tmp_path)
    workshop.save_spec(example())
    directory = workshop.local / 'loop/v01'
    directory.mkdir(parents=True)
    try:
        (directory / 'spec.json').symlink_to('spec.json')
    except OSError:
        pytest.skip('File symlinks require Windows Developer Mode')
    records = workshop.catalog()
    assert len(records) == 2
    assert next(record for record in records if record['id'] == 'loop')['kind'] == 'invalid'


def test_unique_legacy_record_does_not_read_artifact_bytes_for_deduplication(tmp_path, monkeypatch):
    directory = tmp_path / 'projects/unique_design'
    directory.mkdir(parents=True)
    (directory / 'source.scad').write_text('cube(1);')
    (directory / 'large.stl').write_bytes(b'synthetic large-asset stand-in')
    original = Path.open
    def reject_artifact_read(path, *args, **kwargs):
        if path == directory / 'large.stl':
            pytest.fail('Unique-name catalog browsing read a generated artifact for deduplication')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', reject_artifact_read)
    record, = Workshop(tmp_path).catalog()
    assert record['sources'] == ['unique_design/source.scad']


def test_invalid_coupon_request_does_not_reserve_a_saved_version(tmp_path):
    workshop = Workshop(tmp_path)
    saved = workshop.save_spec(example())
    with pytest.raises(ValueError):
        workshop.action('coupon', {**saved, 'project_id': 'synthetic_coupon', 'interface': 'inside_diameter', 'offsets': ['invalid']})
    assert not (workshop.local / 'synthetic_coupon/v01').exists()


def test_coupon_cannot_fill_an_existing_partial_version(tmp_path):
    workshop = Workshop(tmp_path)
    saved = workshop.save_spec(example())
    target = workshop.local / 'synthetic_coupon/v01'
    target.mkdir(parents=True)
    note = target / 'recovery.txt'
    note.write_text('Preserved partial version')
    with pytest.raises(FileExistsError):
        workshop.action('coupon', {**saved, 'project_id': 'synthetic_coupon', 'interface': 'inside_diameter', 'offsets': ['0', '0.2']})
    assert list(target.iterdir()) == [note]


@pytest.mark.parametrize('token', ['NaN', 'Infinity', '-Infinity', '1e999', '9' * 400])
def test_nonfinite_json_number_is_one_diagnostic_not_a_poisoned_api_response(tmp_path, token):
    workshop = Workshop(tmp_path)
    workshop.save_spec(example())
    bad = example()
    bad['project']['id'] = 'bad_number'
    saved = workshop.save_spec(bad)
    path = tmp_path / saved['spec_path']
    path.write_text(path.read_text().replace('"inside_diameter": 20', '"inside_diameter": ' + token))
    records = workshop.catalog()
    assert next(record for record in records if record['id'] == 'bad_number')['kind'] == 'invalid'
    assert next(record for record in records if record['id'] == 'bushing_example')['kind'] == 'parametric'
    json.dumps(records, allow_nan=False)


@pytest.mark.parametrize('number', [float('nan'), float('inf'), 10 ** 400])
def test_nonfinite_save_never_publishes_an_unusable_record(tmp_path, number):
    document = example()
    document['generator']['parameters']['inside_diameter'] = number
    workshop = Workshop(tmp_path)
    with pytest.raises(ValueError, match='finite'):
        workshop.save_spec(document)
    assert not (workshop.local / 'bushing_example/v01').exists()


def test_coupon_publish_keeps_source_hash_and_catalog_identity(tmp_path):
    import hashlib
    workshop = Workshop(tmp_path)
    saved = workshop.save_spec(example())
    coupon = workshop.action('coupon', {**saved, 'project_id': 'synthetic_coupon', 'interface': 'inside_diameter', 'offsets': ['0', '0.2']})
    record = next(item for item in workshop.catalog() if item['id'] == 'synthetic_coupon')
    assert record['catalog_status'] == 'ready'
    assert record['catalog_key'] == coupon['catalog_key']
    assert record['document']['fit_coupon']['source_spec_sha256'] == hashlib.sha256((tmp_path / saved['spec_path']).read_bytes()).hexdigest()
