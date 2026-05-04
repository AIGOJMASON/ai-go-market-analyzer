from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


class CoreSMIError(Exception):
    """Raised when local SMI input is invalid."""


def build_core_status_summary(
    core_id: str,
    runtime_result: Dict[str, Any],
    watcher_result: Dict[str, Any],
    continuity_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Produce a bounded local status summary for market_analyzer_v1.

    This is informational only and carries no execution authority.
    """
    if core_id != "market_analyzer_v1":
        raise CoreSMIError("core_id mismatch")

    if not isinstance(runtime_result, dict):
        raise CoreSMIError("runtime_result must be a dict")

    if not isinstance(watcher_result, dict):
        raise CoreSMIError("watcher_result must be a dict")

    artifacts = runtime_result.get("artifacts", {})
    if not isinstance(artifacts, dict):
        raise CoreSMIError("runtime_result.artifacts must be a dict")

    recommendation_packet = artifacts.get("trade_recommendation_packet", {})
    approval_request_packet = artifacts.get("approval_request_packet", {})

    continuity_snapshot = deepcopy(continuity_state or {})

    return {
        "core_id": "market_analyzer_v1",
        "artifact_type": "child_core_status_summary",
        "status": runtime_result.get("status", "unknown"),
        "watcher_verified": watcher_result.get("watcher_passed", False),
        "recommendation_count": recommendation_packet.get("recommendation_count", 0),
        "approval_required": approval_request_packet.get("approval_type") == "human_trade_approval_record",
        "execution_allowed": False,
        "continuity_snapshot": continuity_snapshot,
        "notes": [
            "Summary is informational only.",
            "No execution authority is created by local SMI."
        ],
    }