from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from AI_GO.child_cores.market_analyzer_v1.refinement.historical_context_bridge import (
        MarketAnalyzerHistoricalContextBridge,
    )
    from AI_GO.historical_market.storage.db_paths import HistoricalMarketPaths
    from AI_GO.historical_market.retrieval.historical_query_runtime import (
        HistoricalQueryRuntime,
    )
    from AI_GO.historical_market.labeled_outcomes.labeled_outcomes_store import (
        load_labeled_outcomes_for_event_theme,
        load_labeled_outcomes_for_symbol,
    )
except ImportError:
    from child_cores.market_analyzer_v1.refinement.historical_context_bridge import (
        MarketAnalyzerHistoricalContextBridge,
    )
    from historical_market.storage.db_paths import HistoricalMarketPaths
    from historical_market.retrieval.historical_query_runtime import (
        HistoricalQueryRuntime,
    )
    from historical_market.labeled_outcomes.labeled_outcomes_store import (
        load_labeled_outcomes_for_event_theme,
        load_labeled_outcomes_for_symbol,
    )


_historical_context_bridge = MarketAnalyzerHistoricalContextBridge()
_historical_paths = HistoricalMarketPaths()
_historical_query_runtime = HistoricalQueryRuntime(paths=_historical_paths)


def _safe_upper(value: Any) -> str:
    return str(value or "").strip().upper()


def _safe_lower(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip().lower()
    return text or fallback


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _extract_live_event_panel(
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
) -> Mapping[str, Any]:
    payload_live_event = _as_mapping(payload.get("live_event_panel"))
    if payload_live_event:
        return payload_live_event
    return _as_mapping(runtime_output.get("live_event_panel"))


def _extract_recommendation_symbol(
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
) -> str:
    for source in (payload, runtime_output):
        recommendation_panel = _as_mapping(source.get("recommendation_panel"))
        items = recommendation_panel.get("items")
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, Mapping):
                continue
            symbol = _safe_upper(item.get("symbol"))
            if symbol:
                return symbol
    return ""


def _resolve_symbol(
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
) -> str:
    live_event_panel = _extract_live_event_panel(payload, runtime_output)

    candidates = [
        payload.get("symbol"),
        runtime_output.get("symbol"),
        live_event_panel.get("symbol"),
        _extract_recommendation_symbol(payload, runtime_output),
        _as_mapping(runtime_output.get("market_panel")).get("symbol"),
        _as_mapping(runtime_output.get("case_panel")).get("symbol"),
        _as_mapping(runtime_output.get("current_case")).get("symbol"),
    ]

    for candidate in candidates:
        symbol = _safe_upper(candidate)
        if symbol:
            return symbol

    return ""


def _resolve_sector(
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
) -> str:
    live_event_panel = _extract_live_event_panel(payload, runtime_output)

    candidates = [
        payload.get("sector"),
        runtime_output.get("sector"),
        live_event_panel.get("sector"),
        _as_mapping(runtime_output.get("market_panel")).get("sector"),
        _as_mapping(runtime_output.get("current_case")).get("sector"),
    ]

    for candidate in candidates:
        sector = _safe_lower(candidate)
        if sector:
            return sector

    return ""


def _resolve_event_theme(
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
) -> str:
    live_event_panel = _extract_live_event_panel(payload, runtime_output)
    runtime_panel = _as_mapping(runtime_output.get("runtime_panel"))
    market_panel = _as_mapping(runtime_output.get("market_panel"))
    current_case = _as_mapping(runtime_output.get("current_case"))

    candidates = [
        payload.get("event_theme"),
        runtime_output.get("event_theme"),
        runtime_panel.get("event_theme"),
        market_panel.get("event_theme"),
        current_case.get("event_theme"),
        live_event_panel.get("event_theme"),
    ]

    for candidate in candidates:
        event_theme = _safe_lower(candidate)
        if event_theme:
            return event_theme

    return ""


def _infer_asset_class(payload: Mapping[str, Any], runtime_output: Mapping[str, Any]) -> str:
    live_event_panel = _extract_live_event_panel(payload, runtime_output)
    if live_event_panel:
        source_type = str(live_event_panel.get("source_type") or "").strip().lower()
        if source_type in {"live_feed", "market_quote", "quote"}:
            return "etf"

    symbol = _resolve_symbol(payload, runtime_output)
    if symbol in {
        "XLE", "SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLI", "XLP",
        "XLU", "XLB", "XLY", "XLC", "XLV", "XBI",
    }:
        return "etf"
    if symbol in {"CL", "GC", "SI", "NG", "HG"}:
        return "commodity"

    return "etf"


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                rows.append(parsed)
    return rows


