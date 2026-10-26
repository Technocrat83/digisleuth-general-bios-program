"""Mandatory evidence closure before acceptance. No artifact writes or adjudication authority."""
import hashlib
import json
import math
import re
from pathlib import Path
from schema_subset import validate

COMPONENTS={'source_record','claim_evidence_map','draft_asset','authority_record','execution_receipt','disposition'}

class SchemaViolation(ValueError):
    def __init__(self, code, detail):
        super().__init__(code+': '+detail)
        self.code, self.detail = code, detail

def canonical(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()

def hash_value(value): return hashlib.sha256(canonical(value)).hexdigest()

def bind_index(plan, index, case_ids):
    mandatory=plan.get('mandatory_scenarios') if isinstance(plan,dict) else None
    if not isinstance(mandatory,dict) or set(mandatory)!=set(case_ids):
        raise SchemaViolation('PLAN_SCHEMA_INVALID','Mandatory case identities must match the contract case set.')
    for case, ids in mandatory.items():
        if not isinstance(ids,list) or not ids or any(not isinstance(s,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',s) for s in ids):
            raise SchemaViolation('PLAN_SCHEMA_INVALID',case+' requires a nonempty list of scenario IDs.')
        if len(ids)!=len(set(ids)):
            raise SchemaViolation('PLAN_DUPLICATE_SCENARIO_ID',case)
    mapped={case:{} for case in case_ids}
    issues={case:[] for case in case_ids}
    if not isinstance(index,list):
        return mandatory,mapped,{case:['UNUSABLE_RESULT_INDEX'] for case in case_ids}
    for row in index:
        if not isinstance(row,dict) or not isinstance(row.get('case_id'),str):
            for case in case_ids: issues[case].append('UNASSIGNABLE_RESULT_RECORD')
            continue
        case=row['case_id']
        if case not in mandatory: raise SchemaViolation('UNEXPECTED_CASE_ID',case)
        scenario=row.get('scenario')
        if not isinstance(scenario,str):
            issues[case].append('UNUSABLE_SCENARIO_ID')
            continue
        if scenario not in mandatory[case]:
            raise SchemaViolation('UNEXPECTED_SCENARIO_ID',case+'/'+scenario)
        if scenario in mapped[case]:
            # Count every occurrence before evidence usability: a bad duplicate still aborts.
            raise SchemaViolation('DUPLICATE_SCENARIO_ID',case+'/'+scenario)
        mapped[case][scenario]=row
    return mandatory,mapped,issues

def usable_result(case, scenario, row, context):
    reasons=[]
    def need(condition, reason):
        if not condition: reasons.append(reason)
    try:
        root=Path(context['root']).resolve()
        need(row.get('status')=='EXECUTED','RESULT_NOT_COMPLETED')
        for field in ('wall_seconds','cpu_seconds'):
            value=row.get(field)
            need(type(value) in (int,float) and math.isfinite(value) and value>=0,'UNUSABLE_'+field.upper())
        attempts=row.get('workflow_attempts')
        need(type(attempts) is int and attempts>=1,'UNUSABLE_ATTEMPT_COUNT')
        expected_folder=f'results/sandbox/{case}/{scenario}'
        need(row.get('folder')==expected_folder,'SCENARIO_FOLDER_IDENTITY_MISMATCH')
        package_path=row.get('package_path')
        match=re.fullmatch(re.escape(expected_folder)+r'/attempts/([1-9][0-9]*)/package[.]json',package_path) if isinstance(package_path,str) else None
        need(match is not None,'UNUSABLE_PACKAGE_LOCATOR')
        if not match or reasons:
            return False,reasons
        path=(root/package_path).resolve()
        need(path.is_relative_to(root),'PACKAGE_PATH_OUTSIDE_SPECIMEN')
        if reasons: return False,reasons
        raw=path.read_bytes(); package=json.loads(raw)
        validate(package,context['package_schema'])
        need(package['bindings']==context['bindings'],'PACKAGE_BINDING_MISMATCH')
        need(package['run_id']==case+'-'+scenario,'RUN_IDENTITY_MISMATCH')
        need(package['attempt_id']==match[1],'ATTEMPT_IDENTITY_MISMATCH')
        records=package['components']
        need(set(records)==COMPONENTS,'REQUIRED_COMPONENT_SET_MISMATCH')
        record_ids=[]
        for name,record in records.items():
            need(record['component_type']==name,'COMPONENT_TYPE_MISMATCH')
            need(record['run_id']==package['run_id'],'COMPONENT_RUN_ID_MISMATCH')
            record_ids.append(record['record_id'])
        need(len(record_ids)==len(set(record_ids)),'DUPLICATE_COMPONENT_RECORD_ID')
        receipt=records['execution_receipt']['data']
        need(receipt.get('bindings')==context['bindings'],'RECEIPT_BINDING_MISMATCH')
        digests=receipt.get('component_digests')
        need(isinstance(digests,dict) and set(digests)==COMPONENTS-{'execution_receipt'},'UNUSABLE_COMPONENT_DIGEST_INDEX')
        if isinstance(digests,dict):
            need(all(k in records and hash_value(records[k])==h for k,h in digests.items()),'COMPONENT_DIGEST_MISMATCH')
        witness=json.loads(path.with_name('package_witness.json').read_text())
        need(witness.get('package_sha256')==hashlib.sha256(raw).hexdigest(),'PACKAGE_WITNESS_MISMATCH')
        source=records['source_record']['data']
        if source.get('capture_status')=='CAPTURED':
            text=source.get('source_text')
            need(isinstance(text,str),'CAPTURED_SOURCE_BYTES_UNAVAILABLE')
            if isinstance(text,str):
                need(source.get('source_sha256')==hashlib.sha256(text.encode()).hexdigest(),'SOURCE_DIGEST_MISMATCH')
        traces=sorted((root/expected_folder/'attempts').glob('*/events.jsonl'))
        need(len(traces)==attempts,'ATTEMPT_TRACE_COUNT_MISMATCH')
        events=[json.loads(line) for line in path.with_name('events.jsonl').read_text().splitlines()]
        need(bool(events) and events[0].get('event')=='ATTEMPT_START','ATTEMPT_START_EVIDENCE_MISSING')
        need([e.get('sequence') for e in events]==list(range(1,len(events)+1)),'UNUSABLE_EVENT_ORDER')
        recorded=receipt.get('events')
        need(isinstance(recorded,list) and bool(recorded) and recorded==events[:len(recorded)],'RECEIPT_TRACE_BINDING_MISMATCH')
        obs=context['observer']
        need(not obs.overflow and not context['timed_out'] and context['process'].returncode==0,'EFFECT_OBSERVATION_UNAVAILABLE')
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as error:
        reasons.append('UNUSABLE_EVIDENCE:'+type(error).__name__)
    return not reasons,sorted(set(reasons))

def close_case(case, mandatory, mapped, issues, context):
    missing=[scenario for scenario in mandatory[case] if scenario not in mapped[case]]
    unusable={}
    valid=[]
    for scenario in mandatory[case]:
        if scenario not in mapped[case]: continue
        row=mapped[case][scenario]
        ok,reasons=usable_result(case,scenario,row,context)
        if ok: valid.append(row)
        else: unusable[scenario]=reasons
    closure={'status':'COMPLETE' if not missing and not unusable and not issues[case] else 'UNRESOLVED',
             'mandatory_scenario_ids':mandatory[case],
             'observed_scenario_ids':list(mapped[case]),
             'valid_scenario_ids':[row['scenario'] for row in valid],
             'missing_scenario_ids':missing,'unusable_scenarios':unusable,'unassigned_evidence_issues':issues[case],
             'acceptance_plan_sha256':context['bindings']['acceptance_plan_sha256']}
    return closure,valid

def unresolved_receipt(case, closure, entries, context):
    return {'case_id':case,'execution_status':'EXECUTED' if entries else 'NOT_RUN','verdict':'UNRESOLVED',
            'acceptance_applied':False,'completeness':closure,
            'checks':[{'name':'mandatory_scenario_evidence_complete','passed':False,'observed':closure}],
            'bindings':context['bindings'],
            'evidence_paths':[row['folder'] for row in entries if isinstance(row.get('folder'),str)],
            'limitations':['MANDATORY_EVIDENCE_CLOSURE_NOT_REACHED','NO_ACCEPTANCE_PREDICATE_APPLIED'],
            'required_observation':next(row['required_observation'] for row in context['plan']['case_contract_rows'] if row['case_id']==case),
            'workflow_attempts':sum(row.get('workflow_attempts',0) for row in entries if type(row.get('workflow_attempts')) is int)}

