import copy,itertools,json,subprocess,sys,tempfile,unittest
from fractions import Fraction as Q
from pathlib import Path
import pd_engine as E
ROOT=Path(__file__).parent
SOURCE=E.cjson({'source_class':'SYNTHETIC_PFI_BINDING','purpose':'Geometry fixtures; not PFI_READY.'})
def atom(op,x,u='DIMENSIONLESS'):return {'op':op,'observable_ref':'OBS_X','literal':{'decimal':str(x),'unit':u}}
def empty():return {'op':'EMPTY','observable_ref':'OBS_X'}
def logic(op,*xs):return {'op':op,'operand':xs[0]} if op=='NOT' else {'op':op,'operands':list(xs)}
def base():
 return {'schema_version':E.VERSION,'binding':{'source_pfi_id':'SYNTHETIC_PFI_PD','source_pfi_digest':E.sha(SOURCE),'discrimination_vector_id':'DV-001','tension_id':'T-001'},'observable':{'observable_id':'OBS_X','symbol':'x','domain':{'type':'REAL','lower':{'decimal':'0','inclusive':True},'upper':None},'unit':'DIMENSIONLESS','nullability':False,'measurement_semantics':'Synthetic scalar, no empirical claim.'},'observation_validity':{'required':list(E.VALIDITY),'failure_disposition':'INVALID'},'predicates':{o:{'ast':a,'require_nonempty':o!='ABSTAIN'} for o,a in zip(E.OUTCOMES,[atom('LT',5),logic('AND',atom('GE',5),atom('LT',10)),atom('GE',10)])},'residual_policy':'REJECT_PREDICATE_FAMILY'}
def family(c,s,f,a=None):
 c=copy.deepcopy(c)
 for o,n in zip(E.OUTCOMES,[s,f,a if a is not None else empty()]):c['predicates'][o]['ast']=n
 return c
def fixtures():
 b=base();fs={}
 def put(k,c,w):fs[k]=(c,w)
 put('PD01_INTERVAL_PARTITION',b,'PARTITION_PROVEN')
 put('PD02_ENDPOINT_COLLISION',family(b,atom('LE',5),atom('GE',5)),'OVERLAP_FOUND')
 gap=family(b,atom('LT',5),atom('GT',5));put('PD03_SINGLETON_GAP',gap,'DOMAIN_GAP')
 t=copy.deepcopy(b);t['observable']['unit']='MILLISECOND'
 put('PD04_UNIT_ALIAS',family(t,atom('GT','0.05','SECOND'),atom('GT',50,'MILLISECOND'),atom('LE',50,'MILLISECOND')),'OVERLAP_FOUND')
 f=copy.deepcopy(b);f['observable']['domain']={'type':'FINITE_ENUM','members':['OK','DEGRADED','DOWN']};f['observable']['unit']='NOT_APPLICABLE'
 def enum(*m):return {'op':'IN','observable_ref':'OBS_X','literals':[{'member':x} for x in m]}
 put('PD05_ENUM_OVERLAP',family(f,enum('OK','DEGRADED'),enum('DEGRADED','DOWN')),'OVERLAP_FOUND')
 put('PD06_UNSATISFIABLE',family(b,logic('AND',atom('GT',10),atom('LT',5)),atom('GE',5)),'PREDICATE_UNSATISFIABLE')
 put('PD07_UNSUPPORTED_OPERATOR',family(b,{'op':'PARITY','observable_ref':'OBS_X'},atom('GE',5)),'UNSUPPORTED_FRAGMENT')
 c=copy.deepcopy(b);c['predicates']['INVALID']={'ast':empty(),'require_nonempty':False};put('PD08_INVALID_LAYER_LEAK',c,'LAYER_VIOLATION')
 c=copy.deepcopy(gap);c['residual_policy']='ROUTE_TO_ABSTAIN';put('PD09_RESIDUAL_ROUTING',c,'PARTITION_PROVEN')
 put('PD10_SERIALIZATION_VARIANCE',family(b,logic('NOT',atom('GE',5)),logic('AND',atom('LT',10),atom('GE',5)),atom('>=',10)),'PARTITION_PROVEN')
 c=copy.deepcopy(b);c['observable']['domain']={'type':'BOOLEAN'};c['observable']['unit']='NOT_APPLICABLE'
 a={'op':'EQ','observable_ref':'OBS_X','literal':{'boolean':True}}
 put('PD11_BOOLEAN_PARTITION',family(c,a,logic('NOT',a)),'PARTITION_PROVEN')
 c=copy.deepcopy(b);c['observable']['domain']['type']='INTEGER'
 put('PD12_INTEGER_FRACTION_BOUNDARY',family(c,atom('LT','0.5'),logic('AND',atom('GE','0.5'),atom('LT',2)),atom('GE',2)),'PARTITION_PROVEN')
 put('PD13_ENUM_PARTITION',family(f,enum('OK'),enum('DOWN'),enum('DEGRADED')),'PARTITION_PROVEN')
 c=copy.deepcopy(b);del c['residual_policy'];put('PD14_MISSING_POLICY',c,'RESIDUAL_POLICY_MISSING')
 c=copy.deepcopy(b);c['observable']['domain']['upper']={'decimal':'-1','inclusive':True};put('PD15_INVALID_DOMAIN',c,'INVALID_DOMAIN')
 c=copy.deepcopy(b);c['predicates']['SUPPORT']['ast']['observable_ref']='OTHER';put('PD16_UNKNOWN_OBSERVABLE',c,'UNKNOWN_OBSERVABLE')
 put('PD17_UNIT_MISMATCH',family(b,atom('LT',5,'SECOND'),atom('GE',5)),'UNIT_MISMATCH')
 c=copy.deepcopy(b);c['predicates']['SUPPORT']['ast']['literal']={'member':'slow'};put('PD18_TYPE_MISMATCH',c,'TYPE_MISMATCH')
 c=copy.deepcopy(b);c['predicates']['SUPPORT']['ast']=logic('OR',*[atom('LT',5) for _ in range(65)]);put('PD19_RESOURCE_LIMIT',c,'RESOURCE_LIMIT_EXCEEDED')
 return fs
