from shared_runtime import ContractSpec

def build_contract(pre_digest: str) -> ContractSpec:
    return ContractSpec(
        chamber_id="KMR_A3_PROVENANCE_DISCONTINUITY",
        operations=[
            {"op":"add_edge","src":"PHENOTYPE_A","rel":"references","dst":"SCIENCE"},
            {"op":"corrupt_parent_hash","cycle_id":"A3","value":"0000000000000000000000000000000000000000000000000000000000000000","edit_digest":"A3_CORRUPT_PARENT"}
        ],
        expected_verdict_domain=["PROVENANCE_DISCONTINUITY_DETECTED","UNEXPECTED_ACCEPTANCE"],
        notes="Correct morphology cannot compensate for exact parent-digest failure."
    )
