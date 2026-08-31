# GENERAL_BIOS_KMR_ADVERSARIAL_EXECUTABLE_HARNESS_v0.1

Status: **MATERIALIZED_UNEXECUTED**

Jurisdiction: implementation standing only.

This package materializes the six frozen adversarial KMR harnesses over one common transactional HCET runtime. It does not execute A1-A6 and does not create scientific evidence.

Boundary:

Battery Specification != Harness Materialization != Execution != Scientific Evidence

Shared runtime responsibilities:
- deterministic serialization and hashing
- raw contract capture surface
- staged transactional mutation
- atomic rollback
- typed rejection reasons
- graph / authority / effective-authority / standing deltas
- exact newly-appended provenance parent validation
- verdict serialization

Chamber injectors:
- A1 mixed-contract atomicity
- A2 effective-authority laundering
- A3 provenance discontinuity
- A4 transform-order sensitivity
- A5 idempotence and replay pressure
- A6 epistemic-standing laundering

A4 remains discriminative: its verdict domain is
DETERMINISTIC_COMMUTATIVE_PASS or ORDER_DEPENDENCY_DETECTED.

No chamber is called on import. Execution authority remains zero pending harness conformance.

Canon delta: 0
Physiology delta: 0
Level-0 delta: 0
PP: BLOCKED
