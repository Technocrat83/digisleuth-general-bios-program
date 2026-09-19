# PREDICATE_DISJOINTNESS_SPECIFICATION_v0.1

```yaml
specification_id: PD-v0.1
standing: CANDIDATE_FORMAL_PREDICATE_CONTRACT
state: FROZEN_IMPLEMENTATION_TARGET
parent: PFI_v0.1r
successor_dependency: RAP_v0.1
implementation_status: NOT_IMPLEMENTED_BY_THIS_ARTIFACT
battery_status: SPECIFIED_NOT_EXECUTED
adjudication_power: ZERO
scientific_evidence_delta: ZERO
truth_delta: ZERO
authority_delta: ZERO
governance_admission: UNINSTANTIATED
```

## 1. Purpose and scope

Determine whether typed predicates over one declared observable form a deterministic three-outcome discrimination geometry, with observation invalidity evaluated separately. This contract fixes the next implementation target; it does not report a successful proof run, authenticate a reviewer, or admit an investigation.

Authentic bytes ≠ valid predicate geometry. Parseability ≠ satisfiability. Pairwise disjointness ≠ domain completeness. Domain completeness ≠ empirical validity. Deterministic classification ≠ truth.

Dependency order: PFI_v0.1r → PD-v0.1 → RAP-v0.1 → Governance Admission review. A PD result supplies bounded mathematical findings to a future PFI integration; it cannot replace review of measurement meaning, source fidelity, claim scope, or authorization.

JANUSIAN_LAW_05 remains: TENSION MAY PETITION INVESTIGATION; TENSION MAY NOT PETITION TRUTH.

## 2. Evaluation spaces and outcome types

Let D_M be the declared valid metric domain. Define disjoint tagged spaces:

Ω = ({VALID} × D_M) ⊔ ({INVALID_OBSERVATION} × D_bad).

D_bad contains observation records rejected by the declared validity contract, including missing measurements, unavailable validity checks, failed acquisition, invalid types, out-of-domain values, unknown units, and failed provenance checks. It does not include valid metric values merely because no scientific predicate covers them.

Scientific regions S_SUPPORT, S_FAIL, S_ABSTAIN are subsets of D_M. The INVALID region belongs exclusively to the second tagged summand. Three scientific pair intersections require set computation; their three intersections with INVALID are disjoint by construction of the tagged spaces. The receipt must distinguish COMPUTED_SET_DISJOINTNESS from TYPE_SEPARATION rather than claim six independent scalar proofs.

**Observation invalidity ≠ hypothesis failure.**

A contract-validation failure is also distinct from an INVALID observation. A malformed predicate contract produces a PD rejection and no usable classifier; it must not classify every future observation as INVALID or ABSTAIN.

## 3. Required contract fields

This is a normative serialization contract. Executable JSON Schema and the normalizer follow as separate implementation work.

| Field | Required content |
|---|---|
| schema_identity | PD-v0.1; CANDIDATE_FORMAL_PREDICATE_CONTRACT |
| binding | source_pfi_id; exact source_pfi_digest; discrimination_vector_id; tension_id |
| observable | observable_id; symbol; domain; unit; nullability fixed false; measurement_semantics |
| observation_validity | fixed required checks and their declared meanings; failure_disposition INVALID |
| predicates | exactly SUPPORT, FAIL, ABSTAIN; each carries a typed AST and require_nonempty boolean |
| residual_policy | exactly ROUTE_TO_ABSTAIN or REJECT_PREDICATE_FAMILY |
| arithmetic_profile | EXACT_RATIONAL_V0_1 |
| unit_profile | PD_UNIT_TABLE_V0_1 |
| resource_envelope | maximum 64 clauses per predicate; maximum 2 numeric atoms per clause; maximum 128 atoms per predicate; maximum 256 digits per numeric literal |

All objects are closed: unknown fields are rejected. Identifiers and descriptive text must be nonempty and non-whitespace. Descriptive text is metadata and is never parsed as executable logic. Candidate or receipt text cannot alter the grammar, unit table, arithmetic rules, or resource limits.

