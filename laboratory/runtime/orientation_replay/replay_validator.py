from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Any
import pathlib, sys

LIFECYCLE_DIR = pathlib.Path(__file__).resolve().parents[1] / "orientation_lifecycle"
if str(LIFECYCLE_DIR) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE_DIR))

from canonical_encoding import evidence_digest, ENCODING_ID
from localization_hook import FieldDelta, LocalizationPolicy, localize
from orientation_monitor import PriorOrientation, evaluate, OrientationLifecycle

REPLAY_CONTRACT_ID = "ORIENTATION_INVALIDATION_REPLAY_VALIDATOR_v0.1"
LOCALIZATION_RULE_ID = "JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1"
MONITOR_RULE_ID = "ORIENTATION_INVALIDATION_MONITOR_v0.1"

class ReplayAxis(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"

@dataclass(frozen=True)
class ReplayResult:
    input_binding: ReplayAxis
    digest_binding: ReplayAxis
    localization_reconstruction: ReplayAxis
    disposition_reconstruction: ReplayAxis
    repair_attempted: ReplayAxis
    violations: tuple[str, ...] = ()

    @property
    def qualification_pass(self) -> bool:
        return all(x == ReplayAxis.PASS for x in (
            self.input_binding,
            self.digest_binding,
            self.localization_reconstruction,
            self.disposition_reconstruction,
            self.repair_attempted,
        ))

    def to_dict(self) -> dict[str, object]:
        return {
            "INPUT_BINDING": self.input_binding.value,
            "DIGEST_BINDING": self.digest_binding.value,
            "LOCALIZATION_RECONSTRUCTION": self.localization_reconstruction.value,
            "DISPOSITION_RECONSTRUCTION": self.disposition_reconstruction.value,
            "REPAIR_ATTEMPTED": self.repair_attempted.value,
            "QUALIFICATION_PASS": self.qualification_pass,
            "CANONICAL_ENCODING": ENCODING_ID,
            "REPLAY_CONTRACT": REPLAY_CONTRACT_ID,
            "VIOLATIONS": list(self.violations),
        }

def _merge(*xs: list[str]) -> tuple[str, ...]:
    out=[]
    for group in xs:
        for x in group:
            if x not in out:
                out.append(x)
    return tuple(out)

def _input_axis(delta: FieldDelta, prior: PriorOrientation, witness: Mapping[str, Any]):
    violations=[]
    required = (
        "object_id", "delta_id", "prior_orientation_id", "prior_orientation_digest",
        "canonical_encoding_id", "localization_rule_id", "monitor_rule_id",
    )
    if any(witness.get(k) in (None, "") for k in required):
        return ReplayAxis.UNRESOLVED, ["INPUT_BINDING_FIELD_MISSING"]

    if witness["object_id"] != delta.object_id: violations.append("WITNESS_OBJECT_ID_MISMATCH")
    if prior.object_id != delta.object_id: violations.append("PRIOR_OBJECT_ID_MISMATCH")
    if witness["delta_id"] != delta.delta_id: violations.append("WITNESS_DELTA_ID_MISMATCH")
    if witness["prior_orientation_id"] != prior.orientation_id: violations.append("PRIOR_ORIENTATION_ID_MISMATCH")
    if witness["prior_orientation_digest"] != prior.orientation_digest: violations.append("PRIOR_ORIENTATION_DIGEST_MISMATCH")
    if delta.prior_orientation_hash != prior.orientation_digest: violations.append("DELTA_PRIOR_ORIENTATION_BINDING_MISMATCH")
    if witness["canonical_encoding_id"] != ENCODING_ID: violations.append("CANONICAL_ENCODING_ID_MISMATCH")
    if witness["localization_rule_id"] != LOCALIZATION_RULE_ID: violations.append("LOCALIZATION_RULE_ID_MISMATCH")
    if witness["monitor_rule_id"] != MONITOR_RULE_ID: violations.append("MONITOR_RULE_ID_MISMATCH")
    return (ReplayAxis.FAIL, violations) if violations else (ReplayAxis.PASS, [])

def _digest_axis(delta: FieldDelta, witness: Mapping[str, Any]):
    if "evidence_digest" not in witness:
        return ReplayAxis.FAIL, ["EVIDENCE_DIGEST_FIELD_MISSING"]
    recorded = witness.get("evidence_digest")
    if not isinstance(recorded, str):
        return ReplayAxis.FAIL, ["EVIDENCE_DIGEST_MALFORMED"]
    try:
        expected = evidence_digest(delta)
    except (TypeError, ValueError):
        return ReplayAxis.FAIL, ["CANONICAL_ENCODING_FAILED"]
    return ((ReplayAxis.PASS, []) if recorded == expected
            else (ReplayAxis.FAIL, ["EVIDENCE_DIGEST_MISMATCH"]))

def _localization_axis(delta: FieldDelta, witness: Mapping[str, Any], policy: LocalizationPolicy):
    try:
        loc = localize(delta, policy)
    except (ValueError, TypeError):
        return ReplayAxis.UNRESOLVED, ["LOCALIZATION_RECONSTRUCTION_UNRESOLVED"], None

    expected = witness.get("localization")
    if not isinstance(expected, Mapping):
        return ReplayAxis.UNRESOLVED, ["LOCALIZATION_RECORD_MISSING"], loc

    required = (
        "standing", "affected_surfaces", "causal_cone",
        "jurisdictional_cone", "unresolved_dependencies", "epoch",
    )
    if any(expected.get(k) is None for k in required):
        return ReplayAxis.UNRESOLVED, ["LOCALIZATION_RECORD_INCOMPLETE"], loc

    violations=[]
    if loc.standing.value != expected["standing"]: violations.append("LOCALIZATION_STANDING_MISMATCH")
    if sorted(loc.affected_surfaces) != sorted(expected["affected_surfaces"]): violations.append("AFFECTED_SURFACES_MISMATCH")
    if sorted(loc.causal_cone) != sorted(expected["causal_cone"]): violations.append("CAUSAL_CONE_MISMATCH")
    if sorted(loc.jurisdictional_cone) != sorted(expected["jurisdictional_cone"]): violations.append("JURISDICTIONAL_CONE_MISMATCH")
    if sorted(loc.unresolved_dependencies) != sorted(expected["unresolved_dependencies"]): violations.append("UNRESOLVED_DEPENDENCIES_MISMATCH")
    if loc.epoch != expected["epoch"]: violations.append("LOCALIZATION_EPOCH_MISMATCH")
    return ((ReplayAxis.FAIL, violations, loc) if violations else
            (ReplayAxis.PASS, [], loc))

def _disposition_axis(prior: PriorOrientation, loc, witness: Mapping[str, Any]):
    recorded_lifecycle = witness.get("lifecycle")
    if loc is None or recorded_lifecycle in (None, ""):
        return ReplayAxis.UNRESOLVED, ["DISPOSITION_RECORD_INCOMPLETE"]
    try:
        ev = evaluate(prior, loc)
    except (ValueError, TypeError):
        return ReplayAxis.UNRESOLVED, ["DISPOSITION_RECONSTRUCTION_UNRESOLVED"]

    violations=[]
    if ev.lifecycle.value != recorded_lifecycle:
        violations.append("LIFECYCLE_MISMATCH")

    if ev.lifecycle == OrientationLifecycle.CURRENT:
        for k in ("repair_attempted","auto_reorientation","authority_effect","execution_effect",
                  "historical_orientation_preserved","epistemic_standing_changed"):
            if k in witness and witness[k] not in (None, False, "NONE"):
                violations.append(f"CURRENT_UNEXPECTED_SIDE_EFFECT:{k}")
        return (ReplayAxis.FAIL, violations) if violations else (ReplayAxis.PASS, [])

    required = (
        "historical_orientation_preserved", "epistemic_standing_changed",
        "repair_attempted", "auto_reorientation", "authority_effect", "execution_effect",
    )
    if any(k not in witness for k in required):
        return ReplayAxis.UNRESOLVED, ["INVALIDATION_SIDE_EFFECT_RECORD_INCOMPLETE"]

    expected_w = ev.witness
    if expected_w is None:
        return ReplayAxis.UNRESOLVED, ["EXPECTED_INVALIDATION_WITNESS_MISSING"]

    if bool(witness["historical_orientation_preserved"]) != expected_w.historical_orientation_preserved:
        violations.append("HISTORICAL_PRESERVATION_MISMATCH")
    if bool(witness["epistemic_standing_changed"]) != expected_w.epistemic_standing_changed:
        violations.append("EPISTEMIC_STANDING_EFFECT_MISMATCH")
    if bool(witness["auto_reorientation"]) != expected_w.auto_reorientation:
        violations.append("AUTO_REORIENTATION_MISMATCH")
    if witness["authority_effect"] != expected_w.authority_effect:
        violations.append("AUTHORITY_EFFECT_MISMATCH")
    if witness["execution_effect"] != expected_w.execution_effect:
        violations.append("EXECUTION_EFFECT_MISMATCH")
    return (ReplayAxis.FAIL, violations) if violations else (ReplayAxis.PASS, [])

def _repair_axis(witness: Mapping[str, Any]):
    if "repair_attempted" not in witness:
        return ReplayAxis.UNRESOLVED, ["REPAIR_ATTEMPTED_FIELD_MISSING"]
    return ((ReplayAxis.FAIL, ["REPAIR_ATTEMPTED"]) if witness["repair_attempted"] is not False
            else (ReplayAxis.PASS, []))

def replay_validate(delta_dict: Mapping[str, Any], prior: PriorOrientation, witness: Mapping[str, Any], policy: LocalizationPolicy) -> ReplayResult:
    try:
        delta = FieldDelta(**dict(delta_dict))
    except (TypeError, ValueError):
        return ReplayResult(
            ReplayAxis.UNRESOLVED, ReplayAxis.FAIL, ReplayAxis.UNRESOLVED,
            ReplayAxis.UNRESOLVED, ReplayAxis.UNRESOLVED,
            ("DELTA_PARSE_UNRESOLVED",),
        )

    ia, iv = _input_axis(delta, prior, witness)
    da, dv = _digest_axis(delta, witness)
    la, lv, loc = _localization_axis(delta, witness, policy)
    sa, sv = _disposition_axis(prior, loc, witness)
    ra, rv = _repair_axis(witness)

    return ReplayResult(ia, da, la, sa, ra, _merge(iv,dv,lv,sv,rv))

# Constitutionally absent:
# repair_witness, relocalize_with_new_facts, reorient_object,
# mutate_authority, mutate_topology, trigger_execution.
