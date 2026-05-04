from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.api.quarantine_retrieval import QuarantineRetrievalError, get_quarantine_closeout
from AI_GO.api.reviewer_registry import ReviewerRegistryError, get_reviewer_profile
from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import receipts_root


REVIEW_MUTATION_CLASS = "market_analyzer_review_decision_persistence"
REVIEW_PERSISTENCE_TYPE = "market_analyzer_review_decision"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": False,
    "can_execute": False,
    "can_mutate_runtime": False,
    "can_mutate_recommendation": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "authority_scope": "market_analyzer_review_decision_artifact",
}


class ReviewDecisionError(ValueError):
    pass


def _review_root() -> Path:
    return receipts_root() / "market_analyzer_v1" / "review"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _normalize_review_outcome(value: Any) -> str:
    text = str(value or "").strip().lower()
    aliases = {
        "approve": "approved",
        "approved": "approved",
        "confirm": "approved",
        "confirmed": "approved",
        "reject": "rejected",
        "rejected": "rejected",
        "pm_review": "pm_review",
        "pm-followup": "pm_review",
        "pm_followup": "pm_review",
        "defer": "deferred",
        "deferred": "deferred",
    }
    normalized = aliases.get(text)
    if not normalized:
        raise ReviewDecisionError("review_outcome must be one of approved, rejected, deferred, pm_review")
    return normalized


def _build_review_decision_id(closeout_id: str) -> str:
    suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"review_{closeout_id}_{suffix}"


def _resolve_pm_followup_required(review_outcome: str, payload: Dict[str, Any]) -> bool:
    if "pm_followup_required" in payload:
        return bool(payload["pm_followup_required"])
    return review_outcome == "pm_review"


def _load_quarantine_context(closeout_id: str) -> Dict[str, Any]:
    try:
        return get_quarantine_closeout(closeout_id)
    except QuarantineRetrievalError as exc:
        raise ReviewDecisionError(str(exc)) from exc


def _normalize_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "market_analyzer_review_decision")
    normalized["artifact_version"] = "v1"
    normalized["sealed"] = True
    normalized["persistence_type"] = REVIEW_PERSISTENCE_TYPE
    normalized["mutation_class"] = REVIEW_MUTATION_CLASS
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_record(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": REVIEW_PERSISTENCE_TYPE,
        "mutation_class": REVIEW_MUTATION_CLASS,
        "advisory_only": False,
        "authority_metadata": dict(AUTHORITY_METADATA),
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


def build_review_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ReviewDecisionError("payload must be a dict")

    closeout_id = str(payload.get("closeout_id", "")).strip()
    reviewer_id = str(payload.get("reviewer_id", "")).strip()
    review_outcome = _normalize_review_outcome(
        payload.get("review_outcome") or payload.get("decision")
    )
    notes = str(payload.get("notes", "")).strip()

    if not closeout_id:
        raise ReviewDecisionError("closeout_id is required")
    if not reviewer_id:
        raise ReviewDecisionError("reviewer_id is required")

    try:
        reviewer = get_reviewer_profile(reviewer_id)
    except ReviewerRegistryError as exc:
        raise ReviewDecisionError(str(exc)) from exc

    quarantine_context = _load_quarantine_context(closeout_id)
    pm_followup_required = _resolve_pm_followup_required(review_outcome, payload)

    return _normalize_record(
        {
            "artifact_type": "market_analyzer_review_decision",
            "review_decision_id": _build_review_decision_id(closeout_id),
            "closeout_id": closeout_id,
            "reviewer_id": reviewer_id,
            "reviewer_role": reviewer.get("role"),
            "review_outcome": review_outcome,
            "pm_followup_required": pm_followup_required,
            "notes": notes,
            "created_at": _utc_now_iso(),
            "source_quarantine": {
                "closeout_id": quarantine_context.get("closeout_id"),
                "closeout_status": quarantine_context.get("closeout_status"),
                "requires_review": quarantine_context.get("requires_review"),
                "issues": quarantine_context.get("issues", []),
            },
        }
    )


def persist_review_decision(record: Dict[str, Any]) -> str:
    review_decision_id = str(record.get("review_decision_id", "")).strip()
    if not review_decision_id:
        raise ReviewDecisionError("review_decision_id is required")

    root = _review_root()
    root.mkdir(parents=True, exist_ok=True)

    path = root / f"{review_decision_id}.json"
    return _governed_write(path, record)


def create_review_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = build_review_decision(payload)
    path = persist_review_decision(record)
    record["path"] = path
    return record


def get_review_decision(review_decision_id: str) -> Dict[str, Any]:
    clean_id = str(review_decision_id or "").strip()
    if not clean_id:
        raise ReviewDecisionError("review_decision_id is required")

    path = _review_root() / f"{clean_id}.json"
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return _safe_dict(payload)


def list_review_decisions(*, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    if limit < 1:
        raise ReviewDecisionError("limit must be >= 1")
    if offset < 0:
        raise ReviewDecisionError("offset must be >= 0")

    root = _review_root()
    items: List[Dict[str, Any]] = []

    if root.exists():
        for path in sorted(root.glob("*.json"), reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(payload, dict):
                items.append(payload)

    paged = items[offset: offset + limit]

    return {
        "artifact_type": "market_analyzer_review_decision_index",
        "sealed": True,
        "count": len(paged),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": _safe_list(paged),
    }