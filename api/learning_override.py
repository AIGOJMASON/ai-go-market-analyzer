from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from secrets import token_hex
from typing import Any, Dict, List

from AI_GO.api.learning_arbitration import LearningArbitrationError, list_learning_decisions
from AI_GO.api.reviewer_registry import ReviewerRegistryError, get_reviewer_profile


LEARNING_OVERRIDE_ROOT = Path("AI_GO/receipts/market_analyzer_v1/learning_override")


class LearningOverrideError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_root() -> None:
    LEARNING_OVERRIDE_ROOT.mkdir(parents=True, exist_ok=True)


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _get_candidate_from_decision_record(candidate_id: str) -> Dict[str, Any]:
    try:
        decision_index = list_learning_decisions(limit=5000, offset=0)
    except LearningArbitrationError as exc:
        raise LearningOverrideError(str(exc)) from exc

    for item in _safe_list(decision_index.get("items")):
        if not isinstance(item, dict):
            continue
        if str(item.get("candidate_id")) == candidate_id:
            return item

    raise LearningOverrideError(f"learning decision not found for candidate_id: {candidate_id}")


def build_learning_override(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise LearningOverrideError("payload must be a dict")

    candidate_id = str(payload.get("candidate_id", "")).strip()
    reviewer_id = str(payload.get("reviewer_id", "")).strip()
    notes = str(payload.get("notes", "")).strip()

    if not candidate_id:
        raise LearningOverrideError("candidate_id is required")
    if not reviewer_id:
        raise LearningOverrideError("reviewer_id is required")

    try:
        reviewer = get_reviewer_profile(reviewer_id)
    except ReviewerRegistryError as exc:
        raise LearningOverrideError(str(exc)) from exc

    candidate = _get_candidate_from_decision_record(candidate_id)
    if str(candidate.get("status")) != "deferred":
        raise LearningOverrideError("only deferred learning candidates may be overridden")

    override_id = f"lovr_{token_hex(8)}"
    promoted_routes = ["refinement"]

    return {
        "artifact_type": "learning_override_record",
        "sealed": True,
        "override_id": override_id,
        "candidate_id": candidate_id,
        "reviewer_id": reviewer_id,
        "reviewer_role": reviewer.get("role"),
        "override_outcome": "approved",
        "notes": notes,
        "created_at": _utc_now_iso(),
        "source_decision": {
            "candidate_id": candidate.get("candidate_id"),
            "status": candidate.get("status"),
            "score": candidate.get("score"),
            "pattern_key": candidate.get("pattern_key"),
            "source_review_ids": candidate.get("source_review_ids", []),
            "repeat_count": candidate.get("repeat_count", 0),
            "confirmed_count": candidate.get("confirmed_count", 0),
            "review_count": candidate.get("review_count", 0),
            "rejected_count": candidate.get("rejected_count", 0),
        },
        "route_targets": promoted_routes,
    }


def persist_learning_override(override_record: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(override_record, dict):
        raise LearningOverrideError("override_record must be a dict")
    if override_record.get("artifact_type") != "learning_override_record":
        raise LearningOverrideError("artifact_type must be learning_override_record")
    if override_record.get("sealed") is not True:
        raise LearningOverrideError("override_record must be sealed")

    override_id = str(override_record.get("override_id", "")).strip()
    if not override_id:
        raise LearningOverrideError("override_id is required")

    _ensure_root()
    path = LEARNING_OVERRIDE_ROOT / f"{override_id}.json"
    path.write_text(json.dumps(override_record, indent=2), encoding="utf-8")
    return override_record


def get_learning_override_by_id(override_id: str) -> Dict[str, Any]:
    override_id = str(override_id or "").strip()
    if not override_id:
        raise LearningOverrideError("override_id is required")

    path = LEARNING_OVERRIDE_ROOT / f"{override_id}.json"
    if not path.exists():
        raise LearningOverrideError(f"learning override not found: {override_id}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LearningOverrideError(f"invalid learning override artifact: {override_id}") from exc


def list_learning_overrides(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise LearningOverrideError("limit must be >= 1")
    if offset < 0:
        raise LearningOverrideError("offset must be >= 0")

    if not LEARNING_OVERRIDE_ROOT.exists():
        items: List[Dict[str, Any]] = []
    else:
        items = []
        for path in sorted(LEARNING_OVERRIDE_ROOT.glob("*.json"), reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                items.append(payload)

    paged_items = items[offset: offset + limit]

    return {
        "artifact_type": "learning_override_index",
        "sealed": True,
        "count": len(paged_items),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }