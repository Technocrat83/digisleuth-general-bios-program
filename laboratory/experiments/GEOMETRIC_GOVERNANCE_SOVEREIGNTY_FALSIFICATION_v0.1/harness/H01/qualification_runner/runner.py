from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RUNNER_IDENTIFIER = "GGS_HARNESS_QUALIFICATION_RUNNER_v0.1"
ALLOWED_OPERATION = "QUALIFY_H01"
DOMAIN_SEPARATOR = b"GGS:H01:v0.1\x00"


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_harness_manifest(harness_root: Path) -> bytes:
    members = []
    for path in sorted((p for p in harness_root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(harness_root).as_posix().encode("utf-8")):
        rel = path.relative_to(harness_root).as_posix()
        data = path.read_bytes()
        members.append({"relative_path": rel, "byte_length": len(data), "sha256": _sha256_bytes(data)})
    return json.dumps({"members": members}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def qualify_h01(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("operation") != ALLOWED_OPERATION:
        raise ValueError("unsupported operation")
    auth = request.get("authorization", {})
    if auth != {
        "qualification": True,
        "scientific_execution": False,
        "execution_token": None,
        "adjudication": False,
        "repair": False,
        "continuation": False,
    }:
        raise ValueError("authorization surface nonconformant")

    harness = request.get("harness", {})
    harness_root = Path(str(harness.get("harness_root", "")))
    manifest_path = Path(str(harness.get("manifest_path", "")))
    expected_digest = harness.get("expected_digest")
    if not harness_root.is_dir() or not manifest_path.is_file() or not isinstance(expected_digest, str):
        raise ValueError("H01 identity binding incomplete")

    canonical_manifest = _canonical_harness_manifest(harness_root)
    if manifest_path.read_bytes() != canonical_manifest:
        raise ValueError("canonical manifest bytes do not match H01 bytes")
    actual_harness_digest = _sha256_bytes(DOMAIN_SEPARATOR + canonical_manifest)
    if actual_harness_digest != expected_digest:
        raise ValueError("H01 digest mismatch")

    q = {f"Q{i:02d}": "INCOMPLETE" for i in range(1, 11)}
    lineage = request.get("lineage", {})
    target = request.get("target", {})
    initial = request.get("initial_state", {})

    q["Q01"] = "CONFORMANT" if lineage.get("parent_commit") == "3cede3afb93bac6b7cb12bf9f23bde3c63b0780a" else "NONCONFORMANT"
    q["Q02"] = "CONFORMANT" if lineage.get("H_GGS") == "4e54099c9acf017e62e4c8015c907a39ae68a5635877f34cbe488f761a090576" else "NONCONFORMANT"
    q["Q03"] = "CONFORMANT" if lineage.get("H_map") == "6acc5fe97466b857285c9978ad35bd5d339239525ed7428a9bfd2d5643a6851c" else "NONCONFORMANT"
    q["Q04"] = "CONFORMANT" if target.get("chamber") == "SG_01" and target.get("coordinate") == "r3" else "NONCONFORMANT"

    specimen_root = Path(str(target.get("specimen_root", "")))
    specimen_file = specimen_root / "SPECIMEN.json"
    expected_specimen = target.get("expected_specimen_digest")
    if specimen_file.is_file() and isinstance(expected_specimen, str):
        q["Q05"] = "CONFORMANT" if _sha256(specimen_file) == expected_specimen else "NONCONFORMANT"

    q["Q06"] = "CONFORMANT" if initial.get("R_GGS") == ["U"] * 8 and initial.get("E_01_present") is False and initial.get("scientific_execution_present") is False else "NONCONFORMANT"

    harness_file = harness_root / "harness.py"
    contract_file = harness_root / "HARNESS_CONTRACT.json"
    if harness_file.is_file() and contract_file.is_file():
        source = harness_file.read_text(encoding="utf-8")
        contract = json.loads(contract_file.read_text(encoding="utf-8"))
        q["Q07"] = "CONFORMANT" if "ASSIGN_r3" in contract.get("prohibited", []) and "def adjudicat" not in source.lower() else "NONCONFORMANT"
        q["Q08"] = "CONFORMANT" if "ACCESS_SG02_SG07" in contract.get("prohibited", []) and all(f"SG_0{i}" not in source for i in range(2, 8)) else "NONCONFORMANT"
        q["Q09"] = "CONFORMANT" if "AUTO_CONTINUE" in contract.get("prohibited", []) and '"next_chamber": None' in source else "NONCONFORMANT"
        q["Q10"] = "CONFORMANT" if "REPAIR" in contract.get("prohibited", []) and "RETRY" in contract.get("prohibited", []) else "NONCONFORMANT"

    if any(v == "NONCONFORMANT" for v in q.values()):
        standing = "UNQUALIFIED"
    elif any(v == "INCOMPLETE" for v in q.values()):
        standing = "QUALIFICATION_INCOMPLETE"
    else:
        standing = "SG01_EXECUTION_ELIGIBLE"

    return {
        "residue_schema": "GGS_H01_QUALIFICATION_RESIDUE_v0.1",
        "runner": RUNNER_IDENTIFIER,
        "harness_identifier": harness.get("identifier"),
        "harness_digest": actual_harness_digest,
        "qualification": q,
        "aggregate_scoring": "PROHIBITED",
        "scientific_semantics": "NONE",
        "standing": standing,
        "scientific_execution": False,
        "execution_token": None,
        "E_01": "UNMINTED",
        "r3": "U",
        "R_GGS": ["U"] * 8,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ggs_harness_qualification")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("qualify-h01")
    p.add_argument("--request", required=True)
    args = parser.parse_args(argv)

    request_path = Path(args.request)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    residue = qualify_h01(request)
    output = Path(request["output"]["residue_path"])
    if output.exists():
        raise FileExistsError("qualification residue path must be new and immutable")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(residue, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0
