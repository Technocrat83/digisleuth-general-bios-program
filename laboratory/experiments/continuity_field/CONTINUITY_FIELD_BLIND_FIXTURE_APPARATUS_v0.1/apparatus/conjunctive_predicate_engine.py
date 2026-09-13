"""Frozen, conjunctive predicate evaluation over uninterpreted residue."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


class PredicateError(RuntimeError):
    pass


@dataclass(frozen=True)
class PredicateResult:
    predicate_id: str
    satisfied: bool


def _resolve(document: Mapping[str, Any], pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise PredicateError("predicate path must be a JSON pointer")
    value: Any = document
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, Mapping) or token not in value:
            raise PredicateError("predicate path is unresolved")
        value = value[token]
    return value


def evaluate_predicates(residue: Mapping[str, Any], predicates: Iterable[Mapping[str, Any]]) -> Sequence[PredicateResult]:
    results = []
    for predicate in predicates:
        pid = str(predicate["predicate_id"])
        actual = _resolve(residue, str(predicate["path"]))
        operation = predicate.get("operation", "equals")
        if operation == "equals":
            satisfied = actual == predicate.get("expected")
        elif operation == "in":
            satisfied = actual in predicate.get("expected", [])
        elif operation == "exists":
            satisfied = True
        else:
            raise PredicateError("unsupported predicate operation")
        results.append(PredicateResult(pid, bool(satisfied)))
    if not results:
        raise PredicateError("empty predicate bundle")
    return tuple(results)


def conjunctive_pass(results: Iterable[PredicateResult]) -> bool:
    values = tuple(result.satisfied for result in results)
    return bool(values) and all(values)
