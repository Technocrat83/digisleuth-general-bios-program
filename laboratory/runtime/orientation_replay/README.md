# ORIENTATION_INVALIDATION_REPLAY_VALIDATOR_v0.1

**Class:** ISOLATED_EXECUTION_WITNESS_VERIFICATION_APPARATUS  
**Parent:** JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1 + ORIENTATION LIFECYCLE MONITOR  
**Authority:** VERIFY_BINDING, VERIFY_CANONICAL_DIGEST, VERIFY_LOCALIZATION_RECONSTRUCTION, VERIFY_DISPOSITION_RECONSTRUCTION  
**Zero Authority:** REPAIR_WITNESS, RELOCALIZE_WITH_NEW_FACTS, REORIENT_OBJECT, MUTATE_AUTHORITY, MUTATE_TOPOLOGY, TRIGGER_EXECUTION  
**PP:** BLOCKED

## Constitutional ordering

`Replay Semantics -> Replay Validator -> Fixture Loader -> Runtime Runner -> G_orientation_exec_qual`

The replay validator verifies that a recorded invalidation witness corresponds to the exact observed delta and prior orientation witness under frozen localization and monitor semantics. It never defines those semantics retrospectively.

## Replay result vector

`Replay(W_I, Delta_obs) = <IdentityMatch, DigestMatch, LocalizationMatch, DispositionMatch>`

Each coordinate is typed independently:

- `INPUT_BINDING: PASS | FAIL | UNRESOLVED`
- `DIGEST_BINDING: PASS | FAIL`
- `LOCALIZATION_RECONSTRUCTION: PASS | FAIL | UNRESOLVED`
- `DISPOSITION_RECONSTRUCTION: PASS | FAIL | UNRESOLVED`
- `REPAIR_ATTEMPTED: FALSE`

Qualification requires all four coordinates to be `PASS`.

A matching digest does not compensate for a wrong cone or wrong lifecycle disposition.

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

## Closure invariants

- replay may verify recorded geometry; it may not invent missing cone members
- `UNRESOLVED != FAIL != PASS`
- replay may reconstruct lifecycle disposition; it may not alter it
- stale prior orientation binding is a replay failure
- noncanonical bytes cannot satisfy digest conformance
- correct digest + wrong disposition is nonconformant
- correct disposition + altered cone is nonconformant

## Static battery

Run:

```bash
python adversarial_replay_battery.py
```

The battery includes: valid control, correct digest/wrong disposition, correct disposition/altered cone, noncanonical bytes, stale prior witness, unresolved coerced to withdrawn, and missing input binding.

No fixture loader, runtime runner, execution qualification gate, admission, authority mutation, or execution action is included in this package.
