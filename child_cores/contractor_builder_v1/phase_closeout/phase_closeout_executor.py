from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.delivery.delivery_receipt_builder import (
    build_delivery_receipt,
    write_delivery_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.delivery.email_runtime import send_email
from AI_GO.child_cores.contractor_builder_v1.delivery.email_schema import (
    build_email_delivery_record,
    validate_email_delivery_record,
)
from AI_GO.child_cores.contractor_builder_v1.delivery.email_retry_runtime import (
    build_retry_attempt,
    should_retry,
)
from AI_GO.child_cores.contractor_builder_v1.documents.pdf_receipt_builder import (
    build_pdf_receipt,
    write_pdf_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.documents.phase_closeout_pdf_builder import (
    build_phase_closeout_pdf,
)
from AI_GO.child_cores.contractor_builder_v1.documents.phase_closeout_pdf_schema import (
    build_phase_closeout_pdf_artifact,
    validate_phase_closeout_pdf_artifact,
)
from AI_GO.child_cores.contractor_builder_v1.explanation.phase_closeout_explainer import (
    build_phase_closeout_body,
    build_phase_closeout_subject,
)
from AI_GO.child_cores.contractor_builder_v1.governance.project_receipt_copy import (
    write_project_receipt_copy,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.client_signoff_status_runtime import (
    append_client_signoff_status,
    build_initial_signoff,
    mark_sent,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.resend_guard import can_resend
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_receipt_builder import (
    build_workflow_receipt,
    write_workflow_receipt,
)
from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.paths.path_resolver import (
    get_contractor_phase_closeout_documents_root,
    get_contractor_project_delivery_root,
)


def _execution_gate_allowed(execution_gate: Dict[str, Any]) -> bool:
    return bool((execution_gate or {}).get("allowed") is True)


def _classification_block(persistence_type: str) -> Dict[str, Any]:
    return {
        "persistence_type": persistence_type,
        "mutation_class": "contractor_phase_closeout_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "advisory_only": False,
    }


def _authority_metadata(
    *,
    operation: str,
    project_id: str,
    phase_id: str,
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "phase_closeout.phase_closeout_executor",
        "project_id": str(project_id or "").strip(),
        "phase_id": str(phase_id or "").strip(),
    }


def _write_project_json(path: Path, payload: Dict[str, Any]) -> Path:
    project_id = str(payload.get("project_id", "")).strip()
    phase_id = str(payload.get("phase_id", "")).strip()

    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="contractor_phase_closeout_persistence",
        persistence_type="contractor_phase_closeout_record",
        authority_metadata=_authority_metadata(
            operation="write_project_json",
            project_id=project_id,
            phase_id=phase_id,
        ),
    )
    return path


def _build_pdf_artifact_record(
    *,
    raw_pdf: Dict[str, Any],
    project_id: str,
    phase_id: str,
    phase_name: str,
) -> Dict[str, Any]:
    artifact = build_phase_closeout_pdf_artifact(
        artifact_id=str(raw_pdf.get("artifact_id", "")).strip(),
        project_id=project_id,
        phase_id=phase_id,
        phase_name=phase_name,
        pdf_path=str(raw_pdf.get("pdf_path", "")).strip(),
        pdf_hash=str(raw_pdf.get("pdf_hash", "")).strip(),
        generated_at=str(raw_pdf.get("generated_at", "")).strip() or None,
        version=1,
    )

    validation_errors = validate_phase_closeout_pdf_artifact(artifact)
    if validation_errors:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "invalid_phase_closeout_pdf_artifact",
                "validation_errors": validation_errors,
            },
        )

    artifact["classification"] = _classification_block("contractor_phase_closeout_pdf_artifact")
    artifact["authority_metadata"] = _authority_metadata(
        operation="build_pdf_artifact_record",
        project_id=project_id,
        phase_id=phase_id,
    )
    artifact["sealed"] = True
    return artifact


def _persist_pdf_artifact_record(
    *,
    project_id: str,
    phase_id: str,
    artifact: Dict[str, Any],
) -> str:
    artifact_id = str(artifact.get("artifact_id", "")).strip()
    if not artifact_id:
        raise HTTPException(status_code=500, detail="Phase closeout artifact_id is missing.")

    output_path = (
        get_contractor_phase_closeout_documents_root(project_id)
        / f"{artifact_id}.artifact.json"
    )
    _write_project_json(output_path, artifact)
    return str(output_path)


def _build_email_record(
    *,
    email_result: Dict[str, Any],
    project_id: str,
    phase_id: str,
    recipient_email: str,
    subject: str,
    artifact_id: str,
    attachment_path: str,
) -> Dict[str, Any]:
    delivery_id = str(email_result.get("delivery_id", "") or "").strip()
    delivery_status = str(email_result.get("status", "") or "").strip() or "failed"
    sent_at = str(email_result.get("sent_at", "") or "").strip() or None

    if not delivery_id:
        delivery_id = f"email-failed-{project_id}-{phase_id}"

    record = build_email_delivery_record(
        delivery_id=delivery_id,
        project_id=project_id,
        phase_id=phase_id,
        recipient_email=recipient_email,
        subject=subject,
        artifact_id=artifact_id,
        attachment_path=attachment_path,
        delivery_status=delivery_status,
        provider_message_id="",
        sent_at=sent_at,
        read_receipt_status="sent" if delivery_status == "sent" else "not_requested",
    )

    validation_errors = validate_email_delivery_record(record)
    if validation_errors:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "invalid_email_delivery_record",
                "validation_errors": validation_errors,
            },
        )

    if email_result.get("error"):
        record["error"] = str(email_result.get("error"))
    if email_result.get("error_type"):
        record["error_type"] = str(email_result.get("error_type"))
    if email_result.get("provider"):
        record["provider"] = str(email_result.get("provider"))

    record["classification"] = _classification_block("contractor_phase_closeout_email_record")
    record["authority_metadata"] = _authority_metadata(
        operation="build_email_record",
        project_id=project_id,
        phase_id=phase_id,
    )
    record["sealed"] = True

    return record


