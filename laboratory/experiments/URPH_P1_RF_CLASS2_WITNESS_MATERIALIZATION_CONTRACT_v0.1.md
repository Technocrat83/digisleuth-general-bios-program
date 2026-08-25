# URPH_P1_RF_CLASS2_WITNESS_MATERIALIZATION_CONTRACT_v0.1

**PROGRAM:** General BIOS / Universal Runtime Pressure Hypothesis (URPH) Phase 1 — Resource Finitude  
**CLASSIFICATION:** EXPERIMENTAL_INSTRUMENT_CONTRACT • MATERIALIZATION_CONFORMANCE_LAYER  
**JURISDICTION:** INSTRUMENT_MATERIALIZATION_AND_CONFORMANCE_ONLY  
**STANDING:** CONTRACT_SPECIFIED • MATERIALIZATION_AUTHORIZED • BASELINE_BLOCKED  
**EPISTEMIC POSTURE:** PRE_BASELINE • PRE_APPLICABILITY • PRE_INTERVENTION  

---

## Governing Law

> **An instrument must prove that it can preserve epistemic distinctions before its observations may enter the applicability denominator.**

This contract does **not** test Resource Finitude. It tests whether the Class-2 observation apparatus is epistemically competent to participate in the later experiment.

```text
Instrument Conformance
!= Resource Applicability
!= Pressure Standing
!= Universality Standing
```

No result produced under this contract confers scientific standing on URPH, CUC, Computational Physiology, Track E, Canon, or PP.

---

## 1. Materialized Evidence Surfaces

The materialized apparatus SHALL instantiate exactly four resource-scoped raw channels:

```text
L_raw,c
L_raw,m
L_raw,n
L_raw,q
```

and one logically distinct causal-binding surface:

```text
L_bind
```

Conceptually:

```text
L_raw = L_raw,c ⊔ L_raw,m ⊔ L_raw,n ⊔ L_raw,q
```

where `⊔` denotes disjoint union.

The resource classes remain operationally distinct:

```text
Compute Evidence
!= Memory Evidence
!= Transmission Evidence
!= Queue Evidence
```

A unified physical store is permissible only if every event retains a cryptographically authenticated resource-plane identity.

---

## 2. Exact Event Identity

Every event SHALL receive an immutable identity derived from canonical serialized content and provenance.

```text
H(e_l) = SHA256(CanonicalSerialize(e_l))
```

Canonical serialization SHALL itself be frozen by version.

```yaml
serialization:
  schema_id: URPH_P1_RF_CLASS2_DYNAMIC_WITNESS_SCHEMA_v0.1
  serializer_id:
  serializer_version:
  canonicalization_version:

integrity:
  previous_event_digest:
  event_digest:
```

Each raw resource plane SHALL form an append-only digest chain:

```text
H_0 -> H_1 -> H_2 -> ... -> H_n
```

Governing separation:

```text
Hash Integrity != Observation Truth != Causal Standing
```

A perfectly preserved bad observation remains a bad observation.

---

## 3. Resource-Scoped Observer Identity

Each resource observer SHALL possess a frozen conformance identity:

```text
O_r = <observer_id, version, resource_scope, instrumentation_method, capture_contract>
```

with:

```text
Scope(O_r) = R_r
```

A single executable observer MAY emit multiple resource classes, but conformance SHALL be established independently for each plane.

```text
Conformant(O,c) does not imply Conformant(O,m)
```

Observer conformance standing is therefore vector-valued:

```text
C_O = <C_O,c, C_O,m, C_O,n, C_O,q>
```

Implementation convenience SHALL NOT confer cross-resource epistemic authority.

---

## 4. Baseline Capture Epoch Identity

Every future baseline capture SHALL be enclosed within a frozen epoch identity:

```text
E_B = <experiment, cell, run, objective, task_graph, observers,
       resource_configuration, environment, start, terminal, integrity>
```

Materialized form:

```yaml
baseline_capture_epoch:
  experiment_id:
  baseline_epoch_id:
  cell_id:

  substrate_id:
  substrate_version:

  architecture_id:
  architecture_version:

  objective_id:
  objective_version:

  task_graph_id:
  task_graph_version:
  task_graph_digest:

  environment_id:
  environment_version:

  run_id:

  observers:
    compute:
    memory:
    transmission:
    queue:

  resource_plane_configuration:

  capture_start:
  capture_terminal:

  epoch_digest:
```

No event may migrate between epochs because its content appears behaviorally equivalent.

```text
Behavioral Similarity != Epoch Identity
```

---

## 5. Append-Only Raw Ledger Contract

Raw evidence surfaces permit only:

```text
APPEND
READ
VERIFY
```

Historical raw records SHALL NOT support:

