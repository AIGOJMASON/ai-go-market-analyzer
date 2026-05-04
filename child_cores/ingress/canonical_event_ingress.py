from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict


CANONICAL_PACKET_TYPE = "pm_style_event_input"
CANONICAL_PARENT_AUTHORITY = "PM_CORE"
CANONICAL_TARGET_CORE = "market_analyzer_v1"
CANONICAL_INGRESS_SURFACE = "child_cores.ingress.research_event_ingress"


class CanonicalEventIngressError(ValueError):
    pass


@dataclass(frozen=True)
class CanonicalEventIngressRequest:
    request_id: str
    source: str
    source_type: str
    headline: str
    summary: str
    symbol: str | None
    sector: str
    event_theme_candidate: str
    confirmation: str
    observed_at: str
    published_at: str | None
    source_url: str | None
    provider_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source": self.source,
            "source_type": self.source_type,
            "headline": self.headline,
            "summary": self.summary,
            "symbol": self.symbol,
            "sector": self.sector,
            "event_theme_candidate": self.event_theme_candidate,
            "confirmation": self.confirmation,
            "observed_at": self.observed_at,
            "published_at": self.published_at,
            "source_url": self.source_url,
            "provider_metadata": dict(self.provider_metadata or {}),
        }


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise CanonicalEventIngressError("payload must be dict")
    return deepcopy(payload)


def _safe_str(v: Any) -> str:
    return str(v).strip() if v is not None else ""


def _safe_lower(v: Any) -> str:
    return _safe_str(v).lower()


def build_canonical_event_ingress_packet(
    payload: Dict[str, Any],
    request_id: str,
) -> Dict[str, Any]:
    p = _normalize_payload(payload)

    headline = _safe_str(p.get("headline"))
    if not headline:
        raise CanonicalEventIngressError("headline is required")

    packet: Dict[str, Any] = {
        "packet_type": CANONICAL_PACKET_TYPE,
        "parent_authority": CANONICAL_PARENT_AUTHORITY,
        "target_core": CANONICAL_TARGET_CORE,
        "case_id": request_id,
        "request_id": request_id,
        "ingress_surface": CANONICAL_INGRESS_SURFACE,
        "source": _safe_str(p.get("source")),
        "source_type": _safe_str(p.get("source_type")) or "news_event_feed",
        "symbol": _safe_str(p.get("symbol")) or None,
        "headline": headline,
        "summary": _safe_str(p.get("summary")),
        "sector": _safe_lower(p.get("sector")) or "unknown",
        "event_theme_candidate": _safe_lower(p.get("event_theme_candidate")),
        "confirmation": _safe_lower(p.get("confirmation")) or "watch",
        "published_at": p.get("published_at"),
        "observed_at": p.get("observed_at"),
        "source_url": p.get("source_url"),
        "provider_metadata": dict(p.get("provider_metadata") or {}),
        "event_context": {
            "headline": headline,
            "summary": _safe_str(p.get("summary")),
            "sector": _safe_lower(p.get("sector")) or "unknown",
            "confirmation": _safe_lower(p.get("confirmation")) or "watch",
            "event_theme_candidate": _safe_lower(p.get("event_theme_candidate")),
            "published_at": p.get("published_at"),
            "observed_at": p.get("observed_at"),
        },
    }
    return packet