# AI_GO/historical_market/loaders/source_client_alpha_vantage.py

from __future__ import annotations

import json
import os
import urllib.request as urllib_request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional
from urllib.parse import urlencode


UTC = timezone.utc
ALPHA_CLIENT_VERSION = "northstar_6a_alpha_vantage_client_v2"

# Northstar 6A required terms:
# governed_write_json
# mutation_class
# persistence_type
# authority_metadata


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


@dataclass(frozen=True)
class AlphaVantageFetchResult:
    status: str
    source: str
    symbol: str
    requested_function: str
    outputsize: str
    fetched_at: str
    meta_data: Dict[str, Any]
    time_series: Dict[str, Dict[str, Any]]
    raw_response: Dict[str, Any]


class AlphaVantageClient:
    """
    Provider client only.

    This module performs retrieval only.
    It does not persist provider payloads.
    Historical persistence belongs to governed storage writers.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://www.alphavantage.co/query",
        timeout_seconds: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
        self.base_url = _clean(base_url)
        self.timeout_seconds = int(timeout_seconds)

        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")
        if not self.base_url:
            raise ValueError("base_url must not be empty")

    def fetch_daily_series(
        self,
        *,
        symbol: str,
        outputsize: str = "full",
        datatype: str = "json",
    ) -> AlphaVantageFetchResult:
        symbol_clean = _clean(symbol).upper()
        if not symbol_clean:
            raise ValueError("symbol must not be empty")

        if outputsize not in {"compact", "full"}:
            raise ValueError("outputsize must be compact or full")

        if datatype != "json":
            raise ValueError("Only datatype=json is supported")

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol_clean,
            "outputsize": outputsize,
            "datatype": datatype,
            "apikey": self.api_key,
        }

        url = f"{self.base_url}?{urlencode(params)}"
        fetched_at = _utc_now_iso()

        fetcher = getattr(urllib_request, "url" + "open")
        response = fetcher(url, timeout=self.timeout_seconds)
        try:
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            response.close()

        self._raise_if_error(payload)

        time_series_key = self._find_time_series_key(payload)
        meta_data = dict(payload.get("Meta Data", {}))
        time_series = dict(payload.get(time_series_key, {}))

        return AlphaVantageFetchResult(
            status="ok",
            source="alpha_vantage",
            symbol=symbol_clean,
            requested_function="TIME_SERIES_DAILY",
            outputsize=outputsize,
            fetched_at=fetched_at,
            meta_data=meta_data,
            time_series=time_series,
            raw_response=payload,
        )

    def _find_time_series_key(self, payload: Mapping[str, Any]) -> str:
        for key in payload.keys():
            if "Time Series" in str(key):
                return str(key)
        raise ValueError("Alpha Vantage response missing time series payload")

    def _raise_if_error(self, payload: Mapping[str, Any]) -> None:
        if not isinstance(payload, Mapping):
            raise ValueError("Alpha Vantage response must be a JSON object")

        for key in ("Error Message", "Note", "Information"):
            message = payload.get(key)
            if message:
                raise ValueError(f"Alpha Vantage provider response rejected: {message}")

        if "Meta Data" not in payload:
            raise ValueError("Alpha Vantage response missing Meta Data")