```text
UPDATE
DELETE
RECLASSIFY
BACKFILL
```

If an observer later discovers an error, the apparatus SHALL append a contradiction/correction record referencing the original event. The original event survives.

```yaml
observation_correction:
  correction_id:
  baseline_epoch_id:

  target_event_id:
  target_event_digest:

  correction_type:
  reason:

  issuing_observer_id:
  issuing_observer_version:

  evidence_references:

  standing:
    - CORRECTION_ASSERTED
    - CORRECTION_VERIFIED
    - CORRECTION_UNRESOLVED

  previous_correction_digest:
  correction_digest:
```

Governing separation:

```text
Correction != Mutation
Correction Assertion != Correction Verification
```

---

## 6. Binding Ledger Contract

`L_bind` SHALL never copy and mutate raw evidence. It SHALL reference immutable raw-event identities.

```yaml
causal_binding:
  binding_id:
  raw_event_id:
  raw_event_digest:

  experiment_id:
  baseline_epoch_id:
  run_id:

  objective_id:
  task_graph_version:
  task_node_id:

  predecessor_state:
  successor_state:

  resource_class:
  binding_basis:
  evidence_references:

  adjudicator_id:
  adjudicator_version:

  standing:
    - VERIFIED
    - NONCAUSAL
    - UNRESOLVED

  previous_binding_digest:
  binding_digest:
```

Authority law:

```text
L_bind may reference L_raw.
L_bind may not rewrite L_raw.
```

Raw observation and causal interpretation remain distinct historical objects.

---

## 7. Instrumentation Completeness Witness

Instrumentation completeness SHALL be resource-scoped:

```text
W_I,r = <coverage, observer_health, capture_start, capture_end,
         loss_count, integrity>
```

with terminal states:

```text
COMPLETE
INCOMPLETE
CONTRADICTED
```

Machine-readable certificate:

```yaml
instrumentation_completeness:
  experiment_id:
  baseline_epoch_id:
  run_id:
  resource_class:

  observer_id:
  observer_version:

  capture_start_event:
  capture_end_event:

  expected_capture_scope:
  observed_capture_scope:

  dropped_event_count:
  sequence_gap_count:
  observer_fault_count:

  integrity_chain_valid:

  standing:
    - COMPLETE
    - INCOMPLETE
    - CONTRADICTED

  evidence_references:
  adjudicator_id:
  integrity_digest:
```

The observer SHALL NOT grant itself `COMPLETE`.

```text
Capture Authority != Completeness Adjudication Authority
```

If no qualifying resource event exists and `W_I,r != COMPLETE`, the only lawful applicability-relevant outcome is `UNRESOLVED`.

```text
No Recorded Event != Verified Zero Consumption
```

`CONTRADICTED` SHALL trigger a resource-local `INSTRUMENTATION_INTEGRITY_HALT_r`. No downstream repair is authorized.

---

## 8. Adversarial Instrument Conformance Battery

Before any real baseline cell may be admitted, the instrumentation system SHALL survive the preregistered battery:

```text
T_I = {T_0, T_OC, T_NC, T_U, T_G, T_C, T_X}
```

### T_0 — Clean Objective-Causal Event

Fixture truth: a known resource event is structurally required for the next task transition.

Required binding outcome:

```text
VERIFIED
```

Purpose: prove positive causal detection.

### T_OC — Observer-Labelled Causal, Actually Noncausal

Raw observer annotation:

```yaml
causal_class_declared_by_observer: OBJECTIVE_CAUSAL
```

Frozen task graph establishes no dependency.

Required binding outcome:

```text
NONCAUSAL
```

Governing law:

```text
Observer Annotation != Causal Standing
```

### T_NC — Background Resource Activity

Fixture produces authentic resource consumption unrelated to the objective.

Required behavior:

```text
Raw ledger: PRESERVE
Binding ledger: NONCAUSAL
```

Governing law:

```text
Resource Was Traversed does not imply Objective Traversed Resource
```

### T_U — Ambiguous Binding

Fixture produces authentic resource traversal whose task-graph relation cannot be established.

Required outcome:

```text
UNRESOLVED
```

Any forced conversion into `VERIFIED` or `NONCAUSAL` fails the instrument.

First-class instrument law:

> **Forced certainty is instrumentation failure.**

### T_G — Capture Gap

Fixture deliberately removes or drops part of one resource stream.

Required resource-local outcome:

```text
W_I,r = INCOMPLETE
```

Other resource planes remain independently adjudicated.

```text
W_I,m = INCOMPLETE does not imply W_I,c = INCOMPLETE
```

### T_C — Integrity Contradiction

Fixture introduces an invalid hash link, impossible sequence order, or observer-state contradiction.

Required outcome:

