from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

try:
    from AI_GO.child_cores.market_analyzer_v1.projection.external_memory_projection import (
        build_external_memory_projection,
    )
    from AI_GO.child_cores.market_analyzer_v1.projection.historical_context_projection import (
        build_historical_context_projection,
    )
    from AI_GO.child_cores.market_analyzer_v1.projection.labeled_outcomes_projection import (
        build_labeled_outcomes_projection,
    )
    from AI_GO.child_cores.market_analyzer_v1.projection.watchlist_projection import (
        build_watchlist_projection,
    )
    from AI_GO.child_cores.market_analyzer_v1.projection.board_quote_snapshot import (
        build_board_quote_snapshot,
    )
    from AI_GO.child_cores.market_analyzer_v1.explanation.operator_explainer import (
        generate_operator_explanation,
    )
except ImportError:
    from child_cores.market_analyzer_v1.projection.external_memory_projection import (
        build_external_memory_projection,
    )
    from child_cores.market_analyzer_v1.projection.historical_context_projection import (
        build_historical_context_projection,
    )
    from child_cores.market_analyzer_v1.projection.labeled_outcomes_projection import (
        build_labeled_outcomes_projection,
    )
    from child_cores.market_analyzer_v1.projection.watchlist_projection import (
        build_watchlist_projection,
    )
    from child_cores.market_analyzer_v1.projection.board_quote_snapshot import (
        build_board_quote_snapshot,
    )
    from child_cores.market_analyzer_v1.explanation.operator_explainer import (
        generate_operator_explanation,
    )


INDICATOR_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "panel_id": "SPY",
        "display_order": 1,
        "symbol": "SPY",
        "full_name": "SPDR S&P 500 ETF Trust",
        "category": "broad_market",
        "meaning": "Broad market risk appetite.",
    },
    {
        "panel_id": "QQQ",
        "display_order": 2,
        "symbol": "QQQ",
        "full_name": "Invesco QQQ Trust",
        "category": "growth",
        "meaning": "Growth and tech leadership.",
    },
    {
        "panel_id": "XLE",
        "display_order": 3,
        "symbol": "XLE",
        "full_name": "Energy Select Sector SPDR Fund",
        "category": "sector",
        "meaning": "Energy sector strength and supply-shock response.",
    },
    {
        "panel_id": "XLP",
        "display_order": 4,
        "symbol": "XLP",
        "full_name": "Consumer Staples Select Sector SPDR Fund",
        "category": "sector",
        "meaning": "Defensive consumer rotation.",
    },
    {
        "panel_id": "XLU",
        "display_order": 5,
        "symbol": "XLU",
        "full_name": "Utilities Select Sector SPDR Fund",
        "category": "sector",
        "meaning": "Safety, defensiveness, and yield sensitivity.",
    },
    {
        "panel_id": "TLT",
        "display_order": 6,
        "symbol": "TLT",
        "full_name": "iShares 20+ Year Treasury Bond ETF",
        "category": "macro_safety",
        "meaning": "Bond flow, macro safety, and rate-pressure release.",
    },
    {
        "panel_id": "COMMODITIES",
        "display_order": 7,
        "symbol": "COMMODITIES",
        "full_name": "Tracked Commodity Board",
        "category": "commodities",
        "meaning": "Raw materials pressure, inflation signals, and supply-driven market stress.",
    },
]

COMMODITY_DEFINITIONS: List[Dict[str, str]] = [
    {"symbol": "CL", "full_name": "Crude Oil", "category": "energy"},
    {"symbol": "NG", "full_name": "Natural Gas", "category": "energy"},
    {"symbol": "GC", "full_name": "Gold", "category": "metals"},
    {"symbol": "SI", "full_name": "Silver", "category": "metals"},
    {"symbol": "HG", "full_name": "Copper", "category": "metals"},
    {"symbol": "ZW", "full_name": "Wheat", "category": "agriculture"},
    {"symbol": "ZC", "full_name": "Corn", "category": "agriculture"},
    {"symbol": "ZS", "full_name": "Soybeans", "category": "agriculture"},
    {"symbol": "SB", "full_name": "Sugar", "category": "softs"},
    {"symbol": "KC", "full_name": "Coffee", "category": "softs"},
    {"symbol": "CC", "full_name": "Cocoa", "category": "softs"},
    {"symbol": "CT", "full_name": "Cotton", "category": "softs"},
]

