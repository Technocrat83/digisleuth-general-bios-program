"""Deterministic role/capability MODEL. Not an operating-system security boundary.

Authority updates and final checks/publication use one SQLite transaction domain.
The scheduler exercises declared serial interleavings; real concurrent races,
hostile Python, actual process isolation and external sinks are NOT_EVALUATED.
"""
import hashlib,json,sqlite3,time,sys,shutil,tempfile
from pathlib import Path
from observer import snapshot,assess,stable
from graph_rules import graph_admits

def digest(data):return hashlib.sha256(data).hexdigest()
def load(path):return json.loads(Path(path).read_text())
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
PAYLOAD='approved synthetic draft'
class Model:
    def __init__(self,directory,root,initial,mutant=None):
        self.d=Path(directory);self.root=root;self.mutant=mutant;self.tick=0;self.last=None;self.reasons=[];self.attempts=0;self.restarts=0;self.intent_calls={};self.pending=None;self.queue=[];self.available=True;self.unknown_seen=False
        self.d.mkdir(parents=True,exist_ok=True);(self.d/'governing').mkdir()
        for name,file in [('policy','config/policy.json'),('thresholds','config/policy.json'),('authoritative_evidence','config/requirements.json'),('authority_store','config/requirements.json')]:shutil.copyfile(root/file,self.d/'governing'/name)
        shutil.copyfile(root/'implementation/graph.json',self.d/'governing/graph')
        shutil.copyfile(root/'implementation/synthetic_evidence.json',self.d/'governing/authoritative_evidence')
        (self.d/'draft.txt').write_text(PAYLOAD)
        write(self.d/'worker_state.json',{'pending_unknown':False,'intent':'intent-001','cached_lock':False})
        self.c=sqlite3.connect(self.d/'model.sqlite',isolation_level=None)
        self.c.executescript('''CREATE TABLE authority(actor TEXT PRIMARY KEY,revoked INTEGER,expires INTEGER,scope TEXT,effect TEXT,parent TEXT);
        CREATE TABLE controls(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE publications(id INTEGER PRIMARY KEY,intent TEXT,payload TEXT,payload_sha TEXT);
        CREATE TABLE identities(intent TEXT PRIMARY KEY,payload_sha TEXT,publication_id INTEGER);
        CREATE TABLE events(seq INTEGER PRIMARY KEY AUTOINCREMENT,tick INTEGER,kind TEXT,actor TEXT,attempt_id TEXT,intent_id TEXT,details TEXT);''')
        self.c.executemany('INSERT INTO authority VALUES(?,?,?,?,?,?)',[('primary',0,100,'publication','CREATE',None),('delegate',0,100,'publication','CREATE','primary')])
        self.c.executemany('INSERT INTO controls VALUES(?,?)',[(k,json.dumps(v)) for k,v in {'lock':False,'drift':0,'evidence':True,'publication_budget':initial.get('publication_budget',3),'epoch':0}.items()])
        for i in range(initial.get('seed_publications',0)):
            intent='seed-'+str(i);ph=digest(PAYLOAD.encode());cur=self.c.execute('INSERT INTO publications(intent,payload,payload_sha) VALUES(?,?,?)',(intent,PAYLOAD,ph));self.c.execute('INSERT INTO identities VALUES(?,?,?)',(intent,ph,cur.lastrowid))
    def get(self,k):return json.loads(self.c.execute('SELECT value FROM controls WHERE key=?',(k,)).fetchone()[0])
    def set(self,k,v):self.c.execute('UPDATE controls SET value=? WHERE key=?',(json.dumps(v),k))
    def event(self,kind,actor='controller',intent=None,**details):
        self.c.execute('INSERT INTO events(tick,kind,actor,attempt_id,intent_id,details) VALUES(?,?,?,?,?,?)',(self.tick,kind,actor,'attempt-'+str(self.attempts) if self.attempts else None,intent,json.dumps(details,sort_keys=True)))
    def decide(self,value,reasons=()):self.last=value;self.reasons.extend(reasons);return value
    def predicates(self,payload,actor,effect):
        reasons=[];grant=self.c.execute('SELECT revoked,expires,scope,effect,parent FROM authority WHERE actor=?',(actor,)).fetchone()
        if not grant:reasons.append('AUTHORITY_MISSING')
        else:
            if grant[0]:reasons.append('AUTHORITY_REVOKED')
            if self.tick>=grant[1]:reasons.append('AUTHORITY_EXPIRED')
            if grant[2]!='publication' or grant[3]!=effect:reasons.append('SCOPE_OR_EFFECT_DENIED')
            if grant[4]:
                parent=self.c.execute('SELECT revoked,expires,scope,effect FROM authority WHERE actor=?',(grant[4],)).fetchone()
                if not parent or parent[0] or self.tick>=parent[1] or parent[2:]!=grant[2:4]:reasons.append('PARENT_AUTHORITY_INVALID')
        if effect!='CREATE':reasons.append('GRAPH_RULE_DENIED')
        if not graph_admits(load(self.d/'governing/graph'),actor):reasons.append('GRAPH_BINDING_INVALID')
        if digest(payload.encode())!=digest(PAYLOAD.encode()):reasons.append('APPROVAL_DIGEST_MISMATCH')
        if not self.get('evidence'):reasons.append('EVIDENCE_MISSING')
        elif digest((self.d/'governing/authoritative_evidence').read_bytes())!=load(self.d/'governing/graph')['evidence_sha256']:reasons.append('EVIDENCE_DIGEST_MISMATCH')
        if self.get('publication_budget')<=0:reasons.append('BUDGET_EXHAUSTED')
        if self.get('lock'):reasons.append('SCOPE_LOCKED')
        drift=self.get('drift');limits=load(self.root/'config/policy.json')['drift']
        if drift is None:reasons.append('DRIFT_UNKNOWN')
        elif drift>=limits['lock_at']:reasons.append('DRIFT_LOCKED')
        elif drift>=limits['warning_at']:reasons.append('DRIFT_REVIEW_REQUIRED')
        return reasons
    def admit(self,payload=PAYLOAD,actor='primary',effect='CREATE',intent='intent-001',**kwargs):
        self.attempts+=1;self.intent_calls[intent]=self.intent_calls.get(intent,0)+1
        if self.attempts>30 or self.intent_calls[intent]-1>2:raise RuntimeError('attempt or retry budget exceeded')
        if not self.available or load(self.d/'worker_state.json')['pending_unknown']:
            self.event('OUTCOME_UNKNOWN',actor,intent);return self.decide('BLOCKED_UNKNOWN',['RECONCILIATION_REQUIRED'])
        old=self.c.execute('SELECT payload_sha,publication_id FROM identities WHERE intent=?',(intent,)).fetchone()
        if old and self.mutant!='unsafe_dedup':
            if old[0]!=digest(payload.encode()):self.event('INTENT_CONFLICT',actor,intent);return self.decide('REJECTED',['INTENT_PAYLOAD_CONFLICT'])
            self.event('EXISTING_INTENT',actor,intent);return self.decide('EXISTING')
        reasons=self.predicates(payload,actor,effect)
        if reasons:
            verdict='REVIEW_REQUIRED' if reasons==['DRIFT_REVIEW_REQUIRED'] else 'REJECTED'
            self.event('ADMISSION_REJECTED',actor,intent,reasons=reasons);return self.decide(verdict,reasons)
        self.pending={'payload':payload,'actor':actor,'effect':effect,'intent':intent}
        self.event('ADMITTED',actor,intent,observed_epoch=self.get('epoch'));return self.decide('ADMITTED')
    def commit(self,lose_ack=False):
        if not self.pending:raise RuntimeError('commit without admitted request')
        q=self.pending;self.pending=None
        self.c.execute('BEGIN IMMEDIATE')
        try:
            self.event('COMMIT_ATTEMPT',q['actor'],q['intent'],current_epoch=self.get('epoch'))
            reasons=[] if self.mutant=='unsafe_stale_commit' else self.predicates(q['payload'],q['actor'],q['effect'])
            if reasons:
                self.event('COMMIT_REJECTED',q['actor'],q['intent'],reasons=reasons);self.c.execute('COMMIT');return self.decide('REJECTED',reasons)
            intent=q['intent'];ph=digest(q['payload'].encode())
            cur=self.c.execute('INSERT INTO publications(intent,payload,payload_sha) VALUES(?,?,?)',(intent,q['payload'],ph))
            if self.mutant=='unsafe_dedup':self.c.execute('INSERT OR REPLACE INTO identities VALUES(?,?,?)',(intent,ph,cur.lastrowid))
            else:self.c.execute('INSERT INTO identities VALUES(?,?,?)',(intent,ph,cur.lastrowid))
            self.set('publication_budget',self.get('publication_budget')-1)
            self.event('COMMITTED',q['actor'],intent,payload_sha=ph,publication_id=cur.lastrowid);self.c.execute('COMMIT')
        except BaseException:
            if self.c.in_transaction:self.c.execute('ROLLBACK')
            raise
        if lose_ack:
            write(self.d/'worker_state.json',{'pending_unknown':True,'intent':q['intent'],'cached_lock':self.get('lock')});self.event('ACK_LOST',q['actor'],q['intent']);return self.decide('ACK_UNKNOWN')
        return self.decide('COMMITTED')
    def publish(self,lose_ack=False,**kwargs):
        value=self.admit(**kwargs)
        return self.commit(lose_ack=lose_ack) if value=='ADMITTED' else value
    def run_step(self,s):
        self.tick+=1;op=s['op'];a=s['args'];self.event('SCHEDULE_STEP',op=op,args=a)
        if op in ['publish','admit','commit']:getattr(self,op)(**a)
        elif op in ['lock','unlock','revoke','grant']:
            self.event(op.upper()+'_REQUEST')
            self.c.execute('BEGIN IMMEDIATE')
            if op in ['lock','unlock']:self.set('lock',op=='lock')
            else:self.c.execute('UPDATE authority SET revoked=?,expires=?',(int(op=='revoke'),self.tick+100))
            self.set('epoch',self.get('epoch')+1);self.event(op.upper()+'_EFFECTIVE',epoch=self.get('epoch'));self.c.execute('COMMIT')
        elif op=='revise_draft':(self.d/'draft.txt').write_text('draft revision two');self.event('DRAFT_REVISED',actor='primary')
        elif op=='enqueue':self.queue.append({'intent':'intent-001'});self.event('ENQUEUED',intent='intent-001')
        elif op=='drain':
            for q in self.queue:self.publish(**q)
            self.queue.clear()
        elif op=='bypass':
            self.attempts+=1
            if self.mutant=='unsafe_bypass':
                ph=digest(PAYLOAD.encode());cur=self.c.execute('INSERT INTO publications(intent,payload,payload_sha) VALUES(?,?,?)',('bypass',PAYLOAD,ph));self.c.execute('INSERT INTO identities VALUES(?,?,?)',('bypass',ph,cur.lastrowid));self.decide('COMMITTED')
            else:self.decide('REJECTED',['MODEL_ACCESS_DENIED'])
            self.event('BYPASS_MODEL_PORT',actor='primary',route=a['route'],decision=self.last)
        elif op=='tamper':
            self.attempts+=1
            if self.mutant=='unsafe_tamper':(self.d/'governing'/a['target']).write_text('altered by worker');self.decide('COMMITTED')
            else:self.decide('REJECTED',['MODEL_ACCESS_DENIED'])
            self.event('TAMPER_MODEL_PORT',actor='primary',target=a['target'],decision=self.last)
        elif op=='checkpoint':write(self.d/'worker_state.json',{'pending_unknown':False,'intent':'intent-001','cached_lock':self.get('lock'),'cached_epoch':self.get('epoch')});self.event('CHECKPOINT_WRITTEN')
        elif op=='restart':
            self.restarts+=1
            if self.restarts>3:raise RuntimeError('restart budget exceeded')
            self.c.close();self.c=sqlite3.connect(self.d/'model.sqlite',isolation_level=None);self.pending=None;self.event('RESTARTED',current_epoch=self.get('epoch'),checkpoint_epoch=load(self.d/'worker_state.json').get('cached_epoch'))
        elif op=='reconcile':
            if not self.available:self.unknown_seen=True;self.event('RECONCILE_UNKNOWN',intent='intent-001')
            else:
                row=self.c.execute('SELECT payload_sha,publication_id FROM identities WHERE intent=?',('intent-001',)).fetchone();self.event('RECONCILED',intent='intent-001',existing=list(row) if row else None);write(self.d/'worker_state.json',{'pending_unknown':False,'intent':'intent-001','cached_lock':self.get('lock')})
        elif op in ['available','unavailable']:self.available=op=='available';self.event('SINK_AVAILABLE' if self.available else 'SINK_UNAVAILABLE')
        elif op=='advance':self.tick+=a['ticks']
        elif op=='set_evidence':self.set('evidence',a['present'])
        elif op=='drift':self.set('drift',a['value'])
        else:raise ValueError('unknown schedule operation')
    def events(self):return [{'seq':r[0],'tick':r[1],'kind':r[2],'actor':r[3],'attempt_id':r[4],'intent_id':r[5],'details':json.loads(r[6])} for r in self.c.execute('SELECT * FROM events ORDER BY seq')]

def run_case(root,case,out,binding,run_id,mutant=None):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=True);error=None
    with tempfile.TemporaryDirectory(prefix='digisleuth-publication-model-') as tmp:
        model=Model(tmp,root,case['initial_overrides'],mutant)
        before,bc=snapshot(tmp)
        try:
            for s in case['schedule']:
                if time.monotonic()-started>60:raise RuntimeError('time budget exceeded')
                model.run_step(s)
        except Exception as e:error=type(e).__name__+': '+str(e)
        after,ac=snapshot(tmp);events=model.events();model.c.close()
        assertions=assess(case,before,after,bc,ac,model.last,model.reasons,events,model.unknown_seen)
        outcome='UNRESOLVED' if error else 'SUPPORTED_WITHIN_FIXTURE' if all(x['passed'] for x in assertions) else 'CONTRADICTED'
        observations={'before':before,'after':after,'before_control':bc,'after_control':ac,'logical_separation_only':True}
        write(out/'effects.json',observations)
        receipt={'schema_version':'0.1.0','receipt_kind':'FIXTURE_RESULT','receipt_id':run_id+':'+case['case_id'],'run_id':run_id,'fixture_id':case['fixture_id'],'case_id':case['case_id'],'specimen_id':'EBA_TEST_001','mode':'MOCK','binding':binding,'initial_conditions':{'overrides':case['initial_overrides'],'protected_initial_sha256':before['protected_sha256'],'synthetic_payload_sha256':digest(PAYLOAD.encode()),'mutant':mutant,'initial_control':bc},'schedule':case['schedule'],'authoritative_ordering':{'mechanism':'SQLite event sequence; serial deterministic scheduler; final check and sink commit share BEGIN IMMEDIATE transaction','complete':error is None,'events':events},'decision':{'last':model.last,'reasons':model.reasons},'independent_effect_observations':{'observer_id':'observer.py:read-only-sql-connection','method':'SELECT protected publication and identity rows independently of decision logs; hash governing files and draft bytes','independence_limit':'Logical observer separation in the same trusted host process. No process/credential isolation established.','before':before,'after':after,'artifacts':[{'path':'effects.json','sha256':digest((out/'effects.json').read_bytes()),'size_bytes':(out/'effects.json').stat().st_size}]},'assertions':assertions,'usage':{'action_attempts':model.attempts,'restarts':model.restarts,'retries_per_intent':{k:max(0,v-1) for k,v in model.intent_calls.items()},'elapsed_seconds':round(time.monotonic()-started,6)},'outcome':outcome,'outcome_reason':error or 'All recorded expectations match independent observations.' if outcome=='SUPPORTED_WITHIN_FIXTURE' else error or 'One or more predeclared expectations contradicted.','claim_scope':'ONLY_RECORDED_CASE_AND_DECLARED_ENVELOPE','production_enforcement':'NOT_EVALUATED','kernel_properties':load(root/'config/requirements.json')['kernel_properties'],'signature':{'status':'UNSIGNED','algorithm':None,'signer':None,'value':None,'trust_assumptions':['Trusted local scheduler, SQLite implementation, host and observer code.'],'limitation':'Integrity and attribution do not establish complete mediation or factual truth.'}}
        write(out/'receipt.json',receipt)
        return receipt

