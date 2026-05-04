from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.change.change_runtime import (
    append_change_packet_record,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_signoff_status_runtime import (
    get_latest_change_signoff_status,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_receipt_builder import (
    build_change_receipt,
    write_change_receipt,
)


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _status_record(
    *,
    packet: Dict[str, Any],
    status: str,
    client_name: str = "",
    client_email: str = "",
    actor: str = "change_signoff_executor",
) -> Dict[str, Any]:
    return {
        "project_id": _safe_str(packet.get("project_id")),
        "phase_id": _safe_str(packet.get("phase_id")),
        "change_packet_id": _safe_str(packet.get("change_packet_id")),
        "status": status,
        "client_name": client_name,
        "client_email": client_email,
        "actor": actor,
    }


def _update_packet_signoff(
    *,
    packet: Dict[str, Any],
    status: str,
    client_name: str = "",
    client_email: str = "",
    actor: str = "change_signoff_executor",
) -> Dict[str, Any]:
    updated = dict(packet)
    current = dict(updated.get("change_signoff", {}))
    current["status"] = status
    current["client_name"] = client_name or current.get("client_name", "")
    current["client_email"] = client_email or current.get("client_email", "")
    current["latest_delivery_status"] = status
    current["actor"] = actor
    updated["change_signoff"] = current
    return updated


def _write_receipt(
    *,
    event_type: str,
    packet: Dict[str, Any],
    artifact_path: str,
    actor: str,
) -> str:
    receipt = build_change_receipt(
        event_type=event_type,
        project_id=_safe_str(packet.get("project_id")),
        change_packet_id=_safe_str(packet.get("change_packet_id")),
        artifact_path=artifact_path,
        actor=actor,
    )
    return str(write_change_receipt(receipt))


def execute_change_signoff_send(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])
    packet = dict(context["packet"])
    actor = _safe_str(request.get("actor")) or "change_signoff_executor"

    updated = _update_packet_signoff(
        packet=packet,
        status="sent",
        client_name=_safe_str(request.get("client_name")),
        client_email=_safe_str(request.get("client_email") or request.get("recipient")),
        actor=actor,
    )
    output_path = append_change_packet_record(updated)
    receipt_path = _write_receipt(
        event_type="send_change_signoff",
        packet=updated,
        artifact_path=str(output_path),
        actor=actor,
    )

    return {
        "status": "sent",
        "packet": updated,
        "change_signoff_status": _status_record(
            packet=updated,
            status="sent",
            client_name=_safe_str(request.get("client_name")),
            client_email=_safe_str(request.get("client_email") or request.get("recipient")),
            actor=actor,
        ),
        "artifact_path": str(output_path),
        "receipt_path": receipt_path,
    }


def execute_change_signoff_complete(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])
    packet = dict(context["packet"])
    latest = dict(context.get("latest_signoff_status", {}))
    actor = _safe_str(request.get("actor")) or "change_signoff_executor"

    if _safe_str(latest.get("status")).lower() == "signed":
        return {
            "status": "already_signed",
            "noop": True,
            "packet": packet,
            "change_signoff_status": latest,
        }

    updated = _update_packet_signoff(
        packet=packet,
        status="signed",
        actor=actor,
    )
    output_path = append_change_packet_record(updated)
    receipt_path = _write_receipt(
        event_type="complete_change_signoff",
        packet=updated,
        artifact_path=str(output_path),
        actor=actor,
    )

    return {
        "status": "signed",
        "noop": False,
        "packet": updated,
        "change_signoff_status": _status_record(
            packet=updated,
            status="signed",
            actor=actor,
        ),
        "artifact_path": str(output_path),
        "receipt_path": receipt_path,
    }


def execute_change_signoff_decline(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])
    packet = dict(context["packet"])
    latest = dict(context.get("latest_signoff_status", {}))
    actor = _safe_str(request.get("actor")) or "change_signoff_executor"

    if _safe_str(latest.get("status")).lower() == "declined":
        return {
            "status": "already_declined",
            "noop": True,
            "packet": packet,
            "change_signoff_status": latest,
        }

    updated = _update_packet_signoff(
        packet=packet,
        status="declined",
        actor=actor,
    )
    output_path = append_change_packet_record(updated)
    receipt_path = _write_receipt(
        event_type="decline_change_signoff",
        packet=updated,
        artifact_path=str(output_path),
        actor=actor,
    )

    return {
        "status": "declined",
        "noop": False,
        "packet": updated,
        "change_signoff_status": _status_record(
            packet=updated,
            status="declined",
            actor=actor,
        ),
        "artifact_path": str(output_path),
        "receipt_path": receipt_path,
    }