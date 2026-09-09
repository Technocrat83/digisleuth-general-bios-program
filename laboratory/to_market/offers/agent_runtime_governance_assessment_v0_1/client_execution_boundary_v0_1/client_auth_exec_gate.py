from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any
from jsonschema import Draft202012Validator

class ClientBoundaryError(ValueError): pass

FACT_TYPES_REQUIRED = {
"CLIENT_ORGANIZATION_IDENTITY","AUTHORIZED_CLIENT_REPRESENTATIVE","AUTHORIZATION_ROLE",
"ENGAGEMENT_SCOPE","PERMITTED_SYSTEMS","EXCLUDED_SYSTEMS","DATA_ACCESS_PERMISSION",
"TEMPORAL_AUTHORIZATION","ISOLATION_REQUIREMENTS","CLIENT_ACCEPTED_PROHIBITED_ACTIONS"
}

@dataclass(frozen=True)
class FactAuthenticationEvaluation:
    status: str
    results: Mapping[str,str]

@dataclass(frozen=True)
class ExecutionAuthorizationEvaluation:
    status: str
    reason: str|None

def _schema_validate(obj: Mapping[str,Any], schema: Mapping[str,Any], prefix: str):
    errs=sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e:list(e.path))
    if errs:
        e=errs[0]
        raise ClientBoundaryError(f"{prefix}_SCHEMA_REJECT:{str(e.validator).upper()}:{list(e.path)}:{e.message}")

def evaluate_fact_bundle(bundle: Mapping[str,Any], schema: Mapping[str,Any]) -> FactAuthenticationEvaluation:
    _schema_validate(bundle,schema,"FACT")
    by_type={f["fact_type"]:f["result"] for f in bundle["facts"]}
    missing=FACT_TYPES_REQUIRED-set(by_type)
    if missing:
        raise ClientBoundaryError("REQUIRED_FACT_SURFACE_MISSING:"+",".join(sorted(missing)))
    return FactAuthenticationEvaluation("EVALUATED", by_type)

def evaluate_execution_petition(
    petition: Mapping[str,Any],
    petition_schema: Mapping[str,Any],
    admission_eligible: bool,
    fact_eval: FactAuthenticationEvaluation|None,
    authenticated_scope: set[str],
    authenticated_environment: str,
    authority_current: bool,
    temporal_authority_current: bool,
) -> ExecutionAuthorizationEvaluation:
    _schema_validate(petition,petition_schema,"DEAP")
    if not admission_eligible:
        return ExecutionAuthorizationEvaluation("BLOCKED","ADMISSION_NOT_ELIGIBLE")
    if fact_eval is None:
        return ExecutionAuthorizationEvaluation("UNRESOLVED","FACT_AUTHENTICATION_ABSENT")
    for req in ["CLIENT_ORGANIZATION_IDENTITY","AUTHORIZED_CLIENT_REPRESENTATIVE","AUTHORIZATION_ROLE","ENGAGEMENT_SCOPE","PERMITTED_SYSTEMS","DATA_ACCESS_PERMISSION","TEMPORAL_AUTHORIZATION","CLIENT_ACCEPTED_PROHIBITED_ACTIONS"]:
        state=fact_eval.results.get(req,"UNRESOLVED")
        if state=="EXPIRED":
            return ExecutionAuthorizationEvaluation("EXPIRED",f"{req}_EXPIRED")
        if state!="AUTHENTICATED":
            return ExecutionAuthorizationEvaluation("UNRESOLVED" if state=="UNRESOLVED" else "BLOCKED",f"{req}_{state}")
    if not temporal_authority_current:
        return ExecutionAuthorizationEvaluation("EXPIRED","TEMPORAL_AUTHORITY_EXPIRED")
    if not authority_current:
        return ExecutionAuthorizationEvaluation("BLOCKED","CURRENT_AUTHORITY_INVALID")
    if petition["orientation_status"]!="CURRENT":
        return ExecutionAuthorizationEvaluation("UNRESOLVED" if petition["orientation_status"]=="UNRESOLVED" else "BLOCKED","ORIENTATION_NOT_CURRENT")
    if set(petition["requested_scope"]) - authenticated_scope:
        return ExecutionAuthorizationEvaluation("BLOCKED","SCOPE_DRIFT_AFTER_ADMISSION")
    if petition["execution_environment"] != authenticated_environment:
        return ExecutionAuthorizationEvaluation("BLOCKED","EXECUTION_ENVIRONMENT_MISMATCH")
    return ExecutionAuthorizationEvaluation("AUTHORIZED",None)
