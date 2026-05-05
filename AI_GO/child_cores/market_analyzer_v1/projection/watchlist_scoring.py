from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _safe_lower(value: Any, default: str = "") -> str:
    text = _safe_str(value).lower()
    return text or default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_live_context(operator_packet: Dict[str, Any]) -> Dict[str, Any]:
    current_case = operator_packet.get("current_case") or {}
    live_event_panel = current_case.get("live_event_panel") or {}
    recommendation_panel = current_case.get("recommendation_panel") or {}
    historical_reference = operator_packet.get("historical_reference") or {}
    historical_context = historical_reference.get("historical_context") or {}
    setup_history_panel = historical_context.get("setup_history_panel") or {}
    setup_detection = historical_reference.get("setup_detection") or {}
    external_memory_packet = operator_packet.get("external_memory_packet") or {}
    advisory_summary = external_memory_packet.get("advisory_summary") or {}

    return {
        "symbol": _safe_str(current_case.get("symbol")),
        "headline": _safe_str(current_case.get("headline")),
        "price_change_pct": _safe_float(live_event_panel.get("price_change_pct"), 0.0),
        "confirmation": _safe_lower(live_event_panel.get("confirmation")),
        "recommendation_present": int(recommendation_panel.get("count") or 0) > 0,
        "setup_type": _safe_str(setup_detection.get("setup_type")),
        "historical_posture": _safe_lower(setup_history_panel.get("historical_posture")),
        "failure_rate_pct": _safe_float(setup_history_panel.get("failure_rate_pct"), 0.0),
        "follow_through_rate_pct": _safe_float(setup_history_panel.get("follow_through_rate_pct"), 0.0),
        "edge_class": _safe_lower(
            (operator_packet.get("labeled_outcomes_panel") or {}).get("edge_class")
        ),
        "memory_posture": _safe_lower(advisory_summary.get("advisory_posture")),
    }


def _apply_role_weights(
    *,
    role: str,
    continuation_score: float,
    fade_score: float,
    avoid_score: float,
) -> Dict[str, float]:
    if role == "beta_upstream":
        continuation_score += 18.0
        fade_score += 10.0
        avoid_score -= 8.0
    elif role == "services":
        continuation_score += 14.0
        fade_score += 4.0
        avoid_score -= 4.0
    elif role == "leader_major":
        continuation_score += 6.0
        fade_score += 2.0
        avoid_score += 10.0
    elif role == "midstream":
        continuation_score += 2.0
        fade_score += 1.0
        avoid_score += 14.0
    elif role == "failure_beta":
        continuation_score += 4.0
        fade_score += 20.0
        avoid_score -= 2.0
    elif role == "sector_etf":
        continuation_score += 4.0
        fade_score += 18.0
        avoid_score += 4.0
    elif role == "driver_gate":
        pass

    return {
        "continuation_score": continuation_score,
        "fade_score": fade_score,
        "avoid_score": avoid_score,
    }


def _apply_role_protection(
    *,
    role: str,
    continuation_score: float,
    fade_score: float,
    avoid_score: float,
) -> Dict[str, float]:
    if role in {"leader_major", "midstream"}:
        fade_score -= 10.0
        avoid_score += 10.0

    if role == "beta_upstream":
        continuation_score += 6.0

    if role == "services":
        fade_score -= 3.0
        continuation_score += 3.0

    return {
        "continuation_score": continuation_score,
        "fade_score": fade_score,
        "avoid_score": avoid_score,
    }


def _normalize_scores(
    *,
    continuation_score: float,
    fade_score: float,
    avoid_score: float,
) -> Dict[str, float]:
    continuation_score = max(0.0, continuation_score)
    fade_score = max(0.0, fade_score)
    avoid_score = max(0.0, avoid_score)

    return {
        "continuation_score": round(continuation_score, 2),
        "fade_score": round(fade_score, 2),
        "avoid_score": round(avoid_score, 2),
    }


