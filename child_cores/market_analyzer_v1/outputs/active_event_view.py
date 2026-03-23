from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def build_active_event_view(event_propagation_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render the active event panel view.
    """
    record = deepcopy(event_propagation_record)

    return {
        "panel": "active_events",
        "core_id": "market_analyzer_v1",
        "artifact_type": "active_event_view",
        "event_id": record.get("event_id"),
        "event_type": record.get("event_type"),
        "shock_confirmed": record.get("shock_confirmed", False),
        "propagation_speed": record.get("propagation_speed"),
        "ripple_depth": record.get("ripple_depth"),
        "source_artifact": record.get("artifact_type"),
    }