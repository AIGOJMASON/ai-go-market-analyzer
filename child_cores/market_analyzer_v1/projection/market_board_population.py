from __future__ import annotations

from typing import Any, Dict, List, Optional


BOARD_VERSION = "v1"


INDICATOR_PANEL_SPECS: List[Dict[str, str]] = [
    {
        "symbol": "SPY",
        "full_name": "SPDR S&P 500 ETF Trust",
        "meaning": "Broad market risk appetite.",
    },
    {
        "symbol": "QQQ",
        "full_name": "Invesco QQQ Trust",
        "meaning": "Growth and tech leadership.",
    },
    {
        "symbol": "XLE",
        "full_name": "Energy Select Sector SPDR Fund",
        "meaning": "Energy sector strength and supply-shock response.",
    },
    {
        "symbol": "XLP",
        "full_name": "Consumer Staples Select Sector SPDR Fund",
        "meaning": "Defensive consumer rotation.",
    },
    {
        "symbol": "XLU",
        "full_name": "Utilities Select Sector SPDR Fund",
        "meaning": "Safety, defensiveness, and yield sensitivity.",
    },
    {
        "symbol": "TLT",
        "full_name": "iShares 20+ Year Treasury Bond ETF",
        "meaning": "Bond flow, macro safety, and rate-pressure release.",
    },
]


COMMODITY_SPECS: List[Dict[str, str]] = [
    {"symbol": "CL", "label": "Crude Oil"},
    {"symbol": "NG", "label": "Natural Gas"},
    {"symbol": "GC", "label": "Gold"},
    {"symbol": "SI", "label": "Silver"},
    {"symbol": "HG", "label": "Copper"},
    {"symbol": "WHEAT", "label": "Wheat"},
    {"symbol": "CORN", "label": "Corn"},
    {"symbol": "SOYBEANS", "label": "Soybeans"},
    {"symbol": "SUGAR", "label": "Sugar"},
    {"symbol": "COFFEE", "label": "Coffee"},
    {"symbol": "COCOA", "label": "Cocoa"},
    {"symbol": "COTTON", "label": "Cotton"},
]


ENERGY_DRIVER_SYMBOLS = {"CL", "USO"}
ENERGY_WATCH_SYMBOLS = {"XLE", "MRO", "APA"}
ENERGY_BUY_SYMBOLS = {"EOG", "OXY", "SLB"}


