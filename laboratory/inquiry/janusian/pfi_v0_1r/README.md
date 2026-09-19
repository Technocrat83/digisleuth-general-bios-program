# PFI v0.1r — candidate executable binding

Status: IMPLEMENTED_REFERENCE_VALIDATOR; SYNTHETIC_TESTS_PASS; EXTERNAL_AUTHENTICATION_ADAPTER_UNBOUND; GOVERNANCE_ADMISSION_UNINSTANTIATED.

This successor package binds a serializable candidate contract, detached review and authority-separation receipts, dependency receipts, and the revised five dispositions. It does not ratify Canon or grant investigation authority. JANUSIAN_LAW_05 remains: TENSION MAY PETITION INVESTIGATION; TENSION MAY NOT PETITION TRUTH.

## Deliverables and use

- `pfi_candidate.schema.json`: closed Draft 2020-12 candidate schema.
- `review_receipt.schema.json`: detached semantic findings, including all six outcome pairs.
- `authority_separation_receipt.schema.json`: bounded non-authority declaration.
- `dependency_receipt.schema.json`: detached satisfaction/hold of a named dependency.
- `pfi_validator.py`: staged evaluator with deny-by-default external authentication seam.
- `test_validator.py`: 29 synthetic tests and specimen generation.
- `test_results.json`: actual test run output.
- `synthetic_examples/`: synthetic input and detached objects, explicitly not authenticated real events.
- `build_schemas.py`: reproducible schema construction.
- `requirements.txt`: version used for local validation.

Run `python -m pip install -r requirements.txt`, then `python test_validator.py` in this directory. To inspect a candidate without an authentication adapter: `python pfi_validator.py synthetic_examples/candidate.json`. The default CLI yields PFI_NOT_READY. It exposes no option to treat a candidate-supplied key or trusted flag as authentication.

## Source basis and migration

Read sources: PETITION_FOR_INVESTIGATION_v0.1.md (libfile_de9173a211708191b807b2643b719169) and the reference PFI_V0_1_VALIDATOR_SPECIFICATION in Pasted markdown(1).md (libfile_34343ad243a8819192ba21786a0925db), plus the user's supplied v0.1r schema and corrections.

This is newly materialized successor code, not a claim to recover historical validator file bytes. The old source was read as text. The four named tests reuse the requested disposition categories with new synthetic content; the original scheduler, memory, networking, and proof examples are not claimed to have passed semantic review.

The user proposal requires the following deliberate serialization changes for upstream closure:

1. `discrimination_vector` is a nonempty array of tension coordinates. Each preserves C+, C−, separation, and a bound collapse_requirement. One flat metric cannot establish coverage of an arbitrary J(C).
2. Every requirement contains a closed four-slot `conditions` object with fixed PASS, FAIL, ABSTAIN, INVALID labels. PASS means conditional support for the bounded target, never truth. `support_condition` therefore migrates to `conditions.PASS.condition`.
3. Whitespace-only text is rejected. Required models, worlds, predictions, failure triggers, negative-pole role, and assumption standing bases preserve review context. Text substance and source accuracy remain semantic obligations.
4. Dependencies have a PFI_READINESS or GOVERNANCE_REVIEW scope. Required readiness dependencies need authenticated satisfaction receipts. Governance dependencies remain declared and forwarded; they do not need to be satisfied merely to request governance review.
5. Candidate provenance binds exact source bytes; review receipts bind exact candidate bytes and a separate review artifact. SHA256_EXACT_BYTES is explicitly not RFC 8785 canonicalization. Whitespace changes to a candidate invalidate its review binding.
6. The output report carries external receipt references and byte digests. Candidate objects carry neither a review signature nor the evidence that makes them ready.
7. The schema identifiers are local URNs. No schema was published at the proposed web URL.

Unknown fields are rejected. JSON duplicate keys and non-JSON constants are rejected. ID uniqueness across each collection is checked by the evaluator; schema shape alone does not ensure it. All six condition-text pairs are compared after whitespace normalization; equal strings cause semantic rejection while distinct strings provide no positive semantic certification. Outcome labels, text identity, and predicate meaning remain three distinct checks.

## Stage semantics

| Condition | Disposition |
|---|---|
| Explicit prohibited delta or power claim | EPISTEMIC_MEMBRANE_VIOLATION |
| Malformed serialization, schema violation, or duplicate collection ID | SYNTACTICALLY_INVALID |
| Demonstrated predicate collision or authenticated negative semantic finding | SEMANTICALLY_UNREVIEWABLE |
| No authenticated review, unevaluated finding, missing source, or unresolved required readiness dependency | PFI_NOT_READY |
| All structural, semantic-review and detached readiness requirements pass | PFI_READY |

