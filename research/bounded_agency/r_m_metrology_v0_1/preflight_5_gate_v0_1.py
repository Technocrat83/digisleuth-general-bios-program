"""Five-gate mechanical preflight for R_M meter v0.1.

Diagnostic-only. Does not execute B_P/B_M/B_J or traverse scientific transitions.
"""

from copy import deepcopy
import json
from r_m_meter_v0_1 import measure_r_m, canonical_json

BASE = {
    "habitat": {"state_space": ["S0", "S1", "S2"]},
    "objects": [{"id": "O_DIAG", "location": "S0"}],
    "P": {"organs": ["CORE_TRANSFORMER"]},
    "G_M": {"declared_transitions": [["S0", "S1"], ["S1", "S2"]]},
    "R_M": {"status": "UNMEASURED", "realizable_transitions": []},
    "J": {"admitted_transitions": []},
    "execution_token": "WITHHELD",
    "adjudication_authority": "WITHHELD",
}
REQ = {
    "S0->S1": {"required_organs": ["CORE_TRANSFORMER"]},
    "S1->S2": {"required_organs": ["AUXILIARY_TRANSFORMER"]},
}
PROV = {
    "source_commit": "64cd1c8d6dbb72e9b920f696509ce0979d3f44dc",
    "fixture_blob": "68a290754eb4b1a785f0b6850741ff42f07bcf4d",
    "operator_blob": "10127e04b921709325a20fd1ec86fc051f32bb54",
    "purpose": "MECHANICAL_PREFLIGHT_ONLY",
}


def run():
    specimen = deepcopy(BASE)
    frozen = deepcopy(specimen)
    o1 = measure_r_m(specimen, REQ, provenance=PROV)
    o2 = measure_r_m(specimen, REQ, provenance=PROV)
    unresolved = measure_r_m(specimen, {}, provenance=PROV)

    required_fields = {
        "apparatus_id", "input_digest_before", "input_digest_after", "side_effect_free",
        "traversal_count", "jurisdiction_mutation_count", "witnesses",
        "realizable_transitions", "nonrealizable_transitions", "unresolved_transitions", "provenance"
    }
    o1d = o1.to_dict()

    G1 = specimen == frozen and o1.side_effect_free and o1.traversal_count == 0 and o1.jurisdiction_mutation_count == 0
    G2 = canonical_json(o1.to_dict()) == canonical_json(o2.to_dict())
    G3 = len(unresolved.unresolved_transitions) == len(BASE["G_M"]["declared_transitions"]) and len(unresolved.nonrealizable_transitions) == 0
    G4 = o1.input_digest_before == o1.input_digest_after and all(PROV.get(k) for k in ("source_commit", "fixture_blob", "operator_blob", "purpose"))
    forbidden = {"scientific_verdict", "geometry_classification", "grant_jurisdiction", "pp", "scientific_evidence"}
    G5 = required_fields.issubset(o1d.keys()) and not (forbidden & set(o1d.keys()))

    gates = {"G1": G1, "G2": G2, "G3": G3, "G4": G4, "G5": G5}
    if not G1:
        standing = "METROLOGICAL_SIDE_EFFECT_HALT"
    elif all(gates.values()):
        standing = "QUALIFIED_MECHANICAL_METER_AWAITING_SEPARATE_SCIENTIFIC_ADMISSION"
    else:
        standing = "PREFLIGHT_HALT"

    return {
        "artifact_id": "R_M_DYNAMIC_MEASUREMENT_APPARATUS_PREFLIGHT_v0.1",
        "gates": gates,
        "standing": standing,
        "scientific_chamber_execution": "NOT_OCCURRED",
        "scientific_adjudication": "WITHHELD",
        "scientific_evidence_delta": 0,
        "pp": "BLOCKED",
        "diagnostic_observation": o1d,
        "abstention_observation": unresolved.to_dict(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
