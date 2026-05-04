from __future__ import annotations


class RefinementIntakeError(Exception):
    """Raised when refinement intake input artifacts are invalid."""


APPROVED_RETRIEVAL_ITEM_TYPES = {
    "case_closeout_record",
    "operator_review_view",
    "operator_review_index",
}


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise RefinementIntakeError(f"{name} must be a dict")


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise RefinementIntakeError(
            f"invalid artifact_type: expected {expected}, got {value.get('artifact_type')}"
        )


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise RefinementIntakeError(f"{name} payload must be a dict")
    return payload


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise RefinementIntakeError(f"{name} contains internal field leakage: {key}")


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise RefinementIntakeError(f"{name} must be sealed")


def _validate_analytics_summary(summary):
    _require_dict(summary, "analytics_summary")
    _require_artifact_type(summary, "analytics_summary")
    payload = _require_payload(summary, "analytics_summary")
    _reject_internal_fields(payload, "analytics_summary")
    _require_sealed(payload, "analytics_summary")

    required_fields = [
        "issuing_authority",
        "total_items_in_scope",
        "counts_by_closeout_state",
        "counts_by_intake_decision",
        "counts_by_target_child_core",
        "pattern_notes",
    ]
    for field in required_fields:
        if field not in payload:
            raise RefinementIntakeError(
                f"analytics_summary missing required field: {field}"
            )

    if not isinstance(payload["counts_by_closeout_state"], dict):
        raise RefinementIntakeError("counts_by_closeout_state must be a dict")
    if not isinstance(payload["counts_by_intake_decision"], dict):
        raise RefinementIntakeError("counts_by_intake_decision must be a dict")
    if not isinstance(payload["counts_by_target_child_core"], dict):
        raise RefinementIntakeError("counts_by_target_child_core must be a dict")
    if not isinstance(payload["pattern_notes"], list):
        raise RefinementIntakeError("pattern_notes must be a list")

    return payload


def _validate_retrieval_result(retrieval_result):
    _require_dict(retrieval_result, "archive_retrieval_result")
    _require_artifact_type(retrieval_result, "archive_retrieval_result")
    payload = _require_payload(retrieval_result, "archive_retrieval_result")
    _reject_internal_fields(payload, "archive_retrieval_result")
    _require_sealed(payload, "archive_retrieval_result")

    if "results" not in payload or not isinstance(payload["results"], list):
        raise RefinementIntakeError("archive_retrieval_result must include results list")

    for index, item in enumerate(payload["results"]):
        _require_dict(item, f"retrieval_result item {index}")
        item_type = item.get("artifact_type")
        if item_type not in APPROVED_RETRIEVAL_ITEM_TYPES:
            raise RefinementIntakeError(
                f"invalid retrieval result item type: {item_type}"
            )
        item_payload = _require_payload(item, f"retrieval_result item {index}")
        _require_sealed(item_payload, f"retrieval_result item {index}")

    return payload


def _build_selected_candidates(summary_payload):
    selected = []

    for note in summary_payload["pattern_notes"]:
        selected.append(
            {
                "candidate_type": "pattern_note",
                "candidate_source": "pattern_notes",
                "candidate_value": note,
                "selection_reason": "approved_pattern_note",
            }
        )

    for key, value in summary_payload["counts_by_closeout_state"].items():
        if value > 0:
            selected.append(
                {
                    "candidate_type": "closeout_count",
                    "candidate_source": "counts_by_closeout_state",
                    "candidate_value": {key: value},
                    "selection_reason": "positive_count_detected",
                }
            )

    for key, value in summary_payload["counts_by_intake_decision"].items():
        if value > 0:
            selected.append(
                {
                    "candidate_type": "intake_count",
                    "candidate_source": "counts_by_intake_decision",
                    "candidate_value": {key: value},
                    "selection_reason": "positive_count_detected",
                }
            )

    for key, value in summary_payload["counts_by_target_child_core"].items():
        if value > 0:
            selected.append(
                {
                    "candidate_type": "target_child_core_count",
                    "candidate_source": "counts_by_target_child_core",
                    "candidate_value": {key: value},
                    "selection_reason": "positive_count_detected",
                }
            )

    return selected


def build_refinement_candidate_set(analytics_summary, archive_retrieval_result=None):
    summary_payload = _validate_analytics_summary(analytics_summary)

    retrieval_context_included = False
    if archive_retrieval_result is not None:
        _validate_retrieval_result(archive_retrieval_result)
        retrieval_context_included = True

    selected_candidates = _build_selected_candidates(summary_payload)
    selected_count = len(selected_candidates)
    rejected_count = 0
    selection_notes = []

    if selected_count == 0:
        selection_notes.append("no_candidates_selected")

    return {
        "artifact_type": "refinement_candidate_set",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_INTAKE",
            "source_artifact_type": "analytics_summary",
            "retrieval_context_included": retrieval_context_included,
            "total_candidates_considered": selected_count,
            "selected_count": selected_count,
            "rejected_count": rejected_count,
            "selected_candidates": selected_candidates,
            "selection_notes": selection_notes,
            "sealed": True,
        },
    }