"""
Phase instance schema for contractor_builder_v1.

Phase instances are project-bound realizations of reusable phase templates.
They represent the live phase state used by workflow, change, router, report,
and signoff logic.

This module owns:
- canonical phase instance construction
- minimum shape validation
- shared phase-status authority exposure

It does NOT:
- advance workflow
- compute checklist readiness
- determine client signoff status
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from ..governance.shared_enums import SHARED_ENUMS

PHASE_INSTANCE_SCHEMA_VERSION = "v1"

PHASE_STATUS_ENUM = list(SHARED_ENUMS["phase_status"])


def _validate_required_text(value: str, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _normalize_optional_text(value: Any) -> str:
    return str(value or "").strip()


def _coerce_string_list(values: Optional[List[Any]]) -> List[str]:
    return [
        str(item).strip()
        for item in list(values or [])
        if str(item).strip()
    ]


def _build_role_expectations(
    *,
    crew_expectations: Optional[List[Any]] = None,
    management_expectations: Optional[List[Any]] = None,
) -> Dict[str, List[str]]:
    return {
        "crew": _coerce_string_list(crew_expectations),
        "management": _coerce_string_list(management_expectations),
    }


def _build_client_gate_requirement(
    *,
    client_gate_required: bool,
    client_gate_checklist: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    required = bool(client_gate_required)
    checklist = _coerce_string_list(client_gate_checklist)

    return {
        "required": required,
        "checklist": checklist,
        "status": "not_required" if not required else "pending",
    }


def _build_drift_block() -> Dict[str, Any]:
    return {
        "schedule_drift_days": 0,
        "dead_time_hours_estimate": 0.0,
        "dead_time_risk_label": "",
    }


def build_phase_instance(
    *,
    phase_id: str,
    project_id: str,
    template_id: str,
    phase_name: str,
    expected_duration_days: int,
    dependencies: Optional[List[str]] = None,
    crew_expectations: Optional[List[str]] = None,
    management_expectations: Optional[List[str]] = None,
    management_checkpoints: Optional[List[str]] = None,
    client_gate_required: bool = False,
    client_gate_checklist: Optional[List[str]] = None,
    planned_start_date: str = "",
    planned_end_date: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical phase instance.

    New instances are created in `not_started` state. Workflow runtime is responsible
    for activating the first phase and governing later transitions.
    """
    phase_id_clean = _validate_required_text(phase_id, "phase_id")
    project_id_clean = _validate_required_text(project_id, "project_id")
    template_id_clean = _validate_required_text(template_id, "template_id")
    phase_name_clean = _validate_required_text(phase_name, "phase_name")

    if not isinstance(expected_duration_days, int) or expected_duration_days <= 0:
        raise ValueError("expected_duration_days must be a positive integer")

    return {
        "schema_version": PHASE_INSTANCE_SCHEMA_VERSION,
        "phase_id": phase_id_clean,
        "project_id": project_id_clean,
        "template_id": template_id_clean,
        "phase_name": phase_name_clean,
        "phase_status": "not_started",
        "expected_duration_days": expected_duration_days,
        "actual_duration_days": None,
        "dependencies": _coerce_string_list(dependencies),
        "planned_start_date": _normalize_optional_text(planned_start_date),
        "planned_end_date": _normalize_optional_text(planned_end_date),
        "actual_start_date": "",
        "actual_end_date": "",
        "role_expectations": _build_role_expectations(
            crew_expectations=crew_expectations,
            management_expectations=management_expectations,
        ),
        "management_checkpoints": _coerce_string_list(management_checkpoints),
        "client_gate_requirement": _build_client_gate_requirement(
            client_gate_required=client_gate_required,
            client_gate_checklist=client_gate_checklist,
        ),
        "drift": _build_drift_block(),
        "notes": _normalize_optional_text(notes),
        "allowed_phase_statuses": list(PHASE_STATUS_ENUM),
    }


