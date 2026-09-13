import unittest

from fmcal.sensor_fusion import SensorFusionEstimator
from fmcal.types import EstimateStanding, FoldState
from tests.helpers import frame


class SensorFusionTests(unittest.TestCase):
    def test_certifies_consistent_fresh_frame(self):
        result = SensorFusionEstimator().estimate(frame(), (0.1, 0.1, 0.1, 0.1), now_ms=1_050)
        self.assertEqual(result.standing, EstimateStanding.CERTIFIED)
        self.assertEqual(result.fold_state, FoldState.FLAT_UNFOLDED)

    def test_missing_posture_fails_closed(self):
        result = SensorFusionEstimator().estimate(
            frame(hinge_angle_deg=None), (0.1, 0.1, 0.1, 0.1), now_ms=1_050
        )
        self.assertEqual(result.standing, EstimateStanding.FALLBACK)
        self.assertEqual(result.reason, "MISSING_POSTURE_EVIDENCE")

    def test_high_uncertainty_fails_closed(self):
        result = SensorFusionEstimator().estimate(frame(), (0.4, 0.4, 0.4, 0.4), now_ms=1_050)
        self.assertEqual(result.reason, "UNCERTAINTY_CEILING_EXCEEDED")

    def test_conflicting_posture_fails_closed(self):
        result = SensorFusionEstimator().estimate(
            frame(hinge_angle_deg=10.0, display_geometry=FoldState.FLAT_UNFOLDED),
            (0.1, 0.1, 0.1, 0.1),
            now_ms=1_050,
        )
        self.assertEqual(result.reason, "POSTURE_EVIDENCE_CONFLICT")

    def test_out_of_order_event_fails_closed(self):
        estimator = SensorFusionEstimator()
        estimator.estimate(frame(timestamp_ms=1_000), (0.1, 0.1, 0.1, 0.1), now_ms=1_050)
        result = estimator.estimate(frame(event_id="event-2", timestamp_ms=999), (0.1, 0.1, 0.1, 0.1), now_ms=1_050)
        self.assertEqual(result.reason, "STALE_OR_OUT_OF_ORDER_EVENT")

    def test_user_override_is_preserved_not_inferred(self):
        result = SensorFusionEstimator().estimate(
            frame(user_override="PORTRAIT_LOCK"), (0.1, 0.1, 0.1, 0.1), now_ms=1_050
        )
        self.assertEqual(result.user_override, "PORTRAIT_LOCK")


if __name__ == "__main__":
    unittest.main()
