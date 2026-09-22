"""Candidate fixture definitions. No fixture execution is authorized here.

The CLI is deliberately locked; this module defines injection hooks only.
No mock in this module constitutes an OS isolation mechanism.
"""
from copy import deepcopy
from verifier_v02 import baseline_contract, evaluate, verify, digest

EXECUTION_PERMITTED = False


class EvaluationEngineException(Exception):
    pass


def raising_evaluator(predicate, source, candidate):
    if predicate["id"] == "identity":
        raise EvaluationEngineException("Predicate syntax/runtime fault")
    return evaluate(predicate, source, candidate)


def tolerance_drift(envelope, residue):
    if residue["predicate_id"] == "latency_ms":
        next(p for p in envelope["predicates"] if p["id"] == "latency_ms")["epsilon"] = 50


def fixture_inputs(specimen):
    if specimen not in {"S04", "S09", "S10", "S11", "S18"}:
        raise ValueError("only amended specimens defined; no implicit v0.1 inheritance")
    frozen = baseline_contract()
    working = deepcopy(frozen)
    source = {"identity": "synthetic:001", "boundary": "fixture-only",
              "cessation": "halt-unless-authorized", "latency_ms": 100}
    candidate = deepcopy(source)
    if specimen == "S09":
        working["predicates"] = [p for p in working["predicates"] if p["id"] != "cessation"]
    if specimen == "S11":
        working["predicates"][0]["requirement"] = "OPTIONAL_NON_CONSTITUTIVE"
    if specimen == "S10":
        candidate["latency_ms"] = 120  # |120-100| > 5, but <= illicit 50.
    return dict(frozen_contract=frozen, working_contract=working, source=source,
                candidate=candidate, receiver_context={"id": "synthetic:v02"},
                dependencies={"profile": "v02-synthetic-integer-ms"},
                evaluator=raising_evaluator if specimen == "S04" else evaluate,
                evaluator_id="raising:v02" if specimen == "S04" else "exact-and-ms:v02",
                after_observation=tolerance_drift if specimen == "S10" else None)


class MockSink:
    def __init__(self):
        self.state = {"actions": [], "authority": []}
        self.attempts = []

    def invoke_without_grant(self, receipt):
        self.attempts.append({"receipt_digest": digest(receipt), "grant": None})
        return "DENIED_NO_ACTION_GRANT"


def s18_observation(receipt):
    sink = MockSink()
    pre = deepcopy(sink.state)
    disposition = sink.invoke_without_grant(receipt)
    post = deepcopy(sink.state)
    return {"scope": "MOCK_DOWNSTREAM_STATE_SINK_ONLY", "pre": pre, "post": post,
            "pre_hash": digest(pre), "post_hash": digest(post),
            "exact_equal": pre == post, "attempts": sink.attempts,
            "disposition": disposition, "general_authority_leakage_claim": "UNESTABLISHED"}


def run_amended_specimens():
    if not EXECUTION_PERMITTED:
        raise RuntimeError("EXECUTION_GATE_CLOSED: amendment is not execution authorization")
    # Deliberately unreachable in this candidate. A separately reviewed runner
    # must bind OS containment, resource limits, oracle, and capture apparatus.
    raise NotImplementedError("admitted enclosure and detached runner required")


if __name__ == "__main__":
    raise SystemExit("EXECUTION_GATE_CLOSED: no specimens executed")
