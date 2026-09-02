#!/usr/bin/env python3
"""OCPP bounded observation-acquisition adapter.

Materialization provides mechanical residue capabilities only. It grants no
execution, adjudication, scoring, repair, mutation, inference, promotion, or
scientific-standing authority. Direct CLI execution remains locked; a future
separately qualified dispatch membrane may import these primitives.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

A_OBS = frozenset({"LOAD", "HASH", "CAPTURE", "PROBE", "VALIDATE_SCHEMA", "EMIT"})
PROHIBITED = frozenset({"SCORE", "ADJUDICATE", "REPAIR", "INFER", "MUTATE", "PROMOTE"})
EXECUTION_AUTHORIZED = False

REQUIRED_RESIDUE_FIELDS = frozenset({
    "chamber_id",
    "source_pre_hash",
    "source_post_hash",
    "representation",
    "telemetry",
    "write_path_probe",
    "execution_status",
})
ALLOWED_EXECUTION_STATUS = frozenset({
    "NOT_EXECUTED",
    "COMPLETED",
    "ABSTAINED",
    "INTEGRITY_HALT",
    "EXECUTION_FAULT",
})


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_json(path: str | Path) -> Any:
    """LOAD: read and decode a JSON object without modifying the source."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def hash_bytes(payload: bytes) -> str:
    """HASH: return SHA-256 over supplied bytes."""
    return hashlib.sha256(payload).hexdigest()


def hash_json(value: Any) -> str:
    """HASH: deterministic SHA-256 over canonical JSON serialization."""
    return hash_bytes(_canonical_json_bytes(value))


def capture(metric_name: str, value: Any, *, sequence_idx: int = 0) -> dict[str, Any]:
    """CAPTURE: create a raw timestamped telemetry observation."""
    return {
        "sequence_idx": int(sequence_idx),
        "sample_epoch_ns": time.time_ns(),
        "metric_name": str(metric_name),
        "value": value,
    }


def probe_declared_write_path(chamber: Mapping[str, Any]) -> dict[str, Any]:
    """PROBE: report only the chamber-declared synthetic write-path condition.

    This function never performs a write and never tests external endpoints.
    """
    attack = chamber.get("attack", {})
    condition = attack.get("environmental_condition") if isinstance(attack, Mapping) else None
    return {
        "probe_mode": "DECLARATION_ONLY_NO_WRITE",
        "environmental_condition": condition,
        "write_attempt_performed": False,
        "external_mutation_performed": False,
    }


def validate_raw_residue_shape(residue: Mapping[str, Any]) -> tuple[bool, list[str]]:
    """VALIDATE_SCHEMA: minimal mechanical conformance to frozen v0.1 schema."""
    missing = sorted(REQUIRED_RESIDUE_FIELDS.difference(residue.keys()))
    errors = [f"missing_required:{field}" for field in missing]
    status = residue.get("execution_status")
    if status not in ALLOWED_EXECUTION_STATUS:
        errors.append("invalid_execution_status")
    if not isinstance(residue.get("representation"), Mapping):
        errors.append("representation_not_object")
    if not isinstance(residue.get("telemetry"), Sequence) or isinstance(residue.get("telemetry"), (str, bytes, bytearray)):
        errors.append("telemetry_not_array")
    if not isinstance(residue.get("write_path_probe"), Mapping):
        errors.append("write_path_probe_not_object")
    return (not errors, errors)


def emit_raw_residue(
    *,
    chamber_id: str,
    source_pre: Any,
    source_post: Any,
    representation: Mapping[str, Any],
    telemetry: Sequence[Mapping[str, Any]],
    write_path_probe: Mapping[str, Any],
    execution_status: str,
) -> dict[str, Any]:
    """EMIT: construct typed raw residue; never score or adjudicate it."""
    residue: dict[str, Any] = {
        "chamber_id": str(chamber_id),
        "source_pre_hash": hash_json(source_pre),
        "source_post_hash": hash_json(source_post),
        "representation": dict(representation),
        "telemetry": [dict(item) for item in telemetry],
        "write_path_probe": dict(write_path_probe),
        "execution_status": execution_status,
        "observation_authority": "A_obs",
        "adjudication_authority": "ZERO",
    }
    valid, errors = validate_raw_residue_shape(residue)
    if not valid:
        raise ValueError("RAW_RESIDUE_SCHEMA_INVALID:" + ";".join(errors))
    return residue


def main() -> None:
    raise SystemExit("EXECUTION_LOCKED: materialized observation adapter requires separate qualified dispatch membrane")


if __name__ == "__main__":
    main()
