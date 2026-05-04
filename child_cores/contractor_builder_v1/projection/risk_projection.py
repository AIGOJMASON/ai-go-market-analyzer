"""
Risk projection for contractor_builder_v1.

This module builds a bounded risk summary panel from risk records.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_risk_projection(
    *,
    risk_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a bounded risks panel.
    """
    open_or_monitoring = [
        record for record in risk_records
        if str(record.get("status", "")).strip() in {"Open", "Monitoring"}
    ]
    occurred = [
        record for record in risk_records
        if str(record.get("status", "")).strip() == "Occurred"
    ]

    latest_items = [
        {
            "risk_id": record.get("risk_id", ""),
            "category": record.get("category", ""),
            "status": record.get("status", ""),
            "probability": record.get("probability", ""),
            "impact_level": record.get("impact_level", ""),
            "mitigation_owner": record.get("mitigation_owner", ""),
        }
        for record in risk_records[-5:]
    ]

    return {
        "risk_count": len(risk_records),
        "open_or_monitoring_count": len(open_or_monitoring),
        "occurred_count": len(occurred),
        "latest_items": latest_items,
    }