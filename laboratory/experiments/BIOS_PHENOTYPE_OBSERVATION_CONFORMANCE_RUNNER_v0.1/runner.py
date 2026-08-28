#!/usr/bin/env python3
"""BIOS Phenotype Observation Conformance Runner v0.1.

Constitutionally stupid runner: executes externally frozen fixtures, records actual
interface behavior, performs exact comparisons, and writes append-only results.
It has zero schema, interpretation, repair, phenotype, or scientific-claim authority.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

RUNNER_ID = "BIOS_PHENOTYPE_OBSERVATION_CONFORMANCE_RUNNER_v0.1"
EXPECTED_FIXTURE_IDS = [f"OC-{i:02d}" for i in range(1, 13)] + [f"PC-{i:02d}" for i in range(1, 13)]


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        f.flush()


def load_interface(module_path: Path):
    spec = importlib.util.spec_from_file_location("bios_observation_interface", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("INTERFACE_MODULE_LOAD_FAILURE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, "invoke_interface", None)
    if not callable(fn):
        raise RuntimeError("INTERFACE_ENTRYPOINT_MISSING: invoke_interface")
    return fn


def validate_manifest(manifest: Dict[str, Any]) -> None:
    if manifest.get("runner_id") != RUNNER_ID:
        raise ValueError("RUNNER_BINDING_MISMATCH")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 24:
        raise ValueError("FROZEN_FIXTURE_COUNT_MISMATCH")
    ids = [x.get("fixture_id") for x in fixtures]
    if ids != EXPECTED_FIXTURE_IDS:
        raise ValueError("FROZEN_FIXTURE_ID_OR_ORDER_MISMATCH")
    for fx in fixtures:
        if fx.get("fixture_class") not in {"NEGATIVE", "POSITIVE"}:
            raise ValueError(f"INVALID_FIXTURE_CLASS:{fx.get('fixture_id')}")
        if not isinstance(fx.get("expected"), dict):
            raise ValueError(f"EXPECTED_BLOCK_MISSING:{fx.get('fixture_id')}")
        required_expected = {"terminal_state", "reason_code", "firing_membrane", "C_GAMMA", "C_I", "C_A"}
        if set(fx["expected"].keys()) != required_expected:
            raise ValueError(f"EXPECTED_BLOCK_SCHEMA_MISMATCH:{fx.get('fixture_id')}")


def fixture_payload(fx: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "fixture_id": fx["fixture_id"],
        "fixture_class": fx["fixture_class"],
        "input_observation": fx["input_observation"],
        "instrument_state": fx["instrument_state"],
        "acquisition_context": fx["acquisition_context"],
        "expected": fx["expected"],
        "serialization_expectation": fx["serialization_expectation"],
    }


def execute_fixture(fx: Dict[str, Any], invoke_interface) -> Dict[str, Any]:
    verified_hash = sha256_bytes(canonical_bytes(fixture_payload(fx)))
    if verified_hash != fx["frozen_fixture_hash"]:
        return {
            "fixture_id": fx["fixture_id"],
            "verified_fixture_hash": verified_hash,
            "actual": None,
            "comparisons": None,
            "fixture_pass": "I",
            "diagnostic": "BATTERY_INVALID_FIXTURE_HASH",
        }

    actual = invoke_interface(
        input_observation=fx["input_observation"],
        instrument_state=fx["instrument_state"],
        acquisition_context=fx["acquisition_context"],
    )
    if not isinstance(actual, dict):
        raise RuntimeError(f"INTERFACE_RETURN_NOT_OBJECT:{fx['fixture_id']}")

    expected = fx["expected"]
    predicate_actual = {k: actual.get(k) for k in ("C_GAMMA", "C_I", "C_A")}
    predicate_expected = {k: expected[k] for k in ("C_GAMMA", "C_I", "C_A")}
    output_digest = sha256_bytes(canonical_bytes(actual.get("output")))

    comparisons = {
        "terminal_match": actual.get("terminal_state") == expected["terminal_state"],
        "reason_match": actual.get("reason_code") == expected["reason_code"],
        "jurisdiction_match": actual.get("firing_membrane") == expected["firing_membrane"],
        "predicate_vector_match": predicate_actual == predicate_expected,
        "serialization_match": output_digest == fx["serialization_expectation"],
    }

    # Noncompensatory. No rejection-only shortcut and no remapping.
    if fx["fixture_class"] == "NEGATIVE":
        fixture_pass = int(
            comparisons["terminal_match"]
            and comparisons["reason_match"]
            and comparisons["jurisdiction_match"]
            and comparisons["predicate_vector_match"]
            and comparisons["serialization_match"]
        )
    else:
        fixture_pass = int(
            actual.get("terminal_state") == expected["terminal_state"]
            and bool(actual.get("C_GAMMA")) == bool(expected["C_GAMMA"])
            and bool(actual.get("C_I")) == bool(expected["C_I"])
            and bool(actual.get("C_A")) == bool(expected["C_A"])
            and all(comparisons.values())
        )

    diagnostic = None
    if not comparisons["jurisdiction_match"]:
        diagnostic = "JURISDICTIONAL_DISCRIMINATION_FAILURE"

    return {
        "fixture_id": fx["fixture_id"],
        "verified_fixture_hash": verified_hash,
        "actual": {
            "terminal_state": actual.get("terminal_state"),
            "reason_code": actual.get("reason_code"),
            "firing_membrane": actual.get("firing_membrane"),
            "C_GAMMA": actual.get("C_GAMMA"),
            "C_I": actual.get("C_I"),
            "C_A": actual.get("C_A"),
            "output_digest": output_digest,
        },
        "comparisons": comparisons,
        "fixture_pass": fixture_pass,
        "diagnostic": diagnostic,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--gamma", required=True, type=Path)
    ap.add_argument("--interface", required=True, type=Path)
    ap.add_argument("--ledger", required=True, type=Path)
    args = ap.parse_args()

    manifest = load_json(args.manifest)
    try:
        validate_manifest(manifest)
    except Exception as e:
        append_jsonl(args.ledger, {"runner_id": RUNNER_ID, "terminal": "BATTERY_INVALID_FIXTURE", "diagnostic": str(e)})
        return 2

    runner_hash = sha256_file(Path(__file__))
    fixture_manifest_hash = sha256_file(args.manifest)
    gamma_hash_before = sha256_file(args.gamma)

    if manifest.get("gamma_sha256") != gamma_hash_before:
        append_jsonl(args.ledger, {
            "runner_id": RUNNER_ID,
            "runner_hash": runner_hash,
            "fixture_manifest_hash": fixture_manifest_hash,
            "gamma_hash_before": gamma_hash_before,
            "terminal": "BATTERY_INVALID_FIXTURE",
            "diagnostic": "H_GAMMA_BINDING_MISMATCH",
        })
        return 2

    invoke_interface = load_interface(args.interface)
    results: List[Dict[str, Any]] = []

    for fx in manifest["fixtures"]:
        try:
            result = execute_fixture(fx, invoke_interface)
        except Exception as e:
            result = {
                "fixture_id": fx["fixture_id"],
                "verified_fixture_hash": None,
                "actual": None,
                "comparisons": None,
                "fixture_pass": "I",
                "diagnostic": f"EXECUTION_ERROR:{type(e).__name__}:{e}",
            }
        results.append(result)
        append_jsonl(args.ledger, {"record_type": "FIXTURE_RESULT", "runner_id": RUNNER_ID, **result})

    gamma_hash_after = sha256_file(args.gamma)
    gamma_identity_preserved = gamma_hash_before == gamma_hash_after

    negative = [r for r in results if r["fixture_id"].startswith("OC-")]
    positive = [r for r in results if r["fixture_id"].startswith("PC-")]

    P_plus = int(all(r["fixture_pass"] == 1 for r in positive))
    P_minus = int(all(r["fixture_pass"] == 1 for r in negative))
    P_J = int(all(r.get("comparisons") and r["comparisons"]["jurisdiction_match"] for r in results))
    P_D = int(all(r.get("comparisons") and r["comparisons"]["serialization_match"] for r in results))
    P_GAMMA = int(gamma_identity_preserved)

    # Blinding is a manifest-bound predicate, not inferred by this runner.
    P_B = int(manifest.get("blinding_membrane_verified") is True)
    aggregate = [P_plus, P_minus, P_J, P_D, P_GAMMA, P_B]

    if not gamma_identity_preserved:
        terminal = "BATTERY_FAIL_CONFORMANCE"
        diagnostic = "APPARATUS_INTEGRITY_FAILURE_GAMMA_MUTATED"
    elif any(r["fixture_pass"] == "I" for r in results):
        terminal = "BATTERY_EXECUTION_INCOMPLETE"
        diagnostic = None
    elif aggregate == [1, 1, 1, 1, 1, 1]:
        terminal = "BATTERY_PASS"
        diagnostic = "BLIND_OBSERVATION_APPARATUS_DETERMINISTIC_CONFORMANCE_SUPPORTED"
    else:
        terminal = "BATTERY_FAIL_CONFORMANCE"
        diagnostic = None

    final = {
        "record_type": "RUN_TERMINAL",
        "runner_id": RUNNER_ID,
        "gamma_hash_before": gamma_hash_before,
        "runner_hash": runner_hash,
        "fixture_manifest_hash": fixture_manifest_hash,
        "aggregate": {
            "P_plus": P_plus,
            "P_minus": P_minus,
            "P_J": P_J,
            "P_D": P_D,
            "P_GAMMA": P_GAMMA,
            "P_B": P_B,
            "R_OC": aggregate,
        },
        "gamma_hash_after": gamma_hash_after,
        "gamma_identity_preserved": gamma_identity_preserved,
        "terminal": terminal,
        "diagnostic": diagnostic,
    }
    append_jsonl(args.ledger, final)
    print(json.dumps(final, indent=2, sort_keys=True))
    return 0 if terminal == "BATTERY_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
