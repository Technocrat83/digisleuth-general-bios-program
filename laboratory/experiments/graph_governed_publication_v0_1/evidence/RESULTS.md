# Mock verification observations — candidate v0.1

Contract commit: `c47b03411eb33831ef9e8f7ba9a225afab8f2aae`  
Implementation commit: `81cec7539f8c64cad0ca36f3b6c6c37f1b813a6a`

## Observed scope

- 12 original fixture families, expanded prospectively into 34 named cases.
- 34/34 cases matched their registered expectations in the declared mock.
- 34/34 deterministic replays matched ordered traces, decisions, assertions and resource snapshots; run IDs and elapsed wall time were excluded.
- Four intentionally unsafe controls produced CONTRADICTED results: stale authorization at commitment, bypass-port write, governing-file tamper and duplicate publication intent.
- Seven malformed/tampered receipt probes rejected. Six earlier structural rejection probes also rejected.
- Four schema definitions checked. Thirteen contract Git blob identities and seven implementation Git blob identities matched locally computed identities before execution.

## Critical observations

F03-revoke-gap recorded ADMITTED at sequence 2, REVOKE_EFFECTIVE at 5, COMMIT_ATTEMPT at 7 and COMMIT_REJECTED at 8. Independent publication count stayed zero. The unsafe stale-commit control published and was detected as a contradiction.

F04-continue-draft recorded an effective publication lock, rejected publication and completed the exact expected draft revision. The publication store remained unchanged.

F07-lost-ack recorded one publication, lost acknowledgment, reopened the worker connection, reconciled the durable intent identity and returned the existing outcome without a second publication.

F08-unknown-prior-outcome preserved the pending intent and blocked a blind retry while reconciliation was unavailable. A final trusted observation inspected the restored store.

## Interpretation boundaries

SUPPORTED_WITHIN_FIXTURE is a mechanical comparison with the pinned expectations, not independent scientific adjudication. The mock is one trusted Python process with a deterministic serial scheduler. Worker-role access ports model restrictions; they are not OS privilege or filesystem boundaries. The observer reads resource rows independently of monitor verdicts but shares the trusted process/host.

No universal non-bypassability, tamper resistance, isolation, atomicity across actual execution mechanisms, operational drift calibration, actual concurrent race freedom, storage-power-loss durability, or general long-horizon reliability is established.

Kernel properties: REQUIREMENT_UNESTABLISHED. Real boundary cases: NOT_RUN. Production enforcement: NOT_EVALUATED. Certification: NOT_GRANTED. Release: HOLD. Receipts: UNSIGNED.

The original proposal, registry and candidate manifest preserve their NOT_RUN status at preregistration. These later receipts report new mock execution; they do not rewrite the historical baseline or ratify new canonical claims.

## Reproduction

Install the version-pinned validation dependencies in an isolated environment. Run `python implementation/mock_harness.py`, then `python evidence/audit_tools/inspect_mock_run.py` with the schema dependencies on PYTHONPATH. Preserve this evidence snapshot before generating a new run. The dependency pins do not constitute a binary-hash-locked hermetic environment.
