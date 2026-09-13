"""Deterministic N=2 synthetic verifier. It does not access or execute CC_F fixtures."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Iterable, Sequence

BASIS_BOUNDED = (
    "s",
    "q",
    "g_1",
    "g_2",
    "kappa_1",
    "kappa_2",
    "L_v1",
    "L_v2",
    "p_mask",
    "C_12",
)
BASIS_PERIODIC = (
    "theta_1",
    "theta_2",
    "phi_11",
    "phi_12",
    "phi_13",
    "phi_21",
    "phi_22",
    "phi_23",
)
PERIODS = (2.0 * math.pi,) * len(BASIS_PERIODIC)


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def torus_distance(left: Sequence[float], right: Sequence[float]) -> float:
    return math.sqrt(sum(wrap(a - b) ** 2 for a, b in zip(left, right, strict=True)))


def metric() -> list[list[float]]:
    size = len(BASIS_BOUNDED) + len(BASIS_PERIODIC)
    result = [[0.0 for _ in range(size)] for _ in range(size)]
    bounded_weights = (4.0, 5.0, 2.0, 2.0, 1.0, 1.0, 3.0, 3.0, 2.0, 2.0)
    for index, weight in enumerate(bounded_weights):
        result[index][index] = weight

    offset = len(BASIS_BOUNDED)
    for index in range(len(BASIS_PERIODIC)):
        result[offset + index][offset + index] = 2.0 if index < 2 else 1.5

    result[offset][offset + 1] = result[offset + 1][offset] = -0.5
    for left, right in ((2, 5), (3, 6), (4, 7)):
        result[offset + left][offset + right] = -0.25
        result[offset + right][offset + left] = -0.25
    return result


def cholesky(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    size = len(matrix)
    lower = [[0.0 for _ in range(size)] for _ in range(size)]
    for row in range(size):
        for column in range(row + 1):
            residual = matrix[row][column] - sum(lower[row][k] * lower[column][k] for k in range(column))
            if row == column:
                if residual <= 1e-12:
                    raise ValueError("metric is not positive definite")
                lower[row][column] = math.sqrt(residual)
            else:
                lower[row][column] = residual / lower[column][column]
    return lower


def quadratic_cost(matrix: Sequence[Sequence[float]], velocity: Sequence[float]) -> float:
    return sum(velocity[i] * matrix[i][j] * velocity[j] for i in range(len(velocity)) for j in range(len(velocity)))


def all_true(values: Iterable[bool]) -> bool:
    frozen = tuple(values)
    return bool(frozen) and all(frozen)


def verify() -> dict[str, object]:
    bounded = {
        "s": 0.90,
        "q": 0.80,
        "g_1": 0.80,
        "g_2": 0.60,
        "kappa_1": 0.50,
        "kappa_2": 0.50,
        "L_v1": 0.90,
        "L_v2": 0.85,
        "p_mask": 0.30,
        "C_12": 0.20,
    }
    periodic = {
        "theta_1": 0.0,
        "theta_2": math.pi / 2.0,
        "phi_1": (0.0, 0.0, 0.0),
        "phi_2": (math.pi, math.pi, math.pi),
    }
    predicate_results = {
        "P_HCA_s_floor": bounded["s"] >= 0.70,
        "P_HCA_q_floor": bounded["q"] >= 0.65,
        "P_HCE_precedence": bounded["g_1"] >= bounded["g_2"],
        "P_HCE_wrapped_difference": -math.pi <= wrap(periodic["theta_1"] - periodic["theta_2"]) < math.pi,
        "P_BMIMS_L_v1": bounded["L_v1"] >= 0.70,
        "P_BMIMS_L_v2": bounded["L_v2"] >= 0.70,
        "P_BMIMS_mask": bounded["p_mask"] <= 0.45,
        "P_BMIMS_conflict": bounded["C_12"] <= 0.40,
        "P_STML_clearance": torus_distance(periodic["phi_1"], periodic["phi_2"]) >= 1.00,
    }
    matrix = metric()
    lower = cholesky(matrix)
    velocity = tuple(0.01 if index % 2 == 0 else -0.01 for index in range(len(matrix)))
    canonical_matrix = json.dumps(matrix, separators=(",", ":"), sort_keys=False).encode("utf-8")
    return {
        "experiment_id": "INTERFACE_ENVELOPE_N2_NUMERICAL_VERIFICATION_v0.1",
        "carrier": "[0,1]^10 x T^8",
        "bounded_basis": BASIS_BOUNDED,
        "periodic_basis": BASIS_PERIODIC,
        "period_lengths": PERIODS,
        "lattice_action_on_bounded_coordinates": "TRIVIAL",
        "metric_sha256": hashlib.sha256(canonical_matrix).hexdigest(),
        "metric_dimension": len(matrix),
        "cholesky_positive": True,
        "minimum_cholesky_pivot": min(lower[index][index] for index in range(len(lower))),
        "maneuver_cost": quadratic_cost(matrix, velocity),
        "wrapped_stml_distance": torus_distance(periodic["phi_1"], periodic["phi_2"]),
        "predicate_results": predicate_results,
        "feasible_witness": all_true(predicate_results.values()),
        "standing_ceiling": "BOUNDED_SYNTHETIC_NUMERICAL_CONFORMANCE_ONLY",
        "cc_fixture_execution": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
