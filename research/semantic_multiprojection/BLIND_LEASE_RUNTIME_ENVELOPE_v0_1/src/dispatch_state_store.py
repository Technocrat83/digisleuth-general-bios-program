from __future__ import annotations

import hashlib
import json
import os
import secrets
from dataclasses import asdict
from pathlib import Path

import fcntl

from .nonce_latch import DispatchLatch, DispatchLatchError


class DispatchStateError(RuntimeError):
    pass


class DispatchReplayError(DispatchStateError):
    pass


class DispatchIdentityError(DispatchStateError):
    pass


class FileDispatchStateStore:
    """Persistent inter-process dispatch CAS using one locked file per nonce.

    The lock and state share one inode; records are updated in place so a
    concurrent process cannot retain a lock on a replaced, obsolete inode.
    """

    def __init__(self, state_dir: Path):
        self.state_dir = state_dir.resolve()
        self.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    @staticmethod
    def _dispatch_key(latch: DispatchLatch) -> str:
        material = f"{latch.lease_id}\0{latch.opaque_trial_id}\0{latch.nonce}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def _record_path(self, latch: DispatchLatch) -> Path:
        return self.state_dir / f"{self._dispatch_key(latch)}.json"

    @staticmethod
    def _write_locked(handle, record: dict) -> None:
        handle.seek(0)
        handle.truncate()
        json.dump(record, handle, sort_keys=True, separators=(",", ":"))
        handle.flush()
        os.fsync(handle.fileno())

    @staticmethod
    def _read_locked(handle) -> dict:
        handle.seek(0)
        raw = handle.read()
        if not raw:
            raise DispatchStateError("dispatch state record is empty")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise DispatchStateError("dispatch state record is malformed") from exc

    def issue_synthetic(self, latch: DispatchLatch) -> None:
        """Materialize synthetic ISSUED state; conveys no real dispatch authority."""
        path = self._record_path(latch)
        with path.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.seek(0)
            if handle.read():
                raise DispatchStateError("dispatch state already exists")
            record = asdict(latch)
            record["state"] = "ISSUED"
            self._write_locked(handle, record)

    def compare_and_swap_consumed(
        self,
        latch: DispatchLatch,
        *,
        now: float,
        nonce: str,
    ) -> DispatchLatch:
        path = self._record_path(latch)
        try:
            handle = path.open("r+", encoding="utf-8")
        except FileNotFoundError as exc:
            raise DispatchStateError("dispatch state record absent") from exc

        with handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            record = self._read_locked(handle)
            expected = asdict(latch)
            expected["state"] = "ISSUED"
            for field in (
                "lease_id", "opaque_trial_id", "nonce", "issued_at", "expires_at",
                "scope_digest", "protected_root", "protected_root_device",
                "protected_root_inode",
            ):
                if record.get(field) != expected[field]:
                    raise DispatchIdentityError(f"dispatch identity mismatch: {field}")
            if record.get("state") != "ISSUED":
                raise DispatchReplayError(
                    f"dispatch authorization not consumable: {record.get('state')}"
                )
            if now >= latch.expires_at:
                raise DispatchLatchError("dispatch authorization not consumable: EXPIRED")
            if not secrets.compare_digest(latch.nonce, nonce):
                raise DispatchLatchError("nonce mismatch")

            record["state"] = "CONSUMED"
            self._write_locked(handle, record)
            return latch.consume(now=now, nonce=nonce)

    def read_state(self, latch: DispatchLatch) -> str:
        path = self._record_path(latch)
        with path.open("r", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
            return str(self._read_locked(handle).get("state"))
