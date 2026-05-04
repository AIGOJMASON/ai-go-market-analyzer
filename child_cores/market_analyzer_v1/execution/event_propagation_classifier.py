from __future__ import annotations

from typing import Any, Dict


ALLOWED_SPEEDS = {"fast", "medium", "slow"}
ALLOWED_DEPTHS = {"primary", "secondary", "tertiary"}


def classify_event_propagation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize propagation speed and ripple depth for the active event.
    """
    event_id = event.get("event_id")
    event_type = event.get("event_type", "unclassified")
    speed = str(event.get("propagation_speed", "medium")).lower()
    depth = str(event.get("ripple_depth", "primary")).lower()

    if speed not in ALLOWED_SPEEDS:
        speed = "medium"
    if depth not in ALLOWED_DEPTHS:
        depth = "primary"

    return {
        "artifact_type": "event_propagation_record",
        "core_id": "market_analyzer_v1",
        "event_id": event_id,
        "event_type": event_type,
        "propagation_speed": speed,
        "ripple_depth": depth,
        "shock_confirmed": bool(event.get("shock_confirmed", False)),
    }