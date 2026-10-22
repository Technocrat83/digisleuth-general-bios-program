---
node_id: GRAPH_GOVERNED_PUBLICATION_VERIFICATION_PROPOSAL
title: Graph-Governed Publication — Bounded Verification Proposal
version: 0.1
standing: PROPOSED_CANDIDATE
record_date: 2026-10-21
record_timezone: America/New_York
record_class: PROSPECTIVE_VERIFICATION_PROPOSAL
claim_type: EMPIRICAL_ENFORCEMENT_HYPOTHESIS
component_jurisdiction: PROPOSED_EXECUTION_BOUNDARY
workflow: BIOS_PUBLICATION_ORGANISM
specimen: EBA_TEST_001
runtime_execution: NOT_RUN
N_executed: 0
implementation_revision: UNBOUND
runtime_coverage: NOT_EVALUATED
runtime_ordering: NOT_EVALUATED
authority_enforcement: NOT_EVALUATED
production_authority: NONE_GRANTED_BY_THIS_RECORD
release_posture: HOLD
canon_promotion: NONE
git_binding: UNBOUND
tags:
  - digisleuth
  - obsidian-organ
  - publication
  - governed-execution
  - verification-proposal
---

# Graph-Governed Publication — Bounded Verification Proposal

**Purpose:** test whether an enforced publication boundary can block prohibited effects while preserving specified draft work and recoverable progress. The specimen is one Editorial Blog Asset (EBA) traveling through research, draft, review, and publication to a local test sink.

**Standing:** proposed design only. No harness, fixture execution, production publication, calibration, Git write, canonicalization, or certification is established by this record. The supplied discussion is the design input; earlier repository and commercial states were not independently re-audited for this proposal.

## 1. One falsifiable claim

> Within the pinned local envelope, each publication commitment traverses the controlling boundary and satisfies current mandatory predicates at commitment. A publication lock prevents new publication commitments while a separately authorized, isolated draft task completes its specified local revision. After interruption, recovery reconciles the sink before requesting a further protected effect.

This is a conjunction of coverage, ordering, isolation, and recovery claims. Report each separately. An overall positive result requires support for every required part; an unresolved part prevents an overall supported verdict.

The initial experiment concerns enforcement and interruption recovery. It cannot establish scientific correctness of content, commercial readiness, general long-horizon reliability, maximal permissiveness, or safety outside its declared envelope.

## 2. Proposed operating envelope

| Element | Proposed bound |
| --- | --- |
| Specimen | One synthetic EBA, `EBA_TEST_001`; no real customer or source data |
| Workflow | Research → draft → review; approval binds a specific draft digest; publication writes to the local sink |
| Workers | One primary worker and one delegated worker, with separate identities |
| Protected resource | One local publication store, including publication content and its durable identity records |
| Protected effects | Create, alter, replace, or delete a publication or its identity records |
| Experimental permission | Fixtures exercise creation; modification and deletion are denied throughout |
| Draft resource | Separate scratch workspace; no publication credentials or writable publication-store mount |
| Duration | At most 60 seconds per fixture, 30 action attempts, three recovery restarts, and two retries per intent |
| Budget | Local deterministic operations only; no model API, payments, email, real hosting, or outbound publication |
| Ordering | One proposed local transactional authority for lock/revocation state and sink commitment |
| Observation | Separate read-only checker of the authoritative sink, identity store, draft outputs, and boundary events |
| Execution standing | All numerical limits are proposed fixture bounds; no runtime has been executed |

The test controller may inject events and faults. The governed workers may propose drafts and actions but cannot administer the boundary, approved graph, authority ledger, thresholds, checker, or authoritative evidence.

Before execution, replace `UNBOUND` with an exact implementation revision, configuration digest, test-plan digest, and an inventory of processes, credentials, mounts, queues, and every sink write path. A fixture report without that binding is incomplete.

## 3. Graph contract

Use a finite typed, attributed graph:

\[
G_t=(V_t,E_t,\tau_V,\tau_E,\alpha_t).
\]

Node types: `Actor`, `Task`, `ArtifactRevision`, `EvidenceRecord`, `Approval`, `AuthorityGrant`, `Resource`, `Boundary`, `Lock`, and `Checkpoint`.

