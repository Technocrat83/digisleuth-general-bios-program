#!/usr/bin/env python3
"""OCPP bounded observation-acquisition adapter.

This module materializes mechanical observation capabilities only. It grants no
execution, projection, adjudication, scoring, repair, mutation, inference,
promotion, dispatch, or scientific-standing authority.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

A_OBS = frozenset({"LOAD_BOUNDED", "HASH", "CAPTURE", "PROBE", "VALIDATE_SCHEMA", "EMIT"})
PROHIBITED = frozenset({
    "APPLY_DECLARED_PROJECTION_TRANSFORM",
    "SCORE",
    "ADJUDICATE",
    "REPAIR",
    "INFER",
    "MUTATE",
    "PROMOTE",
})
EXECUTION_AUTHORIZED = False
DISPATCH_AUTHORIZED = False

BATTERY_ROOT = Path(__file__).resolve().parents[1]
ADMITTED_LOAD_ROOTS = tuple((BATTERY_ROOT / name).resolve() for name in ("fixtures", "schemas"))

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


def _resolve_bounded_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = (BATTERY_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()

    for root in ADMITTED_LOAD_ROOTS:
        try:
            candidate.relative_to(root)
            return candidate
        except ValueError:
            continue
    raise PermissionError("LOAD_BOUNDED_REJECTED: path outside admitted fixture/schema roots")


def load_bounded(path: str | Path) -> Any:
    """LOAD_BOUNDED: read JSON only from admitted fixture/schema roots."""
    bounded = _resolve_bounded_path(path)
    with bounded.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def hash_bytes(payload: bytes) -> str:
    """HASH: return SHA-256 over supplied bytes."""
    return hashlib.sha256(payload).hexdigest()


def hash_json(value: Any) -> str:
    """HASH: deterministic SHA-256 over canonical JSON serialization."""
    return hash_bytes(_canonical_json_bytes(value))


def capture(metric_name: str, value: Any, *, sequence_idx: int = 0) -> dict[str, Any]:
    """CAPTURE: create one timestamped mechanical telemetry observation."""
    return {
        "sequence_idx": int(sequence_idx),
        "sample_epoch_ns": time.time_ns(),
        "metric_name": str(metric_name),
        "value": value,
    }


def probe_declared_write_path(chamber: Mapping[str, Any]) -> dict[str, Any]:
    """PROBE: report only a chamber-declared synthetic path condition; never write."""
    attack = chamber.get("attack", {})
    condition = attack.get("environmental_condition") if isinstance(attack, Mapping) else None
    return {
        "probe_mode": "DECLARATION_ONLY_NO_WRITE",
        "environmental_condition": condition,
        "write_attempt_performed": False,
        "external_mutation_performed": False,
    }


def validate_raw_residue_shape(residue: Mapping[str, Any]) -> tuple[bool, list[str]]:
    """VALIDATE_SCHEMA: mechanical pre-R5 shape validation only."""
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
    """EMIT: construct observation residue without scoring or adjudicating."""
    residue: dict[str, Any] = {
        "chamber_id": str(chamber_id),
        "source_pre_hash": hash_json(source_pre),
        "source_post_hash": hash_json(source_post),
        "representation": dict(representation),
        "telemetry": [dict(item) for item in telemetry],
        "write_path_probe": dict(write_path_probe),
        "execution_status": execution_status,
    }
    valid, errors = validate_raw_residue_shape(residue)
    if not valid:
        raise ValueError("RAW_RESIDUE_SCHEMA_INVALID:" + ";".join(errors))
    return residue


def assert_dispatch_locked() -> None:
    if EXECUTION_AUTHORIZED or DISPATCH_AUTHORIZED:
        raise RuntimeError("EXECUTION_LOCK_INTEGRITY_FAILURE")


def main() -> None:
    assert_dispatch_locked()
    raise SystemExit("EXECUTION_LOCKED: observation runtime exists behind denied dispatch gate")


if __name__ == "__main__":
    main()
