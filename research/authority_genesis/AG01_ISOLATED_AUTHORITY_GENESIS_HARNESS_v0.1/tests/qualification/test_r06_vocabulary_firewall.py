from .common import ROOT, witness

def measure():
    files=[ROOT/"observers"/n for n in ("representation.py","registration.py","effect.py")]
    forbidden={"ENTITLED","AUTHORITY","GENESIS","PASS"}
    hits=[]
    for p in files:
        if not p.exists():
            return witness("C_06","R_06",files,"STATIC_LEXICAL",[f"MISSING:{p.name}"],"Observer emissions contain no adjudicative vocabulary","INCOMPLETE","OBSERVER_MODULE_MISSING")
        text=p.read_text(encoding="utf-8").upper()
        for token in forbidden:
            if token in text: hits.append({"file":p.name,"token":token})
    ok=not hits
    return witness("C_06","R_06",files,"STATIC_LEXICAL",hits or ["NO_FORBIDDEN_VOCABULARY"],"Observer emissions contain no adjudicative vocabulary","PASS" if ok else "FAIL",None if ok else "ADJUDICATIVE_VOCABULARY_DETECTED")
