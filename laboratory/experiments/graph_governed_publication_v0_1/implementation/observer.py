"""Resource inspection independent of the model's decision result.

Logical separation only: observer and model share a trusted test process/host.
"""
import hashlib, json, sqlite3
from pathlib import Path

def stable(value): return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def hash_value(value): return hashlib.sha256(stable(value)).hexdigest()
def snapshot(directory):
    d=Path(directory)
    c=sqlite3.connect('file:'+str((d/'model.sqlite').resolve())+'?mode=ro',uri=True)
    try:
        pubs=[list(r) for r in c.execute('SELECT id,intent,payload,payload_sha FROM publications ORDER BY id')]
        ids=[list(r) for r in c.execute('SELECT intent,payload_sha,publication_id FROM identities ORDER BY intent')]
        auth=[list(r) for r in c.execute('SELECT actor,revoked,expires,scope,effect,parent FROM authority ORDER BY actor')]
        controls=[list(r) for r in c.execute('SELECT key,value FROM controls ORDER BY key')]
    finally:c.close()
    governing={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((d/'governing').iterdir())}
    return {'publication_count':len(pubs),'identity_count':len(ids),'protected_sha256':hash_value({'publications':pubs,'identities':ids}),'governing_sha256':hash_value(governing),'draft_sha256':hashlib.sha256((d/'draft.txt').read_bytes()).hexdigest(),'publications':pubs,'identities':ids}, {'authority':auth,'controls':controls,'governing_files':governing}

def assess(case,before,after,before_control,after_control,last,reasons,events,unknown_seen):
    expected=case['expectations'];checks=[]
    def check(name,e,o):checks.append({'id':name,'expected':e,'observed':o,'passed':e==o})
    observations={'publication_count':after['publication_count'],'identity_count':after['identity_count'],
      'protected_rows_changed':before['protected_sha256']!=after['protected_sha256'],
      'draft_changed':before['draft_sha256']!=after['draft_sha256'],
      'governing_bytes_unchanged':before['governing_sha256']==after['governing_sha256'],
      'last_decision':last,'recovery_unknown':unknown_seen}
    for k,v in observations.items():check(k,expected[k],v)
    check('required_reasons_present',True,all(x in reasons for x in expected['required_reasons']))
    check('publication_payload_hashes_match',True,all(hashlib.sha256(r[2].encode()).hexdigest()==r[3] for r in after['publications']))
    check('unique_publication_intents',True,len({r[1] for r in after['publications']})==len(after['publications']))
    mapping={r[0]:(r[1],r[2]) for r in after['identities']}
    check('identity_rows_match_publications',True,all(mapping.get(r[1])==(r[3],r[0]) for r in after['publications']))
    if case['fixture_id']=='F10':
        check('authority_and_control_rows_unchanged',True,before_control==after_control)
    if case['fixture_id']=='F04':
        check('specified_draft_revision_completed',hashlib.sha256(b'draft revision two').hexdigest(),after['draft_sha256'])
    kinds={}
    for e in events:kinds.setdefault(e['kind'],[]).append(e['seq'])
    if case['fixture_id']=='F02':
        check('revocation_before_admission',True,bool(kinds.get('REVOKE_EFFECTIVE')) and bool(kinds.get('ADMISSION_REJECTED')) and kinds['REVOKE_EFFECTIVE'][0]<kinds['ADMISSION_REJECTED'][0])
    if case['fixture_id']=='F03':
        control='REVOKE_EFFECTIVE' if case['case_id'].endswith('revoke-gap') else 'LOCK_EFFECTIVE'
        order=bool(kinds.get('ADMITTED')) and bool(kinds.get(control)) and bool(kinds.get('COMMIT_ATTEMPT'))
        check('admission_control_commit_attempt_order',True,bool(order and kinds['ADMITTED'][0]<kinds[control][0]<kinds['COMMIT_ATTEMPT'][0]))
    if case['case_id']=='F11-commit-before-controls':
        check('commit_before_later_controls',True,bool(kinds.get('COMMITTED')) and kinds['COMMITTED'][0]<kinds['REVOKE_EFFECTIVE'][0]<kinds['LOCK_EFFECTIVE'][0])
    return checks
