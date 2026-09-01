from __future__ import annotations

import secrets
from dataclasses import dataclass, field

from .nonce_latch import DispatchLatch, DispatchLatchError


class IntegrityHalt(RuntimeError):
    """Dispatch-time integrity identity differs from the lease-bound identity."""


class ReplayHalt(RuntimeError):
    """A one-shot dispatch authorization was already consumed."""


@dataclass
class TemporalDispatchMembrane:
    """Couples immediate integrity revalidation to one-shot latch consumption.

    Ordering is fixed:
        REVALIDATE -> CONSUME -> RETURN CONSUMED AUTHORIZATION

    The membrane never invokes an evaluator and never mutates specimen bytes.
    """
    _consumed_nonces: set[str] = field(default_factory=set, init=False, repr=False)

    def revalidate_and_consume(
        self,
        latch: DispatchLatch,
        *,
        lease_scope_digest: str,
        dispatch_scope_digest: str,
        now: float,
        nonce: str,
    ) -> DispatchLatch:
        if latch.nonce in self._consumed_nonces:
            raise ReplayHalt("dispatch authorization already consumed")

        # Revalidation MUST precede any consumption attempt.
        if not secrets.compare_digest(lease_scope_digest, dispatch_scope_digest):
            raise IntegrityHalt("dispatch-time integrity revalidation failed")
        if not secrets.compare_digest(latch.scope_digest, lease_scope_digest):
            raise IntegrityHalt("lease identity does not match latch-bound scope")

        consumed = latch.consume(now=now, nonce=nonce)
        self._consumed_nonces.add(latch.nonce)
        return consumed

    def was_consumed(self, latch: DispatchLatch) -> bool:
        return latch.nonce in self._consumed_nonces
