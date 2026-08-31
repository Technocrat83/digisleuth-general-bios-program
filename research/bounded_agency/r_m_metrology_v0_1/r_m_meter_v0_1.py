"""R_M dynamic measurement apparatus v0.1.

Read-only counterfactual realizability meter. It does not execute transitions,
mutate the supplied specimen, grant jurisdiction, or adjudicate geometry.

Critical rule: missing or incomplete prerequisite declarations yield UNRESOLVED,
never NONREALIZABLE.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Literal, Mapping, Sequence, Tuple

State = Dict[str, Any]
Status = Literal["REALIZABLE", "NONREALIZABLE", "UNRESOLVED"]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EdgeWitness:
    edge: Tuple[str, str]
    status: Status
    declared: bool
    endpoints_present: bool
    prerequisites_declared: bool
    required_organs: Tuple[str, ...]
    missing_organs: Tuple[str, ...]
    source_counterfactually_reachable: bool | None
    reason: str


@dataclass(frozen=True)
class RMObservation:
    apparatus_id: str
    input_digest_before: str
    input_digest_after: str
    side_effect_free: bool
    traversal_count: int
    jurisdiction_mutation_count: int
    witnesses: Tuple[EdgeWitness, ...]
    realizable_transitions: Tuple[Tuple[str, str], ...]
    nonrealizable_transitions: Tuple[Tuple[str, str], ...]
    unresolved_transitions: Tuple[Tuple[str, str], ...]
    provenance: Mapping[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _edge_tuples(raw_edges: Iterable[Sequence[str]]) -> Tuple[Tuple[str, str], ...]:
    out: List[Tuple[str, str]] = []
    for edge in raw_edges:
        if len(edge) != 2:
            continue
        out.append((str(edge[0]), str(edge[1])))
    return tuple(out)


def _counterfactual_reachable_sources(
    origin: str,
    declared_edges: Tuple[Tuple[str, str], ...],
    edge_requirements: Mapping[str, Any],
    organs: set[str],
) -> set[str]:
    """Graph closure by prerequisite satisfaction only; no specimen traversal."""
    reached = {origin}
    changed = True
    while changed:
        changed = False
        for src, dst in declared_edges:
            key = f"{src}->{dst}"
            req = edge_requirements.get(key)
            if not isinstance(req, Mapping) or "required_organs" not in req:
                continue
            required = {str(x) for x in req.get("required_organs", [])}
            if src in reached and required.issubset(organs) and dst not in reached:
                reached.add(dst)
                changed = True
    return reached


def measure_r_m(
    specimen: State,
    edge_requirements: Mapping[str, Any],
    *,
    provenance: Mapping[str, str],
) -> RMObservation:
    """Measure realizability counterfactually without traversing or mutating specimen."""
    before = deepcopy(specimen)
    before_digest = digest(before)

    habitat_states = {str(s) for s in specimen.get("habitat", {}).get("state_space", [])}
    organs = {str(o) for o in specimen.get("P", {}).get("organs", [])}
    declared_edges = _edge_tuples(specimen.get("G_M", {}).get("declared_transitions", []))
    objects = specimen.get("objects", [])
    origin = None
    if len(objects) == 1 and isinstance(objects[0], Mapping):
        origin = objects[0].get("location")
        if origin is not None:
            origin = str(origin)

    reachable_sources: set[str] | None = None
    if origin is not None:
        reachable_sources = _counterfactual_reachable_sources(origin, declared_edges, edge_requirements, organs)

    witnesses: List[EdgeWitness] = []
    for edge in declared_edges:
        src, dst = edge
        key = f"{src}->{dst}"
        endpoints_present = src in habitat_states and dst in habitat_states
        req = edge_requirements.get(key)
        prerequisites_declared = isinstance(req, Mapping) and "required_organs" in req
        required_organs: Tuple[str, ...] = tuple()
        missing_organs: Tuple[str, ...] = tuple()
        source_reachable: bool | None = None

        if not endpoints_present:
            status: Status = "NONREALIZABLE"
            reason = "EDGE_ENDPOINT_OUTSIDE_HABITAT"
        elif not prerequisites_declared:
            status = "UNRESOLVED"
            reason = "PREREQUISITES_UNDECLARED"
        elif origin is None or reachable_sources is None:
            status = "UNRESOLVED"
            reason = "OBJECT_ORIGIN_UNRESOLVED"
        else:
            required_organs = tuple(sorted(str(x) for x in req.get("required_organs", [])))
            missing_organs = tuple(sorted(set(required_organs) - organs))
            source_reachable = src in reachable_sources
            if missing_organs:
                status = "NONREALIZABLE"
                reason = "REQUIRED_ORGAN_ABSENT"
            elif not source_reachable:
                status = "NONREALIZABLE"
                reason = "SOURCE_NOT_COUNTERFACTUALLY_REACHABLE"
            else:
                status = "REALIZABLE"
                reason = "DECLARED_PREREQUISITES_SATISFIED"

        witnesses.append(
            EdgeWitness(
                edge=edge,
                status=status,
                declared=True,
                endpoints_present=endpoints_present,
                prerequisites_declared=prerequisites_declared,
                required_organs=required_organs,
                missing_organs=missing_organs,
                source_counterfactually_reachable=source_reachable,
                reason=reason,
            )
        )

    after_digest = digest(specimen)
    side_effect_free = before == specimen and before_digest == after_digest

    return RMObservation(
        apparatus_id="R_M_DYNAMIC_MEASUREMENT_APPARATUS_v0.1",
        input_digest_before=before_digest,
        input_digest_after=after_digest,
        side_effect_free=side_effect_free,
        traversal_count=0,
        jurisdiction_mutation_count=0,
        witnesses=tuple(witnesses),
        realizable_transitions=tuple(w.edge for w in witnesses if w.status == "REALIZABLE"),
        nonrealizable_transitions=tuple(w.edge for w in witnesses if w.status == "NONREALIZABLE"),
        unresolved_transitions=tuple(w.edge for w in witnesses if w.status == "UNRESOLVED"),
        provenance=dict(provenance),
    )