Each PD object binds one PFI tension coordinate and one scalar observable. A multi-coordinate PFI requires coverage by separately bound PD objects. Multivariate relations, joint distributions, time-series predicates, and cross-observable comparisons are outside v0.1. Per-coordinate proofs do not prove a joint multivariate partition.

## 4. Domains and exact arithmetic

Supported domain types: BOOLEAN, INTEGER, REAL, ENUM.

- BOOLEAN has exactly false and true. Booleans never count as integers.
- INTEGER permits optional lower and upper bounds with inclusion flags. It denotes mathematical integers within those bounds.
- REAL permits optional lower and upper bounds with inclusion flags. It denotes mathematical real values, while all serialized finite endpoints are exact rationals represented by decimal text.
- ENUM requires a nonempty finite list of unique member identifiers. Members are exact, case-sensitive tokens, not executable strings.

Domain emptiness is invalid. Bounds must be ordered. Infinity is represented by an absent bound, never NaN, Infinity, or a floating-point sentinel.

Numeric literals use tagged exact decimal text: `{"decimal":"0.05","unit":"SECOND"}`. Accepted spelling: optional minus, integer part without redundant leading zeros, optional fractional digits; no exponent, plus sign, whitespace, or NaN. A literal is parsed as an exact rational, not through binary floating point. Decimal text does not admit arbitrary string predicates.

PD_UNIT_TABLE_V0_1 fixes SECOND as time scale 1, MILLISECOND as 1/1000, MICROSECOND as 1/1000000, and DIMENSIONLESS as scale 1 in a distinct dimension. Numeric observables use one of these units; BOOLEAN and ENUM use NOT_APPLICABLE. No implicit dimensional conversion or affine/offset units are admitted. Additional units require a versioned successor profile.

Thus 0.05 SECOND and 50 MILLISECOND normalize exactly to the same threshold. Integer comparisons against noninteger thresholds are valid and normalize using exact floor/ceiling arithmetic. Fractional INTEGER domain bounds themselves are rejected.

## 5. Bounded typed AST

Every atom references the one declared observable. An unknown reference returns UNKNOWN_OBSERVABLE.

Numeric atoms: comparison operator in LT, LE, EQ, NE, GE, GT; observable_ref; exact numeric literal with unit. A numeric clause is one atom or an AND node containing exactly two atoms. A numeric predicate is one clause or an OR node containing 1–64 clauses. AND inside AND, OR inside OR, NOT, arbitrary nesting, arithmetic expressions, functions, parity, recursion, and temporal operators are excluded.

ENUM predicates use one IN node with observable_ref and a finite list of unique declared member tokens. BOOLEAN predicates use EQ or NE with observable_ref and a typed boolean literal. An empty ENUM membership set is allowed as an explicit empty region, subject to require_nonempty. Every domain also permits a dedicated EMPTY node carrying observable_ref and no literal. It denotes the empty set and remains subject to require_nonempty; it is a set constant, not an unrestricted function.

A known grammar shape with an unsupported operator returns UNSUPPORTED_OPERATOR. A scientific predicate that attempts to encode observation-validity fields, or adds an INVALID scientific slot, returns PREDICATE_SCHEMA_INVALID. Type and unit errors retain TYPE_MISMATCH and UNIT_MISMATCH diagnostics. No implementation may fall back to prose interpretation.

This fragment has an exact decision procedure. Resource exhaustion returns RESOURCE_LIMIT_EXCEEDED with proof checks NOT_EVALUATED. It never returns DISJOINTNESS_PROVEN. No mathematical undecidability is asserted for a valid in-envelope contract in this fragment.

## 6. Normal forms

N(P) = S ⊆ D_M.

REAL uses sorted unions of intervals with rational endpoints and explicit open/closed flags. Merge overlapping intervals and touching intervals exactly when their union has no missing point. INTEGER uses sorted unions of closed integer ranges, with absent bounds for infinity; merge overlapping or adjacent ranges. ENUM uses sorted member sets. BOOLEAN uses a sorted subset of [false, true].

