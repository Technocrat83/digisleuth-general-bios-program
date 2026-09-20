# PD-v0.2a — bounded executable predicate solver

Standing: **EXECUTABLE_REFERENCE_PROTOTYPE**. Parent: PD-v0.1 at commit `3e3b461469601dec9d93cf360f7b9ac3353f0ae0`. Scope: `laboratory/inquiry/janusian/pd_v0_2a/`. Constitutional runtime is excluded.

The engine computes exact valuation sets for one declared observable, checks scientific outcome intersections and coverage, and emits deterministic unsigned proof receipts. It never evaluates user code, infers prose meaning, authenticates a reviewer, admits a petition, or executes an investigation.

`PARTITION_PROVEN != PD-v0.2a-READY != PFI_READY != Governance Admission`.

PARTITION_PROVEN is a per-contract result. PD-v0.2a-READY is an engineering assessment of the prototype's bounded capabilities; the included assessment records observed synthetic conformance only. Both remain non-authoritative. Observation invalidity is separate from hypothesis failure.

## Run

Python 3.10+; runtime and tests require only the standard library. No installation or network call is needed.

```sh
python3 test_pd_engine.py
python3 pd_engine.py fixtures/PD01_INTERVAL_PARTITION.json
python3 pd_engine.py fixtures/PD03_SINGLETON_GAP.json
python3 pd_engine.py fixtures/PD09_RESIDUAL_ROUTING.json --observation observation_example.json
```

The CLI writes a deterministic JSON report to stdout. Exit 0 means PARTITION_PROVEN or a valid scientific observation classification; exit 2 means a rejected contract or INVALID observation. Exit code alone is not an outcome classification: inspect the typed disposition. I/O failures remain ordinary process failures.

Tests rewrite synthetic fixture and receipt files and `test_results.json`. They are code-conformance tests, not a scientific investigation. Production solve/classify functions do not write files. The validator and result report confer zero evidence, truth, admission, and execution-authority deltas.

## Seven stages

1. Parse strict UTF-8 JSON and closed AST structures; record unsupported syntax explicitly.
2. Bind every atom to the single observable identity.
3. Validate domain, literal types, finite members, nullability, and Boolean/integer separation.
4. Convert numeric literal units with exact rational factors.
5. Normalize to sorted disjoint interval unions or finite sets, restricted to the domain.
6. Check satisfiability, three pairwise intersections, coverage, residuals, and effective partition after any routing.
7. Emit an unsigned deterministic receipt bound to exact contract bytes and engine bytes.

Failed stages mark later stages NOT_EVALUATED. On rejection the engine emits a diagnostic report, not a successful proof receipt. Declared source-PFI digests are carried as provenance references; PD does not authenticate or read that upstream object. The fixtures include the actual synthetic source bytes matching their declared digest, but that object is not a real PFI_READY record.

## Explicit successor changes

The v0.1 document is preserved unchanged. The user-requested v0.2a operator extension admits nested AND, OR and NOT within depth and node limits, plus IN for numeric and finite values. EMPTY remains available with explicit require_nonempty permission. FINITE_ENUM is the v0.2a serialized spelling of the prior ENUM domain. Unsupported functions, parity, temporal operations, arithmetic expressions, multivariate comparisons, and recursive definitions are rejected.

The primary input is a typed JSON AST. `parse_comparison(text, observable)` is an optional convenience for one numeric comparison, e.g. `latency >= 0.05 SECOND`; it does not accept prose or compound expression text. Compound predicates use AST nodes. Symbolic comparison aliases `<`, `<=`, `=`, `==`, `!=`, `>=`, `>` normalize to LT, LE, EQ, NE, GE, GT.

Scientific outcome slots are exactly SUPPORT, FAIL, ABSTAIN. A scientific INVALID slot or reference to a required observation-validity flag yields LAYER_VIOLATION. Arbitrary undocumented apparatus expressions remain structurally rejected or unbound; no prose detector is claimed.

## Arithmetic and domains

REAL means mathematical real intervals with exact rational endpoints. INTEGER means an integer lattice; fractional comparison thresholds normalize by exact floor/ceiling operations. INTEGER domain bounds must be integral. BOOLEAN excludes integers; FINITE_ENUM has unique, nonempty member tokens.

All numeric input values use decimal **strings**, e.g. `{"decimal":"0.05","unit":"SECOND"}`. JSON numeric tokens, NaN, Infinity, and exponent notation are rejected. No floating-point arithmetic is used. Unbounded domain endpoints are null. Open/closed endpoint flags are explicit.

Units: SECOND, MILLISECOND, MICROSECOND, DIMENSIONLESS; finite domains use NOT_APPLICABLE. Exact conversions target the observable's declared unit. Equal thresholds in different supported units have equal normalized geometry. Changing the observable's own declared unit changes the representation and domain digest; cross-observable-unit receipt equivalence is not asserted. Offset units and inferred conversions are excluded.

## Bounded grammar and limits

