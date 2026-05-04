"""
Contractor dashboard builder for contractor_builder_v1.

This module shapes the final read-only dashboard view from structured operator payload
and bounded explanation. It does not mutate source truth.
"""

from __future__ import annotations

from typing import Any, Dict


def build_contractor_dashboard_view(
    *,
    operator_payload: Dict[str, Any],
    explanation: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the final contractor dashboard view model.
    """
    return {
        "generated_at": operator_payload.get("generated_at", ""),
        "request_id": operator_payload.get("request_id", ""),
        "child_core_id": operator_payload.get("child_core_id", ""),
        "mode": operator_payload.get("mode", "advisory"),
        "approval_required": operator_payload.get("approval_required", True),
        "execution_allowed": operator_payload.get("execution_allowed", False),
        "summary_panel": dict(operator_payload.get("summary_panel", {})),
        "project_panel": dict(operator_payload.get("project_panel", {})),
        "portfolio_panel": dict(operator_payload.get("portfolio_panel", {})),
        "decisions_panel": dict(operator_payload.get("decisions_panel", {})),
        "changes_panel": dict(operator_payload.get("changes_panel", {})),
        "compliance_panel": dict(operator_payload.get("compliance_panel", {})),
        "risks_panel": dict(operator_payload.get("risks_panel", {})),
        "checklist_panel": dict(operator_payload.get("checklist_panel", {})),
        "signoff_summary_panel": dict(operator_payload.get("signoff_summary_panel", {})),
        "delivery_summary_panel": dict(operator_payload.get("delivery_summary_panel", {})),
        "explanation_panel": dict(explanation),
    }