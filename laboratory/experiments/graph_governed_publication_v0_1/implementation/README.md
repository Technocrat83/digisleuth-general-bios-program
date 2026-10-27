# Deterministic mock implementation

This implementation consumes the separately anchored contract candidate. It is a prospective model, not a recovered BIOS runtime and not an implementation of an operating-system reference monitor.

The model uses a finite typed graph match, actor/parent grants, exact approval and synthetic evidence digests, budgets, scoped locks, and synthetic drift thresholds. Admission and final commitment are separate scheduler steps. Final predicates, publication rows, stable intent identity and budget consumption share one `BEGIN IMMEDIATE` SQLite transaction. Revocations and locks use the same store. F03 places those control events between admission and commitment.

Queued and delegated paths use the model admission function. Direct/indirect/retained-handle and tamper attempts address explicit model ports which deny access. This models role restrictions; the Python host could bypass them. Process isolation, filesystem ACLs, privilege separation, alternative real interfaces, hostile workers, actual simultaneous threads, external service atomicity, and universal race freedom are NOT_EVALUATED. SQLite serialization in a single-process deterministic scheduler is not independent proof of those properties.

The observer opens a separate read-only SQL connection, inspects publication and identity rows, and reads governing/draft bytes. It does not infer protected effects from decision logs. It shares the trusted controller process and host; that independence limit is carried in every result. Governing file hashes cover pinned policy/evidence/threshold/graph records. F10 additionally compares actual authority/control table rows so a fake governing-file check cannot substitute for authority-state inspection.

Restart closes and reopens the SQLite connection and reloads a persisted worker checkpoint. It models worker restart, not host power loss or durability under storage failure. Sink unavailability is fault injection during worker reconciliation; the trusted observer inspects the restored sink at the end. Unknown outcomes remain pending and block retries.

`observer.py` evaluates predeclared expectations from independent resource reads. Optional intentionally unsafe model variants exercise stale commitment, bypass, tamper, and duplicate-intent defects; their expected diagnostic result is CONTRADICTED. They are excluded from the normal suite counts and never change fixture expectations.

Replay equivalence compares ordered events, decisions, assertions and effect snapshots. Wall-clock elapsed time and run identifier are excluded. No model provider is called. The graph rules cover this finite specimen, not arbitrary plans or a general best-fit optimizer. Synthetic drift thresholds have no operational calibration claim.

Run `python implementation/mock_harness.py` only after `evidence/implementation_binding.json` binds the contract and exact implementation commit. Output is under `evidence/mock_run`. Validate receipts with `validation/validate_contract.py`; schema validation additionally needs the pinned validation dependencies. No scientific adjudication, certification, release, production authority, or established Kernel property follows from this mock.
