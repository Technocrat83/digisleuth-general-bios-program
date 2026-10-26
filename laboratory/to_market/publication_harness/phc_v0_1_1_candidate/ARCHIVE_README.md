---
artifact_id: PHC_PROTOTYPE_EVIDENCE
version: '0.1.1'
date: '2026-10-26'
standing: EXECUTED_LOCAL_MOCK_CANDIDATE_UNPROMOTED
contract_snapshot: BIOS_PUBLICATION_HARNESS_CONTRACT_v0.1_candidate
source_admission: HELD
certification: NOT_ISSUED
production_enforcement: NOT_ESTABLISHED
market_demand: NOT_ESTABLISHED
git_binding: UNBOUND
---

# Publication harness prototype evidence

Observed **12 publication-contract acceptance cases**, using 17 fixture scenarios and 20 runtime attempts in one suite execution. Verdict counts: `{"SUPPORTED_WITHIN_TESTED_SCOPE": 12}`. These are local deterministic specimen findings; certification and production authority are not granted.

The PHC-01 through PHC-12 definitions were extracted from the saved publication harness contract. Its six records are source record, claim-and-evidence map, draft asset, authority record, execution receipt, and disposition. **No equivalence to transformation-experiment envelopes or fixtures is asserted.**

## Start here

- [Positive-control draft](results/positive_control_draft.md)
- [Positive-control six-record package](results/sandbox/PHC-01/positive/attempts/1/package.json)
- [Observer summary](results/observer_summary.json)
- [Acceptance-case receipts](results/case_receipts/)
- [Pre-execution manifest](manifest.json)
- [Contract snapshot](contract/BIOS_PUBLICATION_HARNESS_CONTRACT_v0.1_candidate.md)
- [Frozen source and permission record](inputs/source_record.json)
- [Predefined useful-draft criterion](fixtures/useful_draft_criterion.json)

## Exact bindings

| Artifact | SHA-256 |
|---|---|
| Contract bytes | `76eff70957f4339ab51eea2a29a4695d3d173c83377c87843c1e62998012e749` |
| Implementation path-to-digest map | `f7d45b79ab52bbcfe8e0e49d186ed4f6f0e6e56d1a2f4b9d7ef6bbc93d27c56a` |
| Pre-execution manifest bytes | `9fbf4a5f4a0c02d0591c527e2d7152a43d162a8869ec1c561cd9fa5ccb5a8d88` |
| `schemas/case_receipt.schema.json` | `c4bc40c39a092f90a3f81c5bcf9c3f74b1bb7ae3b9ccbcfcdc29002208133396` |
| `schemas/package.schema.json` | `9850a436307d40ddf8fb5f8090b764f95a351d3ec8192472b1416916f351d8a7` |

The implementation digest hashes a sorted compact JSON map of source paths to their individual SHA-256 values; those files are listed in the manifest. Package component hashes exclude the execution receipt itself. Each complete package has a separate witness for its entire byte stream. The final evidence index also excludes itself to avoid self-reference.

## Source and useful-draft criterion

The source is a prospective UTF-8 serialization of the user's submitted prototype requirements, with a final newline. It is used under the current task's local preparation scope. Attribution is user-submitted, not independently authenticated; admission remains HELD. Some cases append explicitly synthetic perturbations. Private and credential markers are synthetic, and no real service credentials were used.

Before execution, the positive-control criterion required 100–260 words, at least 3 headings, all four curated source claims with resolving quote references, all six delivery records, the permitted local reviewer, LOCAL_REVIEW_ONLY destination, and READY_FOR_REVIEW disposition. This is a structural and source-traceability proxy. **Human usefulness, time savings, and willingness to pay remain unassessed.**

The drafter uses curated claim specifications, exact-quote matching, and a template. Its boilerplate reflects the contract's review and authority rules. It does not perform general semantic verification, source-authenticity assessment, autonomous research, or model-based reasoning.

## Results

| Case | Execution | Verdict | Checks |
|---|---|---|---:|
| PHC-01 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 14 |
| PHC-02 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 24 |
| PHC-03 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 13 |
| PHC-04 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 13 |
| PHC-05 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 13 |
| PHC-06 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 14 |
| PHC-07 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 13 |
| PHC-08 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 13 |
| PHC-09 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 13 |
| PHC-10 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 37 |
| PHC-11 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 35 |
| PHC-12 | EXECUTED | SUPPORTED_WITHIN_TESTED_SCOPE | 13 |

An acceptance case that deliberately provokes a blocked workflow is still an executed case. Final workflow outcome counts across scenarios are `{"BLOCKED": 3, "CEASED": 3, "COMPLETED": 8, "RECOVERED": 3}`. Each receipt distinguishes case execution status from its verdict and links to the actual scenario packages. Failed checks are preserved in the observer summary: `0`.

The baseline contract snapshot retains its original prospective zero counters. This result package is the separate execution record; the frozen contract was not rewritten after the run.

## Observation and costs

The observer ran in a process distinct from the fixture conductor/runtime. It hashed mock effect files before execution, watched filesystem write/create/delete/rename events with Linux inotify, and inspected persisted packages and returned recipient views afterward. Observer queue overflow: `False`. Frozen files unchanged after execution: `True`.

The monitored boundary covers each prepared scenario's local publication sink, protected draft state, source-admission registry, authoritative index, policy, control state, and synthetic credential fixture. It cannot establish the behavior of uninstrumented resources or hostile same-UID code. The revocation fixture establishes a deterministic control-before-decision order; concurrency and interprocess atomicity were not tested.

Suite wall time: 0.130965 seconds. Sum of measured scenario CPU time: 0.075537 seconds. Runtime external-service calls: 0; external-service cost: $0. Host, assistant, preparation, and human-review costs are UNKNOWN_NOT_MEASURED. These timings are not a business cost or productivity estimate.

No mock-publisher writes were observed. Runtime receipt fields identify costs and exceptions as observed at their own finalization point; separate observer receipts add effect evidence afterward. Crash cases preserve the original attempt fragments and identify recovery-authored records and evidence gaps.

## Limits and next evidence

The first specimen v0.1 attempted 17 workflows, but an event-recorder naming error aborted 15 scenarios. Its complete failed-run archive and manifest identity are retained in [history](history/prior_execution.json). This repaired v0.1.1 specimen has new implementation and manifest identities. Across both specimens, there were two suite executions; the first failure is not erased by the repaired result.

- Local fixed-handler permission and privacy checks do not establish production non-bypassability or isolation.
- The observer and runtime share the same OS user and filesystem. Process separation is procedural independence, not an adversarial trust boundary.
- Curated quote matching does not establish the truth of a claim or the quality of open-ended AI verification.
- No live publisher, model API, service account, shared-memory adapter, recurring job, or external destination was exercised.
- Human usefulness, correction burden, review time, market demand, certification, and Git binding remain pending or unestablished.

Next: a human reviews the positive-control draft against the frozen criterion, then a separately scoped implementation can test actual integrations and independently protected effect boundaries. This evidence supports only the declared local specimen and fixtures.

## Replay

Python standard library only. The included schema validator supports only the keywords used by these schemas and rejects unsupported keywords; it is not a general JSON Schema conformance claim.

Keep this observed package intact. For a fresh run, copy the `src/`, `contract/`, and `history/` directories into an empty directory; run `python3 src/prepare_run.py`, then `python3 src/phc_observer.py`, then `python3 src/build_report.py`. The preparer regenerates the source and fixture inputs from its frozen definitions. A new run has new timing and manifest identity; it is not the same historical run.
