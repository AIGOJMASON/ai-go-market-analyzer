"""
Email schema for contractor_builder_v1.

This module defines the canonical structured metadata for a phase-closeout
email delivery event.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, List


EMAIL_SCHEMA_VERSION = "v1"

READ_RECEIPT_STATUS_ENUM = [
    "not_requested",
    "sent",
    "opened",
    "signed",
    "declined",
    "expired",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_email_delivery_record(
    *,
    delivery_id: str,
    project_id: str,
    phase_id: str,
    recipient_email: str,
    subject: str,
    artifact_id: str,
    attachment_path: str,
    delivery_status: str = "sent",
    provider_message_id: str = "",
    sent_at: str | None = None,
    read_receipt_status: str = "sent",
) -> Dict[str, Any]:
    return {
        "schema_version": EMAIL_SCHEMA_VERSION,
        "delivery_id": delivery_id,
        "project_id": project_id,
        "phase_id": phase_id,
        "recipient_email": recipient_email,
        "subject": subject,
        "artifact_id": artifact_id,
        "attachment_path": attachment_path,
        "delivery_status": delivery_status,
        "provider_message_id": provider_message_id,
        "sent_at": sent_at or _utc_now_iso(),
        "read_receipt_status": read_receipt_status,
        "allowed_read_receipt_statuses": READ_RECEIPT_STATUS_ENUM,
    }


def validate_email_delivery_record(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    required_fields = [
        "delivery_id",
        "project_id",
        "phase_id",
        "recipient_email",
        "subject",
        "artifact_id",
        "attachment_path",
        "delivery_status",
        "sent_at",
        "read_receipt_status",
    ]
    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required email delivery field: {field}")

    if not record.get("delivery_id"):
        errors.append("delivery_id may not be empty")
    if not record.get("project_id"):
        errors.append("project_id may not be empty")
    if not record.get("phase_id"):
        errors.append("phase_id may not be empty")
    if not record.get("recipient_email"):
        errors.append("recipient_email may not be empty")
    if not record.get("attachment_path"):
        errors.append("attachment_path may not be empty")

    read_receipt_status = record.get("read_receipt_status")
    if read_receipt_status not in READ_RECEIPT_STATUS_ENUM:
        errors.append(
            f"read_receipt_status must be one of {READ_RECEIPT_STATUS_ENUM}"
        )

    return errors