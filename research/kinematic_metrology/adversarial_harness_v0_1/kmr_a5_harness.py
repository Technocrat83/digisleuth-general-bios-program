from shared_runtime import ContractSpec

def build_contract(pre_digest: str) -> ContractSpec:
    return ContractSpec(
        chamber_id="KMR_A5_IDEMPOTENCE_AND_REPLAY_PRESSURE",
        operations=[
            {"op":"add_edge","src":"LABS","rel":"projects","dst":"PHENOTYPE_A"},
            {"op":"append_provenance","entry":{"cycle_id":"A5_REPLAY","parent_digest":pre_digest,"edit_digest":"A5_DUPLICATE_TOPOLOGY"}}
        ],
        expected_verdict_domain=["IDEMPOTENT_NO_NEW_MUTATION","PROVENANCE_INFLATION_DETECTED","UNEXPECTED_DUPLICATE_TOPOLOGY"],
        notes="Distinguishes graph idempotence from artificial provenance inflation."
    )
