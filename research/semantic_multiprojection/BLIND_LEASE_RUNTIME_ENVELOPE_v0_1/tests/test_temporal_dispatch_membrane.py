from pathlib import Path
import hashlib

import pytest

from src.integrity import tree_digest
from src.nonce_latch import DispatchLatch, DispatchLatchError
from src.temporal_dispatch_membrane import IntegrityHalt, ReplayHalt, TemporalDispatchMembrane


def _root(tmp_path: Path, payload: bytes = b"alpha") -> Path:
    root = tmp_path / "protected"
    root.mkdir()
    (root / "payload.bin").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (root / "SHA256SUMS.txt").write_text(f"{digest}  payload.bin\n", encoding="utf-8")
    return root


def _latch(root: Path, *, now=10.0, ttl=5.0):
    return DispatchLatch.materialize(
        "L_1", "X_001", tree_digest(root), now=now, ttl_seconds=ttl
    )


def test_fresh_measurement_consumes_matching_latch(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane = TemporalDispatchMembrane()
    consumed = membrane.acquire_verify_compare_and_consume(
        latch, protected_root=root, now=11.0, nonce=latch.nonce
    )
    assert consumed.state == "CONSUMED"
    assert membrane.was_consumed(latch)


def test_stale_latch_rejected_without_consumption(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    (root / "payload.bin").write_bytes(b"mutated")
    membrane = TemporalDispatchMembrane()
    with pytest.raises(IntegrityHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce=latch.nonce
        )
    assert latch.classify(now=11.0) == "ISSUED"
    assert not membrane.was_consumed(latch)


def test_missing_manifest_fails_closed_without_consumption(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    (root / "SHA256SUMS.txt").unlink()
    membrane = TemporalDispatchMembrane()
    with pytest.raises(IntegrityHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce=latch.nonce
        )
    assert not membrane.was_consumed(latch)


def test_caller_has_no_digest_override_surface(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    with pytest.raises(TypeError):
        TemporalDispatchMembrane().acquire_verify_compare_and_consume(
            latch, protected_root=root, dispatch_scope_digest=latch.scope_digest,
            now=11.0, nonce=latch.nonce
        )


def test_expiry_rejected_without_consumption(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root, ttl=1.0)
    membrane = TemporalDispatchMembrane()
    with pytest.raises(DispatchLatchError):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce=latch.nonce
        )
    assert not membrane.was_consumed(latch)


def test_nonce_mismatch_rejected_without_consumption(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane = TemporalDispatchMembrane()
    with pytest.raises(DispatchLatchError):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce="wrong"
        )
    assert not membrane.was_consumed(latch)


def test_replay_rejected(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane = TemporalDispatchMembrane()
    membrane.acquire_verify_compare_and_consume(
        latch, protected_root=root, now=11.0, nonce=latch.nonce
    )
    with pytest.raises(ReplayHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=12.0, nonce=latch.nonce
        )
