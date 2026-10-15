"""Local catalog and immutable specification adapters."""
from __future__ import annotations
import json
import hashlib
import re
import tempfile
from pathlib import Path
from threading import RLock
from core.validation.specification import load_project_spec, validate_project_document, validate_parameter_document
from core.workflow.publication import publish_bundle
from .catalog import build_catalog, read_saved_document, validate_intake_context, validate_finite_numbers
from .paths import safe_path, unredirected_path
from generators.registry import get_generator

class Workshop:
    def __init__(self,root: Path):
        self.root=root.resolve(); self.local=self.root/'owner-validation/local/workshop'
        self.workspace=self.root/'workspace'; self.lock=RLock()

    def catalog(self):
        with self.lock:
            return build_catalog(self.root, self.local, self.workspace)

    def save_spec(self,document,*,accept_interface_changes=False,intake_context=None):
        with self.lock:
            return self._save_spec(document,accept_interface_changes=accept_interface_changes,intake_context=intake_context)

    def _save_spec(self,document,*,accept_interface_changes=False,intake_context=None):
        context={} if intake_context is None else intake_context
        validate_intake_context(context)
        validate_finite_numbers(document)
        validate_project_document(document)
        generator=get_generator(document['generator']['id'],document['generator']['version'])
        validate_parameter_document(generator.parameter_schema, document['generator']['parameters'])
        project=document['project']; changes=[]
        unredirected_path(self.root, self.local)
        target=unredirected_path(self.root, self.local/project['id']/project['version'])
        if target.exists():
            raise FileExistsError(f'Saved version already exists; preserve it and use a new version: {target}')
        previous=sorted((p/'spec.json' for p in (self.local/project['id']).glob('*')
                         if p != target and p.is_dir() and re.fullmatch(r'v\d{2,4}',p.name)),
                        key=lambda p:int(p.parent.name[1:]))
        if previous:
            try:
                old, _ = read_saved_document(self.root, self.local, previous[-1])
            except (OSError, ValueError, LookupError, TypeError, RuntimeError) as exc:
                raise ValueError(f'Cannot compare the prior saved version at {previous[-1]}: {exc}. Preserve it and recover it before revising this project.') from exc
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
        # Stage every sidecar before reserving a destination. spec.json is the
        # completion marker and is published last using the shared exclusive helper.
        self.local.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.spec-save-',dir=self.local) as temporary:
            staging=Path(temporary)
            staged_spec=staging/'spec.json'
            with staged_spec.open('x',encoding='utf-8') as stream:
                json.dump(document,stream,indent=2)
            load_project_spec(staged_spec)
            if changes:
                with (staging/'accepted-interface-changes.json').open('x',encoding='utf-8') as stream:
                    json.dump(changes,stream,indent=2)
            if context:
                with (staging/'intake-context.json').open('x',encoding='utf-8') as stream:
                    json.dump({'spec_sha256':hashlib.sha256(staged_spec.read_bytes()).hexdigest(),'context':context,'meaning':'Owner design context; no measurement or fit claim.'},stream,indent=2)
            unredirected_path(self.root,target)
            publish_bundle(staging,target,manifest_name='spec.json')
        relative=(target/'spec.json').relative_to(self.root).as_posix()
        return {'spec_path':relative,'catalog_key':'parametric:'+relative,'changes':changes}

    def _save_derived_spec(self, project_id, version, create):
        """Use the same immutable version boundary for coupon/evidence adapters."""
        target=unredirected_path(self.root,self.local/project_id/version)
        if target.exists():
            raise FileExistsError(f'Saved version already exists; preserve it and use a new version: {target}')
        with tempfile.TemporaryDirectory(prefix='.spec-save-',dir=self.local) as temporary:
            staging=Path(temporary)
            output=staging/'spec.json'
            create(output)
            loaded=load_project_spec(output)
            if loaded.project_id != project_id or loaded.project_version != version:
                raise ValueError('Derived specification does not match its intended storage location.')
            unredirected_path(self.root,target)
            publish_bundle(staging,target,manifest_name='spec.json')
        relative=(target/'spec.json').relative_to(self.root).as_posix()
        return {'spec_path':relative,'catalog_key':'parametric:'+relative,'physical_fit':'not_confirmed'}

    def action(self,action,payload):
        with self.lock:
            safe_path(self.root,'workspace'); safe_path(self.root,'owner-validation/local/workshop')
            if action=='generate':
                from core.workflow.pipeline import generate_project
                spec=unredirected_path(self.local,self.local/payload['spec_path'].removeprefix('owner-validation/local/workshop/'))
                read_saved_document(self.root,self.local,spec)
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
                source=unredirected_path(self.local,self.local/payload['spec_path'].removeprefix('owner-validation/local/workshop/'))
                read_saved_document(self.root,self.local,source)
                project_id=payload['project_id']; version=payload.get('version','v01')
                if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}',project_id) or not re.fullmatch(r'v\d{2,4}',version): raise ValueError('Invalid coupon project ID/version.')
                return self._save_derived_spec(project_id,version,lambda output:
                    create_fit_coupon_spec(source_spec_path=source,interface_parameter=payload['interface'],
                        candidate_offsets=payload['offsets'],coupon_project_id=project_id,coupon_project_version=version,
                        output_spec_path=output,generate=False,workspace_root=self.workspace))
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
                source=unredirected_path(self.local,self.local/payload['spec_path'].removeprefix('owner-validation/local/workshop/'))
                read_saved_document(self.root,self.local,source)
                evidence=safe_path(self.workspace,payload['evidence_path'].removeprefix('workspace/'))
                document=json.loads(source.read_text()); version=payload['version']
                if not re.fullmatch(r'v\d{2,4}',version): raise ValueError('Use a new vNN version.')
                return self._save_derived_spec(document['project']['id'],version,lambda output:
                    create_full_part_spec_from_coupon(source,passed_coupon_evidence_path=evidence,
                        expected_coupon_evidence_sha256=payload['evidence_sha256'],new_project_version=version,
                        output_spec_path=output,workspace_root=self.workspace))
            raise ValueError('Unknown workshop action.')
