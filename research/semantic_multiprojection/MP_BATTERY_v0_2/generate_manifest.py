#!/usr/bin/env python3
"""Generate MP_BATTERY_v0_2/SHA256_MANIFEST.json from local payload bytes.

Generation creates no qualification standing. The historical v0_1 manifest is
neither read nor inherited.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT_ID = "MP_BATTERY_v0_2"
SOURCE_COMMIT = "e430d9235e10f2023957cb19315c7531def4c1ee"
PAYLOAD_PATHS = (
    "README.md",
    "contracts/BLIND_EXTRACTION_ADJUDICATION_CONTRACT.md",
    "contracts/PRESERVATION_CONTRACTS.json",
    "registry/FROZEN_REGISTRY.json",
    "specimens/MP0_COHERENT_FALSE_SIBLINGS.json",
    "specimens/MP1_IDENTITY_DRIFT.json",
    "specimens/MP2_MEANING_INFLATION.json",
    "specimens/MP3_AUTHORITY_INFLATION.json",
    "specimens/MP4_PROVENANCE_SEVERANCE.json",
    "specimens/MP5_JURISDICTION_SUBSTITUTION.json",
    "specimens/MP6_NONCONSTITUTIVE_LOSS.json",
    "specimens/S0.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path) -> dict:
    entries = {relative: sha256_file(root / relative) for relative in PAYLOAD_PATHS}
    return {
        "algorithm": "SHA-256",
        "artifact_id": ARTIFACT_ID,
        "entries": entries,
        "identity_authority": "PROSPECTIVE_ONLY",
        "payload_count": len(entries),
        "source_commit": SOURCE_COMMIT,
        "standing": "MATERIALIZED_UNQUALIFIED",
    }


def main() -> None:
    root = Path(__file__).resolve().parent
    output = root / "SHA256_MANIFEST.json"
    output.write_text(
        json.dumps(build_manifest(root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
