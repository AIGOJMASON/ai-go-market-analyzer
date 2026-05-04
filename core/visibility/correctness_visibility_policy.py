from __future__ import annotations

from AI_GO.core.visibility.correctness_visibility_registry import (
    CORRECTNESS_VISIBILITY_REGISTRY,
)


def validate_outcome_feedback_record(outcome_feedback_record: dict) -> None:
    if outcome_feedback_record.get("status") != "recorded":
        raise ValueError("outcome_feedback_record_not_recorded")

    if not outcome_feedback_record.get("annotation_only", False):
        raise ValueError("outcome_feedback_record_not_annotation_only")

    for field in CORRECTNESS_VISIBILITY_REGISTRY["required_outcome_fields"]:
        if not outcome_feedback_record.get(field):
            raise ValueError(f"missing_outcome_feedback_field:{field}")


def validate_refinement_packet(refinement_packet: dict) -> None:
    if refinement_packet.get("status") != "generated":
        raise ValueError("refinement_packet_not_generated")

    if not refinement_packet.get("annotation_only", False):
        raise ValueError("refinement_packet_not_annotation_only")

    refinement_signal = refinement_packet.get("refinement_signal", {})
    for field in CORRECTNESS_VISIBILITY_REGISTRY["required_refinement_fields"]:
        if not refinement_signal.get(field):
            raise ValueError(f"missing_refinement_signal_field:{field}")


def validate_pm_intake_record(pm_intake_record: dict) -> None:
    if pm_intake_record.get("status") != "generated":
        raise ValueError("pm_intake_record_not_generated")

    if not pm_intake_record.get("annotation_only", False):
        raise ValueError("pm_intake_record_not_annotation_only")

    pm_signal = pm_intake_record.get("pm_signal", {})
    for field in CORRECTNESS_VISIBILITY_REGISTRY["required_pm_fields"]:
        if not pm_signal.get(field):
            raise ValueError(f"missing_pm_signal_field:{field}")


def normalize_history_view(outcome_feedback_index: dict) -> dict:
    if not isinstance(outcome_feedback_index, dict):
        return {
            "entry_count": 0,
            "latest_entry_id": None,
        }

    return {
        "entry_count": int(outcome_feedback_index.get("entry_count", 0) or 0),
        "latest_entry_id": outcome_feedback_index.get("latest_entry_id"),
    }