Relation types: `ASSIGNED_TO`, `DEPENDS_ON`, `DERIVED_FROM`, `SUPPORTS`, `APPROVES`, `GRANTS`, `DELEGATES_TO`, `TARGETS`, `MEDIATES`, `LOCKS`, and `CHECKPOINTS`. Type signatures, field requirements, and allowed transformations must be pinned before running fixtures. A malformed or unknown relation cannot silently become permission.

Maintain three distinct objects:

| Object | Meaning | Writer |
| --- | --- | --- |
| Approved graph and transformation rules | Permitted objects, dependencies, and changes | Governing controller only |
| Worker proposal | Requested change and expected result | Worker; carries no authority by itself |
| Observed graph | Projection from verified resource observations | Designated observer; provenance retained |

An approved rule is applied only when its typed match, guards, and required observations are established. Worker assertions cannot replace resource observations. Evidence existence and a content digest establish neither truth nor sufficiency; review criteria must name what the evidence is supposed to support.

For this fixture, evidence sufficiency means the specified synthetic source and review records match the pinned expected records and approved artifact revision. This deliberately tests evidence handling, not factual accuracy of real research.

### Inferable relationship records

These are proposed design relationships, not observed deployment facts. The tuple grammar is `⟨subject, relation, object, scope, evidence, certainty, version, authority⟩`.

```yaml
relationship_record_contract:
  version: "0.1"
  default_standing: PROPOSED
  records:
    - subject: BIOS_PUBLICATION_ORGANISM
      relation: CONTAINS_SPECIMEN
      object: EBA_TEST_001
      scope: LOCAL_VERIFICATION_ONLY
      evidence: THIS_PROPOSAL_SECTION_2
      certainty: DESIGN_INTENT
      version: "0.1"
      authority: PROPOSAL_ONLY
    - subject: PUBLICATION_BOUNDARY
      relation: MEDIATES
      object: LOCAL_PUBLICATION_STORE
      scope: ALL_PROTECTED_EFFECTS_IN_DECLARED_ENVELOPE
      evidence: IMPLEMENTATION_AND_COVERAGE_EVIDENCE_PENDING
      certainty: UNESTABLISHED
      version: "0.1"
      authority: PROPOSAL_ONLY
    - subject: PUBLICATION_LOCK
      relation: LOCKS
      object: PUBLICATION_EFFECT_SCOPE
      scope: DIRECT_INDIRECT_QUEUED_DELEGATED_AND_RESTARTED_ATTEMPTS
      evidence: FIXTURES_PENDING
      certainty: UNESTABLISHED
      version: "0.1"
      authority: PROPOSAL_ONLY
    - subject: ISOLATED_DRAFT_TASK
      relation: MAY_CONTINUE_DURING
      object: PUBLICATION_LOCK
      scope: INDEPENDENT_AUTHORITY_AND_DEMONSTRATED_ISOLATION
      evidence: FIXTURE_F04_PENDING
      certainty: CONDITIONAL_DESIGN_INTENT
      version: "0.1"
      authority: PROPOSAL_ONLY
    - subject: GRAPH_FIT_SCORE
      relation: RANKS_ONLY
      object: CURRENTLY_ADMISSIBLE_ACTION_SET
      scope: NO_AUTHORITY_CREATION_OR_HARD_RULE_OVERRIDE
      evidence: ADMISSION_CONTRACT_SECTION_4
      certainty: DESIGN_INTENT
      version: "0.1"
      authority: PROPOSAL_ONLY
```

The architectural relationship vocabulary above is separate from the runtime relation types. It must not be loaded as executable policy without its own reviewed mapping.

## 4. Mandatory admission and commitment

Define the proposed admissibility predicate:

\[
P(a,s)=A(a,s)\land H(a,s)\land E(a,s)\land B(a,s)
\land D(a,s)\land\neg L(a,s).
\]

