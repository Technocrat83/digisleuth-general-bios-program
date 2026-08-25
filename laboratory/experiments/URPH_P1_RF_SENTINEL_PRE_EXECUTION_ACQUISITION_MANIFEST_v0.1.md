# URPH_P1_RF_SENTINEL_PRE_EXECUTION_ACQUISITION_MANIFEST_v0.1

**PROGRAM:** General BIOS / Universal Runtime Pressure Hypothesis — Phase 1 Resource Finitude  
**PARENT:** `URPH_P1_RF_SENTINEL_B0_AND_HOST_BINDING_v0.1`  
**CELL:** `CELL_SENTINEL_S1_A1_O1`  
**JURISDICTION:** `PRE_EXECUTION_BYTE_IDENTITY_AND_EVIDENCE_DESTINATION_BINDING_ONLY`  
**AUTHORITY:** `NO_EXECUTION_AUTHORITY`  
**STATUS:** `PRE_EXECUTION_MANIFEST_SPECIFIED • REFERENT_RECOVERY_HALT • EPOCH_NOT_OPEN`

## Governing Boundary

`Manifest Commitment != Epoch Opening != Observation`

Nothing material to evidentiary identity may be chosen after the epoch begins.

## Frozen byte referents

- Input corpus: zero-byte `CORPUS_CANONICAL_TEST_VECTOR_01`.
- Input SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Objective: `O1_DETERMINISTIC_PAYLOAD_HASH`, transformation `SHA256(input_bytes) -> 32 raw digest bytes`.
- Expected SHA-256 of the 32 output bytes: `5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456`.
- Objective manifest SHA-256: `036051bf62dfdfd2428f11a5c55b615403525bfd037e7bd712fc757df07a06c7`.
- Task graph `G_O1` v1.0 SHA-256: `dbc423d1750dc96b4282d78af638d16034290d09e2bb2d35899289b018d16613`.
- Sentinel source SHA-256: `92c61fe8e5a5ea4c54662f945770144bc9ca4120cc5fe2f70e39c209fc41e354`.

A non-authoritative sandbox build reproduced the expected output digest exactly. This is build validation only; it is not baseline evidence, applicability evidence, or host binding.

## Instrument lineage

- Frozen witness contract commit: `e4358bd6a220ddadef36c51429374c5af9755305`.
- Conformant harness commit: `7b841db6a8fa1ff7dce6c89ef78de6b490df8a35`.
- Conformant harness archive SHA-256: `725ff4a3cb1001182bcda5d21ecd828130c15bd4958ece26ef7532090fae5c4e`.
- Conformance report SHA-256: `2b7123f8267635f7f02538d60a9f808003e3b57240ab593861667344240efa61`.

## Fail-closed unresolved referents

1. Physical host identity is not yet bound.
2. Current substrate identity requires `S1_NATIVE_POSIX_PROCESS`; a Windows-native host, WSL environment, VM, or container may not be silently substituted.
3. `B0` is not yet physically bound.
4. Absolute physical input/output/evidence paths are not yet frozen.
5. The target sentinel executable has not been compiled and hashed on the bound host.
6. The supplied candidate epoch token names `instrument_version: 1.0.4`, while the verified conformant implementation identity is `URPH_P1_RF_CLASS2_INSTRUMENT_HARNESS_v0.1` / package version `0.1.0`. This contradiction is unresolved and may not be repaired downstream.

Therefore:

```text
H_ACQ = UNMINTED
EPOCH_OPENING_TOKEN = NONE
EPOCH_OPENING_ELIGIBLE = FALSE
```

The pre-epoch gate remains unevaluated against the intended physical referent. Any failed coordinate yields `PRE_EXECUTION_HALT` with no partial authorization.

## Scientific containment

```text
ΔURPH = 0
ΔCUC = 0
ΔComputationalPhysiology = 0
ΔTrackE = 0
ΔCanon = 0
PP = BLOCKED
```

## Next lawful transition

`POPULATE_PHYSICAL_PATHS_AND_BYTE_DIGESTS -> RESOLVE_HOST_AND_INSTRUMENT_IDENTITY -> COMMIT_H_ACQ -> EPOCH_OPENING_ELIGIBLE`

No sentinel epoch may open before that chain is physically closed.