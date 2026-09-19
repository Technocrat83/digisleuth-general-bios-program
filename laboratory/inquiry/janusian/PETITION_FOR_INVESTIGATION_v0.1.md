# PETITION_FOR_INVESTIGATION_v0.1

```yaml
artifact_id: PETITION_FOR_INVESTIGATION_v0.1
artifact_class: EPISTEMIC_PETITION_CONTRACT
source_chamber: JANUSIAN_THINKING_CHAMBER_v0.1
source_method: EINSTEIN_SOCRATES_CHAMBER_MOUNT_v0.1
standing: CANDIDATE_SPECIFICATION
specification_state: FROZEN_FOR_REVIEW_AND_DRY_RUN_DESIGN
runtime_enforcement: NOT_IMPLEMENTED
instance_materialized: false
investigation_performed: false
scientific_evidence_delta: ZERO
admission_authority_delta: ZERO
execution_authority_delta: ZERO
canon_mutation_delta: ZERO
pp_gate: BLOCKED
```

## 1. Purpose and law

A Petition for Investigation (PFI) converts a Janusian tension object into a bounded request for investigation design and verification review. Chamber coherence cannot establish truth, evidence, admission, or execution.

J(C) → PFI(J) is a representational transformation. It is not an evidentiary or authority transition.

**JANUSIAN_LAW_05: TENSION MAY PETITION INVESTIGATION; TENSION MAY NOT PETITION TRUTH.**

The law is fixed within this candidate contract. Its identifier is the user-proposed label; this document does not assert a global Canon update or verification of numbering in another registry.

PFI_READY means eligible for downstream design review only. It does not mean the investigation is approved, feasible, funded, scheduled, performed, or evidentially successful. The proposed “admission gate” is named **petition readiness gate** here to prevent confusion with investigation admission.

## 2. Typed source relationship

For each tension coordinate:

T_i = ⟨C_i⁺, C_i⁻, Δ_i, V_i⟩.

C_i⁺ and C_i⁻ are explicit claims or challenges with identifiable source poles. Δ_i identifies the unresolved separation. V_i defines a proposed means of reducing that separation and the criteria for interpreting possible results.

The existence of V_i does not establish its performance. “Collapse requirement” is retained as a field name for compatibility with the proposal; it means a **separation-reduction requirement**, with no promise of complete resolution and no physical-collapse claim.

C⁻ may identify a limitation or defeater rather than assert an exhaustive rival world. The petition must state its role. Failure of either pole does not validate the other. Both can fail; both can remain unresolved; a third explanation can remain viable.

## 3. Normative field contract

This is a normative typed specification, not an executable JSON Schema. An implementation must reject undeclared fields, enforce scalar enums as single values, reject placeholders in required instance fields, and preserve all semantic gates below. Enumerations in this document list permitted alternatives, not simultaneous instance values.

`Text` means a nonempty, non-whitespace string with substantive content. `ID` means a nonempty identifier unique within its declared collection. `Ref` means a resolvable reference to an identified object or field. List minima are explicit. Required empty lists mean “none declared”; they do not prove absence.

| Object | Required fields and constraints |
|---|---|
| identity | petition_id: ID; revision: Text; artifact_class: EPISTEMIC_PETITION; source_chamber: JANUSIAN_THINKING_CHAMBER; source_method: EINSTEIN_SOCRATES; standing: CANDIDATE_SPECIFICATION |
| boundary | requested_operation: INVESTIGATION_DESIGN_REVIEW; chamber_output_role: INQUIRY_ONLY; investigation_status: NOT_PERFORMED_BY_THIS_PETITION; grants_evidence/admission/execution/authority: all false |
| source_object.candidate | id: ID; proposition: Text; provenance: one or more provenance records |
| source_object.janusian_object | id: ID; source_receipt_ref: Ref; constructive_pole_ref: Ref; destructive_pole_ref: Ref; tension_refs: one or more Ref |
| constructive_pole | pole_id: ID; minimal_model.description: Text; possible_worlds: one or more world records; invariants: zero or more invariant records |
| world record | world_id: ID; boundary_conditions: Text list; assumptions: assumption Ref list; predicted_consequences: one or more Text |
| invariant record | invariant_id: ID; formulation: Text; proposed_comparison_frames: one or more Text; standing: HYPOTHESIS_ONLY |
| destructive_pole | pole_id: ID; role: RIVAL_CLAIM, LIMITATION, or DEFEATER; failure_surfaces: one or more failure records; exposed_assumptions: assumption records |
| failure record | failure_id: ID; trigger: at least one substantive premise_change, frame_change, or counterexample; affected_claim: Ref; consequence: one consequence enum; explanation: Text |
| assumption record | assumption_id: ID; proposition: Text; kind: DEFINITIONAL, EMPIRICAL, or FORMAL; epistemic_status: UNVERIFIED, CONTESTED, or EXTERNALLY_SUPPORTED; support_refs: provenance Ref list, nonempty if EXTERNALLY_SUPPORTED |
| tension_vector | unresolved_coordinates: one or more tension records |
| tension record | tension_id: ID; positive_claim: claim record; negative_claim: claim record; separation_basis: one or more separation enums; separation_description: Text; collapse_requirement: requirement record |
| claim record | source_pole_ref: Ref; statement: Text; claim_domain: Text |
| requirement record | requirement_id: ID; investigation_type: one investigation enum; scope_and_limits: Text; investigation_contract_ref: Ref; target_of_success: Text; success_predicate, failure_predicate, abstention_predicate: predicate records |
| predicate record | formulation: Text; input_refs: one or more observable/output Ref; evaluation_rule: Text |
| provenance record | provenance_id: ID; source_locator: Text; source_kind: Text; revision_or_capture: Text; role: CHAMBER_RECORD, EXTERNAL_SOURCE, or DERIVATION; supports: claim Ref list |

