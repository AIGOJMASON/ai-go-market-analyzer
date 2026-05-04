"""
Risk runtime for contractor_builder_v1.

Append-only risk records. No destructive revision.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from AI_GO.core.governance.governed_persistence import governed_append_jsonl
from AI_GO.core.state_runtime.state_paths import contractor_projects_root

from ..governance.integrity import compute_hash_for_mapping
from .risk_schema import build_risk_entry, validate_risk_entry


STATE_ROOT = contractor_projects_root()

BUILD_RISK_ENTRY_FIELDS = {
    "risk_id",
    "project_id",
    "category",
    "description",
    "probability",
    "impact_level",
    "mitigation_strategy",
    "mitigation_owner",
    "review_frequency",
    "linked_decision_ids",
    "linked_change_packet_ids",
    "notes",
}


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _stamp_for_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _new_risk_id(project_id: str) -> str:
    clean_project_id = _safe_str(project_id) or "project"
    return f"risk-{clean_project_id}-{_stamp_for_id()}-{uuid4().hex[:8]}"


def get_risks_path(project_id: str) -> Path:
    return STATE_ROOT / _safe_str(project_id) / "risk_register" / "risks.jsonl"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_risk_record",
        "mutation_class": "contractor_risk_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "append_only": True,
        "advisory_only": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "contractor_risk_runtime",
        "can_execute": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
        "state_authority": "governed_append_only",
    }


def _authority_metadata(
    *,
    operation: str,
    project_id: str,
    risk_id: str = "",
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "risk_register.risk_runtime",
        "project_id": _safe_str(project_id),
        "risk_id": _safe_str(risk_id),
    }


def _normalize_risk_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(kwargs)

    normalized["project_id"] = _safe_str(normalized.get("project_id"))

    if not _safe_str(normalized.get("risk_id")):
        normalized["risk_id"] = _new_risk_id(normalized.get("project_id", ""))

    if "risk_category" in normalized and "category" not in normalized:
        normalized["category"] = normalized.pop("risk_category")

    if "risk_description" in normalized and "description" not in normalized:
        normalized["description"] = normalized.pop("risk_description")

    if "risk_probability" in normalized and "probability" not in normalized:
        normalized["probability"] = normalized.pop("risk_probability")

    if "risk_impact" in normalized and "impact_level" not in normalized:
        normalized["impact_level"] = normalized.pop("risk_impact")

    if "owner" in normalized and "mitigation_owner" not in normalized:
        normalized["mitigation_owner"] = normalized.pop("owner")

    if "mitigation" in normalized and "mitigation_strategy" not in normalized:
        normalized["mitigation_strategy"] = normalized.pop("mitigation")

    if "decision_id" in normalized and "linked_decision_ids" not in normalized:
        decision_id = _safe_str(normalized.pop("decision_id"))
        normalized["linked_decision_ids"] = [decision_id] if decision_id else []

    if "change_packet_id" in normalized and "linked_change_packet_ids" not in normalized:
        change_packet_id = _safe_str(normalized.pop("change_packet_id"))
        normalized["linked_change_packet_ids"] = [change_packet_id] if change_packet_id else []

    if "linked_decision_ids" in normalized:
        normalized["linked_decision_ids"] = [
            _safe_str(item) for item in _safe_list(normalized.get("linked_decision_ids")) if _safe_str(item)
        ]

    if "linked_change_packet_ids" in normalized:
        normalized["linked_change_packet_ids"] = [
            _safe_str(item) for item in _safe_list(normalized.get("linked_change_packet_ids")) if _safe_str(item)
        ]

    normalized.setdefault("category", "Other")
    normalized.setdefault("probability", "Moderate")
    normalized.setdefault("impact_level", "Moderate")
    normalized.setdefault("mitigation_strategy", "Monitor and review during governed project cycle.")
    normalized.setdefault("mitigation_owner", "Project Manager")
    normalized.setdefault("review_frequency", "weekly")
    normalized.setdefault("notes", "")

    return normalized


def _builder_kwargs(normalized: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in normalized.items()
        if key in BUILD_RISK_ENTRY_FIELDS
    }


def _apply_post_build_fields(
    entry: Dict[str, Any],
    normalized: Dict[str, Any],
) -> Dict[str, Any]:
    updated = dict(entry)

    status = _safe_str(normalized.get("status"))
    if status:
        updated["status"] = status

    last_reviewed = _safe_str(normalized.get("last_reviewed"))
    if last_reviewed:
        updated["last_reviewed"] = last_reviewed

    date_logged = _safe_str(normalized.get("date_logged"))
    if date_logged:
        updated["date_logged"] = date_logged

    return updated


def _refresh_risk_integrity(entry: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(entry)
    integrity = dict(updated.get("integrity", {}))

    entry_for_hash = dict(updated)
    entry_for_hash["integrity"] = {
        "entry_hash": "",
        "linked_receipts": integrity.get("linked_receipts", []),
    }

    integrity["entry_hash"] = compute_hash_for_mapping(entry_for_hash)
    updated["integrity"] = integrity
    return updated


def _prepare_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    prepared = _refresh_risk_integrity(entry)
    prepared["classification"] = _classification_block()
    prepared["authority"] = _authority_block()
    prepared["sealed"] = True
    return prepared


def create_risk_record(**kwargs: Any) -> Dict[str, Any]:
    normalized = _normalize_risk_kwargs(kwargs)
    entry = build_risk_entry(**_builder_kwargs(normalized))
    entry = _apply_post_build_fields(entry, normalized)

    errors = validate_risk_entry(entry)
    if errors:
        raise ValueError("Invalid risk entry: " + "; ".join(errors))

    return _refresh_risk_integrity(entry)


def append_risk_record(
    entry: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    errors = validate_risk_entry(entry)
    if errors:
        raise ValueError("Invalid risk entry: " + "; ".join(errors))

    project_id = _safe_str(entry.get("project_id"))
    risk_id = _safe_str(entry.get("risk_id"))

    if not project_id:
        raise ValueError("project_id is required")

    output_path = get_risks_path(project_id)

    governed_append_jsonl(
        path=output_path,
        payload=_prepare_entry(entry),
        mutation_class="contractor_risk_persistence",
        persistence_type="contractor_risk_record",
        authority_metadata=_authority_metadata(
            operation="append_risk_record",
            project_id=project_id,
            risk_id=risk_id,
        ),
    )

    return output_path


def transition_risk_status(
    entry: Dict[str, Any],
    *,
    new_status: str,
    notes: str = "",
) -> Dict[str, Any]:
    updated = dict(entry)
    updated["status"] = _safe_str(new_status)
    updated["last_reviewed"] = _utc_now_iso()

    existing_notes = str(updated.get("notes", "") or "")
    clean_notes = _safe_str(notes)

    if clean_notes:
        updated["notes"] = existing_notes + ("\n" if existing_notes else "") + clean_notes

    errors = validate_risk_entry(updated)
    if errors:
        raise ValueError("Invalid risk entry: " + "; ".join(errors))

    return _refresh_risk_integrity(updated)