Normalize atoms, intersect atoms within each clause, union clauses, and restrict to D_M. Numeric comparisons such as x < 5 may naturally extend beyond a bounded domain; this is ordinary domain restriction, not an invalid predicate. ENUM members outside the declared domain are type errors.

Normalization must not use sampled points, floating-point tolerances, or evaluation of user-supplied code. Representatives used as witnesses must be checked against the exact resulting sets.

An empty normalized region is reported EMPTY. It is a terminal PREDICATE_UNSATISFIABLE only when that outcome declares require_nonempty true. Otherwise emptiness is permitted and explicitly recorded. All three booleans must be supplied: no inferred permission.

This resolves the finite-domain cardinality issue: a two-value BOOLEAN domain can support a three-label classifier only if at least one label has an empty region. “Partition” in PD-v0.1 means a total single-valued outcome labeling; its nonempty fibers form the mathematical partition.

## 7. Intersection and coverage obligations

Compute all three scientific intersections. Any nonempty intersection yields PREDICATE_OVERLAP, exact overlap region, and a deterministic witness. Residual routing cannot repair overlap.

For numeric witnesses, choose deterministically: the included finite lower endpoint when available; otherwise an exact midpoint for a finite real interval, the least member for a lower-bounded integer range, or a fixed admissible point derived from the finite bound for a one-sided interval. A wholly unbounded interval uses zero. For sets, choose the first member in canonical order. Recheck membership in both regions.

Let U = S_SUPPORT ∪ S_FAIL ∪ S_ABSTAIN and R = D_M \ U. Record authored coverage before routing and effective coverage after routing.

**Correction to DOMAIN_OVERCOMPLETE:** because each normalized S is a subset of D_M, U cannot exceed D_M. Overlap is not overcoverage: two sets may overlap while their union is exactly D_M. Therefore DOMAIN_OVERCOMPLETE is not a coverage disposition in this contract. An internal result containing values outside D_M is NORMALIZATION_INVARIANT_FAILURE, not a successful diagnostic classification.

Residual policy:

- REJECT_PREDICATE_FAMILY: nonempty R returns DOMAIN_INCOMPLETE with the exact residual and a witness. Disjointness may be recorded as proven, but no complete classifier is emitted.
- ROUTE_TO_ABSTAIN: set S_ABSTAIN_effective = S_ABSTAIN ∪ R. Preserve the original authored set and the separate routed residual. Recheck all three intersections and effective coverage before PARTITION_PROVEN.

ROUTE_TO_INVALID is excluded: R contains valid scientific valuations and cannot be relabeled as apparatus failure. ROUTE_TO_SUPPORT and ROUTE_TO_FAIL are also forbidden. Missing residual policy returns RESIDUAL_POLICY_MISSING. An unsupported policy is PREDICATE_SCHEMA_INVALID.

A successful receipt must establish effective coverage D_M and effective disjointness, not merely that a residual-policy string exists.

## 8. Observation validity and classification

The fixed prerequisite checks are measurement_present, unit_valid, provenance_valid, and acquisition_successful. Each check has a host-supplied PASS, FAIL, or NOT_ESTABLISHED result. FAIL or NOT_ESTABLISHED routes the observation to INVALID with reasons; this is not a claim that every unknown check is factually false.

PD specifies these inputs but does not authenticate their issuer. RAP and the eventual host integration must establish their provenance. Additional type/domain validation is performed after exact unit normalization. Unsupported or out-of-domain observations return INVALID. The mathematical validity partition does not prove a real sensor or provenance assertion trustworthy.

Given an accepted PARTITION_PROVEN contract, classify a valid in-domain observation by its unique effective scientific region. An observed zero-match or multiple-match condition indicates an implementation or contract-binding failure and returns EVALUATOR_INVARIANT_FAILURE, outside scientific outcomes. It must never choose the first matching rule.

