import io
import json
from pathlib import Path
import numpy as np
import pytest
import trimesh
from core.workshop.service import Workshop
from core.workflow.pipeline import prepare_generation
from core.workflow.review import snapshot_generation

ROOT=Path(__file__).parents[2]

@pytest.fixture(scope='module')
def adapters(tmp_path_factory):
    root=tmp_path_factory.mktemp('round-adapter-probes'); workshop=Workshop(root)
    original=json.loads((ROOT/'examples/specs/round_adapter_example.json').read_text())
    results={}
    for name in ('correct','wrong_bore','wrong_outer','wrong_spacing','v110'):
        document=json.loads(json.dumps(original)); document['project']['id']='adapter_'+name
        params=document['generator']['parameters']
        if name=='wrong_bore': params['end_a']['diameter']=48
        if name=='wrong_outer': params['end_b']['diameter']=38
        if name=='wrong_spacing': params['mounting_flange']['screw_hole_pattern']['bolt_circle_diameter']=67
        if name=='v110':
            document['generator']['version']='1.1.0'; params.pop('fit_class')
            params.update(end_a_fit='nominal',end_b_fit='nominal',mounting_hole_fit='nominal')
        saved=workshop.save_spec(document); result=workshop.action('generate',saved)
        manifest=root/result['manifest']; generation,_,stl,_,_=snapshot_generation(manifest)
        prepared=prepare_generation(generation.spec,workspace_root=workshop.workspace)
        results[name]=(manifest,trimesh.load(io.BytesIO(stl),file_type='stl',force='mesh'),prepared.generation.resolved_parameters_mm)
    return results

def test_supported_adapter_has_bore_body_and_mounting_checks(adapters):
    from core.workshop.features import inspect_features
    for name in ('correct','v110'):
        result=inspect_features(adapters[name][0])
        assert result['computational_probes_passed'],result
        names={item['feature'] for item in result['checks']}
        assert {'end_a.bore','end_b.bore','body_outer_section_a','body_outer_section_b','mounting_hole_1'}.issubset(names)

@pytest.mark.parametrize('name,feature',[('wrong_bore','end_a.bore'),('wrong_outer','body_outer_section_b'),('wrong_spacing','mounting_hole_1')])
def test_wrong_mating_dimension_fails_with_identical_bounds(adapters,name,feature):
    from core.workshop.features import round_adapter_checks
    correct=adapters['correct']; wrong=adapters[name]
    assert np.allclose(correct[1].extents,wrong[1].extents)
    checks,_=round_adapter_checks(wrong[1],correct[2],.05)
    assert next(item for item in checks if item['feature']==feature)['passed'] is False

def test_adapter_probes_account_for_xyz_scale(adapters):
    from core.workshop.features import round_adapter_checks
    mesh=adapters['correct'][1].copy(); mesh.apply_scale((1.1,.9,1.2))
    checks,_=round_adapter_checks(mesh,adapters['correct'][2],.05,scale=(1.1,.9,1.2))
    assert all(item['passed'] for item in checks),checks

def test_fully_obscured_body_is_explicitly_unavailable(adapters):
    from core.workshop.features import round_adapter_checks
    params=dict(adapters['correct'][2]); params['hose_retaining_bead']={**params['hose_retaining_bead'],'width':params['length']}
    checks,pending=round_adapter_checks(adapters['correct'][1],params,.05)
    assert any('obscured' in item for item in pending)
    assert any(item.get('available') is False for item in checks)
