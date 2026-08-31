"""GENERAL BIOS bounded-agency synthetic intervention operators v0.1.

Definitions only. No intervention is executed on import.
Scientific adjudication is intentionally absent.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Tuple

DeltaType = Literal["DIRECT", "INDUCED", "UNRESOLVED"]
State = Dict[str, Any]


@dataclass(frozen=True)
class InterventionRecord:
    chamber: str
    direct_target: str
    before: State
    staged: State
    direct_surfaces: Tuple[str, ...]
    prohibited_direct_surfaces: Tuple[str, ...]


def _copy(state: State) -> State:
    return deepcopy(state)


def stage_B_P(state: State) -> InterventionRecord:
    """Stage physiology-only direct mutation.

    Directly changes P only. G_M and J are conserved by the operator.
    R_M is not computed or mutated here; any later R_M delta must be measured
    and typed separately as INDUCED or UNRESOLVED.
    """
    staged = _copy(state)
    organs: List[str] = list(staged["P"]["organs"])
    if "AUXILIARY_TRANSFORMER" not in organs:
        organs.append("AUXILIARY_TRANSFORMER")
    staged["P"]["organs"] = organs
    return InterventionRecord(
        chamber="B_P",
        direct_target="P",
        before=_copy(state),
        staged=staged,
        direct_surfaces=("P",),
        prohibited_direct_surfaces=("G_M", "R_M", "J"),
    )


def stage_B_M(state: State) -> InterventionRecord:
    """Stage declared-maneuver-topology-only direct mutation.

    Directly adds S2 -> S3 to G_M. It does not assert that the transition is
    realizable and does not alter P, R_M, or J.
    """
    staged = _copy(state)
    edges = [list(edge) for edge in staged["G_M"]["declared_transitions"]]
    candidate = ["S2", "S3"]
    if candidate not in edges:
        edges.append(candidate)
    staged["G_M"]["declared_transitions"] = edges
    return InterventionRecord(
        chamber="B_M",
        direct_target="G_M",
        before=_copy(state),
        staged=staged,
        direct_surfaces=("G_M",),
        prohibited_direct_surfaces=("P", "R_M", "J"),
    )


def stage_B_J(state: State) -> InterventionRecord:
    """Stage jurisdiction-only direct mutation.

    Admits one already-declared transition without changing P, G_M, or R_M.
    This stages admission state only; it does not execute the transition.
    """
    staged = _copy(state)
    admitted = [list(edge) for edge in staged["J"]["admitted_transitions"]]
    candidate = ["S0", "S1"]
    if candidate not in admitted:
        admitted.append(candidate)
    staged["J"]["admitted_transitions"] = admitted
    return InterventionRecord(
        chamber="B_J",
        direct_target="J",
        before=_copy(state),
        staged=staged,
        direct_surfaces=("J",),
        prohibited_direct_surfaces=("P", "G_M", "R_M"),
    )


def direct_surface_delta(record: InterventionRecord, surface: str) -> bool:
    """Mechanical comparison helper for future preflight only."""
    return record.before[surface] != record.staged[surface]


# Deliberately no main block, no fixture loading, no execution loop, no
# reachability evaluator, and no scientific verdict logic.
