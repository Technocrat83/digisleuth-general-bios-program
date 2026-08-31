from shared_runtime import ContractSpec

EXPECTED_VERDICT_DOMAIN = [
    "DETERMINISTIC_COMMUTATIVE_PASS",
    "ORDER_DEPENDENCY_DETECTED",
]


def build_alpha_step_1(parent_digest: str) -> ContractSpec:
    return ContractSpec(
        "KMR_A4_ALPHA_1",
        [
            {"op": "add_node", "id": "ROUTE_A", "attrs": {"kind": "route", "standing": "DERIVED"}},
            {"op": "append_provenance", "entry": {"cycle_id": "A4_ALPHA_1", "parent_digest": parent_digest, "edit_digest": "ALPHA_1"}},
        ],
        ["STEP_ACCEPT", "STEP_REJECT"],
        "alpha step 1; parent must bind to H(K0)",
    )


def build_alpha_step_2(parent_digest: str) -> ContractSpec:
    return ContractSpec(
        "KMR_A4_ALPHA_2",
        [
            {"op": "add_edge", "src": "MAGUS", "rel": "localizes_to", "dst": "ROUTE_A"},
            {"op": "append_provenance", "entry": {"cycle_id": "A4_ALPHA_2", "parent_digest": parent_digest, "edit_digest": "ALPHA_2"}},
        ],
        ["STEP_ACCEPT", "STEP_REJECT"],
        "alpha step 2; parent must be rebound to H(K1)",
    )


def build_beta_step_1(parent_digest: str) -> ContractSpec:
    return ContractSpec(
        "KMR_A4_BETA_1",
        [
            {"op": "add_edge", "src": "MAGUS", "rel": "localizes_to", "dst": "ROUTE_A"},
            {"op": "append_provenance", "entry": {"cycle_id": "A4_BETA_1", "parent_digest": parent_digest, "edit_digest": "BETA_1"}},
        ],
        ["STEP_ACCEPT", "STEP_REJECT"],
        "beta step 1; parent must bind to H(K0)",
    )


def build_beta_step_2(parent_digest: str) -> ContractSpec:
    return ContractSpec(
        "KMR_A4_BETA_2",
        [
            {"op": "add_node", "id": "ROUTE_A", "attrs": {"kind": "route", "standing": "DERIVED"}},
            {"op": "append_provenance", "entry": {"cycle_id": "A4_BETA_2", "parent_digest": parent_digest, "edit_digest": "BETA_2"}},
        ],
        ["STEP_ACCEPT", "STEP_REJECT"],
        "beta step 2; parent must be rebound to H(K1_prime)",
    )


# Deliberately no function returns a pre-bound two-step list.
# The orchestrator must execute/validate step 1, hash the resulting accepted
# intermediate state, and only then construct step 2 using that digest.
# This file contains no execution trigger and does not adjudicate A4.
