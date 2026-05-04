from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from AI_GO.core.system_brain.external_memory_advisory import (
    build_external_memory_system_brain_advisory,
    load_external_memory_system_brain_advisory,
)


SYSTEM_BRAIN_VERSION = "v5F.4"


FORBIDDEN_AUTHORITY_TRUE = [
    "can_execute",
    "can_mutate_state",
    "can_mutate_runtime",
    "can_override_governance",
    "can_override_state_authority",
    "can_override_canon",
    "can_override_watcher",
    "can_override_execution_gate",
    "can_create_decision",
    "can_escalate_automatically",
    "can_route_work",
    "execution_allowed",
    "mutation_allowed",
]


FORBIDDEN_USE_TRUE = [
    "may_change_execution_gate",
    "may_change_watcher",
    "may_change_state",
    "may_change_state_authority",
    "may_change_canon",
    "may_change_runtime",
    "may_change_recommendations",
    "may_change_pm_strategy",
    "may_write_decisions",
    "may_dispatch_actions",
    "may_activate_child_cores",
    "may_override_governance",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _call_builder(
    builder: Callable[..., Dict[str, Any]],
    *,
    limit: int,
) -> Dict[str, Any]:
    try:
        result = builder(limit=limit)
        return _safe_dict(result)
    except TypeError:
        try:
            result = builder()
            return _safe_dict(result)
        except Exception as exc:
            return {
                "status": "unavailable",
                "error": f"{type(exc).__name__}: {exc}",
            }
    except Exception as exc:
        return {
            "status": "unavailable",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _load_smi_posture(limit: int) -> Dict[str, Any]:
    try:
        from AI_GO.core.awareness.smi_pattern_posture_reader import (
            build_smi_pattern_posture_packet,
        )

        return _safe_dict(build_smi_pattern_posture_packet(history_limit=limit))
    except Exception as exc:
        return {
            "status": "unavailable",
            "artifact_type": "smi_pattern_posture_packet",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _load_temporal_awareness(limit: int) -> Dict[str, Any]:
    try:
        from AI_GO.core.awareness.temporal_awareness import (
            build_temporal_awareness_packet,
        )

        return _call_builder(build_temporal_awareness_packet, limit=limit)
    except Exception as exc:
        return {
            "status": "unavailable",
            "artifact_type": "temporal_awareness_packet",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _load_pattern_recognition(limit: int) -> Dict[str, Any]:
    try:
        from AI_GO.core.awareness.pattern_recognition import (
            build_pattern_recognition_packet,
        )

        return _call_builder(build_pattern_recognition_packet, limit=limit)
    except Exception as exc:
        return {
            "status": "unavailable",
            "artifact_type": "pattern_recognition_packet",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _load_unified_awareness(limit: int) -> Dict[str, Any]:
    try:
        from AI_GO.core.awareness.unified_system_awareness import (
            build_unified_system_awareness_packet,
        )

        return _call_builder(build_unified_system_awareness_packet, limit=limit)
    except Exception as exc:
        return {
            "status": "unavailable",
            "artifact_type": "unified_system_awareness_packet",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _load_cross_run(limit: int) -> Dict[str, Any]:
    try:
        from AI_GO.core.awareness.cross_run_intelligence import (
            build_cross_run_intelligence_packet,
        )

        return _call_builder(build_cross_run_intelligence_packet, limit=limit)
    except Exception as exc:
        return {
            "status": "unavailable",
            "artifact_type": "cross_run_intelligence_packet",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _authority() -> Dict[str, Any]:
    return {
        "read_only": True,
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_state": False,
        "can_mutate_runtime": False,
        "can_override_governance": False,
        "can_override_state_authority": False,
        "can_override_canon": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_create_decision": False,
        "can_escalate_automatically": False,
        "can_route_work": False,
        "can_block_request": False,
        "can_allow_request": False,
        "execution_allowed": False,
        "mutation_allowed": False,
    }


def _use_policy() -> Dict[str, Any]:
    return {
        "operator_may_read": True,
        "pm_may_read": True,
        "ai_may_read_later": True,
        "may_display_in_dashboard": True,
        "may_display_external_memory_context": True,
        "may_change_execution_gate": False,
        "may_change_watcher": False,
        "may_change_state": False,
        "may_change_state_authority": False,
        "may_change_canon": False,
        "may_change_runtime": False,
        "may_change_recommendations": False,
        "may_change_pm_strategy": False,
        "may_write_decisions": False,
        "may_dispatch_actions": False,
        "may_activate_child_cores": False,
        "may_override_governance": False,
    }


def _collect_source_errors(*packets: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for packet in packets:
        if not isinstance(packet, dict):
            continue

        status = _safe_str(packet.get("status"))
        artifact_type = _safe_str(packet.get("artifact_type") or packet.get("source"))

        if status == "unavailable":
            errors.append(
                f"{artifact_type or 'unknown_source'} unavailable: {packet.get('error') or packet.get('reason') or 'unknown'}"
            )

    return errors


def _extract_summary(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("summary"))


def _extract_posture(packet: Dict[str, Any], *keys: str, default: str = "unknown") -> str:
    for key in keys:
        value = _safe_str(packet.get(key))
        if value:
            return value

    summary = _extract_summary(packet)
    for key in keys:
        value = _safe_str(summary.get(key))
        if value:
            return value

    return default


def _derive_pattern_signal_count(
    *,
    pattern_recognition: Dict[str, Any],
    unified_awareness: Dict[str, Any],
    cross_run: Dict[str, Any],
    external_memory: Dict[str, Any],
) -> int:
    total = 0

    for packet in (pattern_recognition, unified_awareness, cross_run):
        summary = _safe_dict(packet.get("summary"))
        for key in (
            "pattern_signal_count",
            "pattern_count",
            "signal_count",
            "persistent_signal_count",
        ):
            value = summary.get(key)
            if isinstance(value, int):
                total += value
                break

    retrieval = _safe_dict(external_memory.get("retrieval"))
    returned_count = retrieval.get("returned_count")
    if isinstance(returned_count, int):
        total += returned_count

    return total


def _derive_risk_posture(
    *,
    smi_posture_value: str,
    unified_posture: str,
    cross_run_drift: str,
    external_memory_strength: str,
    source_errors: List[str],
) -> str:
    if source_errors:
        return "cautious"

    if smi_posture_value in {"cautious"}:
        return "cautious"

    if cross_run_drift in {"worsening", "volatile"}:
        return "cautious"

    if unified_posture in {"degraded", "warning", "cautious"}:
        return "cautious"

    if external_memory_strength in {"strong", "moderate"}:
        return "stable_observed"

    if smi_posture_value == "cold_start":
        return "cold_start"

    if smi_posture_value in {"pattern_observed", "stable_observed"}:
        return "stable_observed"

    return "unknown"


def _build_plain_summary(
    *,
    risk_posture: str,
    smi_posture_value: str,
    cross_run_drift: str,
    pattern_signal_count: int,
    external_memory: Dict[str, Any],
) -> str:
    external_memory_strength = _safe_str(external_memory.get("pattern_strength"))

    if risk_posture == "cold_start":
        return (
            "System Brain is online in advisory mode. Continuity history is still cold, "
            "so posture should be treated as early context only."
        )

    if risk_posture == "cautious":
        return (
            "System Brain is online in advisory mode. Current posture is cautious due to "
            "continuity pressure, source uncertainty, memory unavailability, or cross-run drift."
        )

    if external_memory_strength in {"strong", "moderate"}:
        return (
            "System Brain is online in advisory mode. External Memory shows advisory pattern "
            "context, but it remains candidate signal only and grants no authority."
        )

    if pattern_signal_count > 0:
        return (
            "System Brain is online in advisory mode. Recurring patterns are visible, "
            "but they remain context only and do not grant authority."
        )

    return (
        "System Brain is online in advisory mode. Available awareness surfaces do not "
        "show immediate continuity pressure."
    )


def _build_operator_cards(
    *,
    risk_posture: str,
    smi_posture_value: str,
    unified_posture: str,
    cross_run_drift: str,
    pattern_signal_count: int,
    source_errors: List[str],
    external_memory: Dict[str, Any],
) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = [
        {
            "card_id": "system_brain_mode",
            "label": "System Brain Mode",
            "value": "advisory_only",
            "meaning": "System Brain may summarize posture, but may not execute, mutate state, or override governance.",
        },
        {
            "card_id": "risk_posture",
            "label": "Risk Posture",
            "value": risk_posture,
            "meaning": "Advisory posture derived from SMI, awareness, cross-run, and External Memory context.",
        },
        {
            "card_id": "smi_posture",
            "label": "SMI Posture",
            "value": smi_posture_value,
            "meaning": "Continuity posture from the SMI pattern posture reader.",
        },
        {
            "card_id": "unified_posture",
            "label": "Unified Awareness",
            "value": unified_posture,
            "meaning": "Current unified awareness posture when available.",
        },
        {
            "card_id": "cross_run_drift",
            "label": "Cross-Run Drift",
            "value": cross_run_drift,
            "meaning": "Advisory cross-run drift posture.",
        },
        {
            "card_id": "pattern_signals",
            "label": "Pattern Signals",
            "value": pattern_signal_count,
            "meaning": "Visible advisory pattern pressure. This value cannot grant authority.",
        },
    ]

    external_card = _safe_dict(external_memory.get("operator_card"))
    if external_card:
        cards.append(external_card)

    if source_errors:
        cards.append(
            {
                "card_id": "source_errors",
                "label": "Source Errors",
                "value": len(source_errors),
                "meaning": "One or more advisory sources were unavailable. System authority is unchanged.",
            }
        )

    return cards


def _build_watch_list(
    *,
    risk_posture: str,
    cross_run_drift: str,
    source_errors: List[str],
    external_memory: Dict[str, Any],
) -> List[str]:
    watch: List[str] = []

    if risk_posture == "cautious":
        watch.append(
            "System Brain posture is cautious. Continue with elevated review discipline."
        )

    if cross_run_drift in {"watch", "worsening", "volatile"}:
        watch.append(
            f"Cross-run drift is {cross_run_drift}. Treat this as advisory pressure only."
        )

    watch.extend(_safe_list(external_memory.get("what_to_watch")))

    if source_errors:
        watch.append(
            "One or more advisory sources were unavailable. Do not infer system truth from missing advisory context."
        )

    if not watch:
        watch.append(
            "No immediate advisory pressure detected. Controlling layers remain State Authority, Watcher, Canon, and Execution Gate."
        )

    return watch


def _validate_authority_packet(packet: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    authority = _safe_dict(packet.get("authority"))
    use_policy = _safe_dict(packet.get("use_policy"))

    for key in FORBIDDEN_AUTHORITY_TRUE:
        if authority.get(key) is True:
            errors.append(f"forbidden_authority_true:{key}")

    for key in FORBIDDEN_USE_TRUE:
        if use_policy.get(key) is True:
            errors.append(f"forbidden_use_true:{key}")

    return errors


def build_system_brain_context(
    *,
    limit: int = 500,
    external_memory_context: Optional[Dict[str, Any]] = None,
    external_memory_promotion: Optional[Dict[str, Any]] = None,
    include_external_memory: bool = True,
) -> Dict[str, Any]:
    safe_limit = max(1, min(int(limit), 1000))

    smi_posture = _load_smi_posture(safe_limit)
    temporal_awareness = _load_temporal_awareness(safe_limit)
    pattern_recognition = _load_pattern_recognition(safe_limit)
    unified_awareness = _load_unified_awareness(safe_limit)
    cross_run = _load_cross_run(safe_limit)

    if external_memory_context is not None or external_memory_promotion is not None:
        external_memory = build_external_memory_system_brain_advisory(
            retrieval_context=external_memory_context,
            promotion_context=external_memory_promotion,
        )
    elif include_external_memory:
        external_memory = load_external_memory_system_brain_advisory(limit=5)
    else:
        external_memory = build_external_memory_system_brain_advisory()

    source_errors = _collect_source_errors(
        smi_posture,
        temporal_awareness,
        pattern_recognition,
        unified_awareness,
        cross_run,
        external_memory,
    )

    smi_posture_value = _extract_posture(
        smi_posture,
        "posture",
        "smi_posture",
        default="unknown",
    )
    unified_posture = _extract_posture(
        unified_awareness,
        "posture",
        "system_posture",
        "unified_posture",
        default="unknown",
    )
    cross_run_drift = _extract_posture(
        cross_run,
        "drift",
        "drift_posture",
        "cross_run_drift",
        default="unknown",
    )
    cross_run_posture = _extract_posture(
        cross_run,
        "cross_run_posture",
        "posture",
        default="unknown",
    )

    external_memory_strength = _safe_str(external_memory.get("pattern_strength")) or "none"

    pattern_signal_count = _derive_pattern_signal_count(
        pattern_recognition=pattern_recognition,
        unified_awareness=unified_awareness,
        cross_run=cross_run,
        external_memory=external_memory,
    )

    risk_posture = _derive_risk_posture(
        smi_posture_value=smi_posture_value,
        unified_posture=unified_posture,
        cross_run_drift=cross_run_drift,
        external_memory_strength=external_memory_strength,
        source_errors=source_errors,
    )

    system_posture = "cautious" if risk_posture == "cautious" else risk_posture

    context: Dict[str, Any] = {
        "artifact_type": "system_brain_context",
        "artifact_version": SYSTEM_BRAIN_VERSION,
        "generated_at": _utc_now_iso(),
        "status": "ok",
        "mode": "read_only",
        "source": "SYSTEM_BRAIN",
        "sealed": True,
        "system_posture": system_posture,
        "risk_posture": risk_posture,
        "smi_posture": smi_posture_value,
        "cross_run_posture": cross_run_posture,
        "drift": cross_run_drift,
        "pattern_signal_count": pattern_signal_count,
        "plain_summary": _build_plain_summary(
            risk_posture=risk_posture,
            smi_posture_value=smi_posture_value,
            cross_run_drift=cross_run_drift,
            pattern_signal_count=pattern_signal_count,
            external_memory=external_memory,
        ),
        "operator_cards": _build_operator_cards(
            risk_posture=risk_posture,
            smi_posture_value=smi_posture_value,
            unified_posture=unified_posture,
            cross_run_drift=cross_run_drift,
            pattern_signal_count=pattern_signal_count,
            source_errors=source_errors,
            external_memory=external_memory,
        ),
        "what_to_watch": _build_watch_list(
            risk_posture=risk_posture,
            cross_run_drift=cross_run_drift,
            source_errors=source_errors,
            external_memory=external_memory,
        ),
        "sources": {
            "smi_posture": smi_posture,
            "temporal_awareness": temporal_awareness,
            "pattern_recognition": pattern_recognition,
            "unified_awareness": unified_awareness,
            "cross_run": cross_run,
            "external_memory": external_memory,
        },
        "external_memory": external_memory,
        "source_errors": source_errors,
        "authority": _authority(),
        "use_policy": _use_policy(),
    }

    authority_errors = _validate_authority_packet(context)
    if authority_errors:
        context["status"] = "authority_error"
        context["authority_errors"] = authority_errors
        context["system_posture"] = "cautious"
        context["risk_posture"] = "cautious"

    return context


def summarize_system_brain_context(context: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(context)

    return {
        "artifact_type": "system_brain_summary",
        "artifact_version": SYSTEM_BRAIN_VERSION,
        "generated_at": _utc_now_iso(),
        "status": source.get("status", "unknown"),
        "mode": "read_only",
        "system_posture": source.get("system_posture", "unknown"),
        "risk_posture": source.get("risk_posture", "unknown"),
        "cross_run_posture": source.get("cross_run_posture", "unknown"),
        "drift": source.get("drift", "unknown"),
        "pattern_signal_count": source.get("pattern_signal_count", 0),
        "plain_summary": source.get("plain_summary", ""),
        "external_memory": {
            "status": _safe_dict(source.get("external_memory")).get("status", "unknown"),
            "pattern_strength": _safe_dict(source.get("external_memory")).get("pattern_strength", "none"),
            "pattern_context_available": _safe_dict(source.get("external_memory")).get("pattern_context_available", False),
        },
        "authority": _authority(),
        "sealed": True,
    }