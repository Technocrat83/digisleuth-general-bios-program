# GLYPH Constitutive Verification Battery v0.1

## Standing

```yaml
standing: PREREGISTRATION_CANDIDATE
implementation: BOUNDED_REFERENCE_IMPLEMENTED
battery_execution: NOT_EXECUTED
membrane_strict_disconnect: REQUIRED_NOT_YET_TESTED
authority_delta_from_verification: ZERO
```

## Required correction: downstream standing

Admission does not establish execution authority.

```text
CONFORMANCE RECEIPT
    != LOCALIZATION PERMISSION
    != ADMISSION
    != AUTHORITY BINDING
    != SPECIFIC ACTION PERMISSION
    != ACTION
```

A conformance receipt may provide evidence to a localization decision. It confers no localization permission.

## Predicate outcome set

Exactly:

```text
PASS / FAIL / UNKNOWN / ERROR
```

No partial order or lattice structure is asserted.

Outcome-to-standing mapping:

| Outcome | Standing |
|---|---|
| PASS | VERIFIED |
| FAIL | REFUTED |
| UNKNOWN | INDETERMINATE |
| ERROR | INDETERMINATE |

`REFUTED` applies to the specific preservation obligation only. `CONSTITUTIVE_LOSS` requires valid source/evaluator/equivalence bindings sufficient to justify that broader diagnosis.

## Verification-level conditions

The following are not predicate outcomes:

```text
INVALID_CONTRACT
INCOMPLETE_EVALUATION
CONTRACT_BINDING_MISMATCH
INVALID_RECEIPT
STALE_RECEIPT
```

## Six-field residue

```json
{
  "predicate_id": "identity.entity_id",
  "outcome": "PASS",
  "reason_code": "EXACT_MATCH",
  "evidence_binding": {
    "source_value_digest": "<digest>",
    "reconstructed_value_digest": "<digest>",
    "criterion_digest": "<digest>",
    "evaluator_digest": "<digest>"
  },
  "prescribed_disposition": "NONE",
  "standing": "VERIFIED"
}
```

A prescribed disposition is a required response, not proof that an operation was authorized or performed.

## Positive receipt integrity

For receipt body `R_C.body`:

```text
I = SHA256(Serialize_v0.1(R_C.body))
```

The digest is unkeyed and does not authenticate the issuer.

## Scope ceiling

Successful implementation or eventual passage of S01–S18 can establish bounded verifier/harness behavior only. It does not establish transport losslessness, minimality, issuer authentication, production enforcement, or constitutional promotion.
