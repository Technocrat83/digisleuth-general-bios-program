from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import Any, Dict

from schemas import BlindTrace, Coordinate, SealedTruthRecord


@dataclass(frozen=True)
class PerturbationFixture:
    trial_id: str
    perturbation_id: str
    coordinate: Coordinate
    jurisdiction_target: str
    runtime_input: Dict[str, Any]
    observable_trace: Dict[str, Any]


def _digest(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def materialize_fixture(fixture: PerturbationFixture) -> tuple[SealedTruthRecord, BlindTrace]:
    """
    Materializes two epistemically separated artifacts:
      1) sealed truth record — contains true coordinate/jurisdiction
      2) blind trace — contains only unlabeled observations

    The caller is responsible for persisting them into physically separated locations.
    """
    provenance_nonce = secrets.token_hex(16)
    truth_payload = {
        "trial_id": fixture.trial_id,
        "coordinate": fixture.coordinate.value,
        "jurisdiction_target": fixture.jurisdiction_target,
        "perturbation_id": fixture.perturbation_id,
        "provenance_nonce": provenance_nonce,
    }
    truth = SealedTruthRecord(
        trial_id=fixture.trial_id,
        coordinate=fixture.coordinate,
        jurisdiction_target=fixture.jurisdiction_target,
        perturbation_id=fixture.perturbation_id,
        provenance_digest=_digest(truth_payload),
    )

    blind_payload = {
        "trial_id": fixture.trial_id,
        "observations": fixture.observable_trace,
    }
    trace = BlindTrace(
        trial_id=fixture.trial_id,
        observations=fixture.observable_trace,
        trace_digest=_digest(blind_payload),
    )
    return truth, trace
