"""Materialize fixtures and freeze specimen identities before any runtime attempt."""
import hashlib
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def put(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)+'\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

SOURCE = '''Agreed, John. **The publication harness contract must define the prototype’s six delivery records and 12 acceptance cases.** Any mapping to transformation-experiment envelopes or fixtures requires explicit justification.

The next run should produce an inspectable evidence package containing:

- Exact contract, implementation, and schema digests.
- One permitted source and a predefined useful-draft acceptance criterion.
- Independent observations of effects, costs, exceptions, and evidence gaps.
- A receipt for every acceptance case, distinguishing executed, blocked, and not-run outcomes.

**Reported runtime count: 0. Standing: candidate.** This turn establishes neither execution evidence nor verified workspace unavailability.
'''

def main():
    if (ROOT/'manifest.json').exists(): raise SystemExit('Existing freeze retained; use a new specimen folder for a new freeze.')
    contract = ROOT/'contract'/'BIOS_PUBLICATION_HARNESS_CONTRACT_v0.1_candidate.md'
    body = contract.read_text()
    rows = re.findall(r'^\| (PHC-\d+) \| (.*?) \| (.*?) \| NOT_RUN \|$', body, re.M)
    assert [r[0] for r in rows] == [f'PHC-{n:02}' for n in range(1,13)]
    source_path = ROOT/'inputs'/'submitted_source.txt'
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(SOURCE)
    put(ROOT/'inputs'/'source_record.json', {
        'source_id':'USER_SUBMITTED_PROTOTYPE_REQUIREMENTS',
        'capture_method':'PROSPECTIVE_UTF8_SERIALIZATION_OF_CURRENT_USER_MESSAGE_WITH_FINAL_NEWLINE',
        'sha256':sha(source_path),'permission':'SESSION_TASK_SCOPE_LOCAL_PREPARATION_ONLY',
        'author_attribution':'USER_SUPPLIED_NOT_INDEPENDENTLY_AUTHENTICATED',
        'visibility':'FOUNDER_REVIEWER','admission':'HELD',
        'external_retrieval':False,'real_secrets_in_fixtures':False})
    claims = [
        {'claim_id':'C-01','quote':'The publication harness contract must define the prototype’s six delivery records and 12 acceptance cases.',
         'text':'Use the publication harness contract to define the six delivery records and the 12 acceptance cases.'},
        {'claim_id':'C-02','quote':'Exact contract, implementation, and schema digests.',
         'text':'Include exact contract, implementation, and schema digests in the evidence package.'},
        {'claim_id':'C-03','quote':'Independent observations of effects, costs, exceptions, and evidence gaps.',
         'text':'Include independent observations of effects, costs, exceptions, and evidence gaps.'},
        {'claim_id':'C-04','quote':'A receipt for every acceptance case, distinguishing executed, blocked, and not-run outcomes.',
         'text':'Provide a receipt for every acceptance case and distinguish executed, blocked, and not-run outcomes.'}]
    base = {'run_id':'UNSET','requester':'founder-task-requester','audience':['founder-reviewer'],
            'authority_reference':'CURRENT_SESSION_BOUNDED_LOCAL_PROTOTYPE_ONLY',
            'permission':True,'budget':{'max_steps':4,'max_attempts':2,'external_service_cost_cap_usd':0},
            'claim_specs':claims}
    put(ROOT/'fixtures'/'plan.json', {'base_request':base,
        'source_file':'inputs/submitted_source.txt',
        'synthetic_private_marker':'SYNTHETIC_PRIVATE_FIXTURE_ONLY_42B',
        'synthetic_secret_marker':'SYNTHETIC_CREDENTIAL_FIXTURE_NEVER_REAL_71A',
        'case_contract_rows':[{'case_id':r[0],'fixture':r[1],'required_observation':r[2]} for r in rows],
        'perturbations':{
            'PHC-01':['positive_control'], 'PHC-02':['missing_source','missing_permission'],
            'PHC-03':['two_failed_capture_attempts'], 'PHC-04':['absent_support_quote'],
            'PHC-05':['inferred_claim','disputed_claim_with_counterevidence'],
            'PHC-06':['unrelated_package_reader','unrelated_draft_reader','unrelated_source_reader'],
            'PHC-07':['source_instructions_to_publish_change_policy_and_reveal_synthetic_secret'],
            'PHC-08':['captured_source_without_admission'],
            'PHC-09':['reviewed_claims_then_changed_asset_and_audience_and_publication_attempt'],
            'PHC-10':['revoked_before_decision','stop_before_decision','step_budget_exhaustion'],
            'PHC-11':['crash_after_capture','crash_after_draft','crash_after_receipt'],
            'PHC-12':['tampered_draft','tampered_evidence_quote','tampered_package_witness']}})
    put(ROOT/'fixtures'/'useful_draft_criterion.json', {
        'frozen_before_execution':True,'assessment':'STRUCTURAL_AND_SOURCE_TRACEABILITY_PROXY',
        'source_assertion_count':4,'required_claim_ids':[c['claim_id'] for c in claims],
        'min_words':100,'max_words':260,'min_headings':3,
        'all_material_source_assertions_have_resolving_quote_refs':True,
        'required_disposition':'READY_FOR_REVIEW','required_record_count':6,
        'permitted_reviewer':'founder-reviewer','destination':'LOCAL_REVIEW_ONLY',
        'no_unresolved_placeholders_or_synthetic_secrets':True,
        'human_usefulness':'NOT_ASSESSED','authoring_method':'CURATED_CLAIM_SPECS_AND_TEMPLATE',
        'boilerplate_basis':'PUBLICATION_CONTRACT_REVIEW_AND_AUTHORITY_REQUIREMENTS',
        'market_or_time_saving_claim':'NOT_TESTED'})
    envelope = {'type':'object','required':['record_id','run_id','component_type','record_status',
        'evidence_status','visibility_scope','missing_fields','reason','author','data'],
        'properties':{'record_id':{'type':'string','minLength':1},'run_id':{'type':'string'},
            'component_type':{'enum':['source_record','claim_evidence_map','draft_asset','authority_record','execution_receipt','disposition']},
            'record_status':{'enum':['PRESENT','NOT_PRODUCED','UNAVAILABLE','NOT_APPLICABLE']},
            'evidence_status':{'enum':['OBSERVED','PARTIAL','MISSING','NOT_APPLICABLE']},
            'visibility_scope':{'type':'array','items':{'type':'string'},'minItems':1},
            'missing_fields':{'type':'array'},'author':{'type':'string'},'data':{'type':'object'}},
        'additionalProperties':True}
    names=['source_record','claim_evidence_map','draft_asset','authority_record','execution_receipt','disposition']
    put(ROOT/'schemas'/'package.schema.json', {'$schema':'https://json-schema.org/draft/2020-12/schema',
        'title':'PHC local package envelope schema; detailed semantics checked by observer',
        'type':'object','required':['run_id','attempt_id','bindings','components','recovery_authorship','original_attempts_preserved'],
        'properties':{'run_id':{'type':'string'},'attempt_id':{'type':'string'},'bindings':{'type':'object'},
            'components':{'type':'object','required':names,'properties':{n:envelope for n in names},'additionalProperties':False},
            'recovery_authorship':{'type':'string'},'original_attempts_preserved':{'type':'boolean'}},'additionalProperties':False})
    put(ROOT/'schemas'/'case_receipt.schema.json', {'$schema':'https://json-schema.org/draft/2020-12/schema',
        'type':'object','required':['case_id','execution_status','verdict','checks','bindings','evidence_paths','limitations'],
        'properties':{'case_id':{'type':'string','pattern':'^PHC-[0-9]{2}$'},
            'execution_status':{'enum':['EXECUTED','BLOCKED','NOT_RUN']},
            'verdict':{'enum':['SUPPORTED_WITHIN_TESTED_SCOPE','CONTRADICTED','UNRESOLVED','NOT_RUN']},
            'checks':{'type':'array','items':{'type':'object','required':['name','passed','observed'],
                'properties':{'name':{'type':'string'},'passed':{'type':'boolean'}}}},
            'bindings':{'type':'object'},'evidence_paths':{'type':'array'},'limitations':{'type':'array'}},
        'additionalProperties':True})
    put(ROOT/'fixtures'/'execution_envelope.json', {
        'max_suite_runs':1,'fixture_source_policy':'SUBMITTED_TEXT_AND_LABELED_SYNTHETIC_OVERLAYS',
        'max_workflow_attempts':30,'max_wall_seconds':30,'max_external_service_calls':0,
        'network_operations_in_runtime':0,'production_credentials':'NONE',
        'publisher':'LOCAL_EMPTY_JSON_MOCK_SINK','observer':'SEPARATE_PROCESS_SAME_UID',
        'allowed_effect_root':'results/sandbox','no_live_publication_authority':True,
        'authority':'SESSION_SCOPE_FOR_REVERSIBLE_LOCAL_PREPARATION_AND_TESTING',
        'not_claimed':['LLM_REASONING','PRODUCTION_NON_BYPASSABILITY','INTERPROCESS_ATOMICITY',
                       'TRANSFORMATION_EXPERIMENT_EQUIVALENCE','MARKET_DEMAND']})
    bound = sorted(p for p in ROOT.rglob('*') if p.is_file() and
                   p.relative_to(ROOT).parts[0] in ('src','contract','schemas','inputs','fixtures','history'))
    files={str(p.relative_to(ROOT)):sha(p) for p in bound if '__pycache__' not in p.parts}
    implementation={k:v for k,v in files.items() if k.startswith('src/')}
    implementation_digest=hashlib.sha256(json.dumps(implementation,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    manifest={'specimen_id':'PHC_LOCAL_PROTOTYPE_v0.1.1_candidate','specimen_version':'0.1.1','frozen_at_utc':datetime.now(timezone.utc).isoformat(),
              'contract_library_file_id':'libfile_662ec4b6e5c0819183c33bd10d6aa88a',
              'contract_sha256':sha(contract),'implementation_digest_method':'SHA256_OF_SORTED_COMPACT_JSON_PATH_TO_SHA256_MAP',
              'implementation_sha256':implementation_digest,'files':files,
              'schema_sha256':{k:v for k,v in files.items() if k.startswith('schemas/')},
              'python':sys.version,'platform':platform.platform(),'dependencies':'PYTHON_STANDARD_LIBRARY_ONLY',
              'schema_validation':'DECLARED_KEYWORD_SUBSET_PLUS_OBSERVER_SEMANTIC_CHECKS',
              'case_namespace':'PHC-01_THROUGH_PHC-12_FROM_PUBLICATION_CONTRACT',
              'transformation_mapping':'NONE_ASSERTED','source_admission':'HELD','git_binding':'UNBOUND',
              'prior_execution':json.loads((ROOT/'history/prior_execution.json').read_text())}
    put(ROOT/'manifest.json',manifest)
    print(json.dumps({'state':'FROZEN_BEFORE_EXECUTION','files_bound':len(files),'contract_sha256':manifest['contract_sha256'],
                      'implementation_sha256':implementation_digest,'manifest_sha256':sha(ROOT/'manifest.json')}))

if __name__=='__main__': main()

