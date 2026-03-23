from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from .active_event_view import build_active_event_view
from .approval_request_view import build_approval_request_view
from .market_regime_view import build_market_regime_view
from .receipt_trace_view import build_receipt_trace_view
from .trade_recommendation_view import build_trade_recommendation_view
from .watchlist_view import build_watchlist_view


class OutputBuilderError(Exception):
    """Raised when required artifacts are missing for dashboard output."""


REQUIRED_ARTIFACT_KEYS = {
    "market_regime_record",
    "event_propagation_record",
    "necessity_filtered_candidate_set",
    "trade_recommendation_packet",
    "receipt_trace_packet",
    "approval_request_packet",
}


def _require_artifact(artifacts: Dict[str, Any], key: str) -> None:
    if key not in artifacts:
        raise OutputBuilderError(f"missing required artifact: {key}")
    if not isinstance(artifacts[key], dict):
        raise OutputBuilderError(f"artifact must be dict: {key}")


def build_output_views(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert runtime artifacts into dashboard-ready views.

    This module does not invent data and does not alter authority.
    """
    if not isinstance(runtime_result, dict):
        raise OutputBuilderError("runtime_result must be a dict")

    artifacts = runtime_result.get("artifacts")
    if not isinstance(artifacts, dict):
        raise OutputBuilderError("runtime_result.artifacts must be a dict")

    for key in REQUIRED_ARTIFACT_KEYS:
        _require_artifact(artifacts, key)

    market_regime_view = build_market_regime_view(artifacts["market_regime_record"])
    active_event_view = build_active_event_view(artifacts["event_propagation_record"])
    watchlist_view = build_watchlist_view(artifacts["necessity_filtered_candidate_set"])
    trade_recommendation_view = build_trade_recommendation_view(artifacts["trade_recommendation_packet"])
    receipt_trace_view = build_receipt_trace_view(artifacts["receipt_trace_packet"])
    approval_request_view = build_approval_request_view(artifacts["approval_request_packet"])

    return {
        "core_id": "market_analyzer_v1",
        "status": "ok",
        "artifact_type": "market_dashboard_output",
        "views": {
            "market_regime": market_regime_view,
            "active_events": active_event_view,
            "watchlist": watchlist_view,
            "recommendations": trade_recommendation_view,
            "approval_gate": approval_request_view,
            "receipt_trace": receipt_trace_view,
        },
        "source_artifacts": deepcopy(artifacts),
    }