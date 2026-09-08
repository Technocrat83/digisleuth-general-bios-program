# OAB Fixture Ingress v0.2

**Status:** MATERIALIZED • UNQUALIFIED  
**Ancestor contract:** `OAB_FIXTURE_LOADER_CONTRACT_v0.1`  
**Ancestor manifest:** `OAB_FIXTURE_INGRESS_MANIFEST_v0.1`  
**Runtime Runner:** BLOCKED  
**Scientific Delta:** 0  
**Execution Authority Delta:** 0  
**PP:** BLOCKED

## Semantic lineage law

`Semantic Mutation -> Identity Mutation`

A previously witnessed semantic identity may not acquire new mandatory meaning retroactively.

v0.1 remains historically closed and immutable. v0.2 is a descendant contract and must earn independent qualification.

## v0.2 additions

- required root coordinate `invalidation_trigger`
- closed trigger domain: `IDENTITY_SUBSTITUTION | PROVENANCE_SEVERANCE | PLACEMENT_MUTATION | JURISDICTION_DRIFT | STATE_MUTATION | EPOCH_ROLLOVER | TOPOLOGY_MUTATION | AUTHORITY_ESCALATION_ATTEMPTED | UNRESOLVED_DEPENDENCY | NONE`
- jurisdiction identifiers remain `0x` + exactly 32 hex digits (128 bits)
- `prior_jurisdiction_hash` / `current_jurisdiction_hash` are SHA-256 jurisdiction-state digests: exactly 64 hex digits, no prefix
- explicit `prior_manifest_id` and `prior_contract_id` in the manifest

Synthetic jurisdiction-state fixture digests are replayable derivations:
- A = `SHA256("OAB_JURISDICTION_STATE_A_v0.2")` = `f2ed9f914993441fc81a3d366a64201dcc2a3ef4eef31aa1c0e517e8f8c8ccd3`
- B = `SHA256("OAB_JURISDICTION_STATE_B_v0.2")` = `c1eed32124c30ffee4e05d73e5ce6edd8d2b6cd1baec0a124fd3fa7680e5a8c1`

## Separation

`Structural Typing Authority != Causal Compatibility Authority`

The loader validates trigger membership and affected-surface membership independently. It does not infer or enforce trigger-to-surface causal compatibility.

No v0.1 loader qualification is inherited by v0.2.
