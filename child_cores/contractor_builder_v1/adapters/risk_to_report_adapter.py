"""
Risk to report adapter for contractor_builder_v1.

This adapter compresses risk records into a bounded reporting snapshot.
It does not score risk numerically or mutate risk state.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_risk_report_snapshot(
    *,
    risk_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a bounded risk snapshot for reporting.
    """
    open_risks = [
        record for record in risk_records
        if record.get("status") == "Open"
    ]
    monitoring_risks = [
        record for record in risk_records
        if record.get("status") == "Monitoring"
    ]
    occurred_risks = [
        record for record in risk_records
        if record.get("status") == "Occurred"
    ]
    high_impact_open = [
        record for record in risk_records
        if record.get("status") in {"Open", "Monitoring"}
        and record.get("impact_level") == "High"
    ]

    return {
        "risk_count": len(risk_records),
        "open_count": len(open_risks),
        "monitoring_count": len(monitoring_risks),
        "occurred_count": len(occurred_risks),
        "high_impact_open_or_monitoring_count": len(high_impact_open),
    }