```text
W_I,r = CONTRADICTED
INSTRUMENTATION_INTEGRITY_HALT_r
```

No downstream repair.

### T_X — Pressure-Semantic Contamination

Fixture may contain native resource availability, capacity, quota, or utilization metadata. Class-2 processing SHALL refuse to derive:

```text
usage / capacity
pressure
scarcity
saturation
distance_to_limit
```

Required outcome:

```text
PRESSURE_SEMANTIC_ABSTENTION
```

Governing law:

```text
Data Availability != Interpretation Authority
Queue Traversal != Queue Pressure
Resource Traversal != Resource Scarcity
```

---

## 9. Non-Compensatory Conformance

Instrument conformance is Boolean-conjunctive and non-compensatory:

```text
PASS_I = AND_j PASS(T_j)
```

No weighted score, average, compensation rule, or threshold substitution is permitted.

In particular:

```text
T_U = FAIL -> NO_BASELINE_AUTHORIZATION
```

Six passing chambers cannot repair one epistemically broken chamber.

---

## 10. Blinded Fixture / Oracle Separation

Fixture knowledge SHALL NOT leak into the adjudicator.

The fixture generator MAY know ground truth. The binding adjudicator SHALL receive only the evidence surfaces that would be available during a future baseline run.

```text
Fixture Ground Truth Authority != Adjudication Authority
```

The conformance oracle compares emitted outcomes against fixture truth only after the adjudicator has committed its result.

```text
Ground Truth Generator -/-> Binding Adjudicator
```

This is required to prevent the battery from testing answer-key recognition instead of evidence discrimination.

---

## 11. Authority Topology

The lawful authority chain is:

```text
Fixture Generator / Ground Truth
              ||
Observer
  -> L_raw,r
  -> Integrity / Completeness Checker
  -> W_I,r
  -> Binding Adjudicator
  -> L_bind
  -> Applicability Adjudicator
  -> W_A
  -> Pressure Eligibility
```

Every arrow is unidirectional.

Explicit separation:

```text
Observer
!= Completeness Authority
!= Causal Authority
!= Applicability Authority
!= Pressure Authority
```

The independent conformance oracle may adjudicate the instrument battery, but it possesses no applicability, pressure, universality, Canon, or PP authority.

---

## 12. Materialization Exit Vector

Define:

```text
M_I = <M_1,M_2,M_3,M_4,M_5,M_6,M_7,M_8,M_9>
```

where:

```text
M_1 = event schemas instantiate exactly
M_2 = append-only integrity survives mutation attempts
M_3 = W_I,r remains resource-local
M_4 = VERIFIED / NONCAUSAL / UNRESOLVED discriminate correctly
M_5 = raw and binding ledgers cannot cross-write
M_6 = task-graph version identity is enforced
M_7 = pressure-semantic derivations are rejected
M_8 = all adversarial fixtures pass non-compensatorily
M_9 = fixture ground truth cannot leak into the adjudicator
```

Baseline materialization eligibility requires:

```text
M_I = <1,1,1,1,1,1,1,1,1>
```

Only then:

```text
INSTRUMENTATION_CONFORMANT
-> BASELINE_MATERIALIZATION_ELIGIBLE
```

This transition does **not** imply:

```text
RESOURCE_APPLICABLE
URPH_SUPPORTED
CUC_SUPPORTED
COMPUTATIONAL_PHYSIOLOGY_SUPPORTED
CANON_ADMISSION
PP
```

---

## 13. Frozen Scientific Sequence

```text
Theory
-> Schema
-> Instrument
-> Falsify Instrument
-> Observe Baseline
-> Establish Applicability
-> Manipulate Resource
-> Test Pressure
```

No arrow may be traversed backward.

No downstream stage may repair an upstream deficiency.

---

## 14. Exit State and Scientific Delta

Current state:

```text
CONTRACT_SPECIFIED
MATERIALIZATION_AUTHORIZED
BASELINE_BLOCKED
```

Scientific deltas:

```text
Delta URPH   = 0
Delta CUC    = 0
Delta CP     = 0
Delta TrackE = 0
Delta Canon  = 0
Delta PP     = 0
PP           = BLOCKED
```

No resource has earned applicability standing. No Resource Finitude coordinate has earned scientific standing. No universality inference is authorized.

The sole lawful next activity is **physical Class-2 instrument materialization followed by execution of the preregistered adversarial conformance battery `T_I`**.

---

## Constitutional Fence

> **Git persistence is lineage preservation, not scientific admission.**

```text
Git Commit
!= Experimental Pass
!= Resource Applicability
!= Scientific Standing
!= Canon Admission
!= PP
```

The research program does not ask its instruments to be trusted. It requires them to earn the right to observe.
