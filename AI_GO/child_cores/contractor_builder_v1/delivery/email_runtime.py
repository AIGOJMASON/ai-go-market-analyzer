from __future__ import annotations

import os
import smtplib
from datetime import UTC, datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, Optional


MUTATION_CLASS = "contractor_email_delivery_external_effect"
PERSISTENCE_TYPE = "external_smtp_delivery"
ADVISORY_ONLY = False
EMAIL_RUNTIME_VERSION = "northstar_email_runtime_v1"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _delivery_id() -> str:
    return f"email_{int(datetime.now(UTC).timestamp())}"


def _validate_required_text(value: str, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _classification_block() -> Dict[str, Any]:
    return {
        "mutation_class": MUTATION_CLASS,
        "persistence_type": PERSISTENCE_TYPE,
        "advisory_only": ADVISORY_ONLY,
        "external_effect": True,
        "external_effect_type": "smtp_email_delivery",
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "requires_execution_gate": True,
        "requires_receipt": True,
        "governed_persistence": False,
    }


def _authority_metadata() -> Dict[str, Any]:
    return {
        "authority_id": "contractor_builder_v1_delivery_email_runtime",
        "operation": "send_email",
        "source": "AI_GO.child_cores.contractor_builder_v1.delivery.email_runtime",
        "runtime_version": EMAIL_RUNTIME_VERSION,
        "can_execute_external_effect": True,
        "can_mutate_state": False,
        "can_mutate_project_truth": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "requires_execution_gate": True,
        "requires_receipt": True,
    }


def _execution_gate_allowed(execution_gate: Optional[Dict[str, Any]]) -> bool:
    gate = _safe_dict(execution_gate)
    return bool(gate.get("allowed") is True or gate.get("valid") is True)


def _load_smtp_config() -> Dict[str, Any]:
    smtp_host = str(os.getenv("SMTP_HOST", "smtp.gmail.com") or "").strip()
    smtp_port_raw = str(os.getenv("SMTP_PORT", "587") or "").strip()
    smtp_user = str(os.getenv("SMTP_USER", "") or "").strip()
    smtp_pass = str(os.getenv("SMTP_PASS", "") or "").strip()
    from_email = str(os.getenv("FROM_EMAIL", smtp_user) or "").strip()

    try:
        smtp_port = int(smtp_port_raw)
    except Exception as exc:
        raise RuntimeError(f"SMTP_PORT must be an integer: {smtp_port_raw}") from exc

    return {
        "SMTP_HOST": smtp_host,
        "SMTP_PORT": smtp_port,
        "SMTP_USER": smtp_user,
        "SMTP_PASS": smtp_pass,
        "FROM_EMAIL": from_email,
    }


def _smtp_config_present(config: Dict[str, Any]) -> bool:
    return bool(
        config.get("SMTP_HOST")
        and config.get("SMTP_PORT")
        and config.get("SMTP_USER")
        and config.get("SMTP_PASS")
        and config.get("FROM_EMAIL")
    )


def _base_result(
    *,
    delivery_id: str,
    recipient: str,
    subject: str,
    attachment_path: str,
    status: str,
) -> Dict[str, Any]:
    attachment_clean = str(attachment_path or "").strip()

    return {
        "delivery_id": delivery_id,
        "recipient": str(recipient or "").strip(),
        "subject": str(subject or "").strip(),
        "attachment": attachment_clean,
        "attachment_name": Path(attachment_clean).name if attachment_clean else "",
        "attachment_added": False,
        "sent_at": _utc_now_iso(),
        "status": status,
        "provider": "smtp",
        "runtime_version": EMAIL_RUNTIME_VERSION,
        "mutation_class": MUTATION_CLASS,
        "persistence_type": PERSISTENCE_TYPE,
        "advisory_only": ADVISORY_ONLY,
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(),
        "sealed": True,
    }


def _blocked_delivery_result(
    *,
    delivery_id: str,
    recipient: str,
    subject: str,
    attachment_path: str,
    reason: str,
    execution_gate: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result = _base_result(
        delivery_id=delivery_id,
        recipient=recipient,
        subject=subject,
        attachment_path=attachment_path,
        status="blocked",
    )
    result.update(
        {
            "error": reason,
            "error_type": "ExecutionGateBlocked",
            "execution_gate_allowed": False,
            "execution_gate": _safe_dict(execution_gate),
        }
    )
    return result


def _failed_delivery_result(
    *,
    delivery_id: str,
    recipient: str,
    subject: str,
    attachment_path: str,
    error: str,
    error_type: str,
    execution_gate: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result = _base_result(
        delivery_id=delivery_id,
        recipient=recipient,
        subject=subject,
        attachment_path=attachment_path,
        status="failed",
    )
    result.update(
        {
            "error": error,
            "error_type": error_type,
            "execution_gate_allowed": _execution_gate_allowed(execution_gate),
            "execution_gate": _safe_dict(execution_gate),
        }
    )
    return result


def _attach_file_if_present(msg: EmailMessage, attachment_path: str) -> bool:
    attachment_clean = str(attachment_path or "").strip()
    if not attachment_clean:
        return False

    path = Path(attachment_clean)
    if not path.exists() or not path.is_file():
        return False

    file_data = path.read_bytes()
    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=path.name,
    )
    return True


def send_email(
    recipient: str,
    subject: str,
    body: str,
    attachment_path: str = "",
    *,
    execution_gate: Optional[Dict[str, Any]] = None,
    require_execution_gate: bool = False,
) -> Dict[str, Any]:
    delivery_id = _delivery_id()

    try:
        recipient_clean = _validate_required_text(recipient, "recipient")
        subject_clean = _validate_required_text(subject, "subject")
        body_clean = str(body or "")
        attachment_clean = str(attachment_path or "").strip()

        if require_execution_gate and not _execution_gate_allowed(execution_gate):
            return _blocked_delivery_result(
                delivery_id=delivery_id,
                recipient=recipient_clean,
                subject=subject_clean,
                attachment_path=attachment_clean,
                reason="execution_gate_required_for_email_delivery",
                execution_gate=execution_gate,
            )

        config = _load_smtp_config()
        if not _smtp_config_present(config):
            return _failed_delivery_result(
                delivery_id=delivery_id,
                recipient=recipient_clean,
                subject=subject_clean,
                attachment_path=attachment_clean,
                error="SMTP configuration is incomplete.",
                error_type="SMTPConfigMissing",
                execution_gate=execution_gate,
            )

        msg = EmailMessage()
        msg["From"] = str(config["FROM_EMAIL"])
        msg["To"] = recipient_clean
        msg["Subject"] = subject_clean
        msg.set_content(body_clean)

        attachment_added = _attach_file_if_present(msg, attachment_clean)

        with smtplib.SMTP(str(config["SMTP_HOST"]), int(config["SMTP_PORT"])) as server:
            server.starttls()
            server.login(str(config["SMTP_USER"]), str(config["SMTP_PASS"]))
            server.send_message(msg)

        result = _base_result(
            delivery_id=delivery_id,
            recipient=recipient_clean,
            subject=subject_clean,
            attachment_path=attachment_clean,
            status="sent",
        )
        result.update(
            {
                "attachment_added": attachment_added,
                "execution_gate_allowed": _execution_gate_allowed(execution_gate),
                "execution_gate": _safe_dict(execution_gate),
            }
        )
        return result

    except Exception as exc:
        return _failed_delivery_result(
            delivery_id=delivery_id,
            recipient=str(recipient or "").strip(),
            subject=str(subject or "").strip(),
            attachment_path=str(attachment_path or "").strip(),
            error=str(exc),
            error_type=type(exc).__name__,
            execution_gate=execution_gate,
        )