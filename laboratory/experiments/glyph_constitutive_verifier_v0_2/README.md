# GLYPH v0.2 candidate addendum and implementation

Parent: 5330f1605878dc7993485496f5adcddd57aa82f3. v0.1 files remain untouched.

Standing: CANDIDATE / STATICALLY_INSPECTED / NO_SPECIMENS_EXECUTED.

This is a five-specimen amendment implementation, not a complete replacement for the 18-specimen battery. The independent amended oracle covers S04, S09, S10, S11 and S18. No expectation is inferred from runtime output.

- verifier_v02.py implements structural precedence, real evaluator calls and ordinary exception classification, post-observation contract drift checks, full residue capture, and candidate receipts.
- instrumentation_v02.py defines the five fixtures and the explicitly scoped mock sink. Its runner and CLI remain locked.
- amended_expectations.json declares expectations before execution.
- v0.2_PREREGISTRATION_ADDENDUM.yaml uses JSON syntax, a valid YAML representation, to make scalar typing unambiguous.

S10 binds integer milliseconds: source 100, candidate 120, epsilon 5. The initial FAIL residue is retained before the injection widens epsilon to 50; the verifier must reject the drift rather than reevaluate under the relaxed criterion.

S09 and S11 now require INVALID_CONTRACT with distinct reasons. This intentionally differs from the immutable v0.1 oracle. Structural failure prevents binding checks and evaluator invocation.

S04 catches ordinary Exception in the verifier. It does not contain process termination or hanging evaluators. A host must supply resource limits and process supervision.

S18 checks exact mock state equality and hash equality and records the denied attempt separately. The changed attempt log is not part of the target-state equality claim. No inference to general authority leakage is permitted.

Containment is specified, not implemented or verified. Loopback-only networking revises the older no-network requirement and still permits local services unless further restricted. A read-only source directory alone is insufficient to prevent writes elsewhere. No virtual environment or Python flag is claimed to be an OS sandbox.

This commit does not open the execution gate. A complete detached runner, admitted containment and resource limits, and a recorded gate transition are still required. Do not import/call the fixture hooks as a substitute for that gate.

Receipt digests are unkeyed content bindings, not issuer authentication. Receiver/source/evaluator trust is supplied externally. The candidate receipt profile is explicitly versioned v0.2; it does not claim production conformance.
