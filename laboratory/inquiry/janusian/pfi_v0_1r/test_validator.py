"""Synthetic branch tests; no real external review or investigation is asserted."""
import copy,itertools,json
from pathlib import Path
from pfi_validator import evaluate,digest,SCHEMAS,errors
ROOT=Path(__file__).parent
def dump(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
source=dump({'id':'SYNTHETIC_J_001','candidate':'A bounded integer classifier partitions its declared domain.'})
artifact=b'SYNTHETIC TEST REVIEW ARTIFACT. No real reviewer or scientific finding.\n'
conditions={k:{'outcome':k,'condition':v} for k,v in {'PASS':'Input is an integer equal to zero.','FAIL':'Input is an integer greater than zero.','ABSTAIN':'Input is an integer less than zero.','INVALID':'Input is not an integer; booleans are excluded from integers.'}.items()}
c={'schema_identity':{'schema_id':'PETITION_FOR_INVESTIGATION_CANDIDATE','schema_version':'0.1r','artifact_class':'EPISTEMIC_PETITION_CANDIDATE','standing':'UNADMITTED_CANDIDATE'},'pfi_identity':{'pfi_id':'SYNTHETIC_PFI_001','candidate_id':'SYNTHETIC_C_001','source_chamber':'JANUSIAN_THINKING_CHAMBER','source_method':'EINSTEIN_SOCRATES'},'epistemic_membrane':{'evidence_delta_claimed':0,'truth_delta_claimed':0,'authority_delta_claimed':0,'adjudication_power':'ZERO','investigation_authority':'ZERO'},'candidate':{'proposition':'A declared integer domain can be partitioned into four typed outcomes.'},'constructive_pole':{'statement':'A typed partition is possible.','minimal_model':'Three disjoint integer ranges and a complement of the integer domain.','possible_worlds':[{'world_id':'W1','boundary_conditions':['Mathematical integers, excluding booleans.'],'predicted_consequences':['Exactly one classification applies to each input.']}],'invariants':[]},'destructive_pole':{'statement':'Ambiguous integer typing can make the classifier overlap.','role':'DEFEATER','failure_surfaces':[{'failure_id':'F1','trigger':'Boolean accepted as integer.','affected_claim':'candidate.proposition','consequence':'DEFINITIONAL_FAILURE','explanation':'The mathematical domain and host language types may disagree.'}]},'assumptions':[{'assumption_id':'A1','statement':'Integer excludes boolean.','assumption_type':'SEMANTIC','standing':'UNEXAMINED','standing_basis':'Stipulated synthetic definition; no external corroboration asserted.'}],'discrimination_vector':[{'tension_id':'T1','positive_claim':'The partition is disjoint.','negative_claim':'Ambiguous typing permits overlap.','separation_basis':'MISSING_PROOF','separation_description':'Need proof relative to an explicit integer definition.','collapse_requirement':{'investigation_type':'FORMAL_PROOF','question':'Do the predicates partition the declared domain?','scope_and_limits':'A toy mathematical classifier; no physical claims.','target_of_success':'Partition completeness and disjointness.','observable_metric':'Proof obligations for typed domain coverage.','operational_definition':'Check all six intersections and union coverage.','units_or_not_applicable':'NOT_APPLICABLE','acquisition_or_design_obligation':'Downstream formal review must bind definitions.','expected_under_plus':'A proof of all intersections empty.','expected_under_minus':'A countermodel exploiting typing ambiguity.','against_plus':'An input satisfies two outcome predicates.','against_minus':'A proof removes the alleged overlap in the stated domain.','blindness_declaration':'Not applicable to this synthetic formal example.','confounder_declaration':'Host language boolean/integer coercion must be excluded.','alternative_space':'Incomplete coverage could defeat both narratives.','alternatives_exhaustive':False,'conditions':conditions}}],'admission_dependencies':[{'dependency_id':'D1','dependency_type':'EXTERNAL_REVIEW','required':True,'scope':'PFI_READINESS','description':'Externally authenticated readiness dependency.'},{'dependency_id':'D2','dependency_type':'JURISDICTION_CHECK','required':True,'scope':'GOVERNANCE_REVIEW','description':'Deferred to governance; no authorization implied.'}],'provenance':{'source_janusian_object_id':'SYNTHETIC_J_001','source_digest':digest(source),'source_digest_domain':'SHA256_EXACT_BYTES'}}
CHECKS=('discrimination','definitions','coverage','source_fidelity','claim_scope','membrane_nonleakage')
PAIRS=('PASS_FAIL','PASS_ABSTAIN','PASS_INVALID','FAIL_ABSTAIN','FAIL_INVALID','ABSTAIN_INVALID')
def fixtures(candidate):
 raw=dump(candidate);base={'pfi_id':candidate['pfi_identity']['pfi_id'],'candidate_digest':digest(raw),'reviewer_identity':'SYNTHETIC_REVIEWER','review_artifact_digest':digest(artifact),'verification_standing':'DETACHED_VERIFICATION_REQUIRED','authority_delta':0}
 f={'status':'PASS','reason':'Synthetic fixture expectation only.'}
 review={**base,'receipt_type':'PFI_EXTERNAL_REVIEW_RECEIPT','receipt_id':'SYNTHETIC_R1','review_disposition':'SEMANTICALLY_REVIEWABLE','coordinate_reviews':[{'tension_id':'T1','findings':{k:copy.deepcopy(f) for k in CHECKS},'pairwise_separation':{k:copy.deepcopy(f) for k in PAIRS}}]}
 sep={**base,'receipt_type':'AUTHORITY_SEPARATION_RECEIPT','receipt_id':'SYNTHETIC_AS1','scope':'PFI_EVALUATOR_OUTPUT_ONLY','admission_granted':False,'investigation_authorized':False,'execution_requested':False}
 dep={**base,'receipt_type':'PFI_DEPENDENCY_RECEIPT','receipt_id':'SYNTHETIC_D1','dependency_id':'D1','disposition':'SATISFIED'}
 raws=[dump(x) for x in (review,sep,dep)]
 # In-memory test double, never a deployed authentication mechanism.
 pinned=set(raws)
 kw=dict(source_bytes=source,review_bytes=raws[0],separation_bytes=raws[1],dependency_receipts=[raws[2]],review_artifacts={digest(artifact):artifact},authenticate=lambda r,a:r in pinned and a==artifact)
 return raw,kw,review,sep,dep
results=[]
def check(name,raw,kw,expected):
 r=evaluate(raw,**kw);assert r['status']==expected,(name,r)
 assert r['authority_delta']==0 and not any(r[x] for x in ('admission_granted','investigation_authorized','execution_requested'))
 results.append({'case':name,'expected':expected,'actual':r['status'],'passed':True,'scope':'SYNTHETIC_ORCHESTRATION_TEST'})
 return r
raw,kw,review,sep,dep=fixtures(c)
assert not errors(c,'pfi_candidate.schema.json')
for name,v in [('review_receipt.schema.json',review),('authority_separation_receipt.schema.json',sep),('dependency_receipt.schema.json',dep)]:assert not errors(v,name)
check('SPECIMEN_01_READY',raw,kw,'PFI_READY')
check('SPECIMEN_02_NOT_READY',raw,{**kw,'review_bytes':None},'PFI_NOT_READY')
fault=copy.deepcopy(c);fault['discrimination_vector'][0]['collapse_requirement']['conditions']['ABSTAIN']['condition']=conditions['FAIL']['condition']
check('SPECIMEN_03_ABSTAIN_FAULT',dump(fault),{},'SEMANTICALLY_UNREVIEWABLE')
leak=copy.deepcopy(c);leak['epistemic_membrane']['truth_delta_claimed']=1
check('SPECIMEN_04_INVALID_MEMBRANE',dump(leak),{},'EPISTEMIC_MEMBRANE_VIOLATION')
for a,b in itertools.combinations(conditions,2):
 x=copy.deepcopy(c);x['discrimination_vector'][0]['collapse_requirement']['conditions'][a]['condition']=conditions[b]['condition']
 check('pair_'+a+'_'+b,dump(x),{},'SEMANTICALLY_UNREVIEWABLE')
check('default_denies',raw,{**kw,'authenticate':None},'PFI_NOT_READY')
check('untrusted_string_identity',raw,{**kw,'review_bytes':kw['review_bytes'].replace(b'SYNTHETIC_REVIEWER',b'REVIEWER_SIG_PEER_KERNEL_GATE')},'PFI_NOT_READY')
check('candidate_byte_change',raw+b' ',kw,'PFI_NOT_READY')
check('source_mismatch',raw,{**kw,'source_bytes':b'changed'},'PFI_NOT_READY')
check('missing_separation',raw,{**kw,'separation_bytes':None},'PFI_NOT_READY')
check('missing_dependency',raw,{**kw,'dependency_receipts':[]},'PFI_NOT_READY')
check('duplicate_dependency_receipt',raw,{**kw,'dependency_receipts':kw['dependency_receipts']*2},'PFI_NOT_READY')
check('artifact_mismatch',raw,{**kw,'review_artifacts':{digest(artifact):b'wrong'}},'PFI_NOT_READY')
check('invalid_json',b'{',{},'SYNTACTICALLY_INVALID')
check('duplicate_json_keys',b'{"x":1,"x":2}',{},'SYNTACTICALLY_INVALID')
x=copy.deepcopy(c);x['candidate']['proposition']='   '
check('whitespace',dump(x),{},'SYNTACTICALLY_INVALID')
x=copy.deepcopy(c);x['semantic_review_signature']='FAKE'
check('embedded_review',dump(x),{},'SYNTACTICALLY_INVALID')
x=copy.deepcopy(c);x['epistemic_membrane']['truth_delta_claimed']=False
check('boolean_zero',dump(x),{},'SYNTACTICALLY_INVALID')
x=copy.deepcopy(c);x['discrimination_vector']*=2
check('duplicate_tension_id',dump(x),{},'SYNTACTICALLY_INVALID')
x=copy.deepcopy(c);x['discrimination_vector'][0]['collapse_requirement']['conditions']['PASS']['outcome']='FAIL'
check('wrong_outcome_label',dump(x),{},'SYNTACTICALLY_INVALID')
# Distinct predicate text with a failed semantic review cannot pass.
r2=copy.deepcopy(review);r2['coordinate_reviews'][0]['pairwise_separation']['PASS_FAIL']['status']='FAIL'
r2['coordinate_reviews'][0]['pairwise_separation']['PASS_FAIL']['reason']='Synthetic external finding: predicates overlap despite distinct text.'
r2raw=dump(r2)
check('semantic_overlap_detached_review',raw,{**kw,'review_bytes':r2raw,'authenticate':lambda r,a:r==r2raw and a==artifact},'SEMANTICALLY_UNREVIEWABLE')
r3=copy.deepcopy(review);r3['coordinate_reviews'][0]['findings']['coverage']['status']='NOT_EVALUATED';r3raw=dump(r3)
check('semantic_unknown',raw,{**kw,'review_bytes':r3raw,'authenticate':lambda r,a:r==r3raw and a==artifact},'PFI_NOT_READY')
r4=copy.deepcopy(review);r4['coordinate_reviews'][0]['findings']['membrane_nonleakage']['status']='FAIL';r4raw=dump(r4)
check('semantic_membrane_violation',raw,{**kw,'review_bytes':r4raw,'authenticate':lambda r,a:r==r4raw and a==artifact},'EPISTEMIC_MEMBRANE_VIOLATION')
def broken(r,a):raise RuntimeError('verifier unavailable')
check('verifier_exception',raw,{**kw,'authenticate':broken},'PFI_NOT_READY')
(ROOT/'test_results.json').write_bytes(dump({'tests':len(results),'passed':len(results),'real_review_events':0,'governance_admission_implemented':False,'cases':results}))
examples=ROOT/'synthetic_examples';examples.mkdir(exist_ok=True)
for name,data in [('candidate.json',raw),('source_janusian.json',source),('review_receipt.json',kw['review_bytes']),('authority_separation_receipt.json',kw['separation_bytes']),('dependency_receipt.json',kw['dependency_receipts'][0]),('review_artifact.txt',artifact),('membrane_fault.json',dump(leak)),('abstain_fault.json',dump(fault))]: (examples/name).write_bytes(data)
print(json.dumps({'tests':len(results),'passed':len(results),'real_review_events':0}))
