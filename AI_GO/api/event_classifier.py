from __future__ import annotations

from typing import Any, Dict, List

try:
    from api.live_ingress_policy import (
        APPROVED_EVENT_THEMES,
        LAWFUL_EVENT_SECTOR_PAIRS,
        NECESSITY_SECTORS,
        normalize_confirmation,
        normalize_sector,
    )
except ModuleNotFoundError:
    from AI_GO.api.live_ingress_policy import (
        APPROVED_EVENT_THEMES,
        LAWFUL_EVENT_SECTOR_PAIRS,
        NECESSITY_SECTORS,
        normalize_confirmation,
        normalize_sector,
    )


class EventClassifierError(ValueError):
    pass


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def _ensure_event_theme(value: str) -> str:
    if value not in APPROVED_EVENT_THEMES:
        return "unknown"
    return value


def _is_lawful_exception_context(event_theme: str, sector: str) -> bool:
    return (event_theme, sector) in LAWFUL_EVENT_SECTOR_PAIRS


def classify_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise EventClassifierError("classifier payload must be a dict")

    request_id = _clean_text(payload.get("request_id"))
    symbol = _clean_text(payload.get("symbol")).upper()
    headline = _clean_text(payload.get("headline"))
    price_change_pct = payload.get("price_change_pct")
    sector = normalize_sector(payload.get("sector"))
    confirmation = normalize_confirmation(payload.get("confirmation"))

    if not request_id:
        raise EventClassifierError("request_id is required")
    if not symbol:
        raise EventClassifierError("symbol is required")
    if not headline:
        raise EventClassifierError("headline is required")
    if not isinstance(price_change_pct, (int, float)):
        raise EventClassifierError("price_change_pct must be numeric")

    text = headline.lower()
    signals: List[str] = []

    if confirmation == "none":
        signals.append("confirmation:none")
        return {
            "artifact_type": "event_classification",
            "request_id": request_id,
            "event_theme": "confirmation_failure",
            "classification_confidence": "high",
            "signals": signals,
            "bounded": True,
            "sealed": True,
        }

    if "chile" in text:
        signals.append("keyword:chile")
    if "copper" in text:
        signals.append("keyword:copper")
    if "mine" in text:
        signals.append("keyword:mine")
    if "supply" in text:
        signals.append("keyword:supply")
    if "war" in text:
        signals.append("keyword:war")
    if "sanction" in text:
        signals.append("keyword:sanction")
    if "missile" in text:
        signals.append("keyword:missile")
    if "conflict" in text:
        signals.append("keyword:conflict")
    if sector == "energy":
        signals.append("sector:energy")
    if float(price_change_pct) > 0:
        signals.append("price:positive")

    event_theme = "unknown"
    classification_confidence = "low"

    if any(sig in signals for sig in ("keyword:chile", "keyword:copper", "keyword:mine", "keyword:supply")):
        event_theme = "supply_expansion"
        classification_confidence = "high" if len(signals) >= 2 else "medium"
    elif any(sig in signals for sig in ("keyword:war", "keyword:sanction", "keyword:missile", "keyword:conflict")):
        event_theme = "geopolitical_shock"
        classification_confidence = "high"
    elif sector == "energy" and float(price_change_pct) > 0:
        event_theme = "energy_rebound"
        classification_confidence = "medium"
    elif sector not in NECESSITY_SECTORS:
        event_theme = "speculative_move"
        classification_confidence = "medium"

    event_theme = _ensure_event_theme(event_theme)

    lawful_exception = _is_lawful_exception_context(event_theme, sector)

    if sector not in NECESSITY_SECTORS and not lawful_exception:
        signals.append("sector:non_necessity")
    elif lawful_exception:
        signals.append("sector:lawful_exception")

    return {
        "artifact_type": "event_classification",
        "request_id": request_id,
        "event_theme": event_theme,
        "classification_confidence": classification_confidence,
        "signals": signals,
        "bounded": True,
        "sealed": True,
    }