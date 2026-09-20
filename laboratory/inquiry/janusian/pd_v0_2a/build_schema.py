"""Generate the structural contract schema; runtime adds depth/type/unit gates."""
import json
from pathlib import Path
T={'type':'string','minLength':1,'pattern':r'\S'}
DEC={'type':'string','pattern':r'^-?(0|[1-9][0-9]*)(\.[0-9]+)?$','maxLength':258}
H={'type':'string','pattern':'^[a-f0-9]{64}$'}
def obj(p):return {'type':'object','additionalProperties':False,'required':list(p),'properties':p}
def con(v):return {'const':v}
def enum(*xs):return {'enum':list(xs)}
def arr(x,n=0,maximum=256):return {'type':'array','items':x,'minItems':n,'maxItems':maximum}
ref={'$ref':'#/$defs/ast'}
lit={'oneOf':[obj({'decimal':DEC,'unit':enum('SECOND','MILLISECOND','MICROSECOND','DIMENSIONLESS')}),obj({'boolean':{'type':'boolean'}}),obj({'member':T})]}
ast={'oneOf':[obj({'op':enum('LT','LE','EQ','NE','GE','GT','<','<=','=','==','!=','>=','>'),'observable_ref':T,'literal':lit}),obj({'op':con('IN'),'observable_ref':T,'literals':arr(lit)}),obj({'op':enum('AND','OR'),'operands':arr(ref,2,64)}),obj({'op':con('NOT'),'operand':ref}),obj({'op':con('EMPTY'),'observable_ref':T})]}
bound={'oneOf':[{'type':'null'},obj({'decimal':DEC,'inclusive':{'type':'boolean'}})]}
domain={'oneOf':[obj({'type':enum('INTEGER','REAL'),'lower':bound,'upper':bound}),obj({'type':con('BOOLEAN')}),obj({'type':con('FINITE_ENUM'),'members':dict(arr(T,1),uniqueItems=True)})]}
s=obj({'schema_version':con('PD-v0.2a'),'binding':obj({'source_pfi_id':T,'source_pfi_digest':H,'discrimination_vector_id':T,'tension_id':T}),
'observable':obj({'observable_id':T,'symbol':T,'domain':domain,'unit':enum('SECOND','MILLISECOND','MICROSECOND','DIMENSIONLESS','NOT_APPLICABLE'),'nullability':con(False),'measurement_semantics':T}),
'observation_validity':obj({'required':con(['measurement_present','unit_valid','provenance_valid','acquisition_successful']),'failure_disposition':con('INVALID')}),
'predicates':obj({o:obj({'ast':ref,'require_nonempty':{'type':'boolean'}}) for o in ('SUPPORT','FAIL','ABSTAIN')}),
'residual_policy':enum('ROUTE_TO_ABSTAIN','REJECT_PREDICATE_FAMILY')})
s.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:digisleuth:pd-contract:0.2a','title':'PD-v0.2a structural contract','$defs':{'ast':ast},'$comment':'Structural shape only. Host enforces byte/depth/node/digit limits, domain/type/unit and layer constraints. No proof follows from JSON Schema conformance.'})
Path(__file__).with_name('pd_contract.schema.json').write_text(json.dumps(s,indent=2)+'\n')
