from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


FORBIDDEN_FIELDS = {
    "internal_state",
    "internal_notes",
    "private_notes",
    "debug",
    "debug_trace",
    "traceback",
    "_internal",
    "_debug",
    "_private",
}

APPROVED_SOURCE_ARTIFACT_TYPES = {
    "case_closeout_record",
    "operator_review_view",
    "operator_review_index",
}


class AnalyticsSummaryError(ValueError):
    """Raised when Stage 60 analytics summary construction fails."""


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise AnalyticsSummaryError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _require_dict(name: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise AnalyticsSummaryError(f"{name} must be a dict")
    return value


def _increment(counter: Dict[str, int], key: str) -> None:
    counter[key] = counter.get(key, 0) + 1


def _extract_pattern_notes(
    total_items: int,
    by_closeout_state: Dict[str, int],
    by_intake_decision: Dict[str, int],
    by_target_child_core: Dict[str, int],
) -> List[str]:
    notes: List[str] = []

    if total_items == 0:
        notes.append("no_items_in_scope")
        return notes

    if by_closeout_state:
        if len(by_closeout_state) == 1:
            only_key = next(iter(by_closeout_state))
            notes.append(f"single_closeout_state:{only_key}")
        else:
            notes.append("mixed_closeout_states")

    if by_intake_decision:
        if by_intake_decision.get("accepted", 0) > by_intake_decision.get("rejected", 0):
            notes.append("accepted_intake_majority")
        elif by_intake_decision.get("rejected", 0) > by_intake_decision.get("accepted", 0):
            notes.append("rejected_intake_majority")
        else:
            notes.append("balanced_intake_outcomes")

    if by_target_child_core:
        if len(by_target_child_core) == 1:
            only_core = next(iter(by_target_child_core))
            notes.append(f"single_child_core_scope:{only_core}")
        else:
            notes.append("multi_child_core_scope")

    return notes


def build_analytics_summary(
    archive_retrieval_result: Dict[str, Any],
    issuing_authority: str = "RUNTIME_ANALYTICS_SUMMARY",
) -> Dict[str, Any]:
    """
    Stage 60 — descriptive analytics only.

    Consumes one approved archive_retrieval_result and emits one bounded
    analytics_summary artifact.
    """
    _assert_no_internal_field_leakage(archive_retrieval_result, "archive_retrieval_result")
    archive_retrieval_result = _require_dict(
        "archive_retrieval_result",
        deepcopy(archive_retrieval_result),
    )

    if archive_retrieval_result.get("artifact_type") != "archive_retrieval_result":
        raise AnalyticsSummaryError(
            "archive_retrieval_result.artifact_type must be 'archive_retrieval_result'"
        )

    payload = archive_retrieval_result.get("payload")
    if not isinstance(payload, dict):
        raise AnalyticsSummaryError("archive_retrieval_result.payload must be a dict")

    if payload.get("sealed") is not True:
        raise AnalyticsSummaryError("archive_retrieval_result.payload.sealed must be True")

    results = payload.get("results")
    if not isinstance(results, list):
        raise AnalyticsSummaryError("archive_retrieval_result.payload.results must be a list")

    by_artifact_type: Dict[str, int] = {}
    by_closeout_state: Dict[str, int] = {}
    by_final_state: Dict[str, int] = {}
    by_intake_decision: Dict[str, int] = {}
    by_target_child_core: Dict[str, int] = {}

    for index, item in enumerate(results):
        item_name = f"archive_retrieval_result.payload.results[{index}]"
        _assert_no_internal_field_leakage(item, item_name)
        item = _require_dict(item_name, item)

        artifact_type = item.get("artifact_type")
        if artifact_type not in APPROVED_SOURCE_ARTIFACT_TYPES:
            raise AnalyticsSummaryError(
                f"{item_name}.artifact_type must be one of {sorted(APPROVED_SOURCE_ARTIFACT_TYPES)}"
            )

        item_payload = item.get("payload")
        if not isinstance(item_payload, dict):
            raise AnalyticsSummaryError(f"{item_name}.payload must be a dict")

        if item_payload.get("sealed") is not True:
            raise AnalyticsSummaryError(f"{item_name}.payload.sealed must be True")

        _increment(by_artifact_type, artifact_type)

        closeout_state = item_payload.get("closeout_state")
        final_state = item_payload.get("final_state")
        intake_decision = item_payload.get("intake_decision")
        target_child_core = item_payload.get("target_child_core")

        if closeout_state:
            _increment(by_closeout_state, str(closeout_state))
        if final_state:
            _increment(by_final_state, str(final_state))
        if intake_decision:
            _increment(by_intake_decision, str(intake_decision))
        if target_child_core:
            _increment(by_target_child_core, str(target_child_core))

    total_items = len(results)
    pattern_notes = _extract_pattern_notes(
        total_items=total_items,
        by_closeout_state=by_closeout_state,
        by_intake_decision=by_intake_decision,
        by_target_child_core=by_target_child_core,
    )

    return {
        "artifact_type": "analytics_summary",
        "payload": {
            "issuing_authority": issuing_authority,
            "source_retrieval_total_count": payload.get("total_count"),
            "source_retrieval_filtered_count": payload.get("filtered_count"),
            "source_retrieval_returned_count": payload.get("returned_count"),
            "total_items_in_scope": total_items,
            "counts_by_artifact_type": by_artifact_type,
            "counts_by_closeout_state": by_closeout_state,
            "counts_by_final_state": by_final_state,
            "counts_by_intake_decision": by_intake_decision,
            "counts_by_target_child_core": by_target_child_core,
            "pattern_notes": pattern_notes,
            "sealed": True,
        },
    }