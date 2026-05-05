from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from .marketaux_event_policy import MarketauxEventPolicy


class MarketauxEventClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class RawMarketauxNewsResult:
    provider: str
    payload: dict[str, Any]
    fetched_at_epoch: float
    requested_symbols: list[str]
    published_after: str | None


class MarketauxEventClient:
    def __init__(self, api_key: str, policy: MarketauxEventPolicy | None = None) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required")
        self._api_key = api_key.strip()
        self._policy = policy or MarketauxEventPolicy()

    @property
    def policy(self) -> MarketauxEventPolicy:
        return self._policy

    def fetch_news(
        self,
        symbols: list[str] | None = None,
        published_after: str | None = None,
        limit: int | None = None,
    ) -> RawMarketauxNewsResult:
        normalized_symbols = self._policy.normalize_symbols_for_query(symbols)
        effective_limit = limit or self._policy.default_limit

        params: dict[str, Any] = {
            "api_token": self._api_key,
            "language": self._policy.default_language,
            "limit": effective_limit,
        }
        if normalized_symbols:
            params["symbols"] = ",".join(normalized_symbols)
        if published_after:
            params["published_after"] = published_after

        base = self._policy.base_url.rstrip("/")
        path = self._policy.endpoint_path
        url = f"{base}{path}?{urllib.parse.urlencode(params)}"

        last_error: Exception | None = None
        attempts = self._policy.max_retries + 1

        for attempt in range(attempts):
            try:
                request = urllib.request.Request(
                    url=url,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "AI_GO/market_analyzer_v1/marketaux_event_client",
                    },
                    method="GET",
                )
                with urllib.request.urlopen(
                    request,
                    timeout=self._policy.request_timeout_seconds,
                ) as response:
                    if response.status != 200:
                        raise MarketauxEventClientError(
                            f"marketaux_http_status_error:{response.status}"
                        )
                    raw_bytes = response.read()
                    payload = json.loads(raw_bytes.decode("utf-8"))
                    self._validate_payload(payload)
                    return RawMarketauxNewsResult(
                        provider=self._policy.provider_name,
                        payload=payload,
                        fetched_at_epoch=time.time(),
                        requested_symbols=normalized_symbols,
                        published_after=published_after,
                    )
            except Exception as exc:
                last_error = exc
                if attempt >= attempts - 1:
                    break
                time.sleep(0.5)

        raise MarketauxEventClientError(
            f"marketaux_fetch_failed:{type(last_error).__name__}:{last_error}"
        )

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise MarketauxEventClientError("marketaux_invalid_payload_type")

        error_value = payload.get("error")
        if error_value:
            raise MarketauxEventClientError(f"marketaux_provider_error:{error_value}")

        data = payload.get("data")
        if not isinstance(data, list):
            raise MarketauxEventClientError("marketaux_missing_data_list")