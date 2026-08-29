import json
from .common import ROOT, witness

def measure():
    candidates=[ROOT/"schemas"/"runtime_residue.schema.json",ROOT/"schemas"/"qualification_witness.schema.json"]
    residue=next((p for p in candidates if p.exists() and p.name=="runtime_residue.schema.json"),None)
    if residue is None:
        return witness("C_07","R_07",candidates,"SCHEMA_PROBE",["RUNTIME_RESIDUE_SCHEMA_ABSENT"],"Runtime residue schema rejects interpretive field theorem_supported","INCOMPLETE","RESIDUE_SCHEMA_TARGET_ABSENT")
    schema=json.loads(residue.read_text(encoding="utf-8"))
    additional=schema.get("additionalProperties")
    props=schema.get("properties",{})
    leaked="theorem_supported" in props
    ok=(additional is False and not leaked)
    return witness("C_07","R_07",[residue],"SCHEMA_PROBE",[{"additionalProperties":additional,"theorem_supported_declared":leaked}],"Runtime residue schema rejects interpretive field theorem_supported","PASS" if ok else "FAIL",None if ok else "INTERPRETIVE_SCHEMA_LEAK")
