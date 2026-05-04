from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.project_intake.baseline_lock_runtime import (
    create_baseline_lock_record,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.project_intake_receipt_builder import (
    build_project_intake_receipt,
    write_project_intake_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.project_intake_schema import (
    build_project_intake_payload,
    validate_project_intake_payload,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.project_profile import (
    create_project_profile_record,
)
from AI_GO.child_cores.contractor_builder_v1.ui.project_record_builder import (
    build_persistent_project_record_view,
)
from AI_GO.child_cores.contractor_builder_v1.ui.project_record_runtime import (
    load_project_record,
)


PROJECT_INTAKE_RUNNER_VERSION = "northstar_project_intake_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_slug(value: Any, *, fallback: str = "project", max_len: int = 80) -> str:
    raw = _safe_str(value).lower()
    chars = []

    for char in raw:
        if char.isalnum():
            chars.append(char)
        elif char in {" ", "_", "-", ".", "/", "\\", ":"}:
            chars.append("-")

    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")

    slug = slug or fallback
    return slug[:max_len].strip("-") or fallback


def _build_project_id(form_payload: Dict[str, Any]) -> str:
    supplied_project_id = _safe_slug(form_payload.get("project_id"), fallback="")
    if supplied_project_id:
        return supplied_project_id

    project_name = _safe_slug(form_payload.get("project_name"), fallback="contractor-project")
    return f"project-{project_name}-{_utc_now_compact()}"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "project_creation",
        "mutation_class": "root_project_state_creation",
        "execution_allowed": False,
        "state_mutation_allowed": True,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": True,
        "authority_mutation_allowed": False,
        "advisory_only": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "governed_project_creation": True,
        "can_execute": False,
        "can_mutate_workflow_state": False,
        "can_mutate_pm_authority": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_override_state_authority": False,
        "can_override_cross_core_integrity": False,
    }


def _build_baseline_refs() -> Dict[str, str]:
    stamp = _utc_now_compact()

    return {
        "schedule_baseline_id": f"schedule-baseline-{stamp}",
        "budget_baseline_id": f"budget-baseline-{stamp}",
        "compliance_snapshot_id": f"compliance-snapshot-{stamp}",
    }


def create_project_from_form(form_payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(form_payload, dict):
        raise ValueError("form_payload must be a dict")

    baseline_refs = _build_baseline_refs()

    intake_payload = build_project_intake_payload(
        project_name=_safe_str(form_payload.get("project_name")),
        project_type=_safe_str(form_payload.get("project_type")),
        project_description=_safe_str(form_payload.get("project_description")),
        client_name=_safe_str(form_payload.get("client_name")),
        client_contact=_safe_str(form_payload.get("client_email")),
        pm_name=_safe_str(form_payload.get("pm_name")),
        pm_contact=_safe_str(form_payload.get("pm_email")),
        site_address=_safe_str(form_payload.get("site_address")),
        portfolio_id=_safe_str(form_payload.get("portfolio_id")),
        jurisdiction={
            "jurisdiction_id": "-".join(
                part.lower()
                for part in [
                    _safe_str(form_payload.get("city")),
                    _safe_str(form_payload.get("state")),
                ]
                if part
            ),
            "authority_name": _safe_str(form_payload.get("authority_name")),
            "city": _safe_str(form_payload.get("city")),
            "county": _safe_str(form_payload.get("county")),
            "state": _safe_str(form_payload.get("state")),
        },
        baseline_refs=baseline_refs,
        oracle_snapshot_id="",
        exposure_profile_id="",
        notes=_safe_str(form_payload.get("notes")),
    )

    validation_errors = validate_project_intake_payload(intake_payload)
    if validation_errors:
        raise ValueError("Project intake validation failed: " + "; ".join(validation_errors))

    project_id = _build_project_id(form_payload)

    project_profile = create_project_profile_record(
        project_id=project_id,
        project_name=_safe_str(form_payload.get("project_name")),
        project_type=_safe_str(form_payload.get("project_type")),
        project_description=_safe_str(form_payload.get("project_description")),
        client_name=_safe_str(form_payload.get("client_name")),
        client_email=_safe_str(form_payload.get("client_email")),
        pm_name=_safe_str(form_payload.get("pm_name")),
        pm_email=_safe_str(form_payload.get("pm_email")),
        site_address=_safe_str(form_payload.get("site_address")),
        city=_safe_str(form_payload.get("city")),
        county=_safe_str(form_payload.get("county")),
        state=_safe_str(form_payload.get("state")),
        authority_name=_safe_str(form_payload.get("authority_name")),
        portfolio_id=_safe_str(form_payload.get("portfolio_id")),
        notes=_safe_str(form_payload.get("notes")),
    )

    project_id = _safe_str(project_profile.get("project_id"))
    if not project_id:
        raise ValueError("project_id missing after project profile creation")

    baseline_lock = create_baseline_lock_record(
        project_id=project_id,
        project_name=_safe_str(project_profile.get("project_name")),
        created_by="project_intake_runner",
        notes=_safe_str(form_payload.get("notes")),
    )

    project_profile_path = (
        f"AI_GO/state/contractor_builder_v1/projects/by_project/"
        f"{project_id}/project_profile.json"
    )
    baseline_lock_path = (
        f"AI_GO/state/contractor_builder_v1/projects/by_project/"
        f"{project_id}/project_intake/baseline_lock.json"
    )

    create_project_receipt = build_project_intake_receipt(
        event_type="create_project",
        project_id=project_id,
        artifact_path=project_profile_path,
        details={
            "project_name": project_profile.get("project_name"),
            "mutation_class": "root_project_state_creation",
        },
    )
    create_project_receipt_path = write_project_intake_receipt(create_project_receipt)

    lock_baseline_receipt = build_project_intake_receipt(
        event_type="lock_baseline",
        project_id=project_id,
        artifact_path=baseline_lock_path,
        details={
            "baseline_refs": baseline_refs,
            "mutation_class": "root_project_state_creation",
        },
    )
    lock_baseline_receipt_path = write_project_intake_receipt(lock_baseline_receipt)

    project_record = load_project_record(project_id)
    created_view = build_persistent_project_record_view(
        project_record=project_record,
    )

    return {
        "status": "created",
        "artifact_type": "contractor_project_intake_result",
        "artifact_version": PROJECT_INTAKE_RUNNER_VERSION,
        "created_at": _utc_now_iso(),
        "project_id": project_id,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "project_profile": project_profile,
        "baseline_lock": baseline_lock,
        "baseline_refs": baseline_refs,
        "created_view": created_view,
        "artifact_paths": {
            "project_profile": project_profile_path,
            "baseline_lock": baseline_lock_path,
        },
        "receipt_paths": {
            "create_project": str(create_project_receipt_path),
            "lock_baseline": str(lock_baseline_receipt_path),
        },
        "sealed": True,
    }