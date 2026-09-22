from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List
import threading


class MountState(str, Enum):
    ACTIVE = "ACTIVE"
    UNMOUNTING = "UNMOUNTING"
    UNMOUNTED = "UNMOUNTED"
    REVOKED = "REVOKED"


class BoundaryDomain(str, Enum):
    LOCAL_STATE = "LOCAL_STATE"
    EGRESS_DISPATCH = "EGRESS_DISPATCH"
    REMOTE_EFFECT = "REMOTE_EFFECT"


class ReservationStatus(str, Enum):
    HELD = "HELD"
    ENCUMBERED_PENDING_SETTLEMENT = "ENCUMBERED_PENDING_SETTLEMENT"
    SETTLED = "SETTLED"
    RELEASED = "RELEASED"


@dataclass(frozen=True)
class MountBinding:
    mount_id: str
    principal_id: str
    authority_token_fingerprint: str


@dataclass
class Reservation:
    reservation_id: str
    parent_ledger_id: str
    amount: int
    unit: str
    status: ReservationStatus = ReservationStatus.HELD
    spent: int = 0

    @property
    def remaining(self) -> int:
        return self.amount - self.spent


@dataclass
class AuthorityBinding:
    binding_id: str
    mount_id: str
    principal_id: str
    valid: bool = True
    explicitly_denied: bool = False
    ceased: bool = False


@dataclass
class Attempt:
    attempt_id: str
    boundary: BoundaryDomain
    boundary_identifier: str
    mount_binding: MountBinding
    authority_binding: AuthorityBinding
    reservation_id: Optional[str] = None
    assigned: bool = True
    admitted: bool = True


@dataclass
class PreExecutionReceipt:
    receipt_id: str
    attempt_id: str
    global_sequence_number: Optional[int]
    last_revocation_sequence_observed: Optional[int]
    may_execute: bool
    reason_code: str
    consumed_for_dispatch: bool
    reservation_status: Optional[str]
    boundary_identifier: str
    mount_id: str
    principal_id: str