An invalid observation returns INVALID before scientific evaluation. Contract rejection or unavailable proof does not authorize classification.

## 9. Corrected validation procedure

1. Decode strict JSON; reject duplicate keys and unknown structural fields. Recognize a missing residual policy distinctly.
2. Validate the binding, closed AST shapes, resource envelope, nonempty domain, references, types and units.
3. Normalize each predicate exactly and record empty-region permissions.
4. Compute all three intersections, recording exact witnesses for overlaps. Reject any overlap.
5. Compute authored U and R. Record DISJOINTNESS_PROVEN as an intermediate check.
6. If R is nonempty and policy rejects, return DOMAIN_INCOMPLETE. If policy routes to abstention, actually form the effective abstention region.
7. Recompute effective disjointness and coverage. Reject any internal invariant failure.
8. Emit PARTITION_PROVEN only after every required check passes; include a deterministic unsigned receipt.

Errors are typed findings. Aggregate precedence is structural/type/unit/resource failure, prohibited empty-region failure, overlap, then incomplete coverage. Retain applicable diagnostics; checks skipped after a terminal failure remain NOT_EVALUATED. No missing/unknown result becomes PASS.

## 10. Deterministic proof receipt

The receipt contains:

- receipt_version PD-R-v0.1; evaluator version and executable digest; arithmetic/unit/normalization profile versions;
- source_pfi_id and exact source_pfi_digest; discrimination_vector_id and tension_id;
- observable identity; declared domain and domain_digest;
- predicate_contract_digest over the exact submitted UTF-8 bytes;
- authored normalized regions, effective regions, region digest, residual and routing action;
- per-outcome satisfiability/emptiness results and permissions;
- all three computed pair intersections and three INVALID type-separation results;
- type, unit, validity-space, coverage, residual-routing and normalization checks;
- final disposition; evidence_delta ZERO, truth_delta ZERO, authority_delta ZERO;
- authentication_status UNSIGNED_UNAUTHENTICATED.

Use a named local serialization profile PD-CJSON-1 for derived normal forms and receipt bytes: lexicographically sorted object keys, no insignificant whitespace, ASCII-escaped strings, lowercase JSON booleans, exact rational endpoints as reduced numerator/positive-denominator decimal strings, and one final LF. Arrays use their defined canonical order. No floating-point numeric values occur in derived mathematical objects. This is a local deterministic profile, not a claim of RFC 8785 compliance.

Hash domains must be explicit. Domain and region digests cover their PD-CJSON-1 representations. Contract and source-PFI digests cover original exact bytes. Receipt identity, if needed, is a detached hash of completed receipt bytes; the receipt does not include its own digest. No wall-clock timestamp, randomness, environment path, or elapsed time enters deterministic receipt content. Operational timing belongs in a separate run log.

Byte-different but equivalent ASTs may yield equal normalized-region digests and different contract digests and receipts. Deterministic receipt means reproducible for the same input bytes, evaluator and profiles; it does not erase provenance distinctions.

The receipt is a machine-reported bounded formal finding suitable for later authentication. Its existence is not proof that the implementation is sound. Scientific evidence_delta ZERO does not deny that the run creates a new verification artifact.

## 11. Dry-run fixture contract — not executed

All three scientific slots are present in every fixture. Unless stated otherwise use REAL domain [0,+∞), DIMENSIONLESS units, explicit permission for any empty ABSTAIN slot, and REJECT_PREDICATE_FAMILY.

