import unittest

from fmcal.controller import FMCALController
from fmcal.haptics import DeviceCapabilityProfile, HapticDispatcher, ReceiptSigner
from fmcal.sensor_fusion import SensorFusionEstimator
from fmcal.types import DispatchStanding, FoldState, HapticPattern
from tests.helpers import frame


PROFILE = DeviceCapabilityProfile(
    {
        HapticPattern.SINGLE_PULSE: "CLICK_15MS",
        HapticPattern.DOUBLE_PULSE: "DOUBLE_30MS",
        HapticPattern.RISING_CHIRP: "RAMP_UP",
        HapticPattern.DESCENDING_CHIRP: "RAMP_DOWN",
        HapticPattern.FIRM_INTERRUPTION: "BRAKE_120HZ",
    }
)


class AmbiguousFailureBattery(unittest.TestCase):
    def controller(self):
        return FMCALController(HapticDispatcher(PROFILE, ReceiptSigner(b"synthetic-test-secret")))

    def test_uncertain_estimate_cannot_emit_positive_confirmation(self):
        estimate = SensorFusionEstimator().estimate(frame(), (0.4, 0.4, 0.4, 0.4), now_ms=1_050)
        decision = self.controller().select_lens(estimate, "blake3:a", "blake3:a", "pg:v1", "pg:v1")
        result, command = self.controller().dispatch_for(decision)
        self.assertEqual(result.standing, DispatchStanding.ZERO)
        self.assertIsNone(command)

    def test_semantic_digest_mutation_cannot_emit_positive_confirmation(self):
        controller = self.controller()
        estimate = SensorFusionEstimator().estimate(frame(), (0.1, 0.1, 0.1, 0.1), now_ms=1_050)
        decision = controller.select_lens(estimate, "blake3:a", "blake3:b", "pg:v1", "pg:v1")
        result, _ = controller.dispatch_for(decision)
        self.assertEqual(result.pattern, HapticPattern.ZERO_PATTERN)

    def test_predicate_substitution_cannot_emit_positive_confirmation(self):
        controller = self.controller()
        estimate = SensorFusionEstimator().estimate(frame(), (0.1, 0.1, 0.1, 0.1), now_ms=1_050)
        decision = controller.select_lens(estimate, "blake3:a", "blake3:a", "pg:v1", "pg:v2")
        result, _ = controller.dispatch_for(decision)
        self.assertEqual(result.pattern, HapticPattern.ZERO_PATTERN)

    def test_certified_transition_requires_delivery_receipt_for_confirmation(self):
        controller = self.controller()
        estimator = SensorFusionEstimator()
        first = estimator.estimate(frame(), (0.1, 0.1, 0.1, 0.1), now_ms=1_050)
        controller.select_lens(first, "blake3:a", "blake3:a", "pg:v1", "pg:v1")
        second = estimator.estimate(
            frame("event-2", 1_100, 90.0, FoldState.TENT_BOOK),
            (0.1, 0.1, 0.1, 0.1),
            now_ms=1_150,
        )
        decision = controller.select_lens(second, "blake3:a", "blake3:a", "pg:v1", "pg:v1")
        result, command = controller.dispatch_for(decision)
        self.assertEqual(result.standing, DispatchStanding.ISSUED)
        self.assertEqual(command.pattern, HapticPattern.DOUBLE_PULSE)


if __name__ == "__main__":
    unittest.main()
