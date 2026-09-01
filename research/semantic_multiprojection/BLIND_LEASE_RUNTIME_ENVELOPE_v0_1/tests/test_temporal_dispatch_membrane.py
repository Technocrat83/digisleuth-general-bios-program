import pytest

from src.nonce_latch import DispatchLatch, DispatchLatchError
from src.temporal_dispatch_membrane import IntegrityHalt, ReplayHalt, TemporalDispatchMembrane

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def _latch(*, now=10.0, ttl=5.0):
    return DispatchLatch.materialize("L_1", "X_001", DIGEST_A, now=now, ttl_seconds=ttl)


def test_stale_integrity_rejected_without_consumption():
    membrane = TemporalDispatchMembrane()
    latch = _latch()
    with pytest.raises(IntegrityHalt):
        membrane.revalidate_and_consume(
            latch, lease_scope_digest=DIGEST_A, dispatch_scope_digest=DIGEST_B,
            now=11.0, nonce=latch.nonce
        )
    assert latch.classify(now=11.0) == "ISSUED"
    assert not membrane.was_consumed(latch)


def test_latch_binding_mismatch_rejected_without_consumption():
    membrane = TemporalDispatchMembrane()
    latch = _latch()
    with pytest.raises(IntegrityHalt):
        membrane.revalidate_and_consume(
            latch, lease_scope_digest=DIGEST_B, dispatch_scope_digest=DIGEST_B,
            now=11.0, nonce=latch.nonce
        )
    assert latch.classify(now=11.0) == "ISSUED"
    assert not membrane.was_consumed(latch)


def test_expiry_rejection():
    membrane = TemporalDispatchMembrane()
    latch = _latch(ttl=1.0)
    with pytest.raises(DispatchLatchError):
        membrane.revalidate_and_consume(
            latch, lease_scope_digest=DIGEST_A, dispatch_scope_digest=DIGEST_A,
            now=11.0, nonce=latch.nonce
        )
    assert not membrane.was_consumed(latch)


def test_nonce_mismatch_rejection():
    membrane = TemporalDispatchMembrane()
    latch = _latch()
    with pytest.raises(DispatchLatchError):
        membrane.revalidate_and_consume(
            latch, lease_scope_digest=DIGEST_A, dispatch_scope_digest=DIGEST_A,
            now=11.0, nonce="wrong"
        )
    assert not membrane.was_consumed(latch)


def test_successful_one_shot_transition():
    membrane = TemporalDispatchMembrane()
    latch = _latch()
    consumed = membrane.revalidate_and_consume(
        latch, lease_scope_digest=DIGEST_A, dispatch_scope_digest=DIGEST_A,
        now=11.0, nonce=latch.nonce
    )
    assert consumed.state == "CONSUMED"
    assert membrane.was_consumed(latch)


def test_original_issued_object_replay_rejected_by_membrane():
    membrane = TemporalDispatchMembrane()
    latch = _latch()
    membrane.revalidate_and_consume(
        latch, lease_scope_digest=DIGEST_A, dispatch_scope_digest=DIGEST_A,
        now=11.0, nonce=latch.nonce
    )
    # The original frozen latch object still says ISSUED, but membrane state blocks replay.
    assert latch.state == "ISSUED"
    with pytest.raises(ReplayHalt):
        membrane.revalidate_and_consume(
            latch, lease_scope_digest=DIGEST_A, dispatch_scope_digest=DIGEST_A,
            now=12.0, nonce=latch.nonce
        )
