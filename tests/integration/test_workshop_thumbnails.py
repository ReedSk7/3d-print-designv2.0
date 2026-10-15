import json
import shutil
import os
import subprocess
from pathlib import Path
import pytest
from core.workshop.service import Workshop

ROOT=Path(__file__).parents[2]

@pytest.fixture
def previews(tmp_path):
    workshop=Workshop(tmp_path)
    document=json.loads((ROOT/'examples/specs/bushing_example.json').read_text())
    saved=workshop.save_spec(document); generated=workshop.action('generate',saved)
    preview=workshop.action('preview',{**generated,'revision':'r99'})
    original=tmp_path/preview['output']
    shutil.copytree(original.parent,original.parent.parent/'r100')
    return workshop,original

def test_catalog_thumbnail_is_latest_verified_numeric_revision(previews):
    workshop,_=previews
    record=workshop.catalog()[0]
    assert record['preview_revision']=='r100'
    assert record['thumbnail']=='/artifact/bushing_example/v01/previews/r100/iso.png'
    assert record['physical_fit']=='not_confirmed'

def test_invalid_latest_thumbnail_falls_back_to_verified_revision(previews):
    workshop,original=previews
    image=original.parent.parent/'r100/iso.png'; image.write_bytes(b'not a PNG')
    record=workshop.catalog()[0]
    assert record['preview_revision']=='r99'
    assert record['thumbnail'].endswith('/r99/iso.png')

def test_changed_generation_suppresses_thumbnail(previews):
    workshop,original=previews
    source=next(original.parents[2].glob('*.scad')); source.write_text(source.read_text()+'\n// changed')
    assert workshop.catalog()[0].get('thumbnail') is None

def test_thumbnail_cannot_follow_junction_to_another_project(previews):
    workshop,original=previews
    document=json.loads((ROOT/'examples/specs/bushing_example.json').read_text()); document['project']['id']='other_example'
    saved=workshop.save_spec(document); generated=workshop.action('generate',saved)
    other=workshop.root/workshop.action('preview',{**generated,'revision':'r01'})['output']
    link=original.parent.parent/'r101'
    try: link.symlink_to(other.parent,target_is_directory=True)
    except OSError:
        if os.name!='nt': raise
        subprocess.run(['cmd','/c','mklink','/J',str(link),str(other.parent)],capture_output=True,check=True)
    record=next(record for record in workshop.catalog() if record['id']=='bushing_example')
    assert record['thumbnail']=='/artifact/bushing_example/v01/previews/r100/iso.png'
