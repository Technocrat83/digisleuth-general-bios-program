from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Final

import C
import Phi

RUNNER_ID: Final[str] = "R"
SCHEMA_ID: Final[str] = "HD_COUPLED03_RUNNER_v0.1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class HelmCommitment:
    specimen_a_decision: str
    specimen_b_decision: str
    committed_at_ns: int
    commitment_witness: str


@dataclass(frozen=True)
class RawExecutionResidue:
    runner_id: str
    schema_id: str
    input_value: int
    coupling_trace: dict[str, object]
    helm_commitment: dict[str, object]
    delta_phi_exposed_at_ns: int
    specimen_a_delta: dict[str, object]
    specimen_b_delta: dict[str, object]
    temporal_gate_preserved: bool
    abnormal_events: tuple[str, ...]
    residue_root: str


def commit_helm_decisions(
    specimen_a_decision: str,
    specimen_b_decision: str,
    committed_at_ns: int,
) -> HelmCommitment:
    """Seal blind Helm decisions without interpreting their correctness."""
    payload = {
        "specimen_a_decision": specimen_a_decision,
        "specimen_b_decision": specimen_b_decision,
        "committed_at_ns": committed_at_ns,
    }
    witness = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    return HelmCommitment(
        specimen_a_decision=specimen_a_decision,
        specimen_b_decision=specimen_b_decision,
        committed_at_ns=committed_at_ns,
        commitment_witness=witness,
    )


def run_once(
    *,
    input_value: int,
    helm_commitment: HelmCommitment,
    delta_phi_exposed_at_ns: int,
    specimen_a_pre: Phi.PhenotypeState,
    specimen_a_post: Phi.PhenotypeState,
    specimen_b_pre: Phi.PhenotypeState,
    specimen_b_post: Phi.PhenotypeState,
) -> RawExecutionResidue:
    """Execute one deterministic COUPLED03 causal sequence and preserve residue.

    This runner performs mechanical coupling and coordinate-wise Phi measurement.
    It serializes the temporal relation between the already-sealed Helm commitment
    and Delta-Phi exposure. It does not assign SAFE/CONSTITUTIVE/PASS/FAIL labels,
    does not assign C1-C4, does not adjudicate scientific standing, and performs
    no retry or repair when an invariant is violated.
    """
    trace = C.couple(input_value)
    delta_a = Phi.evaluate(specimen_a_pre, specimen_a_post)
    delta_b = Phi.evaluate(specimen_b_pre, specimen_b_post)

    temporal_gate_preserved = (
        helm_commitment.committed_at_ns < delta_phi_exposed_at_ns
    )
    abnormal_events: tuple[str, ...] = (
        ()
        if temporal_gate_preserved
        else ("HELM_COMMIT_NOT_BEFORE_DELTA_PHI_EXPOSURE",)
    )

    residue_payload = {
        "runner_id": RUNNER_ID,
        "schema_id": SCHEMA_ID,
        "input_value": input_value,
        "coupling_trace": C.to_record(trace),
        "helm_commitment": asdict(helm_commitment),
        "delta_phi_exposed_at_ns": delta_phi_exposed_at_ns,
        "specimen_a_delta": Phi.to_record(delta_a),
        "specimen_b_delta": Phi.to_record(delta_b),
        "temporal_gate_preserved": temporal_gate_preserved,
        "abnormal_events": abnormal_events,
    }
    residue_root = hashlib.sha256(_canonical_bytes(residue_payload)).hexdigest()

    return RawExecutionResidue(
        runner_id=RUNNER_ID,
        schema_id=SCHEMA_ID,
        input_value=input_value,
        coupling_trace=C.to_record(trace),
        helm_commitment=asdict(helm_commitment),
        delta_phi_exposed_at_ns=delta_phi_exposed_at_ns,
        specimen_a_delta=Phi.to_record(delta_a),
        specimen_b_delta=Phi.to_record(delta_b),
        temporal_gate_preserved=temporal_gate_preserved,
        abnormal_events=abnormal_events,
        residue_root=residue_root,
    )


def to_record(residue: RawExecutionResidue) -> dict[str, object]:
    """Return canonical serialization-ready raw execution telemetry."""
    return asdict(residue)


if __name__ == "__main__":
    # Materialization smoke surface only. It does not execute the experiment.
    print(json.dumps({"runner_id": RUNNER_ID, "schema_id": SCHEMA_ID}, sort_keys=True, separators=(",", ":")))