def _score_item(item: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    role = _safe_lower(item.get("role"))
    symbol = _safe_str(item.get("symbol"))
    price_change_pct = _safe_float(context.get("price_change_pct"), 0.0)
    confirmation = _safe_lower(context.get("confirmation"))
    setup_type = _safe_str(context.get("setup_type"))
    historical_posture = _safe_lower(context.get("historical_posture"))
    failure_rate_pct = _safe_float(context.get("failure_rate_pct"), 0.0)
    follow_through_rate_pct = _safe_float(context.get("follow_through_rate_pct"), 0.0)
    recommendation_present = bool(context.get("recommendation_present"))
    memory_posture = _safe_lower(context.get("memory_posture"))

    continuation_score = 0.0
    fade_score = 0.0
    avoid_score = 40.0

    if confirmation == "confirmed":
        continuation_score += 18.0
        fade_score += 8.0

    if price_change_pct >= 2.0:
        continuation_score += 12.0
        fade_score += 10.0
    elif price_change_pct >= 1.0:
        continuation_score += 8.0
        fade_score += 6.0

    if recommendation_present:
        continuation_score += 8.0
        fade_score += 4.0

    if setup_type == "contextual_live_override":
        continuation_score += 4.0
        fade_score += 14.0

    if historical_posture == "historically fragile":
        fade_score += 15.0
        continuation_score -= 4.0
    elif historical_posture == "historically constructive":
        continuation_score += 18.0
        fade_score -= 6.0

    if failure_rate_pct >= 60.0:
        fade_score += 15.0

    if follow_through_rate_pct >= 60.0:
        continuation_score += 12.0

    if memory_posture == "strong_context":
        continuation_score += 6.0
        fade_score += 4.0

    weighted = _apply_role_weights(
        role=role,
        continuation_score=continuation_score,
        fade_score=fade_score,
        avoid_score=avoid_score,
    )
    continuation_score = weighted["continuation_score"]
    fade_score = weighted["fade_score"]
    avoid_score = weighted["avoid_score"]

    protected = _apply_role_protection(
        role=role,
        continuation_score=continuation_score,
        fade_score=fade_score,
        avoid_score=avoid_score,
    )
    continuation_score = protected["continuation_score"]
    fade_score = protected["fade_score"]
    avoid_score = protected["avoid_score"]

    normalized = _normalize_scores(
        continuation_score=continuation_score,
        fade_score=fade_score,
        avoid_score=avoid_score,
    )
    continuation_score = normalized["continuation_score"]
    fade_score = normalized["fade_score"]
    avoid_score = normalized["avoid_score"]

    if symbol == "CL":
        return {
            "symbol": symbol,
            "name": _safe_str(item.get("name")),
            "bucket": "driver",
            "score": 100.0,
            "role": role,
            "condition_state": "confirmation_gate",
            "trigger": "Buy bucket strengthens only if crude confirms. Fade risk increases if crude stalls or rolls over.",
            "reason": _safe_str(item.get("notes")),
        }

    # Balanced multi-path decision logic
    if fade_score >= 75.0 and role in {"failure_beta", "sector_etf"}:
        bucket = "fade"
        score = fade_score
        condition_state = "armed_if_failure"
        trigger = "Activate on failed follow-through, loss of strength, or weak next-session confirmation."

    elif role in {"beta_upstream", "services"} and continuation_score >= 45.0:
        bucket = "buy"
        score = continuation_score
        condition_state = "conditional"
        trigger = "Activate only if the rebound holds and sector confirmation improves."

    elif fade_score >= continuation_score + 8.0 and fade_score >= 65.0:
        bucket = "fade"
        score = fade_score
        condition_state = "watch_for_failure"
        trigger = "Monitor for weakening momentum and failed continuation."

    else:
        bucket = "avoid"
        score = max(avoid_score, continuation_score, fade_score)
        condition_state = "no_clear_edge"
        trigger = "Do not prioritize unless the signal strengthens materially."

    return {
        "symbol": symbol,
        "name": _safe_str(item.get("name")),
        "bucket": bucket,
        "score": round(score, 2),
        "role": role,
        "condition_state": condition_state,
        "trigger": trigger,
        "reason": _safe_str(item.get("notes")),
    }


def build_watchlist_scores(
    *,
    operator_packet: Dict[str, Any],
    registry: Dict[str, Any],
) -> Dict[str, Any]:
    packet = deepcopy(operator_packet)
    registry_copy = deepcopy(registry)

    if not registry_copy:
        return {
            "status": "not_available",
            "sector": None,
            "source_symbol": None,
            "items": [],
            "summary": "No governed watchlist registry is available for this sector.",
        }

    context = _extract_live_context(packet)
    items = registry_copy.get("items") or []

    scored_items: List[Dict[str, Any]] = [
        _score_item(item, context) for item in items if isinstance(item, dict)
    ]

    buy_items = [item for item in scored_items if item.get("bucket") == "buy"]
    avoid_items = [item for item in scored_items if item.get("bucket") == "avoid"]
    fade_items = [item for item in scored_items if item.get("bucket") == "fade"]
    driver_items = [item for item in scored_items if item.get("bucket") == "driver"]

    buy_items.sort(key=lambda x: x.get("score", 0), reverse=True)
    avoid_items.sort(key=lambda x: x.get("score", 0), reverse=True)
    fade_items.sort(key=lambda x: x.get("score", 0), reverse=True)

    if context.get("historical_posture") == "historically fragile":
        summary = (
            "Fragile historical posture: treat buy candidates as conditional only and prioritize fade planning if follow-through weakens."
        )
    elif context.get("historical_posture") == "historically constructive":
        summary = (
            "Constructive historical posture: buy candidates are more actionable if sector confirmation holds."
        )
    else:
        summary = (
            "Mixed or unclear historical posture: wait for stronger confirmation before treating any candidate as primary."
        )

    return {
        "status": "ok",
        "sector": registry_copy.get("sector_key"),
        "source_symbol": registry_copy.get("source_symbol"),
        "context": context,
        "items": scored_items,
        "buckets": {
            "buy": buy_items,
            "avoid": avoid_items,
            "fade": fade_items,
            "driver": driver_items,
        },
        "summary": summary,
    }