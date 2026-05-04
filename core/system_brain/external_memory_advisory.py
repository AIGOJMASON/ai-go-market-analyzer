from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


EXTERNAL_MEMORY_SYSTEM_BRAIN_ADVISORY_VERSION = "v5F.4"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_bool(value: Any) -> bool:
    return value is True


def _authority() -> Dict[str, Any]:
    return {
        "read_only": True,
        "advisory_only": True,
        "memory_is_truth": False,
        "memory_is_candidate_signal": True,
        "can_execute": False,
        "can_mutate_state": False,
        "can_mutate_runtime": False,
        "can_override_state_authority": False,
        "can_override_canon": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_block_request": False,
        "can_allow_request": False,
    }


def _use_policy() -> Dict[str, Any]:
    return {
        "may_display_in_system_brain": True,
        "may_display_in_operator_surface": True,
        "may_feed_pattern_context": True,
        "may_feed_system_brain_summary": True,
        "may_change_execution_gate": False,
        "may_change_watcher": False,
        "may_change_state_authority": False,
        "may_change_canon": False,
        "may_change_runtime": False,
        "may_change_recommendations": False,
        "may_change_pm_strategy": False,
        "may_write_decisions": False,
        "may_dispatch_actions": False,
    }


def _build_unavailable_panel(reason: str) -> Dict[str, Any]:
    return {
        "artifact_type": "external_memory_system_brain_advisory",
        "artifact_version": EXTERNAL_MEMORY_SYSTEM_BRAIN_ADVISORY_VERSION,
        "generated_at": _utc_now_iso(),
        "status": "unavailable",
        "mode": "read_only_advisory",
        "source": "EXTERNAL_MEMORY",
        "reason": reason,
        "pattern_context_available": False,
        "retrieval": {},
        "promotion": {},
        "operator_card": {
            "card_id": "external_memory",
            "label": "External Memory",
            "value": "unavailable",
            "meaning": "External Memory advisory context could not be loaded. No authority changes were made.",
        },
        "what_to_watch": [
            "External Memory advisory context is unavailable. Continue using State Authority, Watcher, and Canon as controlling layers."
        ],
        "authority": _authority(),
        "use_policy": _use_policy(),
        "sealed": True,
    }


