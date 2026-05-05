from __future__ import annotations

from typing import Any


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _clean_upper(value: Any) -> str:
    return _clean_str(value).upper()


def _extract_symbol(payload: dict[str, Any]) -> str:
    direct = _clean_upper(payload.get("symbol"))
    if direct:
        return direct

    market_panel = _safe_dict(payload.get("market_panel"))
    market_symbol = _clean_upper(market_panel.get("symbol"))
    if market_symbol:
        return market_symbol

    case_panel = _safe_dict(payload.get("case_panel"))
    case_symbol = _clean_upper(case_panel.get("symbol"))
    if case_symbol:
        return case_symbol

    operator_packet = _safe_dict(payload.get("operator_packet"))
    current_case = _safe_dict(operator_packet.get("current_case"))
    current_case_symbol = _clean_upper(current_case.get("symbol"))
    if current_case_symbol:
        return current_case_symbol

    recommendation_panel = _safe_dict(payload.get("recommendation_panel"))
    items = _safe_list(recommendation_panel.get("items"))
    if items and isinstance(items[0], dict):
        rec_symbol = _clean_upper(items[0].get("symbol"))
        if rec_symbol:
            return rec_symbol

    watchlist_panel = _safe_dict(payload.get("watchlist_panel"))
    source_symbol = _clean_upper(watchlist_panel.get("source_symbol"))
    if source_symbol:
        return source_symbol

    return ""


def _extract_reference_price(payload: dict[str, Any]) -> float | None:
    market_panel = _safe_dict(payload.get("market_panel"))

    for field in ("reference_price", "price_at_closeout", "price"):
        value = _safe_float(market_panel.get(field))
        if value is not None:
            return value

    for field in ("reference_price", "price_at_closeout", "price"):
        value = _safe_float(payload.get(field))
        if value is not None:
            return value

    operator_packet = _safe_dict(payload.get("operator_packet"))
    current_case = _safe_dict(operator_packet.get("current_case"))
    for field in ("reference_price", "price_at_closeout", "price"):
        value = _safe_float(current_case.get(field))
        if value is not None:
            return value

    recommendation_panel = _safe_dict(payload.get("recommendation_panel"))
    items = _safe_list(recommendation_panel.get("items"))
    if items and isinstance(items[0], dict):
        for field in ("entry", "reference_price", "price_at_closeout", "price"):
            value = _safe_float(items[0].get(field))
            if value is not None:
                return value

    return None


def _extract_event_theme(payload: dict[str, Any]) -> str:
    direct = _clean_str(payload.get("event_theme"))
    if direct:
        return direct

    runtime_panel = _safe_dict(payload.get("runtime_panel"))
    runtime_theme = _clean_str(runtime_panel.get("event_theme"))
    if runtime_theme:
        return runtime_theme

    market_panel = _safe_dict(payload.get("market_panel"))
    market_theme = _clean_str(market_panel.get("event_theme"))
    if market_theme:
        return market_theme

    return ""


def _extract_expected_behavior(payload: dict[str, Any], event_theme: str) -> str:
    direct = _clean_str(payload.get("expected_behavior"))
    if direct:
        return direct

    outcome_expectation = _clean_str(payload.get("outcome_expectation"))
    if outcome_expectation:
        return outcome_expectation

    derived_expected_behavior = _clean_str(payload.get("derived_expected_behavior"))
    if derived_expected_behavior:
        return derived_expected_behavior

    if event_theme:
        return event_theme.replace("_", " ")

    return ""


def _derive_direction(event_theme: str, expected_behavior: str) -> str:
    normalized_theme = _clean_str(event_theme).lower()
    normalized_behavior = _clean_str(expected_behavior).lower()

    bullish_tokens = ("rebound", "rally", "breakout", "bullish", "surge", "recovery", "momentum")
    bearish_tokens = ("decline", "selloff", "breakdown", "bearish", "collapse", "drop", "failure", "fade")

    if any(token in normalized_theme for token in bullish_tokens):
        return "up"
    if any(token in normalized_behavior for token in bullish_tokens):
        return "up"

    if any(token in normalized_theme for token in bearish_tokens):
        return "down"
    if any(token in normalized_behavior for token in bearish_tokens):
        return "down"

    return "unknown"


def _extract_confidence(payload: dict[str, Any]) -> float:
    watchlist_panel = _safe_dict(payload.get("watchlist_panel"))
    model = _safe_dict(watchlist_panel.get("model"))
    confidence = _safe_float(model.get("confidence"))
    if confidence is not None:
        return confidence

    return 0.5


def build_outcome_candidate(payload: dict[str, Any]) -> dict[str, Any]:
    symbol = _extract_symbol(payload)
    reference_price = _extract_reference_price(payload)
    event_theme = _extract_event_theme(payload)
    expected_behavior = _extract_expected_behavior(payload, event_theme)
    direction = _derive_direction(event_theme, expected_behavior)
    confidence = _extract_confidence(payload)

    return {
        "artifact_type": "market_outcome_candidate",
        "artifact_version": "v1",
        "generated_at": _clean_str(payload.get("board_generated_at") or payload.get("generated_at")),
        "request_id": _clean_str(payload.get("request_id")),
        "symbol": symbol,
        "reference_price": reference_price,
        "event_theme": event_theme,
        "expected_behavior": expected_behavior,
        "direction": direction,
        "confidence": confidence,
        "evaluation_window": "short_term",
        "advisory_only": bool(payload.get("advisory_only", True)),
        "approval_required": bool(payload.get("approval_required", True)),
        "execution_allowed": bool(payload.get("execution_allowed", False)),
        "lineage": {
            "source_request_id": _clean_str(payload.get("request_id")),
            "source_closeout_id": _clean_str(payload.get("closeout_id")),
            "source_receipt_id": _clean_str(payload.get("receipt_id")),
            "source_artifact_type": "market_analyzer_runtime_payload",
        },
    }


def build_outcome_candidate_result(payload: dict[str, Any]) -> dict[str, Any]:
    candidate = build_outcome_candidate(payload)

    missing_fields: list[str] = []

    if not candidate.get("symbol"):
        missing_fields.append("symbol")

    if candidate.get("reference_price") is None:
        missing_fields.append("reference_price")

    if not candidate.get("event_theme"):
        missing_fields.append("event_theme")

    if not candidate.get("expected_behavior"):
        missing_fields.append("expected_behavior")

    if not candidate.get("direction"):
        missing_fields.append("direction")

    is_minimally_evaluable = len(missing_fields) == 0

    return {
        "status": "ok" if is_minimally_evaluable else "incomplete",
        "candidate": candidate,
        "is_minimally_evaluable": is_minimally_evaluable,
        "missing_fields": missing_fields,
    }