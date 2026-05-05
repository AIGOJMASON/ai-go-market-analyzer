from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from secrets import token_hex
from typing import Any, Dict, List

from AI_GO.api.learning_arbitration import LearningArbitrationError, list_learning_decisions
from AI_GO.api.reviewer_registry import ReviewerRegistryError, get_reviewer_profile
from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import receipts_root


LEARNING_OVERRIDE_MUTATION_CLASS = "learning_override_persistence"
LEARNING_OVERRIDE_PERSISTENCE_TYPE = "filesystem"
LEARNING_OVERRIDE_ADVISORY_ONLY = False


class LearningOverrideError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _learning_override_root() -> Path:
    return receipts_root() / "market_analyzer_v1" / "learning_override"


def _classification_block() -> Dict[str, Any]:
    return {
        "mutation_class": LEARNING_OVERRIDE_MUTATION_CLASS,
        "persistence_type": LEARNING_OVERRIDE_PERSISTENCE_TYPE,
        "advisory_only": LEARNING_OVERRIDE_ADVISORY_ONLY,
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "governed_persistence": True,
        "learning_override": True,
        "can_execute": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
    }


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _normalize_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "learning_override_record")
    normalized["sealed"] = True
    normalized["classification"] = _classification_block()
    normalized["authority"] = _authority_block()
    normalized["persistence_type"] = LEARNING_OVERRIDE_PERSISTENCE_TYPE
    normalized["mutation_class"] = LEARNING_OVERRIDE_MUTATION_CLASS
    normalized["advisory_only"] = LEARNING_OVERRIDE_ADVISORY_ONLY
    normalized["execution_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_record(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": LEARNING_OVERRIDE_PERSISTENCE_TYPE,
        "mutation_class": LEARNING_OVERRIDE_MUTATION_CLASS,
        "advisory_only": LEARNING_OVERRIDE_ADVISORY_ONLY,
        "authority_metadata": _authority_block(),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {key: value for key, value in kwargs.items() if key in signature.parameters}

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _get_candidate_from_decision_record(candidate_id: str) -> Dict[str, Any]:
    try:
        decision_index = list_learning_decisions(limit=5000, offset=0)
    except LearningArbitrationError as exc:
        raise LearningOverrideError(str(exc)) from exc

    for item in _safe_list(decision_index.get("items")):
        if isinstance(item, dict) and str(item.get("candidate_id")) == candidate_id:
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

    return _normalize_record(
        {
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
            "route_targets": ["refinement"],
        }
    )


def persist_learning_override(record: Dict[str, Any]) -> str:
    override_id = str(record.get("override_id", "")).strip()
    if not override_id:
        raise LearningOverrideError("override_id is required")

    root = _learning_override_root()
    root.mkdir(parents=True, exist_ok=True)

    path = root / f"{override_id}.json"
    return _governed_write(path, record)


def create_learning_override(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = build_learning_override(payload)
    path = persist_learning_override(record)
    record["path"] = path
    return record


def get_learning_override(override_id: str) -> Dict[str, Any]:
    clean_id = str(override_id or "").strip()
    if not clean_id:
        raise LearningOverrideError("override_id is required")

    path = _learning_override_root() / f"{clean_id}.json"
    payload = _read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def list_learning_overrides(*, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    if limit < 1:
        raise LearningOverrideError("limit must be >= 1")
    if offset < 0:
        raise LearningOverrideError("offset must be >= 0")

    root = _learning_override_root()
    items: List[Dict[str, Any]] = []

    if root.exists():
        for path in sorted(root.glob("*.json"), reverse=True):
            payload = _read_json(path, {})
            if isinstance(payload, dict):
                items.append(payload)

    paged = items[offset: offset + limit]

    return {
        "artifact_type": "learning_override_index",
        "sealed": True,
        "count": len(paged),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": paged,
    }