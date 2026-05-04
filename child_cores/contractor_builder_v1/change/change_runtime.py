"""
Change runtime for contractor_builder_v1.

This module creates, appends, reads, and transitions change packet records under
append-only posture. It stores:
- change packet records
- approval events

Northstar posture:
- no hardcoded runtime state roots
- no ungoverned writes
- append-only persistence for change history
- compatibility exports preserved for API/service import surfaces
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from AI_GO.core.governance.governed_persistence import governed_append_jsonl
from AI_GO.core.state_runtime.state_paths import contractor_projects_root

from ..governance.integrity import compute_hash_for_mapping
from .change_schema import build_change_packet, validate_change_packet


STATE_ROOT = contractor_projects_root()


CHANGE_RECORD_MUTATION_CLASS = "contractor_change_persistence"
CHANGE_APPROVAL_MUTATION_CLASS = "contractor_change_approval_persistence"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _jsonl_records(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    for line in lines:
        clean = line.strip()
        if not clean:
            continue

        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            if parsed.get("artifact_type") == "governed_persistence_envelope":
                payload = parsed.get("payload")
                if isinstance(payload, dict):
                    records.append(payload)
            else:
                records.append(parsed)

    return records


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------


def get_change_packets_path(project_id: str) -> Path:
    return STATE_ROOT / _safe_str(project_id) / "change" / "change_packets.jsonl"


def get_change_approvals_path(project_id: str) -> Path:
    return STATE_ROOT / _safe_str(project_id) / "change" / "approvals.jsonl"


# -----------------------------------------------------------------------------
# Classification / authority
# -----------------------------------------------------------------------------


def _authority_metadata(
    *,
    operation: str,
    project_id: str = "",
    change_packet_id: str = "",
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6b",
        "operation": _safe_str(operation),
        "child_core_id": "contractor_builder_v1",
        "layer": "change.change_runtime",
        "project_id": _safe_str(project_id),
        "change_packet_id": _safe_str(change_packet_id),
        "can_execute": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "state_authority": "governed_append_only",
    }


def _classification_block(
    *,
    persistence_type: str = "contractor_change_record",
    mutation_class: str = CHANGE_RECORD_MUTATION_CLASS,
) -> Dict[str, Any]:
    return {
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "advisory_only": False,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "append_only": True,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "contractor_change_runtime",
        "can_execute": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
        "state_authority": "governed_append_only",
    }


# -----------------------------------------------------------------------------
# Integrity
# -----------------------------------------------------------------------------


def _refresh_packet_integrity(packet: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(packet)
    integrity = dict(updated.get("integrity", {}))

    packet_for_hash = dict(updated)
    packet_for_hash["integrity"] = {
        "packet_hash": "",
        "linked_receipts": integrity.get("linked_receipts", []),
        "supersedes_change_packet_id": integrity.get("supersedes_change_packet_id"),
    }

    integrity["packet_hash"] = compute_hash_for_mapping(packet_for_hash)
    updated["integrity"] = integrity
    return updated


def _prepare_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(packet)
    project_id = _safe_str(payload.get("project_id"))
    change_packet_id = _safe_str(payload.get("change_packet_id"))

    payload.setdefault("artifact_type", "contractor_change_packet_record")
    payload.setdefault("artifact_version", "northstar_change_packet_v1")
    payload.setdefault("recorded_at", _utc_now_iso())
    payload["classification"] = _classification_block()
    payload["authority_metadata"] = _authority_metadata(
        operation="prepare_change_packet_record",
        project_id=project_id,
        change_packet_id=change_packet_id,
    )
    payload["authority"] = _authority_block()
    payload["sealed"] = True

    return _refresh_packet_integrity(payload)


# -----------------------------------------------------------------------------
# Packet create / append / read
# -----------------------------------------------------------------------------


def create_change_packet_record(**packet_kwargs: Any) -> Dict[str, Any]:
    packet = build_change_packet(**packet_kwargs)
    if not isinstance(packet, dict):
        packet = dict(packet)

    validation_errors = validate_change_packet(packet)
    if validation_errors:
        raise ValueError(
            {
                "error": "invalid_change_packet",
                "validation_errors": validation_errors,
            }
        )

    return _prepare_packet(packet)


def append_change_packet_record(packet: Dict[str, Any]) -> Path:
    if not isinstance(packet, dict):
        raise ValueError("packet must be a dict")

    payload = _prepare_packet(packet)
    project_id = _safe_str(payload.get("project_id"))
    change_packet_id = _safe_str(payload.get("change_packet_id"))

    if not project_id:
        raise ValueError("project_id is required")
    if not change_packet_id:
        raise ValueError("change_packet_id is required")

    path = get_change_packets_path(project_id)

    governed_append_jsonl(
        path=path,
        payload=payload,
        mutation_class=CHANGE_RECORD_MUTATION_CLASS,
        persistence_type="contractor_change_packet_record",
        authority_metadata=_authority_metadata(
            operation="append_change_packet_record",
            project_id=project_id,
            change_packet_id=change_packet_id,
        ),
    )

    return path


def read_change_packet_history(project_id: str) -> List[Dict[str, Any]]:
    return _jsonl_records(get_change_packets_path(project_id))


def list_latest_change_packets(project_id: str) -> List[Dict[str, Any]]:
    return read_change_packet_history(project_id)


def get_latest_change_packet(
    *,
    project_id: str,
    change_packet_id: str,
) -> Optional[Dict[str, Any]]:
    clean_change_packet_id = _safe_str(change_packet_id)
    latest: Optional[Dict[str, Any]] = None

    for record in read_change_packet_history(project_id):
        if _safe_str(record.get("change_packet_id")) == clean_change_packet_id:
            latest = record

    return latest


# -----------------------------------------------------------------------------
# Transitions
# -----------------------------------------------------------------------------


def transition_change_packet_status(
    packet: Dict[str, Any],
    *,
    new_status: str,
) -> Dict[str, Any]:
    if not isinstance(packet, dict):
        raise ValueError("packet must be a dict")

    clean_status = _safe_str(new_status)
    if not clean_status:
        raise ValueError("new_status is required")

    updated = dict(packet)
    status_history = list(_safe_list(updated.get("status_history")))
    previous_status = _safe_str(updated.get("status"))

    status_history.append(
        {
            "from_status": previous_status,
            "to_status": clean_status,
            "transitioned_at": _utc_now_iso(),
        }
    )

    updated["status"] = clean_status
    updated["status_history"] = status_history
    updated["updated_at"] = _utc_now_iso()

    return _prepare_packet(updated)


# -----------------------------------------------------------------------------
# Approval events
# -----------------------------------------------------------------------------


def append_change_approval_event(
    *,
    project_id: str,
    change_packet_id: str,
    event_type: str,
    actor_name: str,
    actor_role: str,
    notes: str = "",
) -> Path:
    clean_project_id = _safe_str(project_id)
    clean_change_packet_id = _safe_str(change_packet_id)

    if not clean_project_id:
        raise ValueError("project_id is required")
    if not clean_change_packet_id:
        raise ValueError("change_packet_id is required")

    payload = {
        "artifact_type": "contractor_change_approval_event",
        "artifact_version": "northstar_change_approval_event_v1",
        "project_id": clean_project_id,
        "change_packet_id": clean_change_packet_id,
        "event_type": _safe_str(event_type),
        "actor_name": _safe_str(actor_name),
        "actor_role": _safe_str(actor_role),
        "notes": str(notes or ""),
        "recorded_at": _utc_now_iso(),
        "classification": _classification_block(
            persistence_type="contractor_change_approval_event",
            mutation_class=CHANGE_APPROVAL_MUTATION_CLASS,
        ),
        "authority_metadata": _authority_metadata(
            operation="append_change_approval_event",
            project_id=clean_project_id,
            change_packet_id=clean_change_packet_id,
        ),
        "authority": _authority_block(),
        "sealed": True,
    }

    path = get_change_approvals_path(clean_project_id)

    governed_append_jsonl(
        path=path,
        payload=payload,
        mutation_class=CHANGE_APPROVAL_MUTATION_CLASS,
        persistence_type="contractor_change_approval_event",
        authority_metadata=_authority_metadata(
            operation="append_change_approval_event",
            project_id=clean_project_id,
            change_packet_id=clean_change_packet_id,
        ),
    )

    return path


def read_change_approval_history(project_id: str) -> List[Dict[str, Any]]:
    return _jsonl_records(get_change_approvals_path(project_id))