# AI_GO/historical_market/storage/raw_store.py

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

try:
    from AI_GO.historical_market.storage.db_paths import HistoricalMarketPaths
except ModuleNotFoundError:
    from historical_market.storage.db_paths import HistoricalMarketPaths


UTC = timezone.utc
RAW_STORE_VERSION = "northstar_6a_raw_store_v1"


@dataclass(frozen=True)
class RawBarWriteResult:
    status: str
    record_count: int
    output_path: str
    receipt_path: str
    written_at: str


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC).isoformat()
        return value.astimezone(UTC).isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe_upper(value: Any) -> str:
    return _clean(value).upper()


def _safe_lower(value: Any) -> str:
    return _clean(value).lower()


def _ensure_mapping(record: Mapping[str, Any], record_name: str) -> Dict[str, Any]:
    if not isinstance(record, Mapping):
        raise TypeError(f"{record_name} must be a mapping")
    return dict(record)


def _require_fields(record: Mapping[str, Any], record_name: str, fields: Iterable[str]) -> None:
    missing = [field for field in fields if field not in record or record[field] in (None, "")]
    if missing:
        raise ValueError(f"{record_name} missing required fields: {', '.join(missing)}")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(parsed, dict) and parsed.get("artifact_type") == "governed_persistence_envelope":
            return parsed.get("payload", default)
        return parsed
    except Exception:
        return default


def _authority_metadata(*, source: str, operation: str) -> Dict[str, Any]:
    return {
        "authority_id": "historical_market_raw_store",
        "source": _clean(source) or "raw_store",
        "operation": _clean(operation),
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_mutate_recommendations": False,
        "can_mutate_pm_authority": False,
        "can_override_governance": False,
        "append_only_memory": True,
        "governance_stage": "northstar_6a",
    }


def _classification(*, persistence_type: str, mutation_class: str) -> Dict[str, Any]:
    return {
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "pm_authority_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "advisory_only": False,
    }


def governed_write_json(
    *,
    path: Path,
    payload: Any,
    mutation_class: str,
    persistence_type: str,
    authority_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    if not mutation_class:
        raise ValueError("mutation_class is required")
    if not persistence_type:
        raise ValueError("persistence_type is required")
    if not isinstance(authority_metadata, dict) or not authority_metadata:
        raise ValueError("authority_metadata is required")

    envelope = {
        "artifact_type": "governed_persistence_envelope",
        "artifact_version": RAW_STORE_VERSION,
        "persisted_at": _utc_now_iso(),
        "classification": _classification(
            persistence_type=persistence_type,
            mutation_class=mutation_class,
        ),
        "authority_metadata": dict(authority_metadata),
        "payload": payload,
        "sealed": True,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False, default=_json_default),
        encoding="utf-8",
    )
    os.replace(tmp_path, path)

    return {
        "status": "persisted",
        "path": str(path),
        "mutation_class": mutation_class,
        "persistence_type": persistence_type,
        "authority_metadata": dict(authority_metadata),
    }


