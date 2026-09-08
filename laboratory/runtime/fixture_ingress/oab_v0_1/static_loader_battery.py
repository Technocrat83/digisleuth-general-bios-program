from __future__ import annotations

import copy
import json

from fixture_loader import FixtureIngressError, LoaderDisposition, load_fixture_bytes


MANIFEST = {
    "manifest_id": "OAB_FIXTURE_INGRESS_MANIFEST_v0.1",
    "battery_id": "OMEGA_ORIENTATION_ADVERSARIAL_BATTERY_01",
    "fixture_schema_version": "OAB_FIXTURE_SHAPE_v0.1",
    "loader_contract_version": "OAB_FIXTURE_LOADER_v0.1",
    "semantic_bindings": {
        "delta_encoding_rule": "ORIENTATION_DELTA_CANONICAL_ENCODING_v0.1",
        "localization_rule": "JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1",
        "monitor_rule": "ORIENTATION_INVALIDATION_MONITOR_v0.1",
        "replay_rule": "ORIENTATION_REPLAY_VALIDATOR_v0.1",
    },
    "fixture_ids": [f"OAB{i}" for i in range(1, 9)],
    "authority": {"interpretation": 0, "repair": 0, "admission": 0, "execution": 0},
}


VALID = {
    "fixture_id": "OAB8",
    "single_fault": True,
    "field_delta": {
        "object_id": "OAB_OBJECT_001",
        "delta_id": "OAB8",
        "prior_orientation_hash": "ORIENT_HASH_001",
        "prior_graph_hash": "GRAPH_A",
        "current_graph_hash": "GRAPH_A",
        "prior_jurisdiction_hash": "JUR_A",
        "current_jurisdiction_hash": "JUR_A",
        "prior_provenance_hash": "PROV_A",
        "current_provenance_hash": "PROV_A",
        "prior_placement_hash": "PLACE_A",
        "current_placement_hash": "PLACE_A",
        "prior_state_hash": "STATE_A",
        "current_state_hash": "STATE_A",
        "prior_boundary_hash": "BOUND_A",
        "current_boundary_hash": "BOUND_A",
        "prior_epoch": "EPOCH_001",
        "current_epoch": "EPOCH_001",
        "adjacency_changed": False,
        "authority_use_attempted": False,
        "evidence_complete": True,
    },
    "expected_localization": {
        "standing": "NO_MATERIAL_INTERSECTION",
        "affected_surfaces": [],
        "causal_cone": [],
        "jurisdictional_cone": [],
    },
    "expected_monitor": {
        "lifecycle": "CURRENT",
        "historical_orientation_preserved": True,
        "epistemic_standing_changed": False,
        "repair_attempted": False,
        "auto_reorientation": False,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
    },
}


def enc(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def expect_reject(name: str, fixture: dict, *, manifest: dict = MANIFEST, needle: str) -> None:
    try:
        load_fixture_bytes(enc(fixture), source_path=f"{name}.json", manifest=manifest)
    except FixtureIngressError as exc:
        if needle not in str(exc):
            raise AssertionError(f"{name}: wrong rejection: {exc}") from exc
        print(f"PASS {name:34} REJECTED {exc}")
        return
    raise AssertionError(f"{name}: expected rejection")


def run() -> None:
    # FL1 — missing required field
    f = copy.deepcopy(VALID)
    del f["field_delta"]["object_id"]
    expect_reject("FL1_MISSING_REQUIRED_FIELD", f, needle="MISSING_REQUIRED_FIELD")

    # FL2 — frozen rule identity drift
    m = copy.deepcopy(MANIFEST)
    m["semantic_bindings"]["localization_rule"] = "JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v9.9"
    expect_reject("FL2_RULE_IDENTITY_MISMATCH", VALID, manifest=m, needle="RULE_IDENTITY_MISMATCH")

    # FL3 — structural identity divergence represented by mismatched delta id
    f = copy.deepcopy(VALID)
    f["field_delta"]["delta_id"] = "OAB7"
    expect_reject("FL3_OBJECT_BINDING_DIVERGENCE", f, needle="DELTA_ID_MISMATCH")

    # FL4 — 128-bit jurisdiction width violation where a jurisdiction member is represented as hex
    f = copy.deepcopy(VALID)
    f["field_delta"]["current_jurisdiction_member"] = "0x0123456789abcdef"
    expect_reject("FL4_JURISDICTION_WIDTH", f, needle="JURISDICTION_WIDTH_INVALID")

    # FL5 — unknown fixture type
    f = copy.deepcopy(VALID)
    f["fixture_id"] = "OAB9"
    f["field_delta"]["delta_id"] = "OAB9"
    expect_reject("FL5_UNKNOWN_FIXTURE_TYPE", f, needle="UNKNOWN_FIXTURE_TYPE")

    # FL6 — byte mutation after an expected digest is frozen
    raw = enc(VALID)
    try:
        load_fixture_bytes(raw + b" ", source_path="FL6.json", manifest=MANIFEST, expected_sha256="0" * 64)
    except FixtureIngressError as exc:
        assert "FIXTURE_DIGEST_MISMATCH" in str(exc)
        print(f"PASS {'FL6_DIGEST_MISMATCH':34} REJECTED {exc}")
    else:
        raise AssertionError("FL6_DIGEST_MISMATCH: expected rejection")

    # FL7 — unresolved semantic input remains an ingress failure, never inferred.
    f = copy.deepcopy(VALID)
    del f["expected_localization"]["standing"]
    expect_reject("FL7_UNRESOLVED_OPTIONALITY", f, needle="MISSING_REQUIRED_FIELD")

    # FL8 — affirmative valid-control ingress.
    result = load_fixture_bytes(enc(VALID), source_path="OAB8.json", manifest=MANIFEST)
    assert result.disposition is LoaderDisposition.LOADED
    print(f"PASS {'FL8_VALID_CONTROL':34} LOADED {result.sha256}")


if __name__ == "__main__":
    run()
