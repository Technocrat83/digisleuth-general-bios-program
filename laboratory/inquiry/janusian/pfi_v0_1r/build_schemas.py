import json
from pathlib import Path
ROOT=Path(__file__).parent
T={'type':'string','minLength':1,'pattern':r'\S'}
H={'type':'string','pattern':'^[a-f0-9]{64}$'}
def const(v): return {'const':v}
def en(*v): return {'enum':list(v)}
def arr(v,n=0): return {'type':'array','items':v,'minItems':n}
def obj(p): return {'type':'object','additionalProperties':False,'required':list(p),'properties':p}
def schema(name,p):
 s=obj(p);s.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:digisleuth:'+name+':0.1r','title':name});return s
def save(name,s): (ROOT/name).write_text(json.dumps(s,indent=2)+'\n')
O=('PASS','FAIL','ABSTAIN','INVALID')
mem=obj({**{k:const(0) for k in ('evidence_delta_claimed','truth_delta_claimed','authority_delta_claimed')},**{k:const('ZERO') for k in ('adjudication_power','investigation_authority')}})
world=obj({'world_id':T,'boundary_conditions':arr(T),'predicted_consequences':arr(T,1)})
inv=obj({'invariant_id':T,'formulation':T,'standing':const('HYPOTHESIS_ONLY')})
fail=obj({'failure_id':T,'trigger':T,'affected_claim':T,'consequence':en('CONTRADICTION','INDETERMINACY','DOMAIN_COLLAPSE','DEFINITIONAL_FAILURE','CAUSAL_FAILURE','OTHER'),'explanation':T})
assumption=obj({'assumption_id':T,'statement':T,'assumption_type':en('STRUCTURAL','EMPIRICAL','SEMANTIC','CAUSAL','JURISDICTIONAL','OPERATIONAL'),'standing':en('UNEXAMINED','ANECDOTAL','PARTIALLY_CORROBORATED','FORMALLY_CONSTRAINED','EMPIRICALLY_FALSIFIED'),'standing_basis':T})
# Fixed property names and constant labels enforce four unique typed outcome slots.
conditions=obj({o:obj({'outcome':const(o),'condition':T}) for o in O})
req=obj({'investigation_type':en('EMPIRICAL_TEST','FORMAL_PROOF','COUNTEREXAMPLE_SEARCH','SIMULATION','MEASUREMENT','REPLICATION','SOURCE_RECOVERY','DEFINITIONAL_ADJUDICATION'),'question':T,'scope_and_limits':T,'target_of_success':T,'observable_metric':T,'operational_definition':T,'units_or_not_applicable':T,'acquisition_or_design_obligation':T,'expected_under_plus':T,'expected_under_minus':T,'against_plus':T,'against_minus':T,'blindness_declaration':T,'confounder_declaration':T,'alternative_space':T,'alternatives_exhaustive':const(False),'conditions':conditions})
tension=obj({'tension_id':T,'positive_claim':T,'negative_claim':T,'separation_basis':en('MISSING_MEASUREMENT','MISSING_PROOF','UNBOUND_DEFINITION','FRAME_DEPENDENCE','MISSING_COUNTERFACTUAL','CAUSAL_AMBIGUITY','SCALE_DEPENDENCE','UNKNOWN'),'separation_description':T,'collapse_requirement':req})
dep=obj({'dependency_id':T,'dependency_type':en('EXTERNAL_REVIEW','FORMAL_VERIFICATION','MEASUREMENT_CAPABILITY','JURISDICTION_CHECK','SAFETY_REVIEW','OTHER'),'required':{'type':'boolean'},'scope':en('PFI_READINESS','GOVERNANCE_REVIEW'),'description':T})
p=schema('PFI_CANDIDATE_SCHEMA',{'schema_identity':obj({'schema_id':const('PETITION_FOR_INVESTIGATION_CANDIDATE'),'schema_version':const('0.1r'),'artifact_class':const('EPISTEMIC_PETITION_CANDIDATE'),'standing':const('UNADMITTED_CANDIDATE')}),'pfi_identity':obj({'pfi_id':T,'candidate_id':T,'source_chamber':const('JANUSIAN_THINKING_CHAMBER'),'source_method':const('EINSTEIN_SOCRATES')}),'epistemic_membrane':mem,'candidate':obj({'proposition':T}),'constructive_pole':obj({'statement':T,'minimal_model':T,'possible_worlds':arr(world,1),'invariants':arr(inv)}),'destructive_pole':obj({'statement':T,'role':en('RIVAL_CLAIM','LIMITATION','DEFEATER'),'failure_surfaces':arr(fail,1)}),'assumptions':arr(assumption,1),'discrimination_vector':arr(tension,1),'admission_dependencies':arr(dep),'provenance':obj({'source_janusian_object_id':T,'source_digest':H,'source_digest_domain':const('SHA256_EXACT_BYTES')})})
save('pfi_candidate.schema.json',p)
checks=('discrimination','definitions','coverage','source_fidelity','claim_scope','membrane_nonleakage')
pairs=('PASS_FAIL','PASS_ABSTAIN','PASS_INVALID','FAIL_ABSTAIN','FAIL_INVALID','ABSTAIN_INVALID')
finding=obj({'status':en('PASS','FAIL','NOT_EVALUATED'),'reason':T})
review=schema('PFI_EXTERNAL_REVIEW_RECEIPT',{'receipt_type':const('PFI_EXTERNAL_REVIEW_RECEIPT'),'receipt_id':T,'pfi_id':T,'candidate_digest':H,'reviewer_identity':T,'review_artifact_digest':H,'verification_standing':const('DETACHED_VERIFICATION_REQUIRED'),'review_disposition':en('SEMANTICALLY_REVIEWABLE','SEMANTICALLY_UNREVIEWABLE','NOT_EVALUATED'),'authority_delta':const(0),'coordinate_reviews':arr(obj({'tension_id':T,'findings':obj({c:finding for c in checks}),'pairwise_separation':obj({p:finding for p in pairs})}),1)})
save('review_receipt.schema.json',review)
save('authority_separation_receipt.schema.json',schema('AUTHORITY_SEPARATION_RECEIPT',{'receipt_type':const('AUTHORITY_SEPARATION_RECEIPT'),'receipt_id':T,'pfi_id':T,'candidate_digest':H,'reviewer_identity':T,'review_artifact_digest':H,'verification_standing':const('DETACHED_VERIFICATION_REQUIRED'),'scope':const('PFI_EVALUATOR_OUTPUT_ONLY'),'authority_delta':const(0),'admission_granted':const(False),'investigation_authorized':const(False),'execution_requested':const(False)}))
save('dependency_receipt.schema.json',schema('PFI_DEPENDENCY_RECEIPT',{'receipt_type':const('PFI_DEPENDENCY_RECEIPT'),'receipt_id':T,'pfi_id':T,'candidate_digest':H,'reviewer_identity':T,'review_artifact_digest':H,'verification_standing':const('DETACHED_VERIFICATION_REQUIRED'),'dependency_id':T,'disposition':en('SATISFIED','UNRESOLVED'),'authority_delta':const(0)}))
