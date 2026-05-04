from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def build_approval_request_view(approval_request_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render the approval gate panel view.
    """
    packet = deepcopy(approval_request_packet)

    return {
        "panel": "approval_gate",
        "core_id": "market_analyzer_v1",
        "artifact_type": "approval_request_view",
        "approval_type": packet.get("approval_type"),
        "recommendation_count": packet.get("recommendation_count", 0),
        "execution_allowed": packet.get("execution_allowed", False),
        "trace_reference": packet.get("trace_reference"),
        "source_artifact": packet.get("artifact_type"),
    }