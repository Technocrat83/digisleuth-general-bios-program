from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Optional


class Coordinate(str, Enum):
    CANON = "Canon"
    COGNITION = "Cognition"
    INFRASTRUCTURE = "Infrastructure"
    EXECUTION = "Execution"


class AdjudicationLabel(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    ABSTAIN = "ABSTAIN"
    INDETERMINATE = "INDETERMINATE"


class FailureLocus(str, Enum):
    TAXONOMY_FAILURE = "TAXONOMY_FAILURE"
    INSTRUMENT_FAILURE = "INSTRUMENT_FAILURE"
    RESOLUTION_FAILURE = "RESOLUTION_FAILURE"


@dataclass(frozen=True)
class SealedTruthRecord:
    trial_id: str
    coordinate: Coordinate
    jurisdiction_target: str
    perturbation_id: str
    provenance_digest: str


@dataclass(frozen=True)
class BlindTrace:
    trial_id: str
    observations: Dict[str, Any]
    trace_digest: str


@dataclass(frozen=True)
class SentinelWitness:
    trial_id: str
    coordinate_hypothesis: Optional[Coordinate]
    confidence: Optional[float]
    abstain: bool = False
    indeterminate: bool = False
    rationale_code: Optional[str] = None


@dataclass(frozen=True)
class JLKLocalization:
    trial_id: str
    jurisdiction_hypothesis: Optional[str]
    boundary_descriptor: Dict[str, Any]
    abstain: bool = False
    indeterminate: bool = False
    rationale_code: Optional[str] = None


@dataclass(frozen=True)
class RoutingProposal:
    trial_id: str
    apparatus_id: Optional[str]
    abstain: bool = False
    indeterminate: bool = False
    rationale_code: Optional[str] = None


@dataclass(frozen=True)
class DiagnosticTuple:
    sentinel: SentinelWitness
    jlk: JLKLocalization
    routing: RoutingProposal


@dataclass(frozen=True)
class AxisAdjudication:
    label: AdjudicationLabel
    detail: str


@dataclass(frozen=True)
class TrialAdjudication:
    trial_id: str
    D_disc: AxisAdjudication
    L_JLK: AxisAdjudication
    R_proposal: AxisAdjudication
    failure_locus: Optional[FailureLocus] = None


def to_dict(obj: Any) -> Dict[str, Any]:
    return asdict(obj)
