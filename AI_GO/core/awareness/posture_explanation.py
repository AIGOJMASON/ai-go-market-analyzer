from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.core.awareness.operator_system_brain_surface import (
    build_operator_system_brain_surface,
)


POSTURE_EXPLANATION_VERSION = "v1.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _explain_posture(system_brain: Dict[str, Any]) -> List[Dict[str, Any]]:
    unified = _safe_dict(system_brain.get("unified_awareness_summary"))
    cross_run = _safe_dict(system_brain.get("cross_run_summary"))

    system_posture = _safe_str(unified.get("system_posture")) or "unknown"
    risk_posture = _safe_str(unified.get("conditioned_risk_posture")) or "unknown"
    anomaly_count = _safe_int(unified.get("anomaly_count"))
    pattern_signal_count = _safe_int(unified.get("pattern_signal_count"))
    memory_record_count = _safe_int(unified.get("memory_record_count"))
    sequence_count = _safe_int(unified.get("sequence_count"))

    cross_run_posture = _safe_str(cross_run.get("cross_run_posture")) or "unknown"
    drift = _safe_str(cross_run.get("drift")) or "unknown"
    persistent_signal_count = _safe_int(cross_run.get("persistent_signal_count"))

    reasons: List[Dict[str, Any]] = []

    if anomaly_count > 0:
        reasons.append(
            {
                "reason_id": "governance_anomalies_present",
                "severity": "medium",
                "summary": "Governance anomalies are present.",
                "evidence": {"anomaly_count": anomaly_count},
                "operator_meaning": "The system should not be treated as fully clean until these anomalies are reviewed.",
            }
        )

    if pattern_signal_count > 0:
        reasons.append(
            {
                "reason_id": "pattern_signals_present",
                "severity": "medium",
                "summary": "Pattern signals are present.",
                "evidence": {"pattern_signal_count": pattern_signal_count},
                "operator_meaning": "The system is detecting repeated behavior, which should be reviewed before relying on the posture.",
            }
        )

    if persistent_signal_count > 0:
        reasons.append(
            {
                "reason_id": "persistent_cross_run_pattern",
                "severity": "medium",
                "summary": "A cross-run pattern is persisting.",
                "evidence": {
                    "cross_run_posture": cross_run_posture,
                    "persistent_signal_count": persistent_signal_count,
                },
                "operator_meaning": "The pattern is not isolated to one snapshot. It has appeared across awareness history.",
            }
        )

    if drift in {"worsening", "volatile"}:
        reasons.append(
            {
                "reason_id": "cross_run_drift_attention",
                "severity": "high",
                "summary": f"Cross-run drift is {drift}.",
                "evidence": {"drift": drift},
                "operator_meaning": "The operator should slow review and inspect recent history.",
            }
        )

    if memory_record_count == 0 or sequence_count == 0:
        reasons.append(
            {
                "reason_id": "limited_history",
                "severity": "low",
                "summary": "System history is limited.",
                "evidence": {
                    "memory_record_count": memory_record_count,
                    "sequence_count": sequence_count,
                },
                "operator_meaning": "The system has less historical context than desired.",
            }
        )

    if not reasons and system_posture in {"aware", "neutral"}:
        reasons.append(
            {
                "reason_id": "clean_awareness_window",
                "severity": "low",
                "summary": "No major caution driver is present in the current awareness window.",
                "evidence": {
                    "system_posture": system_posture,
                    "conditioned_risk_posture": risk_posture,
                },
                "operator_meaning": "The current posture appears stable, but this still does not grant execution authority.",
            }
        )

    return reasons


def _build_plain_explanation(
    *,
    system_posture: str,
    risk_posture: str,
    reasons: List[Dict[str, Any]],
) -> str:
    if not reasons:
        return (
            f"The system posture is {system_posture}. "
            f"The conditioned risk posture is {risk_posture}. "
            "No explicit posture drivers were found in this awareness packet."
        )

    reason_text = "; ".join(_safe_str(reason.get("summary")) for reason in reasons)
    return (
        f"The system posture is {system_posture} because: {reason_text}. "
        f"The conditioned risk posture is {risk_posture}. "
        "This explanation is advisory only and does not grant execution authority."
    )


def build_posture_explanation_packet(limit: int = 500) -> Dict[str, Any]:
    surface = build_operator_system_brain_surface(limit=limit)
    system_brain = _safe_dict(surface.get("system_brain"))
    unified = _safe_dict(system_brain.get("unified_awareness_summary"))

    system_posture = _safe_str(unified.get("system_posture")) or "unknown"
    risk_posture = _safe_str(unified.get("conditioned_risk_posture")) or "unknown"

    reasons = _explain_posture(system_brain)

    return {
        "artifact_type": "posture_explanation_packet",
        "artifact_version": POSTURE_EXPLANATION_VERSION,
        "generated_at": _utc_now_iso(),
        "mode": "deterministic_read_only_explanation",
        "authority": {
            "read_only": True,
            "advisory_only": True,
            "deterministic": True,
            "ai_generated": False,
            "can_execute": False,
            "can_mutate_state": False,
            "can_override_governance": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_create_decision": False,
            "can_escalate_automatically": False,
        },
        "summary": {
            "system_posture": system_posture,
            "conditioned_risk_posture": risk_posture,
            "reason_count": len(reasons),
            "plain_explanation": _build_plain_explanation(
                system_posture=system_posture,
                risk_posture=risk_posture,
                reasons=reasons,
            ),
        },
        "reasons": reasons,
        "source": {
            "source_artifact_type": surface.get("artifact_type"),
            "source_artifact_version": surface.get("artifact_version"),
            "source_generated_at": surface.get("generated_at"),
        },
        "use_policy": {
            "operator_may_read": True,
            "pm_may_read": True,
            "ai_may_read_later": True,
            "may_display_in_dashboard": True,
            "may_explain_posture": True,
            "may_change_execution_gate": False,
            "may_change_watcher": False,
            "may_change_state": False,
            "may_write_decisions": False,
            "may_dispatch_actions": False,
        },
        "sealed": True,
    }