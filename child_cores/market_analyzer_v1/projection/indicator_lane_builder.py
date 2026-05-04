from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class LaneDefinition:
    lane_id: str
    label: str
    anchor_symbols: Tuple[str, ...]
    buy_candidates: Tuple[str, ...]
    avoid_candidates: Tuple[str, ...]
    fade_candidates: Tuple[str, ...]
    driver_candidates: Tuple[str, ...]


LANE_REGISTRY: Tuple[LaneDefinition, ...] = (
    LaneDefinition(
        lane_id="energy",
        label="Energy",
        anchor_symbols=("XLE", "CL", "USO"),
        buy_candidates=("EOG", "OXY", "SLB"),
        avoid_candidates=("KMI", "XOM", "CVX"),
        fade_candidates=("MRO", "APA", "XLE"),
        driver_candidates=("CL", "XLE", "USO"),
    ),
    LaneDefinition(
        lane_id="staples",
        label="Staples",
        anchor_symbols=("XLP",),
        buy_candidates=("PG", "KO", "PEP"),
        avoid_candidates=("KHC", "MDLZ", "MO"),
        fade_candidates=("XLY", "TSLA", "AMZN"),
        driver_candidates=("XLP", "XLU", "TLT"),
    ),
    LaneDefinition(
        lane_id="utilities",
        label="Utilities",
        anchor_symbols=("XLU",),
        buy_candidates=("NEE", "DUK", "SO"),
        avoid_candidates=("AEP", "EXC", "D"),
        fade_candidates=("KRE", "IWM", "XLY"),
        driver_candidates=("XLU", "TLT", "GLD"),
    ),
    LaneDefinition(
        lane_id="risk",
        label="Risk / Growth",
        anchor_symbols=("XLK", "QQQ", "XLY"),
        buy_candidates=("NVDA", "MSFT", "AMZN"),
        avoid_candidates=("AAPL", "META", "GOOGL"),
        fade_candidates=("ARKK", "IWM", "XLY"),
        driver_candidates=("QQQ", "XLK", "TNX"),
    ),
    LaneDefinition(
        lane_id="macro",
        label="Macro / Safety",
        anchor_symbols=("TLT", "GLD", "DXY"),
        buy_candidates=("GLD", "TLT", "XLU"),
        avoid_candidates=("KRE", "IWM", "XLY"),
        fade_candidates=("XBI", "ARKK", "SMH"),
        driver_candidates=("TLT", "GLD", "DXY"),
    ),
)


