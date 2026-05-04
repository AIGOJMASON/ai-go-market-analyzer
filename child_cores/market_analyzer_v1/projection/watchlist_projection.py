from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple


LANE_REGISTRY: Tuple[Dict[str, Any], ...] = (
    {
        "lane_id": "energy",
        "label": "Energy",
        "priority": 1.00,
        "anchor_symbols": ("XLE", "CL", "USO"),
        "headline_keywords": (
            "oil",
            "crude",
            "energy",
            "gas",
            "refinery",
            "e&p",
            "permian",
            "hormuz",
            "supply disruption",
        ),
        "buy": (
            ("EOG", 1.00),
            ("OXY", 0.94),
            ("SLB", 0.88),
        ),
        "avoid": (
            ("XOM", 1.00),
            ("CVX", 0.94),
            ("KMI", 0.88),
        ),
        "fade": (
            ("XLE", 1.16),
            ("MRO", 1.00),
            ("APA", 0.94),
        ),
        "drivers": (
            ("XLE", 1.08),
            ("CL", 1.00),
            ("USO", 0.92),
        ),
    },
    {
        "lane_id": "staples",
        "label": "Staples",
        "priority": 0.88,
        "anchor_symbols": ("XLP",),
        "headline_keywords": (
            "staples",
            "consumer defensive",
            "defensive demand",
            "supply concern",
            "demand rises",
        ),
        "buy": (
            ("PG", 1.00),
            ("KO", 0.94),
            ("PEP", 0.90),
        ),
        "avoid": (
            ("KHC", 1.00),
            ("MDLZ", 0.94),
            ("MO", 0.88),
        ),
        "fade": (
            ("XLY", 1.00),
            ("TSLA", 0.96),
            ("AMZN", 0.92),
        ),
        "drivers": (
            ("XLP", 1.00),
            ("XLU", 0.95),
            ("TLT", 0.90),
        ),
    },
    {
        "lane_id": "utilities",
        "label": "Utilities",
        "priority": 0.84,
        "anchor_symbols": ("XLU",),
        "headline_keywords": (
            "utilities",
            "power",
            "grid",
            "electric",
            "yield defense",
            "defensive rate",
        ),
        "buy": (
            ("NEE", 1.00),
            ("DUK", 0.95),
            ("SO", 0.90),
        ),
        "avoid": (
            ("AEP", 1.00),
            ("EXC", 0.94),
            ("D", 0.88),
        ),
        "fade": (
            ("KRE", 1.00),
            ("IWM", 0.95),
            ("XLY", 0.90),
        ),
        "drivers": (
            ("XLU", 1.00),
            ("TLT", 0.95),
            ("GLD", 0.90),
        ),
    },
    {
        "lane_id": "macro",
        "label": "Macro / Safety",
        "priority": 0.82,
        "anchor_symbols": ("TLT", "GLD", "DXY"),
        "headline_keywords": (
            "treasury",
            "bond",
            "yield",
            "gold",
            "dollar",
            "macro",
            "risk-off",
            "flight to safety",
            "bond yields fall",
        ),
        "buy": (
            ("TLT", 1.00),
            ("GLD", 0.96),
            ("XLU", 0.90),
        ),
        "avoid": (
            ("KRE", 1.00),
            ("IWM", 0.95),
            ("XLY", 0.90),
        ),
        "fade": (
            ("XBI", 1.00),
            ("ARKK", 0.96),
            ("SMH", 0.92),
        ),
        "drivers": (
            ("TLT", 1.00),
            ("GLD", 0.96),
            ("DXY", 0.92),
        ),
    },
    {
        "lane_id": "risk",
        "label": "Risk / Growth",
        "priority": 0.70,
        "anchor_symbols": ("XLK", "QQQ", "XLY"),
        "headline_keywords": (
            "tech",
            "growth",
            "risk-on",
            "momentum",
            "consumer discretionary",
            "ai",
        ),
        "buy": (
            ("NVDA", 1.00),
            ("MSFT", 0.96),
            ("AMZN", 0.92),
        ),
        "avoid": (
            ("AAPL", 1.00),
            ("META", 0.95),
            ("GOOGL", 0.90),
        ),
        "fade": (
            ("ARKK", 1.00),
            ("IWM", 0.95),
            ("XLY", 0.90),
        ),
        "drivers": (
            ("QQQ", 1.00),
            ("XLK", 0.95),
            ("TNX", 0.90),
        ),
    },
)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return deepcopy(value) if isinstance(value, list) else []


