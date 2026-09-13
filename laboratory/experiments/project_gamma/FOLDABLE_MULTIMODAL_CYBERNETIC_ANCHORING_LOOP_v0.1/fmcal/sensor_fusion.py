from __future__ import annotations

import math
from typing import Iterable, Optional

from .types import EstimateStanding, FoldState, OrientationEstimate, SensorFrame


class SensorFusionEstimator:
    """Deterministic conformance estimator, not a production sensor-fusion model."""

    def __init__(self, uncertainty_trace_limit: float = 1.0, max_age_ms: int = 250):
        self.uncertainty_trace_limit = uncertainty_trace_limit
        self.max_age_ms = max_age_ms
        self._last_timestamp_ms: Optional[int] = None

    @staticmethod
    def _derived_fold_state(angle: float) -> FoldState:
        if angle <= 20.0:
            return FoldState.FOLDED_COMPACT
        if angle >= 160.0:
            return FoldState.FLAT_UNFOLDED
        return FoldState.TENT_BOOK

    @staticmethod
    def _finite(values: Iterable[float]) -> bool:
        return all(math.isfinite(value) for value in values)

    def _fallback(self, frame: SensorFrame, covariance: tuple[float, float, float, float], reason: str) -> OrientationEstimate:
        return OrientationEstimate(
            event_id=frame.event_id,
            standing=EstimateStanding.FALLBACK,
            reason=reason,
            azimuth_deg=0.0,
            pitch_deg=0.0,
            roll_deg=0.0,
            fold_state=FoldState.FOLDED_COMPACT,
            covariance_diagonal=covariance,
            provenance=(frame.event_id, "FALLBACK_DEFAULT_CANONICAL"),
            user_override=frame.user_override,
        )

    def estimate(
        self,
        frame: SensorFrame,
        covariance_diagonal: tuple[float, float, float, float],
        now_ms: int,
    ) -> OrientationEstimate:
        if len(covariance_diagonal) != 4 or not self._finite(covariance_diagonal) or any(v < 0 for v in covariance_diagonal):
            return self._fallback(frame, covariance_diagonal, "INVALID_COVARIANCE")
        if not frame.event_id:
            return self._fallback(frame, covariance_diagonal, "MISSING_EVENT_ID")
        if self._last_timestamp_ms is not None and frame.timestamp_ms <= self._last_timestamp_ms:
            return self._fallback(frame, covariance_diagonal, "STALE_OR_OUT_OF_ORDER_EVENT")
        self._last_timestamp_ms = frame.timestamp_ms
        if now_ms < frame.timestamp_ms or now_ms - frame.timestamp_ms > self.max_age_ms:
            return self._fallback(frame, covariance_diagonal, "STALE_OR_FUTURE_EVENT")
        if frame.hinge_angle_deg is None or frame.display_geometry is None:
            return self._fallback(frame, covariance_diagonal, "MISSING_POSTURE_EVIDENCE")
        if not 0.0 <= frame.hinge_angle_deg <= 180.0:
            return self._fallback(frame, covariance_diagonal, "HINGE_OUT_OF_RANGE")
        if not self._finite((*frame.acceleration, *frame.angular_velocity)):
            return self._fallback(frame, covariance_diagonal, "NONFINITE_SENSOR_EVIDENCE")
        if sum(covariance_diagonal) > self.uncertainty_trace_limit:
            return self._fallback(frame, covariance_diagonal, "UNCERTAINTY_CEILING_EXCEEDED")

        fold_state = self._derived_fold_state(frame.hinge_angle_deg)
        if fold_state != frame.display_geometry:
            return self._fallback(frame, covariance_diagonal, "POSTURE_EVIDENCE_CONFLICT")

        ax, ay, az = frame.acceleration
        pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
        roll = math.degrees(math.atan2(ay, az))
        azimuth = frame.magnetic_heading_deg if frame.magnetic_heading_deg is not None else 0.0
        return OrientationEstimate(
            event_id=frame.event_id,
            standing=EstimateStanding.CERTIFIED,
            reason="CERTIFIED_SENSOR_ESTIMATE",
            azimuth_deg=azimuth % 360.0,
            pitch_deg=pitch,
            roll_deg=roll,
            fold_state=fold_state,
            covariance_diagonal=covariance_diagonal,
            provenance=(frame.event_id, "SYNTHETIC_HEADLESS_SENSOR_FRAME"),
            user_override=frame.user_override,
        )

