"""
Change closeout guard for contractor_builder_v1.

This module evaluates whether unresolved change packets should block phase
closeout. It is read-only and derives its answer from the canonical change
runtime append-only log.

Northstar Stage 6A/6B rule:
- No direct filesystem write.
- No hardcoded state root.
- No ungoverned mutation.
- Preserve legacy import surface expected by change APIs and package exports.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .change_runtime import list_latest_change_packets


CHANGE_CLOSEOUT_GUARD_VERSION = "northstar_change_closeout_guard_v2_import_surface"

BLOCKING_CHANGE_STATUSES = {
    "draft",
    "requester_submitted",
    "pending_approvals",
    "pending_approval",
    "pending_pm_review",
    "pm_review",
    "sent",
    "open",
    "active",
}

NON_BLOCKING_CHANGE_STATUSES = {
    "approved",
    "rejected",
    "archived",
    "cancelled",
    "canceled",
    "closed",
    "superseded",
}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_lower(value: Any) -> str:
    return _safe_str(value).lower()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_change_closeout_guard_read",
        "mutation_class": "read_only_guard",
        "advisory_only": False,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": False,
        "read_only": True,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "contractor_change_closeout_guard",
        "can_execute": False,
        "can_mutate_state": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
        "state_authority": "read_only_guard",
    }


def _packet_phase_matches(packet: Dict[str, Any], phase_id: str) -> bool:
    clean_phase_id = _safe_str(phase_id)
    if not clean_phase_id:
        return True

    packet_phase_id = _safe_str(packet.get("phase_id"))
    if packet_phase_id:
        return packet_phase_id == clean_phase_id

    affected_phases = _safe_list(packet.get("affected_phase_ids"))
    if affected_phases:
        return clean_phase_id in {_safe_str(item) for item in affected_phases}

    return True


def _is_blocking_packet(packet: Dict[str, Any]) -> bool:
    status = _safe_lower(packet.get("status"))

    if status in NON_BLOCKING_CHANGE_STATUSES:
        return False

    if status in BLOCKING_CHANGE_STATUSES:
        return True

    if packet.get("blocking") is True:
        return True

    if packet.get("blocks_phase_closeout") is True:
        return True

    if packet.get("requires_resolution_before_closeout") is True:
        return True

    return False


def _blocking_item(packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "change_packet_id": _safe_str(packet.get("change_packet_id")),
        "phase_id": _safe_str(packet.get("phase_id")),
        "status": _safe_str(packet.get("status")),
        "title": _safe_str(packet.get("title") or packet.get("change_title")),
        "reason": "unresolved_change_blocks_phase_closeout",
        "source_packet": dict(packet),
    }


def get_latest_change_packets_for_phase(
    *,
    project_id: str,
    phase_id: str = "",
) -> List[Dict[str, Any]]:
    """
    Compatibility export expected by the contractor change package.

    Returns latest change packets for a project, optionally filtered to the
    requested phase. This function is read-only and delegates storage reads to
    change_runtime.list_latest_change_packets.
    """

    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)

    if not clean_project_id:
        raise ValueError("project_id is required")

    latest_packets = list_latest_change_packets(clean_project_id)

    return [
        dict(packet)
        for packet in latest_packets
        if isinstance(packet, dict) and _packet_phase_matches(packet, clean_phase_id)
    ]


def get_blocking_unresolved_changes(
    *,
    project_id: str,
    phase_id: str = "",
) -> List[Dict[str, Any]]:
    """
    Compatibility export expected by change.__init__ and API import chains.

    Returns normalized blocking unresolved change entries for a project/phase.
    """

    relevant_packets = get_latest_change_packets_for_phase(
        project_id=project_id,
        phase_id=phase_id,
    )

    return [
        _blocking_item(packet)
        for packet in relevant_packets
        if _is_blocking_packet(packet)
    ]


def build_change_closeout_guard_summary(
    *,
    project_id: str,
    phase_id: str = "",
) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)

    if not clean_project_id:
        raise ValueError("project_id is required")

    relevant_packets = get_latest_change_packets_for_phase(
        project_id=clean_project_id,
        phase_id=clean_phase_id,
    )
    blocking_items = get_blocking_unresolved_changes(
        project_id=clean_project_id,
        phase_id=clean_phase_id,
    )

    latest_packets = list_latest_change_packets(clean_project_id)
    blocking_count = len(blocking_items)

    return {
        "artifact_type": "contractor_change_closeout_guard_summary",
        "artifact_version": CHANGE_CLOSEOUT_GUARD_VERSION,
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "status": "blocked" if blocking_count else "passed",
        "valid": blocking_count == 0,
        "phase_has_blocking_unresolved_changes": blocking_count > 0,
        "blocking_unresolved_change_count": blocking_count,
        "blocking_items": blocking_items,
        "blocking_unresolved_changes": blocking_items,
        "latest_change_packet_count": len(latest_packets),
        "relevant_change_packet_count": len(relevant_packets),
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def phase_has_blocking_unresolved_changes(
    *,
    project_id: str,
    phase_id: str = "",
) -> bool:
    summary = build_change_closeout_guard_summary(
        project_id=project_id,
        phase_id=phase_id,
    )
    return bool(summary.get("phase_has_blocking_unresolved_changes"))
