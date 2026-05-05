from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.core.awareness.cross_run_intelligence import (
    build_cross_run_intelligence_packet,
)
from AI_GO.core.awareness.unified_system_awareness import (
    build_unified_system_awareness_packet,
)
from AI_GO.core.system_brain.system_brain import build_system_brain_context


OPERATOR_SYSTEM_BRAIN_SURFACE_VERSION = "v5F.4"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _call_builder(builder, *, limit: int) -> Dict[str, Any]:
    try:
        return _safe_dict(builder(limit=limit))
    except TypeError:
        try:
            return _safe_dict(builder())
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


def _authority() -> Dict[str, Any]:
    return {
        "operator_read_surface": True,
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


def _build_plain_summary(
    *,
    unified: Dict[str, Any],
    cross_run: Dict[str, Any],
    system_brain_context: Dict[str, Any],
) -> str:
    context_summary = _safe_str(system_brain_context.get("plain_summary"))
    if context_summary:
        return context_summary

    unified_summary = _safe_dict(unified.get("summary"))
    cross_run_summary = _safe_dict(cross_run.get("summary"))

    posture = _safe_str(unified_summary.get("posture") or unified.get("posture"))
    drift = _safe_str(cross_run_summary.get("drift") or cross_run.get("drift"))

    if posture:
        return f"System Brain is online in advisory mode. Unified posture is {posture}."

    if drift:
        return f"System Brain is online in advisory mode. Cross-run drift posture is {drift}."

    return "System Brain is online in advisory mode. No authority is granted by this surface."


def _build_operator_cards(
    *,
    system_brain_context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    cards = _safe_list(system_brain_context.get("operator_cards"))

    if cards:
        return cards

    return [
        {
            "card_id": "system_brain_mode",
            "label": "System Brain Mode",
            "value": "advisory_only",
            "meaning": "System Brain may summarize posture, but may not execute, mutate state, or override governance.",
        }
    ]


def _build_what_to_watch(system_brain_context: Dict[str, Any]) -> List[str]:
    watch = _safe_list(system_brain_context.get("what_to_watch"))
    if watch:
        return watch

    return [
        "System Brain is advisory only. Controlling layers remain State Authority, Watcher, Canon, and Execution Gate."
    ]


def build_operator_system_brain_surface(limit: int = 500) -> Dict[str, Any]:
    safe_limit = max(1, min(int(limit), 1000))

    unified = _call_builder(
        build_unified_system_awareness_packet,
        limit=safe_limit,
    )
    cross_run = _call_builder(
        build_cross_run_intelligence_packet,
        limit=safe_limit,
    )
    system_brain_context = build_system_brain_context(limit=safe_limit)

    external_memory = _safe_dict(system_brain_context.get("external_memory"))

    return {
        "artifact_type": "operator_system_brain_surface",
        "artifact_version": OPERATOR_SYSTEM_BRAIN_SURFACE_VERSION,
        "generated_at": _utc_now_iso(),
        "mode": "operator_read_only_surface",
        "status": "ok",
        "sealed": True,
        "plain_summary": _build_plain_summary(
            unified=unified,
            cross_run=cross_run,
            system_brain_context=system_brain_context,
        ),
        "operator_cards": _build_operator_cards(
            system_brain_context=system_brain_context,
        ),
        "what_to_watch": _build_what_to_watch(system_brain_context),
        "system_brain": {
            "context": system_brain_context,
            "system_posture": system_brain_context.get("system_posture", "unknown"),
            "risk_posture": system_brain_context.get("risk_posture", "unknown"),
            "cross_run_posture": system_brain_context.get("cross_run_posture", "unknown"),
            "drift": system_brain_context.get("drift", "unknown"),
            "pattern_signal_count": system_brain_context.get("pattern_signal_count", 0),
            "unified_awareness_summary": _safe_dict(unified.get("summary")),
            "cross_run_summary": _safe_dict(cross_run.get("summary")),
            "external_memory": external_memory,
        },
        "external_memory_panel": {
            "visible": True,
            "source": "external_memory",
            "mode": "system_brain_advisory",
            "advisory_only": True,
            "status": external_memory.get("status", "unknown"),
            "pattern_context_available": external_memory.get(
                "pattern_context_available",
                False,
            ),
            "pattern_strength": external_memory.get("pattern_strength", "none"),
            "summary": external_memory.get(
                "plain_summary",
                "External Memory is visible to System Brain as advisory context only.",
            ),
            "authority": external_memory.get("authority", {}),
        },
        "authority": _authority(),
        "use_policy": _use_policy(),
    }