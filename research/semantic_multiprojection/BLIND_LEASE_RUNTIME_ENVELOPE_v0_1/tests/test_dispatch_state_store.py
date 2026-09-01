from multiprocessing import get_context
from pathlib import Path

from src.dispatch_state_store import DispatchReplayError, FileDispatchStateStore
from src.nonce_latch import DispatchLatch


DIGEST = "a" * 64


def _cas_worker(state_dir, latch, start, results):
    store = FileDispatchStateStore(Path(state_dir))
    start.wait()
    try:
        store.compare_and_swap_consumed(latch, now=11.0, nonce=latch.nonce)
        results.put("CONSUMED")
    except DispatchReplayError:
        results.put("REJECTED")


def test_multiprocess_cas_allows_exactly_one_consumer(tmp_path):
    latch = DispatchLatch.materialize(
        "L_1", "X_001", DIGEST, protected_root=tmp_path,
        now=10.0, ttl_seconds=5.0
    )
    store = FileDispatchStateStore(tmp_path / "state")
    store.issue_synthetic(latch)
    context = get_context("fork")
    start = context.Event()
    results = context.Queue()
    processes = [
        context.Process(
            target=_cas_worker,
            args=(str(store.state_dir), latch, start, results),
        )
        for _ in range(4)
    ]
    for process in processes:
        process.start()
    start.set()
    outcomes = [results.get(timeout=5) for _ in processes]
    for process in processes:
        process.join(timeout=5)
        assert process.exitcode == 0
    assert outcomes.count("CONSUMED") == 1
    assert outcomes.count("REJECTED") == 3
    assert store.read_state(latch) == "CONSUMED"
