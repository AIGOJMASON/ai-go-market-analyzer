from __future__ import annotations

from typing import Any, Dict, List


def _render_panel(title: str) -> str:
    return f"\n=== {title} ==="


def _render_kv(data: Dict[str, Any], keys: List[str]) -> List[str]:
    lines: List[str] = []
    for key in keys:
        lines.append(f"{key}: {data.get(key)}")
    return lines


def render_dashboard_to_text(dashboard_output: Dict[str, Any], watcher_result: Dict[str, Any]) -> str:
    views = dashboard_output.get("views", {})

    market_regime = views.get("market_regime", {})
    active_events = views.get("active_events", {})
    watchlist = views.get("watchlist", {})
    recommendations = views.get("recommendations", {})
    approval_gate = views.get("approval_gate", {})
    receipt_trace = views.get("receipt_trace", {})

    lines: List[str] = []
    lines.append("MARKET_ANALYZER_V1 LIVE TEST")
    lines.append(f"status: {dashboard_output.get('status')}")
    lines.append(f"watcher_passed: {watcher_result.get('watcher_passed')}")

    lines.append(_render_panel("Market Regime"))
    lines.extend(_render_kv(
        market_regime,
        ["regime", "trade_posture", "trade_allowed", "volatility_level", "liquidity_level", "stress_level"],
    ))

    lines.append(_render_panel("Active Event"))
    lines.extend(_render_kv(
        active_events,
        ["event_id", "event_type", "shock_confirmed", "propagation_speed", "ripple_depth"],
    ))

    lines.append(_render_panel("Watchlist"))
    lines.append(f"count: {watchlist.get('count', 0)}")
    for item in watchlist.get("items", []):
        lines.append(
            f"- {item.get('symbol')} | sector={item.get('sector')} | "
            f"liq={item.get('liquidity')} | "
            f"stabilization={item.get('stabilization')} | "
            f"reclaim={item.get('reclaim')} | "
            f"confirmation={item.get('confirmation')}"
        )

    lines.append(_render_panel("Recommendations"))
    lines.append(f"count: {recommendations.get('count', 0)}")
    for item in recommendations.get("items", []):
        lines.append(
            f"- {item.get('symbol')} | sector={item.get('sector')} | "
            f"entry={item.get('entry_signal')} | "
            f"exit={item.get('exit_rule')} | "
            f"horizon_hours={item.get('time_horizon_hours')} | "
            f"approval_required={item.get('approval_required')}"
        )

    lines.append(_render_panel("Approval Gate"))
    lines.extend(_render_kv(
        approval_gate,
        ["approval_type", "recommendation_count", "execution_allowed", "trace_reference"],
    ))

    lines.append(_render_panel("Receipt Trace"))
    lines.append(f"upstream_receipt: {receipt_trace.get('upstream_receipt')}")
    lines.append(f"trace: {receipt_trace.get('trace')}")

    return "\n".join(lines)