"""
Decision runtime for contractor_builder_v1.

Append-only decision records. No destructive revision.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from AI_GO.core.governance.governed_persistence import governed_append_jsonl
from AI_GO.core.state_runtime.state_paths import contractor_projects_root

from ..governance.integrity import compute_hash_for_mapping
from .decision_schema import build_decision_entry, validate_decision_entry


STATE_ROOT = contractor_projects_root()

BUILD_DECISION_ENTRY_FIELDS = {
    "decision_id",
    "project_id",
    "title",
    "decision_type",
    "phase_id",
    "linked_change_packet_id",
    "compliance_snapshot_id",
    "schedule_baseline_id",
    "budget_baseline_id",
    "drawing_revision_id",
    "oracle_snapshot_id",
    "expected_schedule_delta_days",
    "expected_cost_delta_amount",
    "expected_margin_delta_percent",
    "expected_risk_level",
    "notes_on_assumptions",
    "may_reference_in_owner_reports",
    "owner_report_reference_label",
    "notes_internal",
    "attachments_refs",
}


DECISION_TYPE_ALIASES = {
    "scope": "Scope_Clarification",
    "scope_clarification": "Scope_Clarification",
    "design": "Design_Adjustment",
    "design_adjustment": "Design_Adjustment",
    "cost": "Cost_Acceptance",
    "cost_acceptance": "Cost_Acceptance",
    "schedule": "Schedule_Adjustment",
    "schedule_adjustment": "Schedule_Adjustment",
    "risk": "Risk_Acceptance",
    "risk_acceptance": "Risk_Acceptance",
    "vendor": "Vendor_Selection",
    "vendor_selection": "Vendor_Selection",
    "compliance": "Compliance_Clarification",
    "compliance_clarification": "Compliance_Clarification",
    "sequence": "Sequence_Change",
    "sequence_change": "Sequence_Change",
    "quality": "Quality_Standard_Change",
    "quality_standard_change": "Quality_Standard_Change",
    "client": "Client_Request_Confirmation",
    "client_request": "Client_Request_Confirmation",
    "client_request_confirmation": "Client_Request_Confirmation",
}


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _stamp_for_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _new_decision_id(project_id: str) -> str:
    clean_project_id = _safe_str(project_id) or "project"
    return f"decision-{clean_project_id}-{_stamp_for_id()}-{uuid4().hex[:8]}"


def get_decisions_path(project_id: str) -> Path:
    return STATE_ROOT / project_id / "decision_log" / "decisions.jsonl"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_decision_record",
        "mutation_class": "contractor_decision_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "append_only": True,
        "advisory_only": False,
    }


def _authority_metadata(project_id: str, decision_id: str, operation: str) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "decision_log.decision_runtime",
        "project_id": _safe_str(project_id),
        "decision_id": _safe_str(decision_id),
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "contractor_decision_runtime",
        "can_execute": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
        "state_authority": "governed_append_only",
    }


def _normalize_decision_type(value: Any) -> str:
    raw = _safe_str(value)

    if not raw:
        return "Scope_Clarification"

    if raw in set(DECISION_TYPE_ALIASES.values()):
        return raw

    key = raw.lower().replace(" ", "_").replace("-", "_")
    return DECISION_TYPE_ALIASES.get(key, raw)


def _normalize_decision_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(kwargs)

    if "decision_title" in normalized and "title" not in normalized:
        normalized["title"] = normalized.pop("decision_title")

    if "decision_summary" in normalized and "notes_internal" not in normalized:
        normalized["notes_internal"] = normalized.pop("decision_summary")

    if "description" in normalized and "notes_internal" not in normalized:
        normalized["notes_internal"] = normalized.pop("description")

    if "summary" in normalized and "notes_internal" not in normalized:
        normalized["notes_internal"] = normalized.pop("summary")

    if "decision_category" in normalized and "decision_type" not in normalized:
        normalized["decision_type"] = normalized.pop("decision_category")

    if "category" in normalized and "decision_type" not in normalized:
        normalized["decision_type"] = normalized.pop("category")

    if "impact_summary" in normalized and "notes_on_assumptions" not in normalized:
        normalized["notes_on_assumptions"] = normalized.pop("impact_summary")

    normalized["project_id"] = _safe_str(normalized.get("project_id"))
    normalized["phase_id"] = _safe_str(normalized.get("phase_id"))

    if not _safe_str(normalized.get("decision_id")):
        normalized["decision_id"] = _new_decision_id(normalized.get("project_id", ""))

    if not _safe_str(normalized.get("title")):
        normalized["title"] = "Untitled Decision"

    normalized["decision_type"] = _normalize_decision_type(
        normalized.get("decision_type")
    )

    return normalized


def _builder_kwargs(normalized: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in normalized.items()
        if key in BUILD_DECISION_ENTRY_FIELDS
    }


def _apply_identity_block(
    *,
    entry: Dict[str, Any],
    normalized: Dict[str, Any],
    field_name: str,
) -> None:
    incoming = normalized.get(field_name)

    if not isinstance(incoming, dict):
        return

    existing = _safe_dict(entry.get(field_name))
    existing.update(incoming)
    entry[field_name] = existing


def _apply_post_build_fields(
    entry: Dict[str, Any],
    normalized: Dict[str, Any],
) -> Dict[str, Any]:
    updated = dict(entry)

    _apply_identity_block(
        entry=updated,
        normalized=normalized,
        field_name="requested_by",
    )
    _apply_identity_block(
        entry=updated,
        normalized=normalized,
        field_name="approved_by",
    )

    decision_status = _safe_str(normalized.get("decision_status"))
    if decision_status:
        updated["decision_status"] = decision_status

    return updated


def _refresh_decision_integrity(entry: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(entry)
    integrity = dict(updated.get("integrity", {}))

    entry_for_hash = dict(updated)
    entry_for_hash["integrity"] = {
        "entry_hash": "",
        "linked_receipts": integrity.get("linked_receipts", []),
        "supersedes_decision_id": integrity.get("supersedes_decision_id"),
    }

    integrity["entry_hash"] = compute_hash_for_mapping(entry_for_hash)
    updated["integrity"] = integrity
    return updated


def _prepare_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    prepared = _refresh_decision_integrity(entry)
    prepared["classification"] = _classification_block()
    prepared["authority"] = _authority_block()
    prepared["sealed"] = True
    return prepared


def create_decision_record(**kwargs: Any) -> Dict[str, Any]:
    normalized = _normalize_decision_kwargs(kwargs)
    entry = build_decision_entry(**_builder_kwargs(normalized))
    entry = _apply_post_build_fields(entry, normalized)

    errors = validate_decision_entry(entry)
    if errors:
        raise ValueError("Invalid decision entry: " + "; ".join(errors))

    return _refresh_decision_integrity(entry)


def append_decision_record(
    entry: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    errors = validate_decision_entry(entry)
    if errors:
        raise ValueError("Invalid decision entry: " + "; ".join(errors))

    project_id = _safe_str(entry["project_id"])
    decision_id = _safe_str(entry.get("decision_id"))
    output_path = get_decisions_path(project_id)

    governed_append_jsonl(
        path=output_path,
        payload=_prepare_entry(entry),
        mutation_class="contractor_decision_persistence",
        persistence_type="contractor_decision_record",
        authority_metadata=_authority_metadata(
            project_id=project_id,
            decision_id=decision_id,
            operation="append_decision_record",
        ),
    )

    return output_path


def transition_decision_status(
    entry: Dict[str, Any],
    *,
    new_status: str,
) -> Dict[str, Any]:
    updated = dict(entry)
    clean_status = _safe_str(new_status)

    updated["decision_status"] = clean_status
    updated["updated_at"] = _utc_now_iso()

    transitions = list(updated.get("status_history", []))
    transitions.append(
        {
            "status": clean_status,
            "timestamp": _utc_now_iso(),
            "actor": "decision_runtime",
        }
    )
    updated["status_history"] = transitions

    return _refresh_decision_integrity(updated)