| ID | Authored geometry or defect | Required result |
|---|---|---|
| PD_01_CLEAN_PARTITION | SUPPORT <5; FAIL >=5 AND <10; ABSTAIN >=10 | PARTITION_PROVEN |
| PD_02_BOUNDARY_OVERLAP | SUPPORT <=5; FAIL >=5; ABSTAIN empty via <0 | PREDICATE_OVERLAP; witness 5 |
| PD_03_DOMAIN_GAP | SUPPORT <5; FAIL >5; ABSTAIN empty via <0 | DOMAIN_INCOMPLETE; residual {5} |
| PD_04_SEMANTIC_ALIAS | Time domain in ms; SUPPORT >0.05 SECOND; FAIL >50 MILLISECOND; ABSTAIN <=50 ms | Equal normalized SUPPORT/FAIL regions; PREDICATE_OVERLAP |
| PD_05_UNSUPPORTED_LOGIC | Integer parity operator | UNSUPPORTED_OPERATOR |
| PD_06_INVALID_CATEGORY_ERROR | Sensor-failure field or INVALID scientific predicate slot | PREDICATE_SCHEMA_INVALID |
| PD_07_ROUTE_RESIDUAL | PD_03 with ROUTE_TO_ABSTAIN | PARTITION_PROVEN; authored gap {5}; effective abstention {5} |
| PD_08_INVALID_RESIDUAL_ROUTE | PD_03 with ROUTE_TO_INVALID | PREDICATE_SCHEMA_INVALID |
| PD_09_BOOLEAN_PARTITION | BOOLEAN domain; SUPPORT EQ true; FAIL EQ false; ABSTAIN EMPTY with require_nonempty false | PARTITION_PROVEN |
| PD_10_INTEGER_BOUNDARY | INTEGER domain [0,+∞); SUPPORT <0.5; FAIL >=0.5 AND <2; ABSTAIN >=2 | PARTITION_PROVEN; SUPPORT {0}; FAIL {1} |
| PD_11_REQUIRED_EMPTY | PD_03 with ABSTAIN require_nonempty true | PREDICATE_UNSATISFIABLE |
| PD_12_MISSING_POLICY | Otherwise valid contract without residual_policy | RESIDUAL_POLICY_MISSING |
| PD_13_UNKNOWN_REFERENCE | Comparison refers to a different observable | UNKNOWN_OBSERVABLE |
| PD_14_UNIT_ERROR | Numeric literal uses an unsupported unit or incompatible dimension | UNIT_MISMATCH |
| PD_15_VALIDITY_FAILURE | Clean proven partition; absent acquisition success | Observation INVALID; no hypothesis failure |
| PD_16_RESOURCE_LIMIT | Predicate exceeds declared clause/atom limit | RESOURCE_LIMIT_EXCEEDED; proof NOT_EVALUATED |

Every proof-positive fixture must check the normalized sets, coverage and all intersections, not only the final status. Every witness must be independently checked against its target region. Equivalent-unit fixtures must compare normal forms, not string spelling. Observation tests remain separate from contract-validation tests.

## 12. PFI integration and freeze boundary

PFI_v0.1r uses PASS as its support label. An explicit versioned integration maps PD SUPPORT to PFI PASS; FAIL and ABSTAIN retain meaning. PD INVALID is observation validity, so it does not silently replace the former four-symmetric-predicate structure. A successor PFI schema must preserve this typed change and bind exact source candidate, tension, PD contract, and proof receipt identities.

PARTITION_PROVEN ≠ PFI_READY. PD establishes geometry only within the declared fragment and domain. A physically meaningless metric, false measurement model, or inauthentic review can accompany a mathematically valid partition. Semantic review and receipt authentication remain separately required.

RAP will authenticate the already-defined receipt and its provenance. Governance will separately evaluate local eligibility and bind any investigation authority. Investigation produces observation records; evidence standing requires a further evaluation rather than arising automatically from investigation execution.

Frozen here: the bounded grammar, exact arithmetic/unit profiles, INVALID separation, empty-region rule, residual policy, coverage obligations, receipt contents, and fixture expectations. Not performed: executable schema generation, normalizer implementation, proof battery execution, RAP implementation, signing, PFI migration, Governance Admission, or scientific investigation.

Source basis: the user's PD-v0.1 proposal in this conversation and the established PFI_v0.1r successor context. This document records explicit reconciliations rather than claiming the supplied pseudocode already enforced them.
