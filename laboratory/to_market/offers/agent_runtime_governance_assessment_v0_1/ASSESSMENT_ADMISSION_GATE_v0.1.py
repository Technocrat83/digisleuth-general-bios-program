from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
import json, hashlib
from jsonschema import Draft202012Validator

class AssessmentAdmissionError(ValueError): pass

PROHIBITED_CERT_TERMS = (
    "PRODUCTION_CERTIFIED_AGENT_GOVERNANCE_RUNTIME",
    "PROVEN_SAFE_AUTONOMOUS_DEPLOYMENT",
    "ENTERPRISE_RUNTIME_CERTIFICATION",
    "UNIVERSAL_AGENT_SAFETY",
)

@dataclass(frozen=True)
class AdmissionResult:
    status: str
    scope_bound: bool
    buyer_claim_bound: bool
    permission_bound: bool
    contract_bound: bool
    authority_bound: bool
    reason: str|None = None

def validate_contract(contract: Mapping[str,Any], schema: Mapping[str,Any]) -> None:
    errors=sorted(Draft202012Validator(schema).iter_errors(contract), key=lambda e:list(e.path))
    if errors:
        e=errors[0]
        raise AssessmentAdmissionError(f"SCHEMA_REJECT:{str(e.validator).upper()}:{list(e.path)}:{e.message}")

def scope_digest(scope: Mapping[str,Any]) -> str:
    raw=json.dumps(scope,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()

def assess_admission(contract: Mapping[str,Any], schema: Mapping[str,Any]) -> AdmissionResult:
    validate_contract(contract,schema)
    s=bool(contract["scope"]["declared_systems"] and contract["scope"]["declared_workflows"])
    claim=contract["claim_boundary"]["supported_claim"].upper()
    b=all(term not in claim for term in PROHIBITED_CERT_TERMS)
    p=bool(contract["permissions"]["authorized_surfaces"] and contract["permissions"]["client_authorization_ref"])
    c=bool(contract["claim_boundary"]["prohibited_claims"] and contract["output_contract"]["finding_states"])
    a=(contract["authority_boundary"]=={"diagnostic":True,"remediation":False,"certification":False,"execution":False})
    ok=s and b and p and c and a
    return AdmissionResult("ADMISSION_ELIGIBLE" if ok else "EXECUTION_BLOCKED",s,b,p,c,a,None if ok else "GATE_COORDINATE_FAILED")

def validate_result(result: Mapping[str,Any], result_schema: Mapping[str,Any], contract: Mapping[str,Any]) -> bool:
    errors=sorted(Draft202012Validator(result_schema).iter_errors(result), key=lambda e:list(e.path))
    if errors:
        e=errors[0]; raise AssessmentAdmissionError(f"RESULT_SCHEMA_REJECT:{str(e.validator).upper()}:{list(e.path)}:{e.message}")
    if result["assessment_id"] != contract["assessment_id"]:
        raise AssessmentAdmissionError("ASSESSMENT_ID_MISMATCH")
    if result["scope_digest"] != scope_digest(contract["scope"]):
        raise AssessmentAdmissionError("SCOPE_DIGEST_MISMATCH")
    declared=set(contract["scope"]["declared_workflows"])
    for f in result["findings"]:
        if f["workflow_id"] not in declared:
            raise AssessmentAdmissionError("OUT_OF_SCOPE_INFERENCE")
        if f["evidence_state"] in {"UNRESOLVED","NOT_ASSESSED"} and f["severity"]=="CRITICAL":
            raise AssessmentAdmissionError("UNRESOLVED_STATE_COERCION")
    return True