def _iter_symbol_month_files(*, symbol: str, asset_class: str) -> List[Path]:
    if not symbol or not asset_class:
        return []

    root = _historical_paths.raw_bars_dir / asset_class.lower() / symbol.upper()
    if not root.exists():
        return []

    month_files: List[Path] = []
    for year_dir in sorted(root.iterdir(), reverse=True):
        if not year_dir.is_dir():
            continue
        for month_file in sorted(year_dir.glob("*.jsonl"), reverse=True):
            month_files.append(month_file)

    return month_files


def _read_recent_raw_bars(
    *,
    symbol: str,
    asset_class: str,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    if not symbol or not asset_class:
        return []

    collected: List[Dict[str, Any]] = []

    for month_file in _iter_symbol_month_files(symbol=symbol, asset_class=asset_class):
        rows = _read_jsonl(month_file)
        for row in reversed(rows):
            if _safe_upper(row.get("symbol")) != symbol.upper():
                continue
            if _safe_lower(row.get("asset_class")) != asset_class.lower():
                continue
            collected.append(row)
            if len(collected) >= limit:
                return list(reversed(collected))

    return list(reversed(collected))


def _build_recent_bars_from_store(
    *,
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
    limit: int = 5,
) -> List[Dict[str, Any]]:
    symbol = _resolve_symbol(payload, runtime_output)
    asset_class = _infer_asset_class(payload, runtime_output)
    return _read_recent_raw_bars(symbol=symbol, asset_class=asset_class, limit=limit)


def _build_relationship_bars_from_store(
    *,
    symbol: str,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[List[Dict[str, Any]]]]:
    symbol = _safe_upper(symbol)
    if not symbol:
        return None, None

    leader_asset_class = "etf"
    follower_symbol: Optional[str] = None
    follower_asset_class: Optional[str] = None

    if symbol == "XLE":
        follower_symbol = "CL"
        follower_asset_class = "commodity"

    if follower_symbol is None or follower_asset_class is None:
        return None, None

    leader_bars = _read_recent_raw_bars(
        symbol=symbol,
        asset_class=leader_asset_class,
        limit=7,
    )
    follower_bars = _read_recent_raw_bars(
        symbol=follower_symbol,
        asset_class=follower_asset_class,
        limit=7,
    )

    if not leader_bars or not follower_bars:
        return None, None

    return leader_bars, follower_bars


def _runtime_reference(
    *,
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
) -> Dict[str, Any]:
    request_id = str(payload.get("request_id") or runtime_output.get("request_id") or "")
    return {
        "request_id": request_id,
        "core_id": str(runtime_output.get("core_id") or "market_analyzer_v1"),
        "route_mode": str(runtime_output.get("route_mode") or "pm_route"),
        "mode": str(runtime_output.get("mode") or "advisory"),
        "headline": str(
            payload.get("headline")
            or runtime_output.get("headline")
            or _extract_live_event_panel(payload, runtime_output).get("headline")
            or ""
        ),
        "recommendation_panel_state": str(
            (_as_mapping(runtime_output.get("recommendation_panel"))).get("state") or ""
        ),
        "recommendation_panel_count": int(
            (_as_mapping(runtime_output.get("recommendation_panel"))).get("count") or 0
        ),
    }


def _base_constraints() -> Dict[str, Any]:
    return {
        "annotation_only": True,
        "recommendation_mutation_allowed": False,
        "governance_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "attach_to_runtime_output": False,
    }


def _build_unavailable_summary(
    *,
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
    reason: str,
) -> Dict[str, Any]:
    request_id = str(payload.get("request_id") or runtime_output.get("request_id") or "")
    return {
        "source_2_summary": {
            "artifact_type": "market_analyzer_historical_context_summary",
            "status": "unavailable",
            "request_id": request_id,
            "reason": reason,
            "historical_context": {
                "status": "unavailable",
                "operator_summary": "Historical comparison is unavailable because no real stored historical bars or labeled outcomes were found for this case.",
            },
            "constraints": _base_constraints(),
        }
    }


def _summarize_labeled_outcomes(
    *,
    symbol: str,
    event_theme: str,
) -> Optional[Dict[str, Any]]:
    symbol_rows = load_labeled_outcomes_for_symbol(symbol) if symbol else []
    theme_rows = load_labeled_outcomes_for_event_theme(event_theme) if event_theme else []

    rows: List[Dict[str, Any]] = []
    seen_ids = set()

    # Prefer exact symbol+theme matches first, then symbol-only, then theme-only.
    prioritized = []

    if symbol and event_theme:
        prioritized.extend(
            [
                row
                for row in symbol_rows
                if _safe_lower(row.get("event_theme")) == event_theme
            ]
        )

    prioritized.extend(symbol_rows)
    prioritized.extend(theme_rows)

    for row in prioritized:
        record_id = str(row.get("record_id") or "")
        if not record_id or record_id in seen_ids:
            continue
        seen_ids.add(record_id)
        rows.append(row)

    if not rows:
        return None

    follow_through = 0
    failure = 0
    stall = 0

    for row in rows:
        outcome_class = _safe_lower(row.get("outcome_class"))
        if outcome_class == "follow_through":
            follow_through += 1
        elif outcome_class == "failure":
            failure += 1
        elif outcome_class == "stall":
            stall += 1

    outcome_count = len(rows)
    follow_rate = round((follow_through / outcome_count) * 100.0, 2) if outcome_count else 0.0
    failure_rate = round((failure / outcome_count) * 100.0, 2) if outcome_count else 0.0
    stall_rate = round((stall / outcome_count) * 100.0, 2) if outcome_count else 0.0

    if follow_rate > failure_rate:
        posture = "historically constructive"
    elif failure_rate > follow_rate:
        posture = "historically fragile"
    else:
        posture = "historically mixed"

    summary_symbol = _safe_upper(rows[0].get("symbol")) or symbol
    summary_theme = _safe_lower(rows[0].get("event_theme")) or event_theme

    operator_summary = (
        f"{summary_symbol or 'This symbol'} has {outcome_count} labeled outcomes for "
        f"{summary_theme or 'this theme'}: follow-through {follow_rate:.2f}% vs "
        f"failure {failure_rate:.2f}% with historical posture {posture}."
    )

    return {
        "symbol": summary_symbol,
        "event_theme": summary_theme,
        "outcome_count": outcome_count,
        "outcome_counts": {
            "follow_through": follow_through,
            "failure": failure,
            "stall": stall,
        },
        "follow_through_rate_pct": follow_rate,
        "failure_rate_pct": failure_rate,
        "stall_rate_pct": stall_rate,
        "historical_posture": posture,
        "operator_summary": operator_summary,
        "records": rows,
    }


def _build_labeled_outcomes_fallback_summary(
    *,
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
) -> Optional[Dict[str, Any]]:
    request_id = str(payload.get("request_id") or runtime_output.get("request_id") or "")
    symbol = _resolve_symbol(payload, runtime_output)
    event_theme = _resolve_event_theme(payload, runtime_output)

    summary = _summarize_labeled_outcomes(symbol=symbol, event_theme=event_theme)
    if not summary:
        return None

    return {
        "source_2_summary": {
            "artifact_type": "market_analyzer_historical_context_summary",
            "status": "ok",
            "request_id": request_id,
            "setup_detection": {
                "detected": False,
                "setup_type": None,
                "confidence": 0.0,
                "window_start": None,
                "window_end": None,
                "supporting_features": {
                    "reason": "no_supported_setup_detected_labeled_outcomes_fallback_used"
                },
            },
            "historical_context": {
                "status": "ok",
                "setup_history_panel": None,
                "event_package_panel": None,
                "relationship_panel": None,
                "event_history_panel": {
                    "panel_type": "event_history",
                    "symbol": summary["symbol"],
                    "event_theme": summary["event_theme"],
                    "event_count": summary["outcome_count"],
                    "outcome_count": summary["outcome_count"],
                    "outcome_counts": summary["outcome_counts"],
                    "follow_through_rate_pct": summary["follow_through_rate_pct"],
                    "failure_rate_pct": summary["failure_rate_pct"],
                    "stall_rate_pct": summary["stall_rate_pct"],
                    "historical_posture": summary["historical_posture"],
                    "operator_summary": summary["operator_summary"],
                    "source": "labeled_outcomes_store",
                },
                "operator_summary": summary["operator_summary"],
            },
            "runtime_reference": _runtime_reference(payload=payload, runtime_output=runtime_output),
            "constraints": _base_constraints(),
        }
    }


def _build_event_context_fallback_summary(
    *,
    payload: Mapping[str, Any],
    runtime_output: Mapping[str, Any],
) -> Dict[str, Any]:
    request_id = str(payload.get("request_id") or runtime_output.get("request_id") or "")
    symbol = _resolve_symbol(payload, runtime_output)
    sector = _resolve_sector(payload, runtime_output)

    event_summary = _historical_query_runtime.summarize_event_context(
        symbol=symbol or None,
        sector=sector or None,
        signal_seed=None,
    )

    outcome_count = int(event_summary.get("outcome_count", 0) or 0)
    posture = event_summary.get("historical_posture", "not_available")
    operator_summary = event_summary.get(
        "operator_summary",
        f"No event-linked historical outcomes are available yet for {symbol or 'this symbol'}.",
    )

    return {
        "source_2_summary": {
            "artifact_type": "market_analyzer_historical_context_summary",
            "status": "ok",
            "request_id": request_id,
            "setup_detection": {
                "detected": False,
                "setup_type": None,
                "confidence": 0.0,
                "window_start": None,
                "window_end": None,
                "supporting_features": {
                    "reason": "no_supported_setup_detected_event_context_fallback_used"
                },
            },
            "historical_context": {
                "status": "ok" if outcome_count > 0 else "not_available",
                "setup_history_panel": None,
                "event_package_panel": None,
                "relationship_panel": None,
                "event_history_panel": {
                    "panel_type": "event_history",
                    "symbol": event_summary.get("symbol"),
                    "sector": event_summary.get("sector"),
                    "signal_seed": event_summary.get("signal_seed"),
                    "event_count": event_summary.get("event_count", 0),
                    "outcome_count": outcome_count,
                    "outcome_counts": event_summary.get("outcome_counts", {}),
                    "follow_through_rate_pct": event_summary.get("follow_through_rate_pct", 0.0),
                    "failure_rate_pct": event_summary.get("failure_rate_pct", 0.0),
                    "historical_posture": posture,
                    "operator_summary": operator_summary,
                    "source": "historical_query_runtime",
                },
                "operator_summary": operator_summary,
            },
            "runtime_reference": _runtime_reference(payload=payload, runtime_output=runtime_output),
            "constraints": _base_constraints(),
        }
    }


def build_historical_context_projection(
    *,
    payload: dict[str, Any],
    runtime_output: dict[str, Any],
) -> Dict[str, Any]:
    try:
        symbol = _resolve_symbol(payload, runtime_output)

        recent_bars = _build_recent_bars_from_store(
            payload=payload,
            runtime_output=runtime_output,
            limit=5,
        )

        # If no recent bars exist, try labeled outcomes before declaring the case unavailable.
        if not recent_bars:
            labeled_fallback = _build_labeled_outcomes_fallback_summary(
                payload=payload,
                runtime_output=runtime_output,
            )
            if labeled_fallback:
                return labeled_fallback

            return _build_unavailable_summary(
                payload=payload,
                runtime_output=runtime_output,
                reason="no_real_historical_bars_found",
            )

        leader_bars, follower_bars = _build_relationship_bars_from_store(symbol=symbol)

        bridge_result = _historical_context_bridge.build_historical_context_summary(
            request_id=str(payload.get("request_id") or runtime_output.get("request_id") or ""),
            runtime_output=runtime_output,
            recent_bars=recent_bars,
            event_id=None,
            leader_bars=leader_bars,
            follower_bars=follower_bars,
            max_lag_bars=2,
            min_overlap_points=4,
        )

        summary = getattr(bridge_result, "historical_context_summary", {})
        if not isinstance(summary, dict):
            labeled_fallback = _build_labeled_outcomes_fallback_summary(
                payload=payload,
                runtime_output=runtime_output,
            )
            if labeled_fallback:
                return labeled_fallback

            return _build_unavailable_summary(
                payload=payload,
                runtime_output=runtime_output,
                reason="historical_bridge_returned_invalid_summary",
            )

        historical_context = summary.get("historical_context") or {}
        setup_detection = summary.get("setup_detection") or {}

        no_supported_setup = (
            isinstance(setup_detection, dict)
            and not bool(setup_detection.get("detected", False))
            and isinstance(historical_context, dict)
            and str(historical_context.get("status") or "").strip().lower() in {"not_available", "unavailable"}
        )

        if no_supported_setup:
            labeled_fallback = _build_labeled_outcomes_fallback_summary(
                payload=payload,
                runtime_output=runtime_output,
            )
            if labeled_fallback:
                return labeled_fallback

            return _build_event_context_fallback_summary(
                payload=payload,
                runtime_output=runtime_output,
            )

        return {"source_2_summary": summary}
    except Exception:
        traceback.print_exc()

        labeled_fallback = _build_labeled_outcomes_fallback_summary(
            payload=payload,
            runtime_output=runtime_output,
        )
        if labeled_fallback:
            return labeled_fallback

        return _build_unavailable_summary(
            payload=payload,
            runtime_output=runtime_output,
            reason="historical_context_projection_exception",
        )