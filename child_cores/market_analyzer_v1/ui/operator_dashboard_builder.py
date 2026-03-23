from __future__ import annotations

from typing import Any, Dict, List


def build_operator_dashboard(run_result: Dict[str, Any]) -> Dict[str, Any]:
    source_case = run_result["source_case"]
    normalized_packet = run_result["normalized_packet"]
    routed_result = run_result["routed_result"]

    status = routed_result.get("status", "unknown")
    watcher = routed_result.get("watcher", {"passed": False})
    receipt_trace_packet = routed_result.get("receipt_trace_packet", {})
    approval_request_packet = routed_result.get("approval_request_packet", {})

    if status == "ok":
        recommendation_packet = routed_result.get("trade_recommendation_packet", {})
        recommendations: List[Dict[str, Any]] = recommendation_packet.get("recommendations", [])
        candidate_set = routed_result.get("necessity_filtered_candidate_set", [])
        regime = routed_result.get("market_regime_record", {}).get("regime", "unknown")
        event_theme = routed_result.get("event_propagation_record", {}).get(
            "theme",
            normalized_packet["event_context"]["theme"],
        )
        rejection_reason = None
    else:
        recommendations = []
        candidate_set = []
        regime = "rejected"
        event_theme = normalized_packet["event_context"]["theme"]
        rejection_reason = routed_result.get("reason", "unknown_rejection")

    return {
        "dashboard_type": "market_analyzer_v1_operator_dashboard",
        "core_id": "market_analyzer_v1",
        "route_mode": run_result["route_mode"],
        "status": status,
        "case_panel": {
            "case_id": source_case["case_id"],
            "title": source_case["title"],
            "observed_at": source_case["observed_at"],
        },
        "market_panel": {
            "market_regime": regime,
            "event_theme": event_theme,
            "macro_bias": normalized_packet["event_context"]["macro_bias"],
            "headline": normalized_packet["event_context"]["headline"],
        },
        "candidate_panel": {
            "candidate_count": len(candidate_set),
            "symbols": [candidate["symbol"] for candidate in candidate_set],
        },
        "recommendation_panel": {
            "recommendation_count": len(recommendations),
            "recommendations": recommendations,
        },
        "governance_panel": {
            "watcher_passed": bool(watcher.get("passed", False)),
            "approval_required": bool(routed_result.get("approval_required", True)),
            "execution_allowed": bool(routed_result.get("execution_allowed", False)),
            "approval_gate": approval_request_packet.get(
                "approval_gate",
                "human_trade_approval_record",
            ),
            "receipt_id": receipt_trace_packet.get("receipt_id", "missing"),
        },
        "rejection_panel": {
            "rejected": status != "ok",
            "reason": rejection_reason,
        },
    }