def _first_non_empty(*values: Any) -> Optional[str]:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _to_float(value: Any) -> Optional[float]:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_symbol(operator_packet: Dict[str, Any]) -> str:
    current_case = _safe_dict(operator_packet.get("current_case"))
    recommendation_panel = _safe_dict(current_case.get("recommendation_panel"))
    items = _safe_list(recommendation_panel.get("items"))

    recommendation_symbol = ""
    for item in items:
        if isinstance(item, dict) and item.get("symbol"):
            recommendation_symbol = str(item.get("symbol")).strip().upper()
            break

    return (
        _first_non_empty(
            current_case.get("symbol"),
            recommendation_symbol,
        )
        or "UNKNOWN"
    ).upper()


def _extract_headline(operator_packet: Dict[str, Any]) -> str:
    current_case = _safe_dict(operator_packet.get("current_case"))
    live_event_panel = _safe_dict(current_case.get("live_event_panel"))

    return (
        _first_non_empty(
            current_case.get("headline"),
            live_event_panel.get("headline"),
        )
        or ""
    )


def _extract_setup_type(operator_packet: Dict[str, Any]) -> str:
    historical_reference = _safe_dict(operator_packet.get("historical_reference"))
    recent_memory = _safe_dict(operator_packet.get("recent_memory"))
    current_case = _safe_dict(operator_packet.get("current_case"))

    return (
        _first_non_empty(
            historical_reference.get("setup_type"),
            recent_memory.get("setup_type"),
            current_case.get("setup_type"),
            current_case.get("detected_setup"),
        )
        or ""
    ).lower()


def _extract_confirmation(operator_packet: Dict[str, Any]) -> str:
    current_case = _safe_dict(operator_packet.get("current_case"))
    live_event_panel = _safe_dict(current_case.get("live_event_panel"))
    recent_memory = _safe_dict(operator_packet.get("recent_memory"))

    raw = (
        _first_non_empty(
            live_event_panel.get("confirmation"),
            current_case.get("confirmation"),
            recent_memory.get("confirmation"),
        )
        or ""
    ).lower()

    if raw in {"confirmed", "strong", "external_signal"}:
        return "confirmed"
    if raw in {"partial", "watch", "external_watch"}:
        return "partial"
    if raw in {"rejected", "weak", "failed"}:
        return "weak"
    return "unknown"


def _extract_confidence(operator_packet: Dict[str, Any]) -> float:
    current_case = _safe_dict(operator_packet.get("current_case"))
    live_event_panel = _safe_dict(current_case.get("live_event_panel"))
    recommendation_panel = _safe_dict(current_case.get("recommendation_panel"))
    items = _safe_list(recommendation_panel.get("items"))

    item_confidence = None
    for item in items:
        if not isinstance(item, dict):
            continue
        item_confidence = _to_float(
            item.get("confidence")
            or item.get("confidence_score")
            or item.get("setup_confidence")
            or item.get("score")
        )
        if item_confidence is not None:
            break

    direct_confidence = _to_float(
        current_case.get("confidence")
        or current_case.get("confidence_score")
        or current_case.get("setup_confidence")
        or current_case.get("score")
        or live_event_panel.get("confidence")
        or live_event_panel.get("confidence_score")
    )

    confidence = item_confidence if item_confidence is not None else direct_confidence
    if confidence is None:
        confirmation = _extract_confirmation(operator_packet)
        if confirmation == "confirmed":
            return 0.65
        if confirmation == "partial":
            return 0.50
        if confirmation == "weak":
            return 0.35
        return 0.45

    if confidence > 1.0:
        confidence = confidence / 100.0

    return max(0.0, min(1.0, confidence))


