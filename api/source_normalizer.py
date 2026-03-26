from typing import Optional

from AI_GO.api.source_ingress_schema import SourceIngressRequest, SourceSignalRecord
from AI_GO.api.source_registry import resolve_trust_class


ENERGY_KEYWORDS = {
    "energy",
    "oil",
    "gas",
    "refinery",
    "crude",
    "pipeline",
    "drilling",
    "opec",
}

SPECULATIVE_KEYWORDS = {
    "meme",
    "speculative",
    "rumor",
    "chatter",
    "hype",
    "viral",
}

MATERIALS_KEYWORDS = {
    "copper",
    "steel",
    "lithium",
    "mine",
    "mining",
    "materials",
}

MACRO_RISK_KEYWORDS = {
    "inflation",
    "rate",
    "rates",
    "war",
    "sanction",
    "tariff",
    "macro",
    "geopolitical",
}


def _detect_event_theme(text: str, sector_hint: str) -> str:
    lowered = text.lower()

    if any(word in lowered for word in SPECULATIVE_KEYWORDS):
        return "speculative_move"

    if any(word in lowered for word in ENERGY_KEYWORDS) and (
        "rebound" in lowered or "necessity" in lowered or "shock" in lowered
    ):
        return "energy_rebound"

    if any(word in lowered for word in MATERIALS_KEYWORDS) and (
        "open" in lowered or "expansion" in lowered or "supply" in lowered
    ):
        return "supply_expansion"

    if any(word in lowered for word in MACRO_RISK_KEYWORDS):
        return "macro_risk"

    if sector_hint == "energy":
        return "energy_signal"

    if sector_hint == "materials":
        return "materials_signal"

    return "general_signal"


def _detect_propagation(
    event_theme: str,
    confirmation_hint: str,
    price_change_pct: Optional[float],
) -> str:
    if confirmation_hint == "missing":
        return "blocked"

    if event_theme in {"energy_rebound", "supply_expansion"} and confirmation_hint in {
        "confirmed",
        "partial",
    }:
        return "supportive"

    if event_theme == "macro_risk":
        return "mixed"

    if price_change_pct is not None and abs(price_change_pct) >= 4.0:
        return "volatile"

    return "neutral"


def _detect_severity(
    event_theme: str,
    confirmation_hint: str,
    price_change_pct: Optional[float],
) -> str:
    if confirmation_hint == "missing":
        return "low"

    if event_theme in {"energy_rebound", "supply_expansion"} and confirmation_hint == "confirmed":
        return "high"

    if price_change_pct is not None and abs(price_change_pct) >= 3.0:
        return "medium"

    return "low"


def normalize_source_item(request: SourceIngressRequest) -> SourceSignalRecord:
    joined_text = f"{request.headline} {request.body}".strip()
    event_theme = _detect_event_theme(joined_text, request.sector_hint)
    propagation = _detect_propagation(
        event_theme=event_theme,
        confirmation_hint=request.confirmation_hint,
        price_change_pct=request.price_change_pct,
    )
    severity = _detect_severity(
        event_theme=event_theme,
        confirmation_hint=request.confirmation_hint,
        price_change_pct=request.price_change_pct,
    )

    return SourceSignalRecord(
        request_id=request.request_id,
        source_item_id=request.source_item_id,
        source_type=request.source_type,
        trust_class=resolve_trust_class(request.source_type),
        headline=request.headline,
        body=request.body,
        normalized_symbol=request.symbol_hint,
        normalized_sector=request.sector_hint,
        normalized_confirmation=request.confirmation_hint,
        event_theme=event_theme,
        propagation=propagation,
        price_change_pct=request.price_change_pct,
        severity=severity,
        source_name=request.source_name,
        source_url=request.source_url,
        occurred_at=request.occurred_at,
        tags=request.tags,
    )