from pathlib import Path
import pytest

from src.evaluator_firewall import EvaluatorFirewall, FirewallDenied


def test_firewall_denies_repair_and_reconstruction(tmp_path):
    fw = EvaluatorFirewall((tmp_path / "allowed",))
    for operation in ["REPAIR", "INFER_MISSING", "RECONSTRUCT_PROVENANCE", "PROMOTE"]:
        with pytest.raises(FirewallDenied):
            fw.authorize_operation(operation)


def test_firewall_denies_permutation_root(tmp_path):
    allowed = tmp_path / "payloads"
    secret = tmp_path / "reconciliation" / "permutation.json"
    fw = EvaluatorFirewall((allowed,))
    with pytest.raises(FirewallDenied):
        fw.authorize_read(secret)


def test_firewall_rejects_verdict_leakage(tmp_path):
    fw = EvaluatorFirewall((tmp_path,))
    with pytest.raises(FirewallDenied):
        fw.validate_payload({"opaque_trial_id":"X_001","expected_outcome":"PASS"})
