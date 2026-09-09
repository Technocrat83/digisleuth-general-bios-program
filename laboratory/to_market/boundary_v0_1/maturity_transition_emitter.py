"""
Non-sovereign emitter for TO_MARKET_EVENT_v0.1.
Enforces the emission invariant: M_0 != M_1.
"""

from typing import Dict, Any, Optional
import time
import uuid

ALLOWED_TRANSITIONS = {
    "SPECIFICATION_FROZEN",
    "ARCHITECTURE_ADMITTED",
    "STATIC_CONFORMANCE_QUALIFIED",
    "EXPERIMENT_EXECUTED",
    "EVIDENCE_ADMITTED",
    "CAPABILITY_DEMONSTRATED",
    "RUNTIME_QUALIFIED",
    "BIOS_CHARACTERIZED",
    "DEPLOYMENT_CAPABLE",
    "REPEATED_WORKFLOW_PROVEN",
    "CLIENT_OUTCOME_OBSERVED",
    "MATERIAL_TELEMETRY_ACCUMULATED",
}

class InvariantBreach(Exception):
    pass

def emit_to_market_event(
    originating_residue_id: str,
    prior_maturity_state: str,
    current_maturity_state: str,
    transition_type: str,
    exact_scientific_standing: str,
    git_commit_sha: str,
    source_node: str,
    epoch_timestamp: Optional[int] = None
) -> Dict[str, Any]:
    if prior_maturity_state == current_maturity_state:
        raise InvariantBreach(
            f"Zero maturity transition: {prior_maturity_state} -> {current_maturity_state}. "
            "To Market emission forbidden."
        )

    if transition_type not in ALLOWED_TRANSITIONS:
        raise InvariantBreach(
            f"Unrecognized transition type: '{transition_type}'. "
            "Cannot coerce into closed domain."
        )

    if len(git_commit_sha) != 40:
        raise InvariantBreach(f"Invalid Git commit SHA: {git_commit_sha}")

    event_id = f"TME-{uuid.uuid4().hex[:12].upper()}"
    epoch = epoch_timestamp if epoch_timestamp is not None else int(time.time())

    return {
        "event_id": event_id,
        "originating_residue_id": originating_residue_id,
        "prior_maturity_state": prior_maturity_state,
        "current_maturity_state": current_maturity_state,
        "transition_type": transition_type,
        "exact_scientific_standing": exact_scientific_standing,
        "provenance_pointer": {
            "git_commit_sha": git_commit_sha,
            "source_node": source_node
        },
        "epoch_timestamp": epoch
    }