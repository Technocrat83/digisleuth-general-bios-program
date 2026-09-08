from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import FrozenSet
import hashlib, json
from localization_hook import DeltaLocalization, LocalizationStanding

class OrientationLifecycle(str, Enum):
    CURRENT="CURRENT"
    SUSPENDED="SUSPENDED"
    WITHDRAWN="WITHDRAWN"

@dataclass(frozen=True)
class PriorOrientation:
    orientation_id: str
    object_id: str
    orientation_digest: str
    historically_valid: bool
    epistemic_standing_token: str

@dataclass(frozen=True)
class InvalidationWitness:
    witness_id: str
    object_id: str
    prior_orientation_id: str
    prior_orientation_digest: str
    localization_evidence_digest: str
    lifecycle: OrientationLifecycle
    affected_surfaces: FrozenSet[str]
    historical_orientation_preserved: bool
    epistemic_standing_changed: bool
    repair_attempted: bool
    auto_reorientation: bool
    authority_effect: str
    execution_effect: str

    def to_dict(self):
        d=asdict(self)
        d["lifecycle"]=self.lifecycle.value
        d["affected_surfaces"]=sorted(self.affected_surfaces)
        return d

@dataclass(frozen=True)
class OrientationEvaluation:
    lifecycle: OrientationLifecycle
    witness: InvalidationWitness | None

ORIENTATION_RELEVANT = frozenset({"PROVENANCE","PLACEMENT","GRAPH_TOPOLOGY","JURISDICTION","BOUNDARY","STATE_VECTOR","EPOCH","ADJACENCY_STRUCTURE","AUTHORITY_USE"})
STANDING_NEUTRAL_SURFACES = frozenset({"STATE_VECTOR","AUTHORITY_USE"})

def evaluate(prior: PriorOrientation, loc: DeltaLocalization) -> OrientationEvaluation:
    if loc.standing == LocalizationStanding.NO_MATERIAL_INTERSECTION:
        return OrientationEvaluation(OrientationLifecycle.CURRENT, None)
    if loc.standing == LocalizationStanding.UNRESOLVED:
        lifecycle=OrientationLifecycle.SUSPENDED
    else:
        if "AUTHORITY_USE" in loc.affected_surfaces:
            lifecycle = OrientationLifecycle.SUSPENDED
        else:
            lifecycle = OrientationLifecycle.WITHDRAWN if (set(loc.affected_surfaces) & ORIENTATION_RELEVANT) else OrientationLifecycle.CURRENT
    if lifecycle == OrientationLifecycle.CURRENT:
        return OrientationEvaluation(lifecycle, None)
    payload={"object_id":prior.object_id,"prior":prior.orientation_digest,"loc":loc.evidence_digest,"lifecycle":lifecycle.value}
    wid=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    witness=InvalidationWitness(wid, prior.object_id, prior.orientation_id, prior.orientation_digest, loc.evidence_digest, lifecycle, frozenset(loc.affected_surfaces), True, False, False, False, "NONE", "BLOCKED")
    return OrientationEvaluation(lifecycle,witness)

# Constitutional negative outcomes are lawful outcomes, not exceptions.