def _persist_email_record(
    *,
    project_id: str,
    phase_id: str,
    email_record: Dict[str, Any],
) -> str:
    delivery_id = str(email_record.get("delivery_id", "")).strip()
    if not delivery_id:
        raise HTTPException(status_code=500, detail="Email delivery_id is missing.")

    output_path = get_contractor_project_delivery_root(project_id) / f"{delivery_id}.json"
    _write_project_json(output_path, email_record)
    return str(output_path)


def _append_signoff_sent_status(
    *,
    project_id: str,
    phase_id: str,
    client_name: str,
    client_email: str,
    artifact_id: str,
    existing_signoff_status: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    base = (
        dict(existing_signoff_status)
        if existing_signoff_status is not None
        else build_initial_signoff(
            project_id=project_id,
            phase_id=phase_id,
            client_name=client_name,
            client_email=client_email,
        )
    )

    updated = mark_sent(base, artifact_id=artifact_id)
    append_client_signoff_status(updated)
    return updated


def execute_phase_closeout(
    *,
    context: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    if not _execution_gate_allowed(execution_gate):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "execution_gate_blocked",
                "message": "Executor refused to run because execution_gate.allowed is not true.",
                "execution_gate": execution_gate,
            },
        )

    project_id = str(context.get("project_id", "")).strip()
    phase_id = str(context.get("phase_id", "")).strip()
    client_email = str(context.get("client_email", "")).strip()
    client_name = str(context.get("client_name", "Customer")).strip() or "Customer"
    project_name = str(context.get("project_name", project_id)).strip() or project_id
    phase_name = str(context.get("phase_name", phase_id)).strip() or phase_id

    latest_signoff_status = context.get("latest_signoff_status")
    if isinstance(latest_signoff_status, dict):
        resend = can_resend(latest_signoff_status)
        if resend.get("allowed") is not True:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "resend_not_allowed",
                    "resend_guard": resend,
                },
            )

    documents_root = get_contractor_phase_closeout_documents_root(project_id)

    raw_pdf = build_phase_closeout_pdf(
        project_id=project_id,
        phase_id=phase_id,
        phase_name=phase_name,
        base_path=str(documents_root),
    )

    pdf_artifact = _build_pdf_artifact_record(
        raw_pdf=raw_pdf,
        project_id=project_id,
        phase_id=phase_id,
        phase_name=phase_name,
    )
    pdf_artifact_record_path = _persist_pdf_artifact_record(
        project_id=project_id,
        phase_id=phase_id,
        artifact=pdf_artifact,
    )

    pdf_receipt = build_pdf_receipt(
        project_id=project_id,
        phase_id=phase_id,
        artifact_id=pdf_artifact["artifact_id"],
        pdf_path=pdf_artifact["pdf_path"],
        pdf_hash=pdf_artifact["pdf_hash"],
    )
    pdf_receipt_path = write_pdf_receipt(pdf_receipt)

    subject = str(context.get("email_subject", "") or "").strip() or build_phase_closeout_subject(
        project_name=project_name,
        phase_name=phase_name,
    )
    body = str(context.get("email_body", "") or "").strip() or build_phase_closeout_body(
        client_name=client_name,
        project_name=project_name,
        phase_name=phase_name,
    )

    email_result = send_email(
        to_email=client_email,
        subject=subject,
        body=body,
        attachment_path=pdf_artifact["pdf_path"],
    )

    email_record = _build_email_record(
        email_result=email_result,
        project_id=project_id,
        phase_id=phase_id,
        recipient_email=client_email,
        subject=subject,
        artifact_id=pdf_artifact["artifact_id"],
        attachment_path=pdf_artifact["pdf_path"],
    )
    email_record_path = _persist_email_record(
        project_id=project_id,
        phase_id=phase_id,
        email_record=email_record,
    )

    retry_attempt = build_retry_attempt(email_record)
    retry_allowed = should_retry(retry_attempt)

    delivery_receipt = build_delivery_receipt(
        project_id=project_id,
        phase_id=phase_id,
        delivery_id=email_record["delivery_id"],
        artifact_path=email_record_path,
        details={
            "email_status": email_record.get("delivery_status"),
            "retry_allowed": retry_allowed,
        },
    )
    delivery_receipt_path = write_delivery_receipt(delivery_receipt)

    workflow_receipt = build_workflow_receipt(
        event_type="phase_closeout_sent",
        project_id=project_id,
        phase_id=phase_id,
        artifact_path=pdf_artifact["pdf_path"],
        details={
            "delivery_id": email_record["delivery_id"],
            "artifact_id": pdf_artifact["artifact_id"],
        },
    )
    workflow_receipt_path = write_workflow_receipt(workflow_receipt)

    project_receipt_copy_path = write_project_receipt_copy(
        project_id=project_id,
        receipt_path=str(workflow_receipt_path),
    )

    updated_signoff_status = _append_signoff_sent_status(
        project_id=project_id,
        phase_id=phase_id,
        client_name=client_name,
        client_email=client_email,
        artifact_id=pdf_artifact["artifact_id"],
        existing_signoff_status=latest_signoff_status
        if isinstance(latest_signoff_status, dict)
        else None,
    )

    return {
        "status": "sent",
        "project_id": project_id,
        "phase_id": phase_id,
        "artifact_id": pdf_artifact["artifact_id"],
        "pdf_path": pdf_artifact["pdf_path"],
        "pdf_artifact_record_path": pdf_artifact_record_path,
        "pdf_receipt_path": str(pdf_receipt_path),
        "email_record_path": email_record_path,
        "delivery_receipt_path": str(delivery_receipt_path),
        "workflow_receipt_path": str(workflow_receipt_path),
        "project_receipt_copy_path": str(project_receipt_copy_path),
        "email_record": email_record,
        "updated_signoff_status": updated_signoff_status,
        "classification": _classification_block("contractor_phase_closeout_result"),
        "authority_metadata": _authority_metadata(
            operation="execute_phase_closeout",
            project_id=project_id,
            phase_id=phase_id,
        ),
        "sealed": True,
    }