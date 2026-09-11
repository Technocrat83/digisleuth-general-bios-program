# GENERATIVE_UX_JURISDICTION_EXPERIMENT_01 — Stage 2 Runtime Binding v0.1

**CLASSIFICATION:** Project Gamma / Experimental Runtime Precommit  
**STATUS:** RUNTIME_ARCHITECTURE_BOUND • EXECUTION_BLOCKED • HYPOTHESIS_LOCKED_UNPROVEN  
**EXPERIMENT:** `GENERATIVE_UX_JURISDICTION_EXPERIMENT_01`  
**STAGE:** `STAGE_2_RUNTIME_BINDING`  
**PP:** BLOCKED  
**CANON_DELTA:** ZERO  
**EVIDENCE_DELTA:** ZERO

## Governing Boundary

```text
Runtime Specification != Authenticated Runtime Binding != Execution Authority
```

```text
Provider Snapshot Exists != Account Access Authenticated
```

```text
Shared Model Substrate != Shared Evaluator Jurisdiction
```

```text
Frontier Novelty < Authenticated Experimental Identity
```

No candidate generation, evaluator invocation, BMIMS adjudication, UX claim formation, Canon mutation, or production promotion is authorized by this artifact.

---

## Stage 1 Precommit Identity

```yaml
PRECOMMIT_RESULT:
  schemas: 1
  task_specimens: 8
  hashed_artifacts: 10
  structural_validation: PASS

  artifact_set_sha256: 9fe99a62375078a27e81851ddbc65cf862ff437aee94c560f2c1e07325df68e9
  manifest_sha256: 3eea11ebc7e902b6796059366226d51455e72b748792de1a3aff128adece287a
  container_sha256: 2a11fbe5a682d21c5168711a10a5cf5ad678f29a36ea2dde413ad343ac8741b5

  EXECUTION: BLOCKED
  GENERATION: PROHIBITED
  EVALUATION: PROHIBITED
  SCIENTIFIC_STATUS: HYPOTHESIS_LOCKED_UNPROVEN
  CANON_DELTA: ZERO
  PP: BLOCKED
```

The manifest excludes itself from its payload identity to avoid circular identity. Any mutation to the sealed schema, fixtures, or precommit record requires a version increment, new hashes, and a fresh experimental run identity.

---

## Founder Architectural Assignments

```yaml
FOUNDER_ARCHITECTURAL_ASSIGNMENTS:
  provider: OPENAI_API

  generation_model:
    model_id: gpt-5.5-2026-04-23
    endpoint: /v1/responses
    reasoning_effort: medium
    role: CANDIDATE_PHENOTYPE_GENERATOR

  evaluator_model_allocation:
    E_S:
      model_id: gpt-5.4-mini-2026-03-17
      reasoning_effort: low
    E_O:
      model_id: gpt-5.4-mini-2026-03-17
      reasoning_effort: medium
    E_J:
      model_id: gpt-5.4-mini-2026-03-17
      reasoning_effort: medium
    E_M:
      model_id: gpt-5.4-mini-2026-03-17
      reasoning_effort: low
    E_P:
      runtime: BMIMS
      model_judge: PROHIBITED_AS_SUBSTITUTE
      external_model_allocation: NONE

  maximum_experimental_spend:
    currency: USD
    hard_ceiling: 250.00
    ceiling_scope:
      - generation
      - evaluator_invocations
      - permitted_retries
    bmims_local_compute: TRACKED_SEPARATELY
    ceiling_overrun: PROHIBITED
```

### Run 01 Model Selection Law

`GPT-6 Astra` is not bound to Run 01 because the current architectural assignment requires immutable snapshot identity. Run 01 binds the date-stamped `gpt-5.5-2026-04-23` snapshot instead.

```text
Frontier Novelty < Authenticated Experimental Identity
```

Prospective GPT-6 Astra use is reserved for a distinct future replication and may not inherit Run 01 identity, evidence, or conclusions.