def _extract_retrieval_context(retrieval_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    context = _safe_dict(retrieval_context)

    if not context:
        return {}

    if context.get("artifact_type") == "external_memory_read_only_context":
        return context

    nested = context.get("retrieval_context")
    if isinstance(nested, dict):
        return nested

    return context


def _extract_promotion_context(promotion_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    context = _safe_dict(promotion_context)

    if not context:
        return {}

    if context.get("artifact_type") == "external_memory_promotion_artifact":
        return context

    nested = context.get("promotion_artifact") or context.get("artifact")
    if isinstance(nested, dict):
        return nested

    return context


def _derive_pattern_strength(
    *,
    returned_count: int,
    promotion_decision: str,
    promotion_score: float | None,
) -> str:
    if promotion_decision == "promoted":
        return "strong"

    if promotion_decision == "hold":
        return "moderate"

    if promotion_score is not None and promotion_score >= 75:
        return "moderate"

    if returned_count > 0:
        return "weak"

    return "none"


def _build_operator_card(
    *,
    returned_count: int,
    promotion_decision: str,
    pattern_strength: str,
) -> Dict[str, Any]:
    if returned_count <= 0:
        value = "no_context"
        meaning = "External Memory is available, but no bounded memory context was returned."
    elif promotion_decision == "promoted":
        value = "advisory_pattern_promoted"
        meaning = "External Memory found a promoted advisory pattern. It remains context only."
    elif promotion_decision == "hold":
        value = "advisory_pattern_held"
        meaning = "External Memory found a moderate advisory pattern. It remains context only."
    else:
        value = "advisory_context_available"
        meaning = "External Memory returned bounded advisory context. It does not create truth or authority."

    return {
        "card_id": "external_memory",
        "label": "External Memory",
        "value": value,
        "meaning": meaning,
        "record_count": returned_count,
        "pattern_strength": pattern_strength,
    }


def _build_watch_items(
    *,
    returned_count: int,
    promotion_decision: str,
    pattern_strength: str,
) -> List[str]:
    items: List[str] = []

    if returned_count > 0:
        items.append(
            "External Memory returned prior context. Treat it as candidate signal only, not truth."
        )

    if promotion_decision in {"promoted", "hold"}:
        items.append(
            f"External Memory promotion posture is {promotion_decision}. Use it only as advisory pattern context."
        )

    if pattern_strength in {"strong", "moderate"}:
        items.append(
            "Pattern strength is visible in System Brain, but State Authority, Watcher, and Canon remain controlling layers."
        )

    if not items:
        items.append(
            "No External Memory pattern pressure is visible. Continue normal governed review."
        )

    return items


def build_external_memory_system_brain_advisory(
    *,
    retrieval_context: Optional[Dict[str, Any]] = None,
    promotion_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    retrieval = _extract_retrieval_context(retrieval_context)
    promotion = _extract_promotion_context(promotion_context)

    retrieval_authority = _safe_dict(retrieval.get("authority"))
    promotion_authority = _safe_dict(promotion.get("authority"))

    for source_name, authority in (
        ("retrieval", retrieval_authority),
        ("promotion", promotion_authority),
    ):
        if not authority:
            continue

        illegal = [
            key
            for key in (
                "memory_is_truth",
                "can_execute",
                "can_mutate_state",
                "can_mutate_runtime",
                "can_override_state_authority",
                "can_override_canon",
                "can_override_governance",
                "can_override_watcher",
                "can_override_execution_gate",
            )
            if authority.get(key) is True
        ]

        if illegal:
            return _build_unavailable_panel(
                reason=f"{source_name}_authority_guard_failed:{','.join(illegal)}"
            )

    returned_count = int(retrieval.get("returned_count") or promotion.get("record_count") or 0)

    promotion_decision = _safe_str(
        promotion.get("promotion_decision")
        or promotion.get("decision")
        or "none"
    )

    raw_score = promotion.get("promotion_score")
    promotion_score = None
    if raw_score is not None:
        try:
            promotion_score = float(raw_score)
        except (TypeError, ValueError):
            promotion_score = None

    pattern_strength = _derive_pattern_strength(
        returned_count=returned_count,
        promotion_decision=promotion_decision,
        promotion_score=promotion_score,
    )

    pattern_context_available = returned_count > 0

    return {
        "artifact_type": "external_memory_system_brain_advisory",
        "artifact_version": EXTERNAL_MEMORY_SYSTEM_BRAIN_ADVISORY_VERSION,
        "generated_at": _utc_now_iso(),
        "status": "ok",
        "mode": "read_only_advisory",
        "source": "EXTERNAL_MEMORY",
        "pattern_context_available": pattern_context_available,
        "pattern_strength": pattern_strength,
        "retrieval": {
            "status": retrieval.get("status") or retrieval.get("retrieval_status") or "unknown",
            "returned_count": retrieval.get("returned_count", 0),
            "matched_count": retrieval.get("matched_count", 0),
            "retrieval_receipt_id": retrieval.get("retrieval_receipt_id", ""),
            "summary": _safe_dict(retrieval.get("summary")),
        },
        "promotion": {
            "status": promotion.get("status", "none"),
            "promotion_decision": promotion_decision,
            "promotion_score": promotion_score,
            "record_count": promotion.get("record_count", 0),
            "reusable_advisory_signal": _safe_bool(
                promotion.get("reusable_advisory_signal")
            ),
        },
        "operator_card": _build_operator_card(
            returned_count=returned_count,
            promotion_decision=promotion_decision,
            pattern_strength=pattern_strength,
        ),
        "what_to_watch": _build_watch_items(
            returned_count=returned_count,
            promotion_decision=promotion_decision,
            pattern_strength=pattern_strength,
        ),
        "plain_summary": (
            "External Memory is visible to System Brain as advisory pattern context only. "
            "It cannot create truth, execute, mutate state, or override governance."
        ),
        "authority": _authority(),
        "use_policy": _use_policy(),
        "sealed": True,
    }


def load_external_memory_system_brain_advisory(
    *,
    limit: int = 5,
    requester_profile: str = "market_analyzer_reader",
    target_child_core: str = "market_analyzer_v1",
) -> Dict[str, Any]:
    """
    Best-effort System Brain loader.

    This is intentionally fail-soft:
    System Brain may report External Memory unavailable, but it may not block,
    allow, execute, mutate, or override any controlling layer.
    """
    try:
        from AI_GO.EXTERNAL_MEMORY.retrieval.read_only_context import (
            build_external_memory_read_only_context,
        )

        request = {
            "artifact_type": "external_memory_retrieval_request",
            "requester_profile": requester_profile,
            "target_child_core": target_child_core,
            "limit": max(1, min(int(limit), 10)),
        }

        retrieval_context = build_external_memory_read_only_context(request)

        return build_external_memory_system_brain_advisory(
            retrieval_context=retrieval_context,
            promotion_context=None,
        )

    except Exception as exc:
        return _build_unavailable_panel(
            reason=f"{type(exc).__name__}: {exc}"
        )