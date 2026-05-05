from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.core.awareness.pattern_recognition import build_pattern_recognition_packet
from AI_GO.core.awareness.temporal_awareness import build_temporal_awareness_packet


PM_PATTERN_INFLUENCE_VERSION = "v1.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(v: Any) -> str:
    return str(v or "").strip()


# -------------------------
# Influence Builders
# -------------------------

def _build_risk_influence(pattern_packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    influences = []

    for signal in pattern_packet.get("pattern_signals", {}).get("signals", []):
        t = _safe_str(signal.get("type"))

        if t == "repeated_failure_cluster":
            influences.append({
                "type": "risk_increase",
                "reason": "Repeated failure pattern detected",
                "severity": signal.get("severity"),
                "action": "increase scrutiny",
            })

        if t == "duplicate_request_pattern":
            influences.append({
                "type": "integrity_risk",
                "reason": "Duplicate request pattern detected",
                "severity": signal.get("severity"),
                "action": "require validation",
            })

    return influences


def _build_confidence_influence(pattern_packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    influences = []

    for signal in pattern_packet.get("pattern_signals", {}).get("signals", []):
        if signal.get("type") == "high_frequency_action":
            influences.append({
                "type": "confidence_adjustment",
                "direction": "increase",
                "reason": "High frequency stable action detected",
                "severity": signal.get("severity"),
            })

    return influences


def _build_temporal_influence(temporal_packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    influences = []

    dominant = _safe_str(temporal_packet.get("summary", {}).get("dominant_pattern"))

    if dominant == "degradation_path":
        influences.append({
            "type": "risk_increase",
            "reason": "System shows degradation over time",
            "action": "slow decisions",
        })

    elif dominant == "recovery_path":
        influences.append({
            "type": "confidence_adjustment",
            "direction": "increase",
            "reason": "System shows recovery trend",
        })

    elif dominant == "stable_failure":
        influences.append({
            "type": "risk_increase",
            "reason": "Consistent failure pattern",
            "action": "require escalation",
        })

    return influences


# -------------------------
# Merge Influence
# -------------------------

def _merge_influences(
    risk: List[Dict[str, Any]],
    confidence: List[Dict[str, Any]],
    temporal: List[Dict[str, Any]],
) -> Dict[str, Any]:

    all_influences = risk + confidence + temporal

    risk_score = sum(1 for i in risk)
    confidence_score = sum(1 for i in confidence)

    if risk_score > confidence_score:
        posture = "cautious"
    elif confidence_score > risk_score:
        posture = "confident"
    else:
        posture = "neutral"

    return {
        "total_influences": len(all_influences),
        "risk_score": risk_score,
        "confidence_score": confidence_score,
        "recommended_posture": posture,
        "influences": all_influences[:25],
    }


# -------------------------
# Public API
# -------------------------

def build_pm_pattern_influence_packet(limit: int = 500) -> Dict[str, Any]:
    pattern_packet = build_pattern_recognition_packet(limit=limit)
    temporal_packet = build_temporal_awareness_packet(limit=limit)

    risk = _build_risk_influence(pattern_packet)
    confidence = _build_confidence_influence(pattern_packet)
    temporal = _build_temporal_influence(temporal_packet)

    merged = _merge_influences(risk, confidence, temporal)

    return {
        "artifact_type": "pm_pattern_influence_packet",
        "artifact_version": PM_PATTERN_INFLUENCE_VERSION,
        "generated_at": _utc_now_iso(),

        "authority": {
            "pm_only": True,
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_state": False,
            "can_override_governance": False,
            "can_bypass_watcher": False,
        },

        "summary": {
            "recommended_posture": merged["recommended_posture"],
            "risk_score": merged["risk_score"],
            "confidence_score": merged["confidence_score"],
        },

        "pattern_influence": merged,
    }