```yaml
PROSPECTIVE_REPLICATION:
  experiment_id: GENERATIVE_UX_JURISDICTION_EXPERIMENT_02
  trigger: DATE_STAMPED_GPT_6_ASTRA_SNAPSHOT_AVAILABLE
  standing: NOT_YET_GENESIZED
  inheritance:
    may_inherit:
      - experimental_design
      - specimen_classes
      - evaluator_contracts
    may_not_inherit:
      - Run_01_identity
      - evidence
      - conclusions
```

---

## Evaluator Jurisdiction Allocation

All four non-BMIMS evaluators may share the same model substrate because their jurisdictions remain separated by exact instruction digests, disjoint permitted-input manifests, evaluator-specific output schemas, hidden cross-evaluator results, and independent deficiency records.

```text
Shared Model Substrate != Shared Evaluator Jurisdiction
```

Run 01 records the following limitation:

```yaml
shared_model_correlation:
  status: RECORDED_LIMITATION
  limitation: RUN_01_CANNOT_ESTABLISH_EVALUATOR_INDEPENDENCE_ACROSS_MODEL_FAMILIES
```

`E_P` remains bound to BMIMS. External model judgment is prohibited as a substitute for BMIMS perceptual conformance evaluation.

---

## Execution Scale

```yaml
EXECUTION_SCALE:
  specimens: 8
  conditions: 7
  cells: 56

  replay_regime:
    repetitions_per_cell: 3
    total_calls: 168

  sampling_regime:
    repetitions_per_cell: 10
    total_calls: 560

  total_generation_calls: 728
```

Replay and sampling remain distinct regimes:

```text
R_replay != R_sampling
```

Replay measures observed stability under recorded provider conditions. It does not imply mathematical determinism.

---

## Budget Envelope

```yaml
EXPERIMENT_BUDGET_ENVELOPE:
  hard_ceiling_usd: 250.00

  thresholds:
    warning:
      fraction: 0.80
      amount_usd: 200.00
      effect: EMIT_CEILING_WARNING

    admission_stop:
      fraction: 0.95
      amount_usd: 237.50
      effect: PROHIBIT_NEW_CELL_ADMISSION

    terminal_stop:
      fraction: 1.00
      amount_usd: 250.00
      effect: HALT_ALL_PROVIDER_INVOCATIONS

  accounting:
    use_provider_reported_usage: true
    estimate_before_each_call: true
    charge_failed_billable_calls: true
    charge_retries: true
    infer_missing_usage: prohibited
    missing_usage_action: HALT_AND_RECONCILE

  non_implications:
    - UNUSED_BUDGET_DOES_NOT_AUTHORIZE_MORE_CALLS
    - BUDGET_AVAILABILITY_DOES_NOT_AUTHORIZE_EXECUTION
    - COST_COMPLETION_DOES_NOT_IMPLY_EXPERIMENT_COMPLETION
```

The USD 250.00 ceiling is a governance limit, not a forecast of expected spend.

```text
Unused Budget != Additional Experimental Authority
Spend Capacity != Execution Permission
```

BMIMS local compute is tracked separately and does not increase provider-spend authority.

---

## Runtime Identity Vector

Runtime identity is preserved as a vector rather than flattened to a model-name scalar.

```text
M = <provider, endpoint, model ID, snapshot, API version, region, request schema>
```

```yaml
RUNTIME_IDENTITY_VECTOR:
  provider: OpenAI
  endpoint: /v1/responses

  generation_model_id: gpt-5.5
  generation_snapshot: gpt-5.5-2026-04-23

  evaluator_model_id: gpt-5.4-mini
  evaluator_snapshot: gpt-5.4-mini-2026-03-17

  region: DEFAULT_PROVIDER_PROCESSING
  request_schema_digest: PENDING_SERIALIZATION
  system_instruction_digests: PENDING_SERIALIZATION
  account_model_access: PENDING_LIVE_AUTHENTICATION
  provider_rate_limit_tier: PENDING_LIVE_AUTHENTICATION
```

A floating alias is insufficient for final Stage 2 closure when an immutable snapshot is required and available. Where a provider exposes only a floating identifier, the limitation must be recorded rather than synthetically repaired.

---

## Instruction Identity Requirement

System instructions must be serialized as exact UTF-8 byte surfaces and referred to by digest.

