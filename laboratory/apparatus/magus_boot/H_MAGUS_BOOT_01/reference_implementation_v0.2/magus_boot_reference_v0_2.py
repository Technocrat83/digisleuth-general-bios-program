#!/usr/bin/env python3
"""
MAGUS_BOOT_REFERENCE_IMPLEMENTATION_v0.2

STATUS:
    MATERIALIZED / UNEXECUTED / PENDING PREFLIGHT RE-ENTRY

LINEAGE:
    Ancestor v0.1:
      commit: 219e42a51cc55c93d9349b4dea1d7c86dbf76973
      identity: b1b0cce952b3108618d8e891a44da9a18e11547c9238bae70c9ec9d725563ed5
      standing: PREFLIGHT_NONCONFORMANT
      terminal fault: RAW_PATH_INGRESS_NOT_CONFINED (P_input = FAIL)

    Contract anchor:
      commit: 04a506e7cf2ffcdd8b13d61a641d9dd2849f3c01

PURPOSE:
    Fresh successor reference implementation that replaces raw path ingress
    with an explicit, non-self-expanding E_ingress authority envelope:

        E_ingress = < I_C, P_R, H_C, S_A, L_I, Sigma_K >

CONSTITUTIONAL BOUNDARIES:
    - Reachability does not confer ingress authority.
    - Path knowledge != path entitlement != traversal.
    - Discovery may not expand S_A.
    - The ingress envelope may not self-expand.
    - No fixture mutation is implemented.
    - No oracle access is implemented.
    - No boot execution is authorized by materialization or self-validation.
    - No prior v0.1 preflight result is inherited.
    - P_sep, P_immut, P_identity, P_input, P_output, and P_noexec
      must all be independently re-audited before scientific boot execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet, Literal, Tuple
import hashlib
import json
from datetime import datetime, timezone

HashAlgorithm = Literal["sha256"]


class IngressEnvelopeError(Exception):
    """Base error for malformed or non-conforming ingress envelopes."""


class IngressConfinementViolation(IngressEnvelopeError):
    """Raised when a reachable filesystem surface is not entitled for traversal."""


class IngressIdentityViolation(IngressEnvelopeError):
    """Raised when envelope identity or root-hash predicates fail."""


class IngressLeaseViolation(IngressEnvelopeError):
    """Raised when lease scope, freshness, or kernel anchoring fails."""


@dataclass(frozen=True)
class CorpusHashWitness:
    algorithm: HashAlgorithm
    digest: str
    scope: str

    def validate_shape(self) -> None:
        if self.algorithm != "sha256":
            raise IngressIdentityViolation("UNSUPPORTED_HASH_ALGORITHM")
        if len(self.digest) != 64 or any(c not in "0123456789abcdef" for c in self.digest.lower()):
            raise IngressIdentityViolation("INVALID_CORPUS_DIGEST_SHAPE")


@dataclass(frozen=True)
class AllowedSurface:
    relative_path: str
    surface_type: str
    read_entitlement: bool = True

    def validate_shape(self) -> None:
        p = Path(self.relative_path)
        if p.is_absolute():
            raise IngressConfinementViolation("ABSOLUTE_PATH_PROHIBITED_IN_S_A")
        if ".." in p.parts:
            raise IngressConfinementViolation("PARENT_TRAVERSAL_PROHIBITED_IN_S_A")
        if not self.relative_path or self.relative_path in (".", ""):
            raise IngressConfinementViolation("EMPTY_SURFACE_PROHIBITED")
        if self.read_entitlement is not True:
            raise IngressConfinementViolation("NON_READ_ENTITLEMENT_SURFACE_PROHIBITED")


@dataclass(frozen=True)
class LeaseIdentityScopeToken:
    lease_id: str
    issued_at: str
    expires_at: str
    scope_hash: str
    signature_algorithm: str
    signature: str
    issuer: str
    renewable_in_place: bool = False

    def validate_shape(self) -> None:
        if not self.lease_id:
            raise IngressLeaseViolation("LEASE_ID_MISSING")
        if self.renewable_in_place:
            raise IngressLeaseViolation("IN_PLACE_LEASE_RENEWAL_PROHIBITED")
        if len(self.scope_hash) != 64 or any(c not in "0123456789abcdef" for c in self.scope_hash.lower()):
            raise IngressLeaseViolation("INVALID_SCOPE_HASH_SHAPE")
        if not self.signature_algorithm or not self.signature or not self.issuer:
            raise IngressLeaseViolation("LEASE_VERIFICATION_SURFACE_INCOMPLETE")

    def is_current(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        issued = _parse_iso8601(self.issued_at)
        expires = _parse_iso8601(self.expires_at)
        return issued <= now < expires


@dataclass(frozen=True)
class KernelAnchor:
    kernel_id: str
    algorithm: HashAlgorithm
    digest: str

    def validate_shape(self) -> None:
        if not self.kernel_id:
            raise IngressLeaseViolation("KERNEL_ID_MISSING")
        if self.algorithm != "sha256":
            raise IngressLeaseViolation("UNSUPPORTED_KERNEL_HASH_ALGORITHM")
        if len(self.digest) != 64 or any(c not in "0123456789abcdef" for c in self.digest.lower()):
            raise IngressLeaseViolation("INVALID_KERNEL_DIGEST_SHAPE")


@dataclass(frozen=True)
class IngressEnvelope:
    I_C: str
    P_R: str
    H_C: CorpusHashWitness
    S_A: Tuple[AllowedSurface, ...]
    L_I: LeaseIdentityScopeToken
    Sigma_K: KernelAnchor

    def __post_init__(self) -> None:
        if not self.I_C:
            raise IngressEnvelopeError("CORPUS_IDENTITY_HANDLE_MISSING")
        if not self.P_R:
            raise IngressEnvelopeError("PHYSICAL_ROOT_BOUNDARY_MISSING")
        if not self.S_A:
            raise IngressEnvelopeError("ALLOWED_SURFACE_SET_EMPTY")

        self.H_C.validate_shape()
        self.L_I.validate_shape()
        self.Sigma_K.validate_shape()

        seen = set()
        for surface in self.S_A:
            surface.validate_shape()
            if surface.relative_path in seen:
                raise IngressConfinementViolation("DUPLICATE_ALLOWED_SURFACE")
            seen.add(surface.relative_path)

    @property
    def physical_root(self) -> Path:
        return Path(self.P_R).resolve()

    @property
    def allowed_relative_paths(self) -> FrozenSet[str]:
        return frozenset(surface.relative_path for surface in self.S_A)

    def canonical_scope_payload(self) -> bytes:
        payload = {
            "I_C": self.I_C,
            "P_R": str(self.physical_root),
            "H_C": {
                "algorithm": self.H_C.algorithm,
                "digest": self.H_C.digest,
                "scope": self.H_C.scope,
            },
            "S_A": [
                {
                    "relative_path": s.relative_path,
                    "surface_type": s.surface_type,
                    "read_entitlement": s.read_entitlement,
                }
                for s in sorted(self.S_A, key=lambda x: x.relative_path)
            ],
            "Sigma_K": {
                "kernel_id": self.Sigma_K.kernel_id,
                "algorithm": self.Sigma_K.algorithm,
                "digest": self.Sigma_K.digest,
            },
        }
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    def computed_scope_hash(self) -> str:
        return hashlib.sha256(self.canonical_scope_payload()).hexdigest()

    def verify_scope_binding(self) -> None:
        if self.computed_scope_hash().lower() != self.L_I.scope_hash.lower():
            raise IngressLeaseViolation("INGRESS_SCOPE_DIVERGENCE")

    def verify_lease_freshness(self, now: datetime | None = None) -> None:
        if not self.L_I.is_current(now):
            raise IngressLeaseViolation("LEASE_INVALID_NO_TRAVERSAL")

    def verify_kernel_anchor_binding(self, authoritative_kernel_digest: str) -> None:
        if self.Sigma_K.digest.lower() != authoritative_kernel_digest.lower():
            raise IngressLeaseViolation("CONSTITUTIONAL_CONTRADICTION_KERNEL_ANCHOR_MISMATCH")

    def self_verify_static(self) -> None:
        """
        Static envelope self-verification only.

        IMPORTANT:
        - This does not authorize traversal.
        - This does not invoke the five-stage MAGUS boot membrane.
        - This does not verify an external signature cryptographically.
        - This does not read corpus files.
        """
        self.verify_scope_binding()
        self.verify_lease_freshness()


def _parse_iso8601(value: str) -> datetime:
    try:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
    except Exception as exc:
        raise IngressLeaseViolation("INVALID_LEASE_TIMESTAMP") from exc
    if dt.tzinfo is None:
        raise IngressLeaseViolation("LEASE_TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return dt.astimezone(timezone.utc)


def validate_traversal_path(
    target_relative_path: str,
    envelope: IngressEnvelope,
) -> Path:
    """
    Resolve a requested relative path against P_R and enforce S_A membership.

    This function validates entitlement only. It does NOT open, read,
    execute, import, or otherwise traverse the target.
    """
    requested = Path(target_relative_path)
    if requested.is_absolute():
        raise IngressConfinementViolation("ABSOLUTE_TARGET_PATH_PROHIBITED")
    if ".." in requested.parts:
        raise IngressConfinementViolation("PARENT_TRAVERSAL_PROHIBITED")

    base = envelope.physical_root
    resolved = (base / requested).resolve()

    try:
        rel = resolved.relative_to(base).as_posix()
    except ValueError as exc:
        raise IngressConfinementViolation(
            f"ESCAPE_TRAP:{target_relative_path}"
        ) from exc

    if rel not in envelope.allowed_relative_paths:
        raise IngressConfinementViolation(
            f"UNAUTHORIZED_SURFACE:{rel}"
        )

    return resolved


def discover_path_without_authorization(
    candidate_relative_path: str,
    envelope: IngressEnvelope,
) -> bool:
    """
    Discovery is intentionally non-authoritative.

    Returns only whether the candidate path is currently enumerated in S_A.
    It never mutates, appends to, or normalizes S_A.
    """
    return candidate_relative_path in envelope.allowed_relative_paths


def sha256_file_readonly(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_declared_root_hash(
    envelope: IngressEnvelope,
    declared_root_manifest_relative_path: str,
) -> None:
    """
    Verify one explicitly entitled root identity surface.

    The caller must identify the exact root-manifest surface.
    No filesystem discovery or fallback search is performed.
    """
    target = validate_traversal_path(
        declared_root_manifest_relative_path,
        envelope,
    )
    observed = sha256_file_readonly(target)
    if observed.lower() != envelope.H_C.digest.lower():
        raise IngressIdentityViolation("LINEAGE_HALT_ROOT_HASH_MISMATCH")


def boot_corpus(*args, **kwargs):
    """
    Scientific boot remains unauthorized.

    v0.2 materialization exists only to expose the bounded ingress contract
    for independent oracle-isolation preflight. No traversal or five-stage
    membrane evaluation is permitted at this standing.
    """
    raise RuntimeError(
        "SCIENTIFIC_BOOT_UNAUTHORIZED: "
        "MAGUS_BOOT_REFERENCE_IMPLEMENTATION_v0.2 is materialized but "
        "has not passed full oracle-isolation preflight."
    )


if __name__ == "__main__":
    raise SystemExit(
        "MAGUS_BOOT_REFERENCE_IMPLEMENTATION_v0.2 is "
        "MATERIALIZED_UNEXECUTED_PENDING_PREFLIGHT_REENTRY. "
        "No scientific boot execution surface is authorized."
    )
