from __future__ import annotations

import hashlib
import json
import os
import platform
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "contract" / "execution_contract_payload.json"
ARTIFACT_PATH = ROOT / "artifacts" / "bounded_output.txt"
RECEIPT_DIR = ROOT / "receipts"
LEDGER_PATH = ROOT / "ledger" / "submitted_witnesses.jsonl"


def canonical_bytes(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def allowed_write(target: Path, grant: dict) -> bool:
    rel = relative(target)
    allowed = set(grant.get("write", []))
    if rel in allowed:
        return True
    if rel.startswith("receipts/") and "receipts/*.json" in allowed and rel.endswith(".json"):
        return True
    return False


def main() -> int:
    contract_payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract_revision = sha256_hex(canonical_bytes(contract_payload))
    attempt_id = str(uuid.uuid4())
    grant = contract_payload["authenticated_grant"]

    artifacts = []
    observations = []
    blocked_operations = []
    violations = []

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not allowed_write(ARTIFACT_PATH, grant):
        violations.append({"operation": "write", "target": relative(ARTIFACT_PATH), "reason": "grant_mismatch"})
    else:
        artifact_content = (
            "PGE bounded reference artifact\n"
            f"task_id={contract_payload['task_id']}\n"
            f"contract_revision={contract_revision}\n"
            f"attempt_id={attempt_id}\n"
        )
        ARTIFACT_PATH.write_text(artifact_content, encoding="utf-8")
        artifacts.append({
            "path": relative(ARTIFACT_PATH),
            "sha256": sha256_hex(ARTIFACT_PATH.read_bytes()),
            "bytes": ARTIFACT_PATH.stat().st_size,
        })
        observations.append({"event": "bounded_write_completed", "target": relative(ARTIFACT_PATH)})

    unauthorized_target = ROOT.parent / "PGE_UNAUTHORIZED_WRITE_SENTINEL.txt"
    try:
        unauthorized_rel = unauthorized_target.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        unauthorized_rel = "../PGE_UNAUTHORIZED_WRITE_SENTINEL.txt"

    blocked_operations.append({
        "operation": "write",
        "target": unauthorized_rel,
        "result": "BLOCKED_OUTSIDE_AUTHORITY",
        "performed": False,
        "reason": "target_outside_authenticated_grant",
    })

    executor = {
        "executor_label": contract_payload["workspace"]["executor_label"],
        "host_os": platform.platform(),
        "python": platform.python_version(),
        "cwd": os.getcwd(),
        "attestation_limit": "Task execution is self-reported by this adapter; receipt does not prove editor-wide containment or independent host attestation.",
    }

    completion_assertion = (
        f"For task {contract_payload['task_id']}, dossier revision {contract_revision}, "
        f"and execution attempt {attempt_id}, executor {executor['executor_label']} produced the bound artifacts "
        "under this authenticated grant. These observations, blocked operations, and violations describe the attempt. "
        "Execution completion is asserted only within that scope; validation, acceptance, and promotion require their own authorized witnesses."
    )

    receipt = {
        "schema_version": "PGE_REVISION_BOUND_EXECUTION_RECEIPT_v0.1",
        "task_id": contract_payload["task_id"],
        "contract_revision": contract_revision,
        "attempt_id": attempt_id,
        "executor": executor,
        "authenticated_grant": grant,
        "artifacts": artifacts,
        "observations": observations,
        "blocked_operations": blocked_operations,
        "violations": violations,
        "completion_assertion": completion_assertion,
        "standing_claims": {
            "execution_completion": "ASSERTED_WITHIN_ATTEMPT_SCOPE",
            "validation": "UNCLAIMED",
            "acceptance": "UNCLAIMED",
            "promotion": "UNCLAIMED",
            "executor_conformance": "UNCLAIMED",
            "editor_wide_containment": "UNCLAIMED"
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    receipt_name = f"receipt_{attempt_id}.json"
    receipt_path = RECEIPT_DIR / receipt_name
    if not allowed_write(receipt_path, grant):
        raise RuntimeError("Receipt destination is outside authenticated grant")
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("PGE bounded reference attempt finished")
    print(f"task_id: {contract_payload['task_id']}")
    print(f"contract_revision: {contract_revision}")
    print(f"attempt_id: {attempt_id}")
    print(f"receipt: {receipt_path}")
    print("standing: host-specific execution receipt only; no conformance or promotion claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
