import unittest

from fmcal.haptics import CONFIRMATORY_PATTERNS, DeviceCapabilityProfile, HapticDispatcher, ReceiptSigner
from fmcal.types import DeliveryReceipt, DispatchStanding, HapticCommand, HapticPattern


def profile(alias: bool = False) -> DeviceCapabilityProfile:
    signatures = {
        HapticPattern.SINGLE_PULSE: "CLICK_15MS",
        HapticPattern.DOUBLE_PULSE: "DOUBLE_30MS",
        HapticPattern.RISING_CHIRP: "RAMP_UP",
        HapticPattern.DESCENDING_CHIRP: "RAMP_DOWN",
        HapticPattern.FIRM_INTERRUPTION: "BRAKE_120HZ",
    }
    if alias:
        signatures[HapticPattern.DOUBLE_PULSE] = signatures[HapticPattern.SINGLE_PULSE]
    return DeviceCapabilityProfile(signatures)


class HapticDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.signer = ReceiptSigner(b"synthetic-test-secret")
        self.dispatcher = HapticDispatcher(profile(), self.signer)

    def test_vocabulary_is_injective_for_confirmations(self):
        self.assertTrue(profile().is_injective_for(CONFIRMATORY_PATTERNS))

    def test_capability_alias_blocks_positive_issue(self):
        dispatcher = HapticDispatcher(profile(alias=True), self.signer)
        result, command = dispatcher.issue("event-1", HapticPattern.DOUBLE_PULSE)
        self.assertEqual(result.standing, DispatchStanding.REFUSED)
        self.assertEqual(result.pattern, HapticPattern.ZERO_PATTERN)
        self.assertIsNone(command)

    def test_command_is_not_confirmation(self):
        result, command = self.dispatcher.issue("event-1", HapticPattern.DOUBLE_PULSE)
        self.assertEqual(result.standing, DispatchStanding.ISSUED)
        self.assertIsNotNone(command)

    def test_only_authenticated_exact_delivery_confirms(self):
        _, command = self.dispatcher.issue("event-1", HapticPattern.DOUBLE_PULSE)
        receipt = self.signer.sign(command, delivered=True, nonce="n-1")
        result = self.dispatcher.confirm(receipt)
        self.assertEqual(result.standing, DispatchStanding.CONFIRMED_DELIVERED)
        self.assertEqual(result.reason, "DELIVERY_WITNESSED_NOT_USER_PERCEPTION")

    def test_receipt_mismatch_fails_closed(self):
        _, command = self.dispatcher.issue("event-1", HapticPattern.DOUBLE_PULSE)
        substituted = HapticCommand(command.command_id, "event-other", command.pattern, command.physical_signature)
        mismatch = self.signer.sign(substituted, delivered=True, nonce="n-2")
        result = self.dispatcher.confirm(mismatch)
        self.assertEqual(result.reason, "RECEIPT_BINDING_MISMATCH")
        self.assertEqual(result.pattern, HapticPattern.ZERO_PATTERN)

    def test_unauthenticated_receipt_fails_closed(self):
        _, command = self.dispatcher.issue("event-1", HapticPattern.DOUBLE_PULSE)
        receipt = DeliveryReceipt(command.command_id, command.event_id, command.pattern, True, "n-3", "bad-tag")
        result = self.dispatcher.confirm(receipt)
        self.assertEqual(result.reason, "UNAUTHENTICATED_RECEIPT")

    def test_replayed_receipt_fails_closed(self):
        _, command = self.dispatcher.issue("event-1", HapticPattern.DOUBLE_PULSE)
        receipt = self.signer.sign(command, delivered=False, nonce="n-4")
        self.dispatcher.confirm(receipt)
        result = self.dispatcher.confirm(receipt)
        self.assertEqual(result.reason, "REPLAYED_RECEIPT")

    def test_authenticated_non_delivery_fails_closed(self):
        _, command = self.dispatcher.issue("event-1", HapticPattern.DOUBLE_PULSE)
        receipt = self.signer.sign(command, delivered=False, nonce="n-5")
        result = self.dispatcher.confirm(receipt)
        self.assertEqual(result.reason, "ACTUATOR_DID_NOT_DELIVER")
        self.assertEqual(result.pattern, HapticPattern.ZERO_PATTERN)


if __name__ == "__main__":
    unittest.main()
