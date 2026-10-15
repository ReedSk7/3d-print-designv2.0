"""Local feature probes on exact STL bytes. These are computational checks only."""
import io
import math
from pathlib import Path
import numpy as np
import trimesh
from core.workflow.review import snapshot_generation
from core.workflow.pipeline import prepare_generation

def ray_distances(mesh,origin,direction):
    triangles=np.asarray(mesh.triangles); origin=np.asarray(origin); direction=np.asarray(direction)
    e1=triangles[:,1]-triangles[:,0]; e2=triangles[:,2]-triangles[:,0]
    h=np.cross(direction,e2); det=np.einsum('ij,ij->i',e1,h)
    mask=np.abs(det)>1e-10; inverse=np.zeros(len(det)); inverse[mask]=1/det[mask]
    s=origin-triangles[:,0]; u=inverse*np.einsum('ij,ij->i',s,h)
    q=np.cross(s,e1); v=inverse*np.einsum('j,ij->i',direction,q)
    distance=inverse*np.einsum('ij,ij->i',e2,q)
    valid=mask&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(distance>1e-8)
    return np.unique(np.round(distance[valid],7))

def hole_probe(mesh,center,diameter,tolerance,*,xy_scale=(1,1)):
    if not math.isfinite(diameter) or diameter<=0 or not math.isfinite(tolerance) or tolerance<0: raise ValueError('Finite positive diameter and nonnegative tolerance required.')
    distances=[ray_distances(mesh,center,direction) for direction in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]]
    measured=[float(values[0]*2) if len(values) else None for values in distances]
    # A point in an intended hole lies outside solid material: outgoing crossings must be even.
    expected=[diameter*xy_scale[0],diameter*xy_scale[0],diameter*xy_scale[1],diameter*xy_scale[1]]
    passed=all(len(values)>0 and len(values)%2==0 and abs(values[0]*2-target)<=tolerance for values,target in zip(distances,expected))
    return {'expected_diameter_samples_mm':expected,'diameter_samples_mm':measured,'center_mm':list(center),'tolerance_mm':tolerance,'passed':bool(passed),'meaning':'Four cardinal section probes; not a complete surface or physical-fit check.'}

def outer_annulus_probe(mesh,center,diameter,tolerance,*,xy_scale=(1,1)):
    """At an exposed hollow section, the second crossing is its outer wall."""
    distances=[ray_distances(mesh,center,direction) for direction in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]]
    expected=[diameter*xy_scale[0],diameter*xy_scale[0],diameter*xy_scale[1],diameter*xy_scale[1]]
    measured=[float(values[1]*2) if len(values)>=2 else None for values in distances]
    passed=all(len(values)==2 and abs(values[1]*2-target)<=tolerance for values,target in zip(distances,expected))
    return {'expected_diameter_samples_mm':expected,'diameter_samples_mm':measured,'center_mm':list(center),'tolerance_mm':tolerance,'passed':bool(passed),'meaning':'Four cardinal outer-wall section probes in an exposed annular body; not a complete surface or physical-fit check.'}

