from __future__ import annotations

from AI_GO.api.outcome_ingress_policy import (
    build_observed_outcome_view,
    validate_closeout_artifact_linkage,
    validate_outcome_ingress_request,
)
from AI_GO.core.outcome_feedback.closeout_outcome_feedback_bridge import (
    record_outcome_feedback_from_closeout,
)


def ingest_outcome_result(
    *,
    request_payload: dict,
    closeout_artifact: dict,
    core_id: str,
) -> dict:
    if not core_id:
        return {
            "status": "rejected",
            "reason": "missing_core_id",
        }

    try:
        validate_outcome_ingress_request(request_payload)
    except ValueError as exc:
        return {
            "status": "rejected",
            "reason": str(exc),
        }

    try:
        validate_closeout_artifact_linkage(
            closeout_artifact=closeout_artifact,
            request_payload=request_payload,
        )
    except ValueError as exc:
        return {
            "status": "rejected",
            "reason": str(exc),
        }

    observed_outcome_view = build_observed_outcome_view(request_payload)

    bridge_result = record_outcome_feedback_from_closeout(
        closeout_artifact=closeout_artifact,
        observed_outcome_view=observed_outcome_view,
        core_id=core_id,
    )

    if bridge_result.get("status") != "recorded":
        return bridge_result

    return {
        "status": "ingested",
        "annotation_only": True,
        "core_id": core_id,
        "closeout_id": request_payload.get("closeout_id"),
        "observed_outcome_view": observed_outcome_view,
        "outcome_feedback_status": bridge_result.get("status"),
        "outcome_class": bridge_result.get("outcome_class"),
        "confidence_delta": bridge_result.get("confidence_delta"),
        "index_status": bridge_result.get("index_status"),
        "index_entry_id": bridge_result.get("index_entry_id"),
        "index_entry_count": bridge_result.get("index_entry_count"),
    }