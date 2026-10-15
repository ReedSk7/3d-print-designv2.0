import json
from pathlib import Path
import pytest
import os
import subprocess
from core.workshop.service import Workshop, safe_path
from core.workshop.server import authorized

ROOT = Path(__file__).resolve().parents[2]

def example():
    return json.loads((ROOT/'examples/specs/bushing_example.json').read_text())

def directory_link(link,target):
    try: link.symlink_to(target,target_is_directory=True)
    except OSError:
        if os.name!='nt': raise
        subprocess.run(['cmd','/c','mklink','/J',str(link),str(target)],capture_output=True,check=True)

def test_path_escape_is_rejected(tmp_path):
    with pytest.raises(ValueError): safe_path(tmp_path, '../outside.json')

def test_request_guards_require_local_origin_host_and_token():
    assert authorized('127.0.0.1:8765','http://127.0.0.1:8765','abc','abc',8765)
    assert not authorized('evil.test','http://evil.test','abc','abc',8765)
    assert not authorized('127.0.0.1:8765','http://evil.test','abc','abc',8765)
    assert not authorized('127.0.0.1:8765',None,'','abc',8765)

def test_saved_version_is_immutable(tmp_path):
    workshop=Workshop(tmp_path)
    spec=example()
    workshop.save_spec(spec)
    with pytest.raises(FileExistsError): workshop.save_spec(spec)
    assert len(workshop.catalog())==1
    assert workshop.catalog()[0]['physical_fit']=='not_confirmed'

def test_intake_context_is_local_and_bound_to_saved_spec(tmp_path):
    workshop=Workshop(tmp_path)
    context={'exact_target':'Measured bushing for fixture','reused_parts':'Existing shaft','exclusions':'No surrounding mount changes','references':'Owner caliper notes'}
    workshop.save_spec(example(),intake_context=context)
    assert workshop.catalog()[0]['intake_context']==context
    assert workshop.catalog()[0]['document']==example()

def test_unknown_intake_fields_fail_before_publication(tmp_path):
    workshop=Workshop(tmp_path)
    with pytest.raises(ValueError,match='intake'): workshop.save_spec(example(),intake_context={'shell':'unsafe'})
    assert not list(workshop.local.glob('*/*/spec.json'))

def test_preserved_legacy_duplicate_has_one_catalog_record(tmp_path):
    for base in (tmp_path/'projects',tmp_path/'owner-validation/local/workshop/legacy'):
        (base/'preserved_design').mkdir(parents=True); (base/'preserved_design/source.scad').write_text('cube(1);')
    records=Workshop(tmp_path).catalog()
    assert len(records)==1
    assert records[0]['source_route']=='/legacy/'

def test_protected_change_requires_acceptance(tmp_path):
    workshop=Workshop(tmp_path)
    first=example(); workshop.save_spec(first)
    second=example(); second['project']['version']='v02'
    second['generator']['parameters']['inside_diameter']=19
    with pytest.raises(ValueError,match='Protected'): workshop.save_spec(second)
    result=workshop.save_spec(second,accept_interface_changes=True)
    assert result['changes'][0]['parameter']=='inside_diameter'

def test_generator_protected_length_requires_acceptance(tmp_path):
    workshop=Workshop(tmp_path); first=example(); workshop.save_spec(first)
    second=example(); second['project']['version']='v02'; second['generator']['parameters']['length']=30
    with pytest.raises(ValueError,match='Protected'): workshop.save_spec(second)

def test_latest_revision_is_numerical(tmp_path):
    workshop=Workshop(tmp_path); first=example(); first['project']['version']='v99'; workshop.save_spec(first)
    second=example(); second['project']['version']='v100'; second['generator']['parameters']['inside_diameter']=19
    workshop.save_spec(second,accept_interface_changes=True)
    third=json.loads(json.dumps(second)); third['project']['version']='v101'
    workshop.save_spec(third)

def test_unknown_action_rejected(tmp_path):
    with pytest.raises(ValueError): Workshop(tmp_path).action('shell', {'command':'echo unsafe'})

def test_owner_evidence_requires_explicit_actual_test_attestation(tmp_path):
    with pytest.raises(ValueError,match='actual'):
        Workshop(tmp_path).action('record_coupon',{})

def test_nested_hole_spacing_is_protected(tmp_path):
    workshop=Workshop(tmp_path)
    first=json.loads((ROOT/'examples/specs/flange_plate_example.json').read_text()); workshop.save_spec(first)
    second=json.loads(json.dumps(first)); second['project']['version']='v02'
    second['generator']['parameters']['mounting_hole_pattern']['x_spacing']=78
    with pytest.raises(ValueError,match='Protected'): workshop.save_spec(second)

def test_junction_escape_rejected(tmp_path):
    outside=tmp_path.parent/'outside-workshop'; outside.mkdir(exist_ok=True)
    directory_link(tmp_path/'link',outside)
    with pytest.raises(ValueError): safe_path(tmp_path,'link/private.json')

def test_allowed_root_link_is_not_a_new_authority(tmp_path):
    outside=tmp_path/'outside'; outside.mkdir()
    link=tmp_path/'root-link'
    directory_link(link,outside)
    with pytest.raises(ValueError): safe_path(link,'private.json')
