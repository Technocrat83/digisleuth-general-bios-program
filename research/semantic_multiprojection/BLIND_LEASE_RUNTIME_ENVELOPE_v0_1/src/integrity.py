from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class IntegrityError(RuntimeError):
    pass


INTERNAL_INTEGRITY_PROVENANCE = "BLE_INTERNAL_INTEGRITY_ENGINE_v0.1"


@dataclass(frozen=True)
class ProtectedRootIdentity:
    canonical_path: str
    device: int
    inode: int


def resolve_protected_root_identity(root: Path) -> ProtectedRootIdentity:
    canonical = root.resolve(strict=True)
    stat = canonical.stat()
    if not canonical.is_dir():
        raise IntegrityError("protected root must be a directory")
    return ProtectedRootIdentity(str(canonical), stat.st_dev, stat.st_ino)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root: Path, *, exclude: Iterable[str] = ()) -> str:
    """Deterministic digest over relative path + file digest. Read-only by construction."""
    root = root.resolve(strict=True)
    excluded = set(exclude)
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(sha256_file(path).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def parse_sha256_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise IntegrityError(f"invalid SHA-256 digest for {rel!r}")
        if rel in entries:
            raise IntegrityError(f"duplicate manifest path: {rel}")
        entries[rel] = digest
    return entries


def verify_manifest(root: Path, manifest_name: str = "SHA256SUMS.txt") -> dict[str, str]:
    root = root.resolve(strict=True)
    manifest = root / manifest_name
    expected = parse_sha256_manifest(manifest)
    actual: dict[str, str] = {}
    for rel, digest in expected.items():
        path = (root / rel).resolve(strict=True)
        if root not in path.parents:
            raise IntegrityError(f"manifest path escapes battery root: {rel}")
        got = sha256_file(path)
        actual[rel] = got
        if got != digest:
            raise IntegrityError(f"hash mismatch: {rel}")
    return actual


@dataclass(frozen=True)
class BatteryIntegrityWitness:
    pre_tree_digest: str
    post_tree_digest: str
    manifest_verified: bool

    @property
    def unchanged(self) -> bool:
        return self.pre_tree_digest == self.post_tree_digest


@dataclass(frozen=True)
class FreshIntegrityMeasurement:
    """Internally acquired dispatch-time identity with causal provenance."""

    digest: str
    provenance: str
    acquired_at: float
    protected_root: str
    protected_root_device: int
    protected_root_inode: int
    manifest_verified: bool
    unchanged_during_acquisition: bool

    @property
    def provenance_valid(self) -> bool:
        return (
            self.provenance == INTERNAL_INTEGRITY_PROVENANCE
            and self.manifest_verified
            and self.unchanged_during_acquisition
            and bool(self.protected_root)
            and self.protected_root_device >= 0
            and self.protected_root_inode > 0
        )


def read_only_integrity_inspection(root: Path) -> BatteryIntegrityWitness:
    pre = tree_digest(root)
    verify_manifest(root)
    post = tree_digest(root)
    if pre != post:
        raise IntegrityError("battery tree changed during integrity inspection")
    return BatteryIntegrityWitness(pre, post, True)


def acquire_fresh_integrity(root: Path, *, now: float) -> FreshIntegrityMeasurement:
    """Acquire identity directly from the protected root; no digest override exists."""
    identity_pre = resolve_protected_root_identity(root)
    protected_root = Path(identity_pre.canonical_path)
    witness = read_only_integrity_inspection(protected_root)
    identity_post = resolve_protected_root_identity(root)
    if identity_pre != identity_post:
        raise IntegrityError("protected root identity changed during acquisition")
    return FreshIntegrityMeasurement(
        digest=witness.post_tree_digest,
        provenance=INTERNAL_INTEGRITY_PROVENANCE,
        acquired_at=now,
        protected_root=identity_post.canonical_path,
        protected_root_device=identity_post.device,
        protected_root_inode=identity_post.inode,
        manifest_verified=witness.manifest_verified,
        unchanged_during_acquisition=witness.unchanged,
    )
