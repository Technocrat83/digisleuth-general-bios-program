import pytest

from src.nonce_latch import DispatchLatch, DispatchLatchError


DIGEST = "a" * 64


def test_nonce_is_one_shot(tmp_path):
    latch = DispatchLatch.materialize(
        "L_1", "X_001", DIGEST, protected_root=tmp_path,
        now=10.0, ttl_seconds=5.0
    )
    consumed = latch.consume(now=11.0, nonce=latch.nonce)
    assert consumed.state == "CONSUMED"
    with pytest.raises(DispatchLatchError):
        consumed.consume(now=12.0, nonce=latch.nonce)


def test_expired_latch_fails_closed(tmp_path):
    latch = DispatchLatch.materialize(
        "L_1", "X_001", DIGEST, protected_root=tmp_path,
        now=10.0, ttl_seconds=1.0
    )
    assert latch.classify(now=11.0) == "EXPIRED"
    with pytest.raises(DispatchLatchError):
        latch.consume(now=11.0, nonce=latch.nonce)


def test_wrong_nonce_denied(tmp_path):
    latch = DispatchLatch.materialize(
        "L_1", "X_001", DIGEST, protected_root=tmp_path,
        now=10.0, ttl_seconds=5.0
    )
    with pytest.raises(DispatchLatchError):
        latch.consume(now=11.0, nonce="wrong")
