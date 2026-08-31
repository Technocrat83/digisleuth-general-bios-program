from shared_runtime import ContractSpec

def build_contract(pre_digest: str) -> ContractSpec:
    return ContractSpec(
        chamber_id="KMR_A6_EPISTEMIC_STANDING_LAUNDERING",
        operations=[
            {"op":"add_node","id":"DERIVED_DISPLAY_ALIAS","attrs":{"kind":"uiux_projection","standing":"LEVEL_0"}},
            {"op":"add_edge","src":"PHENOTYPE_A","rel":"aliases","dst":"DERIVED_DISPLAY_ALIAS"},
            {"op":"append_provenance","entry":{"cycle_id":"A6","parent_digest":pre_digest,"edit_digest":"A6_STANDING"}}
        ],
        expected_verdict_domain=["EPISTEMIC_STANDING_LAUNDERING_DETECTED","UNEXPECTED_ACCEPTANCE"],
        notes="Morphology cannot promote a derived display object into Level-0 epistemic standing."
    )
