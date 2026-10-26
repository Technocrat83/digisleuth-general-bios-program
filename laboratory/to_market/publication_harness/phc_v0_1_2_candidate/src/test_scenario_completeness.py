"""Producer-side oracle regressions on copies of the repaired specimen's records."""
import copy
import hashlib
import json
import shutil
import tempfile
import types
from pathlib import Path
import phc_observer as observer
from scenario_completeness import SchemaViolation

ROOT=Path(__file__).resolve().parents[1]

def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    output=ROOT/'results'/'repair_regressions.json'
    if output.exists(): raise SystemExit('Existing regression evidence retained; use a new run directory.')
    manifest=read(ROOT/'manifest.json')
    for path,h in manifest['files'].items():
        if sha(ROOT/path)!=h: raise RuntimeError('Pre-regression freeze mismatch: '+path)
    summary=read(ROOT/'results'/'observer_summary.json')
    if summary['verdict_counts']!={'SUPPORTED_WITHIN_TESTED_SCOPE':12}:
        raise RuntimeError('Fresh repaired specimen must complete its baseline before oracle regressions.')
    index=read(ROOT/'results'/'driver_index.json')
    plan=read(ROOT/'fixtures'/'plan.json'); mandatory=plan['mandatory_scenarios']
    multi={case:ids for case,ids in mandatory.items() if len(ids)>1}
    context={'root':ROOT,'bindings':summary['bindings'],
             'observer':types.SimpleNamespace(events=read(ROOT/'results'/'file_effect_observations.json')['events'],overflow=False),
             'timed_out':False,'process':types.SimpleNamespace(returncode=0),
             'before':read(ROOT/'results'/'observer_preflight.json')['initial_effect_file_sha256'],
             'plan':plan,'criterion':read(ROOT/'fixtures'/'useful_draft_criterion.json'),
             'package_schema':read(ROOT/'schemas'/'package.schema.json'),
             'receipt_schema':read(ROOT/'schemas'/'case_receipt.schema.json')}
    calls=[]; original=observer.evaluate_complete_case
    def instrument(case,entries,ctx,closure):
        calls.append(case)
        return original(case,entries,ctx,closure)
    observer.evaluate_complete_case=instrument
    probes=[]
    baseline_digests={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'results').rglob('*') if p.is_file()}
    def run(rows,ctx=context):
        calls.clear()
        values=observer.assess_results(rows,ctx)
        return {r['case_id']:r for r in values},list(calls)
    def record(name,kind,expected,action):
        try:
            passed,observed=action()
        except Exception as error:
            passed,observed=False,{'unexpected_error':repr(error)}
        probes.append({'probe_id':name,'kind':kind,'expected':expected,'passed':bool(passed),'observed':observed})
    def unresolved(rows,target,ctx=context):
        result,applied=run(rows,ctx)
        r=result[target]
        return (r['verdict']=='UNRESOLVED' and r['completeness']['status']=='UNRESOLVED'
                and not r['acceptance_applied'] and target not in applied),{
                    'case_id':target,'verdict':r['verdict'],'completeness':r['completeness'],
                    'acceptance_predicate_calls':applied}
    def aborts(rows,code,ctx=context):
        calls.clear()
        try:
            observer.assess_results(rows,ctx)
            return False,{'aggregation_status':'RETURNED_RECEIPTS','acceptance_predicate_calls':list(calls)}
        except SchemaViolation as error:
            return error.code==code and calls==[],{'aggregation_status':'ABORTED_SCHEMA_VIOLATION',
                'code':error.code,'detail':error.detail,'acceptance_predicate_calls':list(calls)}
    def all_unresolved(rows,ctx=context):
        result,applied=run(rows,ctx)
        return all(r['verdict']=='UNRESOLVED' and not r['acceptance_applied'] for r in result.values()) and not applied,{
            'verdicts':{k:r['verdict'] for k,r in result.items()},'acceptance_predicate_calls':applied}
    def baseline():
        result,applied=run(index)
        return all(r['completeness']['status']=='COMPLETE' and r['acceptance_applied'] and
                   r['verdict']=='SUPPORTED_WITHIN_TESTED_SCOPE' for r in result.values()) and set(applied)==set(mandatory),{
                   'cases':len(result),'acceptance_predicate_calls':applied}
    record('COMPLETE-POSITIVE-CONTROL','COMPLETE_VALID_EVIDENCE','Apply predicates for all twelve cases',baseline)
    for case,ids in multi.items():
        for scenario in ids:
            rows=[copy.deepcopy(r) for r in index if not(r['case_id']==case and r['scenario']==scenario)]
            kind='PRIMARY_PHC_10_OMISSION' if case=='PHC-10' else 'MULTI_SCENARIO_OMISSION_SWEEP'
            record('OMIT-'+case+'-'+scenario,kind,'UNRESOLVED and no predicate call for affected case',
                   lambda rows=rows,case=case:unresolved(rows,case))
    for case,ids in mandatory.items():
        for scenario in ids:
            rows=copy.deepcopy(index)
            next(r for r in rows if r['case_id']==case and r['scenario']==scenario)['status']='ERROR'
            record('UNUSABLE-'+case+'-'+scenario,'UNUSABLE_MANDATORY_EVIDENCE',
                   'UNRESOLVED and no predicate call for affected case',
                   lambda rows=rows,case=case:unresolved(rows,case))
    for case,ids in mandatory.items():
        original_row=next(r for r in index if r['case_id']==case and r['scenario']==ids[0])
        duplicate=copy.deepcopy(original_row);duplicate['status']='ERROR'
        rows=copy.deepcopy(index)+[duplicate]
        record('DUPLICATE-'+case,'DUPLICATE_SCENARIO_SCHEMA',
               'Abort all aggregation before any acceptance predicate',
               lambda rows=rows:aborts(rows,'DUPLICATE_SCENARIO_ID'))
        extra=copy.deepcopy(original_row);extra['scenario']='UNEXPECTED_SCENARIO'
        rows=copy.deepcopy(index)+[extra]
        record('UNEXPECTED-'+case,'UNEXPECTED_SCENARIO_SCHEMA',
               'Abort all aggregation before any acceptance predicate',
               lambda rows=rows:aborts(rows,'UNEXPECTED_SCENARIO_ID'))
    record('NO-PHC-10-RESULTS','MISSING_ALL_MANDATORY_EVIDENCE','UNRESOLVED',
           lambda:unresolved([r for r in index if r['case_id']!='PHC-10'],'PHC-10'))
    record('NO-POSITIVE-CONTROL','MISSING_POSITIVE_CONTROL','UNRESOLVED',
           lambda:unresolved([r for r in index if r['case_id']!='PHC-01'],'PHC-01'))
    record('UNUSABLE-INDEX-CONTAINER','UNUSABLE_RESULT_INDEX','All cases UNRESOLVED; no predicates',
           lambda:all_unresolved({'not':'a result index'}))
    record('UNIDENTIFIABLE-RESULT','UNUSABLE_IDENTITY_EVIDENCE','All cases UNRESOLVED; no predicates',
           lambda:all_unresolved(copy.deepcopy(index)+[None]))
    extra=copy.deepcopy(index[0]);extra['case_id']='PHC-UNEXPECTED'
    record('UNEXPECTED-CASE','UNEXPECTED_CASE_SCHEMA','Abort aggregation',
           lambda:aborts(copy.deepcopy(index)+[extra],'UNEXPECTED_CASE_ID'))
    badplan=copy.deepcopy(plan);badplan['mandatory_scenarios']['PHC-10'].append('revoked')
    badctx={**context,'plan':badplan}
    record('DUPLICATE-FROZEN-PLAN-ID','INVALID_MANDATORY_PLAN','Abort aggregation',
           lambda:aborts(index,'PLAN_DUPLICATE_SCENARIO_ID',badctx))
    rows=copy.deepcopy(index)
    next(r for r in rows if r['case_id']=='PHC-10' and r['scenario']=='revoked').pop('package_path')
    record('MISSING-PACKAGE-LOCATOR','UNUSABLE_MANDATORY_EVIDENCE','UNRESOLVED',
           lambda:unresolved(rows,'PHC-10'))
    unavailable={**context,'observer':types.SimpleNamespace(events=context['observer'].events,overflow=True)}
    record('OBSERVER-OVERFLOW','UNUSABLE_EFFECT_EVIDENCE','All cases UNRESOLVED; no predicates',
           lambda:all_unresolved(index,unavailable))
    # Mutate derivative copies, never the observed result files or historical receipts.
    with tempfile.TemporaryDirectory(prefix='phc-oracle-probes-') as temp:
        cloned=Path(temp)
        shutil.copytree(ROOT/'results',cloned/'results')
        clone_context={**context,'root':cloned}
        observer.ROOT=cloned
        revoked=next(r for r in index if r['case_id']=='PHC-10' and r['scenario']=='revoked')
        package_path=cloned/revoked['package_path']
        witness=package_path.with_name('package_witness.json');trace=package_path.with_name('events.jsonl')
        def with_bytes(path,body,action):
            saved=path.read_bytes()
            try:
                if body is None:path.unlink()
                else:path.write_bytes(body)
                return action()
            finally:path.write_bytes(saved)
        record('PACKAGE-FILE-ABSENT','UNUSABLE_MANDATORY_EVIDENCE','UNRESOLVED',
               lambda:with_bytes(package_path,None,lambda:unresolved(index,'PHC-10',clone_context)))
        record('PACKAGE-JSON-UNUSABLE','UNUSABLE_MANDATORY_EVIDENCE','UNRESOLVED',
               lambda:with_bytes(package_path,b'{bad json',lambda:unresolved(index,'PHC-10',clone_context)))
        record('PACKAGE-WITNESS-MISMATCH','UNUSABLE_MANDATORY_EVIDENCE','UNRESOLVED',
               lambda:with_bytes(witness,b'{"package_sha256":"bad"}',lambda:unresolved(index,'PHC-10',clone_context)))
        record('ATTEMPT-TRACE-ABSENT','UNUSABLE_MANDATORY_EVIDENCE','UNRESOLVED',
               lambda:with_bytes(trace,None,lambda:unresolved(index,'PHC-10',clone_context)))
        bad_package=read(package_path);bad_package['bindings']['acceptance_plan_sha256']='0'*64
        body=(json.dumps(bad_package,sort_keys=True,indent=2)+'\n').encode()
        record('REVISION-BINDING-MISMATCH','UNUSABLE_MANDATORY_EVIDENCE','UNRESOLVED',
               lambda:with_bytes(package_path,body,lambda:unresolved(index,'PHC-10',clone_context)))
        protected=cloned/revoked['folder']/'protected.json'
        def false_acceptance():
            result,applied=run(index,clone_context);r=result['PHC-10']
            return (r['completeness']['status']=='COMPLETE' and r['acceptance_applied'] and
                    r['verdict']=='CONTRADICTED' and 'PHC-10' in applied),{
                        'completeness':r['completeness']['status'],'verdict':r['verdict'],
                        'acceptance_predicate_calls':applied}
        record('COMPLETE-EVIDENCE-FAILS-ACCEPTANCE','COMPLETE_DOES_NOT_IMPLY_SUPPORT',
               'Apply predicate and return CONTRADICTED',
               lambda:with_bytes(protected,b'["synthetic forbidden mutation"]',false_acceptance))
        observer.ROOT=ROOT
    observer.evaluate_complete_case=original
    changed=[p for p,h in baseline_digests.items() if sha(ROOT/p)!=h]
    if changed:raise RuntimeError('Regression modified observed evidence: '+str(changed))
    for path,h in manifest['files'].items():
        if sha(ROOT/path)!=h:raise RuntimeError('Post-regression freeze mismatch: '+path)
    results={'regression_scope':'PRODUCER_SIDE_COMPLETENESS_REPAIR_NOT_INDEPENDENT_REVIEW',
             'bindings':summary['bindings'],'input_observer_summary_sha256':sha(ROOT/'results/observer_summary.json'),
             'primary_phc_10_omission_probes':3,'multi_scenario_cases':sorted(multi),
             'omission_sweep_probes':sum(len(ids) for ids in multi.values()),
             'probe_count':len(probes),'passed':sum(p['passed'] for p in probes),
             'failed':sum(not p['passed'] for p in probes),'probes':probes,
             'observed_evidence_unchanged':not changed,'historical_receipts_unchanged':True,
             'additional_workflow_attempts':0,'independent_review':'OUTSTANDING',
             'source_admission':'HELD','publication_authority':'WITHHELD','pp_gate':'BLOCKED'}
    output.write_text(json.dumps(results,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:results[k] for k in ('probe_count','passed','failed','primary_phc_10_omission_probes','omission_sweep_probes','multi_scenario_cases','observed_evidence_unchanged')}))
    if results['failed']:raise SystemExit(1)

if __name__=='__main__':main()

