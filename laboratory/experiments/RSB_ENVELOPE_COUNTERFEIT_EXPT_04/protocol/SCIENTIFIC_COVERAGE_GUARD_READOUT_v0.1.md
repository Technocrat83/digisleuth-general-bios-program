# SCIENTIFIC_COVERAGE_GUARD_READOUT_v0.1

**EXPERIMENT:** `RSB_ENVELOPE_COUNTERFEIT_EXPT_04_v0.1`
**STATUS:** `READ_ONLY_COVERAGE_CHARACTERIZATION`
**AUTHORITY:** ZERO SPECIMEN-REDEFINITION AUTHORITY
**PP:** BLOCKED

## Frozen control anchors

- `J_D_PRE`: `cca32d004ba0005c508b3ce51250d955ce425cb4`
- `ADM_ORACLE`: `cf2c44f084d81a0aa3b62f6c44f748c4269afe43`

## Materialized frozen bank

- `E4_A`: well-formed unsigned
- `E4_B`: self-signed counterfeit
- `E4_C`: replay/stale witness
- `E4_D`: unrelated bound witness
- `E4_E`: legitimate admitted positive

## Coverage guard

Required for the strongest clean T3/T4 discriminator:

`AuthenticatedFreshEnvelope(E) = 1 AND Admitted(E) = 0`

The frozen bank does contain specimens with `T3=1, T4=0`, but the reasons for T4 failure are confounded with additional admission-witness defects:

- `E4_C`: T3=1, T4=0 because the admission witness is stale/replayed.
- `E4_D`: T3=1, T4=0 because the current witness binds to another envelope.

Neither specimen is the pure case `authentic fresh envelope + no valid admission witness at all`.

Therefore the bank may test freshness and binding separation, and may provide bounded evidence that authentication alone does not cure a defective admission witness, but it must not be used to claim that the clean `T3 ->/ T4` discriminator has been fully isolated.

## Non-repair law

`Coverage deficiency != specimen mutation authority`.

`A frozen test may discover that its coverage is insufficient; coverage deficiency must not be repaired by silently changing the test.`

No specimen semantics, consumer rule, admission-oracle rule, or adjudication rule are altered by this readout.
