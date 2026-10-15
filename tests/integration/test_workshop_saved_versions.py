"""Real CAD with synthetic evidence plumbing only; no owner print is claimed."""
import json

import pytest

from core.models.artifacts import sha256_file
from core.validation.specification import load_project_spec
from core.workshop.service import Workshop
from tests.integration.test_owner_evidence_chain import _record_pass, _source_spec


@pytest.mark.integration
def test_workshop_derived_specs_preserve_hash_bindings_and_existing_versions(examples_dir, tmp_path):
    source = _source_spec(examples_dir, tmp_path, project_id='synthetic_workshop_chain')
    workshop = Workshop(tmp_path)
    saved = workshop.save_spec(json.loads(source.read_text()))
    coupon = workshop.action('coupon', {**saved, 'project_id': 'synthetic_workshop_coupon',
                                        'interface': 'inside_diameter', 'offsets': ['-0.15', '0', '0.15']})
    generated = workshop.action('generate', coupon)
    evidence = _record_pass(tmp_path / generated['manifest'])
    payload = {**saved, 'evidence_path': evidence.relative_to(tmp_path).as_posix(),
               'evidence_sha256': sha256_file(evidence), 'version': 'v02'}
    # The evidence adapter rejects a stale hash before a saved target appears.
    with pytest.raises(ValueError):
        workshop.action('link_full', {**payload, 'evidence_sha256': '0' * 64})
    target = workshop.local / 'synthetic_workshop_chain/v02'
    assert not target.exists()
    linked = workshop.action('link_full', payload)
    specification = load_project_spec(tmp_path / linked['spec_path'])
    assert specification.fit_coupon_evidence.source_spec_sha256 == sha256_file(tmp_path / saved['spec_path'])
    assert specification.fit_coupon_evidence.coupon_result_evidence_sha256 == sha256_file(evidence)
    original = (target / 'spec.json').read_bytes()
    with pytest.raises(FileExistsError):
        workshop.action('link_full', payload)
    assert (target / 'spec.json').read_bytes() == original
    assert all(record['catalog_status'] == 'ready' for record in workshop.catalog())
