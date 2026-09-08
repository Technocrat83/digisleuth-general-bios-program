from __future__ import annotations
from dataclasses import asdict, is_dataclass
from typing import Any
import hashlib

ENCODING_ID = "ORIENTATION_DELTA_CANONICAL_ENCODING_v0.1"

FIELD_ORDER = (
    "object_id","delta_id","prior_orientation_hash",
    "prior_graph_hash","current_graph_hash",
    "prior_jurisdiction_hash","current_jurisdiction_hash",
    "prior_provenance_hash","current_provenance_hash",
    "prior_placement_hash","current_placement_hash",
    "prior_state_hash","current_state_hash",
    "prior_boundary_hash","current_boundary_hash",
    "prior_epoch","current_epoch",
    "adjacency_changed","authority_use_attempted","evidence_complete",
)

def _u32(n: int) -> bytes:
    if n < 0 or n > 0xFFFFFFFF:
        raise ValueError("LENGTH_OUT_OF_RANGE")
    return n.to_bytes(4, "big")

def _text(v: str) -> bytes:
    b = v.encode("utf-8")
    return _u32(len(b)) + b

def _bool(v: bool) -> bytes:
    return b"\x01" if v else b"\x00"

def canonicalize_delta(delta: Any) -> bytes:
    if is_dataclass(delta):
        data = asdict(delta)
    elif isinstance(delta, dict):
        data = dict(delta)
    else:
        raise TypeError("DELTA_MUST_BE_DATACLASS_OR_MAPPING")

    if set(data) != set(FIELD_ORDER):
        missing = sorted(set(FIELD_ORDER) - set(data))
        extra = sorted(set(data) - set(FIELD_ORDER))
        raise ValueError(f"CANONICAL_FIELD_SET_MISMATCH:missing={missing}:extra={extra}")

    out = bytearray()
    out.extend(_text(ENCODING_ID))
    for name in FIELD_ORDER:
        out.extend(_text(name))
        value = data[name]
        if isinstance(value, bool):
            out.extend(b"B")
            out.extend(_bool(value))
        elif isinstance(value, str):
            out.extend(b"S")
            out.extend(_text(value))
        else:
            raise TypeError(f"UNSUPPORTED_CANONICAL_TYPE:{name}:{type(value).__name__}")
    return bytes(out)

def evidence_digest(delta: Any) -> str:
    return hashlib.sha256(canonicalize_delta(delta)).hexdigest()
