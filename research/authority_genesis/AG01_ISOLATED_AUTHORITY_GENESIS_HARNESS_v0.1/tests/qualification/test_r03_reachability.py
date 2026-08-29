import ast
from .common import ROOT, parse_python, witness

def measure():
    path=ROOT/"harness"/"grant_exclusion.py"
    tree=parse_python(path)
    forbidden={"derive","reachable","reachability","networkx","shortest_path","dfs","bfs"}
    hits=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.Name,ast.Attribute)):
            token=(node.id if isinstance(node,ast.Name) else node.attr).lower()
            if token in forbidden: hits.append(token)
    ok=not hits
    return witness("C_03","R_03",[path],"STATIC_AST",hits or ["NO_REACHABILITY_DERIVER_SYMBOLS"],"G_X contains no reachability derivation routine","PASS" if ok else "FAIL",None if ok else "ILLEGAL_DERIVATION_ROUTINE_FOUND")
