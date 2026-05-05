# AI_GO/tests/stage_market_analyzer_v1_external_memory_panel_probe.py
from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
        build_operator_dashboard,
    )
except ImportError:
    from child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (  # type: ignore
        build_operator_dashboard,
    )

try:
    from AI_GO.api.schemas.market_analyzer_response import build_market_analyzer_response
except ImportError:
    from api.schemas.market_analyzer_response import build_market_analyzer_response  # type: ignore


def _base_runtime_result() -> Dict[str, Any]:
    return {
        "status": "ok",
        "request_id": "probe-extmem-001",
        "core_id": "market_analyzer_v1",
        "route_mode": "pm_route",
        "mode": "advisory",
        "execution_allowed": False,
        "case_panel": {
            "case_id": "case-extmem-001",
            "title": "Energy disruption event",
            "observed_at": "2026-03-29T12:00:00Z",
            "input_mode": "live",
        },
        "runtime_panel": {
            "market_regime": "normal",
            "event_theme": "energy_rebound",
            "macro_bias": "neutral",
            "headline": "Energy disruption event",
            "candidate_count": 1,
            "candidates": [{"symbol": "XLE", "score": 0.74}],
        },
        "recommendation_panel": {
            "state": "present",
            "count": 1,
            "items": [{"symbol": "XLE", "entry": "reclaim support", "exit": "short-term resistance"}],
        },
        "governance_panel": {
            "mode": "advisory",
            "execution_allowed": False,
            "approval_required": True,
            "watcher_passed": True,
            "watcher_status": "passed",
            "closeout_status": "accepted",
            "requires_review": False,
        },
    }


def _memory_panel() -> Dict[str, Any]:
    return {
        "visible": True,
        "source": "external_memory",
        "pattern_detected": True,
        "pattern_strength": "medium",
        "historical_confirmation": "mixed",
        "confidence_adjustment": "down",
        "summary": "Two similar energy-disruption patterns produced short-lived strength followed by volatility.",
        "dominant_symbol": "XLE",
        "dominant_sector": "energy",
        "recurrence_count": 2,
        "temporal_span_days": 180,
        "similar_events": [
            {
                "event_id": "evt-001",
                "symbol": "XLE",
                "event_theme": "energy_rebound",
                "outcome": "initial_strength_then_fade",
                "summary": "Short-lived rebound after supply disruption.",
            }
        ],
        "provenance_refs": ["mem-001", "mem-002"],
    }


def case_01_external_memory_panel_is_exposed() -> Dict[str, Any]:
    runtime_result = _base_runtime_result()
    runtime_result["external_memory_panel"] = _memory_panel()

    dashboard = build_operator_dashboard(runtime_result)

    assert "external_memory_panel" in dashboard
    panel = dashboard["external_memory_panel"]
    assert panel["pattern_detected"] is True
    assert panel["pattern_strength"] == "medium"
    assert panel["advisory_only"] is True
    assert panel["recurrence_count"] == 2

    response = build_market_analyzer_response(dashboard)
    assert "external_memory_panel" in response
    return {"case": "case_01_external_memory_panel_is_exposed", "status": "passed"}


def case_02_non_dict_optional_memory_panel_is_omitted() -> Dict[str, Any]:
    runtime_result = _base_runtime_result()
    runtime_result["external_memory_panel"] = "invalid"

    dashboard = build_operator_dashboard(runtime_result)

    assert "external_memory_panel" not in dashboard
    return {"case": "case_02_non_dict_optional_memory_panel_is_omitted", "status": "passed"}


def case_03_empty_memory_signal_is_omitted() -> Dict[str, Any]:
    runtime_result = _base_runtime_result()
    runtime_result["external_memory_panel"] = {
        "pattern_detected": False,
        "summary": None,
        "recurrence_count": 0,
    }

    dashboard = build_operator_dashboard(runtime_result)

    assert "external_memory_panel" not in dashboard
    return {"case": "case_03_empty_memory_signal_is_omitted", "status": "passed"}


def case_04_merge_payload_is_supported() -> Dict[str, Any]:
    runtime_result = _base_runtime_result()
    runtime_result["external_memory_merge"] = {
        "external_memory_panel": _memory_panel()
    }

    dashboard = build_operator_dashboard(runtime_result)

    assert "external_memory_panel" in dashboard
    assert dashboard["external_memory_panel"]["source"] == "external_memory"
    return {"case": "case_04_merge_payload_is_supported", "status": "passed"}


def run_probe() -> Dict[str, Any]:
    results = [
        case_01_external_memory_panel_is_exposed(),
        case_02_non_dict_optional_memory_panel_is_omitted(),
        case_03_empty_memory_signal_is_omitted(),
        case_04_merge_payload_is_supported(),
    ]
    passed = sum(1 for item in results if item["status"] == "passed")
    failed = len(results) - passed
    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_probe())