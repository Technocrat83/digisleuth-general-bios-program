from shared_runtime import ContractSpec

def build_order_alpha(pre_digest: str) -> list[ContractSpec]:
    return [
        ContractSpec("KMR_A4_ALPHA_1",[{"op":"add_node","id":"ROUTE_A","attrs":{"kind":"route","standing":"DERIVED"}}],["STEP_ACCEPT","STEP_REJECT"],"alpha step 1"),
        ContractSpec("KMR_A4_ALPHA_2",[{"op":"add_edge","src":"MAGUS","rel":"localizes_to","dst":"ROUTE_A"},{"op":"append_provenance","entry":{"cycle_id":"A4_ALPHA","parent_digest":pre_digest,"edit_digest":"ALPHA"}}],["STEP_ACCEPT","STEP_REJECT"],"alpha step 2")
    ]

def build_order_beta(pre_digest: str) -> list[ContractSpec]:
    return [
        ContractSpec("KMR_A4_BETA_1",[{"op":"add_edge","src":"MAGUS","rel":"localizes_to","dst":"ROUTE_A"}],["STEP_ACCEPT","STEP_REJECT"],"beta step 1"),
        ContractSpec("KMR_A4_BETA_2",[{"op":"add_node","id":"ROUTE_A","attrs":{"kind":"route","standing":"DERIVED"}},{"op":"append_provenance","entry":{"cycle_id":"A4_BETA","parent_digest":pre_digest,"edit_digest":"BETA"}}],["STEP_ACCEPT","STEP_REJECT"],"beta step 2")
    ]

EXPECTED_VERDICT_DOMAIN=["DETERMINISTIC_COMMUTATIVE_PASS","ORDER_DEPENDENCY_DETECTED"]
# Materialization does not adjudicate which verdict is correct.
