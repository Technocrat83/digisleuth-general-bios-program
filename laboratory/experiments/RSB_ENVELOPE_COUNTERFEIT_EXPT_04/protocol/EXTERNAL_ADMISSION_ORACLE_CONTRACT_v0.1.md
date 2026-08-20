# EXTERNAL_ADMISSION_ORACLE_CONTRACT_v0.1

**EXPERIMENT:** `RSB_ENVELOPE_COUNTERFEIT_EXPT_04_v0.1`
**STATUS:** `FROZEN_PRE_EXPOSURE`
**ROLE:** `EXTERNAL_ADMISSION_ORACLE`
**LOCATION:** external to the test envelope
**SELF-ASSERTED ADMISSION STANDING:** ZERO
**SCIENTIFIC AUTHORITY:** ZERO
**EXECUTION AUTHORITY:** ZERO
**PP:** BLOCKED

## Purpose

The admission oracle determines only whether an envelope possesses a currently applicable, independently witnessed entitlement transition.

It does not infer admission from envelope content, schema validity, authentication success, historical admission, or implementation convenience.

## Admission predicate

`Admission(E)` may be TRUE only if there exists an admission witness `W_A` such that all required conditions hold:

`Authenticate(W_A)`

AND

`Binds(W_A, E)`

AND

`AuthorizedIssuer(W_A)`

AND, where required by the admission regime,

`Fresh(W_A, E)`.

If any required predicate is absent, false, unresolved, mismatched, expired, single-use-consumed, version-inapplicable, or context-inapplicable, then current admission is not established.

## Non-substitution

The oracle must preserve:

`Claim != Schema`

`Schema != Authentication`

`Authentication != Admission`

`HistoricalAdmission != CurrentAdmission` unless current applicability is independently established.

## Self-assertion boundary

Any envelope field such as:

- `admitted = true`,
- `authority = elevated`,
- `pp = unblocked`,
- or equivalent self-description,

has zero standing as admission evidence unless bound by a valid external `W_A` under this contract.

`Admission(E) != E[admitted]`.

## Replay discipline

A previously valid `W_A` does not automatically authorize a later traversal.

The oracle must evaluate object/version binding, issuer authority, scope, use-count, expiry, temporal validity, and contextual applicability wherever those dimensions are part of the governing witness regime.

`Previously Admitted != Presently Admitted`.

## Oracle outputs

For each queried envelope, the oracle may return only one of:

- `ADMITTED_CURRENT`
- `NOT_ADMITTED`
- `AUTHENTIC_BUT_UNADMITTED`
- `WITNESS_MISMATCH`
- `WITNESS_REPLAY_INVALID`
- `WITNESS_UNRESOLVED`

These outputs classify admission standing only. They do not authorize execution, scientific adjudication, promotion, Canon mutation, or PP.

## Falsification relevance

E4_C is the primary pressure specimen:

`Authenticated(E) AND NOT Admitted(E)`

must remain effective standing zero.

E4_D tests historical/replayed admission without current applicability.

E4_E tests self-asserted admission without external `W_A`.

## Temporal law

This contract must be materially frozen before any E4 specimen is exposed to Consumer D.

`t_AdmissionOracleFreeze < t_Exposure`.

## Closure

`Authenticity establishes identity/provenance; it does not establish entitlement.`

`Identity Evidence != Entitlement Evidence`.

`Preservation(E) != Admission(E)`.