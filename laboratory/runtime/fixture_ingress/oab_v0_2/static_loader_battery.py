from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from fixture_loader import FixtureIngressError, LoaderDisposition, load_fixture_bytes

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / "battery_manifest.json").read_text(encoding="utf-8"))
FIXTURE_ROOT = HERE.parents[2] / "fixtures" / "oab_v0_2"
VALID_RAW = (FIXTURE_ROOT / "OAB8.json").read_bytes()
VALID = json.loads(VALID_RAW.decode("utf-8"))


def enc(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":")).encode("utf-8")


def manifest_for_raw(fixture: dict, raw: bytes) -> dict:
    m = copy.deepcopy(MANIFEST)
    m["fixture_sha256"][fixture["fixture_id"]] = hashlib.sha256(raw).hexdigest()
    return m


def expect_reject(name: str, raw: bytes, *, manifest: dict = MANIFEST, needle: str) -> None:
    try:
        load_fixture_bytes(raw, source_path=f"{name}.json", manifest=manifest)
    except FixtureIngressError as exc:
        if needle not in str(exc):
            raise AssertionError(f"{name}: wrong rejection: {exc}") from exc
        print(f"TYPED_INGRESS_REJECTION_RECEIPT {name} {exc}")
        return
    raise AssertionError(f"{name}: expected rejection")


def run() -> None:
    f = copy.deepcopy(VALID); del f["invalidation_trigger"]; raw = enc(f)
    expect_reject("FL1_TRIGGER_REQUIRED", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:REQUIRED")

    f = copy.deepcopy(VALID); f["invalidation_trigger"] = "UNKNOWN_TRIGGER"; raw = enc(f)
    expect_reject("FL2_TRIGGER_ENUM_CLOSED", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:ENUM")

    f = copy.deepcopy(VALID); f["field_delta"]["prior_jurisdiction_hash"] = "abcd"; raw = enc(f)
    expect_reject("FL3_JURISDICTION_STATE_DIGEST_WIDTH", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:PATTERN")

    f = copy.deepcopy(VALID); f["expected_localization"]["jurisdictional_cone"] = ["0x0123456789abcdef"]; raw = enc(f)
    expect_reject("FL4_JURISDICTION_IDENTIFIER_WIDTH", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:PATTERN")

    f = copy.deepcopy(VALID); f["field_delta"]["synthetic_authority"] = "ADMITTED"; raw = enc(f)
    expect_reject("FL5_FIELD_DELTA_CLOSED", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:ADDITIONALPROPERTIES")

    f = copy.deepcopy(VALID); del f["field_delta"]["prior_provenance_hash"]; raw = enc(f)
    expect_reject("FL6_PROVENANCE_REQUIRED", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:REQUIRED")

    m = copy.deepcopy(MANIFEST); m["prior_manifest_id"] = "OAB_FIXTURE_INGRESS_MANIFEST_v0.0"
    expect_reject("FL7_ANCESTOR_MANIFEST_DRIFT", VALID_RAW, manifest=m, needle="PRIOR_MANIFEST_ID_MISMATCH")

    m = copy.deepcopy(MANIFEST); m["prior_contract_id"] = "OAB_FIXTURE_LOADER_CONTRACT_v0.0"
    expect_reject("FL8_ANCESTOR_CONTRACT_DRIFT", VALID_RAW, manifest=m, needle="PRIOR_CONTRACT_ID_MISMATCH")

    expect_reject("FL9_MANIFEST_BYTE_MISMATCH", VALID_RAW + b" ", needle="FIXTURE_DIGEST_MISMATCH")

    for i in range(1, 9):
        p = FIXTURE_ROOT / f"OAB{i}.json"
        result = load_fixture_bytes(p.read_bytes(), source_path=p.name, manifest=MANIFEST)
        assert result.disposition is LoaderDisposition.LOADED
        print(f"LOADED_FIXTURE_RECEIPT OAB{i} {result.sha256}")


if __name__ == "__main__":
    run()