PFI_READY = eligible for Governance Admission review. Neither admission, authorization, nor execution follows automatically.

Parsing is a prerequisite for inspecting a serialized membrane. Nonzero well-typed membrane values are classified before schema validation, so the truth-delta specimen reports EPISTEMIC_MEMBRANE_VIOLATION even though a standalone schema checker would reject its const value. The report records syntax NOT_EVALUATED on this terminal branch, not PASS. Missing or mistyped declarations remain structural failures. The schema and staged disposition therefore answer different questions.

The initial membrane stage checks typed declarations only. Hidden promotion in natural-language claims requires semantic review and can produce the same terminal membrane disposition later. A declarations pass does not claim universal detection of epistemic leakage. This prevents a false claim that a simple JSON precheck understands all prose.

NOT_READY can coexist with semantics NOT_EVALUATED. Missing review is not proof of unreviewability. No status is inferred from the absence of a counterexample. The disposition collection is implemented as staged terminal classifications, not claimed to be a mathematically proved lattice.

## Detached review and trust contract

A detached object, identity string, digest, or `authority_delta: 0` declaration alone authenticates nothing. The host must supply `authenticate(receipt_bytes, artifact_bytes)` through trusted application wiring, never by deserializing candidate input. Literal True is accepted only after host verification of the external event, eligible reviewer, provenance/custody, freshness/revocation, and candidate-independent trust configuration. Exceptions fail closed. The callback is the explicit trusted computing boundary; a dishonest or compromised host verifier can defeat it.

The reference implementation validates schema, candidate ID and byte digest, receipt artifact digest, per-coordinate coverage, every required semantic finding, all six pairwise findings, separate authority-separation receipt, and applicable dependency receipts. It does not implement a signature scheme, key issuance, identity provider, or independent semantic reasoner. Those remain host integration obligations. Digests establish byte correspondence; reviewer authentication establishes event provenance, not infallibility of the judgment.

The test adapter pins synthetic receipt bytes in memory. It exercises the orchestration branch only and must never be used as production authentication. No real reviewer was impersonated, no signature was created, and no real external review event is asserted. All example reviewer and receipt identifiers are explicitly SYNTHETIC.

An AUTHORITY_SEPARATION_RECEIPT has scope PFI_EVALUATOR_OUTPUT_ONLY. It cannot prove absence of authority changes elsewhere in a system. This evaluator does not perform admission or actuation and emits authority_delta 0 and false admission/authorization/execution fields on every branch. End-to-end enforcement outside this process remains unimplemented.

## Semantic obligations retained

Authenticated review must examine substantive discrimination, stable definitions, source fidelity, claim scope, full coverage, semantic membrane non-leakage, and all six pairwise intersections for every coordinate. Free-form predicates are never executed by this validator. Syntax, distinct strings and review-shaped fields cannot substitute for those findings.

INVALID covers invalid acquisition or out-of-domain inputs; PASS/FAIL/ABSTAIN concern valid inputs. Review must ensure invalidity is excluded from each valid-input predicate, not merely rely on precedence to hide overlapping raw conditions. Coverage concerns the declared result domain. Unanticipated valid results must be handled under explicit abstention rules or trigger a contract revision. Investigation-result execution and evidence evaluation are outside this validator.

Required receipt authentication and sufficient review-artifact content are external responsibilities. The evaluator does not fetch network sources or recover missing objects. Missing source bytes fail readiness; matching bytes still require source-fidelity review. Assumption standing is reported standing whose support must be reviewed, not an evidentiary promotion by serialization.

## Verification and limits

29/29 synthetic tests passed. Coverage includes the revised four specimen dispositions; six outcome-pair collisions; no authentication adapter; forged reviewer text; changed candidate bytes; source mismatch; missing separation and dependency receipts; duplicate dependency receipts; mismatched review artifact; malformed and duplicate-key JSON; whitespace text; embedded review field; boolean-as-zero; duplicate tension IDs; incorrect outcome labels; detached semantic overlap, unknown semantic findings, semantic membrane failure; and verifier exceptions. All four schemas passed Draft 2020-12 schema checks and nominal synthetic records validated against them.

This supports bounded implementation correctness for the tested cases. It does not establish complete adversarial closure, external authentication, scientific validity, independent review, or deployed governance enforcement. Full CONTRACT_STRUCTURAL_CLOSURE freeze-ratification should remain conditional on review of these serialization changes and binding a real external verifier. No live PFI has been declared ready.

The next integration operation is to bind a trusted external review adapter and real source/review custody, then rerun candidate-specific readiness. Governance Admission remains deliberately uninstantiated.
