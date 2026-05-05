from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from AI_GO.api.pre_interface_smi import record_pre_interface_exposure
from AI_GO.api.pre_interface_watcher import run_pre_interface_watcher
from AI_GO.child_cores.ingress.canonical_live_ingress import (
    build_canonical_live_pm_packet,
)
from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
    build_operator_dashboard,
)
from AI_GO.core.strategy.pm_market_analyzer_route import route_market_analyzer_request


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _normalize_market_panel(panel: Dict[str, Any]) -> Dict[str, Any]:
    price = _safe_float(
        panel.get("reference_price")
        or panel.get("price_at_closeout")
        or panel.get("price")
    )

    if price is not None:
        panel["reference_price"] = price
        panel["price_at_closeout"] = price
        if panel.get("price") is None:
            panel["price"] = price

    return panel


def _merge_market_panels(
    builder_panel: Dict[str, Any],
    merged_panel: Dict[str, Any],
) -> Dict[str, Any]:
    output = deepcopy(builder_panel or {})

    for key, value in (merged_panel or {}).items():
        if value is not None and output.get(key) is None:
            output[key] = value

    return _normalize_market_panel(output)


def _merge_payload_and_runtime(payload: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(runtime or {})

    for key in [
        "symbol",
        "headline",
        "price_change_pct",
        "price",
        "sector",
        "confirmation",
        "event_theme",
        "market_regime",
        "macro_bias",
        "request_id",
        "approval_required",
        "execution_allowed",
        "route_mode",
        "reference_price",
        "price_at_closeout",
    ]:
        if payload.get(key) is not None:
            merged[key] = payload[key]

    market_panel = deepcopy(runtime.get("market_panel") or {})
    payload_market_panel = deepcopy(payload.get("market_panel") or {})

    for key, value in payload_market_panel.items():
        if value is not None:
            market_panel[key] = value

    merged["market_panel"] = _normalize_market_panel(market_panel)
    return merged


def _derive_event_theme(merged: Dict[str, Any]) -> str:
    explicit = str(merged.get("event_theme") or "").strip()
    if explicit:
        return explicit

    runtime_panel = merged.get("runtime_panel")
    if isinstance(runtime_panel, dict):
        panel_theme = str(runtime_panel.get("event_theme") or "").strip()
        if panel_theme:
            return panel_theme

    market_panel = merged.get("market_panel")
    if isinstance(market_panel, dict):
        panel_theme = str(market_panel.get("event_theme") or "").strip()
        if panel_theme:
            return panel_theme

    headline = str(merged.get("headline") or "").lower()

    if "energy" in headline:
        return "energy_rebound"
    if "oil" in headline or "gas" in headline:
        return "energy_supply_shock"
    if "tech" in headline or "ai" in headline:
        return "tech_momentum"
    if "inflation" in headline:
        return "inflation_pressure"
    if "rate" in headline or "fed" in headline:
        return "rate_shift"

    return "unknown_event"


def run_operator_dashboard(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {"request_id": str(payload or "unknown")}

    request_id = payload.get("request_id") or "unknown"

    runtime = payload.get("runtime_result")
    if not runtime:
        packet = build_canonical_live_pm_packet(payload, request_id)
        runtime = route_market_analyzer_request(packet)

    merged = _merge_payload_and_runtime(payload, runtime)

    dashboard = build_operator_dashboard(merged)

    dashboard["governance_panel"] = {
        "approval_required": merged.get("approval_required", True),
        "execution_allowed": merged.get("execution_allowed", False),
        "route_path": merged.get("route_mode", "pm_route"),
    }

    builder_market_panel = dashboard.get("market_panel", {})
    merged_market_panel = merged.get("market_panel", {})

    dashboard["market_panel"] = _merge_market_panels(
        builder_market_panel,
        merged_market_panel,
    )

    event_theme = _derive_event_theme(merged)

    dashboard["event_theme"] = event_theme
    dashboard["expected_behavior"] = event_theme.replace("_", " ")

    if "runtime_panel" not in dashboard or not isinstance(dashboard["runtime_panel"], dict):
        dashboard["runtime_panel"] = {}

    dashboard["runtime_panel"]["event_theme"] = event_theme
    dashboard["market_panel"]["event_theme"] = event_theme

    if merged.get("headline") is not None and dashboard["market_panel"].get("headline") is None:
        dashboard["market_panel"]["headline"] = merged.get("headline")

    if merged.get("symbol") is not None:
        dashboard["symbol"] = merged.get("symbol")
        if dashboard["market_panel"].get("symbol") is None:
            dashboard["market_panel"]["symbol"] = merged.get("symbol")

        case_panel = dashboard.get("case_panel")
        if isinstance(case_panel, dict) and case_panel.get("symbol") is None:
            case_panel["symbol"] = merged.get("symbol")

    if merged.get("reference_price") is not None:
        dashboard["reference_price"] = merged.get("reference_price")
        if dashboard["market_panel"].get("reference_price") is None:
            dashboard["market_panel"]["reference_price"] = merged.get("reference_price")
        if dashboard["market_panel"].get("price_at_closeout") is None:
            dashboard["market_panel"]["price_at_closeout"] = merged.get("reference_price")

    if merged.get("market_regime") is not None:
        dashboard["runtime_panel"]["market_regime"] = merged.get("market_regime")
        dashboard["market_panel"]["market_regime"] = merged.get("market_regime")

    if merged.get("macro_bias") is not None:
        dashboard["runtime_panel"]["macro_bias"] = merged.get("macro_bias")
        dashboard["market_panel"]["macro_bias"] = merged.get("macro_bias")

    watcher = run_pre_interface_watcher(dashboard)
    dashboard["pre_interface_watcher"] = watcher

    smi = record_pre_interface_exposure(dashboard, watcher)
    dashboard["pre_interface_smi"] = smi

    return dashboard