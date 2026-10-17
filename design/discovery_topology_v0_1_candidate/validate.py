import json, pathlib, re, hashlib
R=pathlib.Path(__file__).parent
g=json.loads((R/'topology.json').read_text()); c=json.loads((R/'review_vault/DISCOVERY_TOPOLOGY.canvas').read_text()); f=json.loads((R/'figma_handoff.json').read_text())
checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
ids=[n['id'] for n in g['nodes']]; eids=[e['id'] for e in g['relationships']]
check('Unique semantic and relationship IDs',len(set(ids+eids))==len(ids+eids))
check('Typed edges resolve and retain proposed standing',all(e['subject'] in ids and e['object'] in ids and e['standing']=='PROPOSED' and e['authority']=='NONE' and all(k in e for k in ['scope','evidence','certainty','version']) for e in g['relationships']))
ci=[x['id'] for x in c['nodes']+c['edges']]
check('Canvas IDs unique and 16 lowercase hex',len(set(ci))==len(ci) and all(re.fullmatch('[a-f0-9]{16}',x) for x in ci))
cn={n['id'] for n in c['nodes']}
check('Canvas edge endpoints and labels',all(e['fromNode'] in cn and e['toNode'] in cn and e['label'].startswith('PROPOSED ') for e in c['edges']))
check('Canvas required fields and file references',all(all(k in n for k in ['id','type','x','y','width','height']) and n['type'] in ['group','file'] and (n['type']!='file' or (R/'review_vault'/n['file']).is_file()) for n in c['nodes']))
check('Figma mapping preserves all source IDs and edge predicates',set(n['source_object_id'] for n in f['nodes'])==set(ids) and {(e['source_relation_id'],e['from'],e['predicate'],e['to']) for e in f['connectors']}=={(e['id'],e['subject'],e['relation'],e['object']) for e in g['relationships']})
check('Graph digest matches handoff',hashlib.sha256((R/'topology.json').read_bytes()).hexdigest()==f['source_graph_sha256'])
check('No fabricated observations or promotions',g['observed_events']==[] and g['measured_basins']==[] and not g['promotion_authority'] and f['attention_metric'] is None)
for n in g['nodes']:
 t=(R/'review_vault/notes'/ (n['key']+'.md')).read_text(); front=json.loads(t.split('---')[1])
 check('Note records match '+n['key'],front['object_id']==n['id'] and front['relationships']==[e for e in g['relationships'] if e['subject']==n['id']])
 for link in re.findall(r'\[\[([^]|]+)',t):assert (R/'review_vault'/(link+'.md')).is_file(),link
report={'result':'PASS','checks':checks,'check_count':len(checks),'scope':'Local structural checks of authored candidate; no application rendering, UA execution, independent semantic review or runtime enforcement tested'}
(R/'validation_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