class SequenceClock:
    """Single-process monotonic sequence source.

    This is the bounded reference linearization mechanism. It does not claim
    distributed consensus or cross-host atomicity.
    """
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def next(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    def current(self) -> int:
        with self._lock:
            return self._value


class MountRegistry:
    def __init__(self, clock: SequenceClock) -> None:
        self.clock = clock
        self._state: Dict[str, MountState] = {}
        self._last_invalidation_seq: Dict[str, int] = {}
        self._lock = threading.Lock()

    def mount(self, mount_id: str) -> int:
        with self._lock:
            seq = self.clock.next()
            self._state[mount_id] = MountState.ACTIVE
            return seq

    def invalidate(self, mount_id: str, state: MountState = MountState.REVOKED) -> int:
        with self._lock:
            seq = self.clock.next()
            self._state[mount_id] = state
            self._last_invalidation_seq[mount_id] = seq
            return seq

    def status(self, mount_id: str) -> MountState:
        with self._lock:
            return self._state.get(mount_id, MountState.UNMOUNTED)

    def last_invalidation_seq(self, mount_id: str) -> Optional[int]:
        with self._lock:
            return self._last_invalidation_seq.get(mount_id)


class BudgetLedger:
    def __init__(self, budget: int, unit: str) -> None:
        self.budget = budget
        self.unit = unit
        self.spent = 0
        self._reservations: Dict[str, Reservation] = {}
        self._lock = threading.Lock()

    def reserved_outstanding(self) -> int:
        return sum(
            r.remaining
            for r in self._reservations.values()
            if r.status in {
                ReservationStatus.HELD,
                ReservationStatus.ENCUMBERED_PENDING_SETTLEMENT,
            }
        )

    def available(self) -> int:
        return self.budget - self.spent - self.reserved_outstanding()

    def reserve(self, reservation_id: str, parent_ledger_id: str, amount: int) -> Reservation:
        with self._lock:
            if amount < 0:
                raise ValueError("negative reservation")
            if amount > self.available():
                raise RuntimeError("DENY_BUDGET_OVERCOMMIT")
            r = Reservation(
                reservation_id=reservation_id,
                parent_ledger_id=parent_ledger_id,
                amount=amount,
                unit=self.unit,
            )
            self._reservations[reservation_id] = r
            return r

    def get(self, reservation_id: str) -> Reservation:
        with self._lock:
            return self._reservations[reservation_id]

    def encumber_pending_settlement(self, reservation_id: str) -> None:
        with self._lock:
            self._reservations[reservation_id].status = ReservationStatus.ENCUMBERED_PENDING_SETTLEMENT

    def release(self, reservation_id: str) -> None:
        with self._lock:
            self._reservations[reservation_id].status = ReservationStatus.RELEASED

    def settle_success(self, reservation_id: str, actual_spend: Optional[int] = None) -> None:
        with self._lock:
            r = self._reservations[reservation_id]
            spend = r.amount if actual_spend is None else actual_spend
            if spend < 0 or spend > r.amount:
                raise ValueError("invalid spend")
            r.spent = spend
            self.spent += spend
            r.status = ReservationStatus.SETTLED

    def settle_verified_failure(self, reservation_id: str) -> None:
        with self._lock:
            r = self._reservations[reservation_id]
            r.status = ReservationStatus.RELEASED


class ExecutionGate:
    def __init__(self, clock: SequenceClock, mounts: MountRegistry, ledger: BudgetLedger) -> None:
        self.clock = clock
        self.mounts = mounts
        self.ledger = ledger
        self._gate_lock = threading.Lock()
        self._consumed_attempts: set[str] = set()

    def evaluate_and_actuate(
        self,
        attempt: Attempt,
        *,
        coherent_sequence: bool = True,
        remote_timeout: bool = False,
    ) -> PreExecutionReceipt:
        # In this bounded model, the gate lock is the linearization enclosure
        # for mount-state observation and controlled actuation release.
        with self._gate_lock:
            if not coherent_sequence:
                return self._receipt(
                    attempt, None, False, "DENY_CLOSED_UNKNOWN_ORDERING", False
                )

            if attempt.attempt_id in self._consumed_attempts:
                return self._receipt(
                    attempt, self.clock.current(), False, "DENY_SINGLE_USE_ATTEMPT_REPLAY", False
                )

            if not attempt.assigned:
                return self._receipt(attempt, self.clock.current(), False, "DENY_NOT_ASSIGNED", False)
            if not attempt.admitted:
                return self._receipt(attempt, self.clock.current(), False, "DENY_NOT_ADMITTED", False)

            B = attempt.authority_binding
            MB = attempt.mount_binding

            if B.principal_id != MB.principal_id or B.mount_id != MB.mount_id:
                return self._receipt(attempt, self.clock.current(), False, "DENY_PRINCIPAL_MOUNT_MISMATCH", False)
            if not B.valid:
                return self._receipt(attempt, self.clock.current(), False, "DENY_INVALID_AUTHORITY_BINDING", False)
            if B.explicitly_denied:
                return self._receipt(attempt, self.clock.current(), False, "DENY_EXPLICIT", False)
            if B.ceased:
                return self._receipt(attempt, self.clock.current(), False, "DENY_CEASED", False)

            status = self.mounts.status(B.mount_id)
            if status != MountState.ACTIVE:
                return self._receipt(attempt, self.clock.current(), False, f"DENY_MOUNT_{status.value}", False)

            if attempt.reservation_id is not None:
                r = self.ledger.get(attempt.reservation_id)
                if r.status not in {ReservationStatus.HELD, ReservationStatus.ENCUMBERED_PENDING_SETTLEMENT}:
                    return self._receipt(attempt, self.clock.current(), False, "DENY_RESERVATION_NOT_ACTIVE", False)

            act_seq = self.clock.next()
            self._consumed_attempts.add(attempt.attempt_id)

            # Controlled boundary semantics:
            # LOCAL_STATE commits here.
            # EGRESS_DISPATCH means release occurred here; remote effect is outside control.
            if attempt.boundary == BoundaryDomain.EGRESS_DISPATCH and attempt.reservation_id:
                if remote_timeout:
                    self.ledger.encumber_pending_settlement(attempt.reservation_id)
                    reason = "SET_PENDING_RECONCILIATION"
                else:
                    reason = "PERMIT_RELEASED"
            else:
                reason = "PERMIT"

            return self._receipt(attempt, act_seq, True, reason, True)

    def _receipt(
        self,
        attempt: Attempt,
        seq: Optional[int],
        may_execute: bool,
        reason_code: str,
        consumed: bool,
    ) -> PreExecutionReceipt:
        reservation_status = None
        if attempt.reservation_id is not None:
            reservation_status = self.ledger.get(attempt.reservation_id).status.value

        return PreExecutionReceipt(
            receipt_id=f"rcpt:{attempt.attempt_id}:{seq if seq is not None else 'unknown'}",
            attempt_id=attempt.attempt_id,
            global_sequence_number=seq,
            last_revocation_sequence_observed=self.mounts.last_invalidation_seq(
                attempt.mount_binding.mount_id
            ),
            may_execute=may_execute,
            reason_code=reason_code,
            consumed_for_dispatch=consumed,
            reservation_status=reservation_status,
            boundary_identifier=attempt.boundary_identifier,
            mount_id=attempt.mount_binding.mount_id,
            principal_id=attempt.mount_binding.principal_id,
        )


def build_reference_runtime(budget: int = 10_000):
    clock = SequenceClock()
    mounts = MountRegistry(clock)
    ledger = BudgetLedger(budget=budget, unit="MODEL_INFERENCE_TOKENS")
    gate = ExecutionGate(clock, mounts, ledger)
    return clock, mounts, ledger, gate
