from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from .live_ingress_receipt import build_live_ingress_receipt
from .live_ingress_state import LiveIngressState


CANONICAL_PACKET_TYPE = "pm_style_live_input"
CANONICAL_PARENT_AUTHORITY = "PM_CORE"
CANONICAL_TARGET_CORE = "market_analyzer_v1"
CANONICAL_INGRESS_SURFACE = "child_cores.ingress.research_live_ingress"


class CanonicalLiveIngressError(ValueError):
    pass


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise CanonicalLiveIngressError("payload must be a dictionary")
    return deepcopy(payload)


def _safe_str(v: Any) -> str:
    return str(v).strip() if v is not None else ""


def _safe_upper(v: Any) -> str:
    return _safe_str(v).upper()


def _safe_lower(v: Any, fallback: str = "") -> str:
    val = _safe_str(v).lower()
    return val or fallback


def _safe_float(v: Any) -> float | None:
    try:
        if v is None:
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def _derive_reference_price(p: Dict[str, Any]) -> float | None:
    for k in (
        "reference_price",
        "price_at_closeout",
        "price",
        "current_price",
        "last_price",
    ):
        val = _safe_float(p.get(k))
        if val is not None:
            return val
    return None


def _derive_confidence(price_change_pct: Any) -> str:
    try:
        pct = float(price_change_pct)
    except Exception:
        return "unknown"

    if pct >= 3.0:
        return "high"
    if pct < 1.5:
        return "low"
    return "medium"


def _derive_theme(sector: str, confirmation: str) -> str:
    if sector == "energy":
        return "energy_rebound"
    if sector == "materials":
        return "supply_expansion"
    if confirmation != "confirmed":
        return "confirmation_failure"
    return "speculative_move"


def build_canonical_live_ingress_packet(
    payload: Dict[str, Any],
    request_id: str,
) -> Dict[str, Any]:
    p = _normalize_payload(payload)

    symbol = _safe_upper(p.get("symbol"))
    headline = p.get("headline")
    summary = p.get("summary")

    source = _safe_str(p.get("source"))
    source_type = _safe_str(p.get("source_type")) or "live_market_input"
    sector = _safe_lower(p.get("sector"), "unknown")
    confirmation = _safe_lower(p.get("confirmation"))
    observed_at = p.get("observed_at")
    published_at = p.get("published_at")
    source_url = p.get("source_url")
    provider_metadata = deepcopy(p.get("provider_metadata")) if isinstance(p.get("provider_metadata"), dict) else {}

    price_change_pct = p.get("price_change_pct")
    reference_price = _derive_reference_price(p)

    confidence = _derive_confidence(price_change_pct)
    theme = _derive_theme(sector, confirmation)

    packet: Dict[str, Any] = {
        "packet_type": CANONICAL_PACKET_TYPE,
        "parent_authority": CANONICAL_PARENT_AUTHORITY,
        "target_core": CANONICAL_TARGET_CORE,
        "case_id": request_id,
        "request_id": request_id,
        "ingress_surface": CANONICAL_INGRESS_SURFACE,
        "source": source or None,
        "source_type": source_type,
        "symbol": symbol or None,
        "headline": headline,
        "summary": summary,
        "sector": sector,
        "confirmation": confirmation,
        "price_change_pct": price_change_pct,
        "reference_price": reference_price,
        "price_at_closeout": reference_price,
        "price": reference_price,
        "observed_at": observed_at,
        "published_at": published_at,
        "source_url": source_url,
        "provider_metadata": provider_metadata,
        "event_theme": theme,
        "live_market_context": {
            "source": source or None,
            "source_type": source_type,
            "symbol": symbol or None,
            "headline": headline,
            "summary": summary,
            "sector": sector,
            "confirmation": confirmation,
            "price_change_pct": price_change_pct,
            "reference_price": reference_price,
            "price_at_closeout": reference_price,
            "price": reference_price,
            "observed_at": observed_at,
            "published_at": published_at,
            "source_url": source_url,
            "provider_metadata": provider_metadata,
            "event_theme": theme,
        },
        "event_context": {
            "theme": theme,
            "propagation": "sector",
            "confirmed": confirmation == "confirmed",
            "headline": headline,
            "summary": summary,
            "sector": sector,
            "confirmation": confirmation,
            "price_change_pct": price_change_pct,
            "reference_price": reference_price,
            "price_at_closeout": reference_price,
            "price": reference_price,
            "observed_at": observed_at,
            "published_at": published_at,
            "source_url": source_url,
        },
        "candidates": [
            {
                "symbol": symbol or None,
                "confidence": confidence,
                "reference_price": reference_price,
                "price_change_pct": price_change_pct,
                "sector": sector,
                "confirmation": confirmation,
                "event_theme": theme,
            }
        ],
    }

    return packet


def build_canonical_live_pm_packet(
    payload: Dict[str, Any],
    request_id: str,
) -> Dict[str, Any]:
    return build_canonical_live_ingress_packet(payload=payload, request_id=request_id)


def build_canonical_live_ingress_artifacts(
    payload: Dict[str, Any],
    request_id: str,
    state: LiveIngressState | None = None,
) -> Dict[str, Any]:
    packet = build_canonical_live_ingress_packet(payload=payload, request_id=request_id)
    receipt = build_live_ingress_receipt(packet=packet)

    if state is not None:
        state.update(
            ingress_id=receipt["ingress_id"],
            request_id=request_id,
            target_core=packet["target_core"],
        )

    return {
        "packet": packet,
        "receipt": receipt,
    }