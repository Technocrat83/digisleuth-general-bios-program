"""Shared, non-scientific utilities for AG01 qualification realizers."""
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMIT = "71b0461161242ffcf876e4d5ba95b0905c9e3733"
H_MAT = "sha256:a59293b5158a13319659216dde5ca1f71ce98e6b643c55ef78c54748f544a872"
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
