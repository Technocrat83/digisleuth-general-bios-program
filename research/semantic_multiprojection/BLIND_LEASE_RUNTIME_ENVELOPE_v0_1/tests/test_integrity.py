from pathlib import Path
import hashlib

import pytest

from src.integrity import IntegrityError, read_only_integrity_inspection


def _make_tree(tmp_path: Path) -> Path:
    root = tmp_path / "battery"
    root.mkdir()
    (root / "a.txt").write_text("alpha", encoding="utf-8")
    digest = hashlib.sha256(b"alpha").hexdigest()
    (root / "SHA256SUMS.txt").write_text(f"{digest}  a.txt\n", encoding="utf-8")
    return root


def test_integrity_pre_post_digest_stable(tmp_path):
    root = _make_tree(tmp_path)
    witness = read_only_integrity_inspection(root)
    assert witness.manifest_verified
    assert witness.unchanged


def test_integrity_fails_closed_on_mismatch(tmp_path):
    root = _make_tree(tmp_path)
    (root / "a.txt").write_text("mutated", encoding="utf-8")
    with pytest.raises(IntegrityError):
        read_only_integrity_inspection(root)