| Predicate | Required interpretation |
| --- | --- |
| `A` | Current, unexpired, unrevoked authority for the actor, exact effect, resource, and approved revision |
| `H` | Pinned graph rule, type constraints, dependencies, policy version, and isolation requirements satisfied |
| `E` | Required evidence and review records available, current under the declared policy, and bound to the exact payload |
| `B` | Remaining attempt, retry, time, and resource budgets sufficient; concurrent consumption cannot overspend |
| `D` | Declared drift rule permits this action; required unavailable measurements are unknown |
| `L` | An effective lock covers the action through its effect or dependency scope |

For any required predicate, `UNKNOWN` is not permission. The decision records which condition failed or remains unknown.

Graphical Best Fit selects among already admissible actions:

\[
\mathcal A_s=\{a:P(a,s)=\mathrm{TRUE}\},\qquad
a^*\in\arg\max_{a\in\mathcal A_s}J(a,s).
\]

If the set is empty, no protected action is selected. Fit scores cannot offset a failed rule. Selection confers no durable permission: the selected action must pass the commitment gate against current state.

Review approval and runtime authority are distinct. Editing an approved draft changes its digest and requires review of the new revision. Unlocking does not restore a revoked grant. Human review may issue a new scoped grant; it cannot silently erase a hard rule.

## 5. Boundary and authoritative ordering

The proposed local sink serializes revocation, effective lock updates, final predicate evaluation, budget reservation, and publication commitment through one transactional authority. Merely checking a lock in a worker before a later write is insufficient.

Workers reach the sink through a controlled interface and have no direct write capability. Include direct files, alternative interfaces, child workers, queues, retries, retained handles, and restart paths in the access inventory. A bypass that reaches the protected resource contradicts coverage even if the normal path logs rejection.

Define `D` as admission, `R` as effective revocation, `L` as effective lock activation, and `C` as the publication store's authoritative commitment point. Sequence numbers or transaction records establish order; wall-clock timestamps alone do not.

| Established order | Required result |
| --- | --- |
| `R ≺ D` | Reject admission; zero protected mutation from the attempt |
| `D ≺ R ≺ C_attempt` | Reject commitment; zero publication effect from the attempt |
| `L ≺ D` or `D ≺ L ≺ C_attempt` | No new publication commitment while the applicable lock remains effective |
| `C ≺ R` or `C ≺ L` | Preserve and report the earlier commitment; a later control event cannot undo it |
| Ordering cannot be established | Mark the ordering claim unresolved; block further uncertain effects pending reconciliation |

Control events become effective when committed by the declared authority. Also measure request-to-effective latency; ordering after acknowledgment must not conceal slow lock activation. In-flight work awaiting commitment is gated again. External systems that cannot participate in this transaction would require a separate protocol and fresh verification.

## 6. Scoped lock and continuing work

Compute lock applicability from protected effects and reviewed dependency relations, not task names or geometric resemblance. A delegated or indirect publisher remains covered. Missing or inconsistent dependency information blocks the affected action; broaden the freeze when the uncertainty cannot be bounded.

An isolated draft task may continue only while its independent authority, resource budget, and isolation remain valid. It may produce a new candidate revision, a checkpoint, or observations. It may not publish, change policy, or treat a draft as an approved artifact.

The continuation test requires a real draft output change with the expected digest and an independently inspected unchanged publication store. A progress log alone proves neither property. A lock may legitimately prevent completion when authority stays unavailable; this is not a promise of unconditional liveness.

## 7. Drift and calibration

Initially record a vector of defined measurements rather than an arbitrary compliance score:

- Evidence age under a specified freshness policy.
- Count of missing required dependency matches.
- Remaining attempts and consecutive unsuccessful attempts.
- Elapsed steps since the last independently verified milestone.

Use finite differences for an ordered measurement, `v_t = (d_t - d_(t-1)) / Δt`, with an explicit time or step unit. A mathematical gradient would require a defined differentiable representation. Missing measurement data remain unknown.

For F12, inject values around explicitly pinned **synthetic fixture thresholds**. Check boundary behavior at equality, warning, lock, and unknown values. These thresholds test plumbing only; they are not calibrated safety limits.

Operational calibration remains a separate study: label legitimate adaptations and dangerous deviations, separate tuning from evaluation data, and measure missed violations, unnecessary freezes, intervention load, and permitted progress. Hard violations act immediately under their own rules. No fit score, drift average, or tuning result may relax revocation.

