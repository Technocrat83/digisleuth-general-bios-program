"""Detached witness authentication with a non-compensatory typed result."""

from __future__ import annotations

import hashlib
from enum import Enum
from typing import Any, Mapping


class AuthenticationState(str, Enum):
    AUTH_VALID = "AUTH_VALID"
    AUTH_INVALID = "AUTH_INVALID"
    AUTH_UNRESOLVED = "AUTH_UNRESOLVED"


def authenticate_witness(artifact: Mapping[str, Any]) -> AuthenticationState:
    payload = artifact.get("payload")
    declared = artifact.get("declared_sha256")
    if not isinstance(payload, str) or not isinstance(declared, str):
        return AuthenticationState.AUTH_UNRESOLVED
    if len(declared) != 64:
        return AuthenticationState.AUTH_INVALID
    observed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return AuthenticationState.AUTH_VALID if observed == declared else AuthenticationState.AUTH_INVALID
