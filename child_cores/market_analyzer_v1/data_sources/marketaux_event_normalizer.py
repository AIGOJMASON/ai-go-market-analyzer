from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

try:
    from AI_GO.child_cores.ingress.canonical_event_ingress import (
        CanonicalEventIngressRequest,
    )
except ImportError:
    from child_cores.ingress.canonical_event_ingress import (  # type: ignore
        CanonicalEventIngressRequest,
    )

from .marketaux_event_client import RawMarketauxNewsResult
from .marketaux_event_policy import MarketauxEventPolicy


class MarketauxEventNormalizationError(RuntimeError):
    pass


@dataclass(frozen=True)
class CanonicalEventBatch:
    request_count: int
    requests: list[CanonicalEventIngressRequest]

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_count": self.request_count,
            "requests": [item.to_dict() for item in self.requests],
        }


class MarketauxEventNormalizer:
    def __init__(self, policy: MarketauxEventPolicy | None = None) -> None:
        self._policy = policy or MarketauxEventPolicy()

    def normalize(self, raw: RawMarketauxNewsResult) -> CanonicalEventBatch:
        data = raw.payload.get("data")
        if not isinstance(data, list):
            raise MarketauxEventNormalizationError("normalizer_missing_data_list")

        normalized: list[CanonicalEventIngressRequest] = []

        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                record = self._normalize_one(item=item, raw=raw)
            except MarketauxEventNormalizationError:
                continue

            normalized.append(record)
            if len(normalized) >= self._policy.max_normalized_records_per_run:
                break

        return CanonicalEventBatch(
            request_count=len(normalized),
            requests=normalized,
        )

    def _normalize_one(
        self,
        item: dict[str, Any],
        raw: RawMarketauxNewsResult,
    ) -> CanonicalEventIngressRequest:
        headline = self._extract_headline(item)
        summary = self._extract_summary(item)
        published_at = self._extract_published_at(item)
        source_url = self._extract_source_url(item)

        symbol = self._extract_symbol(item)
        sector = self._extract_sector(item, headline, summary, symbol)
        event_theme_candidate = self._policy.derive_event_theme_candidate(
            headline=headline,
            summary=summary,
            sector=sector,
        )
        entity_count = self._extract_entity_count(item)
        confirmation = self._policy.confirmation_for_story(
            symbol=symbol,
            sector=sector,
            headline=headline,
            entity_count=entity_count,
        )

        provider_metadata = {
            "language": self._safe_str(item.get("language")),
            "sentiment": self._safe_str(item.get("sentiment")),
            "entity_count": entity_count,
            "requested_symbols": list(raw.requested_symbols),
            "published_after": raw.published_after,
        }

        return CanonicalEventIngressRequest(
            request_id=self._build_request_id(symbol=symbol, sector=sector),
            source=self._policy.provider_name,
            source_type="news_event_feed",
            headline=headline,
            summary=summary,
            symbol=symbol,
            sector=sector,
            event_theme_candidate=event_theme_candidate,
            confirmation=confirmation,
            observed_at=self._now_timestamp(),
            published_at=published_at,
            source_url=source_url,
            provider_metadata=provider_metadata,
        )

    def _extract_headline(self, item: dict[str, Any]) -> str:
        headline = self._safe_str(item.get("title")) or self._safe_str(item.get("headline"))
        if not headline:
            raise MarketauxEventNormalizationError("normalizer_missing_headline")
        return headline

    def _extract_summary(self, item: dict[str, Any]) -> str:
        return (
            self._safe_str(item.get("description"))
            or self._safe_str(item.get("snippet"))
            or self._safe_str(item.get("summary"))
        )

    def _extract_published_at(self, item: dict[str, Any]) -> str | None:
        value = (
            self._safe_str(item.get("published_at"))
            or self._safe_str(item.get("publishedAt"))
            or self._safe_str(item.get("datetime"))
        )
        return value or None

    def _extract_source_url(self, item: dict[str, Any]) -> str | None:
        value = self._safe_str(item.get("url"))
        return value or None

    def _extract_symbol(self, item: dict[str, Any]) -> str | None:
        direct_candidates = [item.get("symbol"), item.get("ticker")]
        for candidate in direct_candidates:
            normalized = self._policy.validate_optional_symbol(candidate)
            if normalized:
                return normalized

        symbols = item.get("symbols")
        if isinstance(symbols, list):
            for value in symbols:
                normalized = self._policy.validate_optional_symbol(value)
                if normalized:
                    return normalized

        entities = item.get("entities")
        if isinstance(entities, list):
            for entity in entities:
                if not isinstance(entity, dict):
                    continue
                normalized = self._policy.validate_optional_symbol(
                    entity.get("symbol") or entity.get("ticker") or entity.get("name")
                )
                if normalized:
                    return normalized

        return None

    def _extract_sector(
        self,
        item: dict[str, Any],
        headline: str,
        summary: str,
        symbol: str | None,
    ) -> str:
        if symbol:
            return self._policy.sector_for_symbol(symbol)

        explicit_sector = self._safe_str(item.get("sector"))
        if explicit_sector:
            return explicit_sector.strip().lower().replace(" ", "_")

        return self._policy.infer_sector(headline, summary)

    def _extract_entity_count(self, item: dict[str, Any]) -> int:
        entities = item.get("entities")
        if isinstance(entities, list):
            return len(entities)
        return 0

    def _build_request_id(self, symbol: str | None, sector: str) -> str:
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        suffix = uuid.uuid4().hex[:8]
        token = (symbol or sector or "event").lower().replace(" ", "_")
        return f"event-marketaux-{token}-{stamp}-{suffix}"

    def _now_timestamp(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _safe_str(self, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()