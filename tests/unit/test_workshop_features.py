import numpy as np
import trimesh
from core.workshop.features import hole_probe

def ring(inner):
    return trimesh.creation.annulus(r_min=inner/2,r_max=15,height=20,sections=96)

def test_wrong_hole_fails_despite_identical_outer_bounds():
    correct=ring(20); wrong=ring(18)
    assert np.allclose(correct.extents,wrong.extents)
    assert hole_probe(correct,(0,0,0),20,.05)['passed']
    assert not hole_probe(wrong,(0,0,0),20,.05)['passed']

def test_solid_surface_at_expected_hole_center_fails():
    solid=trimesh.creation.box(extents=(30,30,20))
    assert not hole_probe(solid,(0,0,0),20,.05)['passed']

def test_anisotropic_xy_scale_uses_both_axes():
    mesh=ring(20); mesh.apply_scale((1.1,.9,1.2))
    assert hole_probe(mesh,(0,0,0),20,.05,xy_scale=(1.1,.9))['passed']
