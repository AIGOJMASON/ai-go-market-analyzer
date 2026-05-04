from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.core.pm.pm_pattern_influence import build_pm_pattern_influence_packet


PM_DECISION_CONDITIONING_VERSION = "v1.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _condition_risk_posture(posture: str, risk_score: int, confidence_score: int) -> str:
    if risk_score >= confidence_score + 2:
        return "high_caution"

    if posture == "cautious":
        return "cautious"

    if posture == "confident" and confidence_score > risk_score:
        return "constructive"

    return "neutral"


def _condition_review_depth(risk_posture: str) -> str:
    if risk_posture == "high_caution":
        return "expanded_pm_review"

    if risk_posture == "cautious":
        return "standard_pm_review_with_pattern_notes"

    return "standard_pm_review"


def _condition_escalation_hint(risk_posture: str, risk_score: int) -> str:
    if risk_posture == "high_caution" or risk_score >= 3:
        return "pm_review_recommended"

    if risk_posture == "cautious":
        return "operator_awareness_recommended"

    return "no_escalation_hint"


def _build_conditioning_notes(influence_packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    notes: List[Dict[str, Any]] = []

    for influence in influence_packet.get("pattern_influence", {}).get("influences", []):
        notes.append(
            {
                "source": "pm_pattern_influence",
                "type": _safe_str(influence.get("type")),
                "reason": _safe_str(influence.get("reason")),
                "severity": _safe_str(influence.get("severity")),
                "action": _safe_str(influence.get("action")),
            }
        )

    return notes[:25]


def build_pm_decision_conditioning_packet(limit: int = 500) -> Dict[str, Any]:
    influence_packet = build_pm_pattern_influence_packet(limit=limit)

    summary = influence_packet.get("summary", {})
    recommended_posture = _safe_str(summary.get("recommended_posture")) or "neutral"
    risk_score = _safe_int(summary.get("risk_score"))
    confidence_score = _safe_int(summary.get("confidence_score"))

    conditioned_risk_posture = _condition_risk_posture(
        recommended_posture,
        risk_score,
        confidence_score,
    )

    conditioned_review_depth = _condition_review_depth(conditioned_risk_posture)
    escalation_hint = _condition_escalation_hint(conditioned_risk_posture, risk_score)

    return {
        "artifact_type": "pm_decision_conditioning_packet",
        "artifact_version": PM_DECISION_CONDITIONING_VERSION,
        "generated_at": _utc_now_iso(),
        "mode": "passive",
        "authority": {
            "pm_context_only": True,
            "advisory_only": True,
            "passive_only": True,
            "can_execute": False,
            "can_mutate_state": False,
            "can_override_governance": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_write_decision": False,
            "can_auto_apply": False,
        },
        "source": {
            "source_artifact_type": influence_packet.get("artifact_type"),
            "source_artifact_version": influence_packet.get("artifact_version"),
            "source_generated_at": influence_packet.get("generated_at"),
        },
        "conditioning": {
            "recommended_posture": recommended_posture,
            "conditioned_risk_posture": conditioned_risk_posture,
            "conditioned_review_depth": conditioned_review_depth,
            "escalation_hint": escalation_hint,
            "risk_score": risk_score,
            "confidence_score": confidence_score,
            "notes": _build_conditioning_notes(influence_packet),
        },
        "use_policy": {
            "pm_may_read": True,
            "pm_may_reference_in_decision_notes": True,
            "pm_may_use_for_review_depth": True,
            "may_change_execution_gate": False,
            "may_change_watcher": False,
            "may_change_state": False,
            "may_auto_create_decision": False,
            "may_auto_transition_workflow": False,
        },
        "sealed": True,
    }


def summarize_pm_decision_conditioning(limit: int = 500) -> Dict[str, Any]:
    packet = build_pm_decision_conditioning_packet(limit=limit)

    return {
        "status": "ok",
        "artifact_type": "pm_decision_conditioning_summary",
        "artifact_version": PM_DECISION_CONDITIONING_VERSION,
        "generated_at": packet["generated_at"],
        "mode": "passive",
        "authority": packet["authority"],
        "conditioning": packet["conditioning"],
    }