def main():
    root=Path(__file__).resolve().parents[1];binding=load(root/'evidence/implementation_binding.json')['fixture_binding'];registry=load(root/'fixtures/registry.json')
    output=root/'evidence/mock_run';output.mkdir(exist_ok=True)
    results=[]
    for c in registry['cases']:
        r=run_case(root,c,output/c['case_id'],binding,'mock-v0.1-run-001');results.append({'case_id':c['case_id'],'fixture_id':c['fixture_id'],'outcome':r['outcome'],'receipt':c['case_id']+'/receipt.json'})
        if r['outcome']!='SUPPORTED_WITHIN_FIXTURE':break
    completed={r['case_id'] for r in results}
    results += [{'case_id':c['case_id'],'fixture_id':c['fixture_id'],'outcome':'NOT_RUN','receipt':None} for c in registry['cases'] if c['case_id'] not in completed]
    summary={'run_id':'mock-v0.1-run-001','specimen_id':'EBA_TEST_001','mode':'MOCK','binding':binding,'registered_families':12,'registered_cases':len(registry['cases']),'results':results,'production_enforcement':'NOT_EVALUATED','kernel_properties':load(root/'config/requirements.json')['kernel_properties']}
    write(output/'summary.json',summary);print(json.dumps({'cases':len(results),'outcomes':{k:sum(r['outcome']==k for r in results) for k in ['SUPPORTED_WITHIN_FIXTURE','CONTRADICTED','UNRESOLVED','NOT_RUN']}}))
    return int(any(r['outcome']!='SUPPORTED_WITHIN_FIXTURE' for r in results))
if __name__=='__main__':raise SystemExit(main())
