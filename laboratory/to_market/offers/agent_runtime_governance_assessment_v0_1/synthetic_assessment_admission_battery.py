import copy, json, pathlib, importlib.util
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("gate",HERE/"ASSESSMENT_ADMISSION_GATE_v0.1.py")
gate=importlib.util.module_from_spec(spec); import sys; sys.modules["gate"]=gate; spec.loader.exec_module(gate)
schema=json.loads((HERE/"AGENT_RUNTIME_GOVERNANCE_ASSESSMENT_CONTRACT_v0.1.schema.json").read_text())
rschema=json.loads((HERE/"ASSESSMENT_RESULT_SCHEMA_v0.1.json").read_text())

BASE={
"assessment_id":"ARGA-SYNTH-001","parent_translation_id":"CTO-OAB-002","parent_event_id":"TME-OAB-002",
"offer_class":"ADVISORY_DIAGNOSTIC_ASSESSMENT","scientific_standing":"FIXTURE_CONFORMANCE_ONLY",
"scope":{"declared_systems":["SYNTH_SYS"],"declared_workflows":["WF-1"],"excluded_systems":["SYS-X"],"scope_epoch":1},
"permissions":{"authorized_surfaces":["AGENT_INVENTORY","WORKFLOW_INVENTORY","PERMISSION_MODEL"],"client_authorization_ref":"AUTH-SYNTH-001"},
"claim_boundary":{"supported_claim":"Digisleuth can assess where autonomous AI workflows may continue operating from stale, changed, or no-longer-valid organizational context and identify governance controls needed to bound that behavior.","prohibited_claims":["PRODUCTION_CERTIFIED_AGENT_GOVERNANCE_RUNTIME","PROVEN_SAFE_AUTONOMOUS_DEPLOYMENT","ENTERPRISE_RUNTIME_CERTIFICATION","UNIVERSAL_AGENT_SAFETY"]},
"authority_boundary":{"diagnostic":True,"remediation":False,"certification":False,"execution":False},
"output_contract":{"finding_states":["OBSERVED","DECLARED_BY_CLIENT","INFERRED","UNRESOLVED","NOT_ASSESSED"],"abstention_codes":["OUT_OF_SCOPE_SYSTEM","UNRESOLVED_PERMISSION_MODEL"]}
}
def result_for(c):
  return {"assessment_id":c["assessment_id"],"client_id":"CLIENT-SYNTH","scope_digest":gate.scope_digest(c["scope"]),
  "findings":[{"finding_id":"SCG-F-001","workflow_id":"WF-1","finding_type":"SCG-03","evidence_state":"OBSERVED","severity":"HIGH","evidence_refs":["E-1"],"unresolved_dependencies":[],"recommendations":["ORIENTATION_INVALIDATION_GATE"]}],
  "recommendations":["ORIENTATION_INVALIDATION_GATE"],"unresolved_surfaces":[],"economic_measurements":["GOVERNANCE_GATE_COVERAGE"],"prohibited_conclusions":["NO_CERTIFICATION"],"assessment_epoch":1}

def reject(name, fn, needle):
  try: fn()
  except Exception as e:
    assert needle in str(e), (name,str(e))
    print("PASS",name,"BLOCKED",str(e)); return
  raise AssertionError(name+" expected block")

c=copy.deepcopy(BASE); r=result_for(c); r["findings"][0]["workflow_id"]="WF-OUT"
reject("AA01_SCOPE_OVERREACH",lambda:gate.validate_result(r,rschema,c),"OUT_OF_SCOPE_INFERENCE")
c=copy.deepcopy(BASE); c["claim_boundary"]["supported_claim"]="PROVEN_SAFE_AUTONOMOUS_DEPLOYMENT"
res=gate.assess_admission(c,schema); assert res.status=="EXECUTION_BLOCKED"; print("PASS AA02_CERTIFICATION_INFLATION BLOCKED")
c=copy.deepcopy(BASE); r=result_for(c); r["findings"][0]["evidence_state"]="UNRESOLVED"; r["findings"][0]["severity"]="CRITICAL"
reject("AA03_UNRESOLVED_STATE_COERCION",lambda:gate.validate_result(r,rschema,c),"UNRESOLVED_STATE_COERCION")
c=copy.deepcopy(BASE); c["authority_boundary"]["remediation"]=True
reject("AA04_UNAUTHORIZED_REMEDIATION",lambda:gate.assess_admission(c,schema),"SCHEMA_REJECT")
c=copy.deepcopy(BASE); r=result_for(c); r["findings"][0]["workflow_id"]="SYS-X"
reject("AA05_OUT_OF_SCOPE_INFERENCE",lambda:gate.validate_result(r,rschema,c),"OUT_OF_SCOPE_INFERENCE")
c=copy.deepcopy(BASE); c["permissions"]["client_authorization_ref"]=""
reject("AA06_MISSING_PERMISSION_BINDING",lambda:gate.assess_admission(c,schema),"SCHEMA_REJECT")
c=copy.deepcopy(BASE); c["claim_boundary"]["prohibited_claims"]=[]
reject("AA07_MISSING_PROHIBITED_CLAIMS",lambda:gate.assess_admission(c,schema),"SCHEMA_REJECT")
c=copy.deepcopy(BASE); a=gate.assess_admission(c,schema); assert a.status=="ADMISSION_ELIGIBLE"; r=result_for(c); assert gate.validate_result(r,rschema,c); print("PASS AA08_VALID_DIAGNOSTIC_CONTROL ADMISSION_ELIGIBLE")
print("PASS_ASSESSMENT_ADMISSION_BATTERY=TRUE")
