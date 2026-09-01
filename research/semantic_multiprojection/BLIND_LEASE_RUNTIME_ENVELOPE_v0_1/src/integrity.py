from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class IntegrityError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root: Path, *, exclude: Iterable[str] = ()) -> str:
    root = root.resolve(strict=True)
    excluded = set(exclude)
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        h.update(rel.encode("utf-8")); h.update(b"\0"); h.update(sha256_file(path).encode("ascii")); h.update(b"\n")
    return h.hexdigest()


def parse_sha256_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        digest, rel = line.split(maxsplit=1); rel = rel.strip()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise IntegrityError(f"invalid SHA-256 digest for {rel!r}")
        if rel in entries: raise IntegrityError(f"duplicate manifest path: {rel}")
        entries[rel] = digest
    return entries


def verify_manifest(root: Path, manifest_name: str = "SHA256SUMS.txt") -> dict[str, str]:
    root = root.resolve(strict=True); expected = parse_sha256_manifest(root / manifest_name); actual = {}
    for rel, digest in expected.items():
        path = (root / rel).resolve(strict=True)
        if root not in path.parents: raise IntegrityError(f"manifest path escapes battery root: {rel}")
        got = sha256_file(path); actual[rel] = got
        if got != digest: raise IntegrityError(f"hash mismatch: {rel}")
    return actual


@dataclass(frozen=True)
class BatteryIntegrityWitness:
    pre_tree_digest: str
    post_tree_digest: str
    manifest_verified: bool
    @property
    def unchanged(self) -> bool: return self.pre_tree_digest == self.post_tree_digest


def read_only_integrity_inspection(root: Path) -> BatteryIntegrityWitness:
    pre = tree_digest(root); verify_manifest(root); post = tree_digest(root)
    if pre != post: raise IntegrityError("battery tree changed during integrity inspection")
    return BatteryIntegrityWitness(pre, post, True)
