"""Harness controller. Battery execution requires an external authorization token."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .blind_serializer import rules_hash, serialize_fixture
from .continuity_field_interface import OneShotOperator
from .hidden_fixture_store import HiddenFixtureStore
from .isolated_adjudicator import ChamberVerdict, adjudicate
from .witness_authentication_stub import authenticate_witness


class ExecutionBlocked(PermissionError):
    pass


@dataclass(frozen=True)
class ExecutionAuthorization:
    apparatus_id: str
    battery_id: str
    authorization_id: str
    authorized: bool = False


class CrossFixtureSessionController:
    APPARATUS_ID = "CONTINUITY_FIELD_BLIND_FIXTURE_APPARATUS_v0.1"
    BATTERY_ID = "CC_F01_THROUGH_CC_F12"

    def __init__(self, store: HiddenFixtureStore, operator: OneShotOperator) -> None:
        self._store = store
        self._operator = operator

    @staticmethod
    def order_commitment(fixture_ids: Sequence[str], seed: bytes) -> str:
        payload = b"\x00".join([seed, *(item.encode("ascii") for item in fixture_ids)])
        return hashlib.sha256(payload).hexdigest()

    def run_battery(
        self,
        fixture_ids: Sequence[str],
        *,
        seed: bytes,
        authorization: ExecutionAuthorization,
    ) -> Mapping[str, Any]:
        if not authorization.authorized:
            raise ExecutionBlocked("fixture execution is not authorized")
        if (authorization.apparatus_id, authorization.battery_id) != (self.APPARATUS_ID, self.BATTERY_ID):
            raise ExecutionBlocked("authorization scope mismatch")
        expected_ids = {f"CC_F{i:02d}" for i in range(1, 13)}
        if set(fixture_ids) != expected_ids or len(fixture_ids) != 12:
            raise ValueError("the frozen battery requires exactly CC_F01 through CC_F12")

        randomized = list(fixture_ids)
        random.Random(seed).shuffle(randomized)
        commitment = self.order_commitment(randomized, seed)
        chamber_rows = []
        verdicts: list[ChamberVerdict] = []

        for fixture_id in randomized:
            fixture = self._store.load(fixture_id)
            auth = authenticate_witness(fixture["witness_artifact"])
            x_i = serialize_fixture(fixture, auth)
            y_i = self._operator.evaluate(x_i)
            verdict = adjudicate(y_i, fixture["predicate_bundle"])
            verdicts.append(verdict)
            chamber_rows.append({
                "fixture_id": fixture_id,
                "residue_sha256": verdict.residue_sha256,
                "predicate_bundle_id": verdict.predicate_bundle_id,
                "predicate_results": [item.satisfied for item in verdict.predicate_results],
                "pass": verdict.passed,
            })

        passed = sum(item.passed for item in verdicts)
        return {
            "apparatus_id": self.APPARATUS_ID,
            "battery_id": self.BATTERY_ID,
            "serializer_commitment": rules_hash(),
            "order_commitment": commitment,
            "chambers": chamber_rows,
            "aggregate": {
                "pass": passed == 12,
                "passed": passed,
                "total": 12,
                "standing_ceiling": "BOUNDED_BLIND_HARNESS_CONFORMANCE_ONLY",
            },
        }
