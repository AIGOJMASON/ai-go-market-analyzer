"""
Shared pre-interface validation contract for contractor_builder_v1.

This module owns the final dashboard payload validation rules used before
operator exposure.

Authority:
- This file validates payload shape and advisory governance invariants.
- API routes may call this file but must not duplicate its rules.
- This file must not mutate payloads, workflow state, signoff state, receipts,
  visibility state, or dashboard output.
"""

from __future__ import annotations

from typing import Any, Dict, List


REQUIRED_CONTRACTOR_DASHBOARD_FIELDS: tuple[str, ...] = (
    "generated_at",
    "request_id",
    "child_core_id",
    "mode",
    "approval_required",
    "execution_allowed",
    "summary_panel",
    "project_panel",
    "decisions_panel",
    "changes_panel",
    "compliance_panel",
    "risks_panel",
    "explanation_panel",
)


def validate_contractor_dashboard_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not isinstance(payload, dict):
        return ["payload must be a mapping"]

    for field in REQUIRED_CONTRACTOR_DASHBOARD_FIELDS:
        if field not in payload:
            errors.append(f"Missing required payload field: {field}")

    if payload.get("mode") != "advisory":
        errors.append("mode must remain advisory")

    if payload.get("execution_allowed") is not False:
        errors.append("execution_allowed must be false")

    if payload.get("approval_required") is not True:
        errors.append("approval_required must be true")

    for panel_name in (
        "summary_panel",
        "project_panel",
        "compliance_panel",
        "explanation_panel",
    ):
        if not isinstance(payload.get(panel_name, {}), dict):
            errors.append(f"{panel_name} must be a mapping")

    return errors


def build_pre_interface_validation_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    errors = validate_contractor_dashboard_payload(payload)
    return {
        "status": "ok" if not errors else "invalid",
        "valid": len(errors) == 0,
        "errors": errors,
    }