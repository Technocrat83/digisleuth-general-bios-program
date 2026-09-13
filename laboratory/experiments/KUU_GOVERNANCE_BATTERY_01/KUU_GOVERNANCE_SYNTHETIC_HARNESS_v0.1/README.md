# KUU_GOVERNANCE_SYNTHETIC_HARNESS_v0.1

Synthetic reference-conformance harness only.

## Master non-equivalence
`Synthetic Oracle Agreement != Scientific Validation`

## Frozen separation
`Fixture Generator != Binding Evaluator != Epistemic Classifier != Operation Eligibility Evaluator != Oracle Comparator != Residue Ledger`

## Runtime state domains
- BindingState = {BOUND, UNBOUND}
- EpistemicState = {KNOWN, UNKNOWN, CONTRADICTED, NOT_APPLICABLE}
- EligibilityState = {ELIGIBLE, INELIGIBLE_BINDING, INELIGIBLE_EPISTEMIC, INELIGIBLE_AUTHORITY}

`UNBOUND` is produced only by binding evaluation. Epistemic classification of an unbound referent is `NOT_APPLICABLE`.

## Blind oracle
Runtime fixture payloads carry opaque UUID identities and contain no target law, expected verdict, expected refusal reason, or pass/fail condition.
Oracle records are external to the runtime surface and bound to exact fixture bytes by SHA-256.

## Standing ceiling
Even PASS_KUU establishes only:
`KUU_REFERENCE_RUNTIME_CONFORMS_UNDER_SYNTHETIC_BATTERY`

Scientific validation, Canon standing, physiology inference, Level-0 mutation, and PP remain zero/blocked.
