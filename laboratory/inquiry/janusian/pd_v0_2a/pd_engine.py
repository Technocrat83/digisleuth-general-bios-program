"""PD-v0.2a: bounded exact single-observable predicate algebra. No actuation."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json
import math
import re

VERSION = 'PD-v0.2a'
OUTCOMES = ('SUPPORT', 'FAIL', 'ABSTAIN')
VALIDITY = ('measurement_present', 'unit_valid', 'provenance_valid', 'acquisition_successful')
UNITS = {'SECOND': ('TIME', Q(1)), 'MILLISECOND': ('TIME', Q(1,1000)),
         'MICROSECOND': ('TIME', Q(1,1000000)), 'DIMENSIONLESS': ('SCALAR', Q(1))}
ALIASES = {'<':'LT','<=':'LE','==':'EQ','=':'EQ','!=':'NE','>=':'GE','>':'GT'}
CMP = ('LT','LE','EQ','NE','GE','GT')
LIMITS = {'bytes':1048576,'json_depth':24,'ast_depth':8,'nodes_per_predicate':256,
          'operands':64,'members':256,'digits':256,'intervals':1024}
STAGES = ('parsing','binding','typing','canonicalization','normalization','proof','receipt')
AUTHORITY = {k:'ZERO' for k in ('evidence_delta','truth_delta','admission_delta','execution_authority')}

class Reject(Exception):
    def __init__(self, disposition, reason):
        self.disposition, self.reason = disposition, reason
        super().__init__(reason)

def reject(code, reason): raise Reject(code, reason)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def cjson(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def text(x):
    if type(x) is not str or not x.strip(): reject('PREDICATE_SCHEMA_INVALID','Nonempty text required')
def shape(x, keys):
    if type(x) is not dict or set(x)!=set(keys): reject('PREDICATE_SCHEMA_INVALID','Unexpected or missing fields; expected '+','.join(sorted(keys)))
def digest_text(x):
    if type(x) is not str or re.fullmatch('[a-f0-9]{64}',x) is None: reject('PREDICATE_SCHEMA_INVALID','Expected lowercase SHA256 hex')
def boolean(x):
    if type(x) is not bool: reject('TYPE_MISMATCH','Expected a boolean')
def decimal(x):
    if type(x) is not str: reject('TYPE_MISMATCH','Numeric literal requires exact decimal text')
    if len(x)>LIMITS['digits']+2 or sum(c.isdigit() for c in x)>LIMITS['digits']: reject('RESOURCE_LIMIT_EXCEEDED','Decimal digit limit')
    if re.fullmatch(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?',x) is None: reject('TYPE_MISMATCH','Invalid exact decimal')
    return Q(x)
def load(raw):
    if type(raw) is not bytes: reject('PREDICATE_SCHEMA_INVALID','Input must be exact bytes')
    if len(raw)>LIMITS['bytes']: reject('RESOURCE_LIMIT_EXCEEDED','Input byte limit')
    def pairs(items):
        out={}
        for k,v in items:
            if k in out: reject('PREDICATE_SCHEMA_INVALID','Duplicate JSON key')
            out[k]=v
        return out
    def bad(_): reject('PREDICATE_SCHEMA_INVALID','JSON numbers are not supported; use decimal strings')
    try: value=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_int=bad,parse_float=bad,parse_constant=bad)
    except (UnicodeError,ValueError): reject('PREDICATE_SCHEMA_INVALID','Invalid UTF-8 JSON')
    except RecursionError: reject('RESOURCE_LIMIT_EXCEEDED','JSON nesting limit')
    stack=[(value,0)]
    while stack:
        v,d=stack.pop()
        if d>LIMITS['json_depth']: reject('RESOURCE_LIMIT_EXCEEDED','JSON nesting limit')
        if isinstance(v,dict): stack.extend((x,d+1) for x in v.values())
        elif isinstance(v,list): stack.extend((x,d+1) for x in v)
        elif isinstance(v,str):
            try: v.encode('utf-8')
            except UnicodeError: reject('PREDICATE_SCHEMA_INVALID','Unpaired Unicode surrogate')
    return value

# Intervals: (lower, upper, lower_closed, upper_closed); None denotes infinity.
def empty(i):
    l,h,lc,hc=i
    return l is not None and h is not None and (l>h or (l==h and not(lc and hc)))
def intersection(a,b):
    l,lc=a[0],a[2]
    if l is None or (b[0] is not None and b[0]>l): l,lc=b[0],b[2]
    elif b[0] is not None and b[0]==l: lc=lc and b[2]
    h,hc=a[1],a[3]
    if h is None or (b[1] is not None and b[1]<h): h,hc=b[1],b[3]
    elif b[1] is not None and b[1]==h: hc=hc and b[3]
    i=(l,h,lc if l is not None else False,hc if h is not None else False)
    return None if empty(i) else i

def canon(intervals,integer=False):
    out=[]
    for l,h,lc,hc in intervals:
        if integer:
            if l is not None: l=Q(math.ceil(l) if lc else math.floor(l)+1);lc=True
            if h is not None: h=Q(math.floor(h) if hc else math.ceil(h)-1);hc=True
        i=(l,h,lc if l is not None else False,hc if h is not None else False)
        if not empty(i): out.append(i)
    out.sort(key=lambda i:(i[0] is not None,i[0] or Q(0),not i[2]))
    merged=[]
    for b in out:
        if not merged: merged.append(b);continue
        a=merged[-1]
        joins=(a[1] is None or b[0] is None or b[0]<a[1] or
               (b[0]==a[1] and (a[3] or b[2])) or
               (integer and b[0]<=a[1]+1))
        if not joins: merged.append(b);continue
        h,hc=a[1],a[3]
        if h is not None:
            if b[1] is None or b[1]>h: h,hc=b[1],b[3]
            elif b[1]==h: hc=hc or b[3]
        merged[-1]=(a[0],h,a[2],hc)
    if len(merged)>LIMITS['intervals']: reject('RESOURCE_LIMIT_EXCEEDED','Normalized interval limit')
    return merged

def inter(a,b,integer=False):
    return canon([i for x in a for y in b if (i:=intersection(x,y)) is not None],integer)
def subtract(a,b,integer=False):
    parts=list(a)
    for cut in b:
        rest=[]
        for p in parts:
            hit=intersection(p,cut)
            if hit is None: rest.append(p);continue
            if hit[0] is not None: rest.append((p[0],hit[0],p[2],not hit[2]))
            if hit[1] is not None: rest.append((hit[1],p[1],not hit[3],p[3]))
        parts=canon(rest,integer)
    return parts

def rational(x): return None if x is None else {'numerator':str(x.numerator),'denominator':str(x.denominator)}
def contains_interval(regions,x):
    return any((l is None or x>l or (lc and x==l)) and (h is None or x<h or (hc and x==h)) for l,h,lc,hc in regions)

class Space:
    def __init__(self, observable):
        shape(observable,('observable_id','symbol','domain','unit','nullability','measurement_semantics'))
        for k in ('observable_id','symbol','measurement_semantics'): text(observable[k])
        if observable['nullability'] is not False: reject('INVALID_DOMAIN','Nullability must be false')
        self.obs=observable;d=observable['domain']
        if type(d) is not dict: reject('INVALID_DOMAIN','Domain must be an object')
        self.kind=d.get('type');self.integer=self.kind=='INTEGER';self.numeric=self.kind in ('REAL','INTEGER')
        if self.numeric:
            shape(d,('type','lower','upper'))
            if type(observable['unit']) is not str or observable['unit'] not in UNITS: reject('UNIT_MISMATCH','Unknown numeric observable unit')
            bounds=[]
            for key in ('lower','upper'):
                b=d[key]
                if b is None: bounds.append((None,False));continue
                shape(b,('decimal','inclusive'));boolean(b['inclusive'])
                q=decimal(b['decimal'])
                if self.integer and q.denominator!=1: reject('INVALID_DOMAIN','Fractional INTEGER bound')
                bounds.append((q,b['inclusive']))
            (l,lc),(h,hc)=bounds
            self.domain=canon([(l,h,lc,hc)],self.integer)
            if not self.domain: reject('INVALID_DOMAIN','Empty or reversed domain')
        elif self.kind in ('BOOLEAN','FINITE_ENUM'):
            if observable['unit']!='NOT_APPLICABLE': reject('UNIT_MISMATCH','Finite domain requires NOT_APPLICABLE')
            if self.kind=='BOOLEAN': shape(d,('type',));self.domain=frozenset((False,True))
            else:
                shape(d,('type','members'));m=d['members']
                if type(m) is not list or not m: reject('INVALID_DOMAIN','Nonempty enum domain required')
                if len(m)>LIMITS['members']: reject('RESOURCE_LIMIT_EXCEEDED','Enum member limit')
                for x in m: text(x)
                if len(set(m))!=len(m): reject('INVALID_DOMAIN','Duplicate enum members')
                self.domain=frozenset(m)
        else: reject('INVALID_DOMAIN','Unsupported domain type')
    def literal(self, lit):
        if self.numeric:
            shape(lit,('decimal','unit'));q=decimal(lit['decimal']);u=lit['unit']
            if type(u) is not str or u not in UNITS: reject('UNIT_MISMATCH','Unknown literal unit')
            a,b=UNITS[u],UNITS[self.obs['unit']]
            if a[0]!=b[0]: reject('UNIT_MISMATCH','Incompatible dimensions')
            return q*a[1]/b[1]
        if self.kind=='BOOLEAN':
            shape(lit,('boolean',));boolean(lit['boolean']);return lit['boolean']
        shape(lit,('member',));x=lit['member'];text(x)
        if x not in self.domain: reject('TYPE_MISMATCH','Unknown enum member')
        return x
    def blank(self): return [] if self.numeric else frozenset()
    def union(self,a,b): return canon(a+b,self.integer) if self.numeric else a|b
    def intersect(self,a,b): return inter(a,b,self.integer) if self.numeric else a&b
    def minus(self,a,b): return subtract(a,b,self.integer) if self.numeric else a-b
    def has(self,a,x): return contains_interval(a,x) if self.numeric else x in a
    def serialize(self,a):
        if not self.numeric: return {'form':'FINITE_SET_V0_2A','members':sorted(a)}
        return {'form':'INTEGER_INTERVAL_SET_V0_2A' if self.integer else 'REAL_INTERVAL_SET_V0_2A',
                'unit':self.obs['unit'],'intervals':[{'lower':rational(l),'upper':rational(h),'lower_closed':lc,'upper_closed':hc} for l,h,lc,hc in a]}
    def witness(self,a):
        if not a: return None
        if not self.numeric: return sorted(a)[0]
        l,h,lc,hc=a[0]
        if l is not None:
            if lc: x=l
            elif h is not None: x=(l+h)/2
            else: x=l+1
        elif h is not None: x=h if hc else h-1
        else: x=Q(0)
        if not self.has(a,x): reject('EVALUATOR_INVARIANT_FAILURE','Invalid witness')
        return rational(x)
    def normalize(self,node):
        op=node['op']
        if op=='EMPTY': return self.blank()
        if op=='NOT': return self.minus(self.domain,self.normalize(node['operand']))
        if op in ('AND','OR'):
            value=self.domain if op=='AND' else self.blank()
            for x in node['operands']:
                value=(self.intersect if op=='AND' else self.union)(value,self.normalize(x))
            return value
        if op=='IN':
            value=self.blank()
            for x in node['values']: value=self.union(value,self.atom('EQ',x))
            return value
        return self.atom(op,node['value'])
    def atom(self,op,x):
        if not self.numeric:
            return frozenset((x,)) if op=='EQ' else self.domain-frozenset((x,))
        shapes={'LT':[(None,x,False,False)],'LE':[(None,x,False,True)],
                'GT':[(x,None,False,False)],'GE':[(x,None,True,False)],
                'EQ':[(x,x,True,True)],'NE':[(None,x,False,False),(x,None,False,False)]}
        return self.intersect(canon(shapes[op],self.integer),self.domain)

def parse_node(node,budget,depth=0):
    budget[0]+=1
    if depth>LIMITS['ast_depth'] or budget[0]>LIMITS['nodes_per_predicate']: reject('RESOURCE_LIMIT_EXCEEDED','AST depth/node limit')
    if type(node) is not dict: reject('PREDICATE_SCHEMA_INVALID','AST node must be object')
    if 'observation_validity' in node or 'sensor_failure' in node: reject('LAYER_VIOLATION','Observation-validity field in scientific AST')
    op=node.get('op')
    if type(op) is not str: reject('PREDICATE_SCHEMA_INVALID','Operator must be text')
    op=ALIASES.get(op,op)
    if op in ('AND','OR'):
        shape(node,('op','operands'));items=node['operands']
        if type(items) is not list or len(items)<2: reject('PREDICATE_SCHEMA_INVALID','AND/OR require at least two operands')
        if len(items)>LIMITS['operands']: reject('RESOURCE_LIMIT_EXCEEDED','Operand limit')
        return {'op':op,'operands':[parse_node(x,budget,depth+1) for x in items]}
    if op=='NOT':
        shape(node,('op','operand'));return {'op':op,'operand':parse_node(node['operand'],budget,depth+1)}
    if op=='EMPTY': shape(node,('op','observable_ref'))
    elif op=='IN':
        shape(node,('op','observable_ref','literals'))
        if type(node['literals']) is not list: reject('PREDICATE_SCHEMA_INVALID','IN needs literal list')
        if len(node['literals'])>LIMITS['members']: reject('RESOURCE_LIMIT_EXCEEDED','IN member limit')
    elif op in CMP: shape(node,('op','observable_ref','literal'))
    else: reject('UNSUPPORTED_FRAGMENT','Unsupported operator: '+op)
    text(node['observable_ref']);return dict(node,op=op)

def leaves(node):
    if node['op'] in ('AND','OR'):
        for n in node['operands']: yield from leaves(n)
    elif node['op']=='NOT': yield from leaves(node['operand'])
    else: yield node

def bind(nodes,observable):
    for node in nodes.values():
        for atom in leaves(node):
            if atom['observable_ref'] in VALIDITY: reject('LAYER_VIOLATION','Apparatus validity referenced as scientific observable')
            if atom['observable_ref']!=observable['observable_id']: reject('UNKNOWN_OBSERVABLE','Unknown observable reference')

def typed(nodes,space):
    for node in nodes.values():
        for atom in leaves(node):
            if atom['op']=='EMPTY':continue
            if not space.numeric and atom['op'] not in ('EQ','NE','IN'): reject('TYPE_MISMATCH','Ordered comparison on finite domain')
            lits=atom['literals'] if atom['op']=='IN' else [atom['literal']]
            for lit in lits:
                if type(lit) is not dict: reject('TYPE_MISMATCH','Typed literal object required')
                expected={'decimal','unit'} if space.numeric else {'boolean'} if space.kind=='BOOLEAN' else {'member'}
                if set(lit)!=expected: reject('TYPE_MISMATCH','Literal type does not match observable')
                # Check type now; unit conversion happens only in canonicalization.
                if space.numeric: decimal(lit['decimal'])
                elif space.kind=='BOOLEAN': boolean(lit['boolean'])
                else:
                    text(lit['member'])
                    if lit['member'] not in space.domain: reject('TYPE_MISMATCH','Unknown enum member')

def canonicalize(node,space):
    op=node['op']
    if op in ('AND','OR'):return {'op':op,'operands':[canonicalize(n,space) for n in node['operands']]}
    if op=='NOT':return {'op':op,'operand':canonicalize(node['operand'],space)}
    if op=='EMPTY':return {'op':op}
    if op=='IN':return {'op':op,'values':[space.literal(x) for x in node['literals']]}
    return {'op':op,'value':space.literal(node['literal'])}

def header(c):
    if type(c) is not dict: reject('PREDICATE_SCHEMA_INVALID','Contract must be an object')
    if 'residual_policy' not in c: reject('RESIDUAL_POLICY_MISSING','Explicit residual policy required')
    shape(c,('schema_version','binding','observable','observation_validity','predicates','residual_policy'))
    if c['schema_version']!=VERSION: reject('PREDICATE_SCHEMA_INVALID','Unsupported schema version')
    shape(c['binding'],('source_pfi_id','source_pfi_digest','discrimination_vector_id','tension_id'))
    for k,v in c['binding'].items(): digest_text(v) if k=='source_pfi_digest' else text(v)
    shape(c['observation_validity'],('required','failure_disposition'))
    if c['observation_validity']!={'required':list(VALIDITY),'failure_disposition':'INVALID'}: reject('LAYER_VIOLATION','Validity contract changed')
    p=c['predicates']
    if type(p) is dict and 'INVALID' in p: reject('LAYER_VIOLATION','INVALID is outside scientific geometry')
    shape(p,OUTCOMES)
    for v in p.values():shape(v,('ast','require_nonempty'));boolean(v['require_nonempty'])
    if c['residual_policy'] not in ('REJECT_PREDICATE_FAMILY','ROUTE_TO_ABSTAIN'): reject('PREDICATE_SCHEMA_INVALID','Unsupported residual policy')
    return {o:parse_node(p[o]['ast'],[0]) for o in OUTCOMES}

def _solve(raw):
    stages={s:'NOT_EVALUATED' for s in STAGES};active='parsing'
    result={'engine_version':VERSION,'predicate_contract_digest':sha(raw) if type(raw) is bytes else None,
            'stages':stages,'authority':AUTHORITY.copy(),'authentication_status':'UNSIGNED_UNAUTHENTICATED'}
    try:
        c=load(raw);nodes=header(c);stages['parsing']='PASS'
        active='binding'
        if type(c['observable']) is not dict or 'observable_id' not in c['observable']:reject('PREDICATE_SCHEMA_INVALID','Observable identity missing')
        bind(nodes,c['observable']);stages['binding']='PASS'
        active='typing';space=Space(c['observable']);typed(nodes,space);stages['typing']='PASS'
        active='canonicalization';canonical={o:canonicalize(n,space) for o,n in nodes.items()};stages['canonicalization']='PASS'
        active='normalization';regions={o:space.normalize(n) for o,n in canonical.items()}
        for v in regions.values():
            if space.minus(v,space.domain):reject('EVALUATOR_INVARIANT_FAILURE','Region exceeds domain')
        stages['normalization']='PASS'
        result['binding']=c['binding'];result['observable_id']=c['observable']['observable_id']
        result['normalized_domain']=space.serialize(space.domain)
        result['normalized_domain_digest']=sha(cjson(result['normalized_domain']))
        result['authored_regions']={o:space.serialize(v) for o,v in regions.items()}
        result['normalized_geometry_digest']=sha(cjson(result['authored_regions']))
        result['satisfiability']={o:('SATISFIABLE' if regions[o] else 'EMPTY_ALLOWED' if not c['predicates'][o]['require_nonempty'] else 'EMPTY_FORBIDDEN') for o in OUTCOMES}
        active='proof'
        if 'EMPTY_FORBIDDEN' in result['satisfiability'].values():reject('PREDICATE_UNSATISFIABLE','Required outcome has empty region')
        pairs=[]
        for a,b in combinations(OUTCOMES,2):
            overlap=space.intersect(regions[a],regions[b])
            pairs.append({'left':a,'right':b,'disposition':'OVERLAP_FOUND' if overlap else 'PAIRWISE_DISJOINT',
                          'intersection':space.serialize(overlap),'witness':space.witness(overlap)})
        result['pairwise_checks']=pairs
        result['invalid_type_separation']=[{'left':o,'right':'INVALID','basis':'TAGGED_OBSERVATION_VALIDITY','result':'DISJOINT_BY_TYPE'} for o in OUTCOMES]
        if any(p['disposition']=='OVERLAP_FOUND' for p in pairs):reject('OVERLAP_FOUND','Scientific outcome regions overlap')
        covered=space.blank()
        for v in regions.values():covered=space.union(covered,v)
        residual=space.minus(space.domain,covered)
        result['authored_coverage']='DOMAIN_GAP' if residual else 'DOMAIN_COMPLETE'
        result['residual']=space.serialize(residual);result['residual_witness']=space.witness(residual)
        if residual and c['residual_policy']=='REJECT_PREDICATE_FAMILY':reject('DOMAIN_GAP','Authored predicates leave uncovered values')
        effective=dict(regions)
        if residual:effective['ABSTAIN']=space.union(effective['ABSTAIN'],residual)
        final=space.blank()
        for v in effective.values():final=space.union(final,v)
        if space.minus(space.domain,final) or any(space.intersect(effective[a],effective[b]) for a,b in combinations(OUTCOMES,2)):
            reject('EVALUATOR_INVARIANT_FAILURE','Effective partition recheck failed')
        stages['proof']='PASS';active='receipt'
        result.update(disposition='PARTITION_PROVEN',effective_regions={o:space.serialize(v) for o,v in effective.items()},
                      effective_coverage='DOMAIN_COMPLETE',residual_routing='ROUTED_TO_ABSTAIN' if residual else 'NOT_NEEDED',
                      receipt_version='PD_PROOF_RECEIPT_v0.2a',engine_digest=sha(Path(__file__).read_bytes()),
                      profiles={'arithmetic':'EXACT_RATIONAL_V0_1','units':'PD_UNIT_TABLE_V0_1','serialization':'PD-CJSON-1'},
                      limits=LIMITS.copy(),source_binding_status='DECLARED_NOT_AUTHENTICATED')
        stages['receipt']='PASS'
        return result,(space,effective)
    except Reject as e:
        stages[active]='FAIL';result.update(disposition=e.disposition,reason=e.reason);return result,None
    except (RecursionError,MemoryError):
        stages[active]='FAIL';result.update(disposition='RESOURCE_LIMIT_EXCEEDED',reason='Host resource limit');return result,None

def solve(raw):return _solve(raw)[0]
def classify(contract_bytes,observation_bytes):
    proof,state=_solve(contract_bytes)
    if state is None:return {'disposition':'CONTRACT_REJECTED','contract_disposition':proof['disposition'],'authority':AUTHORITY.copy()}
    space,regions=state
    try:
        obs=load(observation_bytes);shape(obs,('validity','value'));shape(obs['validity'],VALIDITY)
        if any(obs['validity'][k]!='PASS' for k in VALIDITY):reject('INVALID','Observation validity not established')
        v=space.literal(obs['value'])
        if space.integer and v.denominator!=1:reject('INVALID','Noninteger measurement')
        if not space.has(space.domain,v):reject('INVALID','Measurement outside declared domain')
        matches=[o for o in OUTCOMES if space.has(regions[o],v)]
        if len(matches)!=1:reject('EVALUATOR_INVARIANT_FAILURE','Not exactly one scientific outcome')
        return {'disposition':matches[0],'authority':AUTHORITY.copy(),'predicate_contract_digest':sha(contract_bytes)}
    except Reject as e:
        return {'disposition':'EVALUATOR_INVARIANT_FAILURE' if e.disposition=='EVALUATOR_INVARIANT_FAILURE' else 'INVALID',
                'reason':e.reason,'authority':AUTHORITY.copy()}

def parse_comparison(source,observable):
    """Optional bounded text convenience for one numeric atom; no prose parser."""
    if type(source) is not str or len(source)>1024:reject('UNSUPPORTED_FRAGMENT','Comparison text limit')
    m=re.fullmatch(r'([A-Za-z_][A-Za-z_0-9]*)\s*(<=|>=|!=|==|=|<|>)\s*(-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?)\s+([A-Z_]+)',source.strip())
    if not m:reject('UNSUPPORTED_FRAGMENT','Only one numeric comparison accepted as text')
    symbol,op,value,unit=m.groups()
    if symbol!=observable['symbol']:reject('UNKNOWN_OBSERVABLE','Unknown symbol')
    decimal(value)
    return {'op':ALIASES[op],'observable_ref':observable['observable_id'],'literal':{'decimal':value,'unit':unit}}

if __name__=='__main__':
    import argparse,sys
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('contract');p.add_argument('--observation')
    args=p.parse_args();raw=Path(args.contract).read_bytes()
    result=classify(raw,Path(args.observation).read_bytes()) if args.observation else solve(raw)
    sys.stdout.buffer.write(cjson(result))
    sys.exit(0 if result['disposition']=='PARTITION_PROVEN' or result['disposition'] in OUTCOMES else 2)
