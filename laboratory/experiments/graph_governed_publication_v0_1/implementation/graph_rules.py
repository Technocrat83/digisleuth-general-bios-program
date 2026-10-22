"""Finite typed graph matching for this specimen, not general graph rewriting."""
def graph_admits(graph,actor):
    nodes={n['id']:n for n in graph['nodes']}
    if len(nodes)!=len(graph['nodes']):return False
    allowed={k:tuple(v) for k,v in graph['relation_signatures'].items()}
    edges=set()
    for edge in graph['edges']:
        a,r,b=edge
        if a not in nodes or b not in nodes or r not in allowed:return False
        if (nodes[a]['type'],nodes[b]['type'])!=allowed[r]:return False
        edges.add((a,r,b))
    required=[(actor,'ASSIGNED_TO','task'),('task','DEPENDS_ON','revision'),('source','SUPPORTS','revision'),('review','APPROVES','revision'),('grant-'+actor,'GRANTS',actor),('task','TARGETS','sink'),('boundary','MEDIATES','sink')]
    if actor=='delegate':required.append(('primary','DELEGATES_TO','delegate'))
    return all(e in edges for e in required)
