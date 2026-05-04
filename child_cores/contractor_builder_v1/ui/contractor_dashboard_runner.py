"""
Contractor dashboard runner for contractor_builder_v1.

This module coordinates payload assembly and bounded explanation for the contractor
dashboard runtime. It is read-only runtime assembly only.

It owns:
- operator payload assembly orchestration
- dashboard-facing enrichments
- explanation attachment
- final dashboard view shaping

It does NOT:
- mutate workflow truth
- infer approvals
- compute workflow readiness
- advance phases
- override structured source data
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..explanation.operator_explainer import build_contractor_operator_explanation
from ..projection.operator_projection_runtime import build_contractor_operator_payload
from .contractor_dashboard_builder import build_contractor_dashboard_view
from .dashboard_enrichment import enrich_dashboard


def _normalize_mapping(value: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _normalize_list_of_mappings(value: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _normalize_signoff_status(value: Any) -> str:
    cleaned = str(value or "").strip()
    return cleaned or "not_requested"


def _build_checklist_panel(
    *,
    checklist_summary: Optional[Dict[str, Any]],
    checklist_items: Optional[List[Dict[str, Any]]],
) -> Dict[str, Any]:
    return {
        "summary": _normalize_mapping(checklist_summary),
        "items": _normalize_list_of_mappings(checklist_items),
    }


def run_contractor_dashboard(
    *,
    request_id: str,
    project_profile: Dict[str, Any],
    baseline_lock: Dict[str, Any],
    workflow_snapshot: Dict[str, Any],
    latest_project_report: Dict[str, Any],
    portfolio_report: Dict[str, Any] | None = None,
    decision_records: List[Dict[str, Any]] | None = None,
    change_records: List[Dict[str, Any]] | None = None,
    compliance_snapshot: Dict[str, Any] | None = None,
    risk_records: List[Dict[str, Any]] | None = None,
    phase_signoff_status: str = "not_requested",
    checklist_summary: Dict[str, Any] | None = None,
    checklist_items: List[Dict[str, Any]] | None = None,
    latest_delivery_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Build the full contractor dashboard runtime payload.

    This runner remains read-only. It assembles the operator payload, applies
    bounded dashboard-facing enrichments, generates explanation, and returns the
    final dashboard view model.

    Important:
    - source branches remain authoritative
    - dashboard enrichments are visibility-only
    - no workflow or signoff truth is created here
    """
    operator_payload = build_contractor_operator_payload(
        request_id=request_id,
        project_profile=_normalize_mapping(project_profile),
        baseline_lock=_normalize_mapping(baseline_lock),
        workflow_snapshot=_normalize_mapping(workflow_snapshot),
        latest_project_report=_normalize_mapping(latest_project_report),
        portfolio_report=_normalize_mapping(portfolio_report),
        decision_records=_normalize_list_of_mappings(decision_records),
        change_records=_normalize_list_of_mappings(change_records),
        compliance_snapshot=_normalize_mapping(compliance_snapshot),
        risk_records=_normalize_list_of_mappings(risk_records),
    )

    project_panel = _normalize_mapping(operator_payload.get("project_panel", {}))
    project_panel["phase_signoff_status"] = _normalize_signoff_status(phase_signoff_status)
    operator_payload["project_panel"] = project_panel

    operator_payload["checklist_panel"] = _build_checklist_panel(
        checklist_summary=checklist_summary,
        checklist_items=checklist_items,
    )

    operator_payload = enrich_dashboard(
        operator_payload=operator_payload,
        phase_signoff_status=_normalize_signoff_status(phase_signoff_status),
        checklist_summary=checklist_summary,
        latest_delivery_record=latest_delivery_record,
    )

    explanation = build_contractor_operator_explanation(operator_payload)

    return build_contractor_dashboard_view(
        operator_payload=operator_payload,
        explanation=explanation,
    )