Limits are constants in the engine, not candidate overrides: 1 MiB raw input; JSON depth 24; AST depth 8 (root depth 0); 256 nodes per outcome; 64 operands per AND/OR; 256 enum/IN members; 256 digits per decimal; 1,024 normalized intervals. Depth/node/input limits enforce a bounded executable fragment. RESOURCE_LIMIT_EXCEEDED is a rejection, never disjointness. This prototype does not promise a host-independent wall-clock or memory budget; execution still needs host process limits when exposed to untrusted clients.

`pd_contract.schema.json` captures closed serialization shapes. Runtime adds the depth/node/digit limits, binding, unit/type/domain rules, layer rules, and exact mathematical checks. JSON Schema conformance alone proves none of those semantic properties. `build_schema.py` regenerates the schema. Draft 2020-12 metaschema validation and structurally valid named fixture checks were performed using the available validation library; that library is not a solver runtime dependency.

## Geometry and residuals

Three scalar/set intersections are computed. Three additional intersections with INVALID are recorded as tagged-type separation, not scalar calculations. The engine retains the parent disjoint-sum model for invalid records because an absent measurement need not have a value in D_M; a naive Cartesian product requiring every invalid record to contain a metric value would misrepresent missing telemetry.

An overlap returns OVERLAP_FOUND and an exact region and witness. A gap under REJECT_PREDICATE_FAMILY returns DOMAIN_GAP and residual region/witness. ROUTE_TO_ABSTAIN actually unions the residual into effective abstention, then recomputes all three intersections and coverage. Authored and effective regions are both retained. ROUTE_TO_INVALID is forbidden for valid-domain residuals.

Empty regions are allowed only when require_nonempty is false; this permits three outcome labels on a two-value BOOLEAN domain. A forbidden empty region returns PREDICATE_UNSATISFIABLE. Predicate overlap, empty required regions, missing policy, unbound observable, type/unit errors, unsupported fragment and invalid domain remain distinct dispositions. EVALUATOR_INVARIANT_FAILURE is an implementation failure, not a scientific outcome.

## Observation boundary

`classify` accepts contract bytes and a separate observation envelope. It recomputes the partition from those bytes; it does not trust a candidate-supplied receipt or mutable cached proof. Rejected contracts yield CONTRACT_REJECTED, not INVALID.

For a proven contract, all four observation validity fields must equal PASS: measurement_present, unit_valid, provenance_valid, acquisition_successful. Missing, unknown, or failed validity, bad measurement type/unit, and out-of-domain values yield INVALID. An in-domain value then receives exactly one scientific outcome. A zero/multiple-match internal condition yields EVALUATOR_INVARIANT_FAILURE.

Validity flags are host-provided assertions. Their authenticity, measurement calibration, sensor reliability, reviewer identity, and empirical relevance remain unestablished by PD. RAP and later governance integration are deliberately absent. A caller cannot obtain investigation authority from a receipt.

## Deterministic receipts

PD-CJSON-1: sorted object keys; compact separators; ASCII-escaped strings; one trailing LF; reduced rational numerator/denominator strings; canonical sorted interval/set arrays. Derived resource limits are exact JSON integers; no floating-point values occur. This is a local deterministic encoding, not RFC 8785.

Successful receipts contain the engine byte digest, exact input-byte digest, normalized-domain digest, normalized-geometry digest, profiles, limits, authored/effective regions, residual routing, satisfiability, three computed intersections, validity-type separation, stage results, source binding, and zero-authority declarations. They are UNSIGNED_UNAUTHENTICATED. There is no timestamp, nonce, local path or self-digest. Receipt digests are stored separately in the test results and manifest.

Same input bytes and engine bytes produce the same receipt across processes. Byte-different equivalent predicates retain different contract digests while sharing normalized geometry. Engine code changes invalidate engine-bound receipts even if a mathematical normal form remains the same. Engine_digest binds this source file only; it is not an authenticated runtime/dependency attestation.

## Observed verification

- 19/19 named contract fixtures match expected dispositions, including the user's ten requested specimen categories.
- 16/16 unittest methods pass, including independent membership oracles, unit aliases, observation validity, complements, all comparison operators, integer rounding, and cross-process receipt determinism.
- The interval oracle checks 8,192 ordered interval-pair/domain-mode combinations, with every generated endpoint and intervening rational cell represented in its bounded test range. It covers union, intersection and subtraction against direct inequalities rather than reproducing their algorithms. This is bounded testing, not a proof of implementation correctness for all inputs.
- Endpoint collision yields witness 5; singleton gap yields {5}; 0.05 SECOND and 50 MILLISECOND yield equal regions.
- Source fixtures, diagnostic reports and successful receipts are serialized under `fixtures/` and `receipts/`. No real investigation, authentication event, governance admission, or PFI readiness transition occurred.

The engineering gate assessment is eligible to inform Vector B design. It does not promote the engine beyond reference-prototype standing, certify the correctness of Python itself, or independently validate the measurement semantics. PFI_v0.1r's detached semantic-review requirements remain unchanged.
