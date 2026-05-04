
"""
Change signoff status runtime for contractor_builder_v1.

This module records append-only change signoff status events and exposes the
latest signoff posture for a change packet.

Northstar Stage 6A rule:
No direct filesystem mutation calls are permitted.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from AI_GO.core.governance.governed_persistence import governed_append_jsonl
from AI_GO.core.state_runtime.state_paths import contractor_projects_root


STATE_ROOT = contractor_projects_root()

VALID_CHANGE_SIGNOFF_STATUSES = {
    "not_requested",
    "sent",
    "signed",
    "declined",
    "expired",
    "cancelled",
}


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_lower(value: Any) -> str:
    return _safe_str(value).lower()


def get_change_signoff_status_path(project_id: str) -> Path:
    return STATE_ROOT / _safe_str(project_id) / "change" / "change_signoff_status.jsonl"


def _authority_metadata(
    *,
    operation: str,
    project_id: str = "",
    change_packet_id: str = "",
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "change.change_signoff_status_runtime",
        "project_id": _safe_str(project_id),
        "change_packet_id": _safe_str(change_packet_id),
    }


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_change_signoff_record",
        "mutation_class": "contractor_change_signoff_persistence",
        "advisory_only": False,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "append_only": True,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "contractor_change_signoff_status_runtime",
        "can_execute": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
        "state_authority": "governed_append_only",
    }


def _stamp_record(record: Dict[str, Any]) -> Dict[str, Any]:
    stamped = dict(record)
    stamped.setdefault("artifact_type", "contractor_change_signoff_status")
    stamped.setdefault("schema_version", "v1")
    stamped.setdefault("recorded_at", _utc_now_iso())
    stamped["classification"] = _classification_block()
    stamped["authority"] = _authority_block()
    stamped["sealed"] = True
    return stamped


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    records: List[Dict[str, Any]] = []

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        try:
            payload = json.loads(clean_line)
        except json.JSONDecodeError:
            continue

        if isinstance(payload, dict):
            records.append(payload)

    return records


def build_change_signoff_status(
    *,
    project_id: str,
    change_packet_id: str,
    status: str,
    phase_id: str = "",
    client_name: str = "",
    client_email: str = "",
    actor: str = "change_signoff_status_runtime",
    notes: str = "",
    artifact_id: str = "",
) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    clean_change_packet_id = _safe_str(change_packet_id)
    clean_status = _safe_lower(status)

    if not clean_project_id:
        raise ValueError("project_id is required")
    if not clean_change_packet_id:
        raise ValueError("change_packet_id is required")
    if clean_status not in VALID_CHANGE_SIGNOFF_STATUSES:
        raise ValueError(
            "status must be one of: "
            + ", ".join(sorted(VALID_CHANGE_SIGNOFF_STATUSES))
        )

    return _stamp_record(
        {
            "artifact_type": "contractor_change_signoff_status",
            "schema_version": "v1",
            "project_id": clean_project_id,
            "phase_id": _safe_str(phase_id),
            "change_packet_id": clean_change_packet_id,
            "status": clean_status,
            "client_name": _safe_str(client_name),
            "client_email": _safe_str(client_email),
            "actor": _safe_str(actor) or "change_signoff_status_runtime",
            "notes": notes,
            "artifact_id": _safe_str(artifact_id),
            "recorded_at": _utc_now_iso(),
        }
    )


def append_change_signoff_status(
    status_record: Optional[Dict[str, Any]] = None,
    *,
    project_id: str = "",
    change_packet_id: str = "",
    status: str = "",
    phase_id: str = "",
    client_name: str = "",
    client_email: str = "",
    actor: str = "change_signoff_status_runtime",
    notes: str = "",
    artifact_id: str = "",
) -> Path:
    """
    Append a change signoff status record.

    Accepts either a prepared status_record dict or keyword fields.
    """
    if status_record is None:
        record = build_change_signoff_status(
            project_id=project_id,
            change_packet_id=change_packet_id,
            status=status,
            phase_id=phase_id,
            client_name=client_name,
            client_email=client_email,
            actor=actor,
            notes=notes,
            artifact_id=artifact_id,
        )
    else:
        if not isinstance(status_record, dict):
            raise ValueError("status_record must be a dict")

        record = dict(status_record)
        record.setdefault("artifact_type", "contractor_change_signoff_status")
        record.setdefault("schema_version", "v1")
        record["project_id"] = _safe_str(record.get("project_id"))
        record["change_packet_id"] = _safe_str(record.get("change_packet_id"))
        record["status"] = _safe_lower(record.get("status"))
        record.setdefault("phase_id", "")
        record.setdefault("client_name", "")
        record.setdefault("client_email", "")
        record.setdefault("actor", actor)
        record.setdefault("notes", "")
        record.setdefault("artifact_id", "")
        record.setdefault("recorded_at", _utc_now_iso())
        record = _stamp_record(record)

        if not record["project_id"]:
            raise ValueError("project_id is required")
        if not record["change_packet_id"]:
            raise ValueError("change_packet_id is required")
        if record["status"] not in VALID_CHANGE_SIGNOFF_STATUSES:
            raise ValueError(
                "status must be one of: "
                + ", ".join(sorted(VALID_CHANGE_SIGNOFF_STATUSES))
            )

    output_path = get_change_signoff_status_path(record["project_id"])

    governed_append_jsonl(
        path=output_path,
        payload=record,
        mutation_class="contractor_change_signoff_persistence",
        persistence_type="contractor_change_signoff_record",
        authority_metadata=_authority_metadata(
            operation="append_change_signoff_status",
            project_id=record["project_id"],
            change_packet_id=record["change_packet_id"],
        ),
    )

    return output_path


def list_change_signoff_statuses(
    *,
    project_id: str,
    change_packet_id: str = "",
) -> List[Dict[str, Any]]:
    records = _read_jsonl(get_change_signoff_status_path(project_id))

    clean_change_packet_id = _safe_str(change_packet_id)
    if not clean_change_packet_id:
        return records

    return [
        record
        for record in records
        if _safe_str(record.get("change_packet_id")) == clean_change_packet_id
    ]


def list_change_signoff_status_history(
    *,
    project_id: str,
    change_packet_id: str = "",
) -> List[Dict[str, Any]]:
    """
    Backward-compatible public contract expected by change package imports.
    """
    return list_change_signoff_statuses(
        project_id=project_id,
        change_packet_id=change_packet_id,
    )


def get_latest_change_signoff_status(
    *,
    project_id: str,
    change_packet_id: str,
) -> Optional[Dict[str, Any]]:
    latest: Optional[Dict[str, Any]] = None

    for record in list_change_signoff_statuses(
        project_id=project_id,
        change_packet_id=change_packet_id,
    ):
        latest = record

    return latest


def build_initial_change_signoff(
    *,
    project_id: str,
    change_packet_id: str,
    phase_id: str = "",
    client_name: str = "",
    client_email: str = "",
    actor: str = "change_signoff_status_runtime",
) -> Dict[str, Any]:
    return build_change_signoff_status(
        project_id=project_id,
        change_packet_id=change_packet_id,
        phase_id=phase_id,
        status="not_requested",
        client_name=client_name,
        client_email=client_email,
        actor=actor,
    )


def mark_change_signoff_sent(
    status_record: Dict[str, Any],
    *,
    client_name: str = "",
    client_email: str = "",
    actor: str = "change_signoff_status_runtime",
    artifact_id: str = "",
) -> Dict[str, Any]:
    record = dict(status_record)
    record["status"] = "sent"

    if client_name:
        record["client_name"] = client_name
    if client_email:
        record["client_email"] = client_email
    if artifact_id:
        record["artifact_id"] = artifact_id

    record["actor"] = actor
    record["sent_at"] = _utc_now_iso()
    record["recorded_at"] = _utc_now_iso()

    return _stamp_record(record)


def mark_sent(
    status_record: Dict[str, Any],
    artifact_id: str = "",
) -> Dict[str, Any]:
    """
    Compatibility alias expected by change package imports.
    """
    return mark_change_signoff_sent(
        status_record,
        artifact_id=artifact_id,
    )


def mark_change_signoff_signed(
    status_record: Dict[str, Any],
    *,
    actor: str = "change_signoff_status_runtime",
    notes: str = "",
) -> Dict[str, Any]:
    record = dict(status_record)
    record["status"] = "signed"
    record["actor"] = actor
    if notes:
        record["notes"] = notes
    record["signed_at"] = _utc_now_iso()
    record["recorded_at"] = _utc_now_iso()

    return _stamp_record(record)


def mark_signed(
    status_record: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compatibility alias expected by change package imports.
    """
    return mark_change_signoff_signed(status_record)


def mark_change_signoff_declined(
    status_record: Dict[str, Any],
    *,
    actor: str = "change_signoff_status_runtime",
    notes: str = "",
) -> Dict[str, Any]:
    record = dict(status_record)
    record["status"] = "declined"
    record["actor"] = actor
    if notes:
        record["notes"] = notes
    record["declined_at"] = _utc_now_iso()
    record["recorded_at"] = _utc_now_iso()

    return _stamp_record(record)


def mark_declined(
    status_record: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compatibility alias expected by change package imports.
    """
    return mark_change_signoff_declined(status_record)