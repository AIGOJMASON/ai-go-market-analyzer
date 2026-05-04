from __future__ import annotations

try:
    from AI_GO.api.market_outcome_schema import ALLOWED_MARKET_OUTCOME_SOURCES
except ImportError:
    from api.market_outcome_schema import ALLOWED_MARKET_OUTCOME_SOURCES


def _safe_float(value) -> float | None:
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


def extract_closeout_symbol(closeout_artifact: dict) -> str:
    direct_symbol = str(closeout_artifact.get("symbol", "")).strip()
    if direct_symbol:
        return direct_symbol

    case_panel = closeout_artifact.get("case_panel", {})
    case_symbol = str(case_panel.get("symbol", "")).strip()
    if case_symbol:
        return case_symbol

    recommendation_panel = closeout_artifact.get("recommendation_panel", {})
    items = recommendation_panel.get("items", [])
    if items and isinstance(items[0], dict):
        rec_symbol = str(items[0].get("symbol", "")).strip()
        if rec_symbol:
            return rec_symbol

    return ""


def extract_reference_price(closeout_artifact: dict) -> float | None:
    direct_price = _safe_float(closeout_artifact.get("reference_price"))
    if direct_price is not None:
        return direct_price

    market_panel = closeout_artifact.get("market_panel", {})
    for field in ("reference_price", "price_at_closeout"):
        value = _safe_float(market_panel.get(field))
        if value is not None:
            return value

    recommendation_panel = closeout_artifact.get("recommendation_panel", {})
    items = recommendation_panel.get("items", [])
    if items and isinstance(items[0], dict):
        first_item = items[0]

        for field in ("reference_price", "price_at_closeout", "entry_price", "price"):
            value = _safe_float(first_item.get(field))
            if value is not None:
                return value

        entry = _safe_float(first_item.get("entry"))
        if entry is not None:
            return entry

    return None


def extract_event_theme(closeout_artifact: dict) -> str:
    runtime_panel = closeout_artifact.get("runtime_panel", {})
    runtime_event_theme = str(runtime_panel.get("event_theme", "")).strip()
    if runtime_event_theme:
        return runtime_event_theme

    market_panel = closeout_artifact.get("market_panel", {})
    market_event_theme = str(market_panel.get("event_theme", "")).strip()
    if market_event_theme:
        return market_event_theme

    direct_expected = str(closeout_artifact.get("expected_behavior", "")).strip()
    if direct_expected:
        return direct_expected.replace(" ", "_").lower()

    return ""


def classify_direction_from_event_theme(event_theme: str) -> str:
    normalized = str(event_theme or "").strip().lower()

    bullish_tokens = ("rebound", "rally", "breakout", "bullish", "surge", "recovery")
    bearish_tokens = ("decline", "selloff", "breakdown", "bearish", "collapse", "drop")

    if any(token in normalized for token in bullish_tokens):
        return "up"

    if any(token in normalized for token in bearish_tokens):
        return "down"

    return "unknown"


def validate_market_outcome_source(source: str) -> None:
    normalized = str(source or "").strip().lower()
    if normalized not in ALLOWED_MARKET_OUTCOME_SOURCES:
        raise ValueError("invalid_market_outcome_source")


def build_market_outcome_narrative(
    *,
    event_theme: str,
    direction: str,
    reference_price: float,
    current_price: float,
) -> tuple[str, float]:
    if reference_price <= 0:
        raise ValueError("invalid_reference_price")

    delta_pct = ((current_price - reference_price) / reference_price) * 100.0
    normalized_theme = str(event_theme or "").replace("_", " ").strip()

    if direction == "up":
        if current_price > reference_price:
            actual_outcome = (
                f"confirmed {normalized_theme} via price increase "
                f"from {reference_price:.2f} to {current_price:.2f} "
                f"({delta_pct:+.2f}%)"
            )
            return actual_outcome, delta_pct

        actual_outcome = (
            f"price decreased from {reference_price:.2f} to {current_price:.2f} "
            f"({delta_pct:+.2f}%), against expected upward direction"
        )
        return actual_outcome, delta_pct

    if direction == "down":
        if current_price < reference_price:
            actual_outcome = (
                f"confirmed {normalized_theme} via price decrease "
                f"from {reference_price:.2f} to {current_price:.2f} "
                f"({delta_pct:+.2f}%)"
            )
            return actual_outcome, delta_pct

        actual_outcome = (
            f"price increased from {reference_price:.2f} to {current_price:.2f} "
            f"({delta_pct:+.2f}%), against expected downward direction"
        )
        return actual_outcome, delta_pct

    raise ValueError("unsupported_event_theme_direction")