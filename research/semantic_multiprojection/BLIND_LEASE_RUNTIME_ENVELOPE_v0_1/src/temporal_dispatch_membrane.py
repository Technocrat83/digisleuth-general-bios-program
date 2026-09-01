from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock

from .integrity import IntegrityError, acquire_fresh_integrity
from .nonce_latch import DispatchLatch


class IntegrityHalt(RuntimeError):
    """Fresh dispatch-time identity is absent, untrusted, or mismatched."""


class ReplayHalt(RuntimeError):
    """A one-shot dispatch authorization was already consumed."""


@dataclass
class TemporalDispatchMembrane:
    """Causally bind fresh protected-root measurement to one-shot consumption.

    Ordering is fixed:
        ACQUIRE_FRESH -> VERIFY_PROVENANCE -> COMPARE -> CONSUME

    Callers provide the protected root, never a measured dispatch digest. The
    membrane never invokes an evaluator and never mutates specimen bytes.
    """

    _consumed_nonces: set[str] = field(default_factory=set, init=False, repr=False)
    _coupling_lock: RLock = field(default_factory=RLock, init=False, repr=False)

    def acquire_verify_compare_and_consume(
        self,
        latch: DispatchLatch,
        *,
        protected_root: Path,
        now: float,
        nonce: str,
    ) -> DispatchLatch:
        with self._coupling_lock:
            if latch.nonce in self._consumed_nonces:
                raise ReplayHalt("dispatch authorization already consumed")

            try:
                measurement = acquire_fresh_integrity(protected_root, now=now)
            except (IntegrityError, OSError, ValueError) as exc:
                raise IntegrityHalt("fresh integrity measurement unresolved") from exc

            if not measurement.provenance_valid:
                raise IntegrityHalt("fresh integrity provenance invalid")
            if not secrets.compare_digest(measurement.digest, latch.scope_digest):
                raise IntegrityHalt("fresh dispatch-time integrity mismatch")

            consumed = latch.consume(now=now, nonce=nonce)
            self._consumed_nonces.add(latch.nonce)
            return consumed

    def was_consumed(self, latch: DispatchLatch) -> bool:
        return latch.nonce in self._consumed_nonces
