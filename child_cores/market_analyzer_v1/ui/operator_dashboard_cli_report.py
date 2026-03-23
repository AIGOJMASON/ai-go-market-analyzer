from __future__ import annotations

from typing import Any, Dict, List


def render_operator_dashboard_cli(dashboard: Dict[str, Any]) -> str:
    case_panel = dashboard["case_panel"]
    market_panel = dashboard["market_panel"]
    candidate_panel = dashboard["candidate_panel"]
    recommendation_panel = dashboard["recommendation_panel"]
    governance_panel = dashboard["governance_panel"]
    rejection_panel = dashboard["rejection_panel"]

    lines: List[str] = []
    lines.append("")
    lines.append("=== MARKET ANALYZER V1 ===")
    lines.append("")
    lines.append(f"Case ID: {case_panel['case_id']}")
    lines.append(f"Title: {case_panel['title']}")
    lines.append(f"Observed At: {case_panel['observed_at']}")
    lines.append(f"Route Mode: {dashboard['route_mode']}")
    lines.append(f"Status: {dashboard['status']}")
    lines.append("")
    lines.append(f"Regime: {market_panel['market_regime']}")
    lines.append(f"Event: {market_panel['event_theme']}")
    lines.append(f"Macro Bias: {market_panel['macro_bias']}")
    lines.append(f"Headline: {market_panel['headline']}")
    lines.append(f"Candidates: {candidate_panel['symbols']}")
    lines.append(f"Recommendations: {recommendation_panel['recommendation_count']}")
    lines.append("")

    if recommendation_panel["recommendations"]:
        lines.append("--- Recommendation Detail ---")
        for recommendation in recommendation_panel["recommendations"]:
            lines.append(f"Symbol: {recommendation['symbol']}")
            lines.append(f"Entry: {recommendation['entry']}")
            lines.append(f"Exit: {recommendation['exit']}")
            lines.append(f"Confidence: {recommendation['confidence']}")
            lines.append("")

    if rejection_panel["rejected"]:
        lines.append("--- Rejection Detail ---")
        lines.append(f"Reason: {rejection_panel['reason']}")
        lines.append("")

    lines.append("--- System Status ---")
    lines.append(f"Watcher Passed: {governance_panel['watcher_passed']}")
    lines.append(f"Approval Required: {governance_panel['approval_required']}")
    lines.append(f"Execution Allowed: {governance_panel['execution_allowed']}")
    lines.append(f"Approval Gate: {governance_panel['approval_gate']}")
    lines.append(f"Receipt: {governance_panel['receipt_id']}")
    lines.append("")
    lines.append("============================")
    lines.append("")

    return "\n".join(lines)