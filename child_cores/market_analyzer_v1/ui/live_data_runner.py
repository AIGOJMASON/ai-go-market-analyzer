from __future__ import annotations

import importlib
import json
from typing import Any, Callable, Dict, Optional

from .live_data_adapter import normalize_live_input
from .live_data_source import get_default_live_style_case, get_live_style_case


class LiveDataRunnerError(RuntimeError):
    pass


def _resolve_pm_route_callable() -> Optional[Callable[[Dict[str, Any]], Dict[str, Any]]]:
    module_name = "core.strategy.pm_market_analyzer_route"
    candidate_function_names = (
        "route_market_analyzer_request",
        "route_market_analyzer_packet",
        "route_request",
        "run_route",
        "run",
    )

    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None

    for function_name in candidate_function_names:
        candidate = getattr(module, function_name, None)
        if callable(candidate):
            return candidate
    return None


def _fallback_route(normalized_packet: Dict[str, Any]) -> Dict[str, Any]:
    qualified_candidates = [
        candidate
        for candidate in normalized_packet["candidates"]
        if candidate["necessity_qualified"] and candidate["rebound_confirmed"]
    ]

    if not normalized_packet["event_context"]["confirmed"]:
        return {
            "status": "rejected",
            "reason": "event_not_confirmed",
            "watcher": {"passed": False},
            "approval_required": True,
            "execution_allowed": False,
            "recommendations": [],
            "receipt_trace_packet": {
                "receipt_id": f"{normalized_packet['case_id']}-REJECT-UNCONFIRMED",
                "path": "live_data_runner.fallback_route",
            },
        }

    if not qualified_candidates:
        return {
            "status": "rejected",
            "reason": "no necessity-qualified candidates available",
            "watcher": {"passed": False},
            "approval_required": True,
            "execution_allowed": False,
            "recommendations": [],
            "receipt_trace_packet": {
                "receipt_id": f"{normalized_packet['case_id']}-REJECT-NONECESSITY",
                "path": "live_data_runner.fallback_route",
            },
        }

    recommendations = []
    for candidate in qualified_candidates:
        recommendations.append(
            {
                "symbol": candidate["symbol"],
                "entry": candidate["entry_signal"],
                "exit": candidate["exit_signal"],
                "confidence": candidate["confidence"],
            }
        )

    return {
        "status": "ok",
        "market_regime_record": {"regime": "normal"},
        "event_propagation_record": {
            "theme": normalized_packet["event_context"]["theme"],
            "propagation": normalized_packet["event_context"]["propagation"],
        },
        "necessity_filtered_candidate_set": qualified_candidates,
        "trade_recommendation_packet": {
            "recommendation_count": len(recommendations),
            "recommendations": recommendations,
        },
        "approval_request_packet": {
            "approval_gate": "human_trade_approval_record",
            "approval_required": True,
        },
        "watcher": {"passed": True},
        "approval_required": True,
        "execution_allowed": False,
        "receipt_trace_packet": {
            "receipt_id": f"{normalized_packet['case_id']}-OK-001",
            "path": "live_data_runner.fallback_route",
        },
    }


def run_live_case(case_id: Optional[str] = None) -> Dict[str, Any]:
    raw_case = get_default_live_style_case() if case_id is None else get_live_style_case(case_id)
    normalized_packet = normalize_live_input(raw_case)

    pm_route = _resolve_pm_route_callable()
    if pm_route is None:
        routed_result = _fallback_route(normalized_packet)
        route_mode = "fallback_stub"
    else:
        routed_result = pm_route(normalized_packet)
        route_mode = "pm_route"

    return {
        "source_case": raw_case,
        "normalized_packet": normalized_packet,
        "route_mode": route_mode,
        "routed_result": routed_result,
    }


if __name__ == "__main__":
    result = run_live_case()
    print(json.dumps(result, indent=2))
