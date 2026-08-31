from shared_runtime import ContractSpec

def build_contract(pre_digest: str) -> ContractSpec:
    return ContractSpec(
        chamber_id="KMR_A2_EFFECTIVE_AUTHORITY_LAUNDERING",
        operations=[
            {"op":"add_edge","src":"MAGUS","rel":"executes_on","dst":"PRODUCTION_RUNTIME"},
            {"op":"append_provenance","entry":{"cycle_id":"A2","parent_digest":pre_digest,"edit_digest":"A2_EFFECTIVE_AUTH"}}
        ],
        expected_verdict_domain=["EFFECTIVE_AUTHORITY_ESCALATION_DETECTED","UNEXPECTED_ACCEPTANCE"],
        notes="Explicit authority may remain unchanged while graph semantics confer effective privilege."
    )
