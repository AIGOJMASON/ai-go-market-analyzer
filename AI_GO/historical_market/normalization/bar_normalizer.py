from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


UTC = timezone.utc


def _safe_str(value: Any, field_name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} must not be empty")
    return text


def _parse_date_to_utc_midnight(value: str) -> str:
    """
    Alpha Vantage daily series keys are date strings like YYYY-MM-DD.
    Normalize to UTC midnight ISO timestamp for internal storage.
    """
    text = _safe_str(value, "date")
    parsed = datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=UTC)
    return parsed.isoformat()


def _parse_timestamp_like(value: str, field_name: str) -> str:
    text = _safe_str(value, field_name)
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).isoformat()


def _to_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc


@dataclass(frozen=True)
class NormalizedBarBatch:
    source: str
    symbol: str
    asset_class: str
    timeframe: str
    record_count: int
    bars: List[Dict[str, Any]]


class BarNormalizer:
    """
    Normalizes vendor-native daily time series rows into AI_GO historical raw-bar records.
    """

    def normalize_alpha_vantage_daily_series(
        self,
        *,
        symbol: str,
        asset_class: str,
        time_series: Mapping[str, Mapping[str, Any]],
        fetched_at: str,
        adjusted: bool = False,
        provider_symbol: Optional[str] = None,
        currency: str = "",
        ingest_metadata: Optional[Mapping[str, Any]] = None,
    ) -> NormalizedBarBatch:
        symbol_clean = _safe_str(symbol, "symbol").upper()
        asset_class_clean = _safe_str(asset_class, "asset_class").lower()
        fetched_at_iso = _parse_timestamp_like(fetched_at, "fetched_at")
        provider_symbol_clean = (provider_symbol or symbol_clean).strip().upper()

        normalized_rows: List[Dict[str, Any]] = []

        for date_key in sorted(time_series.keys()):
            point = dict(time_series[date_key])

            row = {
                "source": "alpha_vantage",
                "symbol": symbol_clean,
                "asset_class": asset_class_clean,
                "bar_timestamp": _parse_date_to_utc_midnight(date_key),
                "timeframe": "1d",
                "open": _to_float(point.get("1. open"), "1. open"),
                "high": _to_float(point.get("2. high"), "2. high"),
                "low": _to_float(point.get("3. low"), "3. low"),
                "close": _to_float(point.get("4. close"), "4. close"),
                "volume": _to_float(point.get("5. volume", 0), "5. volume"),
                "fetched_at": fetched_at_iso,
                "adjusted": adjusted,
                "provider_symbol": provider_symbol_clean,
                "currency": currency,
                "ingest_metadata": dict(ingest_metadata or {}),
            }
            normalized_rows.append(row)

        return NormalizedBarBatch(
            source="alpha_vantage",
            symbol=symbol_clean,
            asset_class=asset_class_clean,
            timeframe="1d",
            record_count=len(normalized_rows),
            bars=normalized_rows,
        )