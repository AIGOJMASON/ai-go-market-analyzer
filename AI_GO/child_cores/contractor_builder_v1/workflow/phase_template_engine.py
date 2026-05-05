"""
Phase template engine for contractor_builder_v1.

This module expands reusable phase templates into project-specific phase instances.

It owns:
- template validation before expansion
- deterministic project-bound phase_id generation
- template dependency translation into instance dependency phase_ids

It does NOT:
- persist workflow state
- initialize workflow on disk
- advance workflow
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..governance.identity import build_phase_id
from .phase_instance_schema import build_phase_instance
from .phase_template_schema import validate_phase_template


def _validate_required_text(value: str, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _normalize_dependency_values(values: List[Any]) -> List[str]:
    return [
        str(item).strip()
        for item in list(values or [])
        if str(item).strip()
    ]


def generate_phase_instances_from_template(
    *,
    project_id: str,
    phase_templates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Expand a list of validated phase templates into project-bound phase instances.

    Important:
    - each template gets a project-specific phase_id
    - template dependencies are translated into those generated phase_ids
    - dependency references are interpreted as template phase_name values
    """
    project_id_clean = _validate_required_text(project_id, "project_id")

    if not isinstance(phase_templates, list) or not phase_templates:
        raise ValueError("phase_templates must be a non-empty list")

    validated_templates: List[Dict[str, Any]] = []
    phase_name_to_phase_id: Dict[str, str] = {}

    # First pass:
    # validate templates and allocate deterministic project-bound phase IDs.
    for template in phase_templates:
        if not isinstance(template, dict):
            raise ValueError("Each phase template must be a mapping")

        errors = validate_phase_template(template)
        if errors:
            raise ValueError("Invalid phase template: " + "; ".join(errors))

        template_clean = dict(template)
        phase_name = _validate_required_text(
            str(template_clean["phase_name"]),
            "phase_name",
        )

        if phase_name in phase_name_to_phase_id:
            raise ValueError(
                f"Duplicate phase_name in phase_templates is not allowed: {phase_name}"
            )

        phase_name_to_phase_id[phase_name] = build_phase_id(project_id_clean, phase_name)
        validated_templates.append(template_clean)

    instances: List[Dict[str, Any]] = []

    # Second pass:
    # build live phase instances and translate dependencies into generated phase_ids.
    for template in validated_templates:
        phase_name = str(template["phase_name"]).strip()
        phase_id = phase_name_to_phase_id[phase_name]

        raw_dependencies = _normalize_dependency_values(template.get("dependencies", []))
        translated_dependencies: List[str] = []

        for dependency_name in raw_dependencies:
            if dependency_name not in phase_name_to_phase_id:
                raise ValueError(
                    f"Unknown dependency '{dependency_name}' for phase '{phase_name}'. "
                    "Dependencies must reference another template phase_name."
                )
            translated_dependencies.append(phase_name_to_phase_id[dependency_name])

        instance = build_phase_instance(
            phase_id=phase_id,
            project_id=project_id_clean,
            template_id=str(template["template_id"]).strip(),
            phase_name=phase_name,
            expected_duration_days=int(template["expected_duration_days"]),
            dependencies=translated_dependencies,
            crew_expectations=template.get("role_expectations", {}).get("crew", []),
            management_expectations=template.get("role_expectations", {}).get(
                "management", []
            ),
            management_checkpoints=template.get("management_checkpoints", []),
            client_gate_required=template.get("client_gate_requirement", {}).get(
                "required", False
            ),
            client_gate_checklist=template.get("client_gate_requirement", {}).get(
                "checklist", []
            ),
            notes=template.get("notes", ""),
        )
        instances.append(instance)

    return instances