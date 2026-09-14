"""Run fixture cores in fresh processes, then reveal isolated expected vectors."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CORES = ROOT / "fixtures" / "fixture_cores_v0.2.json"
ORACLE = ROOT / "oracle" / "expected_vectors_v0.2.json"
EVALUATOR = ROOT / "src" / "evaluate_case.py"
PRECOMMITTED_SEED = "G_SMPTE_STANZA_APERTURE_v0.2::BLIND_ORDER::01"


def order_key(case: dict) -> str:
    material = f"{PRECOMMITTED_SEED}:{case['fixture_id']}".encode()
    return hashlib.sha256(material).hexdigest()


def main() -> int:
    fixture_doc = json.loads(CORES.read_text(encoding="utf-8"))
    if any("expected" in case for case in fixture_doc["fixtures"]):
        raise RuntimeError("ANSWER_LEAKAGE_IN_FIXTURE_CORE")

    observations: dict[str, dict] = {}
    for case in sorted(fixture_doc["fixtures"], key=order_key):
        request = {"surface": case["surface"], "input": case["input"]}
        completed = subprocess.run(
            [sys.executable, str(EVALUATOR)],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            check=True,
            cwd=ROOT,
        )
        observations[case["fixture_id"]] = json.loads(completed.stdout)

    # Oracle bytes are loaded only after every isolated evaluation has completed.
    expected = json.loads(ORACLE.read_text(encoding="utf-8"))["expected"]
    failures: list[dict] = []
    for fixture_id, vector in expected.items():
        observed = observations[fixture_id]
        actual = {
            "status": observed["status"],
            "all_triggered_failures": observed["all_triggered_failures"],
        }
        if actual != vector:
            failures.append(
                {"fixture_id": fixture_id, "expected": vector, "observed": actual}
            )

    report = {
        "battery_id": "G_SMPTE_STANZA_APERTURE_SYNTHETIC_BATTERY_v0.2",
        "fixtures": len(expected),
        "conformant": len(expected) - len(failures),
        "contradicted": len(failures),
        "result": "PASS_SYNTHETIC" if not failures else "CONTRADICTED",
        "standing": {
            "reference_validator_contract": "EVALUATED",
            "scientific": "UNEVALUATED",
            "physiological": "ZERO",
            "constitutional": "ZERO",
            "PP": "HARD_BLOCKED",
        },
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
