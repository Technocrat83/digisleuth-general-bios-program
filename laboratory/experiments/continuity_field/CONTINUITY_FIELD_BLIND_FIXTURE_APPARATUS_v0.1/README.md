# Continuity Field Blind Fixture Apparatus v0.1

Status: **materialized, unexecuted, quarantined**.

This package implements the frozen boundary:

`hidden fixture -> blind serializer -> isolated operator -> residue -> isolated adjudicator -> quarantined report`

It does not contain `CC_F01` through `CC_F12`, expected verdicts, an operational Continuity Field implementation, or authorization to execute the battery.

## Frozen constraints

- A fresh subprocess is required for every fixture.
- Only the harness can read complete fixture objects.
- The operator receives canonical `X_i` bytes and returns uninterpreted `Y_i` bytes.
- The operator never receives fixture identity, ordering, counts, expected results, prior verdicts, aggregate score, or adjudicator feedback.
- Witness authentication is independent and emits only a typed state.
- Battery aggregation occurs only after every chamber adjudication.
- Persistent state requires a separately declared battery and is absent here.

## Materialization map

| Required artifact | Path |
|---|---|
| fixture_schema | `schemas/fixture.schema.json` |
| hidden_fixture_store | `apparatus/hidden_fixture_store.py` |
| blind_serializer | `apparatus/blind_serializer.py` |
| serializer_leakage_audit | `tests/test_serializer_leakage_audit.py` |
| witness_authentication_stub | `apparatus/witness_authentication_stub.py` |
| continuity_field_interface | `apparatus/continuity_field_interface.py` |
| residue_schema | `schemas/residue.schema.json` |
| isolated_adjudicator | `apparatus/isolated_adjudicator.py` |
| conjunctive_predicate_engine | `apparatus/conjunctive_predicate_engine.py` |
| cross_fixture_session_controller | `apparatus/cross_fixture_session_controller.py` |
| quarantine_report_schema | `schemas/quarantine_report.schema.json` |
| executable_conformance_tests | `tests/test_executable_conformance.py` |

`contracts/FROZEN_APPARATUS_CONTRACT_v0.1.json` binds the serializer rules, permitted input surface, reset obligations, and blocked runtime state.

## Candidate extension

`SPECTRAL_GOALPOST_RECONSTRUCTIVE_HELM_PETITION_PROTOCOL_v0.1.md` defines how authenticated external control surfaces may petition—but never directly query—the sealed battery for read-only historical Helm-state reconstruction. Its machine-readable ingress contract is `schemas/reconstructive_helm_petition.schema.json`. The extension is materialized but unexecuted; its SMPTE goalpost battery and interface-plane semantic bindings remain absent.

## Current authority state

```yaml
code_materialization: COMPLETE
fixture_execution: NOT_AUTHORIZED
executable_conformance: UNEVALUATED
scientific_evidence_delta: ZERO
canon_delta: ZERO
track_E_delta: ZERO
PP: HARD_BLOCKED
```
