from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from AI_GO.api.artifact_retrieval import ArtifactRetrievalError
from AI_GO.api.quarantine_retrieval import QuarantineRetrievalError, get_quarantine_closeout
from AI_GO.api.reviewer_registry import ReviewerRegistryError, get_reviewer_profile


REVIEW_ROOT = Path("AI_GO/receipts/market_analyzer_v1/review")


class ReviewDecisionError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_review_root() -> None:
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)


def _safe_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


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


def build_review_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ReviewDecisionError("payload must be a dict")

    closeout_id = str(payload.get("closeout_id", "")).strip()
    if not closeout_id:
        raise ReviewDecisionError("closeout_id is required")

    reviewer_id = str(payload.get("reviewer_id", "")).strip()
    if not reviewer_id:
        raise ReviewDecisionError("reviewer_id is required")

    review_outcome = _normalize_review_outcome(payload.get("review_outcome"))
    notes = str(payload.get("notes", "")).strip()

    try:
        reviewer_profile = get_reviewer_profile(reviewer_id)
    except ReviewerRegistryError as exc:
        raise ReviewDecisionError(str(exc)) from exc

    quarantine_item = _load_quarantine_context(closeout_id)
    context = _safe_dict(quarantine_item.get("closeout_artifact"))

    route_mode = str(
        quarantine_item.get("route_mode")
        or context.get("route_mode")
        or "pm_route"
    ).strip() or "pm_route"

    market_panel = _safe_dict(context.get("market_panel"))
    case_panel = _safe_dict(context.get("case_panel"))
    event_theme = str(
        context.get("event_theme")
        or market_panel.get("event_theme")
        or "unknown"
    ).strip() or "unknown"

    review_decision_id = _build_review_decision_id(closeout_id)
    pm_followup_required = _resolve_pm_followup_required(review_outcome, payload)

    return {
        "artifact_type": "review_decision",
        "sealed": True,
        "review_decision_id": review_decision_id,
        "closeout_id": closeout_id,
        "reviewer_id": reviewer_id,
        "reviewer_role": reviewer_profile.get("role"),
        "review_outcome": review_outcome,
        "pm_followup_required": pm_followup_required,
        "notes": notes,
        "reviewed_at": _utc_now_iso(),
        "route_mode": route_mode,
        "event_theme": event_theme,
        "context": {
            "case_panel": case_panel,
            "market_panel": market_panel,
            "governance_panel": _safe_dict(context.get("governance_panel")),
            "rejection_panel": _safe_dict(context.get("rejection_panel")),
            "historical_analog_panel": _safe_dict(context.get("historical_analog_panel")),
        },
    }


def persist_review_decision(review_decision: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(review_decision, dict):
        raise ReviewDecisionError("review_decision must be a dict")

    if review_decision.get("artifact_type") != "review_decision":
        raise ReviewDecisionError("artifact_type must be review_decision")

    if review_decision.get("sealed") is not True:
        raise ReviewDecisionError("review_decision must be sealed")

    review_decision_id = str(review_decision.get("review_decision_id", "")).strip()
    if not review_decision_id:
        raise ReviewDecisionError("review_decision_id is required")

    _ensure_review_root()
    output_path = REVIEW_ROOT / f"{review_decision_id}.json"
    output_path.write_text(json.dumps(review_decision, indent=2), encoding="utf-8")
    return review_decision


def get_review_decision_by_id(review_decision_id: str) -> Dict[str, Any]:
    review_decision_id = str(review_decision_id or "").strip()
    if not review_decision_id:
        raise ReviewDecisionError("review_decision_id is required")

    path = REVIEW_ROOT / f"{review_decision_id}.json"
    if not path.exists():
        raise ReviewDecisionError(f"review decision not found: {review_decision_id}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReviewDecisionError(f"invalid review decision artifact: {review_decision_id}") from exc