def _derive_history_context(operator_packet: Dict[str, Any]) -> Dict[str, Any]:
    historical_reference = _safe_dict(operator_packet.get("historical_reference"))
    labeled_outcomes_panel = _safe_dict(operator_packet.get("labeled_outcomes_panel"))

    setup_panel = _safe_dict(
        historical_reference
        .get("historical_context", {})
        .get("setup_history_panel")
    )

    follow_through = _to_float(setup_panel.get("follow_through_rate_pct"))
    failure = _to_float(setup_panel.get("failure_rate_pct"))
    outcome_count = _to_int(setup_panel.get("outcome_count"))
    pattern_count = _to_int(setup_panel.get("pattern_count"))
    historical_posture = _first_non_empty(setup_panel.get("historical_posture")) or ""

    if labeled_outcomes_panel:
        rates = _safe_dict(labeled_outcomes_panel.get("rates"))
        if follow_through is None:
            follow_through = _to_float(rates.get("follow_through_pct"))
        if failure is None:
            failure = _to_float(rates.get("failure_pct"))
        if outcome_count is None:
            outcome_count = _to_int(labeled_outcomes_panel.get("outcome_count"))

    bias = "unknown"
    note = "Historical edge is unclear."

    if follow_through is not None and failure is not None:
        count = outcome_count or pattern_count or 0

        if failure > follow_through:
            bias = "caution"
            note = (
                "History argues for caution. "
                f"Failure {failure:.1f}% vs follow-through {follow_through:.1f}% "
                f"across {count} outcomes."
            )
        elif follow_through > failure:
            bias = "supportive"
            note = (
                "History supports continuation. "
                f"Follow-through {follow_through:.1f}% vs failure {failure:.1f}% "
                f"across {count} outcomes."
            )
        else:
            bias = "mixed"
            note = "History is balanced."

    return {
        "historical_posture": historical_posture,
        "follow_through_rate_pct": follow_through,
        "failure_rate_pct": failure,
        "outcome_count": outcome_count,
        "pattern_count": pattern_count,
        "history_bias": bias,
        "history_note": note,
    }


def _compute_historical_edge(context: Dict[str, Any]) -> float:
    follow = _to_float(context.get("follow_through_rate_pct"))
    fail = _to_float(context.get("failure_rate_pct"))
    if follow is None or fail is None:
        return 0.0
    return max(-1.0, min(1.0, (follow - fail) / 100.0))


def _compute_sample_weight(context: Dict[str, Any]) -> float:
    count = _to_int(context.get("outcome_count")) or 0
    return max(0.0, min(1.0, count / 10.0))


def _compute_adjusted_historical_edge(context: Dict[str, Any]) -> float:
    return _compute_historical_edge(context) * _compute_sample_weight(context)


def _setup_multiplier(setup_type: str) -> float:
    normalized = str(setup_type or "").strip().lower()

    if any(token in normalized for token in ("breakout", "rebound", "event_confirmation", "confirmation")):
        return 1.00
    if "continuation" in normalized:
        return 0.80
    if any(token in normalized for token in ("mean_reversion", "mean reversion", "dip_rebound", "dip rebound")):
        return 0.60
    if "fade" in normalized:
        return 0.55
    return 0.50


def _formal_score_components(context: Dict[str, Any]) -> Dict[str, Any]:
    confidence = _to_float(context.get("confidence")) or 0.45
    historical_edge_raw = _compute_historical_edge(context)
    sample_weight = _compute_sample_weight(context)
    historical_edge_adjusted = historical_edge_raw * sample_weight
    setup_multiplier = _setup_multiplier(str(context.get("setup_type") or ""))

    final_score = confidence * (1.0 + historical_edge_adjusted) * setup_multiplier
    final_score = max(0.0, min(2.0, final_score))

    if final_score >= 0.75:
        classification = "buy"
    elif final_score >= 0.55:
        classification = "watch"
    elif final_score >= 0.40:
        classification = "avoid"
    else:
        classification = "fade"

    return {
        "confidence": round(confidence, 4),
        "historical_edge_raw": round(historical_edge_raw, 4),
        "sample_weight": round(sample_weight, 4),
        "historical_edge_adjusted": round(historical_edge_adjusted, 4),
        "setup_multiplier": round(setup_multiplier, 4),
        "formal_score": round(final_score, 4),
        "formal_classification": classification,
    }


