from fmcal.types import FoldState, SensorFrame


def frame(
    event_id: str = "event-1",
    timestamp_ms: int = 1_000,
    hinge_angle_deg: float | None = 180.0,
    display_geometry: FoldState | None = FoldState.FLAT_UNFOLDED,
    user_override: str | None = None,
) -> SensorFrame:
    return SensorFrame(
        event_id=event_id,
        timestamp_ms=timestamp_ms,
        acceleration=(0.0, 0.0, 1.0),
        angular_velocity=(0.0, 0.0, 0.0),
        magnetic_heading_deg=90.0,
        hinge_angle_deg=hinge_angle_deg,
        display_geometry=display_geometry,
        ambient_lux=400.0,
        ambient_color_temp_k=5_000.0,
        user_override=user_override,
    )
