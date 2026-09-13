"""Synthetic tests for the corrected mixed carrier; no hidden battery access."""

import math
import unittest

from apparatus.interface_envelope_n2_verifier import metric, torus_distance, verify, wrap


class InterfaceEnvelopeN2Tests(unittest.TestCase):
    def test_wrapping_is_period_invariant(self) -> None:
        self.assertAlmostEqual(wrap(0.25), wrap(0.25 + 8.0 * math.pi))

    def test_torus_distance_is_lattice_invariant(self) -> None:
        left = (0.1, 0.2, 0.3)
        shifted = (left[0] + 2.0 * math.pi, left[1] - 4.0 * math.pi, left[2] + 6.0 * math.pi)
        right = (1.0, 1.1, 1.2)
        self.assertAlmostEqual(torus_distance(left, right), torus_distance(shifted, right))

    def test_metric_is_symmetric(self) -> None:
        matrix = metric()
        self.assertTrue(all(matrix[i][j] == matrix[j][i] for i in range(len(matrix)) for j in range(len(matrix))))

    def test_frozen_specimen_is_positive_and_feasible(self) -> None:
        residue = verify()
        self.assertTrue(residue["cholesky_positive"])
        self.assertGreater(residue["minimum_cholesky_pivot"], 0.0)
        self.assertGreater(residue["maneuver_cost"], 0.0)
        self.assertTrue(residue["feasible_witness"])
        self.assertFalse(residue["cc_fixture_execution"])


if __name__ == "__main__":
    unittest.main()