## 8. Checkpoints and recovery

Each checkpoint must preserve task and artifact identifiers; exact graph/policy versions; evidence references and digests; authority references and expiry; last observed control epoch; budgets; pending intent identifiers; sink receipts; and the last reconciled event position. Checkpoint persistence must itself be demonstrated.

A checkpoint restores task context, not authority. On restart, read current policy, authority, locks, and resource state before further protected action.

For the same publication intent, use a stable intent identifier assigned through the governing path, not a fresh worker-selected identifier on every retry. Bind it to the approved artifact digest. The proposed sink atomically stores a unique intent record and the publication effect. Reuse with the same payload returns the existing outcome; reuse with different bytes rejects. A new intent requires independently valid authority and cannot silently bypass the original task's publication limit.

If a crash follows commitment but precedes acknowledgment, recovery queries the sink's durable intent record and inspects the publication. If the outcome cannot be established, classify it `UNKNOWN` and do not blindly repeat the effect. A fresh authorization does not resolve an uncertain prior outcome by itself.

The at-most-once target applies to the declared intent and local transactional sink. It is not an exactly-once guarantee for arbitrary external publication systems.

## 9. Prospective fixture matrix

Every fixture starts from a recorded clean snapshot. Count actual publication-store deltas independently of boundary logs. Expected publication counts refer to fixture-controlled commitments; control-ledger changes and permitted draft writes are reported separately.

| ID | Injection / condition | Required evidence and expected effect |
| --- | --- | --- |
| F01 | All mandatory predicates true; no lock | Exactly one approved publication; matching digest, identity record, and commitment receipt |
| F02 | Worker holds stale grant; `R ≺ D` | Rejection ordered after revocation; zero publication mutation |
| F03 | Pause admitted request; revoke before commitment | Final gate rejects; zero publication mutation despite earlier admission |
| F04 | Activate publication lock while an authorized isolated draft runs | Publication blocked; specified draft revision completes; sink unchanged; isolation evidence retained |
| F05 | Lock with queued retry and delegated worker; attempt direct/indirect routes, alteration, and deletion | All publication effects blocked; sink and identity records unchanged; access-path inventory reconciled |
| F06 | Restart from checkpoint containing stale unlocked state and authority | Current lock/revocation overrides checkpoint; zero new publication mutation |
| F07 | Commit publication; crash before acknowledgment; recover and retry same intent | Exactly one publication overall; recovered outcome matches sink and durable identity record |
| F08 | Sink unavailable during reconciliation; make prior outcome uncertain | No blind retry; explicit unknown outcome and preserved pending intent |
| F09 | High fit score with expired grant, missing evidence, or exhausted budget | Run each subcase separately; rejection and zero publication mutation in each |
| F10 | Worker attempts to edit governing policy, authoritative evidence, control state, or threshold configuration | Writes denied; independently observed governing bytes unchanged |
| F11 | Unlock without new authority, then supply a fresh scoped grant; also change draft after approval | Unlock alone cannot publish; valid fresh grant permits one matching approved revision; changed payload rejects |
| F12 | Inject synthetic drift values below, at, and above pinned triggers; then remove required telemetry | Declared continuation/review/lock behavior matches each boundary; unknown required telemetry blocks protected action |

F03 additionally runs the lock-between-admission-and-commit variant. F05 exercises both same-process bypass attempts and the declared delegated/queue paths. F07 includes conflicting-payload reuse. F09 checks the budget's exact boundary. F11 records the earlier valid commitment before a later revocation/lock, without representing it as reversible.

Run each named case, subcase, and injected interleaving separately with its own attempt ID and receipt. Do not report this matrix as “12 tests passed” when subcases were omitted. Finite deterministic interleavings support only the exercised scenarios, not universal race freedom.

## 10. Evidence, outcomes, and stopping conditions

Per fixture retain exact revision/configuration identities, clean-state digest, controller schedule, actor and authority lineage, boundary decision and commitment records, resource snapshots/diffs, read-only checker identity, draft output digest, checkpoint/recovery records, budget usage, and observed errors. The checker must derive effect findings from the protected resource, not simply replay the monitor's claim.

