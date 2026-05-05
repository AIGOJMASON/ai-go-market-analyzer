from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from .market_quote_policy import MarketQuotePolicy


UTC = timezone.utc


def _utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip().replace("%", "")
            if not value:
                return None
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class RawQuoteResult:
    provider: str
    symbol: str
    fetched_at: str
    payload: dict[str, Any]


class AlphaVantageQuoteClient:
    def __init__(self, api_key: str, policy: MarketQuotePolicy | None = None) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required")
        self._api_key = api_key.strip()
        self._policy = policy or MarketQuotePolicy()

    @property
    def policy(self) -> MarketQuotePolicy:
        return self._policy

    def fetch_global_quote(self, *, symbol: str) -> RawQuoteResult:
        normalized_symbol = self._policy.validate_symbol(symbol)

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": normalized_symbol,
            "apikey": self._api_key,
        }
        url = f"{self._policy.base_url}?{urlencode(params)}"

        with urlopen(url, timeout=self._policy.request_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self._raise_if_error(payload)

        quote = payload.get("Global Quote")
        if not isinstance(quote, dict) or not quote:
            raise ValueError("market_quote_missing_global_quote")

        returned_symbol = str(quote.get("01. symbol", "")).strip().upper()
        if returned_symbol and returned_symbol != normalized_symbol:
            raise ValueError("market_quote_symbol_mismatch")

        price = _safe_float(quote.get("05. price"))
        if price is None:
            raise ValueError("market_quote_missing_price")

        return RawQuoteResult(
            provider=self._policy.provider_name,
            symbol=returned_symbol or normalized_symbol,
            fetched_at=_utc_now_iso(),
            payload=payload,
        )

    def _raise_if_error(self, payload: dict[str, Any]) -> None:
        if "Error Message" in payload:
            raise ValueError(f"market_quote_provider_error:{payload['Error Message']}")
        if "Note" in payload:
            raise RuntimeError(f"market_quote_provider_note:{payload['Note']}")
        if "Information" in payload:
            raise RuntimeError(f"market_quote_provider_information:{payload['Information']}")