from copy import deepcopy
from checker import Disposition, ValidationPolicy, verify_warrant

POLICY = ValidationPolicy(
    allowed_rule_ids=["RULE_TRANSITIVE_BOUND_v1"],
    allowed_rule_versions={"RULE_TRANSITIVE_BOUND_v1": ["1.0.0"]},
    known_input_ids=["A", "B"],
    valid_source_cones={"SC_AB": ["A", "B"]},
    allowed_scopes=["A_TO_C_DERIVATION_ONLY"],
    allowed_jurisdictions=["J_GEP01"],
    allowed_epochs=["EPOCH_001"],
    authorized_issuers=["ISSUER_GEP_WD_01"],
)

BASE = {
    "warrant_id": "WD_CANONICAL_TRANSITIVE_v1",
    "rule_id": "RULE_TRANSITIVE_BOUND_v1",
    "rule_version": "1.0.0",
    "input_ids": ["A", "B"],
    "source_cone_id": "SC_AB",
    "assumptions": ["A_TO_B_SUPPORTED", "B_TO_C_SUPPORTED"],
    "scope": "A_TO_C_DERIVATION_ONLY",
    "jurisdiction": "J_GEP01",
    "epoch": "EPOCH_001",
    "issuer_id": "ISSUER_GEP_WD_01",
    "provenance": {
        "artifact_id": "ART_WD_001",
        "content_hash": "sha256:example",
        "replay_ref": "git:example"
    }
}


def case(name, mutate, expected, expected_violation=None):
    warrant = deepcopy(BASE)
    mutate(warrant)
    result = verify_warrant(warrant, POLICY)
    assert result.result == expected, (name, result.to_dict())
    assert result.repair_authority is False
    assert result.admission_authority is False
    assert result.epistemic_standing_effect == "NONE"
    if expected_violation:
        assert expected_violation in result.violations, (name, result.violations)
    print(f"PASS {name}: {result.result.value}")


if __name__ == "__main__":
    case("VALID_CONTROL", lambda w: None, Disposition.VALID)
    case("MISSING_WARRANT_DATA_IS_UNRESOLVED", lambda w: w.pop("issuer_id"), Disposition.UNRESOLVED, "ISSUER_MISSING")
    case("INVALID_SCOPE_IS_NOT_REPAIRED", lambda w: w.__setitem__("scope", "GLOBAL_ADMISSION"), Disposition.INVALID, "SCOPE_EXCEEDED")
    case("VALID_SOURCE_CONE_DOES_NOT_VALIDATE_BAD_WARRANT", lambda w: w.__setitem__("issuer_id", "UNAUTHORIZED_ISSUER"), Disposition.INVALID, "ISSUER_UNAUTHORIZED")
    case("SOURCE_CONE_MISMATCH_INVALID", lambda w: w.__setitem__("input_ids", ["B", "A"]), Disposition.INVALID, "SOURCE_CONE_BINDING_MISMATCH")
    case("UNKNOWN_SOURCE_CONE_UNRESOLVED_NOT_INVALID", lambda w: w.__setitem__("source_cone_id", "SC_UNKNOWN"), Disposition.UNRESOLVED, "SOURCE_CONE_AUTHENTICATION_UNRESOLVED")
    case("UNKNOWN_INPUT_AUTH_UNRESOLVED", lambda w: w.__setitem__("input_ids", ["A", "Z"]), Disposition.UNRESOLVED, "INPUT_ID_AUTHENTICATION_UNRESOLVED")
    case("MISSING_PROVENANCE_UNRESOLVED", lambda w: w["provenance"].pop("replay_ref"), Disposition.UNRESOLVED, "PROVENANCE_FIELD_MISSING:replay_ref")
    case("UNAUTHORIZED_RULE_INVALID", lambda w: w.__setitem__("rule_id", "RULE_FORBIDDEN"), Disposition.INVALID, "RULE_ID_UNAUTHORIZED")

    valid = verify_warrant(BASE, POLICY)
    assert valid.result == Disposition.VALID
    assert valid.admission_authority is False
    print("PASS VALID_WD_DOES_NOT_ADMIT_RELATION")
