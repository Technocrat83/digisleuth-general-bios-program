from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class FoldState(str, Enum):
    FLAT_UNFOLDED = "FLAT_UNFOLDED"
    TENT_BOOK = "TENT_BOOK"
    FOLDED_COMPACT = "FOLDED_COMPACT"


class EstimateStanding(str, Enum):
    CERTIFIED = "CERTIFIED"
    FALLBACK = "FALLBACK_DEFAULT_CANONICAL"


class HapticPattern(str, Enum):
    SINGLE_PULSE = "SINGLE_PULSE"
    DOUBLE_PULSE = "DOUBLE_PULSE"
    RISING_CHIRP = "RISING_CHIRP"
    DESCENDING_CHIRP = "DESCENDING_CHIRP"
    FIRM_INTERRUPTION = "FIRM_INTERRUPTION"
    ZERO_PATTERN = "ZERO_PATTERN"


class DispatchStanding(str, Enum):
    ISSUED = "ISSUED_NOT_CONFIRMED"
    CONFIRMED_DELIVERED = "CONFIRMED_DELIVERED"
    REFUSED = "REFUSED"
    ZERO = "ZERO"


@dataclass(frozen=True)
class SensorFrame:
    event_id: str
    timestamp_ms: int
    acceleration: Tuple[float, float, float]
    angular_velocity: Tuple[float, float, float]
    magnetic_heading_deg: Optional[float]
    hinge_angle_deg: Optional[float]
    display_geometry: Optional[FoldState]
    ambient_lux: Optional[float]
    ambient_color_temp_k: Optional[float]
    user_override: Optional[str] = None


@dataclass(frozen=True)
class OrientationEstimate:
    event_id: str
    standing: EstimateStanding
    reason: str
    azimuth_deg: float
    pitch_deg: float
    roll_deg: float
    fold_state: FoldState
    covariance_diagonal: Tuple[float, float, float, float]
    provenance: Tuple[str, ...]
    user_override: Optional[str]

    @property
    def covariance_trace(self) -> float:
        return sum(self.covariance_diagonal)


@dataclass(frozen=True)
class LensDecision:
    event_id: str
    lens: str
    semantic_digest: str
    predicate_bundle_id: str
    certified_transition: bool


@dataclass(frozen=True)
class HapticCommand:
    command_id: str
    event_id: str
    pattern: HapticPattern
    physical_signature: str


@dataclass(frozen=True)
class DeliveryReceipt:
    command_id: str
    event_id: str
    pattern: HapticPattern
    delivered: bool
    nonce: str
    auth_tag: str


@dataclass(frozen=True)
class DispatchResult:
    standing: DispatchStanding
    pattern: HapticPattern
    reason: str
    command_id: Optional[str] = None

