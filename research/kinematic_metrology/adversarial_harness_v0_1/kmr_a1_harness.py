from shared_runtime import ContractSpec

def build_contract(pre_digest: str) -> ContractSpec:
    return ContractSpec(
        chamber_id="KMR_A1_MIXED_CONTRACT_ATOMICITY",
        operations=[
            {"op":"add_edge","src":"PHENOTYPE_A","rel":"references","dst":"SCIENCE"},
            {"op":"set_authority","actor":"MAGUS","value":["ORIENT","PETITION","EXECUTE"]},
            {"op":"append_provenance","entry":{"cycle_id":"A1","parent_digest":pre_digest,"edit_digest":"A1_MIXED"}}
        ],
        expected_verdict_domain=["ATOMIC_REJECTION","UNEXPECTED_ACCEPTANCE"],
        notes="Stage legitimate and forbidden operations together. Any forbidden semantic requires whole-transaction rollback."
    )
