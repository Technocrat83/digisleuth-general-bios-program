"""Adjudication boundary: receives only Y_i and a precommitted predicate bundle."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .blind_serializer import canonical_json
from .conjunctive_predicate_engine import PredicateResult, conjunctive_pass, evaluate_predicates


class PredicateCommitmentError(RuntimeError):
    pass


@dataclass(frozen=True)
class ChamberVerdict:
    predicate_bundle_id: str
    residue_sha256: str
    predicate_results: Sequence[PredicateResult]
    passed: bool


def adjudicate(y_i: bytes, predicate_bundle: Mapping[str, Any]) -> ChamberVerdict:
    declared_hash = predicate_bundle.get("bundle_hash")
    committed_material = {
        "bundle_id": predicate_bundle.get("bundle_id"),
        "predicates": predicate_bundle.get("predicates"),
    }
    observed_hash = hashlib.sha256(canonical_json(committed_material)).hexdigest()
    if declared_hash != observed_hash:
        raise PredicateCommitmentError("predicate bundle commitment mismatch")
    residue = json.loads(y_i)
    if not isinstance(residue, Mapping):
        raise ValueError("residue must be an object")
    results = evaluate_predicates(residue, predicate_bundle["predicates"])
    return ChamberVerdict(
        predicate_bundle_id=str(predicate_bundle["bundle_id"]),
        residue_sha256=hashlib.sha256(y_i).hexdigest(),
        predicate_results=results,
        passed=conjunctive_pass(results),
    )
