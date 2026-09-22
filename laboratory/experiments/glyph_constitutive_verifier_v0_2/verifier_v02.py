"""Unexecuted v0.2 candidate. Pure bounded evaluation; no I/O or action API.

The host must enforce deadlines and containment. Exception classification does
not interrupt an evaluator that hangs, exits the process, or exhausts memory.
"""
from copy import deepcopy
import hashlib
import json

OUTCOMES = {"PASS", "FAIL", "UNKNOWN", "ERROR"}
STANDING = {"PASS": "VERIFIED", "FAIL": "REFUTED",
            "UNKNOWN": "INDETERMINATE", "ERROR": "INDETERMINATE"}


def serialize(value):
    def check(x):
        if x is None or type(x) in (str, bool, int):
            return
        if type(x) is list:
            for v in x:
                check(v)
            return
        if type(x) is dict and all(type(k) is str for k in x):
            for v in x.values():
                check(v)
            return
        raise ValueError("unsupported serialized value")
    check(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return "sha256:" + hashlib.sha256(serialize(value)).hexdigest()


def baseline_contract():
    return {"revision": "0.2", "predicates": [
        {"id": "identity", "requirement": "REQUIRED", "mode": "EXACT"},
        {"id": "boundary", "requirement": "REQUIRED", "mode": "EXACT"},
        {"id": "cessation", "requirement": "REQUIRED", "mode": "EXACT"},
        {"id": "latency_ms", "requirement": "REQUIRED", "mode": "ABSOLUTE_INTEGER",
         "unit": "ms", "epsilon": 5}]}


REQUIRED = ("identity", "boundary", "cessation", "latency_ms")


def structural_reason(contract):
    if type(contract) is not dict or set(contract) != {"revision", "predicates"}:
        return "INVALID_CONTRACT_SHAPE"
    if contract["revision"] != "0.2" or type(contract["predicates"]) is not list:
        return "INVALID_CONTRACT_SHAPE"
    predicates = contract["predicates"]
    if not predicates or any(type(p) is not dict for p in predicates):
        return "EMPTY_OR_INVALID_PREDICATES"
    ids = [p.get("id") for p in predicates]
    if any(type(pid) is not str for pid in ids) or len(set(ids)) != len(ids):
        return "DUPLICATE_OR_INVALID_PREDICATE_ID"
    if set(ids) != set(REQUIRED):
        return "DETERMINISTIC_STRUCTURAL_INVALIDITY"
    if any(p.get("requirement") != "REQUIRED" for p in predicates):
        return "SCHEMA_MODALITY_REJECTION"
    for p in predicates:
        if p["id"] == "latency_ms":
            if (set(p) != {"id", "requirement", "mode", "unit", "epsilon"}
                    or p["mode"] != "ABSOLUTE_INTEGER" or p["unit"] != "ms"
                    or type(p["epsilon"]) is not int or p["epsilon"] < 0):
                return "INVALID_TOLERANCE_DECLARATION"
        elif set(p) != {"id", "requirement", "mode"} or p["mode"] != "EXACT":
            return "INVALID_EQUIVALENCE_DECLARATION"
    return None


def evaluate(predicate, source, candidate):
    if predicate["mode"] == "ABSOLUTE_INTEGER":
        if type(source) is not int or type(candidate) is not int:
            raise TypeError("temporal values must be integer milliseconds")
        return abs(candidate - source) <= predicate["epsilon"]
    return serialize(source) == serialize(candidate)


def verify(*, frozen_contract, working_contract, source, candidate,
           receiver_context, dependencies, evaluator, evaluator_id,
           after_observation=None):
    """Caller binds evaluator identity and source externally; no issuer auth.

    after_observation is an explicit laboratory injection, not production API.
    It receives the working envelope and a COPY of the captured residue.
    """
    frozen = deepcopy(frozen_contract)
    source, candidate = deepcopy(source), deepcopy(candidate)
    frozen_digest = digest(frozen)
    residues, events = [], []

    def result(status, reason=None, receipt=None):
        return {"status": status, "reason": reason, "residues": deepcopy(residues),
                "events": deepcopy(events), "receipt": receipt,
                "authority_effect": "NONE"}

    if structural_reason(frozen):
        return result("INVALID_CONTRACT", "INVALID_UPSTREAM_CONTRACT")
    reason = structural_reason(working_contract)
    events.append({"stage": "STRUCTURAL_PRECHECK", "reason": reason})
    if reason:
        return result("INVALID_CONTRACT", reason)
    events.append({"stage": "BINDING_CHECK"})
    if digest(working_contract) != frozen_digest:
        return result("CONTRACT_BINDING_MISMATCH", "ENVELOPE_DRIFT_BEFORE_EVALUATION")

    for predicate in frozen["predicates"]:
        pid = predicate["id"]
        evidence = {"criterion_digest": digest(predicate), "evaluator_id": evaluator_id,
                    "source_digest": digest(source[pid]) if pid in source else None,
                    "candidate_digest": digest(candidate[pid]) if pid in candidate else None}
        diagnostic = None
        if pid not in source or pid not in candidate:
            outcome, reason = "UNKNOWN", "VALUE_UNRESOLVED"
        else:
            try:
                decision = evaluator(deepcopy(predicate), deepcopy(source[pid]), deepcopy(candidate[pid]))
                if type(decision) is not bool:
                    raise TypeError("evaluator must return bool")
                outcome = "PASS" if decision else "FAIL"
                reason = "CRITERION_SATISFIED" if decision else "CRITERION_REFUTED"
            except Exception as exc:
                outcome, reason = "ERROR", "DIAGNOSTIC_ERROR"
                diagnostic = {"type": type(exc).__name__, "message": str(exc)}
        residue = {"predicate_id": pid, "outcome": outcome, "reason_code": reason,
                   "evidence_binding": evidence, "standing": STANDING[outcome],
                   "prescribed_disposition": "NONE" if outcome == "PASS" else "HALT_FORWARD"}
        residues.append(residue)
        events.append({"stage": "OBSERVATION_CAPTURED", "predicate_id": pid,
                       "residue_digest": digest(residue), "diagnostic": diagnostic})
        if after_observation:
            after_observation(working_contract, deepcopy(residue))
        if digest(working_contract) != frozen_digest:
            old = next(p for p in frozen["predicates"] if p["id"] == "latency_ms")
            new = next((p for p in working_contract.get("predicates", [])
                        if p.get("id") == "latency_ms"), {})
            reason = ("CONTRACT_TOLERANCE_VIOLATION" if new.get("epsilon") != old["epsilon"]
                      else "POST_OBSERVATION_ENVELOPE_DRIFT")
            events.append({"stage": "POST_OBSERVATION_BINDING_CHECK", "reason": reason,
                           "frozen_digest": frozen_digest, "observed_digest": digest(working_contract)})
            return result("CONTRACT_BINDING_MISMATCH", reason)
    outcomes = [r["outcome"] for r in residues]
    if "FAIL" in outcomes:
        return result("NONCONFORMANT")
    if any(o in {"ERROR", "UNKNOWN"} for o in outcomes):
        return result("INDETERMINATE")
    body = {"schema_version": "glyph.scoped_receipt.v0.2.candidate",
            "contract_digest": frozen_digest, "source_digest": digest(source),
            "candidate_digest": digest(candidate), "receiver_digest": digest(receiver_context),
            "dependency_digest": digest(dependencies), "evaluator_id": evaluator_id,
            "predicate_residues": sorted(residues, key=lambda r: r["predicate_id"]),
            "authority_effect": "NONE"}
    return result("CONFORMANT", receipt={"body": body, "body_digest": digest(body)})
