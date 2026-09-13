"""Deterministic B_sigma projection from a hidden fixture to permitted X_i."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from .witness_authentication_stub import AuthenticationState

SERIALIZER_ID = "CFBFA_BLIND_SERIALIZER"
SERIALIZER_VERSION = "0.1.0"
PERMITTED_FIELDS = (
    "O_t",
    "O_t_plus_1_candidate",
    "rho_t",
    "authenticated_witness_status",
    "Q_t",
)
RULES = {
    "normalize": [
        "field_order",
        "container_wrapping",
        "identifier_format",
        "optional_field_representation",
        "filename",
        "serialization_comments",
        "nonsemantic_object_ids",
    ],
    "preserve": ["causal_missingness", "tested_structural_relations"],
    "prohibited": [
        "fixture_specific_normalization",
        "post_verdict_normalization",
        "causal_information_removal",
        "synthetic_completion_of_missing_data",
    ],
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def rules_hash() -> str:
    return hashlib.sha256(canonical_json(RULES)).hexdigest()


def serialize_fixture(fixture: Mapping[str, Any], auth: AuthenticationState) -> bytes:
    source = fixture.get("operator_input")
    if not isinstance(source, Mapping):
        raise ValueError("operator_input is required")
    required = {"O_t", "O_t_plus_1_candidate", "rho_t", "Q_t"}
    if set(source) != required:
        raise ValueError("operator_input must contain exactly the frozen input fields")
    q_t = source["Q_t"]
    if not isinstance(q_t, Mapping):
        raise ValueError("Q_t must be an object")
    for preserved in ("causal_missingness", "tested_structural_relations"):
        if preserved not in q_t:
            raise ValueError(f"Q_t must preserve {preserved}")
    projected = {
        "O_t": deepcopy(source["O_t"]),
        "O_t_plus_1_candidate": deepcopy(source["O_t_plus_1_candidate"]),
        "rho_t": deepcopy(source["rho_t"]),
        "authenticated_witness_status": auth.value,
        "Q_t": deepcopy(q_t),
    }
    if tuple(projected) != PERMITTED_FIELDS:
        raise AssertionError("serializer field contract drift")
    return canonical_json(projected)
