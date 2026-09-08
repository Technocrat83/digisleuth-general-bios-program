# ORIENTATION_INVALIDATION_REPLAY_VALIDATOR_v0.1

**Class:** ISOLATED_EXECUTION_WITNESS_VERIFICATION_APPARATUS  
**Parent:** JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1 + ORIENTATION_INVALIDATION_MONITOR_v0.1  
**Authority:** VERIFY_BINDING, VERIFY_CANONICAL_DIGEST, VERIFY_LOCALIZATION_RECONSTRUCTION, VERIFY_DISPOSITION_RECONSTRUCTION  
**Zero Authority:** REPAIR_WITNESS, RELOCALIZE_WITH_NEW_FACTS, REORIENT_OBJECT, MUTATE_AUTHORITY, MUTATE_TOPOLOGY, TRIGGER_EXECUTION  
**PP:** BLOCKED

## Constitutional ordering

`Replay Semantics -> Replay Validator -> Fixture Loader -> Runtime Runner -> G_orientation_exec_qual`

The replay validator verifies that a recorded invalidation witness corresponds to the exact observed delta and prior orientation witness under frozen localization and monitor semantics. It never defines those semantics retrospectively.

## Replay result vector

`Replay(W_I, Delta_obs) = <IdentityMatch, DigestMatch, LocalizationMatch, DispositionMatch, NoRepair>`

Each coordinate is typed independently:

- `INPUT_BINDING: PASS | FAIL | UNRESOLVED`
- `DIGEST_BINDING: PASS | FAIL`
- `LOCALIZATION_RECONSTRUCTION: PASS | FAIL | UNRESOLVED`
- `DISPOSITION_RECONSTRUCTION: PASS | FAIL | UNRESOLVED`
- `REPAIR_ATTEMPTED: PASS | FAIL | UNRESOLVED`

Qualification requires all five coordinates to be `PASS`.

A matching digest does not compensate for a wrong cone, wrong lifecycle disposition, stale prior-object binding, version drift, or any recorded repair attempt.

## Frozen semantic identities

Replay input must explicitly bind to:

- `ORIENTATION_DELTA_CANONICAL_ENCODING_v0.1`
- `JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1`
- `ORIENTATION_INVALIDATION_MONITOR_v0.1`

Rule identifiers are part of input conformance and may not be inferred from the currently installed runtime.

## Canonical evidence encoding

`ORIENTATION_DELTA_CANONICAL_ENCODING_v0.1` fixes:

- exact FieldDelta field set
- exact field order
- UTF-8 string encoding
- 32-bit unsigned big-endian length prefixes
- one-byte Boolean encoding (`0x00 | 0x01`)
- explicit field names and type tags in the byte stream
- no field omission, default elision, debug serialization, map-order dependence, enum-format dependence, or runtime-specific object representation

`H_evidence = SHA256(CanonicalEncode_v0.1(Delta_obs))`

Any change to field set, ordering, width, or primitive encoding requires a new canonical encoding version.

## Localization replay completeness

Replay compares:

- localization standing
- affected surfaces
- causal cone
- jurisdictional cone
- unresolved dependencies
- localization epoch

The validator may verify recorded geometry; it may not invent missing cone members or add new facts during replay.

## Disposition replay completeness

For non-`CURRENT` outcomes, replay also verifies the frozen monitor side effects:

- historical orientation preservation
- epistemic-standing non-mutation
- no automatic reorientation
- zero authority effect
- execution blocking
- no repair attempt

`CURRENT`, `SUSPENDED`, and `WITHDRAWN` remain lawful typed outcomes; constitutional negative outcomes are not software errors.

## Closure invariants

- replay may verify recorded geometry; it may not invent missing cone members
- `UNRESOLVED != FAIL != PASS`
- replay may reconstruct lifecycle disposition; it may not alter it
- stale prior orientation binding is a replay failure
- prior object identity must match delta object identity
- noncanonical bytes cannot satisfy digest conformance
- correct digest + wrong disposition is nonconformant
- correct disposition + altered cone is nonconformant
- repair attempted => qualification blocked
- encoding/rule identity drift => qualification blocked

## Static battery

Run:

```bash
python adversarial_replay_battery.py
```

The battery includes: valid control, correct digest/wrong disposition, correct disposition/altered cone, noncanonical bytes, stale prior witness, unresolved coerced to withdrawn, missing input binding, repair attempt, encoding-version drift, unresolved-dependency drift, and prior-object mismatch.

No fixture loader, runtime runner, execution qualification gate, admission, authority mutation, or execution action is included in this package.
