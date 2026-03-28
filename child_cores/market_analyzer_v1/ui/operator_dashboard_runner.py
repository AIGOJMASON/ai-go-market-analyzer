from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.api.pm_influence import build_pm_influence_record
    from AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner import run_live_payload
    from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
        build_operator_dashboard,
    )
    from AI_GO.child_cores.market_analyzer_v1.external_memory.pattern_runtime_integration import (
        apply_external_memory_pattern_flow,
    )
except ModuleNotFoundError:
    from api.pm_influence import build_pm_influence_record
    from child_cores.market_analyzer_v1.ui.live_data_runner import run_live_payload
    from child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
        build_operator_dashboard,
    )
    from child_cores.market_analyzer_v1.external_memory.pattern_runtime_integration import (
        apply_external_memory_pattern_flow,
    )


def _build_live_case_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    request_id = payload.get("request_id", "live-case")
    symbol = payload.get("symbol", "UNKNOWN")
    headline = payload.get("headline", "Live event")
    sector = payload.get("sector", "unknown")
    confirmation = payload.get("confirmation", "partial")
    price_change_pct = float(payload.get("price_change_pct", 0.0))

    return {
        "case_id": request_id,
        "observed_at": None,
        "macro_context": {
            "headline": headline,
            "macro_bias": "neutral",
        },
        "event_signal": {
            "event_theme": "energy_rebound" if sector == "energy" else "speculative_move",
            "confirmed": confirmation in {"confirmed", "partial"},
            "propagation": "moderate" if abs(price_change_pct) >= 1 else "limited",
        },
        "candidates": [
            {
                "symbol": symbol,
                "sector": sector,
                "necessity_qualified": sector in {
                    "energy",
                    "utilities",
                    "consumer_staples",
                    "healthcare",
                    "materials",
                },
                "rebound_confirmed": confirmation in {"confirmed", "partial"},
                "entry_signal": "reclaim support",
                "exit_signal": "short-term resistance",
                "confidence": "medium",
            }
        ],
        "operator_notes": "Generated from live API payload",
    }


def _coerce_refinement_packet(result: Dict[str, Any]) -> Dict[str, Any] | None:
    refinement_packet = result.get("refinement_packet")
    if isinstance(refinement_packet, dict):
        return refinement_packet

    refinement_panel = result.get("refinement_panel")
    if isinstance(refinement_panel, dict):
        return refinement_panel

    cognition_panel = result.get("cognition_panel")
    if isinstance(cognition_panel, dict):
        refinement = cognition_panel.get("refinement")
        if isinstance(refinement, dict):
            return refinement

    return None


def _apply_pm_influence(result: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(result)

    refinement_packet = _coerce_refinement_packet(enriched)
    recommendation_panel = enriched.get("recommendation_panel", {})

    if not refinement_packet:
        enriched["pm_influence_record"] = build_pm_influence_record(
            core_id="market_analyzer_v1",
            recommendation_panel=recommendation_panel,
            refinement_packets=None,
        )
        return enriched

    enriched["pm_influence_record"] = build_pm_influence_record(
        core_id="market_analyzer_v1",
        recommendation_panel=recommendation_panel,
        refinement_packets=[refinement_packet],
    )

    return enriched


def run_operator_dashboard(payload: Dict[str, Any]) -> Dict[str, Any]:
    live_case = _build_live_case_from_payload(payload)

    result = run_live_payload(live_case)

    # 🔥 NEW: pattern aggregation injection
    result = apply_external_memory_pattern_flow(result)

    influenced_result = _apply_pm_influence(result)
    dashboard = build_operator_dashboard(influenced_result)

    return {
        "status": "ok",
        "request_id": payload.get("request_id"),
        "core_id": "market_analyzer_v1",
        "route_mode": "pm_route",
        "mode": "advisory",
        "execution_allowed": False,
        **dashboard,
    }