def _safe_get(d: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _as_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _as_upper(value: Any) -> str:
    return _as_text(value).upper()


def _extract_active_symbol(payload: Dict[str, Any]) -> str:
    return (
        _as_upper(payload.get("symbol"))
        or _as_upper(_safe_get(payload, "market_panel", "symbol"))
        or _as_upper(_safe_get(payload, "operator_packet", "current_case", "symbol"))
    )


def _extract_event_theme(payload: Dict[str, Any]) -> str:
    return (
        _as_text(payload.get("event_theme"))
        or _as_text(_safe_get(payload, "runtime_panel", "event_theme"))
        or _as_text(_safe_get(payload, "market_panel", "event_theme"))
    )


def _extract_headline(payload: Dict[str, Any]) -> str:
    return (
        _as_text(_safe_get(payload, "runtime_panel", "headline"))
        or _as_text(_safe_get(payload, "market_panel", "headline"))
        or _as_text(_safe_get(payload, "operator_packet", "current_case", "headline"))
    )


def _extract_price_change_pct(payload: Dict[str, Any]) -> Optional[float]:
    return (
        _as_float(_safe_get(payload, "market_panel", "price_change_pct"))
        or _as_float(_safe_get(payload, "operator_packet", "current_case", "price_change_pct"))
        or _as_float(payload.get("price_change_pct"))
    )


def _extract_reference_price(payload: Dict[str, Any]) -> Optional[float]:
    return (
        _as_float(payload.get("reference_price"))
        or _as_float(_safe_get(payload, "market_panel", "reference_price"))
        or _as_float(_safe_get(payload, "operator_packet", "current_case", "reference_price"))
        or _as_float(_safe_get(payload, "market_panel", "price"))
    )


def _extract_formal_score(payload: Dict[str, Any]) -> Optional[float]:
    candidates = [
        payload.get("formal_score"),
        _safe_get(payload, "action_board", "formal_score"),
        _safe_get(payload, "watchlist_panel", "formal_score"),
        _safe_get(payload, "watchlist_panel", "context", "formal_score"),
        _safe_get(payload, "watchlist_panel", "model", "formal_score"),
        _safe_get(payload, "operator_packet", "watchlist_panel", "formal_score"),
        _safe_get(payload, "operator_packet", "watchlist_panel", "context", "formal_score"),
        _safe_get(payload, "operator_packet", "watchlist_panel", "model", "formal_score"),
    ]
    for value in candidates:
        parsed = _as_float(value)
        if parsed is not None:
            return parsed
    return None


def _extract_memory_posture(payload: Dict[str, Any]) -> str:
    return (
        _as_text(_safe_get(payload, "external_memory_packet", "advisory_posture"))
        or _as_text(_safe_get(payload, "recent_memory_board", "posture"))
        or "absent"
    )


def _extract_promotion_score(payload: Dict[str, Any]) -> Optional[float]:
    return (
        _as_float(_safe_get(payload, "external_memory_packet", "advisory_summary", "promotion_score"))
        or _as_float(_safe_get(payload, "source_1_summary", "promotion_artifact", "promotion_score"))
        or _as_float(_safe_get(payload, "recent_memory_board", "promotion_score"))
    )


def _extract_promoted_record_count(payload: Dict[str, Any]) -> int:
    candidates = [
        _safe_get(payload, "external_memory_packet", "advisory_summary", "record_count"),
        _safe_get(payload, "source_1_summary", "promotion_artifact", "record_count"),
        _safe_get(payload, "recent_memory_board", "promoted_records"),
    ]
    for value in candidates:
        if isinstance(value, int):
            return value
    return 0


def _extract_historical_panel(payload: Dict[str, Any]) -> Dict[str, Any]:
    return (
        _safe_get(payload, "source_2_summary", "historical_context", "event_history_panel", default={})
        or _safe_get(payload, "historical_board", default={})
        or {}
    )


def _format_pct(value: Optional[float], digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}%"


def _format_price(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{value:.2f}"


def _derive_board_posture(payload: Dict[str, Any]) -> str:
    watchlist_posture = (
        _as_text(_safe_get(payload, "watchlist_panel", "posture_label"))
        or _as_text(_safe_get(payload, "action_board", "posture_label"))
    )
    if watchlist_posture:
        return watchlist_posture

    formal_score = _extract_formal_score(payload)
    if formal_score is None:
        return "placeholder"
    if formal_score >= 0.7:
        return "constructive"
    if formal_score >= 0.45:
        return "watchful_neutral"
    return "fade_grade"


def _derive_current_read(payload: Dict[str, Any]) -> str:
    symbol = _extract_active_symbol(payload)
    event_theme = _extract_event_theme(payload)
    formal_score = _extract_formal_score(payload)
    hist = _extract_historical_panel(payload)

    follow = _as_float(hist.get("follow_through_rate_pct"))
    fail = _as_float(hist.get("failure_rate_pct"))
    outcome_count = hist.get("outcome_count") or 0

    if symbol == "XLE" and event_theme == "energy_rebound":
        lead = (
            f"Energy leads, but posture remains neutral. "
            f"History supports continuation. Follow-through {_format_pct(follow, 1)} vs failure {_format_pct(fail, 1)} across {outcome_count} outcomes."
            if outcome_count
            else "Energy leads, but historical outcome support is not yet available."
        )
        if formal_score is not None:
            tail = (
                f" The current signal should not be trusted on its own. "
                f"Wait for stronger confirmation. Formal score is {formal_score:.2f}, which reads as fade-grade."
                if formal_score < 0.6
                else f" Formal score is {formal_score:.2f}, which supports closer monitoring."
            )
        else:
            tail = ""
        return lead + tail

    headline = _extract_headline(payload)
    if headline:
        return headline

    return "The highest-priority governed takeaway from the latest payload."


def _extract_watch_items(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    watch_items: List[Dict[str, str]] = []

    primary_watch = _as_text(
        _safe_get(payload, "watch_board", "primary_watch")
        or _safe_get(payload, "watchlist_panel", "summary")
    )
    if primary_watch:
        watch_items.append({"symbol": "PRIMARY", "note": primary_watch})

    for bucket_name in ("driver", "buy", "avoid", "fade"):
        bucket = _safe_get(payload, "watchlist_panel", "buckets", bucket_name, default=[])
        if not isinstance(bucket, list):
            continue
        for item in bucket:
            if not isinstance(item, dict):
                continue
            symbol = _as_upper(item.get("symbol"))
            thesis = _as_text(item.get("thesis") or item.get("note") or item.get("summary"))
            if symbol:
                watch_items.append({"symbol": symbol, "note": thesis or f"{bucket_name} lane watch"})

    return watch_items


def _build_active_indicator_panel(payload: Dict[str, Any], spec: Dict[str, str]) -> Dict[str, Any]:
    symbol = spec["symbol"]
    active_symbol = _extract_active_symbol(payload)
    event_theme = _extract_event_theme(payload)
    formal_score = _extract_formal_score(payload)
    price_change_pct = _extract_price_change_pct(payload)
    reference_price = _extract_reference_price(payload)

    hist = _extract_historical_panel(payload)
    hist_summary = _as_text(hist.get("operator_summary"))
    current_read = _derive_current_read(payload)

    watch_items = _extract_watch_items(payload)
    watch_symbols = [w for w in watch_items if w["symbol"] != "PRIMARY"]
    primary_watch = next((w["note"] for w in watch_items if w["symbol"] == "PRIMARY"), "")

    posture = _derive_board_posture(payload)

    current_move = f"{_format_pct(price_change_pct, 1)} | {_format_price(reference_price)} | sector"

    if symbol != active_symbol:
        return _build_placeholder_indicator_panel(spec)

    watch_text = primary_watch
    if not watch_text and event_theme == "energy_rebound":
        watch_text = (
            "Only treat EOG, OXY, SLB as actionable if the lane keeps confirming. "
            "If momentum fails, shift focus toward XLE, MRO, APA. Use XLE, CL, USO as the confirmation gate."
        )

    return {
        "symbol": symbol,
        "full_name": spec["full_name"],
        "posture": posture,
        "what_it_means": spec["meaning"],
        "current_move": current_move,
        "system_read": current_read if current_read else hist_summary,
        "what_to_watch": watch_text or "No panel-specific trigger available yet.",
        "event_theme": event_theme,
        "formal_score": formal_score,
        "support_symbols": [w["symbol"] for w in watch_symbols],
    }


def _build_placeholder_indicator_panel(spec: Dict[str, str]) -> Dict[str, Any]:
    return {
        "symbol": spec["symbol"],
        "full_name": spec["full_name"],
        "posture": "Placeholder",
        "what_it_means": spec["meaning"],
        "current_move": "Awaiting dedicated live panel data.",
        "system_read": "Awaiting dedicated live panel data.",
        "what_to_watch": "No panel-specific trigger available yet.",
    }


def _build_indicator_panels(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    panels: List[Dict[str, Any]] = []
    active_symbol = _extract_active_symbol(payload)

    for spec in INDICATOR_PANEL_SPECS:
        if spec["symbol"] == active_symbol:
            panels.append(_build_active_indicator_panel(payload, spec))
        else:
            panels.append(_build_placeholder_indicator_panel(spec))

    return panels


def _build_commodity_board(payload: Dict[str, Any]) -> Dict[str, Any]:
    event_theme = _extract_event_theme(payload)
    active_symbol = _extract_active_symbol(payload)

    summary = "Commodity context is not yet populated for the current board."
    trigger_symbols: List[Dict[str, str]] = []

    if active_symbol == "XLE" or event_theme == "energy_rebound":
        summary = "Commodities are currently serving as confirmation for the live energy signal."
        trigger_symbols = [{"symbol": "CL", "note": "confirmation gate for the energy lane"}]

    rows: List[Dict[str, str]] = []
    for spec in COMMODITY_SPECS:
        rows.append(
            {
                "symbol": spec["symbol"],
                "label": spec["label"],
                "move": "move unavailable",
            }
        )

    return {
        "title": "Tracked Commodity Board",
        "posture": "starter",
        "what_it_means": "Raw materials pressure, inflation signals, and supply-driven market stress.",
        "system_read": summary,
        "rows": rows,
        "summary": summary,
        "watch_triggers": trigger_symbols,
    }


def _build_top_buys(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    bucket = _safe_get(payload, "watchlist_panel", "buckets", "buy", default=[])
    if not isinstance(bucket, list):
        bucket = []

    for item in bucket[:5]:
        if not isinstance(item, dict):
            continue
        symbol = _as_upper(item.get("symbol"))
        if not symbol:
            continue
        full_name = _as_text(item.get("full_name") or item.get("name") or symbol)
        note = _as_text(item.get("thesis") or item.get("note") or "conditional only; no clean edge yet")
        result.append({"symbol": symbol, "full_name": full_name, "note": note})

    if result:
        return result

    active_symbol = _extract_active_symbol(payload)
    event_theme = _extract_event_theme(payload)
    formal_score = _extract_formal_score(payload)

    if active_symbol == "XLE" and event_theme == "energy_rebound":
        default_note = (
            "conditional only; no clean edge yet"
            if formal_score is None or formal_score < 0.6
            else "watch for continued confirmation"
        )
        return [
            {"symbol": "EOG", "full_name": "EOG", "note": default_note},
            {"symbol": "OXY", "full_name": "OXY", "note": default_note},
            {"symbol": "SLB", "full_name": "SLB", "note": default_note},
        ]

    return []


def _build_watch_board(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = _extract_watch_items(payload)
    active_symbol = _extract_active_symbol(payload)
    event_theme = _extract_event_theme(payload)

    primary_watch = next((item["note"] for item in items if item["symbol"] == "PRIMARY"), "")
    structured_items = [item for item in items if item["symbol"] != "PRIMARY"]

    if not primary_watch and active_symbol == "XLE" and event_theme == "energy_rebound":
        primary_watch = (
            "Only treat EOG, OXY, SLB as actionable if the lane keeps confirming. "
            "If momentum fails, shift focus toward XLE, MRO, APA. Use XLE, CL, USO as the confirmation gate."
        )
        structured_items = [
            {"symbol": "XLE", "note": "active anchor for the energy lane"},
            {"symbol": "CL", "note": "confirmation gate for the energy lane"},
            {"symbol": "USO", "note": "confirmation gate for the energy lane"},
            {"symbol": "XLE", "note": "watch for failure"},
            {"symbol": "MRO", "note": "watch for failure"},
            {"symbol": "APA", "note": "watch for failure"},
        ]

    return {
        "title": "What to Watch",
        "primary_watch": primary_watch or "No governed watch trigger available yet.",
        "items": structured_items,
    }


def _build_historical_board(payload: Dict[str, Any]) -> Dict[str, Any]:
    hist = _extract_historical_panel(payload)
    return {
        "title": "Historical Read",
        "summary": _as_text(hist.get("operator_summary") or "Historical context is not strong enough to summarize confidently."),
        "symbol": _as_text(hist.get("symbol")),
        "event_theme": _as_text(hist.get("event_theme")),
        "follow_through_rate_pct": _as_float(hist.get("follow_through_rate_pct")),
        "failure_rate_pct": _as_float(hist.get("failure_rate_pct")),
        "outcome_count": hist.get("outcome_count") or 0,
        "historical_posture": _as_text(hist.get("historical_posture")),
    }


def _build_recent_memory_board(payload: Dict[str, Any]) -> Dict[str, Any]:
    posture = _extract_memory_posture(payload)
    promotion_score = _extract_promotion_score(payload)
    record_count = _extract_promoted_record_count(payload)
    coherence_flags = _safe_get(payload, "external_memory_packet", "advisory_summary", "coherence_flags", default=[])

    if not isinstance(coherence_flags, list):
        coherence_flags = []

    return {
        "title": "Recent Memory",
        "posture": posture,
        "promoted_records": record_count,
        "promotion_score": promotion_score,
        "coherence_flags": coherence_flags,
    }


def _build_governance_board(payload: Dict[str, Any]) -> Dict[str, Any]:
    request_id = _as_text(payload.get("request_id"))
    approval_required = bool(
        payload.get("approval_required")
        or _safe_get(payload, "governance_panel", "approval_required")
    )
    execution_allowed = bool(
        payload.get("execution_allowed")
        or _safe_get(payload, "governance_panel", "execution_allowed")
    )
    route_mode = _as_text(payload.get("route_mode") or _safe_get(payload, "governance_panel", "route_path"))

    return {
        "title": "Governance",
        "advisory_only": True,
        "approval_required": approval_required,
        "execution_allowed": execution_allowed,
        "route_mode": route_mode,
        "request_id": request_id,
    }


def build_market_board_population(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds a fixed-universe board payload around the current governed case.

    This file does NOT mutate recommendation or governance truth.
    It assembles a board-shaped read model for UI consumption.
    """
    current_read = _derive_current_read(payload)

    return {
        "dashboard_type": "market_analyzer_v1_market_board",
        "board_version": BOARD_VERSION,
        "board_status": "ok",
        "current_read": current_read,
        "indicator_panels": _build_indicator_panels(payload),
        "commodity_board": _build_commodity_board(payload),
        "top_buys": _build_top_buys(payload),
        "watch_board": _build_watch_board(payload),
        "historical_board": _build_historical_board(payload),
        "recent_memory_board": _build_recent_memory_board(payload),
        "governance_board": _build_governance_board(payload),
    }