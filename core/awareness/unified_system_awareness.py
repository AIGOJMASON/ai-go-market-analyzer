from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from AI_GO.core.governance.governance_index_awareness import (
    build_governance_index_awareness_packet,
)

from AI_GO.core.awareness.pattern_recognition import build_pattern_recognition_packet
from AI_GO.core.awareness.temporal_awareness import build_temporal_awareness_packet
from AI_GO.core.memory.memory_integration import load_system_memory_index
from AI_GO.core.pm.pm_decision_conditioning import build_pm_decision_conditioning_packet
from AI_GO.core.pm.pm_pattern_influence import build_pm_pattern_influence_packet


UNIFIED_SYSTEM_AWARENESS_VERSION = "v1.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _derive_system_posture(
    *,
    governance_awareness: Dict[str, Any],
    memory_index: Dict[str, Any],
    temporal_awareness: Dict[str, Any],
    pattern_recognition: Dict[str, Any],
    pm_influence: Dict[str, Any],
    pm_conditioning: Dict[str, Any],
) -> Dict[str, Any]:
    governance_summary = _safe_dict(governance_awareness.get("summary"))
    temporal_summary = _safe_dict(temporal_awareness.get("summary"))
    pattern_summary = _safe_dict(pattern_recognition.get("summary"))
    conditioning = _safe_dict(pm_conditioning.get("conditioning"))

    anomaly_count = _safe_int(governance_summary.get("anomaly_count"))
    memory_count = _safe_int(memory_index.get("record_count"))
    sequence_count = _safe_int(temporal_summary.get("sequence_count"))
    signal_count = _safe_int(pattern_summary.get("signal_count"))

    conditioned_risk_posture = _safe_str(conditioning.get("conditioned_risk_posture")) or "neutral"
    escalation_hint = _safe_str(conditioning.get("escalation_hint")) or "none"

    if anomaly_count >= 5 or conditioned_risk_posture == "high_caution":
        system_posture = "high_caution"
    elif anomaly_count > 0 or signal_count > 0 or conditioned_risk_posture == "cautious":
        system_posture = "cautious"
    elif memory_count > 0 and sequence_count > 0:
        system_posture = "aware"
    else:
        system_posture = "limited_data"

    return {
        "system_posture": system_posture,
        "conditioned_risk_posture": conditioned_risk_posture,
        "escalation_hint": escalation_hint,
        "anomaly_count": anomaly_count,
        "memory_record_count": memory_count,
        "sequence_count": sequence_count,
        "pattern_signal_count": signal_count,
    }


def build_unified_system_awareness_packet(limit: int = 500) -> Dict[str, Any]:
    governance_awareness = build_governance_index_awareness_packet(limit=limit)
    memory_index = load_system_memory_index()
    temporal_awareness = build_temporal_awareness_packet(limit=limit)
    pattern_recognition = build_pattern_recognition_packet(limit=limit)
    pm_influence = build_pm_pattern_influence_packet(limit=limit)
    pm_conditioning = build_pm_decision_conditioning_packet(limit=limit)

    system_posture = _derive_system_posture(
        governance_awareness=governance_awareness,
        memory_index=memory_index,
        temporal_awareness=temporal_awareness,
        pattern_recognition=pattern_recognition,
        pm_influence=pm_influence,
        pm_conditioning=pm_conditioning,
    )

    return {
        "artifact_type": "unified_system_awareness_packet",
        "artifact_version": UNIFIED_SYSTEM_AWARENESS_VERSION,
        "generated_at": _utc_now_iso(),
        "mode": "read_only_system_brain_view",
        "authority": {
            "read_only": True,
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_state": False,
            "can_override_governance": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_auto_create_decision": False,
            "can_auto_apply_conditioning": False,
        },
        "summary": system_posture,
        "surfaces": {
            "governance_awareness": governance_awareness,
            "memory_index": {
                "artifact_type": memory_index.get("artifact_type"),
                "artifact_version": memory_index.get("artifact_version"),
                "generated_at": memory_index.get("generated_at"),
                "record_count": memory_index.get("record_count", 0),
                "by_type": memory_index.get("by_type", {}),
                "authority": memory_index.get("authority", {}),
            },
            "temporal_awareness": temporal_awareness,
            "pattern_recognition": pattern_recognition,
            "pm_pattern_influence": pm_influence,
            "pm_decision_conditioning": pm_conditioning,
        },
        "use_policy": {
            "operator_may_read": True,
            "pm_may_read": True,
            "ai_may_read_later": True,
            "may_support_operator_surface": True,
            "may_support_ai_interpretation_later": True,
            "may_change_execution_gate": False,
            "may_change_watcher": False,
            "may_change_state": False,
            "may_write_decisions": False,
            "may_dispatch_actions": False,
        },
        "sealed": True,
    }


def summarize_unified_system_awareness(limit: int = 500) -> Dict[str, Any]:
    packet = build_unified_system_awareness_packet(limit=limit)

    return {
        "status": "ok",
        "artifact_type": "unified_system_awareness_summary",
        "artifact_version": UNIFIED_SYSTEM_AWARENESS_VERSION,
        "generated_at": packet["generated_at"],
        "mode": packet["mode"],
        "authority": packet["authority"],
        "summary": packet["summary"],
    }