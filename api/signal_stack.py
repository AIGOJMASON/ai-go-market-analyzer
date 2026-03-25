from __future__ import annotations

from typing import Any, Dict, List

try:
    from api.live_ingress_policy import (
        LAWFUL_EVENT_SECTOR_PAIRS,
        NECESSITY_SECTORS,
        normalize_confirmation,
        normalize_sector,
    )
except ModuleNotFoundError:
    from AI_GO.api.live_ingress_policy import (
        LAWFUL_EVENT_SECTOR_PAIRS,
        NECESSITY_SECTORS,
        normalize_confirmation,
        normalize_sector,
    )


class SignalStackError(ValueError):
    pass


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def _price_direction_signal(price_change_pct: float) -> str:
    if price_change_pct > 0:
        return "price:positive"
    if price_change_pct < 0:
        return "price:negative"
    return "price:flat"


def _price_magnitude_signal(price_change_pct: float) -> str:
    absolute = abs(price_change_pct)
    if absolute >= 3.0:
        return "price_magnitude:high"
    if absolute >= 1.0:
        return "price_magnitude:medium"
    return "price_magnitude:low"


def _confirmation_signal(confirmation: str) -> str:
    return f"confirmation:{confirmation}"


def _legality_signal(event_theme: str, sector: str) -> str:
    if sector in NECESSITY_SECTORS:
        return "legality:necessity"
    if (event_theme, sector) in LAWFUL_EVENT_SECTOR_PAIRS:
        return "legality:lawful_exception"
    return "legality:restricted"


def _stack_summary(
    *,
    signal_count: int,
    price_change_pct: float,
    confirmation: str,
    event_theme: str,
    sector: str,
) -> Dict[str, Any]:
    legality_state = _legality_signal(event_theme, sector).split(":", 1)[1]
    price_direction = _price_direction_signal(price_change_pct).split(":", 1)[1]

    return {
        "price_direction": price_direction,
        "confirmation_state": confirmation,
        "legality_state": legality_state,
        "signal_count": signal_count,
    }


def build_signal_stack(
    *,
    request_id: str,
    symbol: str,
    headline: str,
    price_change_pct: float,
    sector: str,
    confirmation: str,
    classification: Dict[str, Any],
) -> Dict[str, Any]:
    request_id = _clean_text(request_id)
    symbol = _clean_text(symbol).upper()
    headline = _clean_text(headline)
    sector = normalize_sector(sector)
    confirmation = normalize_confirmation(confirmation)

    if not request_id:
        raise SignalStackError("request_id is required")
    if not symbol:
        raise SignalStackError("symbol is required")
    if not headline:
        raise SignalStackError("headline is required")
    if not isinstance(price_change_pct, (int, float)):
        raise SignalStackError("price_change_pct must be numeric")
    if not isinstance(classification, dict):
        raise SignalStackError("classification must be a dict")

    event_theme = _clean_text(classification.get("event_theme")) or "unknown"
    classification_confidence = _clean_text(classification.get("classification_confidence")) or "low"
    classifier_signals = classification.get("signals")
    if not isinstance(classifier_signals, list):
        raise SignalStackError("classification signals must be a list")

    upstream_signals: List[str] = []
    for signal in classifier_signals:
        clean = _clean_text(signal)
        if clean:
            upstream_signals.append(clean)

    derived_signals = [
        _confirmation_signal(confirmation),
        _price_direction_signal(float(price_change_pct)),
        _price_magnitude_signal(float(price_change_pct)),
        _legality_signal(event_theme, sector),
        f"symbol:{symbol}",
        f"sector:{sector}",
    ]

    stack_signals: List[str] = []
    seen = set()

    for signal in upstream_signals + derived_signals:
        if signal not in seen:
            stack_signals.append(signal)
            seen.add(signal)

    return {
        "artifact_type": "signal_stack_record",
        "request_id": request_id,
        "event_theme": event_theme,
        "classification_confidence": classification_confidence,
        "stack_signals": stack_signals,
        "stack_summary": _stack_summary(
            signal_count=len(stack_signals),
            price_change_pct=float(price_change_pct),
            confirmation=confirmation,
            event_theme=event_theme,
            sector=sector,
        ),
        "bounded": True,
        "sealed": True,
    }