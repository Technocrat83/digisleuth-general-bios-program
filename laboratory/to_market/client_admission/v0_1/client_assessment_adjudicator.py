"""
Adjudicates client-specific assessment petitions against G_assessment-admit = S & B & P & C & A.
Enforces non-compensation: any failed coordinate halts evaluation.
"""

from typing import Dict, Any, Tuple
import datetime

FROZEN_PROHIBITIONS = {
    "PRODUCTION_CERTIFIED_AGENT_GOVERNANCE_RUNTIME",
    "PROVEN_SAFE_AUTONOMOUS_DEPLOYMENT",
    "ENTERPRISE_RUNTIME_CERTIFICATION",
    "UNIVERSAL_AGENT_SAFETY"
}

class ClientAdmissionFault(Exception):
    pass

def evaluate_client_admission_petition(
    petition: Dict[str, Any],
    frozen_offer_sha: str
) -> Tuple[bool, str]:
    # 1. Offer Lineage Link
    lineage = petition.get("offer_lineage_ref", {})
    if lineage.get("git_commit_sha") != frozen_offer_sha:
        raise ClientAdmissionFault(
            f"Offer lineage mismatch: petition binds to {lineage.get('git_commit_sha')}, "
            f"expected frozen {frozen_offer_sha}"
        )

    # 2. Scope Envelope (S)
    scope = petition.get("S_scope_envelope", {})
    if not scope.get("included_workflows"):
        raise ClientAdmissionFault("S_FAULT: Scope must enumerate at least one explicit workflow.")
    if not scope.get("explicit_exclusions"):
        raise ClientAdmissionFault("S_FAULT: Scope must explicitly declare exclusions (no open cones).")

    # 3. Boundary & Isolation (B)
    boundary = petition.get("B_boundary_specification", {})
    if not boundary.get("isolation_attestation"):
        raise ClientAdmissionFault("B_FAULT: Isolation attestation must be explicit TRUE.")
    if boundary.get("write_socket_status") not in ["PHYSICALLY_DISABLED", "FIREWALL_BLOCKED", "CREDENTIAL_STRIPPED"]:
        raise ClientAdmissionFault("B_FAULT: Write sockets are not verified disabled.")

    # 4. Permission & Authority (P)
    perm = petition.get("P_permission_binding", {})
    if perm.get("remediation_authorization") != "ZERO_REMEDIATION_PERMITTED":
        raise ClientAdmissionFault("P_FAULT: Remediation authority cannot be non-zero.")
    if perm.get("production_execution_authorization") != "ZERO_EXECUTION_PERMITTED":
        raise ClientAdmissionFault("P_FAULT: Execution authority cannot be non-zero.")
    
    # TTL Check
    expiry_str = perm.get("lease_expiry_utc")
    try:
        expiry = datetime.datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        if expiry <= now:
            raise ClientAdmissionFault("P_FAULT: Diagnostic lease token is already expired.")
    except Exception as e:
        raise ClientAdmissionFault(f"P_FAULT: Invalid lease expiry format: {e}")

    # 5. Claim Ceiling & Anti-Inflation (C)
    claim = petition.get("C_claim_ceiling", {})
    if claim.get("inherited_scientific_standing") != "FIXTURE_CONFORMANCE_ONLY":
        raise ClientAdmissionFault("C_FAULT: Standing inflation detected in petition.")
    
    ack_prohibitions = set(claim.get("acknowledged_prohibited_claims", []))
    if not FROZEN_PROHIBITIONS.issubset(ack_prohibitions):
        missing = FROZEN_PROHIBITIONS - ack_prohibitions
        raise ClientAdmissionFault(f"C_FAULT: Petition fails to acknowledge mandatory prohibitions: {missing}")
    
    if not claim.get("client_acknowledged_non_warranty"):
        raise ClientAdmissionFault("C_FAULT: Client must acknowledge non-warranty diagnostic nature.")

    # 6. Artifact & Uncertainty Contract (A)
    artifact = petition.get("A_artifact_contract", {})
    if artifact.get("output_schema_id") != "ASSESSMENT_RESULT_SCHEMA_v0.1":
        raise ClientAdmissionFault("A_FAULT: Output schema must bind to ASSESSMENT_RESULT_SCHEMA_v0.1.")
    if not artifact.get("uncertainty_reporting_mandate"):
        raise ClientAdmissionFault("A_FAULT: Uncertainty reporting mandate cannot be waived.")
    if not artifact.get("advisory_disclaimer_bound"):
        raise ClientAdmissionFault("A_FAULT: Advisory disclaimer must be bound.")

    return True, "CLIENT_ENGAGEMENT_ADMISSION_ELIGIBLE"
