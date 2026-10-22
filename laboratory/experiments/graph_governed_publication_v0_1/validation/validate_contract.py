"""Inspect exact contract/receipt bytes. Does not establish runtime enforcement."""
from pathlib import Path
import copy, hashlib, json, sys
from jsonschema import Draft202012Validator

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def require(v, message):
    if not v: raise ValueError(message)
def validate_schema(root, name, document):
    s=load(root/'schemas'/name)
    Draft202012Validator.check_schema(s)
    Draft202012Validator(s).validate(document)
def inspect_contract(root):
    root=Path(root)
    for p in sorted((root/'schemas').glob('*.json')):
        Draft202012Validator.check_schema(load(p))
    m=load(root/'candidate_manifest.json')
    validate_schema(root,'candidate-manifest.schema.json',m)
    r=load(root/'fixtures/registry.json')
    validate_schema(root,'fixture-registry.schema.json',r)
    ids=[x['case_id'] for x in r['cases']]
    require(len(ids)==len(set(ids))==r['case_count'],'case IDs/count mismatch')
    require([x['fixture_id'] for x in r['families']]==[f'F{i:02d}' for i in range(1,13)],'family mapping mismatch')
    require(sorted(ids)==sorted(c for f in r['families'] for c in f['case_ids']),'family/case reconciliation failed')
    for f in r['families']:
        require(f['case_ids']==[c['case_id'] for c in r['cases'] if c['fixture_id']==f['fixture_id']],'case assigned to wrong family')
    paths=[]
    for x in m['files']:
        p=root/x['path']; require(p.resolve().is_relative_to(root.resolve()),'path escapes contract')
        require(p.is_file() and sha(p)==x['sha256'] and p.stat().st_size==x['size_bytes'],'digest/size mismatch: '+x['path'])
        paths.append(x['path'])
    require(len(paths)==len(set(paths)),'duplicate artifact path')
    expected=sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and str(p.relative_to(root)) not in m['exclusions'] and not any(part=='__pycache__' for part in p.parts) and not str(p.relative_to(root)).startswith(('evidence/','implementation/')))
    require(sorted(paths)==expected,'unlisted or missing contract file')
    require(sha(root/m['source']['path'])==m['source']['sha256'],'source binding mismatch')
    require(sha(root/m['fixture_registry']['path'])==m['fixture_registry']['sha256'],'registry binding mismatch')
    require(sha(root/m['execution_envelope']['path'])==m['execution_envelope']['sha256'],'envelope binding mismatch')
    require(m['fixture_registry']['case_count']==len(ids),'manifest case count mismatch')
    return {'schema_definitions_checked':len(list((root/'schemas').glob('*.json'))),'families':12,'cases':len(ids),'artifact_digests_checked':len(paths)}

def inspect_receipt(root, path):
    root=Path(root); path=Path(path); r=load(path)
    validate_schema(root,'fixture-receipt.schema.json',r)
    registry=load(root/'fixtures/registry.json')
    case=next((c for c in registry['cases'] if c['case_id']==r['case_id']),None)
    require(case is not None and case['fixture_id']==r['fixture_id'],'unknown fixture/case binding')
    require(case['schedule']==r['schedule'],'receipt schedule differs from registry')
    require(r['binding']['contract_manifest_sha256']==sha(root/'candidate_manifest.json'),'wrong contract digest')
    for key,file in [('registry_sha256','fixtures/registry.json'),('envelope_sha256','config/envelope.json'),('policy_sha256','config/policy.json')]:
        require(r['binding'][key]==sha(root/file),'wrong '+key)
    ev=r['authoritative_ordering']['events']; seq=[e['seq'] for e in ev]
    require(seq==sorted(set(seq)) and all(b>a for a,b in zip(seq,seq[1:])),'non-monotonic ordering')
    for a in r['assertions']:
        if a['passed'] is not None: require(a['passed']==(a['expected']==a['observed']),'assertion truth mismatch')
    if r['outcome']=='SUPPORTED_WITHIN_FIXTURE':
        require(r['assertions'] and all(a['passed'] is True for a in r['assertions']),'unsupported positive result')
        require(r['authoritative_ordering']['complete'],'positive result lacks ordering')
        require(r['independent_effect_observations']['before'] is not None and r['independent_effect_observations']['after'] is not None,'positive result lacks effect observations')
    if r['outcome']=='CONTRADICTED': require(any(a['passed'] is False for a in r['assertions']),'contradiction lacks a failed assertion')
    for a in r['independent_effect_observations']['artifacts']:
        p=path.parent/a['path']; require(p.resolve().is_relative_to(path.parent.resolve()),'receipt artifact escapes evidence directory')
        require(p.is_file() and sha(p)==a['sha256'] and p.stat().st_size==a['size_bytes'],'effect artifact mismatch')
    limits=load(root/'config/envelope.json'); usage=r['usage']
    if r['outcome']=='SUPPORTED_WITHIN_FIXTURE':
        require(usage['action_attempts']<=limits['max_action_attempts_per_case'],'action budget exceeded')
        require(usage['restarts']<=limits['max_restarts_per_case'],'restart budget exceeded')
        require(usage['elapsed_seconds']<=limits['max_seconds_per_case'],'time budget exceeded')
        require(all(n<=limits['max_retries_per_intent'] for n in usage['retries_per_intent'].values()),'retry budget exceeded')
    return r['outcome']

if __name__=='__main__':
    root=Path(sys.argv[1]).resolve()
    result=inspect_contract(root)
    if len(sys.argv)>2: result['receipt_outcome']=inspect_receipt(root,sys.argv[2])
    print(json.dumps(result,sort_keys=True))
