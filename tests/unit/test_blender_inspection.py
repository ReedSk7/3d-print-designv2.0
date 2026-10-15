from pathlib import Path
from core.workshop.blender import compatibility, probe_blender

def test_exact_blender_target_only():
    assert compatibility('Blender 5.2.2')['compatible']
    assert not compatibility('Blender 5.2.1')['compatible']
    assert not compatibility('Blender 4.5.0')['compatible']

def test_absent_blender_is_optional(monkeypatch):
    monkeypatch.setenv('BLENDER_PATH','Z:/missing/blender.exe')
    result=probe_blender()
    assert not result['compatible']
    assert result['optional']
    assert 'explicit' in result['detail'].lower()
