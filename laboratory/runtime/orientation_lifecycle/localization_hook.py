from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import FrozenSet, Iterable, Mapping, Sequence
import re
from canonical_encoding import evidence_digest

HEX128 = re.compile(r"^0x[0-9a-fA-F]{32}$")

class LocalizationStanding(str, Enum):
    LOCALIZED = "LOCALIZED"
    NO_MATERIAL_INTERSECTION = "NO_MATERIAL_INTERSECTION"
    UNRESOLVED = "UNRESOLVED"

class AffectedSurface(str, Enum):
    PROVENANCE = "PROVENANCE"
    PLACEMENT = "PLACEMENT"
    GRAPH_TOPOLOGY = "GRAPH_TOPOLOGY"
    JURISDICTION = "JURISDICTION"
    BOUNDARY = "BOUNDARY"
    STATE_VECTOR = "STATE_VECTOR"
    EPOCH = "EPOCH"
    AUTHORITY_USE = "AUTHORITY_USE"
    ADJACENCY_STRUCTURE = "ADJACENCY_STRUCTURE"

@dataclass(frozen=True)
class FieldDelta:
    object_id: str
    delta_id: str
    prior_orientation_hash: str
    prior_graph_hash: str
    current_graph_hash: str
    prior_jurisdiction_hash: str
    current_jurisdiction_hash: str
    prior_provenance_hash: str
    current_provenance_hash: str
    prior_placement_hash: str
    current_placement_hash: str
    prior_state_hash: str
    current_state_hash: str
    prior_boundary_hash: str
    current_boundary_hash: str
    prior_epoch: str
    current_epoch: str
    adjacency_changed: bool = False
    authority_use_attempted: bool = False
    evidence_complete: bool = True

@dataclass(frozen=True)
class LocalizationPolicy:
    causal_members_by_surface: Mapping[str, Sequence[str]]
    jurisdiction_members_by_surface: Mapping[str, Sequence[str]]
    unresolved_dependency_by_surface: Mapping[str, Sequence[str]]

@dataclass(frozen=True)
class DeltaLocalization:
    object_id: str
    delta_id: str
    standing: LocalizationStanding
    causal_cone: FrozenSet[str]
    jurisdictional_cone: FrozenSet[str]
    affected_surfaces: FrozenSet[str]
    unresolved_dependencies: FrozenSet[str]
    evidence_digest: str
    epoch: str

    def to_dict(self):
        d = asdict(self)
        for k in ("causal_cone","jurisdictional_cone","affected_surfaces","unresolved_dependencies"):
            d[k] = sorted(d[k])
        d["standing"] = self.standing.value
        return d

def _changed(delta: FieldDelta) -> FrozenSet[str]:
    out=set()
    if delta.prior_provenance_hash != delta.current_provenance_hash: out.add(AffectedSurface.PROVENANCE.value)
    if delta.prior_placement_hash != delta.current_placement_hash: out.add(AffectedSurface.PLACEMENT.value)
    if delta.prior_graph_hash != delta.current_graph_hash: out.add(AffectedSurface.GRAPH_TOPOLOGY.value)
    if delta.prior_jurisdiction_hash != delta.current_jurisdiction_hash: out.add(AffectedSurface.JURISDICTION.value)
    if delta.prior_state_hash != delta.current_state_hash: out.add(AffectedSurface.STATE_VECTOR.value)
    if delta.prior_boundary_hash != delta.current_boundary_hash: out.add(AffectedSurface.BOUNDARY.value)
    if delta.adjacency_changed: out.add(AffectedSurface.ADJACENCY_STRUCTURE.value)
    if delta.prior_epoch != delta.current_epoch: out.add(AffectedSurface.EPOCH.value)
    if delta.authority_use_attempted: out.add(AffectedSurface.AUTHORITY_USE.value)
    return frozenset(out)

def _validate_jurisdiction_ids(ids: Iterable[str]) -> None:
    for item in ids:
        if not HEX128.fullmatch(item):
            raise ValueError(f"JURISDICTION_ID_WIDTH_INVALID:{item}")

def localize(delta: FieldDelta, policy: LocalizationPolicy) -> DeltaLocalization:
    surfaces = _changed(delta)
    digest = evidence_digest(delta)
    if not delta.evidence_complete:
        unresolved=set()
        for s in surfaces:
            unresolved.update(policy.unresolved_dependency_by_surface.get(s, (f"UNRESOLVED:{s}",)))
        return DeltaLocalization(delta.object_id, delta.delta_id, LocalizationStanding.UNRESOLVED, frozenset(), frozenset(), surfaces, frozenset(unresolved), digest, delta.current_epoch)
    causal=set(); jurisdictional=set()
    for s in surfaces:
        causal.update(policy.causal_members_by_surface.get(s, ()))
        jurisdictional.update(policy.jurisdiction_members_by_surface.get(s, ()))
    _validate_jurisdiction_ids(jurisdictional)
    standing = LocalizationStanding.LOCALIZED if surfaces else LocalizationStanding.NO_MATERIAL_INTERSECTION
    return DeltaLocalization(delta.object_id, delta.delta_id, standing, frozenset(causal), frozenset(jurisdictional), surfaces, frozenset(), digest, delta.current_epoch)

# Constitutionally absent: withdraw_orientation, repair_orientation, grant_authority,
# change_jurisdiction, admit_object, execute_object.
