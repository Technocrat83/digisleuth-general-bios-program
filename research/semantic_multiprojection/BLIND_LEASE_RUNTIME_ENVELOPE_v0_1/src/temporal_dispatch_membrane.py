from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock

from .dispatch_state_store import (
    DispatchIdentityError,
    DispatchReplayError,
    DispatchStateError,
    FileDispatchStateStore,
)
from .integrity import (
    IntegrityError,
    acquire_fresh_integrity,
    resolve_protected_root_identity,
)
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

    state_store: FileDispatchStateStore
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

            root_identity = resolve_protected_root_identity(protected_root)
            if (
                root_identity.canonical_path != latch.protected_root
                or root_identity.device != latch.protected_root_device
                or root_identity.inode != latch.protected_root_inode
            ):
                raise IntegrityHalt("presented root is not the lease-bound protected root")

            measurement = self._acquire_verified(protected_root, latch=latch, now=now)
            if not secrets.compare_digest(measurement.digest, latch.scope_digest):
                raise IntegrityHalt("fresh dispatch-time integrity mismatch")

            # Close the mutation window before the authoritative transition.
            terminal = self._acquire_verified(protected_root, latch=latch, now=now)
            if not secrets.compare_digest(terminal.digest, measurement.digest):
                raise IntegrityHalt("protected root changed during consumption coupling")

            try:
                consumed = self.state_store.compare_and_swap_consumed(
                    latch, now=now, nonce=nonce
                )
            except DispatchReplayError as exc:
                raise ReplayHalt("dispatch authorization already consumed") from exc
            except (DispatchIdentityError, DispatchStateError) as exc:
                raise IntegrityHalt("authoritative dispatch state invalid") from exc
            self._consumed_nonces.add(latch.nonce)
            return consumed

    @staticmethod
    def _acquire_verified(
        protected_root: Path, *, latch: DispatchLatch, now: float
    ):
        try:
            measurement = acquire_fresh_integrity(protected_root, now=now)
        except (IntegrityError, OSError, ValueError) as exc:
            raise IntegrityHalt("fresh integrity measurement unresolved") from exc
        if not measurement.provenance_valid:
            raise IntegrityHalt("fresh integrity provenance invalid")
        if (
            measurement.protected_root != latch.protected_root
            or measurement.protected_root_device != latch.protected_root_device
            or measurement.protected_root_inode != latch.protected_root_inode
        ):
            raise IntegrityHalt("measurement root identity is not lease-bound")
        return measurement

    def was_consumed(self, latch: DispatchLatch) -> bool:
        return latch.nonce in self._consumed_nonces