def validate_phase_instance(instance: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required phase instance shape.
    """
    errors: List[str] = []

    if not isinstance(instance, dict):
        return ["phase instance must be a mapping"]

    required_fields = [
        "phase_id",
        "project_id",
        "template_id",
        "phase_name",
        "phase_status",
        "expected_duration_days",
        "dependencies",
        "role_expectations",
        "management_checkpoints",
        "client_gate_requirement",
        "drift",
    ]
    for field in required_fields:
        if field not in instance:
            errors.append(f"Missing required phase instance field: {field}")

    if errors:
        return errors

    if not str(instance.get("phase_id", "")).strip():
        errors.append("phase_id may not be empty")
    if not str(instance.get("project_id", "")).strip():
        errors.append("project_id may not be empty")
    if not str(instance.get("template_id", "")).strip():
        errors.append("template_id may not be empty")
    if not str(instance.get("phase_name", "")).strip():
        errors.append("phase_name may not be empty")

    duration = instance.get("expected_duration_days")
    if not isinstance(duration, int) or duration <= 0:
        errors.append("expected_duration_days must be a positive integer")

    actual_duration = instance.get("actual_duration_days")
    if actual_duration is not None and (
        not isinstance(actual_duration, int) or actual_duration < 0
    ):
        errors.append("actual_duration_days must be null or a non-negative integer")

    phase_status = str(instance.get("phase_status", "")).strip()
    if phase_status not in PHASE_STATUS_ENUM:
        errors.append(f"phase_status must be one of {PHASE_STATUS_ENUM}")

    dependencies = instance.get("dependencies")
    if not isinstance(dependencies, list):
        errors.append("dependencies must be a list")
    else:
        for dependency in dependencies:
            if not str(dependency).strip():
                errors.append("dependencies may not contain empty values")
                break

    role_expectations = instance.get("role_expectations", {})
    if not isinstance(role_expectations, dict):
        errors.append("role_expectations must be a mapping")
    else:
        if "crew" not in role_expectations:
            errors.append("role_expectations.crew is required")
        elif not isinstance(role_expectations.get("crew"), list):
            errors.append("role_expectations.crew must be a list")

        if "management" not in role_expectations:
            errors.append("role_expectations.management is required")
        elif not isinstance(role_expectations.get("management"), list):
            errors.append("role_expectations.management must be a list")

    management_checkpoints = instance.get("management_checkpoints")
    if not isinstance(management_checkpoints, list):
        errors.append("management_checkpoints must be a list")

    client_gate_requirement = instance.get("client_gate_requirement", {})
    if not isinstance(client_gate_requirement, dict):
        errors.append("client_gate_requirement must be a mapping")
    else:
        if "required" not in client_gate_requirement:
            errors.append("client_gate_requirement.required is required")
        elif not isinstance(client_gate_requirement.get("required"), bool):
            errors.append("client_gate_requirement.required must be a boolean")

        if "checklist" not in client_gate_requirement:
            errors.append("client_gate_requirement.checklist is required")
        elif not isinstance(client_gate_requirement.get("checklist"), list):
            errors.append("client_gate_requirement.checklist must be a list")

        if "status" not in client_gate_requirement:
            errors.append("client_gate_requirement.status is required")
        else:
            status_value = str(client_gate_requirement.get("status", "")).strip()
            if status_value not in {"not_required", "pending", "approved", "denied"}:
                errors.append(
                    "client_gate_requirement.status must be one of "
                    "['not_required', 'pending', 'approved', 'denied']"
                )

    drift = instance.get("drift", {})
    if not isinstance(drift, dict):
        errors.append("drift must be a mapping")
    else:
        schedule_drift_days = drift.get("schedule_drift_days")
        if not isinstance(schedule_drift_days, int):
            errors.append("drift.schedule_drift_days must be an integer")

        dead_time_hours_estimate = drift.get("dead_time_hours_estimate")
        if not isinstance(dead_time_hours_estimate, (int, float)):
            errors.append("drift.dead_time_hours_estimate must be numeric")

        if "dead_time_risk_label" not in drift:
            errors.append("drift.dead_time_risk_label is required")

    allowed_phase_statuses = instance.get("allowed_phase_statuses")
    if allowed_phase_statuses is not None:
        if not isinstance(allowed_phase_statuses, list):
            errors.append("allowed_phase_statuses must be a list when present")
        elif list(allowed_phase_statuses) != PHASE_STATUS_ENUM:
            errors.append(
                f"allowed_phase_statuses must match canonical enum {PHASE_STATUS_ENUM}"
            )

    return errors


def get_phase_instance_template() -> Dict[str, Any]:
    """
    Return an empty phase instance shape.
    """
    return deepcopy(
        {
            "schema_version": PHASE_INSTANCE_SCHEMA_VERSION,
            "phase_id": "",
            "project_id": "",
            "template_id": "",
            "phase_name": "",
            "phase_status": "not_started",
            "expected_duration_days": 1,
            "actual_duration_days": None,
            "dependencies": [],
            "planned_start_date": "",
            "planned_end_date": "",
            "actual_start_date": "",
            "actual_end_date": "",
            "role_expectations": {
                "crew": [],
                "management": [],
            },
            "management_checkpoints": [],
            "client_gate_requirement": {
                "required": False,
                "checklist": [],
                "status": "not_required",
            },
            "drift": {
                "schedule_drift_days": 0,
                "dead_time_hours_estimate": 0.0,
                "dead_time_risk_label": "",
            },
            "notes": "",
            "allowed_phase_statuses": list(PHASE_STATUS_ENUM),
        }
    )