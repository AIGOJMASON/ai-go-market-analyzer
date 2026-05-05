from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping


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
}

DEFAULT_SECTOR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "energy": (
        "energy", "oil", "gas", "crude", "pipeline", "refinery",
        "opec", "drilling", "petroleum", "lng", "hormuz", "shipping",
        "texas e&ps", "e&ps", "exploration", "production"
    ),
    "financials": (
        "bank", "credit", "finance", "financial", "insurance"
    ),
    "technology": (
        "technology", "software", "semiconductor", "chip", "ai", "cloud"
    ),
    "utilities": (
        "utility", "grid", "power", "electricity"
    ),
}

DEFAULT_THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "energy_rebound": (
        "oil",
        "oil prices",
        "saudi oil",
        "gas",
        "crude",
        "pipeline",
        "refinery",
        "energy prices",
        "premium",
        "premiums",
        "hormuz",
        "shipping",
        "strait",
        "production cut",
        "supply disruption",
        "supply shock",
        "texas e&ps",
        "e&ps",
        "exploration",
        "production",
    ),
    "financial_stress": (
        "liquidity", "credit stress", "downgrade", "default"
    ),
    "tech_momentum": (
        "ai", "semiconductor", "chip", "cloud"
    ),
}


@dataclass(frozen=True)
class MarketauxEventPolicy:
    provider_name: str = "marketaux"
    base_url: str = "https://api.marketaux.com"
    endpoint_path: str = "/v1/news/all"

    request_timeout_seconds: float = 12.0
    max_retries: int = 1
    default_language: str = "en"
    default_limit: int = 25
    max_normalized_records_per_run: int = 10

    allowed_symbols: tuple[str, ...] = (
        "XLE", "XLF", "XLK", "XLV", "XLI",
        "XLY", "XLP", "XLB", "XLU", "XLRE",
        "SPY", "QQQ", "IWM",
    )

    symbol_sector_map: Mapping[str, str] = field(
        default_factory=lambda: dict(DEFAULT_SYMBOL_SECTOR_MAP)
    )
    sector_keywords: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: dict(DEFAULT_SECTOR_KEYWORDS)
    )
    theme_keywords: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: dict(DEFAULT_THEME_KEYWORDS)
    )

    def validate_symbol(self, symbol: str) -> str:
        normalized = (symbol or "").strip().upper()
        if not normalized:
            raise ValueError("symbol is required")
        if normalized not in self.allowed_symbols:
            raise ValueError(f"symbol_not_allowed:{normalized}")
        return normalized

    def validate_optional_symbol(self, symbol: object) -> str | None:
        if symbol is None:
            return None
        text = str(symbol).strip().upper()
        if not text:
            return None
        if text not in self.allowed_symbols:
            return None
        return text

    def sector_for_symbol(self, symbol: str) -> str:
        normalized = self.validate_symbol(symbol)
        return self.symbol_sector_map.get(normalized, "unknown")

    def infer_sector(self, *texts: str) -> str:
        haystack = " ".join(texts).lower()
        for sector, keywords in self.sector_keywords.items():
            if any(keyword in haystack for keyword in keywords):
                return sector
        return "unknown"

    def derive_event_theme_candidate(
        self,
        headline: str,
        summary: str,
        sector: str,
    ) -> str:
        haystack = f"{headline} {summary}".lower()

        strong_energy_terms = (
            "oil prices",
            "saudi oil",
            "premium",
            "premiums",
            "hormuz",
            "shipping",
            "strait",
            "crude",
            "refinery",
            "texas e&ps",
            "e&ps",
            "exploration",
            "production",
            "energy prices",
        )
        if any(term in haystack for term in strong_energy_terms):
            return "energy_rebound"

        broad_market_terms = (
            "nasdaq",
            "dow",
            "s&p",
            "markets",
            "stocks",
            "equities",
            "mixed opening",
            "market volatility",
        )
        if any(term in haystack for term in broad_market_terms):
            return "unknown"

        for theme, keywords in self.theme_keywords.items():
            if any(keyword in haystack for keyword in keywords):
                return theme

        return "unknown"

    def confirmation_for_story(
        self,
        symbol: str | None,
        sector: str,
        headline: str,
        entity_count: int,
    ) -> str:
        headline_l = (headline or "").lower()

        broad_market_terms = (
            "nasdaq", "dow", "s&p", "markets",
            "stocks", "equities", "mixed opening"
        )
        if any(term in headline_l for term in broad_market_terms):
            return "external_watch"

        strong_energy_terms = (
            "oil",
            "oil prices",
            "saudi oil",
            "gas",
            "crude",
            "premium",
            "premiums",
            "hormuz",
            "shipping",
            "supply disruption",
            "production cut",
            "texas e&ps",
            "e&ps",
        )

        strong_match = (
            sector == "energy" and
            any(term in headline_l for term in strong_energy_terms)
        )

        if symbol and strong_match:
            return "external_signal"

        if symbol or sector != "unknown":
            return "external_watch"

        return "external_weak"

    def normalize_symbols_for_query(self, symbols: Iterable[str] | None) -> list[str]:
        if not symbols:
            return []
        normalized: list[str] = []
        for symbol in symbols:
            try:
                normalized.append(self.validate_symbol(symbol))
            except ValueError:
                continue
        return list(dict.fromkeys(normalized))