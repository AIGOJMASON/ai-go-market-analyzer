from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.api.learning_candidates import LearningCandidateError, list_learning_candidates


class LearningArbitrationError(ValueError):
    pass


APPROVED_STATUSES = {"approved", "deferred", "rejected"}


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _score_candidate(candidate: Dict[str, Any]) -> int:
    repeat_count = int(candidate.get("repeat_count", 0))
    confirmation_count = int(candidate.get("confirmed_count", 0))
    rejection_count = int(candidate.get("rejected_count", 0))
    review_count = int(candidate.get("review_count", 0))

    return (repeat_count * 3) + (confirmation_count * 2) + review_count - rejection_count


def _resolve_decision(candidate: Dict[str, Any]) -> Dict[str, Any]:
    score = _score_candidate(candidate)
    repeat_count = int(candidate.get("repeat_count", 0))
    confirmation_count = int(candidate.get("confirmed_count", 0))

    if repeat_count >= 3 and confirmation_count >= 2 and score >= 8:
        status = "approved"
        rationale = "Repeated reviewed pattern meets governed promotion threshold."
    elif repeat_count >= 2 and score >= 4:
        status = "deferred"
        rationale = "Pattern is emerging but does not yet meet approval threshold."
    else:
        status = "rejected"
        rationale = "Pattern strength is insufficient for governed learning promotion."

    return {
        "candidate_id": candidate.get("candidate_id"),
        "status": status,
        "score": score,
        "rationale": rationale,
        "pattern_key": candidate.get("pattern_key"),
        "source_review_ids": _safe_list(candidate.get("source_review_ids")),
        "repeat_count": repeat_count,
        "confirmed_count": confirmation_count,
        "review_count": int(candidate.get("review_count", 0)),
        "rejected_count": int(candidate.get("rejected_count", 0)),
    }


def list_learning_decisions(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise LearningArbitrationError("limit must be >= 1")
    if offset < 0:
        raise LearningArbitrationError("offset must be >= 0")

    try:
        candidate_result = list_learning_candidates(limit=5000, offset=0)
    except LearningCandidateError as exc:
        raise LearningArbitrationError(str(exc)) from exc

    candidates = _safe_list(candidate_result.get("items"))
    decisions = [_resolve_decision(candidate) for candidate in candidates]

    paged_items = decisions[offset: offset + limit]

    return {
        "artifact_type": "learning_decision_index",
        "sealed": True,
        "count": len(paged_items),
        "total": len(decisions),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }