# KMR_A4_SEQUENTIAL_PROVENANCE_BINDING_SPEC_v0.1

REGISTRY_ACTION: RESOLVE_A4_SEQUENTIAL_PROVENANCE_BINDING

PARENT: KMR_ADVERSARIAL_HARNESS_CONFORMANCE_ADJUDICATION_v0.1

TARGET_CHAMBER: KMR_A4_TRANSFORM_ORDER_SENSITIVITY

DEFICIENCY: STALE_INTERMEDIATE_PARENT_DIGEST

## Jurisdictional localization

A4 is the sole affected chamber. A1, A2, A3, A5, and A6 retain their prior conformance/readiness standing. No execution authority is granted by this repair.

The repair is upstream and mechanical:

- T1.parent_digest = H(K0)
- APPLY T1 -> K1
- T2.parent_digest = H(K1)
- APPLY T2 -> K2

For beta:

- T1'.parent_digest = H(K0)
- APPLY T1' -> K1'
- T2'.parent_digest = H(K1')
- APPLY T2' -> K2_beta

The prohibited stale pattern is T2.parent_digest = H(K0).

## Required capture

- H(K0)
- H(K1)
- H(K1_prime)
- H(K2_alpha)
- H(K2_beta)
- INTERMEDIATE_CONFORMANCE_ALPHA
- INTERMEDIATE_CONFORMANCE_BETA
- TERMINAL_DIGEST_COMPARISON

## Prohibited repairs

- REUSE_GENESIS_DIGEST_FOR_STEP_2
- BYPASS_PARENT_VALIDATION
- DISABLE_PROVENANCE_CHECK_FOR_A4
- REWRITE_SHARED_RUNTIME_RULES
- MODIFY_A4_EXPECTED_OUTCOME

## Non-forcing scientific verdict domain

A4 remains discriminative. If both sequential paths are independently provenance-valid and all intermediate states conform:

- equal terminal digests -> DETERMINISTIC_COMMUTATIVE_PASS
- unequal terminal digests -> ORDER_DEPENDENCY_DETECTED

Neither verdict is a preregistered success condition. Sequence validity is a precondition for order comparison, not part of the scientific result.

## Resolution gate

A4 may become STRUCTURALLY_READY_UNEXECUTED only when:

1. parent(T1) = H(K0)
2. parent(T2) = H(K1)
3. parent(T1') = H(K0)
4. parent(T2') = H(K1')
5. all intermediate provenance validations pass

If any parent binding fails, A4 remains EXECUTION_SEALED and scientific delta remains zero.

## Authority boundary

Harness Repair = Correct Sequential Binding

Delta Shared Runtime Semantics = 0

STATUS: UPSTREAM_REPAIR_SPECIFICATION_MATERIALIZED
EXECUTION_AUTHORITY: ZERO
SCIENTIFIC_ADJUDICATION_AUTHORITY: ZERO
CANON_DELTA: 0
PHYSIOLOGY_DELTA: 0
LEVEL_0_DELTA: 0
PP: BLOCKED