class RawStore:
    def __init__(self, *, paths: Optional[HistoricalMarketPaths] = None) -> None:
        self.paths = paths or HistoricalMarketPaths()
        self.paths.ensure_all()

    def _bars_root(self) -> Path:
        return self.paths.raw_bars_dir

    def _receipts_root(self) -> Path:
        return self.paths.raw_receipts_dir

    def _partition_path(self, *, symbol: str, asset_class: str, timeframe: str, year_month: str) -> Path:
        return (
            self._bars_root()
            / _safe_lower(asset_class)
            / _safe_upper(symbol)
            / _safe_lower(timeframe)
            / f"{year_month}.json"
        )

    def _receipt_path(self, *, symbol: str, timeframe: str, written_at: str) -> Path:
        stamp = written_at.replace(":", "").replace("+", "_").replace(".", "_")
        return self._receipts_root() / f"raw-write-{_safe_upper(symbol)}-{_safe_lower(timeframe)}-{stamp}.json"

    def _normalize_year_month(self, record: Mapping[str, Any]) -> str:
        raw = _clean(record.get("year_month"))
        if raw:
            return raw

        timestamp = _clean(record.get("timestamp") or record.get("date") or record.get("observed_at"))
        if not timestamp:
            raise ValueError("raw bar record requires timestamp, date, observed_at, or year_month")

        return timestamp[:7]

    def _normalize_bar(
        self,
        *,
        record: Mapping[str, Any],
        symbol: str,
        asset_class: str,
        timeframe: str,
        source: str,
        fetched_at: str,
    ) -> Dict[str, Any]:
        payload = _ensure_mapping(record, "raw_bar_record")
        _require_fields(payload, "raw_bar_record", ["timestamp"])

        payload.setdefault("artifact_type", "historical_raw_market_bar")
        payload.setdefault("artifact_version", RAW_STORE_VERSION)
        payload["symbol"] = _safe_upper(payload.get("symbol") or symbol)
        payload["asset_class"] = _safe_lower(payload.get("asset_class") or asset_class)
        payload["timeframe"] = _safe_lower(payload.get("timeframe") or timeframe)
        payload["source"] = _safe_lower(payload.get("source") or source)
        payload["fetched_at"] = _clean(payload.get("fetched_at") or fetched_at)
        payload["classification"] = _classification(
            persistence_type="historical_raw_market_bar",
            mutation_class="historical_market_raw_persistence",
        )
        payload["authority_metadata"] = _authority_metadata(
            source=payload["source"],
            operation="append_raw_bar",
        )
        payload["execution_allowed"] = False
        payload["sealed"] = True
        return payload

    def write_bars(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        symbol: str,
        asset_class: str,
        timeframe: str = "1d",
        source: str = "unknown",
        fetched_at: Optional[str] = None,
        receipt_id: Optional[str] = None,
    ) -> RawBarWriteResult:
        written_at = _utc_now_iso()
        clean_symbol = _safe_upper(symbol)
        clean_asset_class = _safe_lower(asset_class)
        clean_timeframe = _safe_lower(timeframe)
        clean_source = _safe_lower(source)
        clean_fetched_at = _clean(fetched_at) or written_at

        if not clean_symbol:
            raise ValueError("symbol is required")
        if not clean_asset_class:
            raise ValueError("asset_class is required")
        if not records:
            raise ValueError("records must not be empty")

        partitions: Dict[str, List[Dict[str, Any]]] = {}

        for index, record in enumerate(records):
            normalized = self._normalize_bar(
                record=record,
                symbol=clean_symbol,
                asset_class=clean_asset_class,
                timeframe=clean_timeframe,
                source=clean_source,
                fetched_at=clean_fetched_at,
            )
            year_month = self._normalize_year_month(normalized)
            normalized["raw_sequence_index"] = index
            partitions.setdefault(year_month, []).append(normalized)

        partition_results: List[Dict[str, Any]] = []

        for year_month, rows in partitions.items():
            path = self._partition_path(
                symbol=clean_symbol,
                asset_class=clean_asset_class,
                timeframe=clean_timeframe,
                year_month=year_month,
            )
            existing = _read_json(path, [])
            if not isinstance(existing, list):
                existing = []

            combined = existing + rows

            result = governed_write_json(
                path=path,
                payload=combined,
                mutation_class="historical_market_raw_persistence",
                persistence_type="historical_raw_market_bar_partition",
                authority_metadata=_authority_metadata(
                    source=clean_source,
                    operation="write_raw_bar_partition",
                ),
            )
            partition_results.append(
                {
                    "year_month": year_month,
                    "record_count": len(rows),
                    "path": result["path"],
                }
            )

        receipt = {
            "artifact_type": "historical_raw_write_receipt",
            "artifact_version": RAW_STORE_VERSION,
            "receipt_id": _clean(receipt_id) or f"raw-write-{clean_symbol}-{written_at}",
            "written_at": written_at,
            "symbol": clean_symbol,
            "asset_class": clean_asset_class,
            "timeframe": clean_timeframe,
            "source": clean_source,
            "record_count": sum(len(rows) for rows in partitions.values()),
            "partition_count": len(partitions),
            "partitions": partition_results,
            "classification": _classification(
                persistence_type="historical_raw_write_receipt",
                mutation_class="historical_market_raw_receipt",
            ),
            "authority_metadata": _authority_metadata(
                source=clean_source,
                operation="write_raw_receipt",
            ),
            "sealed": True,
        }

        receipt_path = self._receipt_path(
            symbol=clean_symbol,
            timeframe=clean_timeframe,
            written_at=written_at,
        )
        governed_write_json(
            path=receipt_path,
            payload=receipt,
            mutation_class="historical_market_raw_receipt",
            persistence_type="historical_raw_write_receipt",
            authority_metadata=_authority_metadata(
                source=clean_source,
                operation="write_raw_receipt",
            ),
        )

        first_output = partition_results[0]["path"] if partition_results else ""

        return RawBarWriteResult(
            status="written",
            record_count=receipt["record_count"],
            output_path=first_output,
            receipt_path=str(receipt_path),
            written_at=written_at,
        )

    def append_bars(
        self,
        *,
        bars: Sequence[Mapping[str, Any]],
        symbol: str,
        asset_class: str,
        timeframe: str = "1d",
        source: str = "unknown",
        fetched_at: Optional[str] = None,
        receipt_id: Optional[str] = None,
    ) -> RawBarWriteResult:
        return self.write_bars(
            records=bars,
            symbol=symbol,
            asset_class=asset_class,
            timeframe=timeframe,
            source=source,
            fetched_at=fetched_at,
            receipt_id=receipt_id,
        )

    def read_bars(
        self,
        *,
        symbol: str,
        asset_class: str = "",
        timeframe: str = "1d",
        limit: int = 5000,
    ) -> List[Dict[str, Any]]:
        clean_symbol = _safe_upper(symbol)
        clean_timeframe = _safe_lower(timeframe)
        rows: List[Dict[str, Any]] = []

        roots: List[Path] = []
        if asset_class:
            roots.append(self._bars_root() / _safe_lower(asset_class) / clean_symbol / clean_timeframe)
        else:
            for asset_root in self._bars_root().glob("*"):
                candidate = asset_root / clean_symbol / clean_timeframe
                if candidate.exists():
                    roots.append(candidate)

        for root in roots:
            for path in sorted(root.glob("*.json")):
                parsed = _read_json(path, [])
                if isinstance(parsed, list):
                    rows.extend([dict(item) for item in parsed if isinstance(item, dict)])
                if len(rows) >= limit:
                    return rows[:limit]

        return rows[:limit]