def _build_context(operator_packet: Dict[str, Any]) -> Dict[str, Any]:
    current_case = _safe_dict(operator_packet.get("current_case"))
    live_event_panel = _safe_dict(current_case.get("live_event_panel"))
    history = _derive_history_context(operator_packet)

    context = {
        "symbol": _extract_symbol(operator_packet),
        "headline": _extract_headline(operator_packet),
        "setup_type": _extract_setup_type(operator_packet),
        "confirmation": _extract_confirmation(operator_packet),
        "confidence": _extract_confidence(operator_packet),
        "sector": (
            _first_non_empty(
                live_event_panel.get("sector"),
                current_case.get("sector"),
            )
            or ""
        ).strip().lower(),
        **history,
    }

    context.update(_formal_score_components(context))
    return context


def _score_lane(lane: Dict[str, Any], context: Dict[str, Any]) -> float:
    score = 0.0
    symbol = context.get("symbol", "")
    headline = str(context.get("headline") or "").lower()
    setup_type = str(context.get("setup_type") or "").lower()
    sector = str(context.get("sector") or "").lower()
    priority = float(lane.get("priority") or 0.0)

    score += priority * 10.0

    if symbol in lane.get("anchor_symbols", ()):
        score += 20.0

    for keyword in lane.get("headline_keywords", ()):
        if keyword in headline:
            score += 3.0

    lane_id = str(lane.get("lane_id") or "")
    if lane_id and lane_id in setup_type:
        score += 4.0

    if lane_id == "energy" and sector == "energy":
        score += 8.0
    if lane_id == "staples" and sector in {"consumer_defensive", "consumer defensive", "staples"}:
        score += 8.0
    if lane_id == "utilities" and sector == "utilities":
        score += 8.0

    if context.get("confirmation") == "confirmed":
        score += 4.0
    elif context.get("confirmation") == "partial":
        score -= 2.0
    elif context.get("confirmation") == "weak":
        score -= 4.0

    score += float(context.get("formal_score") or 0.0) * 10.0

    return round(score, 2)


