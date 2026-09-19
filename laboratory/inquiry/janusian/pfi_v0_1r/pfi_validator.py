"""Reference orchestration; host authenticates external events. Default denies readiness."""
import hashlib
import itertools
import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).parent
OUTCOMES=('PASS','FAIL','ABSTAIN','INVALID')
SCHEMAS={p.name:json.loads(p.read_text()) for p in ROOT.glob('*.schema.json')}
for s in SCHEMAS.values(): Draft202012Validator.check_schema(s)
def digest(raw): return hashlib.sha256(raw).hexdigest()
def strict_load(raw):
 def pairs(items):
  result={}
  for k,v in items:
   if k in result: raise ValueError('Duplicate JSON key: '+k)
   result[k]=v
  return result
 def reject(x): raise ValueError('Non-JSON numeric constant: '+x)
 return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=reject)
def errors(value,name):
 return [e.message for e in Draft202012Validator(SCHEMAS[name]).iter_errors(value)]
def report(status,reasons,stages,**kw):
 return dict(status=status,reasons=reasons,stages=stages,authority_delta=0,
             admission_granted=False,investigation_authorized=False,execution_requested=False,**kw)
def evaluate(candidate_bytes,*,source_bytes=None,review_bytes=None,separation_bytes=None,
             dependency_receipts=(),review_artifacts=None,authenticate=None):
 """authenticate(raw_receipt, artifact_bytes) must return literal True only after
 host-controlled authentication, reviewer eligibility, external event custody and
 revocation checks. It MUST NOT trust fields supplied by the candidate or receipt.
 No auth policy/key/allowlist may be loaded from candidate input. Exceptions deny.
 Hashes use original bytes, not reserialization; nothing is fetched or executed.
 """
 stages={k:'NOT_EVALUATED' for k in ('membrane','syntax','semantics','readiness')}
 try: c=strict_load(candidate_bytes)
 except (ValueError,UnicodeError,TypeError,RecursionError) as e:
  stages['syntax']='FAIL'
  return report('SYNTACTICALLY_INVALID',[str(e)],stages)
 # Parsing is transport precondition. Missing/mistyped declarations are structural
 # errors, not positive evidence of a membrane violation.
 m=c.get('epistemic_membrane',{}) if isinstance(c,dict) else {}
 violations=[]
 if isinstance(m,dict):
  for k in ('evidence_delta_claimed','truth_delta_claimed','authority_delta_claimed'):
   v=m.get(k)
   if type(v) in (int,float) and v!=0: violations.append(k+' != 0')
  for k in ('adjudication_power','investigation_authority'):
   if isinstance(m.get(k),str) and m[k]!='ZERO': violations.append(k+' != ZERO')
 if violations:
  stages['membrane']='FAIL'
  return report('EPISTEMIC_MEMBRANE_VIOLATION',violations,stages)
 err=errors(c,'pfi_candidate.schema.json')
 if err:
  stages['syntax']='FAIL'
  return report('SYNTACTICALLY_INVALID',err,stages)
 stages['membrane']='DECLARATIONS_PASS';stages['syntax']='PASS'
 # Local structural cross-record checks and sound, limited semantic rejection.
 for collection,key in ((c['assumptions'],'assumption_id'),(c['discrimination_vector'],'tension_id'),(c['admission_dependencies'],'dependency_id'),(c['constructive_pole']['possible_worlds'],'world_id'),(c['constructive_pole']['invariants'],'invariant_id'),(c['destructive_pole']['failure_surfaces'],'failure_id')):
  ids=[x[key] for x in collection]
  if len(ids)!=len(set(ids)):
   stages['syntax']='FAIL'
   return report('SYNTACTICALLY_INVALID',['Duplicate '+key],stages)
 for t in c['discrimination_vector']:
  conditions=t['collapse_requirement']['conditions']
  for a,b in itertools.combinations(OUTCOMES,2):
   if ' '.join(conditions[a]['condition'].split())==' '.join(conditions[b]['condition'].split()):
    stages['semantics']='FAIL'
    return report('SEMANTICALLY_UNREVIEWABLE',[t['tension_id']+': identical '+a+'/'+b+' predicates'],stages)
 # Different text never constitutes positive semantic review.
 cd=digest(candidate_bytes);pid=c['pfi_identity']['pfi_id'];artifacts=review_artifacts or {}
 def receipt(raw,name):
  if raw is None: return None
  try:
   r=strict_load(raw)
   if errors(r,name) or r['candidate_digest']!=cd or r['pfi_id']!=pid: return None
   a=artifacts.get(r['review_artifact_digest'])
   if not isinstance(a,bytes) or digest(a)!=r['review_artifact_digest']: return None
   if authenticate is None or authenticate(raw,a) is not True: return None
   return r
  except Exception: return None # Malformed or failed external verification: fail closed.
 r=receipt(review_bytes,'review_receipt.schema.json')
 if r is None:
  return report('PFI_NOT_READY',['Authenticated detached semantic review required'],stages)
 reviews=r['coordinate_reviews']; tids=[t['tension_id'] for t in c['discrimination_vector']]
 if sorted(x['tension_id'] for x in reviews)!=sorted(tids):
  return report('PFI_NOT_READY',['Review coordinate coverage mismatch'],stages)
 findings=[f for x in reviews for group in ('findings','pairwise_separation') for f in x[group].values()]
 if any(x['findings']['membrane_nonleakage']['status']=='FAIL' for x in reviews):
  stages['membrane']='FAIL'
  return report('EPISTEMIC_MEMBRANE_VIOLATION',['Authenticated review identifies semantic membrane leakage'],stages)
 if r['review_disposition']=='SEMANTICALLY_UNREVIEWABLE' or any(f['status']=='FAIL' for f in findings):
  stages['semantics']='FAIL'
  return report('SEMANTICALLY_UNREVIEWABLE',['Authenticated review rejected semantic closure'],stages)
 if r['review_disposition']!='SEMANTICALLY_REVIEWABLE' or any(f['status']!='PASS' for f in findings):
  return report('PFI_NOT_READY',['Semantic review remains unevaluated'],stages)
 stages['semantics']='PASS_BY_AUTHENTICATED_REVIEW';stages['membrane']='PASS_BY_AUTHENTICATED_REVIEW'
 missing=[]
 if not isinstance(source_bytes,bytes) or digest(source_bytes)!=c['provenance']['source_digest']:
  missing.append('Source bytes missing or digest mismatch')
 separation=receipt(separation_bytes,'authority_separation_receipt.schema.json')
 if separation is None: missing.append('Authenticated authority-separation receipt required')
 deps=[receipt(raw,'dependency_receipt.schema.json') for raw in dependency_receipts]
 for d in c['admission_dependencies']:
  if d['required'] and d['scope']=='PFI_READINESS':
   matches=[x for x in deps if x is not None and x['dependency_id']==d['dependency_id']]
   if len(matches)!=1 or matches[0]['disposition']!='SATISFIED': missing.append('Unresolved or ambiguous dependency: '+d['dependency_id'])
 if missing:
  stages['readiness']='FAIL'
  return report('PFI_NOT_READY',missing,stages)
 stages['readiness']='PASS'
 return report('PFI_READY',[],stages,meaning='ELIGIBLE_FOR_GOVERNANCE_ADMISSION_REVIEW',
               candidate_digest=cd,external_review_receipt_ref=r['receipt_id'],
               external_review_receipt_digest=digest(review_bytes),
               authority_separation_receipt_ref=separation['receipt_id'],
               authority_separation_receipt_digest=digest(separation_bytes),
               governance_dependencies=[d for d in c['admission_dependencies'] if d['scope']=='GOVERNANCE_REVIEW'])
if __name__=='__main__':
 import sys
 # CLI intentionally has no candidate-controlled trust option.
 print(json.dumps(evaluate(Path(sys.argv[1]).read_bytes()),indent=2))
