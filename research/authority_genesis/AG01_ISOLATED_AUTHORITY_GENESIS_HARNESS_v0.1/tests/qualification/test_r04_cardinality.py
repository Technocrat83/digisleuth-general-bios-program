import ast
from .common import ROOT, parse_python, witness

def measure():
    candidates=[ROOT/"harness"/"state_machine.py",ROOT/"harness"/"invocation.py",ROOT/"runtime"/"run_ag01.py"]
    existing=[p for p in candidates if p.exists()]
    if not existing:
        return witness("C_04","R_04",candidates,"STATIC_AST",["NO_CARDINALITY_LOCK_SURFACE"],"Second invocation is rejected by terminal single-use lock","INCOMPLETE","INVOCATION_LOCK_REALIZER_TARGET_ABSENT")
    tokens=[]
    for p in existing:
        text=p.read_text(encoding="utf-8").lower()
        tokens += [t for t in ("single_use","invocation_count","permanently_closed","second invocation") if t in text]
    if not tokens:
        return witness("C_04","R_04",existing,"STATIC_AST",["NO_CARDINALITY_LOCK_SYMBOLS"],"Second invocation is rejected by terminal single-use lock","INCOMPLETE","INVOCATION_LOCK_REALIZER_TARGET_ABSENT")
    return witness("C_04","R_04",existing,"STATIC_AST",tokens,"Second invocation is rejected by terminal single-use lock","PASS",None)
