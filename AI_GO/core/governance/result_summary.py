from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


RESULT_SUMMARY_VERSION = "v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _append_if_present(items: List[Dict[str, Any]], *, artifact_type: str, path: Any) -> None:
    clean_path = _safe_str(path)
    if clean_path:
        items.append({"artifact_type": artifact_type, "path": clean_path})


def build_result_summary(
    *,
    action: str,
    result: Dict[str, Any],
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    result_payload = _safe_dict(result)
    context_payload = _safe_dict(context)
    entry = _safe_dict(result_payload.get("entry"))

    status = _safe_str(result_payload.get("status")) or "unknown"

    artifacts_created: List[Dict[str, Any]] = []
    external_actions: List[Dict[str, Any]] = []
    state_mutations: List[Dict[str, Any]] = []

    project_id = _safe_str(
        result_payload.get("project_id")
        or entry.get("project_id")
        or context_payload.get("project_id")
    )

    phase_id = _safe_str(
        result_payload.get("phase_id")
        or entry.get("phase_id")
        or context_payload.get("phase_id")
    )

    _append_if_present(
        artifacts_created,
        artifact_type="phase_closeout_pdf_artifact_record",
        path=result_payload.get("pdf_artifact_record_path"),
    )

    document_receipts = _safe_dict(result_payload.get("document_receipts"))
    _append_if_present(
        artifacts_created,
        artifact_type="pdf_receipt_global",
        path=document_receipts.get("global_receipt_path"),
    )
    _append_if_present(
        artifacts_created,
        artifact_type="pdf_receipt_project",
        path=document_receipts.get("project_receipt_path"),
    )

    _append_if_present(
        artifacts_created,
        artifact_type="email_delivery_record",
        path=result_payload.get("email_record_path"),
    )

    delivery_receipts = _safe_dict(result_payload.get("delivery_receipts"))
    _append_if_present(
        artifacts_created,
        artifact_type="delivery_receipt_global",
        path=delivery_receipts.get("global_receipt_path"),
    )
    _append_if_present(
        artifacts_created,
        artifact_type="delivery_receipt_project",
        path=delivery_receipts.get("project_receipt_path"),
    )

    workflow_receipts = _safe_dict(result_payload.get("workflow_receipts"))
    _append_if_present(
        artifacts_created,
        artifact_type="workflow_receipt_global",
        path=workflow_receipts.get("global_receipt_path"),
    )
    _append_if_present(
        artifacts_created,
        artifact_type="workflow_receipt_project",
        path=workflow_receipts.get("project_receipt_path"),
    )

    _append_if_present(
        state_mutations,
        artifact_type="client_signoff_status",
        path=result_payload.get("signoff_status_path"),
    )

    if action.startswith("decision_"):
        _append_if_present(
            state_mutations,
            artifact_type="contractor_decision_record",
            path=result_payload.get("artifact_path"),
        )
        _append_if_present(
            artifacts_created,
            artifact_type="contractor_decision_receipt",
            path=result_payload.get("receipt_path"),
        )

    if action.startswith("risk_"):
        _append_if_present(
            state_mutations,
            artifact_type="contractor_risk_record",
            path=result_payload.get("artifact_path"),
        )
        _append_if_present(
            artifacts_created,
            artifact_type="contractor_risk_receipt",
            path=result_payload.get("receipt_path"),
        )

    if action.startswith("assumption_"):
        _append_if_present(
            state_mutations,
            artifact_type="contractor_assumption_record",
            path=result_payload.get("artifact_path"),
        )
        _append_if_present(
            artifacts_created,
            artifact_type="contractor_assumption_receipt",
            path=result_payload.get("receipt_path"),
        )

    if action.startswith("router_"):
        _append_if_present(
            state_mutations,
            artifact_type="contractor_router_schedule_blocks",
            path=result_payload.get("artifact_path"),
        )
        _append_if_present(
            artifacts_created,
            artifact_type="contractor_router_receipt",
            path=result_payload.get("receipt_path"),
        )

    if action.startswith("comply_"):
        _append_if_present(
            state_mutations,
            artifact_type="contractor_compliance_record",
            path=result_payload.get("artifact_path"),
        )
        _append_if_present(
            artifacts_created,
            artifact_type="contractor_compliance_receipt",
            path=result_payload.get("receipt_path"),
        )

    if action.startswith("oracle_"):
        _append_if_present(
            state_mutations,
            artifact_type="contractor_oracle_projection",
            path=result_payload.get("artifact_path"),
        )
        _append_if_present(
            artifacts_created,
            artifact_type="contractor_oracle_receipt",
            path=result_payload.get("receipt_path"),
        )

    email_result = _safe_dict(result_payload.get("email_result"))
    if email_result:
        external_actions.append(
            {
                "action_type": "send_email",
                "provider": _safe_str(email_result.get("provider")) or "smtp",
                "status": _safe_str(email_result.get("status")) or "unknown",
                "recipient": _safe_str(email_result.get("recipient")),
                "delivery_id": _safe_str(email_result.get("delivery_id")),
                "execution_gate_allowed": bool(
                    email_result.get("execution_gate_allowed") is True
                ),
            }
        )

    if status in {
        "ok",
        "created",
        "transitioned",
        "signed",
        "reviewed",
        "invalidated",
        "stored",
        "completed",
    }:
        effect = "execution_completed"
    elif status == "delivery_failed":
        effect = "execution_partial_delivery_failed"
    elif status == "blocked":
        effect = "execution_blocked"
    else:
        effect = "execution_result_unknown"

    return {
        "artifact_type": "post_execution_result_summary",
        "artifact_version": RESULT_SUMMARY_VERSION,
        "created_at": _utc_now_iso(),
        "action": _safe_str(action) or _safe_str(context_payload.get("action")),
        "status": status,
        "effect": effect,
        "project_id": project_id,
        "phase_id": phase_id,
        "artifacts_created": artifacts_created,
        "external_actions": external_actions,
        "state_mutations": state_mutations,
        "counts": {
            "artifacts_created": len(artifacts_created),
            "external_actions": len(external_actions),
            "state_mutations": len(state_mutations),
        },
        "sealed": True,
    }