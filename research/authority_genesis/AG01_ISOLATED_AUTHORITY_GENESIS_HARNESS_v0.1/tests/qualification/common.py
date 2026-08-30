"""Shared, non-scientific utilities for AG01 qualification realizers."""
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMIT = "12418b9db7185c39c1d96c09af74c3e01a3f9239"
H_MAT = "sha256:1641442c2083bfb59235a34288234da8d3aa27488f9eccb7aad51429e9712f4b"
VALID = {"PASS", "FAIL", "INCOMPLETE"}

def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def parse_python(path: Path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

def witness(check_id, realizer_id, inputs, probe_type, raw, predicate, result, reason=None):
    assert result in VALID
    record = {
        "check_id": check_id,
        "realizer_id": realizer_id,
        "apparatus_commit": COMMIT,
        "materialization_hash": H_MAT,
        "inputs": [str(x) for x in inputs],
        "probe_type": probe_type,
        "raw_observations": raw,
        "expected_predicate": predicate,
        "result": result,
        "failure_or_incompleteness_reason": reason,
    }
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["witness_digest"] = "sha256:" + hashlib.sha256(canonical).hexdigest()
    return record