FULL_NAME_OVERRIDES: Dict[str, str] = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "QQQ": "Invesco QQQ Trust",
    "XLE": "Energy Select Sector SPDR Fund",
    "XLP": "Consumer Staples Select Sector SPDR Fund",
    "XLU": "Utilities Select Sector SPDR Fund",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "XOM": "Exxon Mobil Corporation",
    "CVX": "Chevron Corporation",
    "KMI": "Kinder Morgan, Inc.",
    "MRO": "Marathon Oil Corporation",
    "APA": "APA Corporation",
    "CL": "Crude Oil",
    "USO": "United States Oil Fund, LP",
    "NG": "Natural Gas",
    "GC": "Gold",
    "SI": "Silver",
    "HG": "Copper",
    "ZW": "Wheat",
    "ZC": "Corn",
    "ZS": "Soybeans",
    "SB": "Sugar",
    "KC": "Coffee",
    "CC": "Cocoa",
    "CT": "Cotton",
    "GLD": "SPDR Gold Shares",
    "NEE": "NextEra Energy, Inc.",
    "DUK": "Duke Energy Corporation",
    "SO": "The Southern Company",
    "AEP": "American Electric Power Company, Inc.",
    "EXC": "Exelon Corporation",
    "D": "Dominion Energy, Inc.",
    "KRE": "SPDR S&P Regional Banking ETF",
    "IWM": "iShares Russell 2000 ETF",
    "KHC": "The Kraft Heinz Company",
    "MDLZ": "Mondelez International, Inc.",
    "MO": "Altria Group, Inc.",
    "PG": "The Procter & Gamble Company",
    "KO": "The Coca-Cola Company",
    "PEP": "PepsiCo, Inc.",
    "XLY": "Consumer Discretionary Select Sector SPDR Fund",
    "TSLA": "Tesla, Inc.",
    "AMZN": "Amazon.com, Inc.",
}


def _safe_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return deepcopy(value) if isinstance(value, list) else []


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return None
            return float(normalized)
        return float(value)
    except (TypeError, ValueError):
        return None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _extract_governance_panel(normalized_result: dict[str, Any]) -> dict[str, Any]:
    return _safe_dict(normalized_result.get("governance_panel"))


def _extract_live_event_panel(normalized_result: dict[str, Any]) -> dict[str, Any]:
    live_event_panel = _safe_dict(normalized_result.get("live_event_panel"))
    if live_event_panel:
        return live_event_panel

    payload_like = {
        "symbol": normalized_result.get("symbol"),
        "headline": normalized_result.get("headline"),
        "summary": normalized_result.get("summary"),
        "price_change_pct": normalized_result.get("price_change_pct"),
        "confirmation": normalized_result.get("confirmation"),
        "observed_at": normalized_result.get("observed_at"),
        "published_at": normalized_result.get("published_at"),
        "source": normalized_result.get("source"),
        "source_type": normalized_result.get("source_type"),
        "source_url": normalized_result.get("source_url"),
        "provider_metadata": normalized_result.get("provider_metadata"),
        "sector": normalized_result.get("sector"),
        "event_theme": normalized_result.get("event_theme"),
        "reference_price": normalized_result.get("reference_price"),
        "price_at_closeout": normalized_result.get("price_at_closeout"),
        "price": normalized_result.get("price"),
    }
    return {k: v for k, v in payload_like.items() if v is not None}


def _extract_runtime_panel(normalized_result: dict[str, Any]) -> dict[str, Any]:
    return _safe_dict(normalized_result.get("runtime_panel"))


def _extract_history_panel(source_2_summary: dict[str, Any]) -> dict[str, Any]:
    historical_context = _safe_dict(source_2_summary.get("historical_context"))
    event_history_panel = _safe_dict(historical_context.get("event_history_panel"))
    if event_history_panel:
        return event_history_panel
    return _safe_dict(historical_context.get("setup_history_panel"))


def _extract_recent_memory_summary(
    source_1_summary: dict[str, Any],
    external_memory_packet: dict[str, Any],
) -> dict[str, Any]:
    external_advisory = _safe_dict(external_memory_packet.get("advisory_summary"))
    if external_advisory:
        return external_advisory

    promotion_artifact = _safe_dict(source_1_summary.get("promotion_artifact"))
    return _safe_dict(promotion_artifact.get("advisory_summary"))


def _derive_symbol(
    *,
    payload: dict[str, Any],
    normalized_result: dict[str, Any],
) -> str:
    recommendation_panel = _safe_dict(normalized_result.get("recommendation_panel"))
    items = recommendation_panel.get("items") or [{}]
    live_event_panel = _extract_live_event_panel(normalized_result)
    market_panel = _safe_dict(normalized_result.get("market_panel"))

    return str(
        payload.get("symbol")
        or normalized_result.get("symbol")
        or live_event_panel.get("symbol")
        or market_panel.get("symbol")
        or items[0].get("symbol")
        or ""
    ).strip().upper()


def _derive_price_change_pct(
    *,
    normalized_result: dict[str, Any],
    payload: dict[str, Any],
    live_event_panel: dict[str, Any],
) -> float | None:
    candidates = [
        live_event_panel.get("price_change_pct"),
        normalized_result.get("price_change_pct"),
        _safe_dict(normalized_result.get("market_panel")).get("price_change_pct"),
        payload.get("price_change_pct"),
    ]
    for candidate in candidates:
        numeric = _safe_float(candidate)
        if numeric is not None:
            return numeric
    return None