def round_adapter_checks(mesh,params,tolerance,*,scale=(1,1,1)):
    """Generator 1.0/1.1 resolved geometry, including its extended cutting cone."""
    sx,sy,sz=map(float,scale); length=float(params['length'])
    a=params['end_a']; b=params['end_b']; checks=[]; pending=[]
    # The generator extends its cutting cone by epsilon at each end. Use that
    # actual section formula rather than comparing a tapered section to an end.
    epsilon=.01
    for feature,z in [('end_a.bore',length*.025),('transition.bore',length*.5),('end_b.bore',length*.975)]:
        fraction=(z+epsilon)/(length+2*epsilon)
        expected=float(a['inside_diameter'])+(float(b['inside_diameter'])-float(a['inside_diameter']))*fraction
        checks.append({'feature':feature,'reference_end_diameters_mm':[float(a['inside_diameter']),float(b['inside_diameter'])],**hole_probe(mesh,(0,0,z*sz),expected,tolerance,xy_scale=(sx,sy))})
    flange=params['mounting_flange']; bead=params['hose_retaining_bead']
    lower=float(flange['thickness']) if flange['enabled'] else 0
    upper=length-float(bead['width']) if bead['enabled'] else length
    if upper-lower<=max(1e-6,length*1e-6):
        pending.append('Outer mating body is fully obscured by flange/bead; endpoint outside diameters need dedicated review.')
        checks.append({'feature':'body_outer_sections','available':False,'passed':None,'meaning':'No exposed body section exists; no outside mating-dimension claim.'})
    else:
        for feature,fraction in [('body_outer_section_a',.25),('body_outer_section_b',.75)]:
            z=lower+(upper-lower)*fraction
            expected=float(a['outside_diameter'])+(float(b['outside_diameter'])-float(a['outside_diameter']))*z/length
            checks.append({'feature':feature,'reference_end_diameters_mm':[float(a['outside_diameter']),float(b['outside_diameter'])],**outer_annulus_probe(mesh,(0,0,z*sz),expected,tolerance,xy_scale=(sx,sy))})
    pattern=flange['screw_hole_pattern']
    if flange['enabled'] and pattern['enabled']:
        count=int(pattern['count']); radius=float(pattern['bolt_circle_diameter'])/2
        for index in range(count):
            angle=2*math.pi*index/count
            center=(radius*math.cos(angle)*sx,radius*math.sin(angle)*sy,float(flange['thickness'])*sz/2)
            checks.append({'feature':f'mounting_hole_{index+1}',**hole_probe(mesh,center,float(pattern['hole_diameter']),tolerance,xy_scale=(sx,sy))})
    pending.append('Adapter bead/flange finish surfaces and full taper/axes require visual or dedicated surface review.')
    return checks,pending

def inspect_features(manifest:Path):
    generation,_,stl,_,report=snapshot_generation(manifest)
    prepared=prepare_generation(generation.spec,workspace_root=generation.workspace_root)
    params=prepared.generation.resolved_parameters_mm; family=generation.spec.generator.id
    mesh=trimesh.load(io.BytesIO(stl),file_type='stl',force='mesh'); checks=[]; pending=[]
    tolerance=float(generation.spec.verification_policy.mesh_bounds_tolerance_mm)
    sx,sy,sz=map(float,prepared.context.scale_correction)
    if prepared.generation.artifact_kind!='full_part':
        pending.append('Coupon feature mapping remains generator/evidence-bound; full-part section probes not applied.')
    elif family=='bushing' and not params.get('split'):
        checks.append({'feature':'inside_diameter',**hole_probe(mesh,(0,0,float(params['length'])*sz/2),float(params['inside_diameter']),tolerance,xy_scale=(sx,sy))})
    elif family=='round_adapter':
        checks,pending=round_adapter_checks(mesh,params,tolerance,scale=(sx,sy,sz))
    elif family=='flange_plate':
        thickness=float(params['plate_thickness']); z=thickness*sz/4
        opening=params['center_opening']
        if opening['type']=='circle': checks.append({'feature':'center_opening',**hole_probe(mesh,(0,0,z),float(opening['diameter']),tolerance,xy_scale=(sx,sy))})
        else: pending.append('Non-circular center opening needs a dedicated section check.')
        pattern=params['mounting_hole_pattern']; centers=[]
        if pattern['type']=='rectangular': centers=[(sx*float(pattern['x_spacing'])/2,sy*float(pattern['y_spacing'])/2,z) for sx in (-1,1) for sy in (-1,1)]
        elif pattern['type']=='bolt_circle': centers=[(float(pattern['bolt_circle_diameter'])/2*math.cos(2*math.pi*i/int(pattern['count'])),float(pattern['bolt_circle_diameter'])/2*math.sin(2*math.pi*i/int(pattern['count'])),z) for i in range(int(pattern['count']))]
        for index,center in enumerate(centers):
            center=(center[0]*sx,center[1]*sy,center[2])
            checks.append({'feature':f'mounting_hole_{index+1}',**hole_probe(mesh,center,float(params['mounting_hole_diameter']),tolerance,xy_scale=(sx,sy))})
    else: pending.append('This geometry needs dedicated section probes; dimensions and protected-source comparisons remain available.')
    pending.append('Curved surfaces, complete hole axes, finish geometry and physical fit require further review.')
    return {'checks':checks,'pending':pending,'computational_probes_passed':bool(checks) and all(item['passed'] for item in checks),'physical_fit':'not_confirmed'}