Consequence enum: CONTRADICTION, INDETERMINACY, DOMAIN_COLLAPSE, DEFINITIONAL_FAILURE, CAUSAL_FAILURE, OTHER. OTHER requires a specific explanation.

Separation enum: MISSING_MEASUREMENT, MISSING_PROOF, UNBOUND_DEFINITION, FRAME_DEPENDENCE, MISSING_COUNTERFACTUAL, CAUSAL_AMBIGUITY, SCALE_DEPENDENCE, UNKNOWN.

Investigation enum: EMPIRICAL_TEST, FORMAL_PROOF, COUNTEREXAMPLE_SEARCH, SIMULATION, MEASUREMENT, REPLICATION, SOURCE_RECOVERY, DEFINITIONAL_ADJUDICATION.

All source and cross-object references must resolve without inferred identities. Claims represented in multiple places must remain congruent. Chamber records establish provenance of inquiry only. External sources may retain their pre-existing reported standing, subject to separate authentication and evaluation; inclusion in a PFI does not certify them.

Two changes remove category leakage: `proposed_comparison_frames` replaces `observed_across_frames`, and assumption `kind` is separated from `epistemic_status`. EMPIRICAL describes a claim type, not proof that it is supported.

## 4. Investigation contracts

`investigation_contracts` is a nonempty collection. Each contract has a unique contract_id and a nonempty list of tension_refs. Each requirement resolves to a contract covering its own tension coordinate. One contract may cover multiple coordinates only when its criteria discriminate each coordinate explicitly.

Every contract requires:

- **Investigation question:** one bounded question with scope, relevant definitions, and frame conditions.
- **Discriminating observation or output:** what measurement, proof object, counterexample, recovered source, or adjudication record would bear on the separation.
- **Observables:** one or more records with observable_id, output_kind, operational_definition, and interpretation_limits. Units are required for quantities or explicitly NOT_APPLICABLE. Acquisition method is required where it affects discrimination; otherwise its downstream design obligation must be named. Actual instruments and schedules need not be authorized here.
- **Predicted dispositions:** per-tension expected patterns under C⁺ and C⁻, plus an explicit non-discriminating pattern mapped to ABSTAIN. LIMITATION and DEFEATER roles specify what would sustain or defeat the challenge instead of inventing a rival model.
- **Falsifiability:** substantive conditions counting against each pole. Formal and definitional work uses proof obligations, countermodels, consistency failures, or declared adjudication criteria rather than requiring a physical measurement.
- **Blindness requirements and confounders:** lists with either substantive entries or a reasoned “none identified/not applicable” declaration. An empty list alone is insufficient for readiness review.
- **Alternative space:** known alternatives and unknown alternatives, with exhaustion_established fixed false in v0.1. Do not invent a C° merely to populate the record.
- **Design dependencies:** unresolved sampling, apparatus, resource, custody, replication, consent, or jurisdiction requirements. A dependency that prevents stating a discriminating criterion blocks readiness; a dependency concerning how an already intelligible test would be implemented remains a downstream obligation.
- **Prohibited inferences:** coherence → evidence; absence of counterexample → truth; failure of one pole → validation of the other; simulation agreement → empirical confirmation; source recovery → source truth; readiness → execution permission; lens agreement → independent corroboration.

Formal proof remains relative to stated axioms and inference rules. Simulation remains relative to its model. Source recovery concerns custody. Definitional adjudication binds a stipulated use; it cannot establish an empirical fact by definition.

