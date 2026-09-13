from __future__ import annotations

import hashlib
import hmac
import uuid
from dataclasses import dataclass
from typing import Mapping, Optional

from .types import (
    DeliveryReceipt,
    DispatchResult,
    DispatchStanding,
    HapticCommand,
    HapticPattern,
)


CONFIRMATORY_PATTERNS = frozenset(
    {
        HapticPattern.SINGLE_PULSE,
        HapticPattern.DOUBLE_PULSE,
        HapticPattern.RISING_CHIRP,
        HapticPattern.DESCENDING_CHIRP,
    }
)


@dataclass(frozen=True)
class DeviceCapabilityProfile:
    signatures: Mapping[HapticPattern, str]

    def signature_for(self, pattern: HapticPattern) -> Optional[str]:
        return self.signatures.get(pattern)

    def is_injective_for(self, patterns: frozenset[HapticPattern]) -> bool:
        values = [self.signatures[p] for p in patterns if p in self.signatures]
        return len(values) == len(patterns) and len(values) == len(set(values))


class ReceiptSigner:
    """Test-only HMAC boundary standing in for an authenticated actuator."""

    def __init__(self, secret: bytes):
        if not secret:
            raise ValueError("receipt secret must not be empty")
        self._secret = secret

    @staticmethod
    def _message(command_id: str, event_id: str, pattern: HapticPattern, delivered: bool, nonce: str) -> bytes:
        return f"{command_id}|{event_id}|{pattern.value}|{int(delivered)}|{nonce}".encode()

    def sign(self, command: HapticCommand, delivered: bool, nonce: str) -> DeliveryReceipt:
        tag = hmac.new(
            self._secret,
            self._message(command.command_id, command.event_id, command.pattern, delivered, nonce),
            hashlib.sha256,
        ).hexdigest()
        return DeliveryReceipt(command.command_id, command.event_id, command.pattern, delivered, nonce, tag)

    def verify(self, receipt: DeliveryReceipt) -> bool:
        expected = hmac.new(
            self._secret,
            self._message(receipt.command_id, receipt.event_id, receipt.pattern, receipt.delivered, receipt.nonce),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, receipt.auth_tag)


class HapticDispatcher:
    def __init__(self, profile: DeviceCapabilityProfile, signer: ReceiptSigner):
        self.profile = profile
        self.signer = signer
        self._issued: dict[str, HapticCommand] = {}
        self._used_nonces: set[str] = set()

    def issue(self, event_id: str, pattern: HapticPattern) -> tuple[DispatchResult, Optional[HapticCommand]]:
        if pattern == HapticPattern.ZERO_PATTERN:
            return DispatchResult(DispatchStanding.ZERO, pattern, "NO_CERTIFIED_STATE_TRANSITION"), None
        signature = self.profile.signature_for(pattern)
        if signature is None:
            return DispatchResult(DispatchStanding.REFUSED, HapticPattern.ZERO_PATTERN, "UNSUPPORTED_PATTERN"), None
        if pattern in CONFIRMATORY_PATTERNS and not self.profile.is_injective_for(CONFIRMATORY_PATTERNS):
            return DispatchResult(DispatchStanding.REFUSED, HapticPattern.ZERO_PATTERN, "CAPABILITY_PATTERN_ALIAS"), None
        command = HapticCommand(str(uuid.uuid4()), event_id, pattern, signature)
        self._issued[command.command_id] = command
        return DispatchResult(DispatchStanding.ISSUED, pattern, "COMMAND_IS_NOT_DELIVERY", command.command_id), command

    def confirm(self, receipt: DeliveryReceipt) -> DispatchResult:
        command = self._issued.get(receipt.command_id)
        if command is None:
            return DispatchResult(DispatchStanding.REFUSED, HapticPattern.ZERO_PATTERN, "UNKNOWN_COMMAND")
        if receipt.nonce in self._used_nonces:
            return DispatchResult(DispatchStanding.REFUSED, HapticPattern.ZERO_PATTERN, "REPLAYED_RECEIPT")
        if not self.signer.verify(receipt):
            return DispatchResult(DispatchStanding.REFUSED, HapticPattern.ZERO_PATTERN, "UNAUTHENTICATED_RECEIPT")
        self._used_nonces.add(receipt.nonce)
        if receipt.event_id != command.event_id or receipt.pattern != command.pattern:
            return DispatchResult(DispatchStanding.REFUSED, HapticPattern.ZERO_PATTERN, "RECEIPT_BINDING_MISMATCH")
        if not receipt.delivered:
            return DispatchResult(DispatchStanding.REFUSED, HapticPattern.ZERO_PATTERN, "ACTUATOR_DID_NOT_DELIVER")
        del self._issued[receipt.command_id]
        return DispatchResult(
            DispatchStanding.CONFIRMED_DELIVERED,
            receipt.pattern,
            "DELIVERY_WITNESSED_NOT_USER_PERCEPTION",
            receipt.command_id,
        )

