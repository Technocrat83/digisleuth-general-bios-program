import unittest
import threading

from magus_eg10_model import (
    AuthorityBinding,
    Attempt,
    BoundaryDomain,
    MountBinding,
    MountState,
    ReservationStatus,
    build_reference_runtime,
)


def mk_attempt(
    attempt_id: str,
    boundary: BoundaryDomain,
    reservation_id: str | None = None,
    mount_id: str = "mnt_browser_witness_inst_4821",
    principal_id: str = "agent_atelier_worker_9",
):
    mb = MountBinding(
        mount_id=mount_id,
        principal_id=principal_id,
        authority_token_fingerprint="sha256:test",
    )
    ab = AuthorityBinding(
        binding_id=f"bind:{attempt_id}",
        mount_id=mount_id,
        principal_id=principal_id,
    )
    return Attempt(
        attempt_id=attempt_id,
        boundary=boundary,
        boundary_identifier=f"{boundary.value}:fixture",
        mount_binding=mb,
        authority_binding=ab,
        reservation_id=reservation_id,
    )


class EG10PredeterminedOracleTests(unittest.TestCase):

    def test_HIST_01_unmount_before_actuation_denies(self):
        clock, mounts, ledger, gate = build_reference_runtime()
        mounts.mount("mnt_browser_witness_inst_4821")
        ledger.reserve("res1", "parent", 1500)
        mounts.invalidate("mnt_browser_witness_inst_4821", MountState.UNMOUNTED)

        r = gate.evaluate_and_actuate(mk_attempt("HIST-01", BoundaryDomain.EGRESS_DISPATCH, "res1"))
        self.assertFalse(r.may_execute)
        self.assertEqual(r.reason_code, "DENY_MOUNT_UNMOUNTED")
        ledger.release("res1")
        self.assertEqual(ledger.available(), 10_000)

    def test_HIST_02_local_actuation_before_unmount_permits(self):
        clock, mounts, ledger, gate = build_reference_runtime()
        mounts.mount("mnt_browser_witness_inst_4821")
        r = gate.evaluate_and_actuate(mk_attempt("HIST-02", BoundaryDomain.LOCAL_STATE))
        self.assertTrue(r.may_execute)
        self.assertEqual(r.reason_code, "PERMIT")
        mounts.invalidate("mnt_browser_witness_inst_4821", MountState.UNMOUNTED)

        r2 = gate.evaluate_and_actuate(mk_attempt("HIST-02b", BoundaryDomain.LOCAL_STATE))
        self.assertFalse(r2.may_execute)

    def test_HIST_03_egress_release_then_unmount_retains_liability(self):
        clock, mounts, ledger, gate = build_reference_runtime()
        mounts.mount("mnt_browser_witness_inst_4821")
        ledger.reserve("res3", "parent", 1500)
        r = gate.evaluate_and_actuate(
            mk_attempt("HIST-03", BoundaryDomain.EGRESS_DISPATCH, "res3"),
            remote_timeout=True,
        )
        self.assertTrue(r.may_execute)
        self.assertEqual(r.reason_code, "SET_PENDING_RECONCILIATION")
        self.assertEqual(
            ledger.get("res3").status,
            ReservationStatus.ENCUMBERED_PENDING_SETTLEMENT,
        )
        mounts.invalidate("mnt_browser_witness_inst_4821", MountState.UNMOUNTED)
        self.assertEqual(ledger.available(), 8500)

    def test_HIST_04_unknown_ordering_fails_closed(self):
        clock, mounts, ledger, gate = build_reference_runtime()
        mounts.mount("mnt_browser_witness_inst_4821")
        r = gate.evaluate_and_actuate(
            mk_attempt("HIST-04", BoundaryDomain.LOCAL_STATE),
            coherent_sequence=False,
        )
        self.assertFalse(r.may_execute)
        self.assertEqual(r.reason_code, "DENY_CLOSED_UNKNOWN_ORDERING")

    def test_HIST_05_timeout_requires_reconciliation(self):
        clock, mounts, ledger, gate = build_reference_runtime()
        mounts.mount("mnt_browser_witness_inst_4821")
        ledger.reserve("res5", "parent", 1000)
        r = gate.evaluate_and_actuate(
            mk_attempt("HIST-05", BoundaryDomain.EGRESS_DISPATCH, "res5"),
            remote_timeout=True,
        )
        self.assertTrue(r.may_execute)
        self.assertEqual(r.reason_code, "SET_PENDING_RECONCILIATION")
        self.assertEqual(ledger.available(), 9000)

    def test_single_use_attempt_replay_denied(self):
        clock, mounts, ledger, gate = build_reference_runtime()
        mounts.mount("mnt_browser_witness_inst_4821")
        a = mk_attempt("REPLAY-01", BoundaryDomain.LOCAL_STATE)
        first = gate.evaluate_and_actuate(a)
        second = gate.evaluate_and_actuate(a)
        self.assertTrue(first.may_execute)
        self.assertFalse(second.may_execute)
        self.assertEqual(second.reason_code, "DENY_SINGLE_USE_ATTEMPT_REPLAY")

    def test_sibling_concurrent_reservation_conserves_budget(self):
        clock, mounts, ledger, gate = build_reference_runtime(budget=1)
        outcomes = []

        def reserve(name):
            try:
                ledger.reserve(name, "parent", 1)
                outcomes.append("OK")
            except RuntimeError as e:
                outcomes.append(str(e))

        t1 = threading.Thread(target=reserve, args=("r1",))
        t2 = threading.Thread(target=reserve, args=("r2",))
        t1.start(); t2.start()
        t1.join(); t2.join()

        self.assertEqual(outcomes.count("OK"), 1)
        self.assertEqual(outcomes.count("DENY_BUDGET_OVERCOMMIT"), 1)
        self.assertEqual(ledger.reserved_outstanding(), 1)

    def test_ancestor_like_invalidation_without_bus_event_still_denies(self):
        # This bounded runner models source-of-truth registry lookup at gate time.
        clock, mounts, ledger, gate = build_reference_runtime()
        mounts.mount("mnt_browser_witness_inst_4821")
        mounts.invalidate("mnt_browser_witness_inst_4821", MountState.REVOKED)
        r = gate.evaluate_and_actuate(mk_attempt("NO-BUS-01", BoundaryDomain.LOCAL_STATE))
        self.assertFalse(r.may_execute)
        self.assertEqual(r.reason_code, "DENY_MOUNT_REVOKED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
