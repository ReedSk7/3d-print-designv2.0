"""Real OpenSCAD geometry with simulated PNG subprocesses where explicitly stated."""
import json
from pathlib import Path
import subprocess
import sys
import pytest
from core.models.artifacts import sha256_file
from core.workflow.bambu import prepare_bambu_handoff
from core.workflow.pipeline import generate_project
from core.workflow.preview import export_previews, verify_preview_bundle
from core.workflow.review import snapshot_generation
from core.evidence import create_full_part_spec_from_coupon
from core.validation.specification import SpecificationError
from tests.integration.test_owner_evidence_chain import _generated_coupon, _record_pass
from tests.unit.test_upgrade_safety import png_bytes


@pytest.mark.integration
@pytest.mark.parametrize('tamper', ['change', 'delete'])
def test_linked_full_part_rechecks_coupon_scad(examples_dir, tmp_path, tamper):
    source, workspace, manifest = _generated_coupon(examples_dir, tmp_path, suffix='source_tamper')
    evidence = _record_pass(manifest)
    linked = tmp_path/'linked.json'
    create_full_part_spec_from_coupon(source, passed_coupon_evidence_path=evidence,
        expected_coupon_evidence_sha256=sha256_file(evidence), new_project_version='v02',
        output_spec_path=linked, workspace_root=workspace)
    scad = next(manifest.parent.glob('*.scad'))
    if tamper == 'change': scad.write_text('// changed fixture')
    else: scad.unlink()
    with pytest.raises(SpecificationError, match='SCAD'):
        generate_project(linked, workspace_root=workspace)
    assert not (workspace/'full_source_source_tamper'/'v02').exists()


@pytest.mark.integration
def test_handoff_preserves_bytes_alignment_and_blocks_wrong_printer(examples_dir, tmp_path, repo_root):
    root = tmp_path/'workspace with spaces'
    result = generate_project(examples_dir/'bushing_example.json', workspace_root=root)
    manifest = prepare_bambu_handoff(result.manifest_path)
    data = json.loads(manifest.read_text())
    assert data['kind'] == 'manual_stl_import' and not data['bambu_project_verified']
    assert not data['physical_fit_confirmed'] and data['profiles'] == []
    assert (manifest.parent/'geometry.stl').read_bytes() == result.stl_path.read_bytes()
    assert (manifest.parent/'source.scad').read_bytes() == result.scad_path.read_bytes()
    with pytest.raises(FileExistsError): prepare_bambu_handoff(result.manifest_path)
    with pytest.raises(ValueError, match='substitution'):
        prepare_bambu_handoff(result.manifest_path, printer_model='Bambu Lab P1S')
    completed = subprocess.run([sys.executable, str(repo_root/'scripts/verify_mesh.py'),
        '--manifest', str(result.manifest_path)], cwd=tmp_path, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    doc = json.loads(result.manifest_path.read_text()); doc['checks']['expected_bounds_mm'] = []
    result.manifest_path.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match='bounds'): snapshot_generation(result.manifest_path)


@pytest.mark.integration
def test_preview_bindings_and_failed_render_do_not_consume_revision(examples_dir, tmp_path, monkeypatch):
    import core.workflow.preview as preview
    result = generate_project(examples_dir/'bushing_example.json', workspace_root=tmp_path/'space root')
    monkeypatch.setattr(preview, 'find_openscad', lambda: Path('fixture renderer'))
    monkeypatch.setattr(preview, 'openscad_version', lambda _: 'synthetic PNG renderer')
    calls = []
    def render(command, **kw):
        calls.append(command)
        # Assert the rendered source is exactly the bound version, not the live input spec.
        assert Path(command[-1]).read_bytes() == result.scad_path.read_bytes()
        Path(command[command.index('-o')+1]).write_bytes(png_bytes())
        return subprocess.CompletedProcess(command, 0, '', '')
    monkeypatch.setattr(preview, 'run_openscad_command', render)
    manifest = export_previews(result.manifest_path, size=(64,64), detail_camera='0,0,2,90,0,0,12')
    doc = json.loads(manifest.read_text())
    assert len(calls) == 5 and len(doc['views']) == 5
    assert doc['source_scad']['sha256'] == sha256_file(result.scad_path)
    assert doc['source_stl']['sha256'] == sha256_file(result.stl_path)
    assert doc['agent_visual_review'] == doc['owner_review'] == 'pending'
    assert '--viewall' not in calls[-1] and '--projection=o' in calls[-1]
    assert verify_preview_bundle(manifest)['automated_checks'] == 'passed'
    image = manifest.parent/'iso.png'
    original = image.read_bytes(); image.write_bytes(b'wrong PNG')
    with pytest.raises(ValueError, match='SHA-256'): verify_preview_bundle(manifest)
    image.write_bytes(original)
    with pytest.raises(FileExistsError): export_previews(result.manifest_path)
    with pytest.raises(ValueError): export_previews(result.manifest_path, revision='../escape')
    def fail(*a, **kw): raise preview.OpenSCADExecutionError('synthetic renderer failure')
    monkeypatch.setattr(preview, 'run_openscad_command', fail)
    with pytest.raises(preview.OpenSCADExecutionError): export_previews(result.manifest_path, revision='r02')
    assert not (manifest.parent.parent/'r02').exists()
    result.scad_path.write_text('// stale source')
    with pytest.raises(ValueError): export_previews(result.manifest_path, revision='r03')


@pytest.mark.integration
def test_competing_empty_version_directory_is_preserved(examples_dir, tmp_path, monkeypatch):
    import core.workflow.pipeline as pipeline
    original = pipeline.publish_bundle
    target = tmp_path/'bushing_example'/'v01'
    evidence = {}
    def collide(staging, destination, **kwargs):
        destination.mkdir(parents=True)
        evidence['inode'] = destination.stat().st_ino
        return original(staging, destination, **kwargs)
    monkeypatch.setattr(pipeline, 'publish_bundle', collide)
    with pytest.raises(FileExistsError):
        generate_project(examples_dir/'bushing_example.json', workspace_root=tmp_path)
    assert target.stat().st_ino == evidence['inode']
    assert list(target.iterdir()) == []


@pytest.mark.integration
def test_handoff_blocks_mismatched_source_profile(examples_dir, tmp_path):
    document = json.loads((examples_dir/'bushing_example.json').read_text())
    document['printer_profile'] = 'bambu_lab_p1s_owner_local'
    source = tmp_path/'wrong-printer.json'; source.write_text(json.dumps(document))
    result = generate_project(source, workspace_root=tmp_path/'workspace')
    with pytest.raises(ValueError, match='printer-profile identity'):
        prepare_bambu_handoff(result.manifest_path)
    assert not (result.output_directory/'bambu-handoff').exists()
