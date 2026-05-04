"""
Checklist runtime for contractor_builder_v1 workflow.

This module owns checklist-side computation only.

It provides:
- canonical phase checklist summary building
- checklist item completion helpers

It does NOT:
- persist checklist state
- advance workflow
- decide workflow authority
- replace phase closeout gating

Division of responsibility:
- checklist_runtime.py -> compute checklist readiness deterministically
- workflow_runtime.py -> use checklist readiness to reconcile workflow state
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import List

from .checklist_schema import ChecklistItem, PhaseChecklist


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _validate_required_text(value: str, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _is_item_complete(item: ChecklistItem) -> bool:
    return str(item.status or "").strip() == "complete"


def _required_items(items: List[ChecklistItem]) -> List[ChecklistItem]:
    return [item for item in items if bool(item.required)]


def _completed_required_items(items: List[ChecklistItem]) -> List[ChecklistItem]:
    return [item for item in _required_items(items) if _is_item_complete(item)]


def build_phase_checklist(
    project_id: str,
    phase_id: str,
    items: List[ChecklistItem],
) -> PhaseChecklist:
    """
    Build a canonical phase checklist summary.

    Readiness rule:
    - At least one required item must exist
    - All required items must be complete
    """
    project_id_clean = _validate_required_text(project_id, "project_id")
    phase_id_clean = _validate_required_text(phase_id, "phase_id")

    if not isinstance(items, list):
        raise ValueError("items must be a list of ChecklistItem")

    required_items = _required_items(items)
    completed_required = _completed_required_items(items)

    required_item_count = len(required_items)
    completed_required_count = len(completed_required)

    ready_for_signoff = (
        required_item_count > 0
        and completed_required_count == required_item_count
    )

    return PhaseChecklist(
        project_id=project_id_clean,
        phase_id=phase_id_clean,
        items=items,
        required_item_count=required_item_count,
        completed_required_count=completed_required_count,
        ready_for_signoff=ready_for_signoff,
    )


def complete_checklist_item(item: ChecklistItem, user: str) -> ChecklistItem:
    """
    Mark one checklist item complete.

    This mutates the passed ChecklistItem instance in place and returns it.
    """
    if not isinstance(item, ChecklistItem):
        raise ValueError("item must be a ChecklistItem")

    user_clean = _validate_required_text(user, "user")

    item.status = "complete"
    item.completed_by = user_clean
    item.completed_at = _utc_now()
    return item