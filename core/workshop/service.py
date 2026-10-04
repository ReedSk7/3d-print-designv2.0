"""Local catalog and immutable specification adapters."""
from __future__ import annotations
import json
import hashlib
import re
from pathlib import Path
from threading import RLock
from core.validation.specification import load_project_spec, validate_project_document
from generators.registry import get_generator

def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative,str) or not relative or Path(relative).is_absolute():
        raise ValueError('Use a relative project path.')
    if root.absolute()!=root.resolve(): raise ValueError('Allowed root is redirected by a link or junction.')
    candidate=(root/relative).resolve()
    try: candidate.relative_to(root.resolve())
    except ValueError: raise ValueError('Path leaves the allowed project directory.') from None
    return candidate

class Workshop:
    def __init__(self,root: Path):
        self.root=root.resolve(); self.local=self.root/'owner-validation/local/workshop'
        self.workspace=self.root/'workspace'; self.lock=RLock()

    def catalog(self):
        records=[]
        for path in sorted(self.local.glob('*/*/spec.json')):
            path=safe_path(self.root,path.relative_to(self.root).as_posix())
            spec=json.loads(path.read_text(encoding='utf-8'))
            project=spec['project']; directory=self.workspace/project['id']/project['version']
            intake={}; intake_path=path.parent/'intake-context.json'
            if intake_path.is_file():
                note=json.loads(intake_path.read_text())
                if note.get('spec_sha256')==hashlib.sha256(path.read_bytes()).hexdigest(): intake=note['context']
            status={'workflow_state':'draft','physical_fit':'not_confirmed'}
            if (directory/'artifact-manifest.json').is_file():
                from core.evidence.service import inspect_project_status
                try: status['report']=inspect_project_status(directory)
                except Exception as exc: status['error']=str(exc)
                # Report stays conservative; generated files never establish physical fit.
                status['workflow_state']=status.get('report',{}).get('highest_defensible_workflow_state','draft')
                # Thumbnails derive only from the latest numerically ordered
                # preview revision that still verifies against this exact version.
                from core.workflow.preview import verify_preview_bundle
                candidates=[p for p in (directory/'previews').glob('r*/preview-manifest.json') if re.fullmatch(r'r\d{2,4}',p.parent.name)]
                for preview in sorted(candidates,key=lambda p:int(p.parent.name[1:]),reverse=True):
                    try:
                        declared_revision=preview.parent.name
                        preview=safe_path(self.workspace,preview.relative_to(self.workspace).as_posix())
                        if preview.parents[2]!=directory.absolute() or preview.parent.name!=declared_revision:
                            raise ValueError('Thumbnail revision resolves to another project/version or revision.')
                        verify_preview_bundle(preview)
                        status.update(thumbnail='/artifact/'+(preview.parent/'iso.png').relative_to(self.workspace).as_posix(),preview_revision=preview.parent.name)
                        break
                    except (OSError,ValueError,KeyError,TypeError): continue
            records.append({**project,**status,'kind':'parametric','intake_context':intake,'spec_path':path.relative_to(self.root).as_posix(),
                            'manifest':(directory/'artifact-manifest.json').relative_to(self.root).as_posix(), 'document':spec})
        legacy_roots=[(self.root/'projects','/legacy/'),(self.local/'legacy','/local-legacy/')]
        legacy_ids=set()
        for legacy_root,route in legacy_roots:
          safe_path(self.root,legacy_root.relative_to(self.root).as_posix())
          for directory in sorted(legacy_root.glob('*')):
            if directory.is_dir() and directory.name!='_template' and directory.name not in legacy_ids:
                legacy_ids.add(directory.name)
                records.append({'id':directory.name,'name':directory.name.replace('_',' '),'version':'legacy',
                    'kind':'legacy','physical_fit':'not_confirmed','workflow_state':'Legacy; automated generation unavailable',
                    'path':directory.relative_to(self.root).as_posix(),
                    'source_route':route,
                    'sources':[p.relative_to(legacy_root).as_posix() for p in directory.rglob('*.scad') if p.is_file()]})
        return records

    def save_spec(self,document,*,accept_interface_changes=False,intake_context=None):
        with self.lock:
            return self._save_spec(document,accept_interface_changes=accept_interface_changes,intake_context=intake_context)

    def _save_spec(self,document,*,accept_interface_changes=False,intake_context=None):
        context={} if intake_context is None else intake_context
        if not isinstance(context,dict) or set(context)-{'exact_target','reused_parts','exclusions','references'} or any(not isinstance(value,str) or len(value)>10000 for value in context.values()):
            raise ValueError('Invalid intake context; use bounded target, reused parts, exclusions and references text.')
        validate_project_document(document)
        generator=get_generator(document['generator']['id'],document['generator']['version'])
        project=document['project']; changes=[]
        safe_path(self.root,'owner-validation/local/workshop')
        previous=sorted(self.local.glob(f"{project['id']}/*/spec.json"),key=lambda p:int(p.parent.name[1:]))
        if previous:
            old=json.loads(previous[-1].read_text())
            if old['generator']['id']!=document['generator']['id']:
                raise ValueError('Keep generator family consistent within a project.')
            protected=set(generator.applicable_protected_interfaces(document['generator']['parameters']))
            # Conservatively protect all generator inputs, including nominal dimensions
            # and nested finish/pattern relationships beyond fit-interface metadata.
            protected.update(old['generator']['parameters']); protected.update(document['generator']['parameters'])
            def value(parameters,path):
                for part in path.split('.'):
                    parameters=parameters.get(part) if isinstance(parameters,dict) else None
                return parameters
            for parameter in sorted(protected):
                a=value(old['generator']['parameters'],parameter); b=value(document['generator']['parameters'],parameter)
                if a!=b or old['input_units']!=document['input_units']:
                    changes.append({'parameter':parameter,'before':a,'after':b,'before_units':old['input_units'],'after_units':document['input_units']})
            if changes and not accept_interface_changes: raise ValueError('Protected interface changes require explicit acceptance: '+', '.join(c['parameter'] for c in changes))
        with self.lock:
            target=safe_path(self.local,f"{project['id']}/{project['version']}/spec.json")
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('x',encoding='utf-8') as stream: json.dump(document,stream,indent=2)
            try: load_project_spec(target)
            except Exception:
                target.unlink(); raise
            if changes:
                (target.parent/'accepted-interface-changes.json').write_text(json.dumps(changes,indent=2))
            if context:
                with (target.parent/'intake-context.json').open('x',encoding='utf-8') as stream:
                    json.dump({'spec_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'context':context,'meaning':'Owner design context; no measurement or fit claim.'},stream,indent=2)
        return {'spec_path':target.relative_to(self.root).as_posix(),'changes':changes}

    def action(self,action,payload):
        with self.lock:
            safe_path(self.root,'workspace'); safe_path(self.root,'owner-validation/local/workshop')
            if action=='generate':
                from core.workflow.pipeline import generate_project
                spec=safe_path(self.local,payload['spec_path'].removeprefix('owner-validation/local/workshop/'))
                result=generate_project(spec,workspace_root=self.workspace)
                return {'manifest':result.manifest_path.relative_to(self.root).as_posix(),'state':result.reached_state.value,'physical_fit':'not_confirmed'}
            if action in {'preview','review_preview','handoff','inspect','blender'}:
                manifest=safe_path(self.workspace,payload['manifest'].removeprefix('workspace/'))
                if action=='inspect':
                    from core.evidence.service import inspect_project_status
                    from .features import inspect_features
                    return {'status':inspect_project_status(manifest.parent,expected_fit_evidence_sha256=payload.get('expected_fit_evidence_sha256'),expected_physical_evidence_sha256=payload.get('expected_physical_evidence_sha256')),'features':inspect_features(manifest),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}
                revision=payload.get('revision','r01')
                if action in {'preview','review_preview'}:
                    from core.workflow.preview import export_previews, verify_preview_bundle
                    if action=='preview': output=export_previews(manifest,revision=revision,size=(1000,750))
                    else: output=safe_path(manifest.parent,f'previews/{revision}/preview-manifest.json')
                    verify_preview_bundle(output)
                    return {'output':output.relative_to(self.root).as_posix(),'preview_manifest_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'physical_fit':'not_confirmed'}
                elif action=='handoff':
                    from core.workflow.bambu import prepare_bambu_handoff
                    output=prepare_bambu_handoff(manifest,revision=revision)
                else:
                    from .blender import inspect_blender
                    output=inspect_blender(manifest,revision=revision)
                return {'output':output.relative_to(self.root).as_posix(),'physical_fit':'not_confirmed'}
            if action=='coupon':
                from core.evidence.service import create_fit_coupon_spec
                source=safe_path(self.local,payload['spec_path'].removeprefix('owner-validation/local/workshop/'))
                project_id=payload['project_id']; version=payload.get('version','v01')
                if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}',project_id) or not re.fullmatch(r'v\d{2,4}',version): raise ValueError('Invalid coupon project ID/version.')
                output=safe_path(self.local,f'{project_id}/{version}/spec.json')
                output.parent.mkdir(parents=True,exist_ok=True)
                result=create_fit_coupon_spec(source_spec_path=source,interface_parameter=payload['interface'],candidate_offsets=payload['offsets'],coupon_project_id=project_id,coupon_project_version=version,output_spec_path=output,generate=False,workspace_root=self.workspace)
                return {'spec_path':output.relative_to(self.root).as_posix(),'physical_fit':'not_confirmed'}
            if action in {'record_coupon','record_physical'}:
                from core.evidence.service import inspect_project_status
                if payload.get('owner_performed_actual_test') is not True:
                    raise ValueError('Confirm that you personally performed the actual recorded physical test.')
                manifest=safe_path(self.workspace,payload['manifest'].removeprefix('workspace/'))
                data=payload['record']
                if action=='record_coupon':
                    from core.evidence.service import record_fit_coupon_result
                    output=record_fit_coupon_result(manifest,**{key:data[key] for key in ('expected_manifest_sha256','selected_candidate_offset_mm','tested_by','tested_at','acceptance_criterion','observed_result','notes','passed')})
                else:
                    from core.evidence.service import record_physical_fit
                    output=record_physical_fit(manifest,**{key:data[key] for key in ('expected_manifest_sha256','confirmed_by','confirmed_at','interface_results','notes')},measured_dimensions=data.get('measured_dimensions',()))
                digest=hashlib.sha256(output.read_bytes()).hexdigest()
                anchor='expected_fit_evidence_sha256' if action=='record_coupon' else 'expected_physical_evidence_sha256'
                return {'evidence_path':output.relative_to(self.root).as_posix(),'evidence_sha256':digest,'evidence_anchor':anchor,'status':inspect_project_status(output.parent,**{anchor:digest})}
            if action=='record_visual':
                if payload.get('personally_inspected_images') is not True:
                    raise ValueError('Confirm you personally inspected the actual images.')
                from core.workflow.preview import verify_preview_bundle
                from datetime import datetime, timezone
                preview=safe_path(self.workspace,payload['preview_manifest'].removeprefix('workspace/'))
                verify_preview_bundle(preview)
                digest=hashlib.sha256(preview.read_bytes()).hexdigest()
                if digest!=payload['expected_preview_manifest_sha256']: raise ValueError('Preview manifest SHA-256 changed.')
                for key in ('reviewed_by','observations','remaining_concerns'):
                    if not isinstance(payload.get(key),str) or not payload[key].strip(): raise ValueError('Supply '+key+'.')
                if payload.get('reviewer_kind') not in {'agent','owner'}: raise ValueError('Use agent or owner reviewer kind.')
                note={'kind':'visual_review','preview_manifest':preview.relative_to(self.root).as_posix(),'preview_manifest_sha256':digest,'images':json.loads(preview.read_text())['views'],'reviewed_at':datetime.now(timezone.utc).isoformat(),**{key:payload[key] for key in ('reviewed_by','reviewer_kind','observations','remaining_concerns')},'physical_fit_confirmed':False}
                output=preview.parent/('visual-review-'+payload['reviewer_kind']+'.json')
                with output.open('x',encoding='utf-8') as stream: json.dump(note,stream,indent=2)
                return {'output':output.relative_to(self.root).as_posix(),'review_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'physical_fit':'not_confirmed'}
            if action=='link_full':
                from core.evidence.service import create_full_part_spec_from_coupon
                source=safe_path(self.local,payload['spec_path'].removeprefix('owner-validation/local/workshop/'))
                evidence=safe_path(self.workspace,payload['evidence_path'].removeprefix('workspace/'))
                document=json.loads(source.read_text()); version=payload['version']
                if not re.fullmatch(r'v\d{2,4}',version): raise ValueError('Use a new vNN version.')
                output=safe_path(self.local,f"{document['project']['id']}/{version}/spec.json"); output.parent.mkdir(parents=True,exist_ok=True)
                create_full_part_spec_from_coupon(source,passed_coupon_evidence_path=evidence,expected_coupon_evidence_sha256=payload['evidence_sha256'],new_project_version=version,output_spec_path=output,workspace_root=self.workspace)
                return {'spec_path':output.relative_to(self.root).as_posix(),'physical_fit':'not_confirmed'}
            raise ValueError('Unknown workshop action.')
