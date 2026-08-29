from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

HARNESS_IDENTIFIER = "GGS_ISOLATED_CHAMBER_EXECUTION_HARNESS_v0.1"
TARGET_CHAMBER = "SG_01"
TARGET_COORDINATE = "r3"


class HarnessBoundaryError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExecutionAuthorization:
    chamber: str
    token: str | None
    scientific_execution: bool


def execute_sg01(specimen: Mapping[str, Any], authorization: ExecutionAuthorization) -> dict[str, Any]:
    if authorization.chamber != TARGET_CHAMBER:
        raise HarnessBoundaryError("cross-chamber execution prohibited")
    if not authorization.scientific_execution or authorization.token is None:
        raise HarnessBoundaryError("scientific execution authorization absent")
    if specimen.get("chamber") != "SG_01_SUCCESS_WITHOUT_CONFORMANCE":
        raise HarnessBoundaryError("unexpected SG-01 specimen identity")

    crossed_pair = specimen.get("crossed_pair")
    if not isinstance(crossed_pair, Mapping):
        raise HarnessBoundaryError("malformed SG-01 crossed pair")

    # Runtime residue only. No PASS/FAIL, r3, standing, interpretation, repair,
    # retry, continuation, or cross-chamber transition exists in this grammar.
    return {
        "harness_identifier": HARNESS_IDENTIFIER,
        "chamber": TARGET_CHAMBER,
        "runtime_completed": True,
        "observed_crossed_pair": dict(crossed_pair),
        "scientific_interpretation": None,
        "next_chamber": None,
    }
