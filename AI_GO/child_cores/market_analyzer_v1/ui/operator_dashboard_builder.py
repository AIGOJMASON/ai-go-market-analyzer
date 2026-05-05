from __future__ import annotations

from typing import Any, Dict, List


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _extract_primary_recommendation(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    recommendation_panel = _safe_dict(runtime_result.get("recommendation_panel"))
    items = _safe_list(recommendation_panel.get("items"))
    if items and isinstance(items[0], dict):
        return items[0]

    recommendations = _safe_list(recommendation_panel.get("recommendations"))
    if recommendations and isinstance(recommendations[0], dict):
        return recommendations[0]

    return {}


def _extract_symbol(runtime_result: Dict[str, Any]) -> Any:
    direct = _coalesce(runtime_result.get("symbol"))
    if direct is not None:
        return direct

    case_panel = _safe_dict(runtime_result.get("case_panel"))
    case_symbol = _coalesce(case_panel.get("symbol"))
    if case_symbol is not None:
        return case_symbol

    market_panel = _safe_dict(runtime_result.get("market_panel"))
    market_symbol = _coalesce(market_panel.get("symbol"))
    if market_symbol is not None:
        return market_symbol

    primary = _extract_primary_recommendation(runtime_result)
    rec_symbol = _coalesce(primary.get("symbol"))
    if rec_symbol is not None:
        return rec_symbol

    return None


def _extract_reference_price(runtime_result: Dict[str, Any]) -> Any:
    direct = _coalesce(
        runtime_result.get("reference_price"),
        runtime_result.get("price_at_closeout"),
        runtime_result.get("price"),
    )
    if direct is not None:
        return direct

    market_panel = _safe_dict(runtime_result.get("market_panel"))
    panel_price = _coalesce(
        market_panel.get("reference_price"),
        market_panel.get("price_at_closeout"),
        market_panel.get("price"),
    )
    if panel_price is not None:
        return panel_price

    primary = _extract_primary_recommendation(runtime_result)
    rec_price = _coalesce(primary.get("entry"))
    if rec_price is not None:
        return rec_price

    return None


def _build_case_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    existing = _safe_dict(runtime_result.get("case_panel"))

    case_id = _coalesce(
        existing.get("case_id"),
        runtime_result.get("case_id"),
        runtime_result.get("request_id"),
    )
    title = _coalesce(
        existing.get("title"),
        runtime_result.get("headline"),
        runtime_result.get("title"),
    )
    symbol = _coalesce(
        existing.get("symbol"),
        _extract_symbol(runtime_result),
    )
    observed_at = _coalesce(
        existing.get("observed_at"),
        runtime_result.get("observed_at"),
    )

    panel: Dict[str, Any] = {}
    if case_id:
        panel["case_id"] = case_id
    if title:
        panel["title"] = title
    if symbol:
        panel["symbol"] = symbol
    if observed_at:
        panel["observed_at"] = observed_at

    return panel


def _build_runtime_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    existing = _safe_dict(runtime_result.get("runtime_panel"))

    panel: Dict[str, Any] = {}

    for key in ["market_regime", "event_theme", "macro_bias", "headline"]:
        value = _coalesce(existing.get(key), runtime_result.get(key))
        if value is not None:
            panel[key] = value

    return panel


def _build_recommendation_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    existing = _safe_dict(runtime_result.get("recommendation_panel"))
    if existing:
        return existing

    primary = _extract_primary_recommendation(runtime_result)
    if not primary:
        return {}

    return {
        "state": "present",
        "count": 1,
        "items": [primary],
    }


def _build_market_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    existing = _safe_dict(runtime_result.get("market_panel"))

    panel: Dict[str, Any] = dict(existing)

    symbol = _extract_symbol(runtime_result)
    if symbol is not None and panel.get("symbol") is None:
        panel["symbol"] = symbol

    reference_price = _extract_reference_price(runtime_result)
    if reference_price is not None and panel.get("reference_price") is None:
        panel["reference_price"] = reference_price

    if reference_price is not None and panel.get("price_at_closeout") is None:
        panel["price_at_closeout"] = reference_price

    if panel.get("price") is None:
        price = _coalesce(runtime_result.get("price"))
        if price is not None:
            panel["price"] = price

    return panel


def build_operator_dashboard(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    runtime_result = _safe_dict(runtime_result)

    symbol = _extract_symbol(runtime_result)
    reference_price = _extract_reference_price(runtime_result)

    return {
        "request_id": runtime_result.get("request_id"),
        "core_id": runtime_result.get("core_id"),
        "route_mode": runtime_result.get("route_mode"),
        "mode": runtime_result.get("mode"),
        "symbol": symbol,
        "reference_price": reference_price,
        "case_panel": _build_case_panel(runtime_result),
        "runtime_panel": _build_runtime_panel(runtime_result),
        "recommendation_panel": _build_recommendation_panel(runtime_result),
        "market_panel": _build_market_panel(runtime_result),
        "execution_allowed": runtime_result.get("execution_allowed"),
        "approval_required": runtime_result.get("approval_required"),
    }