## 5. Predicate semantics and outcome completeness

Success and failure are relative to the declared target_of_success, not synonyms for C⁺ true and C⁻ true. Each target identifies the limited verification question and the maximum interpretation permitted.

For valid result r, define predicates S_i(r), F_i(r), and A_i(r). Require pairwise disjointness and coverage of the declared valid-result domain: exactly one applies. Ambiguous, non-discriminating, insufficient, or unanticipated valid results fall into ABSTAIN. Invalid acquisition, broken provenance, or a breached design contract is INVALID_RESULT and precedes this three-way classification.

Predicate overlap or an uncovered result exposes a defective contract: record INVALID_CONTRACT and return for revision. Never select the most favorable predicate. These outcomes belong to a future investigation result record; the petition contains definitions only and cannot carry a completed result.

## 6. Petition readiness gate

PFIReady(J,P) holds iff all of the following pass against the exact submitted revision:

1. Structure is well-formed; identities and provenance are explicit; references resolve.
2. Both poles are substantive; the negative pole’s role is declared.
3. The tension vector is nonempty and faithfully represents J.
4. Every T_i has a bound V_i and a covering investigation contract.
5. Predicted patterns genuinely discriminate within declared frames; the criteria are substantive and evaluable.
6. Definitions are sufficiently stable for the requested investigation. A definition may itself be the target, provided the competing definitions and adjudication procedure are fixed.
7. Success/failure/abstention semantics are coherent, non-overlapping, and complete within the declared result domain.
8. Claim-domain limits, alternative possibilities, and the non-propagation boundary are preserved.
9. No inquiry output is promoted to evidence or authority, and no execution command is embedded as an authorized action.

Gate entries have status PASS, FAIL, or NOT_EVALUATED, plus a reason and inspected field references. User-asserted booleans are declarations, not gate findings. Structural validation alone cannot establish discrimination, truthfulness of provenance, or semantic non-leakage. No aggregate score may compensate for a failed gate.

The detached readiness receipt requires petition identity and revision binding, reviewer identity and role, review method, gate findings, disposition, reason_codes, and authority_delta: ZERO. Any changed petition revision requires fresh review. A digest may bind exact bytes when actually computed; no cryptographic signature is implied.

Disposition precedence:

1. PFI_BOUNDARY_VIOLATION for attempted evidentiary promotion, execution authorization, or authority escalation.
2. PFI_INCOMPLETE for missing required content, unresolved references, or unevaluated gates.
3. PFI_DEFINITIONALLY_UNSTABLE for definitions that prevent review.
4. PFI_NONDISCRIMINATING for indistinguishable declared outcomes.
5. PFI_UNFALSIFIABLE for absent meaningful challenge/refutation criteria appropriate to the investigation type.
6. PFI_READY only when every gate passes.

All applicable reasons are retained even when one disposition takes precedence. RETURN_TO_JANUSIAN_CHAMBER is the routing action for a non-ready petition, not a competing scientific outcome. CEASE halts review with available residue and no implied disposition if review is incomplete.

## 7. Downstream topology and authority boundary

The full prospective route is:

C → J(C) → PFI → petition readiness review → investigation design → separate governance review → local investigation admission and authority binding → bounded investigation → observation/result custody → evidence evaluation.

A ready petition may enter design review. Every subsequent arrow has its own contract; none is automatic. Governance determines whether, where, by whom, with which resources, under which limits, and with what CEASE provisions an investigation may occur. Design admission is distinct from execution admission.

Investigation results and evidence evaluations are separate successor objects referencing the petition revision. They must not overwrite the petition’s original predictions or retroactively change its criteria. Evidence evaluation itself grants no operational authority.

States, transitions, and authorities remain separately typed. This document creates a specification artifact; it creates no investigation admission, execution authority, or runtime enforcement mechanism.

## 8. Freeze scope and next operation

The candidate contract and JANUSIAN_LAW_05 are fixed here for review. No concrete J→PFI dry-run, schema validator, adversarial battery, investigation, or evidentiary adjudication has been performed. Normative closure is proposed; tested closure is unestablished.

The next bounded operation is to derive an executable structural schema and a separate semantic review fixture contract from this specification, then test a concrete J→PFI translation against both. Outcomes must distinguish valid serialization, petition readiness, and downstream authority.

Sources: the user’s PFI proposal in this conversation; current JANUSIAN_THINKING_CHAMBER_v0.1.md (libfile_9272378d3e7881918b44bbec4f8ddb65); current EINSTEIN_SOCRATES_CHAMBER_MOUNT_v0.1.md (libfile_6a76672673e88191be474ab017c45d9f). The two parent specifications were read for this formalization.
