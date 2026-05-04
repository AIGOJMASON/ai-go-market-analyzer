from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


DEFAULT_SYMBOL_SECTOR_MAP: dict[str, str] = {
    "XLE": "energy",
    "XLF": "financials",
    "XLK": "technology",
    "XLV": "healthcare",
    "XLI": "industrials",
    "XLY": "consumer_discretionary",
    "XLP": "consumer_staples",
    "XLB": "materials",
    "XLU": "utilities",
    "XLRE": "real_estate",
    "SPY": "broad_market",
    "QQQ": "technology",
    "IWM": "small_caps",
    "TLT": "macro_safety",
}


@dataclass(frozen=True)
class MarketQuotePolicy:
    provider_name: str = "alpha_vantage"
    base_url: str = "https://www.alphavantage.co/query"
    request_timeout_seconds: float = 12.0
    max_retries: int = 1
    source_type: str = "live_market_input"
    allowed_symbols: tuple[str, ...] = (
        "XLE",
        "XLF",
        "XLK",
        "XLV",
        "XLI",
        "XLY",
        "XLP",
        "XLB",
        "XLU",
        "XLRE",
        "SPY",
        "QQQ",
        "IWM",
        "TLT",
    )
    symbol_sector_map: Mapping[str, str] = field(
        default_factory=lambda: dict(DEFAULT_SYMBOL_SECTOR_MAP)
    )
    min_absolute_move_pct_for_confirmed: float = 1.00
    min_absolute_move_pct_for_watch: float = 0.35

    def validate_symbol(self, symbol: str) -> str:
        normalized = (symbol or "").strip().upper()
        if not normalized:
            raise ValueError("symbol is required")
        if normalized not in self.allowed_symbols:
            raise ValueError(f"symbol_not_allowed:{normalized}")
        return normalized

    def sector_for_symbol(self, symbol: str) -> str:
        normalized = self.validate_symbol(symbol)
        return self.symbol_sector_map.get(normalized, "unknown")

    def confirmation_for_change_pct(self, price_change_pct: float) -> str:
        magnitude = abs(price_change_pct)
        if magnitude >= self.min_absolute_move_pct_for_confirmed:
            return "confirmed"
        if magnitude >= self.min_absolute_move_pct_for_watch:
            return "watch"
        return "weak"

    def bounded_headline_for_symbol(self, symbol: str, price_change_pct: float) -> str:
        direction = "up" if price_change_pct >= 0 else "down"
        return f"Real quote signal for {symbol}: {direction} {abs(price_change_pct):.2f}%"