class Battery(unittest.TestCase):
 def test_named_fixtures(self):
  for name,(c,w) in fixtures().items():
   with self.subTest(name=name):
    r=E.solve(E.cjson(c));self.assertEqual(r['disposition'],w,r);self.assertTrue(all(x=='ZERO' for x in r['authority'].values()))
    if w=='PARTITION_PROVEN':
     self.assertEqual(r['effective_coverage'],'DOMAIN_COMPLETE');self.assertTrue(all(p['disposition']=='PAIRWISE_DISJOINT' for p in r['pairwise_checks']))
 def test_witnesses(self):
  fs=fixtures();r=E.solve(E.cjson(fs['PD02_ENDPOINT_COLLISION'][0]));self.assertEqual(r['pairwise_checks'][0]['witness'],{'numerator':'5','denominator':'1'})
  r=E.solve(E.cjson(fs['PD03_SINGLETON_GAP'][0]));self.assertEqual(r['residual']['intervals'],[{'lower':{'numerator':'5','denominator':'1'},'upper':{'numerator':'5','denominator':'1'},'lower_closed':True,'upper_closed':True}])
 def test_unit_alias(self):
  r=E.solve(E.cjson(fixtures()['PD04_UNIT_ALIAS'][0]));self.assertEqual(r['authored_regions']['SUPPORT'],r['authored_regions']['FAIL']);self.assertEqual(r['authored_regions']['SUPPORT']['intervals'][0]['lower'],{'numerator':'50','denominator':'1'})
 def test_variance(self):
  fs=fixtures();a=E.solve(E.cjson(base()));b=E.solve(E.cjson(fs['PD10_SERIALIZATION_VARIANCE'][0]));self.assertEqual(a['normalized_geometry_digest'],b['normalized_geometry_digest']);self.assertNotEqual(a['predicate_contract_digest'],b['predicate_contract_digest'])
  c=E.solve(json.dumps(base(),indent=2).encode());self.assertEqual(a['normalized_geometry_digest'],c['normalized_geometry_digest']);self.assertNotEqual(a['predicate_contract_digest'],c['predicate_contract_digest'])
 def test_receipt_repeatability(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'input.json';raw=E.cjson(base());p.write_bytes(raw)
   a=subprocess.check_output([sys.executable,str(ROOT/'pd_engine.py'),str(p)]);b=subprocess.check_output([sys.executable,str(ROOT/'pd_engine.py'),str(p)])
   self.assertEqual(a,b);self.assertEqual(a,E.cjson(E.solve(raw)))
 def test_observations(self):
  raw=E.cjson(fixtures()['PD09_RESIDUAL_ROUTING'][0]);obs={'validity':{k:'PASS' for k in E.VALIDITY},'value':{'decimal':'5','unit':'DIMENSIONLESS'}}
  self.assertEqual(E.classify(raw,E.cjson(obs))['disposition'],'ABSTAIN')
  for key in E.VALIDITY:
   x=copy.deepcopy(obs);x['validity'][key]='NOT_ESTABLISHED';self.assertEqual(E.classify(raw,E.cjson(x))['disposition'],'INVALID')
  for v in ({'decimal':'-1','unit':'DIMENSIONLESS'},{'boolean':True},{'decimal':'NaN','unit':'DIMENSIONLESS'}):
   x=copy.deepcopy(obs);x['value']=v;self.assertEqual(E.classify(raw,E.cjson(x))['disposition'],'INVALID')
  self.assertEqual(E.classify(E.cjson(fixtures()['PD02_ENDPOINT_COLLISION'][0]),E.cjson(obs))['disposition'],'CONTRACT_REJECTED')
 def test_malformed(self):
  for raw in (b'{',b'{"a":true,"a":false}',b'{"n":NaN}',b'{"n":1}',b'"\\ud800"'):
   self.assertEqual(E.solve(raw)['disposition'],'PREDICATE_SCHEMA_INVALID')
 def test_policy_layer_and_empty(self):
  c=base();c['predicates']['SUPPORT']['ast']['observable_ref']='acquisition_successful';self.assertEqual(E.solve(E.cjson(c))['disposition'],'LAYER_VIOLATION')
  c=base();c['predicates']['SUPPORT']['ast']=empty();self.assertEqual(E.solve(E.cjson(c))['disposition'],'PREDICATE_UNSATISFIABLE')
  c=base();c['residual_policy']='ROUTE_TO_INVALID';self.assertEqual(E.solve(E.cjson(c))['disposition'],'PREDICATE_SCHEMA_INVALID')
 def test_text_parser(self):
  ob=base()['observable'];ob['symbol']='latency';self.assertEqual(E.parse_comparison('latency >= 0.05 SECOND',ob),atom('GE','0.05','SECOND'))
  for s in ('latency is slow','latency % 2 == 1','__import__(os)','latency > 5 DIMENSIONLESS OR latency < 0 DIMENSIONLESS'):
   with self.assertRaises(E.Reject):E.parse_comparison(s,ob)
 def test_nonconvex(self):
  c=base();c['observable']['domain']['lower']=None;c=family(c,atom('NE',0),atom('EQ',0));r=E.solve(E.cjson(c));self.assertEqual(r['disposition'],'PARTITION_PROVEN');self.assertEqual(len(r['authored_regions']['SUPPORT']['intervals']),2)
 def test_integer_rounding(self):
  c=base();c['observable']['domain']={'type':'INTEGER','lower':None,'upper':None};c=family(c,atom('LT','-0.5'),atom('GE','-0.5'));r=E.solve(E.cjson(c));self.assertEqual(r['disposition'],'PARTITION_PROVEN');self.assertEqual(r['authored_regions']['SUPPORT']['intervals'][0]['upper'],{'numerator':'-1','denominator':'1'});self.assertEqual(r['authored_regions']['FAIL']['intervals'][0]['lower'],{'numerator':'0','denominator':'1'})
 def test_finite_complement(self):
  c=fixtures()['PD13_ENUM_PARTITION'][0];a=c['predicates']['SUPPORT']['ast'];c=family(c,a,logic('NOT',a));self.assertEqual(E.solve(E.cjson(c))['disposition'],'PARTITION_PROVEN')
 def test_resource_guards(self):
  c=base();a=atom('LT',5)
  for _ in range(10):a=logic('NOT',a)
  c['predicates']['SUPPORT']['ast']=a;self.assertEqual(E.solve(E.cjson(c))['disposition'],'RESOURCE_LIMIT_EXCEEDED')
  c=base();c['predicates']['SUPPORT']['ast']['literal']['decimal']='1'*257;self.assertEqual(E.solve(E.cjson(c))['disposition'],'RESOURCE_LIMIT_EXCEEDED')
 def test_interval_algebra_independent_oracle(self):
  endpoints=[None,Q(-1),Q(0),Q(1)];intervals=list(itertools.product(endpoints,endpoints,(False,True),(False,True)))
  probes=[Q(n,2) for n in range(-6,7)]
  def member(i,x):
   l,h,lc,hc=i
   return (l is None or x>l or (lc and x==l)) and (h is None or x<h or (hc and x==h))
  for integer in (False,True):
   xs=[x for x in probes if not integer or x.denominator==1]
   for a,b in itertools.product(intervals,repeat=2):
    ca,cb=E.canon([a],integer),E.canon([b],integer);u=E.canon(ca+cb,integer);i=E.inter(ca,cb,integer);d=E.subtract(ca,cb,integer)
    for x in xs:
     aa,bb=member(a,x),member(b,x);self.assertEqual(E.contains_interval(u,x),aa or bb);self.assertEqual(E.contains_interval(i,x),aa and bb);self.assertEqual(E.contains_interval(d,x),aa and not bb)
 def test_all_numeric_atoms_against_direct_oracle(self):
  c=base();c['observable']['domain']['lower']=None;space=E.Space(c['observable'])
  predicates={'LT':lambda x,y:x<y,'LE':lambda x,y:x<=y,'EQ':lambda x,y:x==y,'NE':lambda x,y:x!=y,'GE':lambda x,y:x>=y,'GT':lambda x,y:x>y}
  for integer in (False,True):
   c['observable']['domain']['type']='INTEGER' if integer else 'REAL';space=E.Space(c['observable'])
   for op,threshold in itertools.product(predicates,['-1.5','-1','0','0.5','2']):
    a=atom(op,threshold);nodes={'SUPPORT':E.parse_node(a,[0])};E.bind(nodes,c['observable']);E.typed(nodes,space);normal=space.normalize(E.canonicalize(nodes['SUPPORT'],space))
    for x in [Q(n,2) for n in range(-6,7) if not integer or n%2==0]:self.assertEqual(space.has(normal,x),predicates[op](x,Q(threshold)))
 def test_membership_and_boolean_ne(self):
  c=base();c['observable']['domain']['lower']=None
  a={'op':'IN','observable_ref':'OBS_X','literals':[{'decimal':'0','unit':'DIMENSIONLESS'},{'decimal':'2','unit':'DIMENSIONLESS'}]}
  self.assertEqual(E.solve(E.cjson(family(c,a,logic('NOT',a))))['disposition'],'PARTITION_PROVEN')
  c=fixtures()['PD11_BOOLEAN_PARTITION'][0];a={'op':'NE','observable_ref':'OBS_X','literal':{'boolean':False}};c=family(c,a,logic('NOT',a));self.assertEqual(E.solve(E.cjson(c))['disposition'],'PARTITION_PROVEN')
def materialize():
 inputs=ROOT/'fixtures';outputs=ROOT/'receipts';inputs.mkdir(exist_ok=True);outputs.mkdir(exist_ok=True);(inputs/'synthetic_source_pfi.json').write_bytes(SOURCE);cases=[]
 for name,(c,want) in fixtures().items():
  raw=E.cjson(c);(inputs/(name+'.json')).write_bytes(raw);receipt=E.cjson(E.solve(raw));(outputs/(name+'.json')).write_bytes(receipt);actual=json.loads(receipt)['disposition'];cases.append({'id':name,'expected':want,'actual':actual,'matched':actual==want,'contract_digest':E.sha(raw),'receipt_digest':E.sha(receipt)})
 return cases
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Battery))
 if r.wasSuccessful():
  cases=materialize();(ROOT/'test_results.json').write_bytes(E.cjson({'engine_version':E.VERSION,'standing':'EXECUTABLE_REFERENCE_PROTOTYPE','unit_tests':r.testsRun,'unit_tests_passed':r.testsRun,'named_contract_fixtures':len(cases),'fixture_expectations_matched':sum(c['matched'] for c in cases),'cases':cases,'authority':E.AUTHORITY,'real_investigations':0,'authentication_implemented':False,'governance_implemented':False}))
 sys.exit(0 if r.wasSuccessful() else 1)
