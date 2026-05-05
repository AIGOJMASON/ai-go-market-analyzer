from __future__ import annotations


class RefinementScoringError(Exception):
    """Raised when refinement scoring input artifacts are invalid."""


APPROVED_CANDIDATE_TYPES = {
    "pattern_note",
    "closeout_count",
    "intake_count",
    "target_child_core_count",
}


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise RefinementScoringError(f"{name} must be a dict")


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise RefinementScoringError(f"{name} payload must be a dict")
    return payload


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise RefinementScoringError(
            f"invalid artifact_type: expected {expected}, got {value.get('artifact_type')}"
        )


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise RefinementScoringError(f"{name} must be sealed")


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise RefinementScoringError(f"{name} contains internal field leakage: {key}")


def _validate_candidate_set(refinement_candidate_set):
    _require_dict(refinement_candidate_set, "refinement_candidate_set")
    _require_artifact_type(refinement_candidate_set, "refinement_candidate_set")
    payload = _require_payload(refinement_candidate_set, "refinement_candidate_set")
    _reject_internal_fields(payload, "refinement_candidate_set")
    _require_sealed(payload, "refinement_candidate_set")

    required_fields = [
        "issuing_authority",
        "source_artifact_type",
        "retrieval_context_included",
        "total_candidates_considered",
        "selected_count",
        "rejected_count",
        "selected_candidates",
        "selection_notes",
    ]
    for field in required_fields:
        if field not in payload:
            raise RefinementScoringError(
                f"refinement_candidate_set missing required field: {field}"
            )

    if not isinstance(payload["retrieval_context_included"], bool):
        raise RefinementScoringError("retrieval_context_included must be a bool")
    if not isinstance(payload["total_candidates_considered"], int):
        raise RefinementScoringError("total_candidates_considered must be an int")
    if not isinstance(payload["selected_count"], int):
        raise RefinementScoringError("selected_count must be an int")
    if not isinstance(payload["rejected_count"], int):
        raise RefinementScoringError("rejected_count must be an int")
    if not isinstance(payload["selected_candidates"], list):
        raise RefinementScoringError("selected_candidates must be a list")
    if not isinstance(payload["selection_notes"], list):
        raise RefinementScoringError("selection_notes must be a list")

    return payload


def _validate_selected_candidate(candidate, index):
    _require_dict(candidate, f"selected candidate {index}")

    required_fields = [
        "candidate_type",
        "candidate_source",
        "candidate_value",
        "selection_reason",
    ]
    for field in required_fields:
        if field not in candidate:
            raise RefinementScoringError(
                f"selected candidate {index} missing required field: {field}"
            )

    candidate_type = candidate["candidate_type"]
    if candidate_type not in APPROVED_CANDIDATE_TYPES:
        raise RefinementScoringError(
            f"selected candidate {index} has invalid candidate_type: {candidate_type}"
        )

    return candidate


def _score_pattern_note(candidate_value):
    if not isinstance(candidate_value, str):
        raise RefinementScoringError("pattern_note candidate_value must be a string")

    components = [{"component": "base_pattern_note", "score": 3}]

    if ":" in candidate_value:
        components.append({"component": "structured_pattern_note", "score": 1})

    return components


def _score_count_candidate(candidate_type, candidate_value):
    if not isinstance(candidate_value, dict):
        raise RefinementScoringError(f"{candidate_type} candidate_value must be a dict")
    if len(candidate_value) != 1:
        raise RefinementScoringError(
            f"{candidate_type} candidate_value must contain exactly one key"
        )

    _, value = next(iter(candidate_value.items()))
    if not isinstance(value, int):
        raise RefinementScoringError(f"{candidate_type} count value must be an int")
    if value < 0:
        raise RefinementScoringError(f"{candidate_type} count value may not be negative")

    components = [{"component": "base_count_signal", "score": 2}]

    if value >= 2:
        components.append({"component": "count_at_least_two", "score": 1})
    if value >= 5:
        components.append({"component": "count_at_least_five", "score": 1})

    return components


def _score_candidate(candidate, retrieval_context_included):
    candidate_type = candidate["candidate_type"]
    candidate_value = candidate["candidate_value"]

    if candidate_type == "pattern_note":
        components = _score_pattern_note(candidate_value)
    elif candidate_type in {"closeout_count", "intake_count", "target_child_core_count"}:
        components = _score_count_candidate(candidate_type, candidate_value)
    else:
        raise RefinementScoringError(f"unsupported candidate_type: {candidate_type}")

    if retrieval_context_included:
        components.append({"component": "retrieval_context_present", "score": 1})

    total_score = sum(item["score"] for item in components)

    return {
        "candidate_type": candidate["candidate_type"],
        "candidate_source": candidate["candidate_source"],
        "candidate_value": candidate["candidate_value"],
        "selection_reason": candidate["selection_reason"],
        "score_components": components,
        "total_score": total_score,
    }


def build_refinement_scoring_record(refinement_candidate_set):
    payload = _validate_candidate_set(refinement_candidate_set)

    scored_candidates = []
    for index, candidate in enumerate(payload["selected_candidates"]):
        valid_candidate = _validate_selected_candidate(candidate, index)
        scored_candidates.append(
            _score_candidate(valid_candidate, payload["retrieval_context_included"])
        )

    sorted_candidates = sorted(
        scored_candidates,
        key=lambda item: (
            -item["total_score"],
            item["candidate_type"],
            str(item["candidate_value"]),
        ),
    )

    scoring_notes = []
    if not sorted_candidates:
        scoring_notes.append("no_candidates_to_score")

    return {
        "artifact_type": "refinement_scoring_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_SCORING",
            "source_artifact_type": "refinement_candidate_set",
            "retrieval_context_included": payload["retrieval_context_included"],
            "scored_count": len(sorted_candidates),
            "scored_candidates": sorted_candidates,
            "scoring_notes": scoring_notes,
            "sealed": True,
        },
    }