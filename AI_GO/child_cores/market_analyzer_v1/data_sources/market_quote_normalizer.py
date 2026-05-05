from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

from .market_quote_client import RawQuoteResult
from .market_quote_policy import MarketQuotePolicy


class MarketQuoteNormalizationError(RuntimeError):
    pass


def _safe_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        text = str(value).strip().replace("%", "")
        if not text:
            return None
        return round(float(text), 4)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class CanonicalLiveQuoteRequest:
    request_id: str
    source: str
    source_type: str
    symbol: str
    headline: str
    price_change_pct: float
    sector: str
    confirmation: str
    price: float
    reference_price: float
    price_at_closeout: float
    observed_at: str
    provider_metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source": self.source,
            "source_type": self.source_type,
            "symbol": self.symbol,
            "headline": self.headline,
            "price_change_pct": self.price_change_pct,
            "sector": self.sector,
            "confirmation": self.confirmation,
            "price": self.price,
            "reference_price": self.reference_price,
            "price_at_closeout": self.price_at_closeout,
            "observed_at": self.observed_at,
            "provider_metadata": dict(self.provider_metadata),
        }


class MarketQuoteNormalizer:
    def __init__(self, policy: MarketQuotePolicy | None = None) -> None:
        self._policy = policy or MarketQuotePolicy()

    def normalize(self, raw: RawQuoteResult) -> CanonicalLiveQuoteRequest:
        quote = raw.payload.get("Global Quote")
        if not isinstance(quote, dict):
            raise MarketQuoteNormalizationError("normalizer_missing_global_quote")

        symbol = self._policy.validate_symbol(raw.symbol)

        price = _safe_float(quote.get("05. price"))
        if price is None:
            raise MarketQuoteNormalizationError("normalizer_missing_price")

        price_change_pct = _safe_float(quote.get("10. change percent"))
        if price_change_pct is None:
            raise MarketQuoteNormalizationError("normalizer_missing_change_percent")

        latest_trading_day = str(quote.get("07. latest trading day", "")).strip()
        observed_at = f"{latest_trading_day}T00:00:00Z" if latest_trading_day else raw.fetched_at

        confirmation = self._policy.confirmation_for_change_pct(price_change_pct)
        headline = self._policy.bounded_headline_for_symbol(symbol, price_change_pct)
        sector = self._policy.sector_for_symbol(symbol)

        provider_metadata = {
            "provider": raw.provider,
            "fetched_at": raw.fetched_at,
            "latest_trading_day": latest_trading_day,
            "change": quote.get("09. change"),
            "change_percent": quote.get("10. change percent"),
        }

        return CanonicalLiveQuoteRequest(
            request_id=self._build_request_id(symbol),
            source=self._policy.provider_name,
            source_type=self._policy.source_type,
            symbol=symbol,
            headline=headline,
            price_change_pct=price_change_pct,
            sector=sector,
            confirmation=confirmation,
            price=price,
            reference_price=price,
            price_at_closeout=price,
            observed_at=observed_at,
            provider_metadata=provider_metadata,
        )

    def _build_request_id(self, symbol: str) -> str:
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        suffix = uuid.uuid4().hex[:8]
        return f"real-quote-{symbol.lower()}-{stamp}-{suffix}"