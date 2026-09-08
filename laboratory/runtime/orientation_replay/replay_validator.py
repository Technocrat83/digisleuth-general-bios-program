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
from orientation_monitor import PriorOrientation, evaluate

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
    repair_attempted: bool = False

    @property
    def qualification_pass(self) -> bool:
        return all(x == ReplayAxis.PASS for x in (
            self.input_binding,
            self.digest_binding,
            self.localization_reconstruction,
            self.disposition_reconstruction,
        )) and not self.repair_attempted

    def to_dict(self) -> dict[str, object]:
        return {
            "INPUT_BINDING": self.input_binding.value,
            "DIGEST_BINDING": self.digest_binding.value,
            "LOCALIZATION_RECONSTRUCTION": self.localization_reconstruction.value,
            "DISPOSITION_RECONSTRUCTION": self.disposition_reconstruction.value,
            "REPAIR_ATTEMPTED": self.repair_attempted,
            "QUALIFICATION_PASS": self.qualification_pass,
            "CANONICAL_ENCODING": ENCODING_ID,
        }

def replay_validate(delta_dict: Mapping[str, Any], prior: PriorOrientation, witness: Mapping[str, Any], policy: LocalizationPolicy) -> ReplayResult:
    try:
        delta = FieldDelta(**dict(delta_dict))
    except (TypeError, ValueError):
        return ReplayResult(ReplayAxis.UNRESOLVED, ReplayAxis.FAIL, ReplayAxis.UNRESOLVED, ReplayAxis.UNRESOLVED)

    required = ("object_id", "delta_id", "prior_orientation_id", "prior_orientation_digest")
    if any(witness.get(k) in (None, "") for k in required):
        input_axis = ReplayAxis.UNRESOLVED
    else:
        ok = (
            witness.get("object_id") == delta.object_id
            and witness.get("delta_id") == delta.delta_id
            and witness.get("prior_orientation_id") == prior.orientation_id
            and witness.get("prior_orientation_digest") == prior.orientation_digest
            and delta.prior_orientation_hash == prior.orientation_digest
        )
        input_axis = ReplayAxis.PASS if ok else ReplayAxis.FAIL

    recorded_digest = witness.get("evidence_digest") or witness.get("localization_evidence_digest")
    digest_axis = ReplayAxis.PASS if isinstance(recorded_digest, str) and recorded_digest == evidence_digest(delta) else ReplayAxis.FAIL

    try:
        loc = localize(delta, policy)
    except Exception:
        loc = None

    expected_loc = witness.get("localization")
    if loc is None or not isinstance(expected_loc, Mapping):
        loc_axis = ReplayAxis.UNRESOLVED
    else:
        required_loc = ("standing", "affected_surfaces", "causal_cone", "jurisdictional_cone")
        if any(expected_loc.get(k) is None for k in required_loc):
            loc_axis = ReplayAxis.UNRESOLVED
        else:
            same = (
                loc.standing.value == expected_loc["standing"]
                and sorted(loc.affected_surfaces) == sorted(expected_loc["affected_surfaces"])
                and sorted(loc.causal_cone) == sorted(expected_loc["causal_cone"])
                and sorted(loc.jurisdictional_cone) == sorted(expected_loc["jurisdictional_cone"])
            )
            loc_axis = ReplayAxis.PASS if same else ReplayAxis.FAIL

    recorded_lifecycle = witness.get("lifecycle")
    if loc is None or recorded_lifecycle in (None, ""):
        disp_axis = ReplayAxis.UNRESOLVED
    else:
        try:
            ev = evaluate(prior, loc)
            disp_axis = ReplayAxis.PASS if ev.lifecycle.value == recorded_lifecycle else ReplayAxis.FAIL
        except Exception:
            disp_axis = ReplayAxis.UNRESOLVED

    return ReplayResult(input_axis, digest_axis, loc_axis, disp_axis, repair_attempted=False)
