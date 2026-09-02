#!/usr/bin/env python3
"""OCPP bounded observation-acquisition adapter.

Mechanical observation capability only. No chamber execution, projection,
adjudication, scoring, repair, inference, mutation, promotion, dispatch, or
scientific-standing authority is granted by this module.
"""
from __future__ import annotations

import hashlib
import json
import re
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

ROOT_FIELDS = frozenset({
    "chamber_id",
    "source_pre_hash",
    "source_post_hash",
    "representation",
    "telemetry",
    "write_path_probe",
    "execution_status",
})
REPRESENTATION_FIELDS = frozenset({"observed_predicates"})
OBSERVED_PREDICATE_FIELDS = frozenset({"predicate", "value"})
TELEMETRY_FIELDS = frozenset({"sequence_idx", "sample_epoch_ns", "metric_name", "value"})
PROBE_FIELDS = frozenset({
    "probe_mode",
    "environmental_condition",
    "write_attempt_performed",
    "external_mutation_performed",
})
ALLOWED_EXECUTION_STATUS = frozenset({
    "NOT_EXECUTED",
    "COMPLETED",
    "ABSTAINED",
    "INTEGRITY_HALT",
    "EXECUTION_FAULT",
})
SCALAR_TYPES = (str, int, float, bool, type(None))
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _resolve_bounded_path(path: str | Path) -> Path:
    candidate = Path(path)
    candidate = (BATTERY_ROOT / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    for root in ADMITTED_LOAD_ROOTS:
        try:
            candidate.relative_to(root)
            return candidate
        except ValueError:
            continue
    raise PermissionError("LOAD_BOUNDED_REJECTED: path outside admitted fixture/schema roots")


def load_bounded(path: str | Path) -> Any:
    """LOAD_BOUNDED: decode JSON only from admitted fixture/schema roots."""
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
    """CAPTURE: create one observation-typed telemetry item."""
    if not isinstance(value, SCALAR_TYPES):
        raise TypeError("TELEMETRY_VALUE_NOT_SCALAR")
    return {
        "sequence_idx": int(sequence_idx),
        "sample_epoch_ns": time.time_ns(),
        "metric_name": str(metric_name),
        "value": value,
    }


def probe_declared_write_path(chamber: Mapping[str, Any]) -> dict[str, Any]:
    """PROBE: report a declared synthetic path condition without performing a write."""
    attack = chamber.get("attack", {})
    condition = attack.get("environmental_condition") if isinstance(attack, Mapping) else None
    return {
        "probe_mode": "DECLARATION_ONLY_NO_WRITE",
        "environmental_condition": str(condition) if condition is not None else None,
        "write_attempt_performed": False,
        "external_mutation_performed": False,
    }


def _closed_keys(obj: Mapping[str, Any], allowed: frozenset[str], label: str) -> list[str]:
    extra = sorted(set(obj.keys()).difference(allowed))
    missing = sorted(allowed.difference(obj.keys()))
    errors = [f"{label}_missing:{key}" for key in missing]
    errors.extend(f"{label}_extra:{key}" for key in extra)
    return errors


def _is_scalar(value: Any) -> bool:
    return isinstance(value, SCALAR_TYPES)


def validate_raw_residue_shape(residue: Mapping[str, Any]) -> tuple[bool, list[str]]:
    """VALIDATE_SCHEMA: enforce recursive observation-only structural closure."""
    errors = _closed_keys(residue, ROOT_FIELDS, "root")

    if not isinstance(residue.get("chamber_id"), str) or not residue.get("chamber_id"):
        errors.append("chamber_id_invalid")
    for field in ("source_pre_hash", "source_post_hash"):
        value = residue.get(field)
        if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
            errors.append(f"{field}_invalid_sha256")
    if residue.get("execution_status") not in ALLOWED_EXECUTION_STATUS:
        errors.append("execution_status_invalid")

    representation = residue.get("representation")
    if not isinstance(representation, Mapping):
        errors.append("representation_not_object")
    else:
        errors.extend(_closed_keys(representation, REPRESENTATION_FIELDS, "representation"))
        predicates = representation.get("observed_predicates")
        if not isinstance(predicates, list):
            errors.append("observed_predicates_not_array")
        else:
            for idx, item in enumerate(predicates):
                if not isinstance(item, Mapping):
                    errors.append(f"observed_predicate_{idx}_not_object")
                    continue
                errors.extend(_closed_keys(item, OBSERVED_PREDICATE_FIELDS, f"observed_predicate_{idx}"))
                if not isinstance(item.get("predicate"), str) or not item.get("predicate"):
                    errors.append(f"observed_predicate_{idx}_predicate_invalid")
                if not _is_scalar(item.get("value")):
                    errors.append(f"observed_predicate_{idx}_value_not_scalar")

    telemetry = residue.get("telemetry")
    if not isinstance(telemetry, list):
        errors.append("telemetry_not_array")
    else:
        for idx, item in enumerate(telemetry):
            if not isinstance(item, Mapping):
                errors.append(f"telemetry_{idx}_not_object")
                continue
            errors.extend(_closed_keys(item, TELEMETRY_FIELDS, f"telemetry_{idx}"))
            if not isinstance(item.get("sequence_idx"), int) or item.get("sequence_idx", -1) < 0:
                errors.append(f"telemetry_{idx}_sequence_idx_invalid")
            if not isinstance(item.get("sample_epoch_ns"), int) or item.get("sample_epoch_ns", -1) < 0:
                errors.append(f"telemetry_{idx}_sample_epoch_ns_invalid")
            if not isinstance(item.get("metric_name"), str) or not item.get("metric_name"):
                errors.append(f"telemetry_{idx}_metric_name_invalid")
            if not _is_scalar(item.get("value")):
                errors.append(f"telemetry_{idx}_value_not_scalar")

    probe = residue.get("write_path_probe")
    if not isinstance(probe, Mapping):
        errors.append("write_path_probe_not_object")
    else:
        errors.extend(_closed_keys(probe, PROBE_FIELDS, "write_path_probe"))
        if probe.get("probe_mode") != "DECLARATION_ONLY_NO_WRITE":
            errors.append("probe_mode_invalid")
        if probe.get("environmental_condition") is not None and not isinstance(probe.get("environmental_condition"), str):
            errors.append("environmental_condition_invalid")
        if probe.get("write_attempt_performed") is not False:
            errors.append("write_attempt_performed_must_be_false")
        if probe.get("external_mutation_performed") is not False:
            errors.append("external_mutation_performed_must_be_false")

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
    """EMIT: emit only recursively validated observation-typed residue."""
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
