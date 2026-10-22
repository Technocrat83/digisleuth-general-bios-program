"""Audit registered expectations, receipt bindings, replay and defect sensitivity."""
from pathlib import Path
import copy,hashlib,json,sys,tempfile,collections,platform,sqlite3
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'validation'));sys.path.insert(0,str(ROOT/'implementation'))
from validate_contract import inspect_contract,inspect_receipt,sha,load,require
from mock_harness import run_case
from observer import assess,hash_value

def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def inspect(path):
    r=load(path);inspect_receipt(ROOT,path)
    binding=load(ROOT/'evidence/implementation_binding.json')['fixture_binding']
    require(r['binding']==binding,'wrong pinned implementation binding')
    case=next(c for c in load(ROOT/'fixtures/registry.json')['cases'] if c['case_id']==r['case_id'])
    raw=load(path.parent/'effects.json')
    ob=r['independent_effect_observations']
    require(ob['before']==raw['before'] and ob['after']==raw['after'],'receipt and independent observation artifact differ')
    for name in ['before','after']:
        s=raw[name];require(s['publication_count']==len(s['publications']) and s['identity_count']==len(s['identities']),'snapshot row counts differ')
        require(s['protected_sha256']==hash_value({'publications':s['publications'],'identities':s['identities']}),'protected snapshot digest differs')
        require(s['governing_sha256']==hash_value(raw[name+'_control']['governing_files']),'governing snapshot digest differs')
    expected=assess(case,raw['before'],raw['after'],raw['before_control'],raw['after_control'],r['decision']['last'],r['decision']['reasons'],r['authoritative_ordering']['events'],any(e['kind']=='RECONCILE_UNKNOWN' for e in r['authoritative_ordering']['events']))
    require(expected==r['assertions'],'receipt omits or alters registered oracle checks')
    require(r['initial_conditions']['protected_initial_sha256']==raw['before']['protected_sha256'],'initial snapshot binding differs')
    return r

def canonical(r):
    return {k:r[k] for k in ['case_id','binding','initial_conditions','schedule','authoritative_ordering','decision','independent_effect_observations','assertions','outcome','kernel_properties','production_enforcement']}

def main():
    static=inspect_contract(ROOT);registry=load(ROOT/'fixtures/registry.json');summary=load(ROOT/'evidence/mock_run/summary.json')
    require(len(summary['results'])==len(registry['cases']),'suite omits registered cases')
    require({x['case_id'] for x in summary['results']}=={x['case_id'] for x in registry['cases']},'summary case set mismatch')
    receipts={}
    for item in summary['results']:
        require(item['receipt'] is not None,'case not run')
        r=inspect(ROOT/'evidence/mock_run'/item['receipt']);require(item['outcome']==r['outcome'],'summary outcome mismatch');receipts[r['case_id']]=r
    binding=load(ROOT/'evidence/implementation_binding.json')['fixture_binding'];replay=[]
    with tempfile.TemporaryDirectory(prefix='digisleuth-replay-') as tmp:
        for c in registry['cases']:
            r=run_case(ROOT,c,Path(tmp)/c['case_id'],binding,'replay-v0.1-run-002')
            require(canonical(r)==canonical(receipts[c['case_id']]),'non-deterministic replay: '+c['case_id'])
            replay.append({'case_id':c['case_id'],'matched':True})
    controls=[]
    for mutant,caseid in [('unsafe_stale_commit','F03-revoke-gap'),('unsafe_bypass','F05-direct'),('unsafe_tamper','F10-policy'),('unsafe_dedup','F07-lost-ack')]:
        c=next(c for c in registry['cases'] if c['case_id']==caseid);out=ROOT/'evidence/diagnostic_controls'/mutant
        r=run_case(ROOT,c,out,binding,'diagnostic-'+mutant,mutant=mutant);inspect(out/'receipt.json')
        require(r['outcome']=='CONTRADICTED','oracle failed to detect known defect: '+mutant)
        controls.append({'mutant':mutant,'case_id':caseid,'expected':'CONTRADICTED','observed':r['outcome'],'failed_assertions':[a['id'] for a in r['assertions'] if a['passed'] is False]})
    probes=[]
    with tempfile.TemporaryDirectory(prefix='digisleuth-receipt-probes-') as tmp:
        p=Path(tmp);source=ROOT/'evidence/mock_run/F01-normal'
        (p/'effects.json').write_bytes((source/'effects.json').read_bytes())
        for name,mut in [('wrong-implementation',lambda r:r['binding'].update(implementation_commit='0'*40)),('missing-oracle',lambda r:r.update(assertions=r['assertions'][:-1])),('no-revision',lambda r:r['binding'].update(implementation_commit=None)),('unobserved-positive',lambda r:r['independent_effect_observations'].update(after=None)),('forged-effect-count',lambda r:r['independent_effect_observations']['after'].update(publication_count=100)),('false-signature-label',lambda r:r['signature'].update(status='SIGNED'))]:
            r=copy.deepcopy(receipts['F01-normal']);mut(r);write(p/'receipt.json',r)
            try:inspect(p/'receipt.json')
            except Exception:probes.append({'id':name,'expected':'REJECT','observed':'REJECT'})
            else:raise AssertionError('bad receipt accepted: '+name)
        r=copy.deepcopy(receipts['F01-normal']);write(p/'receipt.json',r);(p/'effects.json').write_text('{}')
        try:inspect(p/'receipt.json')
        except Exception:probes.append({'id':'tampered-effect-artifact','expected':'REJECT','observed':'REJECT'})
        else:raise AssertionError('tampered effects accepted')
    report={'receipt_kind':'MOCK_EVIDENCE_INSPECTION','contract_commit':binding['contract_commit'],'implementation_commit':binding['implementation_commit'],'manifest_sha256':binding['contract_manifest_sha256'],'audit_tool_sha256':sha(Path(__file__)),'validator_sha256':sha(ROOT/'validation/validate_contract.py'),'observer_sha256':sha(ROOT/'implementation/observer.py'),'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'jsonschema_version':'4.25.1','structural_checks':static,'normal_cases_inspected':len(receipts),'normal_outcomes':dict(collections.Counter(r['outcome'] for r in receipts.values())),'families_accounted_for':len({r['fixture_id'] for r in receipts.values()}),'replay':{'cases':len(replay),'all_match':all(x['matched'] for x in replay),'comparison_excludes':['run_id','receipt_id','wall_clock_elapsed_seconds'],'case_results':replay},'diagnostic_defect_controls':controls,'invalid_receipt_probes':probes,'effect_observation_independence':'Read-only SQL observer, logically separate code, same trusted test host process. No OS isolation claim.','production_enforcement':'NOT_EVALUATED','real_boundary_cases':'NOT_RUN','kernel_properties':load(ROOT/'config/requirements.json')['kernel_properties'],'scientific_adjudication':'NOT_PERFORMED','certification':'NOT_GRANTED','signature_status':'UNSIGNED'}
    write(ROOT/'evidence/mock_evidence_inspection.json',report)
    print(json.dumps({'normal_cases':len(receipts),'families':report['families_accounted_for'],'replays_match':len(replay),'defect_controls_detected':len(controls),'bad_receipts_rejected':len(probes),'production_enforcement':'NOT_EVALUATED'}))
if __name__=='__main__':main()
