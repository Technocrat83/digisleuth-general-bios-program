---
artifact_id: PHC_OBSERVER_COMPLETENESS_REPAIR
version: '0.1.2'
date: '2026-10-26'
standing: EXECUTED_LOCAL_REPAIR_CANDIDATE_UNPROMOTED
defect_id: PHC-10-OBSERVER-01
parent_commit: f36edde767d445524ce4d3ea8e49679b12d7095b
independent_review: OUTSTANDING
source_admission: HELD
publication_authority: WITHHELD
pp_gate: BLOCKED
git_binding: UNBOUND
---

# Publication observer completeness repair

This is a new candidate revision implementing the supplied locked repair specification. The earlier v0.1.1 archive and all its historical receipts are preserved byte-for-byte. The task runtime is unchanged; the observer, frozen acceptance plan, case receipt schema, revision bindings, regression suite, and packaging were revised.

## Locked decision order

1. Bind mandatory scenario IDs to the frozen acceptance plan.
2. Validate the entire result index for duplicate or unexpected scenario IDs before applying any acceptance predicate. Either condition raises a schema violation and aborts aggregation globally, including when one duplicate is unusable.
3. Require exactly one usable, revision-bound result for every mandatory scenario. Missing or unusable mandatory evidence yields UNRESOLVED, with the missing IDs or reasons recorded and acceptance_applied false.
4. Apply the existing case acceptance predicate only after mandatory evidence closure. Complete evidence can still yield CONTRADICTED; completeness does not confer support.

Unassignable or unusable records create an explicit unresolved evidence condition. An index with an unexpected case ID also aborts aggregation. The observer's executable main path records a schema-abort artifact and exits without producing acceptance receipts when aggregation is aborted.

## Frozen mandatory sets

The plan declares 17 mandatory scenario IDs across the publication contract's 12 cases. Its multi-scenario cases are PHC-02 (missing source and missing permission), PHC-10 (revoked, stopped, budget), and PHC-11 (crash after capture, draft, or receipt). These identities are not derived from whatever results happen to arrive.

The publication harness still uses its own six delivery records and PHC-01–PHC-12 namespace. No transformation-experiment equivalence is introduced.

## Observed results

- New candidate workflow execution: 17 scenarios and 20 runtime attempts.
- New candidate case verdicts: `{"SUPPORTED_WITHIN_TESTED_SCOPE": 12}`.
- Producer-side oracle regressions: 64/64 passed; 0 failed.
- Primary PHC-10 omission probes: 3/3 passed, each yielding UNRESOLVED with no PHC-10 acceptance call.
- Omission sweep across every multi-scenario case: 8/8 passed.
- Additional probes cover unusable evidence, duplicate and unexpected IDs, invalid mandatory plans, missing files or traces, wrong revision bindings, unavailable observations, and complete evidence that fails an acceptance predicate.

The regression suite instruments the actual acceptance function. Omission and unusable-evidence probes require zero calls for the affected case; schema-abort probes require zero calls across the entire aggregation. A complete-evidence negative control requires the acceptance function to run and return CONTRADICTED. Probes use copies of result indexes or derivative temporary files. The original observed results and historical receipts remain unchanged.

| Case | Evidence closure | Acceptance applied | Producer verdict |
|---|---|---|---|
| PHC-01 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-02 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-03 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-04 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-05 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-06 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-07 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-08 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-09 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-10 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-11 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |
| PHC-12 | COMPLETE | True | SUPPORTED_WITHIN_TESTED_SCOPE |

The recorded history contains 57 workflow attempts: 17 in the preserved original failed run, 20 in v0.1.1, and 20 in this revision. Oracle regression assessments reuse this revision's records; they add no workflow attempts.

## Exact bindings

| Referent | SHA-256 |
|---|---|
| Publication contract | `76eff70957f4339ab51eea2a29a4695d3d173c83377c87843c1e62998012e749` |
| Repaired implementation path-to-digest map | `f9a1122cbba5f1001e6cb4c9dea2ce2886e69e5073d298948955a071e4d2eed1` |
| Frozen acceptance plan | `faaecb901533d9511fb1ede60d890c8091b4b68185872e4194b9c231edaed750` |
| New manifest bytes | `901de4badc5a98a66329a56ba5ec26b7e4e01afba78374fe62bfeddf42012a95` |
| Preserved v0.1.1 archive | `b8fef1e5ccddcb8097aab21d630d7ddd39d3ee0d1c518cbd2cddaf5229a1e558` |

Each runtime package, case receipt, and repair regression result binds to the repaired implementation and acceptance plan. Both schema digests are recorded in manifest.json and the result bindings. Whole-package witness digests and the final evidence index remain separate to avoid self-reference.

## Review files

- [Frozen repair scope](fixtures/repair_scope.json)
- [Mandatory acceptance plan](fixtures/plan.json)
- [Completeness guard](src/scenario_completeness.py)
- [Observer](src/phc_observer.py)
- [Regression implementation](src/test_scenario_completeness.py)
- [Regression receipts](results/repair_regressions.json)
- [Case receipts](results/case_receipts/)
- [Observer summary](results/observer_summary.json)
- [Preserved history record](history/prior_execution.json)
- [Positive-control draft](results/positive_control_draft.md)

## Scope and standing

These are producer-side local mock results from the same assistant that implemented and audited the earlier specimen. Independent review remains outstanding. No certification, knowledge admission, publication authority, production enforcement, or market demand is established. PP remains BLOCKED.

The observer and runtime still share an OS user. Curated quote matching and template drafting do not establish general factual verification or model reasoning quality. No live publisher, authenticated service, model API, or concurrent interprocess authority race was tested. The positive-control criterion remains a structural and traceability proxy; human usefulness remains unassessed.

External service calls and costs were zero. Observer suite wall time was 0.104746 seconds. Host, assistant, preparation, and human review costs remain UNKNOWN_NOT_MEASURED. Timings are not a business productivity estimate.

## Replay

Keep this evidence package intact. For a fresh run, copy src/, contract/, and history/ into an empty directory. Run `python3 src/prepare_run.py`, `python3 src/phc_observer.py`, `python3 src/test_scenario_completeness.py`, and `python3 src/build_report.py`. A replay has new timing and manifest identities and is a separate execution. Python standard library only; the included schema validator supports only its declared keyword subset.