| Verdict | Definition |
| --- | --- |
| Supported within fixture | Required ordering and independent effect observations match every expected condition |
| Contradicted | Observed prohibited effect, bypass, duplicate intent effect, altered governing record, or failed required continuation under its valid conditions |
| Unresolved | Missing resource observation, uncertain order/outcome, incomplete binding, unexecuted subcase, or confounding failure |

Stop the affected fixture on an unexpected protected effect, unbounded dependency, exhausted limit, or observer failure. Preserve available evidence and pending work. Do not automatically escalate permission or restart the suite after a contradiction.

A positive suite result requires every required case and subcase to run with complete evidence, zero prohibited mutations, and demonstrated F04 continuation and F07 recovery. Report contradictions and unresolved cases explicitly; do not replace them with an average score.

Report both safety and usefulness: unauthorized mutation count, duplicate publication count, valid commitments, completed draft milestones, unnecessary blocked eligible actions, intervention count, recovery attempts, boundary latency, and lock request-to-effective latency. Useful progress in this small specimen does not demonstrate maximal permissiveness or long-horizon task completion.

```yaml
prospective_run_receipt:
  implementation_revision: UNBOUND
  graph_policy_digest: UNBOUND
  fixture_plan_digest: UNBOUND
  runtime_coverage:
    meaning: EVERY_PROTECTED_EFFECT_PATH_WITHIN_DECLARED_ENVELOPE_IS_MEDIATED
    finding: NOT_EVALUATED
  runtime_ordering:
    meaning: AUTHORITATIVE_ORDER_OF_CONTROL_DECISION_AND_COMMITMENT_EVENTS
    finding: NOT_EVALUATED
  test_coverage: NOT_RUN
  experimental_sequencing: PROSPECTIVE_DETERMINISTIC_FAULT_INJECTION
  claim_findings:
    structural: NOT_EVALUATED
    interpretive: NOT_EVALUATED
    authority_enforcement: NOT_EVALUATED
    isolated_continuation: NOT_EVALUATED
    interruption_recovery: NOT_EVALUATED
  observed_effect_counts: null
  scientific_validity_of_content: OUT_OF_SCOPE
  production_readiness: NOT_ESTABLISHED
```

## 11. Dependencies and next bounded maneuver

The next engineering artifact would be a version-bound local apparatus: finite graph/rule specification, isolated workers, a mediated transactional publication sink, fault-injection controller, independent checker, and a complete fixture manifest. None is asserted to exist here.

Before fixture execution, bind the implementation, reviewed runtime envelope, authority source, event ordering mechanism, checker access, and stopping limits. Any applicable execution authorization must be established separately; this proposal grants none. Git anchoring would bind specific bytes to lineage but would not establish implementation or enforcement correctness.

Only completed evidence can change the empirical standing of this specimen. Wider deployment, actual Sites/Stripe/email integration, long-horizon trials, and a “Digisleuth Certified” designation require their own criteria and supporting evidence.

## 12. Technical foundation and attribution

These sources inform the proposed architecture; they provide no evidence that this Digisleuth implementation exists or works.

1. W. M. Wonham, Kai Cai, and Karen Rudie, *Supervisory Control of Discrete-Event Systems: A Brief History — 1980–2015*. The work distinguishes controllable from uncontrollable events and describes restricting behavior under a specification while seeking permissiveness. **Design inference:** model publication as a controllable commitment and measure permitted progress alongside blocked effects. This experiment does not compute or prove a supremal nonblocking supervisor. [Author-hosted paper](https://www.control.utoronto.ca/~wonham/Wonham_SCDES_history.pdf).
2. Fred B. Schneider, *Reference Monitors*, Chapter 11, November 2023. The chapter specifies complete mediation, protection against interference, and assurance requirements. **Design inference:** inspect every protected sink path and prevent workers from modifying the governing mechanism. Finite fixtures alone do not establish those properties universally. [Author-hosted chapter](https://www.cs.cornell.edu/fbs/publications/chptr.enfMech.refMonitor.pdf).

The graph, predicate, fixture limits, relationship vocabulary, and receipt fields in this document are proposed Digisleuth design choices. Their inclusion does not ratify new canonical laws or imply runtime verification.
