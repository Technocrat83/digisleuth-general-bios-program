from pathlib import Path
import hashlib

import pytest

from src.dispatch_state_store import FileDispatchStateStore
from src.integrity import tree_digest
from src.nonce_latch import DispatchLatch, DispatchLatchError
from src.temporal_dispatch_membrane import IntegrityHalt, ReplayHalt, TemporalDispatchMembrane


def _root(tmp_path: Path, name: str = "protected", payload: bytes = b"alpha") -> Path:
    root = tmp_path / name
    root.mkdir()
    (root / "payload.bin").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (root / "SHA256SUMS.txt").write_text(f"{digest}  payload.bin\n", encoding="utf-8")
    return root


def _latch(root: Path, *, now=10.0, ttl=5.0):
    return DispatchLatch.materialize(
        "L_1", "X_001", tree_digest(root), protected_root=root,
        now=now, ttl_seconds=ttl
    )


def _membrane(tmp_path: Path, latch: DispatchLatch):
    store = FileDispatchStateStore(tmp_path / "dispatch_state")
    store.issue_synthetic(latch)
    return TemporalDispatchMembrane(store), store


def test_fresh_measurement_consumes_matching_latch(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane, store = _membrane(tmp_path, latch)
    consumed = membrane.acquire_verify_compare_and_consume(
        latch, protected_root=root, now=11.0, nonce=latch.nonce
    )
    assert consumed.state == "CONSUMED"
    assert membrane.was_consumed(latch)
    assert store.read_state(latch) == "CONSUMED"


def test_stale_latch_rejected_without_consumption(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    (root / "payload.bin").write_bytes(b"mutated")
    membrane, store = _membrane(tmp_path, latch)
    with pytest.raises(IntegrityHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce=latch.nonce
        )
    assert latch.classify(now=11.0) == "ISSUED"
    assert not membrane.was_consumed(latch)
    assert store.read_state(latch) == "ISSUED"


def test_missing_manifest_fails_closed_without_consumption(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    (root / "SHA256SUMS.txt").unlink()
    membrane, store = _membrane(tmp_path, latch)
    with pytest.raises(IntegrityHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce=latch.nonce
        )
    assert not membrane.was_consumed(latch)
    assert store.read_state(latch) == "ISSUED"


def test_caller_has_no_digest_override_surface(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane, _ = _membrane(tmp_path, latch)
    with pytest.raises(TypeError):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, dispatch_scope_digest=latch.scope_digest,
            now=11.0, nonce=latch.nonce
        )


def test_root_substitution_with_identical_bytes_fails_closed(tmp_path):
    root = _root(tmp_path)
    substitute = _root(tmp_path, "substitute")
    assert tree_digest(substitute) == tree_digest(root)
    latch = _latch(root)
    membrane, store = _membrane(tmp_path, latch)
    with pytest.raises(IntegrityHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=substitute, now=11.0, nonce=latch.nonce
        )
    assert store.read_state(latch) == "ISSUED"


def test_root_replacement_at_same_path_fails_closed(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane, store = _membrane(tmp_path, latch)
    root.rename(tmp_path / "original")
    replacement = _root(tmp_path)
    assert replacement.resolve() == Path(latch.protected_root)
    with pytest.raises(IntegrityHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=replacement, now=11.0, nonce=latch.nonce
        )
    assert store.read_state(latch) == "ISSUED"


def test_mutation_between_measurements_fails_closed(tmp_path, monkeypatch):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane, store = _membrane(tmp_path, latch)
    original_acquire = membrane._acquire_verified
    acquisition_count = 0

    def mutate_between_measurements(protected_root, *, latch, now):
        nonlocal acquisition_count
        acquisition_count += 1
        if acquisition_count == 2:
            (root / "extra.bin").write_bytes(b"mutation-window")
        return original_acquire(protected_root, latch=latch, now=now)

    monkeypatch.setattr(membrane, "_acquire_verified", mutate_between_measurements)
    with pytest.raises(IntegrityHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce=latch.nonce
        )
    assert not membrane.was_consumed(latch)
    assert store.read_state(latch) == "ISSUED"


def test_expiry_rejected_without_consumption(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root, ttl=1.0)
    membrane, store = _membrane(tmp_path, latch)
    with pytest.raises(DispatchLatchError):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce=latch.nonce
        )
    assert not membrane.was_consumed(latch)
    assert store.read_state(latch) == "ISSUED"


def test_nonce_mismatch_rejected_without_consumption(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane, store = _membrane(tmp_path, latch)
    with pytest.raises(DispatchLatchError):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=11.0, nonce="wrong"
        )
    assert not membrane.was_consumed(latch)
    assert store.read_state(latch) == "ISSUED"


def test_same_instance_replay_rejected(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    membrane, store = _membrane(tmp_path, latch)
    membrane.acquire_verify_compare_and_consume(
        latch, protected_root=root, now=11.0, nonce=latch.nonce
    )
    with pytest.raises(ReplayHalt):
        membrane.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=12.0, nonce=latch.nonce
        )
    assert store.read_state(latch) == "CONSUMED"


def test_cross_instance_replay_rejected(tmp_path):
    root = _root(tmp_path)
    latch = _latch(root)
    store = FileDispatchStateStore(tmp_path / "dispatch_state")
    store.issue_synthetic(latch)
    first = TemporalDispatchMembrane(FileDispatchStateStore(store.state_dir))
    second = TemporalDispatchMembrane(FileDispatchStateStore(store.state_dir))
    first.acquire_verify_compare_and_consume(
        latch, protected_root=root, now=11.0, nonce=latch.nonce
    )
    with pytest.raises(ReplayHalt):
        second.acquire_verify_compare_and_consume(
            latch, protected_root=root, now=12.0, nonce=latch.nonce
        )
    assert store.read_state(latch) == "CONSUMED"
