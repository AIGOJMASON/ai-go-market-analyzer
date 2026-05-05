from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.governance.project_receipt_copy import (
    write_project_receipt_copy,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.client_signoff_status_runtime import (
    append_client_signoff_status,
    mark_declined,
    mark_signed,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_receipt_builder import (
    build_workflow_receipt,
    write_workflow_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_runtime import (
    reconcile_workflow_state,
)
from AI_GO.core.paths.path_resolver import get_client_signoff_status_path


def _write_signoff_receipt(
    *,
    project_id: str,
    phase_id: str,
    actor: str,
    action: str,
    status: str,
) -> Dict[str, str]:
    artifact_path = str(get_client_signoff_status_path(project_id))

    receipt = build_workflow_receipt(
        event_type="record_client_signoff",
        project_id=project_id,
        artifact_path=artifact_path,
        actor=actor,
        details={
            "phase_id": phase_id,
            "action": action,
            "status": status,
        },
    )

    global_path = str(write_workflow_receipt(receipt))
    project_path = str(
        write_project_receipt_copy(
            project_id=project_id,
            module_name="signoff",
            receipt=receipt,
        )
    )

    return {
        "global_receipt_path": global_path,
        "project_receipt_path": project_path,
    }


def execute_signoff_complete(context: Dict[str, Any]) -> Dict[str, Any]:
    project_id = context["project_id"]
    phase_id = context["phase_id"]
    actor = context["actor"]
    latest = dict(context.get("latest_signoff_status", {}))

    latest_status = str(latest.get("status", "")).strip().lower()

    if latest_status == "signed":
        return {
            "status": "already_signed",
            "noop": True,
            "signoff": latest,
            "workflow_state": context.get("workflow_state", {}),
            "current_phase_id": str(
                context.get("workflow_state", {}).get("current_phase_id", "")
            ),
            "reconciliation": {
                "changed": False,
                "receipt_paths": [],
            },
            "signoff_receipts": {},
        }

    signed = mark_signed(latest)
    status_path = append_client_signoff_status(signed)

    receipt_paths = _write_signoff_receipt(
        project_id=project_id,
        phase_id=phase_id,
        actor=actor,
        action="signed",
        status="signed",
    )

    reconciliation = reconcile_workflow_state(
        project_id=project_id,
        actor=actor,
    )

    return {
        "status": "ok",
        "noop": False,
        "signoff": signed,
        "signoff_status_path": str(status_path),
        "workflow_state": reconciliation.get("workflow_state", {}),
        "current_phase_id": reconciliation.get("current_phase_id", ""),
        "reconciliation": {
            "changed": reconciliation.get("changed", False),
            "latest_signoff_status": reconciliation.get("latest_signoff_status", {}),
            "receipt_paths": reconciliation.get("receipt_paths", []),
        },
        "signoff_receipts": receipt_paths,
    }


def execute_signoff_decline(context: Dict[str, Any]) -> Dict[str, Any]:
    project_id = context["project_id"]
    phase_id = context["phase_id"]
    actor = context["actor"]
    latest = dict(context.get("latest_signoff_status", {}))

    latest_status = str(latest.get("status", "")).strip().lower()

    if latest_status == "declined":
        return {
            "status": "already_declined",
            "noop": True,
            "signoff": latest,
            "workflow_state": context.get("workflow_state", {}),
            "current_phase_id": str(
                context.get("workflow_state", {}).get("current_phase_id", "")
            ),
            "reconciliation": {
                "changed": False,
                "receipt_paths": [],
            },
            "signoff_receipts": {},
        }

    declined = mark_declined(latest)
    status_path = append_client_signoff_status(declined)

    receipt_paths = _write_signoff_receipt(
        project_id=project_id,
        phase_id=phase_id,
        actor=actor,
        action="declined",
        status="declined",
    )

    reconciliation = reconcile_workflow_state(
        project_id=project_id,
        actor=actor,
    )

    return {
        "status": "ok",
        "noop": False,
        "signoff": declined,
        "signoff_status_path": str(status_path),
        "workflow_state": reconciliation.get("workflow_state", {}),
        "current_phase_id": reconciliation.get("current_phase_id", ""),
        "reconciliation": {
            "changed": reconciliation.get("changed", False),
            "latest_signoff_status": reconciliation.get("latest_signoff_status", {}),
            "receipt_paths": reconciliation.get("receipt_paths", []),
            "rollback_skipped": True,
            "rollback_reason": "rollback_workflow_for_declined_signoff is deprecated under current workflow_runtime",
        },
        "signoff_receipts": receipt_paths,
    }