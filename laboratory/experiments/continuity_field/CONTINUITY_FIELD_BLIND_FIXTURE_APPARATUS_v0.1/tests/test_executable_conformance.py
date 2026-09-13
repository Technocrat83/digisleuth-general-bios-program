"""Non-battery component conformance tests; no CC_F fixture is loaded or executed."""

import hashlib
import json
import unittest

from apparatus.blind_serializer import canonical_json
from apparatus.conjunctive_predicate_engine import PredicateResult, conjunctive_pass
from apparatus.cross_fixture_session_controller import (
    CrossFixtureSessionController,
    ExecutionAuthorization,
    ExecutionBlocked,
)
from apparatus.isolated_adjudicator import adjudicate
from apparatus.witness_authentication_stub import AuthenticationState, authenticate_witness


class ExecutableConformanceTests(unittest.TestCase):
    def test_witness_authentication_is_typed(self) -> None:
        payload = "synthetic witness"
        valid = {"payload": payload, "declared_sha256": hashlib.sha256(payload.encode()).hexdigest()}
        self.assertEqual(authenticate_witness(valid), AuthenticationState.AUTH_VALID)
        self.assertEqual(authenticate_witness({"payload": payload, "declared_sha256": "0" * 64}), AuthenticationState.AUTH_INVALID)
        self.assertEqual(authenticate_witness({"payload": payload, "declared_sha256": None}), AuthenticationState.AUTH_UNRESOLVED)

    def test_conjunction_is_non_compensatory(self) -> None:
        self.assertTrue(conjunctive_pass([PredicateResult("p1", True), PredicateResult("p2", True)]))
        self.assertFalse(conjunctive_pass([PredicateResult("p1", True), PredicateResult("p2", False)]))

    def test_adjudicator_honors_precommitted_bundle(self) -> None:
        material = {"bundle_id": "SYNTHETIC", "predicates": [{"predicate_id": "p1", "path": "/standing", "operation": "equals", "expected": "SUPPORTED"}]}
        bundle = dict(material, bundle_hash=hashlib.sha256(canonical_json(material)).hexdigest())
        residue = json.dumps({"standing": "SUPPORTED"}, sort_keys=True, separators=(",", ":")).encode()
        self.assertTrue(adjudicate(residue, bundle).passed)

    def test_battery_execution_defaults_to_blocked(self) -> None:
        controller = object.__new__(CrossFixtureSessionController)
        authorization = ExecutionAuthorization(
            apparatus_id=controller.APPARATUS_ID,
            battery_id=controller.BATTERY_ID,
            authorization_id="ABSENT",
            serializer_commitment="",
            order_commitment="",
            authorized=False,
        )
        with self.assertRaises(ExecutionBlocked):
            controller.run_battery([], seed=b"hidden", authorization=authorization)


if __name__ == "__main__":
    unittest.main()