```text
H_system = SHA256(exact system-instruction bytes)
```

Pending instruction surfaces include:

```yaml
instruction_surfaces:
  generation_system_instruction_bytes: PENDING_SERIALIZATION
  E_S_system_instruction_bytes: PENDING_SERIALIZATION
  E_O_system_instruction_bytes: PENDING_SERIALIZATION
  E_J_system_instruction_bytes: PENDING_SERIALIZATION
  E_M_system_instruction_bytes: PENDING_SERIALIZATION
```

No digest may be declared before its exact corresponding byte surface exists.

---

## Replay and Sampling Semantics

```yaml
replay_regime:
  repetitions_per_cell: 3
  requested_seed: UNBOUND
  deterministic_guarantee: UNESTABLISHED
  interpretation: >
    Measures observed replay stability under recorded provider conditions;
    it does not assume mathematical determinism.
```

If the selected provider/model endpoint does not expose seed control:

```yaml
sampling_regime:
  repetitions_per_cell: 10
  seed_control: PROVIDER_UNAVAILABLE
  surrogate_identity:
    - provider_request_id
    - request_timestamp
    - response_digest
  limitation: RECORDED_WITHOUT_SYNTHETIC_REPAIR
```

Provider request identifiers are observational identities only. They are not substitutes for seed semantics.

---

## Cross-Stage Non-Interference

```yaml
cross_stage_non_interference:
  specimen_corpus_may_be_read: true
  specimen_corpus_may_be_mutated: false

  evaluators_may_be_defined: true
  evaluators_may_execute: false

  compiler_may_be_serialized: true
  compiler_may_emit_generation_packets: false

  runtime_may_be_declared: true
  runtime_may_be_invoked: false
```

```text
Observed Outcome !-> Retroactive Evaluation Mutation
```

```text
Instrument Deficiency Detection != Instrument Repair Authority Within Run
```

---

## Remaining Stage 2 Blockers

```yaml
STAGE_2_CLOSURE_DECISION:
  runtime_manifest_serialization: AUTHORIZED
  final_stage_2_seal: BLOCKED_PENDING_AUTHENTICATED_BINDINGS
  execution_permission: NOT_GRANTED
  candidate_generation: PROHIBITED
  evidence_delta: ZERO
  canon_delta: ZERO
  pp: BLOCKED

  unresolved_runtime_facts:
    - account_model_access
    - provider_rate_limit_tier
    - exact_request_schema_bytes
    - request_schema_digest
    - exact_generation_system_instruction_bytes
    - exact_evaluator_system_instruction_bytes
    - system_instruction_digests
    - provider_seed_semantics_for_bound_endpoint_and_snapshots
    - final_runtime_metadata_capture_contract
```

---

## Next Lawful Frontier

```text
SERIALIZE_AND_PRECOMMIT:
  E_S
  E_O
  E_J
  E_M
  CONDITION_PACKET_COMPILER
  BLIND_ADJUDICATION_PROTOCOL
  RUNTIME_AND_SAMPLING_MANIFEST
```

Then authenticate live account/runtime facts, serialize exact request and instruction bytes, calculate their digests, and only thereafter determine Stage 2 seal eligibility.

```text
NOT AUTHORIZED:
  CANDIDATE GENERATION
  EVALUATOR EXECUTION
  BMIMS ADJUDICATION
  UX CLAIM FORMATION
  CANON MUTATION
  PRODUCTION PROMOTION
```

## Terminal State

```yaml
GATE_DELTA:
  provider: RESOLVED_ARCHITECTURALLY
  generation_model: RESOLVED_ARCHITECTURALLY
  evaluator_allocation: RESOLVED_ARCHITECTURALLY
  spend_ceiling: RESOLVED_ARCHITECTURALLY

  runtime_access_authentication: PENDING
  request_schema_digest: PENDING
  system_instruction_digests: PENDING
  stage_2_seal: BLOCKED
  execution_authority: NOT_GRANTED
  evidence_delta: ZERO
  canon_delta: ZERO
  pp: BLOCKED
```

**Controlling law:** architectural binding may advance while scientific evidence remains immobile.
