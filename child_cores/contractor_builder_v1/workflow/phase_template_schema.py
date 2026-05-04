"""
Phase template schema for contractor_builder_v1.

Phase templates are reusable blueprints for project phases by project_type.
They define expected duration, dependencies, role expectations, checkpoints,
and optional client gate requirements.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

PHASE_TEMPLATE_SCHEMA_VERSION = "v1"


def build_phase_template(
    *,
    template_id: str,
    project_type: str,
    phase_name: str,
    expected_duration_days: int,
    dependencies: Optional[List[str]] = None,
    crew_expectations: Optional[List[str]] = None,
    management_expectations: Optional[List[str]] = None,
    management_checkpoints: Optional[List[str]] = None,
    client_gate_required: bool = False,
    client_gate_checklist: Optional[List[str]] = None,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical phase template.
    """
    return {
        "schema_version": PHASE_TEMPLATE_SCHEMA_VERSION,
        "template_id": template_id,
        "project_type": project_type,
        "phase_name": phase_name,
        "expected_duration_days": expected_duration_days,
        "dependencies": list(dependencies or []),
        "role_expectations": {
            "crew": list(crew_expectations or []),
            "management": list(management_expectations or []),
        },
        "management_checkpoints": list(management_checkpoints or []),
        "client_gate_requirement": {
            "required": client_gate_required,
            "checklist": list(client_gate_checklist or []),
        },
        "notes": notes,
    }


def validate_phase_template(template: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required phase template shape.
    """
    errors: List[str] = []

    required_fields = [
        "template_id",
        "project_type",
        "phase_name",
        "expected_duration_days",
        "dependencies",
        "role_expectations",
        "management_checkpoints",
        "client_gate_requirement",
    ]
    for field in required_fields:
        if field not in template:
            errors.append(f"Missing required phase template field: {field}")

    if not template.get("template_id"):
        errors.append("template_id may not be empty")
    if not template.get("project_type"):
        errors.append("project_type may not be empty")
    if not template.get("phase_name"):
        errors.append("phase_name may not be empty")

    duration = template.get("expected_duration_days")
    if not isinstance(duration, int) or duration <= 0:
        errors.append("expected_duration_days must be a positive integer")

    role_expectations = template.get("role_expectations", {})
    if not isinstance(role_expectations, dict):
        errors.append("role_expectations must be a mapping")
    else:
        if "crew" not in role_expectations:
            errors.append("role_expectations.crew is required")
        if "management" not in role_expectations:
            errors.append("role_expectations.management is required")

    client_gate_requirement = template.get("client_gate_requirement", {})
    if not isinstance(client_gate_requirement, dict):
        errors.append("client_gate_requirement must be a mapping")
    else:
        if "required" not in client_gate_requirement:
            errors.append("client_gate_requirement.required is required")
        if "checklist" not in client_gate_requirement:
            errors.append("client_gate_requirement.checklist is required")

    return errors


def get_phase_template_template() -> Dict[str, Any]:
    """
    Return an empty phase template shape.
    """
    return deepcopy(
        {
            "schema_version": PHASE_TEMPLATE_SCHEMA_VERSION,
            "template_id": "",
            "project_type": "",
            "phase_name": "",
            "expected_duration_days": 1,
            "dependencies": [],
            "role_expectations": {
                "crew": [],
                "management": [],
            },
            "management_checkpoints": [],
            "client_gate_requirement": {
                "required": False,
                "checklist": [],
            },
            "notes": "",
        }
    )