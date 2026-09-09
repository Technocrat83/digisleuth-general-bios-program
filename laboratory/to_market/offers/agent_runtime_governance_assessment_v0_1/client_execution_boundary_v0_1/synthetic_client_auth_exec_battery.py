from __future__ import annotations
import json
from pathlib import Path
from client_auth_exec_gate import *
HERE=Path(__file__).resolve().parent
FACT_SCHEMA=json.loads((HERE/"CLIENT_FACT_AUTHENTICATION_BUNDLE_v0.1.schema.json").read_text())
DEAP_SCHEMA=json.loads((HERE/"DIAGNOSTIC_EXECUTION_AUTHORIZATION_PETITION_v0.1.schema.json").read_text())
def fact(t,r="AUTHENTICATED"):
    return {"fact_id":"CF-"+t,"fact_type":t,"declared_value":"DECLARED","evidence_refs":["EVIDENCE:"+t],"provenance_pointer":"PROV:"+t,"authentication_epoch":100,"result":r}
FACT_TYPES=["CLIENT_ORGANIZATION_IDENTITY","AUTHORIZED_CLIENT_REPRESENTATIVE","AUTHORIZATION_ROLE","ENGAGEMENT_SCOPE","PERMITTED_SYSTEMS","EXCLUDED_SYSTEMS","DATA_ACCESS_PERMISSION","TEMPORAL_AUTHORIZATION","ISOLATION_REQUIREMENTS","CLIENT_ACCEPTED_PROHIBITED_ACTIONS"]
def bundle():
    return {"bundle_id":"CFAB-ALPHA-001","client_specimen_id":"CAAP-ALPHA-001","facts":[fact(t) for t in FACT_TYPES],"bundle_epoch":100}
def petition():
    return {"petition_id":"DEAP-ALPHA-001","client_specimen_id":"CAAP-ALPHA-001","admission_receipt_id":"CAAP-ALPHA-001-ADMIT","fact_bundle_id":"CFAB-ALPHA-001","requested_scope":["AGENT_A","WORKFLOW_A"],"current_authority_ref":"AUTH-CLIENT-001","execution_environment":"SANDBOX-CLIENT-A","orientation_status":"CURRENT","petition_epoch":101,"requested_actions":["OBSERVE","INSPECT","CLASSIFY","PRODUCE_RECOMMENDATIONS"]}

def run():
    b=bundle(); [f.update(result="UNRESOLVED") for f in b["facts"] if f["fact_type"]=="AUTHORIZED_CLIENT_REPRESENTATIVE"]
    ev=evaluate_fact_bundle(b,FACT_SCHEMA); assert ev.results["AUTHORIZED_CLIENT_REPRESENTATIVE"]=="UNRESOLVED"; print("PASS CFA01 AUTHORIZED_REPRESENTATIVE_UNVERIFIED -> UNRESOLVED")
    b=bundle(); [f.update(result="CONTRADICTED") for f in b["facts"] if f["fact_type"]=="CLIENT_ORGANIZATION_IDENTITY"]
    ev=evaluate_fact_bundle(b,FACT_SCHEMA); assert ev.results["CLIENT_ORGANIZATION_IDENTITY"]=="CONTRADICTED"; print("PASS CFA02 CLIENT_IDENTITY_CONTRADICTED -> CONTRADICTED")
    b=bundle(); [f.update(result="UNRESOLVED") for f in b["facts"] if f["fact_type"]=="PERMITTED_SYSTEMS"]
    ev=evaluate_fact_bundle(b,FACT_SCHEMA); assert ev.results["PERMITTED_SYSTEMS"]=="UNRESOLVED"; print("PASS CFA03 SCOPE_PERMISSION_UNRESOLVED -> UNRESOLVED")
    b=bundle(); [f.update(result="EXPIRED") for f in b["facts"] if f["fact_type"]=="TEMPORAL_AUTHORIZATION"]
    ev=evaluate_fact_bundle(b,FACT_SCHEMA); assert ev.results["TEMPORAL_AUTHORIZATION"]=="EXPIRED"; print("PASS CFA04 LEASE_EXPIRED -> EXPIRED")
    b=bundle(); [f.update(result="CONTRADICTED") for f in b["facts"] if f["fact_type"]=="EXCLUDED_SYSTEMS"]
    ev=evaluate_fact_bundle(b,FACT_SCHEMA); assert ev.results["EXCLUDED_SYSTEMS"]=="CONTRADICTED"; print("PASS CFA05 EXCLUSION_BOUNDARY_MISMATCH -> CONTRADICTED")
    ev=evaluate_fact_bundle(bundle(),FACT_SCHEMA); assert all(v=="AUTHENTICATED" for v in ev.results.values()); print("PASS CFA06 VALID_AUTHENTICATED_FACT_SET -> AUTHENTICATED")
    good_eval=ev; p=petition()
    r=evaluate_execution_petition(p,DEAP_SCHEMA,False,good_eval,set(p["requested_scope"]),p["execution_environment"],True,True); assert r.status=="BLOCKED"; print("PASS DEA01 ADMISSION_WITHOUT_AUTHENTICATION -> BLOCKED")
    r=evaluate_execution_petition(p,DEAP_SCHEMA,True,None,set(p["requested_scope"]),p["execution_environment"],True,True); assert r.status=="UNRESOLVED"; print("PASS DEA02 AUTHENTICATION_WITHOUT_ADMISSION -> UNRESOLVED")
    r=evaluate_execution_petition(p,DEAP_SCHEMA,True,good_eval,set(p["requested_scope"]),p["execution_environment"],True,False); assert r.status=="EXPIRED"; print("PASS DEA03 EXPIRED_TEMPORAL_AUTHORITY -> EXPIRED")
    r=evaluate_execution_petition(p,DEAP_SCHEMA,True,good_eval,{"AGENT_A"},p["execution_environment"],True,True); assert r.status=="BLOCKED"; print("PASS DEA04 SCOPE_DRIFT_AFTER_ADMISSION -> BLOCKED")
    r=evaluate_execution_petition(p,DEAP_SCHEMA,True,good_eval,set(p["requested_scope"]),"OTHER-ENV",True,True); assert r.status=="BLOCKED"; print("PASS DEA05 EXECUTION_ENVIRONMENT_MISMATCH -> BLOCKED")
    r=evaluate_execution_petition(p,DEAP_SCHEMA,True,good_eval,set(p["requested_scope"]),p["execution_environment"],False,True); assert r.status=="BLOCKED"; print("PASS DEA06 AUTHORITY_ESCALATION_ATTEMPT -> BLOCKED")
    r=evaluate_execution_petition(p,DEAP_SCHEMA,True,good_eval,set(p["requested_scope"]),p["execution_environment"],True,True); assert r.status=="AUTHORIZED"; print("PASS DEA07 VALID_DIAGNOSTIC_AUTHORIZATION -> AUTHORIZED")
if __name__=="__main__": run()