def _select_lanes(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []
    for lane in LANE_REGISTRY:
        scored_lane = deepcopy(lane)
        scored_lane["_lane_score"] = _score_lane(scored_lane, context)
        scored.append(scored_lane)

    scored.sort(key=lambda item: float(item.get("_lane_score") or 0.0), reverse=True)
    return scored[:5]


def _desk_buy_note(context: Dict[str, Any], lane_label: str) -> str:
    bias = context.get("history_bias")
    classification = context.get("formal_classification")
    if bias == "supportive" and classification in {"buy", "watch"}:
        return f"{lane_label.lower()} continuation with history support"
    if bias == "caution":
        return "conditional only; history still leans failure"
    if bias == "mixed":
        return "conditional only; tape needs cleaner confirmation"
    return "conditional only; no clean edge yet"


def _desk_avoid_note(context: Dict[str, Any], lane_label: str) -> str:
    bias = context.get("history_bias")
    if bias == "caution":
        return f"no clean edge under a fragile {lane_label.lower()} tape"
    if bias == "supportive":
        return "secondary expression; stronger setups exist"
    return "no clean edge"


def _desk_fade_note(context: Dict[str, Any], lane_label: str) -> str:
    bias = context.get("history_bias")
    if bias == "caution":
        return f"first failure expression if {lane_label.lower()} loses momentum"
    if bias == "mixed":
        return "fade only on confirmed weakness"
    return "watch for failure"


def _desk_driver_note(lane_label: str) -> str:
    return f"confirmation gate for the {lane_label.lower()} lane"


def _resolve_size_band(score: float, bucket: str) -> Tuple[str, str]:
    if bucket == "driver":
        return (
            "confirmation_only",
            "Use for confirmation, not sizing.",
        )

    if bucket == "avoid":
        if score >= 95:
            return (
                "avoid_preferred",
                "Stand aside here; stronger expressions exist elsewhere.",
            )
        return (
            "neutral_watch",
            "No sizing edge here.",
        )

    if bucket == "buy":
        if score >= 95:
            return (
                "highest_priority_if_used",
                "Best long expression if the operator chooses exposure.",
            )
        if score >= 80:
            return (
                "moderate_if_used",
                "Valid long expression, but still not a full-conviction tape.",
            )
        if score >= 65:
            return (
                "light_if_used",
                "Smaller long only if the tape keeps improving.",
            )
        return (
            "watch_only",
            "Watch only until confirmation strengthens.",
        )

    if bucket == "fade":
        if score >= 115:
            return (
                "primary_fade_if_used",
                "Primary downside expression if the setup rolls over.",
            )
        if score >= 95:
            return (
                "secondary_fade_if_used",
                "Secondary downside expression if weakness confirms.",
            )
        if score >= 75:
            return (
                "tactical_fade_if_used",
                "Smaller fade only if weakness becomes clear.",
            )
        return (
            "watch_only",
            "Watch only until failure becomes clearer.",
        )

    return (
        "watch_only",
        "Watch only.",
    )


def _resolve_confidence_band(context: Dict[str, Any], bucket: str) -> str:
    formal_score = _to_float(context.get("formal_score")) or 0.0

    if bucket == "driver":
        return "structural_confirmation"

    if bucket == "buy":
        if formal_score >= 0.75:
            return "high"
        if formal_score >= 0.55:
            return "moderate"
        if formal_score >= 0.40:
            return "low"
        return "very_low"

    if bucket == "avoid":
        if formal_score < 0.40:
            return "high"
        if formal_score < 0.55:
            return "moderate"
        return "low"

    if bucket == "fade":
        if formal_score < 0.40:
            return "high"
        if formal_score < 0.55:
            return "moderate"
        if formal_score < 0.75:
            return "low"
        return "very_low"

    return "low"


def _confidence_note(confidence_band: str, bucket: str) -> str:
    if bucket == "driver":
        return "Confidence reflects confirmation value, not trade direction."

    mapping = {
        "high": "The formal model strongly supports this posture.",
        "moderate": "The formal model supports this posture, but not decisively.",
        "low": "Formal support is limited.",
        "very_low": "Formal support is weak; treat this as highly conditional.",
        "structural_confirmation": "Use this to confirm the tape, not to express size.",
    }
    return mapping.get(confidence_band, "Formal support is limited.")


def _is_extreme_failure(context: Dict[str, Any]) -> bool:
    follow = _to_float(context.get("follow_through_rate_pct")) or 0.0
    fail = _to_float(context.get("failure_rate_pct")) or 0.0
    count = _to_int(context.get("outcome_count")) or 0
    return count >= 5 and follow == 0.0 and fail >= 70.0


def _resolve_posture_label(
    context: Dict[str, Any],
    merged_buy: List[Dict[str, Any]],
    merged_fade: List[Dict[str, Any]],
) -> str:
    history_bias = str(context.get("history_bias") or "unknown")
    failure = _to_float(context.get("failure_rate_pct")) or 0.0
    follow_through = _to_float(context.get("follow_through_rate_pct")) or 0.0

    if _is_extreme_failure(context):
        return "hard_fade"
    if history_bias == "caution" and failure >= 70.0:
        return "fade_dominant"
    if history_bias == "caution" and failure >= 55.0:
        return "defensive_caution"
    if history_bias == "supportive" and follow_through >= 60.0 and merged_buy:
        return "conditional_long"
    if history_bias == "mixed":
        return "balanced_wait"
    if not merged_buy and merged_fade:
        return "fade_dominant"
    return "watchful_neutral"


def _resolve_no_trade_state(
    context: Dict[str, Any],
    merged_buy: List[Dict[str, Any]],
    merged_fade: List[Dict[str, Any]],
) -> Dict[str, Any]:
    history_bias = str(context.get("history_bias") or "unknown")
    failure = _to_float(context.get("failure_rate_pct")) or 0.0
    follow_through = _to_float(context.get("follow_through_rate_pct")) or 0.0
    confirmation = str(context.get("confirmation") or "unknown")
    count = _to_int(context.get("outcome_count")) or 0

    if count < 5:
        return {
            "state": "no_trade",
            "is_no_trade": True,
            "reason": "Insufficient historical sample size.",
            "rule": "min_sample_not_met",
        }

    if _is_extreme_failure(context):
        return {
            "state": "no_trade",
            "is_no_trade": True,
            "reason": "0% follow-through with dominant failure profile.",
            "rule": "extreme_failure",
        }

    if confirmation in {"weak", "unknown"}:
        return {
            "state": "no_trade",
            "is_no_trade": True,
            "reason": "Confirmation is too weak to support directional exposure.",
            "rule": "weak_confirmation_gate",
        }

    if history_bias == "mixed" and follow_through < 45.0 and failure < 55.0:
        return {
            "state": "no_trade",
            "is_no_trade": True,
            "reason": "Historical outcomes are too mixed to establish a directional edge.",
            "rule": "mixed_history_gate",
        }

    if history_bias == "caution" and failure >= 85.0 and not merged_fade:
        return {
            "state": "no_trade",
            "is_no_trade": True,
            "reason": "History is decisively fragile, but there is no clean failure expression to favor.",
            "rule": "fragile_history_without_expression",
        }

    if not merged_buy and not merged_fade:
        return {
            "state": "no_trade",
            "is_no_trade": True,
            "reason": "No bucket carries enough edge to justify a directional posture.",
            "rule": "no_ranked_expression",
        }

    return {
        "state": "active",
        "is_no_trade": False,
        "reason": "",
        "rule": "",
    }


def _normalize_weighted_symbol(entry: Any) -> Tuple[str, float]:
    if isinstance(entry, tuple) and len(entry) == 2:
        symbol = str(entry[0]).upper()
        try:
            weight = float(entry[1])
        except (TypeError, ValueError):
            weight = 1.0
        return symbol, weight

    return str(entry).upper(), 1.0


def _bucket_alignment_bonus(bucket: str, formal_classification: str) -> float:
    if bucket == "buy":
        if formal_classification == "buy":
            return 18.0
        if formal_classification == "watch":
            return 8.0
        if formal_classification == "avoid":
            return -10.0
        return -22.0

    if bucket == "avoid":
        if formal_classification == "avoid":
            return 12.0
        if formal_classification == "watch":
            return 4.0
        if formal_classification == "buy":
            return -6.0
        return 6.0

    if bucket == "fade":
        if formal_classification == "fade":
            return 18.0
        if formal_classification == "avoid":
            return 10.0
        if formal_classification == "watch":
            return -4.0
        return -18.0

    if bucket == "driver":
        return 0.0

    return 0.0


def _make_item(
    *,
    entry: Any,
    lane: Dict[str, Any],
    bucket: str,
    context: Dict[str, Any],
    is_active_anchor: bool = False,
) -> Dict[str, Any]:
    symbol, symbol_weight = _normalize_weighted_symbol(entry)

    lane_id = str(lane.get("lane_id") or "")
    lane_label = str(lane.get("label") or lane_id.title())
    lane_score = float(lane.get("_lane_score") or 0.0)
    active_symbol = str(context.get("symbol") or "").upper()
    confirmation = str(context.get("confirmation") or "")
    history_bias = str(context.get("history_bias") or "unknown")
    formal_score = float(context.get("formal_score") or 0.0)
    formal_classification = str(context.get("formal_classification") or "watch")

    note = ""
    base_score = formal_score * 100.0

    if bucket == "buy":
        note = _desk_buy_note(context, lane_label)
    elif bucket == "avoid":
        note = _desk_avoid_note(context, lane_label)
    elif bucket == "fade":
        note = _desk_fade_note(context, lane_label)
    elif bucket == "driver":
        note = _desk_driver_note(lane_label)

    base_score += _bucket_alignment_bonus(bucket, formal_classification)
    base_score *= symbol_weight

    if bucket == "driver":
        base_score = 44.0 * symbol_weight
        if is_active_anchor:
            note = f"active anchor for the {lane_label.lower()} lane"
            base_score += 22.0

    if symbol == active_symbol:
        base_score += 18.0

    if confirmation == "confirmed":
        base_score += 6.0
    elif confirmation == "partial":
        base_score -= 4.0
    elif confirmation == "weak":
        base_score -= 8.0

    if bucket == "fade" and history_bias == "caution":
        base_score += 8.0
    if bucket == "buy" and history_bias == "supportive":
        base_score += 6.0
    if bucket == "buy" and history_bias == "caution":
        base_score -= 10.0

    total_score = round(base_score + lane_score, 2)
    exposure_posture, size_note = _resolve_size_band(total_score, bucket)
    confidence_band = _resolve_confidence_band(context, bucket)

    return {
        "symbol": symbol,
        "note": note,
        "lane_id": lane_id,
        "lane_label": lane_label,
        "score": total_score,
        "bucket": bucket,
        "formal_score": round(formal_score, 4),
        "formal_classification": formal_classification,
        "model_confidence": round(float(context.get("confidence") or 0.0), 4),
        "historical_edge_adjusted": round(float(context.get("historical_edge_adjusted") or 0.0), 4),
        "sample_weight": round(float(context.get("sample_weight") or 0.0), 4),
        "setup_multiplier": round(float(context.get("setup_multiplier") or 0.0), 4),
        "exposure_posture": exposure_posture,
        "size_note": size_note,
        "confidence_band": confidence_band,
        "confidence_note": _confidence_note(confidence_band, bucket),
    }


def _lane_summary(lane: Dict[str, Any], context: Dict[str, Any]) -> str:
    label = str(lane.get("label") or "Lane")
    confirmation = context.get("confirmation") or "unknown"
    history_note = context.get("history_note") or "Historical edge is unclear."
    symbol = context.get("symbol") or ""

    if symbol in lane.get("anchor_symbols", ()):
        return f"{label} leads. Signal is {confirmation}. {history_note}"

    return f"{label} is secondary context. Signal remains {confirmation}. {history_note}"


def _build_lane_output(lane: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    buy_items = [
        _make_item(entry=entry, lane=lane, bucket="buy", context=context)
        for entry in lane.get("buy", ())
    ]
    avoid_items = [
        _make_item(entry=entry, lane=lane, bucket="avoid", context=context)
        for entry in lane.get("avoid", ())
    ]
    fade_items = [
        _make_item(entry=entry, lane=lane, bucket="fade", context=context)
        for entry in lane.get("fade", ())
    ]
    driver_items = [
        _make_item(entry=entry, lane=lane, bucket="driver", context=context)
        for entry in lane.get("drivers", ())
    ]

    active_symbol = str(context.get("symbol") or "").upper()
    if active_symbol in lane.get("anchor_symbols", ()):
        driver_items.insert(
            0,
            _make_item(
                entry=(active_symbol, 1.0),
                lane=lane,
                bucket="driver",
                context=context,
                is_active_anchor=True,
            ),
        )

    return {
        "lane_id": lane.get("lane_id"),
        "label": lane.get("label"),
        "lane_score": lane.get("_lane_score"),
        "summary": _lane_summary(lane, context),
        "buy": buy_items,
        "avoid": avoid_items,
        "fade": fade_items,
        "drivers": driver_items,
    }


def _merge_bucket(
    lane_outputs: List[Dict[str, Any]],
    bucket: str,
    limit: int,
) -> List[Dict[str, Any]]:
    best_by_symbol: Dict[str, Dict[str, Any]] = {}
    lane_key = "drivers" if bucket == "driver" else bucket

    for lane_output in lane_outputs:
        for item in lane_output.get(lane_key, []):
            symbol = str(item.get("symbol") or "").upper()
            if not symbol:
                continue
            existing = best_by_symbol.get(symbol)
            if existing is None or float(item.get("score") or 0.0) > float(existing.get("score") or 0.0):
                best_by_symbol[symbol] = item

    merged = list(best_by_symbol.values())
    merged.sort(key=lambda item: float(item.get("score") or 0.0), reverse=True)
    return merged[:limit]


def _apply_posture_filters(
    context: Dict[str, Any],
    merged_buy: List[Dict[str, Any]],
    merged_avoid: List[Dict[str, Any]],
    merged_fade: List[Dict[str, Any]],
    merged_drivers: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    history_bias = str(context.get("history_bias") or "unknown")
    failure = _to_float(context.get("failure_rate_pct")) or 0.0
    follow_through = _to_float(context.get("follow_through_rate_pct")) or 0.0

    buy = list(merged_buy)
    avoid = list(merged_avoid)
    fade = list(merged_fade)
    drivers = list(merged_drivers)

    if _is_extreme_failure(context):
        buy = []
        return buy, avoid, fade, drivers

    if history_bias == "caution" and failure >= 70.0:
        buy = []

    if history_bias == "supportive" and follow_through >= 60.0:
        fade = fade[:2]

    return buy, avoid, fade, drivers


def _summary_line(
    context: Dict[str, Any],
    active_label: str,
    posture_label: str,
    no_trade_state: Dict[str, Any],
) -> str:
    note = context.get("history_note") or "Historical edge is unclear."

    if no_trade_state.get("is_no_trade"):
        return f"{active_label} is live, but posture is no-trade. {no_trade_state.get('reason')}"

    posture_map = {
        "hard_fade": f"{active_label} leads, and the desk is hard fade.",
        "fade_dominant": f"{active_label} leads, and the desk is fade-dominant.",
        "defensive_caution": f"{active_label} leads, but the desk stays defensive.",
        "conditional_long": f"{active_label} leads with a conditional long posture.",
        "balanced_wait": f"{active_label} leads, but the desk is waiting for cleaner asymmetry.",
        "watchful_neutral": f"{active_label} leads, but posture remains neutral.",
    }

    return f"{posture_map.get(posture_label, f'{active_label} leads.')} {note}"


def build_watchlist_projection(
    *,
    operator_packet: Dict[str, Any],
) -> Dict[str, Any]:
    packet = _safe_dict(operator_packet)
    context = _build_context(packet)
    selected_lanes = _select_lanes(context)
    lane_outputs = [_build_lane_output(lane, context) for lane in selected_lanes]

    if not lane_outputs:
        return {
            "artifact_type": "watchlist_projection",
            "status": "not_available",
            "active_lane": None,
            "summary": "No governed watchlist suggestions are available.",
            "posture_label": "not_available",
            "no_trade_state": {
                "state": "no_trade",
                "is_no_trade": True,
                "reason": "No governed watchlist suggestions are available.",
                "rule": "not_available",
            },
            "items": [],
            "buckets": {
                "buy": [],
                "avoid": [],
                "fade": [],
                "driver": [],
            },
            "lane_suggestions": [],
            "context": context,
            "constraints": {
                "annotation_only": True,
                "recommendation_mutation_allowed": False,
                "governance_mutation_allowed": False,
                "runtime_mutation_allowed": False,
            },
        }

    merged_buy = _merge_bucket(lane_outputs, "buy", limit=3)
    merged_avoid = _merge_bucket(lane_outputs, "avoid", limit=3)
    merged_fade = _merge_bucket(lane_outputs, "fade", limit=3)
    merged_drivers = _merge_bucket(lane_outputs, "driver", limit=3)

    merged_buy, merged_avoid, merged_fade, merged_drivers = _apply_posture_filters(
        context,
        merged_buy,
        merged_avoid,
        merged_fade,
        merged_drivers,
    )

    posture_label = _resolve_posture_label(context, merged_buy, merged_fade)
    no_trade_state = _resolve_no_trade_state(context, merged_buy, merged_fade)

    active_lane = lane_outputs[0].get("lane_id")
    active_label = str(lane_outputs[0].get("label") or "Lead lane")

    return {
        "artifact_type": "watchlist_projection",
        "status": "ok",
        "active_lane": active_lane,
        "source_symbol": context.get("symbol"),
        "summary": _summary_line(context, active_label, posture_label, no_trade_state),
        "posture_label": posture_label,
        "no_trade_state": no_trade_state,
        "items": merged_buy + merged_avoid + merged_fade + merged_drivers,
        "buckets": {
            "buy": merged_buy,
            "avoid": merged_avoid,
            "fade": merged_fade,
            "driver": merged_drivers,
        },
        "lane_suggestions": lane_outputs,
        "context": context,
        "model": {
            "name": "watchlist_formal_score_v1",
            "confidence": context.get("confidence"),
            "historical_edge_raw": context.get("historical_edge_raw"),
            "sample_weight": context.get("sample_weight"),
            "historical_edge_adjusted": context.get("historical_edge_adjusted"),
            "setup_multiplier": context.get("setup_multiplier"),
            "formal_score": context.get("formal_score"),
            "formal_classification": context.get("formal_classification"),
        },
        "constraints": {
            "annotation_only": True,
            "recommendation_mutation_allowed": False,
            "governance_mutation_allowed": False,
            "runtime_mutation_allowed": False,
        },
    }