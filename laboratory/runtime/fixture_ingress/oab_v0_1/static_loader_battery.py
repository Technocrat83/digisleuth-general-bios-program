from __future__ import annotations

import copy
import json
from pathlib import Path

from fixture_loader import FixtureIngressError, LoaderDisposition, load_fixture_bytes

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / "battery_manifest.json").read_text(encoding="utf-8"))
VALID_RAW = (HERE.parents[2] / "fixtures" / "oab_v0_1" / "OAB8.json").read_bytes()
VALID = json.loads(VALID_RAW.decode("utf-8"))


def enc(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def manifest_for_raw(fixture: dict, raw: bytes) -> dict:
    import hashlib
    m = copy.deepcopy(MANIFEST)
    m["fixture_sha256"][fixture["fixture_id"]] = hashlib.sha256(raw).hexdigest()
    return m


def expect_reject(name: str, raw: bytes, *, manifest: dict = MANIFEST, needle: str) -> None:
    try:
        load_fixture_bytes(raw, source_path=f"{name}.json", manifest=manifest)
    except FixtureIngressError as exc:
        if needle not in str(exc):
            raise AssertionError(f"{name}: wrong rejection: {exc}") from exc
        print(f"PASS {name:38} REJECTED {exc}")
        return
    raise AssertionError(f"{name}: expected rejection")


def run() -> None:
    f = copy.deepcopy(VALID)
    del f["field_delta"]["prior_provenance_hash"]
    raw = enc(f)
    expect_reject("FL1_PROVENANCE_STRIP", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:REQUIRED")

    f = copy.deepcopy(VALID)
    f["field_delta"]["synthetic_authority"] = "ADMITTED"
    raw = enc(f)
    expect_reject("FL2_FIELD_DELTA_OVERFLOW", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:ADDITIONALPROPERTIES")

    f = copy.deepcopy(VALID)
    f["field_delta"]["adjacency_changed"] = "false"
    raw = enc(f)
    expect_reject("FL3_PRIMITIVE_TYPE_COERCION", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:TYPE")

    f = copy.deepcopy(VALID)
    f["expected_localization"]["affected_surfaces"] = ["MAKE_ME_ADMIN"]
    raw = enc(f)
    expect_reject("FL4_UNMAPPED_AFFECTED_SURFACE", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:ENUM")

    f = copy.deepcopy(VALID)
    f["expected_localization"]["jurisdictional_cone"] = ["0x0123456789abcdef"]
    raw = enc(f)
    expect_reject("FL5_JURISDICTION_128BIT_WIDTH", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:PATTERN")

    f = copy.deepcopy(VALID)
    f["expected_monitor"]["lifecycle"] = "UNKNOWN"
    raw = enc(f)
    expect_reject("FL6_UNMAPPED_LIFECYCLE", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:ENUM")

    f = copy.deepcopy(VALID)
    f["expected_monitor"]["authority_effect"] = "ESCALATE"
    raw = enc(f)
    expect_reject("FL7_AUTHORITY_EFFECT_CLOSED", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:CONST")

    f = copy.deepcopy(VALID)
    f["expected_monitor"]["execution_effect"] = "EXECUTE"
    raw = enc(f)
    expect_reject("FL8_EXECUTION_EFFECT_CLOSED", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:ENUM")

    f = copy.deepcopy(VALID)
    f["expected_monitor"]["historical_orientation_preserved"] = False
    raw = enc(f)
    expect_reject("FL9_HISTORY_REWRITE", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:CONST")

    f = copy.deepcopy(VALID)
    f["expected_monitor"]["epistemic_standing_changed"] = True
    raw = enc(f)
    expect_reject("FL10_EPISTEMIC_MUTATION", raw, manifest=manifest_for_raw(f, raw), needle="SCHEMA_REJECT:CONST")

    dup = VALID_RAW.replace(b'"fixture_id":"OAB8"', b'"fixture_id":"OAB8","fixture_id":"OAB8"', 1)
    expect_reject("FL11_DUPLICATE_JSON_KEY", dup, needle="DUPLICATE_JSON_KEY")

    m = copy.deepcopy(MANIFEST)
    m["loader_contract_version"] = "OAB_FIXTURE_LOADER_v9.9"
    expect_reject("FL12_MANIFEST_VERSION_DRIFT", VALID_RAW, manifest=m, needle="LOADER_CONTRACT_VERSION_MISMATCH")

    m = copy.deepcopy(MANIFEST)
    m["fixture_ids"].insert(0, "OAB1")
    expect_reject("FL13_MANIFEST_DUPLICATE_ID", VALID_RAW, manifest=m, needle="FIXTURE_ID_SEQUENCE_MISMATCH")

    m = copy.deepcopy(MANIFEST)
    del m["fixture_sha256"]["OAB8"]
    expect_reject("FL14_MANIFEST_DIGEST_ABSENCE", VALID_RAW, manifest=m, needle="FIXTURE_DIGEST_SET_MISMATCH")

    m = copy.deepcopy(MANIFEST)
    m["semantic_bindings"]["localization_rule"] = "JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v9.9"
    expect_reject("FL15_RULE_IDENTITY_DRIFT", VALID_RAW, manifest=m, needle="RULE_IDENTITY_MISMATCH")

    expect_reject("FL16_MANIFEST_BYTE_MISMATCH", VALID_RAW + b" ", needle="FIXTURE_DIGEST_MISMATCH")

    f = copy.deepcopy(VALID)
    f["field_delta"]["delta_id"] = "OAB7"
    raw = enc(f)
    expect_reject("FL17_DELTA_ID_DIVERGENCE", raw, manifest=manifest_for_raw(f, raw), needle="DELTA_ID_MISMATCH")

    fixture_root = HERE.parents[2] / "fixtures" / "oab_v0_1"
    for i in range(1, 9):
        p = fixture_root / f"OAB{i}.json"
        result = load_fixture_bytes(p.read_bytes(), source_path=p.name, manifest=MANIFEST)
        assert result.disposition is LoaderDisposition.LOADED
        print(f"PASS {'FLP_'+str(i)+'_CANONICAL_OAB':38} LOADED {result.sha256}")


if __name__ == "__main__":
    run()
