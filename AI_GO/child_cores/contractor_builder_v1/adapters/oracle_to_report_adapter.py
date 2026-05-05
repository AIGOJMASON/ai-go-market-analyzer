"""
Oracle to report adapter for contractor_builder_v1.

This adapter translates oracle radar and projection outputs into a bounded report
snapshot. It does not forecast, execute procurement, or mutate project truth.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_oracle_report_snapshot(
    *,
    risk_radar: Dict[str, Any],
    procurement_advisories: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    Build a bounded oracle report snapshot.
    """
    procurement_advisories = procurement_advisories or []

    escalate_count = sum(
        1
        for advisory in procurement_advisories
        if advisory.get("procurement_posture") == "Escalate_For_PM"
    )
    advance_buy_count = sum(
        1
        for advisory in procurement_advisories
        if advisory.get("procurement_posture") == "Advance_Buy"
    )

    return {
        "summary_label": risk_radar.get("summary_label", ""),
        "high_domains": list(risk_radar.get("high_domains", [])),
        "moderate_domains": list(risk_radar.get("moderate_domains", [])),
        "low_domains": list(risk_radar.get("low_domains", [])),
        "high_domain_count": len(risk_radar.get("high_domains", [])),
        "moderate_domain_count": len(risk_radar.get("moderate_domains", [])),
        "escalate_for_pm_count": escalate_count,
        "advance_buy_count": advance_buy_count,
    }