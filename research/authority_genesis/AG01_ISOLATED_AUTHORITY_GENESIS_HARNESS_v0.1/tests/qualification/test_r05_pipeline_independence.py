import ast
from .common import ROOT, parse_python, witness

def measure():
    files=[ROOT/"observers"/n for n in ("representation.py","registration.py","effect.py")]
    if not all(p.exists() for p in files):
        return witness("C_05","R_05",files,"STATIC_AST",["OBSERVER_MODULE_MISSING"],"O_R, O_G, O_E are isolated pipelines with no cross-import or shared evaluator","INCOMPLETE","OBSERVATION_PIPELINE_MISSING")
    cross=[]
    names={p.stem for p in files}
    for p in files:
        tree=parse_python(p)
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[-1] in names: cross.append((p.name,alias.name))
            if isinstance(node,ast.ImportFrom) and node.module and node.module.split(".")[-1] in names:
                cross.append((p.name,node.module))
    ok=not cross
    return witness("C_05","R_05",files,"STATIC_AST",cross or ["THREE_MODULES_PRESENT_NO_CROSS_IMPORTS"],"O_R, O_G, O_E are isolated pipelines with no cross-import or shared evaluator","PASS" if ok else "FAIL",None if ok else "OBSERVATION_SURFACE_CONTAMINATED")
