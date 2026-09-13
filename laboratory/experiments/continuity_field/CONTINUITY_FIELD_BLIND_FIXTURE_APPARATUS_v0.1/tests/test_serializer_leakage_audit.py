"""Static and synthetic leakage checks. These tests do not load or execute CC_F fixtures."""

import json
import unittest

from apparatus.blind_serializer import PERMITTED_FIELDS, serialize_fixture
from apparatus.witness_authentication_stub import AuthenticationState


class SerializerLeakageAudit(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = {
            "fixture_id": "SYNTHETIC_NON_BATTERY_PROBE",
            "chamber_id": "SECRET_CHAMBER",
            "attack_family": "SECRET_ATTACK",
            "expected_verdict": "SECRET_EXPECTATION",
            "operator_input": {
                "O_t": {"state": 1},
                "O_t_plus_1_candidate": {"state": 2},
                "rho_t": {"transition": "probe"},
                "Q_t": {"causal_missingness": ["edge"], "tested_structural_relations": ["a->b"]},
            },
        }

    def test_output_surface_is_exact(self) -> None:
        encoded = serialize_fixture(self.fixture, AuthenticationState.AUTH_UNRESOLVED)
        value = json.loads(encoded)
        self.assertEqual(set(value), set(PERMITTED_FIELDS))

    def test_evaluation_metadata_is_absent(self) -> None:
        encoded = serialize_fixture(self.fixture, AuthenticationState.AUTH_UNRESOLVED)
        for secret in (b"SYNTHETIC_NON_BATTERY_PROBE", b"SECRET_CHAMBER", b"SECRET_ATTACK", b"SECRET_EXPECTATION"):
            self.assertNotIn(secret, encoded)

    def test_serializer_is_deterministic(self) -> None:
        left = serialize_fixture(self.fixture, AuthenticationState.AUTH_UNRESOLVED)
        right = serialize_fixture(dict(reversed(list(self.fixture.items()))), AuthenticationState.AUTH_UNRESOLVED)
        self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