def _derive_confirmation(
    *,
    normalized_result: dict[str, Any],
    payload: dict[str, Any],
    live_event_panel: dict[str, Any],
) -> str | None:
    value = _coalesce(
        live_event_panel.get("confirmation"),
        normalized_result.get("confirmation"),
        _safe_dict(normalized_result.get("market_panel")).get("confirmation"),
        payload.get("confirmation"),
    )
    if value is None:
        return None
    text = str(value).strip().lower()
    return text or None


def _normalize_recommendation_panel(normalized_result: dict[str, Any]) -> dict[str, Any]:
    panel = _safe_dict(normalized_result.get("recommendation_panel"))
    items = _safe_list(panel.get("items"))
    state = panel.get("state")
    if state is None:
        state = "no_recommendation" if not items else "present"
    count = panel.get("count")
    if count is None:
        count = len([item for item in items if isinstance(item, dict)])
    return {
        "state": state,
        "count": count,
        "items": items,
    }


def _group_watchlist_items(watchlist_panel: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {
        "buy": [],
        "avoid": [],
        "fade": [],
        "driver": [],
    }

    buckets = _safe_dict(watchlist_panel.get("buckets"))
    for bucket_name in grouped.keys():
        bucket_items = _safe_list(buckets.get(bucket_name))
        grouped[bucket_name].extend([item for item in bucket_items if isinstance(item, dict)])

    for item in _safe_list(watchlist_panel.get("items")):
        if not isinstance(item, dict):
            continue
        bucket = str(item.get("bucket") or "").strip().lower()
        if bucket in grouped:
            grouped[bucket].append(item)
    return grouped


def _full_name_for_symbol(symbol: str) -> str:
    normalized = str(symbol or "").strip().upper()
    return FULL_NAME_OVERRIDES.get(normalized, normalized or "Unknown")


def _direction_from_pct(value: Any) -> str | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number > 0:
        return "up"
    if number < 0:
        return "down"
    return "flat"


def _display_move(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "move unavailable"
    prefix = "+" if number > 0 else ""
    return f"{prefix}{number:.1f}%"


def _derive_numeric_price(
    *,
    normalized_result: dict[str, Any],
    payload: dict[str, Any],
) -> float | None:
    live_event_panel = _extract_live_event_panel(normalized_result)
    market_panel = _safe_dict(normalized_result.get("market_panel"))
    recommendation_panel = _safe_dict(normalized_result.get("recommendation_panel"))
    recommendation_items = _safe_list(recommendation_panel.get("items"))

    candidate_values = [
        payload.get("reference_price"),
        payload.get("price_at_closeout"),
        payload.get("current_price"),
        payload.get("price"),
        payload.get("last_price"),
        market_panel.get("reference_price"),
        market_panel.get("price_at_closeout"),
        market_panel.get("current_price"),
        market_panel.get("price"),
        live_event_panel.get("reference_price"),
        live_event_panel.get("price_at_closeout"),
        live_event_panel.get("current_price"),
        live_event_panel.get("price"),
        normalized_result.get("reference_price"),
        normalized_result.get("price_at_closeout"),
        normalized_result.get("current_price"),
        normalized_result.get("price"),
        normalized_result.get("last_price"),
    ]

    if recommendation_items and isinstance(recommendation_items[0], dict):
        first_item = recommendation_items[0]
        candidate_values.extend(
            [
                first_item.get("reference_price"),
                first_item.get("entry_price"),
                first_item.get("price"),
            ]
        )

    for candidate in candidate_values:
        numeric = _safe_float(candidate)
        if numeric is not None:
            return numeric

    return None


def _build_market_panel(
    *,
    normalized_result: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    existing_market_panel = _safe_dict(normalized_result.get("market_panel"))
    runtime_panel = _extract_runtime_panel(normalized_result)
    live_event_panel = _extract_live_event_panel(normalized_result)
    symbol = _derive_symbol(payload=payload, normalized_result=normalized_result)

    market_panel = existing_market_panel
    market_panel["symbol"] = _coalesce(
        market_panel.get("symbol"),
        live_event_panel.get("symbol"),
        normalized_result.get("symbol"),
        payload.get("symbol"),
        symbol,
    )
    market_panel["market_regime"] = _coalesce(
        market_panel.get("market_regime"),
        runtime_panel.get("market_regime"),
    )
    market_panel["event_theme"] = _coalesce(
        market_panel.get("event_theme"),
        runtime_panel.get("event_theme"),
        live_event_panel.get("event_theme"),
        normalized_result.get("event_theme"),
        payload.get("event_theme_candidate"),
    )
    market_panel["macro_bias"] = _coalesce(
        market_panel.get("macro_bias"),
        runtime_panel.get("macro_bias"),
    )
    market_panel["headline"] = _coalesce(
        market_panel.get("headline"),
        runtime_panel.get("headline"),
        live_event_panel.get("headline"),
        payload.get("headline"),
    )
    market_panel["confirmation"] = _coalesce(
        market_panel.get("confirmation"),
        live_event_panel.get("confirmation"),
        normalized_result.get("confirmation"),
        payload.get("confirmation"),
    )
    market_panel["price_change_pct"] = _coalesce(
        market_panel.get("price_change_pct"),
        live_event_panel.get("price_change_pct"),
        normalized_result.get("price_change_pct"),
        payload.get("price_change_pct"),
    )
    market_panel["observed_at"] = _coalesce(
        market_panel.get("observed_at"),
        live_event_panel.get("observed_at"),
        payload.get("observed_at"),
    )

    numeric_price = _derive_numeric_price(
        normalized_result=normalized_result,
        payload=payload,
    )
    if numeric_price is not None:
        market_panel["reference_price"] = numeric_price
        market_panel["price_at_closeout"] = numeric_price
        if market_panel.get("price") is None:
            market_panel["price"] = numeric_price

    return {key: value for key, value in market_panel.items() if value is not None}


def _build_header_panel(
    *,
    normalized_result: dict[str, Any],
) -> dict[str, Any]:
    governance_panel = _extract_governance_panel(normalized_result)

    return {
        "title": "AI_GO Market Board",
        "subtitle": "Governed market read from live signal, historical outcomes, and recent memory.",
        "request_id": normalized_result.get("request_id"),
        "mode": normalized_result.get("mode"),
        "route_mode": normalized_result.get("route_mode") or governance_panel.get("route_path"),
        "approval_required": governance_panel.get("approval_required"),
        "execution_allowed": governance_panel.get("execution_allowed"),
        "last_updated_at": _utc_now_iso(),
        "update_state": "latest_payload_loaded",
    }


def _board_snapshot_summary(symbol: str, quote_row: dict[str, Any]) -> str:
    price = quote_row.get("price")
    price_change_pct = quote_row.get("price_change_pct")
    observed_at = quote_row.get("observed_at")

    if price is None:
        return "Awaiting dedicated live panel data."

    if price_change_pct is not None and observed_at:
        direction = "up" if price_change_pct > 0 else "down" if price_change_pct < 0 else "flat"
        return (
            f"Board-level live snapshot. {symbol} is {direction} "
            f"{abs(price_change_pct):.2f}% at price {price:.2f} as of {observed_at}."
        )

    if observed_at:
        return f"Board-level live snapshot. Latest price {price:.2f} at {observed_at}."

    return f"Board-level live snapshot. Latest price {price:.2f}."


def _build_indicator_panels(
    *,
    normalized_result: dict[str, Any],
    source_2_summary: dict[str, Any],
    watchlist_panel: dict[str, Any],
    action_board: dict[str, Any],
    watch_board: dict[str, Any],
) -> list[dict[str, Any]]:
    live_event_panel = _extract_live_event_panel(normalized_result)
    active_symbol = str(live_event_panel.get("symbol") or "").strip().upper()
    history_panel = _extract_history_panel(source_2_summary)
    snapshot = build_board_quote_snapshot(
        symbols=[
            "SPY",
            "QQQ",
            "XLE",
            "XLP",
            "XLU",
            "TLT",
        ]
    )

    panels: list[dict[str, Any]] = []
    for config in INDICATOR_DEFINITIONS:
        panel_id = str(config["panel_id"])
        symbol = str(config["symbol"])
        is_active = active_symbol == symbol and symbol != "COMMODITIES"

        if panel_id == "COMMODITIES":
            panels.append(
                {
                    "panel_id": panel_id,
                    "display_order": config["display_order"],
                    "symbol": symbol,
                    "full_name": config["full_name"],
                    "category": config["category"],
                    "state": "starter",
                    "meaning": config["meaning"],
                    "current_move": {
                        "status": "partial",
                        "price_change_pct": None,
                        "direction": None,
                        "confirmation": None,
                        "headline": None,
                    },
                    "system_read": {
                        "status": "ok",
                        "posture_label": None,
                        "historical_posture": None,
                        "no_trade": bool(_safe_dict(watchlist_panel.get("no_trade_state")).get("is_no_trade")),
                        "summary": "Commodities are currently serving as confirmation for the live energy signal."
                        if watchlist_panel.get("active_lane") == "energy"
                        else "Commodity confirmation data is not yet fully populated in this payload.",
                    },
                    "what_to_watch": {
                        "status": "ok",
                        "summary": _coalesce(
                            watch_board.get("primary_watch_text"),
                            "Watch tracked commodity drivers when they appear on the live feed.",
                        ),
                        "trigger_symbols": [
                            item.get("symbol")
                            for item in _safe_list(watch_board.get("trigger_items"))
                            if isinstance(item, dict) and item.get("symbol")
                        ],
                    },
                    "source_refs": ["commodity_board", "watch_board"],
                }
            )
            continue

        if not is_active:
            quote_row = _safe_dict(snapshot.get(symbol))
            if quote_row.get("status") == "ok":
                panels.append(
                    {
                        "panel_id": panel_id,
                        "display_order": config["display_order"],
                        "symbol": symbol,
                        "full_name": config["full_name"],
                        "category": config["category"],
                        "state": "snapshot",
                        "meaning": config["meaning"],
                        "current_move": {
                            "status": "ok",
                            "price": quote_row.get("price"),
                            "price_change_pct": quote_row.get("price_change_pct"),
                            "direction": _direction_from_pct(quote_row.get("price_change_pct")),
                            "confirmation": None,
                            "headline": None,
                            "observed_at": quote_row.get("observed_at"),
                        },
                        "system_read": {
                            "status": "ok",
                            "posture_label": None,
                            "historical_posture": None,
                            "no_trade": None,
                            "summary": _board_snapshot_summary(symbol, quote_row),
                        },
                        "what_to_watch": {
                            "status": "ok",
                            "summary": "Watch for alignment with the active lane.",
                            "trigger_symbols": [],
                        },
                        "source_refs": ["board_quote_snapshot"],
                    }
                )
            else:
                panels.append(
                    {
                        "panel_id": panel_id,
                        "display_order": config["display_order"],
                        "symbol": symbol,
                        "full_name": config["full_name"],
                        "category": config["category"],
                        "state": "placeholder",
                        "meaning": config["meaning"],
                        "current_move": {
                            "status": "unavailable",
                            "price_change_pct": None,
                            "direction": None,
                            "confirmation": None,
                            "headline": None,
                            "observed_at": None,
                        },
                        "system_read": {
                            "status": "placeholder",
                            "posture_label": None,
                            "historical_posture": None,
                            "no_trade": None,
                            "summary": "Awaiting dedicated live panel data.",
                        },
                        "what_to_watch": {
                            "status": "placeholder",
                            "summary": "No panel-specific trigger available yet.",
                            "trigger_symbols": [],
                        },
                        "source_refs": [],
                    }
                )
            continue

        panels.append(
            {
                "panel_id": panel_id,
                "display_order": config["display_order"],
                "symbol": symbol,
                "full_name": config["full_name"],
                "category": config["category"],
                "state": "active",
                "meaning": config["meaning"],
                "current_move": {
                    "status": "ok",
                    "price_change_pct": live_event_panel.get("price_change_pct"),
                    "direction": _direction_from_pct(live_event_panel.get("price_change_pct")),
                    "confirmation": live_event_panel.get("confirmation"),
                    "headline": live_event_panel.get("headline"),
                    "observed_at": live_event_panel.get("observed_at"),
                    "price": live_event_panel.get("reference_price"),
                },
                "system_read": {
                    "status": "ok",
                    "posture_label": watchlist_panel.get("posture_label"),
                    "historical_posture": history_panel.get("historical_posture"),
                    "no_trade": bool(_safe_dict(watchlist_panel.get("no_trade_state")).get("is_no_trade")),
                    "summary": watchlist_panel.get("summary"),
                },
                "what_to_watch": {
                    "status": "ok",
                    "summary": watch_board.get("primary_watch_text"),
                    "trigger_symbols": [
                        item.get("symbol")
                        for item in _safe_list(watch_board.get("trigger_items"))
                        if isinstance(item, dict) and item.get("symbol")
                    ],
                },
                "source_refs": ["live_event_panel", "watchlist_panel", "source_2_summary"],
            }
        )

    return panels


def _build_commodity_board(
    *,
    watchlist_panel: dict[str, Any],
    live_event_panel: dict[str, Any],
) -> dict[str, Any]:
    grouped = _group_watchlist_items(watchlist_panel)
    driver_symbols = {
        str(item.get("symbol") or "").strip().upper(): item
        for item in grouped.get("driver", [])
        if isinstance(item, dict)
    }
    live_symbol = str(live_event_panel.get("symbol") or "").strip().upper()

    commodity_rows: list[dict[str, Any]] = []
    watch_items: list[dict[str, Any]] = []

    for definition in COMMODITY_DEFINITIONS:
        symbol = definition["symbol"]
        tracked_item = driver_symbols.get(symbol)
        is_live_symbol = live_symbol == symbol

        price_change_pct = None
        if is_live_symbol:
            price_change_pct = live_event_panel.get("price_change_pct")

        state = "tracked" if tracked_item or is_live_symbol else "unavailable"

        row = {
            "symbol": symbol,
            "full_name": definition["full_name"],
            "category": definition["category"],
            "state": state,
            "price_change_pct": price_change_pct,
            "direction": _direction_from_pct(price_change_pct),
            "display_move": _display_move(price_change_pct) if price_change_pct is not None else "move unavailable",
            "is_live_feed_tracked": bool(is_live_symbol),
            "is_watch_item": bool(tracked_item),
        }
        commodity_rows.append(row)

        if tracked_item:
            watch_items.append(
                {
                    "symbol": symbol,
                    "full_name": definition["full_name"],
                    "reason": tracked_item.get("note") or "Watch for confirmation behavior.",
                }
            )

    summary_text = (
        "Commodities are currently serving as confirmation for the live energy signal."
        if watchlist_panel.get("active_lane") == "energy"
        else "Commodity confirmation data is not yet fully populated in this payload."
    )

    return {
        "panel_id": "COMMODITIES",
        "full_name": "Tracked Commodity Board",
        "state": "starter",
        "meaning": "Raw materials pressure, inflation signals, and supply-driven market stress.",
        "system_read": {
            "status": "ok",
            "classification": "confirming_energy"
            if watchlist_panel.get("active_lane") == "energy"
            else "partial",
            "summary": summary_text,
        },
        "summary_line": {
            "status": "ok",
            "text": summary_text,
        },
        "what_to_watch": {
            "status": "ok",
            "items": watch_items[:5],
        },
        "commodity_rows": commodity_rows,
    }


def _build_action_board(
    *,
    watchlist_panel: dict[str, Any],
) -> dict[str, Any]:
    grouped = _group_watchlist_items(watchlist_panel)
    no_trade_state = _safe_dict(watchlist_panel.get("no_trade_state"))
    is_no_trade = bool(no_trade_state.get("is_no_trade"))

    buy_items = grouped.get("buy", [])[:5]
    avoid_items = grouped.get("avoid", [])[:5]
    fade_items = grouped.get("fade", [])[:5]

    if buy_items and not is_no_trade:
        primary_title = "Top 5 Buys Right Now"
        primary_subtitle = "Governed long candidates from the current board."
        primary_list = [
            {
                "symbol": item.get("symbol"),
                "full_name": _full_name_for_symbol(str(item.get("symbol") or "")),
                "action_type": "buy",
                "reason": item.get("note") or item.get("reason") or "Governed long candidate.",
            }
            for item in buy_items
        ]
        state = "buy_candidates"
    else:
        primary_title = "No Governed Buys Right Now"
        primary_subtitle = "Best conditional longs if this setup improves."
        primary_list = [
            {
                "symbol": item.get("symbol"),
                "full_name": _full_name_for_symbol(str(item.get("symbol") or "")),
                "action_type": "conditional_long_watch",
                "reason": item.get("note") or item.get("reason") or "Conditional long watch only.",
            }
            for item in avoid_items
        ]
        state = "no_trade"

    secondary_list = [
        {
            "symbol": item.get("symbol"),
            "full_name": _full_name_for_symbol(str(item.get("symbol") or "")),
            "action_type": "fade",
            "reason": item.get("note") or item.get("reason") or "Failure expression if the setup rolls over.",
        }
        for item in fade_items
    ]

    return {
        "state": state,
        "primary_title": primary_title,
        "primary_subtitle": primary_subtitle,
        "primary_list": primary_list,
        "secondary_title": "Fade Candidates",
        "secondary_list": secondary_list,
        "posture_label": watchlist_panel.get("posture_label"),
        "no_trade_state": _safe_dict(watchlist_panel.get("no_trade_state")),
        "formal_score": _coalesce(
            _safe_dict(watchlist_panel.get("context")).get("formal_score"),
            _safe_dict(watchlist_panel.get("model")).get("formal_score"),
            watchlist_panel.get("formal_score"),
        ),
    }


def _build_watch_board(
    *,
    watchlist_panel: dict[str, Any],
    operator_explanation: dict[str, Any],
) -> dict[str, Any]:
    grouped = _group_watchlist_items(watchlist_panel)

    trigger_items = [
        {
            "symbol": item.get("symbol"),
            "full_name": _full_name_for_symbol(str(item.get("symbol") or "")),
            "trigger_type": "driver",
            "reason": item.get("note") or item.get("reason") or "Confirmation trigger.",
        }
        for item in grouped.get("driver", [])[:5]
    ]

    risk_items = [
        {
            "symbol": item.get("symbol"),
            "full_name": _full_name_for_symbol(str(item.get("symbol") or "")),
            "risk_type": "failure_expression",
            "reason": item.get("note") or item.get("reason") or "Failure expression if momentum fades.",
        }
        for item in grouped.get("fade", [])[:3]
    ]

    return {
        "state": "ok",
        "primary_watch_text": operator_explanation.get("what_to_watch_next")
        or operator_explanation.get("what_to_watch")
        or "Wait for the next confirming condition.",
        "trigger_items": trigger_items,
        "risk_items": risk_items,
    }


def _build_historical_board(
    *,
    source_2_summary: dict[str, Any],
) -> dict[str, Any]:
    historical_context = _safe_dict(source_2_summary.get("historical_context"))
    event_history_panel = _safe_dict(historical_context.get("event_history_panel"))
    setup_history_panel = _safe_dict(historical_context.get("setup_history_panel"))
    history_panel = event_history_panel or setup_history_panel

    follow_through = history_panel.get("follow_through_rate_pct")
    failure = history_panel.get("failure_rate_pct")
    outcome_count = history_panel.get("outcome_count")
    stall_rate_pct = history_panel.get("stall_rate_pct")

    if stall_rate_pct is None:
        stall_count = history_panel.get("stall_count")
        if isinstance(outcome_count, (int, float)) and outcome_count:
            if isinstance(stall_count, (int, float)):
                stall_rate_pct = round((float(stall_count) / float(outcome_count)) * 100.0, 2)

    return {
        "state": historical_context.get("status") or "not_available",
        "setup_type": history_panel.get("setup_type"),
        "pattern_count": history_panel.get("pattern_count"),
        "outcome_count": outcome_count,
        "follow_through_rate_pct": follow_through,
        "failure_rate_pct": failure,
        "stall_rate_pct": stall_rate_pct,
        "historical_posture": history_panel.get("historical_posture"),
        "operator_summary": historical_context.get("operator_summary"),
        "symbol": history_panel.get("symbol"),
        "event_theme": history_panel.get("event_theme"),
    }


def _build_recent_memory_board(
    *,
    source_1_summary: dict[str, Any],
    external_memory_packet: dict[str, Any],
) -> dict[str, Any]:
    advisory_summary = _extract_recent_memory_summary(source_1_summary, external_memory_packet)
    return {
        "state": "ok" if advisory_summary else "not_available",
        "advisory_posture": external_memory_packet.get("advisory_posture") or advisory_summary.get("decision"),
        "promotion_score": advisory_summary.get("promotion_score"),
        "record_count": advisory_summary.get("record_count"),
        "coherence_flags": _safe_list(advisory_summary.get("coherence_flags")),
        "operator_summary": (
            f"Recent memory context is strong across {advisory_summary.get('record_count')} promoted recent records."
            if advisory_summary.get("record_count") is not None
            else "Recent memory context is not available."
        ),
    }


def _build_governance_board(
    *,
    normalized_result: dict[str, Any],
    watchlist_panel: dict[str, Any],
) -> dict[str, Any]:
    governance_panel = _extract_governance_panel(normalized_result)
    no_trade_state = _safe_dict(watchlist_panel.get("no_trade_state"))
    return {
        "state": "ok",
        "advisory_only": True,
        "approval_required": governance_panel.get("approval_required"),
        "execution_allowed": governance_panel.get("execution_allowed"),
        "route_path": governance_panel.get("route_path") or normalized_result.get("route_mode"),
        "posture_label": watchlist_panel.get("posture_label"),
        "no_trade": bool(no_trade_state.get("is_no_trade")),
        "no_trade_reason": no_trade_state.get("reason"),
    }


def _build_operator_packet(
    *,
    normalized_result: dict[str, Any],
    payload: dict[str, Any],
    source_1_summary: dict[str, Any],
    source_2_summary: dict[str, Any],
    external_memory_packet: dict[str, Any],
    labeled_outcomes_panel: dict[str, Any],
    market_panel: dict[str, Any],
) -> dict[str, Any]:
    live_event_panel = _extract_live_event_panel(normalized_result)
    governance_panel = _extract_governance_panel(normalized_result)
    runtime_panel = _extract_runtime_panel(normalized_result)
    recommendation_panel = _normalize_recommendation_panel(normalized_result)

    current_case_symbol = _derive_symbol(payload=payload, normalized_result=normalized_result)
    current_case_price_change_pct = _derive_price_change_pct(
        normalized_result=normalized_result,
        payload=payload,
        live_event_panel=live_event_panel,
    )
    current_case_confirmation = _derive_confirmation(
        normalized_result=normalized_result,
        payload=payload,
        live_event_panel=live_event_panel,
    )

    current_case = {
        "request_id": normalized_result.get("request_id") or payload.get("request_id"),
        "symbol": current_case_symbol,
        "headline": (
            runtime_panel.get("headline")
            or live_event_panel.get("headline")
            or payload.get("headline")
        ),
        "price_change_pct": current_case_price_change_pct,
        "confirmation": current_case_confirmation,
        "price_at_closeout": market_panel.get("price_at_closeout"),
        "reference_price": market_panel.get("reference_price"),
        "recommendation_panel": recommendation_panel,
        "governance_panel": governance_panel,
        "live_event_panel": live_event_panel,
    }

    return {
        "artifact_type": "market_analyzer_operator_packet",
        "status": "ok",
        "current_case": current_case,
        "historical_reference": source_2_summary,
        "recent_memory": source_1_summary,
        "external_memory_packet": external_memory_packet,
        "labeled_outcomes_panel": labeled_outcomes_panel,
        "market_panel": market_panel,
        "constraints": {
            "advisory_only": True,
            "execution_mutation_allowed": False,
            "governance_mutation_allowed": False,
            "recommendation_mutation_allowed": False,
        },
    }


def build_market_analyzer_operator_projection(
    *,
    normalized_result: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    normalized = _safe_dict(normalized_result)
    symbol = _derive_symbol(payload=payload, normalized_result=normalized)

    external_memory_projection = build_external_memory_projection(symbol)
    historical_projection = build_historical_context_projection(
        payload=payload,
        runtime_output=normalized,
    )

    source_1_summary = _safe_dict(external_memory_projection.get("source_1_summary"))
    external_memory_packet = _safe_dict(
        external_memory_projection.get("external_memory_packet")
    )
    source_2_summary = _safe_dict(historical_projection.get("source_2_summary"))

    labeled_outcomes_panel = _safe_dict(
        build_labeled_outcomes_projection(
            {
                "source_2_summary": source_2_summary,
            }
        )
    )

    market_panel = _build_market_panel(
        normalized_result=normalized,
        payload=payload,
    )

    operator_packet = _build_operator_packet(
        normalized_result=normalized,
        payload=payload,
        source_1_summary=source_1_summary,
        source_2_summary=source_2_summary,
        external_memory_packet=external_memory_packet,
        labeled_outcomes_panel=labeled_outcomes_panel,
        market_panel=market_panel,
    )

    watchlist_panel = _safe_dict(
        build_watchlist_projection(
            operator_packet=operator_packet,
        )
    )
    if watchlist_panel:
        operator_packet["watchlist_panel"] = watchlist_panel

    explanation_result = generate_operator_explanation(operator_packet)
    operator_explanation: dict[str, Any] = {}
    if isinstance(explanation_result, dict):
        if isinstance(explanation_result.get("operator_explanation"), dict):
            operator_explanation = _safe_dict(explanation_result.get("operator_explanation"))
        else:
            operator_explanation = _safe_dict(explanation_result)

    header_panel = _build_header_panel(normalized_result=normalized)
    historical_board = _build_historical_board(source_2_summary=source_2_summary)
    recent_memory_board = _build_recent_memory_board(
        source_1_summary=source_1_summary,
        external_memory_packet=external_memory_packet,
    )
    governance_board = _build_governance_board(
        normalized_result=normalized,
        watchlist_panel=watchlist_panel,
    )
    action_board = _build_action_board(watchlist_panel=watchlist_panel)
    watch_board = _build_watch_board(
        watchlist_panel=watchlist_panel,
        operator_explanation=operator_explanation,
    )
    commodity_board = _build_commodity_board(
        watchlist_panel=watchlist_panel,
        live_event_panel=_extract_live_event_panel(normalized),
    )
    indicator_panels = _build_indicator_panels(
        normalized_result=normalized,
        source_2_summary=source_2_summary,
        watchlist_panel=watchlist_panel,
        action_board=action_board,
        watch_board=watch_board,
    )

    enriched = deepcopy(normalized)
    enriched["dashboard_type"] = "market_analyzer_v1_market_board"
    enriched["board_version"] = "v1"
    enriched["board_generated_at"] = _utc_now_iso()
    enriched["board_status"] = "ok"
    enriched["source_1_summary"] = source_1_summary
    enriched["source_2_summary"] = source_2_summary
    enriched["external_memory_packet"] = external_memory_packet
    enriched["operator_packet"] = operator_packet
    enriched["current_case"] = _safe_dict(operator_packet.get("current_case"))
    enriched["labeled_outcomes_panel"] = labeled_outcomes_panel
    enriched["watchlist_panel"] = watchlist_panel
    enriched["operator_explanation"] = operator_explanation
    enriched["market_panel"] = market_panel
    enriched["recommendation_panel"] = _normalize_recommendation_panel(normalized)
    enriched["header_panel"] = header_panel
    enriched["indicator_panels"] = indicator_panels
    enriched["commodity_board"] = commodity_board
    enriched["action_board"] = action_board
    enriched["watch_board"] = watch_board
    enriched["historical_board"] = historical_board
    enriched["recent_memory_board"] = recent_memory_board
    enriched["governance_board"] = governance_board

    return enriched