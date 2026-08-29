from .common import ROOT, witness
from observers import representation, registration, effect

def measure():
    files=[ROOT/"observers"/n for n in ("representation.py","registration.py","effect.py")]
    outputs=[
        representation.observe("QUALIFICATION_FIXTURE","INDETERMINATE"),
        registration.observe("QUALIFICATION_FIXTURE","INDETERMINATE"),
        effect.observe("QUALIFICATION_FIXTURE","INDETERMINATE"),
    ]
    ok=all(v.get("value")=="UNRESOLVED" for v in outputs)
    return witness("C_09","R_09",files,"SYNTHETIC_FIXTURE",outputs,"Indeterminate observation fixture is preserved as UNRESOLVED on all three surfaces","PASS" if ok else "FAIL",None if ok else "MISSINGNESS_COLLAPSE")