def build_multi_lane_watchlist(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic multi-lane watchlist builder.

    Output shape is UI ready and keeps the existing watchlist_panel contract:
    {
      "active_lane": "energy",
      "context": {...},
      "lane_suggestions": [...],
      "buy": [...],
      "avoid": [...],
      "fade": [...],
      "drivers": [...]
    }
    """
    context = _extract_context(payload)
    lane_scores = _score_lanes(context)
    selected_lanes = _select_lanes(lane_scores)
    lane_outputs = [_build_lane_output(lane, context) for lane in selected_lanes]
    merged = _merge_lane_outputs(lane_outputs)

    return {
        "active_lane": selected_lanes[0].lane_id if selected_lanes else "macro",
        "context": {
            "symbol": context.get("symbol"),
            "headline": context.get("headline"),
            "setup_type": context.get("setup_type"),
            "confirmation": context.get("confirmation"),
            "history_bias": context.get("history_bias"),
            "history_note": context.get("history_note"),
        },
        "lane_suggestions": lane_outputs,
        "buy": merged["buy"],
        "avoid": merged["avoid"],
        "fade": merged["fade"],
        "drivers": merged["drivers"],
    }


def _extract_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    operator_packet = _as_dict(payload.get("operator_packet"))
    current_case = _as_dict(operator_packet.get("current_case"))
    source_1_summary = _as_dict(operator_packet.get("source_1_summary"))
    source_2_summary = _as_dict(operator_packet.get("source_2_summary"))
    runtime_panel = _as_dict(current_case.get("runtime_panel"))
    recommendation_panel = _as_dict(current_case.get("recommendation_panel"))

    symbol = (
        _first_non_empty(
            current_case.get("symbol"),
            runtime_panel.get("symbol"),
            source_1_summary.get("symbol"),
            payload.get("symbol"),
        )
        or _extract_symbol_from_recommendations(recommendation_panel)
        or "UNKNOWN"
    )

    headline = _first_non_empty(
        current_case.get("headline"),
        runtime_panel.get("headline"),
        source_1_summary.get("headline"),
        payload.get("headline"),
    )

    setup_type = _first_non_empty(
        source_2_summary.get("setup_type"),
        source_1_summary.get("setup_type"),
        current_case.get("detected_setup"),
        current_case.get("setup_type"),
    )

    confirmation = _normalize_confirmation(
        _first_non_empty(
            source_1_summary.get("confirmation"),
            current_case.get("confirmation"),
            payload.get("confirmation"),
        )
    )

    history_bias, history_note = _derive_history_bias(source_2_summary)
    return {
        "symbol": str(symbol).upper(),
        "headline": headline or "",
        "setup_type": setup_type or "",
        "confirmation": confirmation,
        "history_bias": history_bias,
        "history_note": history_note,
    }


def _derive_history_bias(source_2_summary: Dict[str, Any]) -> Tuple[str, str]:
    posture = str(source_2_summary.get("historical_posture") or "").strip().lower()
    follow_through = _to_float(source_2_summary.get("follow_through_rate_pct"))
    failure = _to_float(source_2_summary.get("failure_rate_pct"))
    pattern_count = _to_int(source_2_summary.get("pattern_count"))
    outcome_count = _to_int(source_2_summary.get("outcome_count"))

    if "constructive" in posture:
        return "supportive", "History supports continuation."

    if "mixed" in posture:
        note = f"History is mixed across {outcome_count or pattern_count or 0} labeled outcomes."
        return "mixed", note

    if "weak" in posture or "not_available" in posture:
        return "weak", "Historical context is weak."

    if follow_through is not None and failure is not None:
        if failure > follow_through:
            note = (
                f"History argues for caution. Failure rate {failure:.2f}% "
                f"vs follow-through {follow_through:.2f}%."
            )
            return "caution", note
        if follow_through > failure:
            note = (
                f"History supports continuation. Follow-through {follow_through:.2f}% "
                f"vs failure {failure:.2f}%."
            )
            return "supportive", note
        return "mixed", "History is balanced with no clear edge."

    return "unknown", "Historical edge is unclear."


def _score_lanes(context: Dict[str, Any]) -> List[Tuple[LaneDefinition, float]]:
    symbol = context.get("symbol", "").upper()
    headline = str(context.get("headline") or "").lower()
    setup_type = str(context.get("setup_type") or "").lower()

    keyword_map = {
        "energy": ("oil", "crude", "energy", "gas", "refinery", "e&p", "e&p", "hormuz"),
        "staples": ("staples", "defensive", "consumer defensive", "demand", "supply concern"),
        "utilities": ("utilities", "power", "grid", "electric", "defensive yield"),
        "risk": ("tech", "growth", "consumer discretionary", "risk-on", "momentum"),
        "macro": ("treasury", "bond", "yield", "gold", "dollar", "risk-off", "macro"),
    }

    scored: List[Tuple[LaneDefinition, float]] = []
    for lane in LANE_REGISTRY:
        score = 0.0
        if symbol in lane.anchor_symbols:
            score += 10.0
        if lane.lane_id in setup_type:
            score += 2.0
        for keyword in keyword_map.get(lane.lane_id, ()):
            if keyword in headline:
                score += 1.5
        if lane.lane_id == "macro":
            score += 0.25
        scored.append((lane, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored


def _select_lanes(lane_scores: List[Tuple[LaneDefinition, float]]) -> List[LaneDefinition]:
    if not lane_scores:
        return [LANE_REGISTRY[-1]]

    selected: List[LaneDefinition] = []
    for lane, score in lane_scores:
        if score > 0 or not selected:
            selected.append(lane)
        if len(selected) >= 5:
            break

    if len(selected) < 5:
        for lane in LANE_REGISTRY:
            if lane not in selected:
                selected.append(lane)
            if len(selected) >= 5:
                break

    return selected[:5]


def _build_lane_output(lane: LaneDefinition, context: Dict[str, Any]) -> Dict[str, Any]:
    history_bias = context.get("history_bias", "unknown")
    confirmation = context.get("confirmation", "unknown")
    symbol = context.get("symbol", "").upper()

    buy_tone = _buy_tone(history_bias=history_bias, confirmation=confirmation)
    fade_tone = _fade_tone(history_bias=history_bias, confirmation=confirmation)
    avoid_tone = _avoid_tone(history_bias=history_bias)

    buy = [
        _watch_item(item, f"{lane.label.lower()} continuation candidate | {buy_tone}")
        for item in lane.buy_candidates
    ]
    avoid = [
        _watch_item(item, f"no clear edge | {avoid_tone}")
        for item in lane.avoid_candidates
    ]
    fade = [
        _watch_item(item, f"failure-sensitive on weakness | {fade_tone}")
        for item in lane.fade_candidates
    ]
    drivers = [
        _watch_item(item, f"confirmation driver for {lane.label.lower()} lane")
        for item in lane.driver_candidates
    ]

    if symbol in lane.anchor_symbols:
        drivers.insert(
            0,
            _watch_item(symbol, f"active anchor for {lane.label.lower()} lane"),
        )

    return {
        "lane_id": lane.lane_id,
        "label": lane.label,
        "summary": _lane_summary(lane, context),
        "buy": buy[:3],
        "avoid": avoid[:3],
        "fade": fade[:3],
        "drivers": _dedupe_items(drivers)[:3],
    }


def _buy_tone(history_bias: str, confirmation: str) -> str:
    if history_bias == "supportive" and confirmation == "confirmed":
        return "history supports follow-through"
    if history_bias in {"caution", "mixed", "weak", "unknown"}:
        return "conditional only"
    return "needs confirmation"


def _fade_tone(history_bias: str, confirmation: str) -> str:
    if history_bias == "caution":
        return "history favors failure"
    if confirmation != "confirmed":
        return "confirmation is weak"
    if history_bias == "mixed":
        return "mixed history, react only on weakness"
    return "watch for failure"

def _avoid_tone(history_bias: str) -> str:
    if history_bias == "supportive":
        return "lower priority than stronger names"
    if history_bias == "caution":
        return "history argues for caution"
    return "edge is unclear"


def _lane_summary(lane: LaneDefinition, context: Dict[str, Any]) -> str:
    confirmation = context.get("confirmation", "unknown")
    history_note = context.get("history_note", "Historical edge is unclear.")
    symbol = context.get("symbol", "").upper()

    if symbol in lane.anchor_symbols:
        return (
            f"{lane.label} lane is active. Signal is {confirmation}. "
            f"{history_note}"
        )

    return (
        f"{lane.label} lane is secondary context. Signal posture remains {confirmation}. "
        f"{history_note}"
    )


def _merge_lane_outputs(lane_outputs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
    merged = {
        "buy": [],
        "avoid": [],
        "fade": [],
        "drivers": [],
    }

    merged["buy"] = _merge_bucket(lane_outputs, "buy", limit=5)
    merged["avoid"] = _merge_bucket(lane_outputs, "avoid", limit=5)
    merged["fade"] = _merge_bucket(lane_outputs, "fade", limit=5)
    merged["drivers"] = _merge_bucket(lane_outputs, "drivers", limit=5)
    return merged


def _merge_bucket(
    lane_outputs: Iterable[Dict[str, Any]],
    bucket: str,
    limit: int,
) -> List[Dict[str, str]]:
    seen: set[str] = set()
    merged: List[Dict[str, str]] = []

    for lane_output in lane_outputs:
        for item in lane_output.get(bucket, []):
            symbol = str(item.get("symbol") or "").upper()
            if not symbol or symbol in seen:
                continue
            seen.add(symbol)
            merged.append(item)
            if len(merged) >= limit:
                return merged

    return merged


def _watch_item(symbol: str, note: str) -> Dict[str, str]:
    return {
        "symbol": str(symbol).upper(),
        "note": note,
    }


def _dedupe_items(items: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    seen: set[str] = set()
    result: List[Dict[str, str]] = []
    for item in items:
        symbol = str(item.get("symbol") or "").upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        result.append(item)
    return result


def _extract_symbol_from_recommendations(recommendation_panel: Dict[str, Any]) -> Optional[str]:
    items = recommendation_panel.get("items")
    if not isinstance(items, list):
        return None

    for item in items:
        if isinstance(item, dict) and item.get("symbol"):
            return str(item["symbol"]).upper()
    return None


def _normalize_confirmation(value: Optional[str]) -> str:
    text = str(value or "").strip().lower()
    if text in {"confirmed", "strong", "external_signal"}:
        return "confirmed"
    if text in {"partial", "watch", "external_watch"}:
        return "partial"
    if text in {"rejected", "failed", "weak"}:
        return "weak"
    return "unknown"


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


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
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None