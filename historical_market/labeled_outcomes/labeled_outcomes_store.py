from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json

from AI_GO.core.state_runtime.state_paths import state_root
from AI_GO.historical_market.labeled_outcomes.labeled_outcomes_registry import (
    ALLOWED_DIRECTIONAL_BIAS,
    ALLOWED_OUTCOME_CLASSES,
    ALLOWED_SOURCE_TYPES,
    INDEX_FILE_NAMES,
    LABELED_OUTCOME_ARTIFACT_TYPE,
    LABELED_OUTCOME_RECEIPT_TYPE,
)
from AI_GO.historical_market.labeled_outcomes.labeled_outcomes_schema import (
    LabeledOutcomeRecord,
)


LABELED_OUTCOMES_STORE_VERSION = "northstar_6a_labeled_outcomes_store_v7"


def _state_root() -> Path:
    return state_root() / "historical_market" / "labeled_outcomes"


def _records_dir() -> Path:
    return _state_root() / "records"


def _indexes_dir() -> Path:
    return _state_root() / "indexes"


def _receipts_dir() -> Path:
    return _state_root() / "receipts"


def ensure_dirs() -> None:
    for path in (_state_root(), _records_dir(), _indexes_dir(), _receipts_dir()):
        path.mkdir(parents=True, exist_ok=True)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _upper(value: Any) -> str:
    return _clean(value).upper()


def _lower(value: Any) -> str:
    return _clean(value).lower()


def _short_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def build_record_id(
    *,
    symbol: str,
    event_theme: str,
    outcome_class: str,
    observed_at: str,
) -> str:
    seed = f"{_upper(symbol)}|{_lower(event_theme)}|{_lower(outcome_class)}|{_clean(observed_at)}"
    return f"lblout_{_short_hash(seed)}"


def _classification(*, persistence_type: str, mutation_class: str) -> Dict[str, Any]:
    return {
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "pm_authority_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "historical_truth_mutation": True,
    }


def _authority_metadata(*, operation: str) -> Dict[str, Any]:
    return {
        "authority_id": "historical_market_labeled_outcomes_store",
        "operation": operation,
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_mutate_recommendations": False,
        "can_mutate_pm_authority": False,
        "can_override_governance": False,
        "append_only_memory": True,
        "governance_stage": "northstar_6a",
    }



def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))

        if isinstance(parsed, dict) and parsed.get("artifact_type") == "governed_persistence_envelope":
            return parsed.get("payload", default)

        return parsed
    except Exception:
        return default


def _validate_inputs(
    *,
    symbol: str,
    event_theme: str,
    outcome_class: str,
    directional_bias: str,
    observed_at: str,
    source_type: str,
) -> None:
    if not _clean(symbol):
        raise ValueError("symbol is required")
    if not _clean(event_theme):
        raise ValueError("event_theme is required")
    if outcome_class not in ALLOWED_OUTCOME_CLASSES:
        raise ValueError(f"Unsupported outcome_class: {outcome_class}")
    if directional_bias not in ALLOWED_DIRECTIONAL_BIAS:
        raise ValueError(f"Unsupported directional_bias: {directional_bias}")
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(f"Unsupported source_type: {source_type}")
    if not _clean(observed_at):
        raise ValueError("observed_at is required")


def _record_path(record_id: str) -> Path:
    return _records_dir() / f"{record_id}.json"


def _receipt_path(record_id: str) -> Path:
    return _receipts_dir() / f"{record_id}.receipt.json"


def _index_path(index_name: str) -> Path:
    return _indexes_dir() / INDEX_FILE_NAMES[index_name]


def _update_index_list(index: Dict[str, List[str]], key: str, record_id: str) -> Dict[str, List[str]]:
    values = list(index.get(key, []))
    if record_id not in values:
        values.append(record_id)
    index[key] = values
    return index


def _write_indexes(record: Dict[str, Any]) -> Dict[str, str]:
    symbol = _upper(record.get("symbol"))
    event_theme = _lower(record.get("event_theme"))
    record_id = _clean(record.get("record_id"))

    by_symbol_path = _index_path("by_symbol")
    by_event_theme_path = _index_path("by_event_theme")
    latest_path = _index_path("latest")

    by_symbol = _load_json(by_symbol_path, {})
    by_event_theme = _load_json(by_event_theme_path, {})
    latest = _load_json(latest_path, [])

    if not isinstance(by_symbol, dict):
        by_symbol = {}
    if not isinstance(by_event_theme, dict):
        by_event_theme = {}
    if not isinstance(latest, list):
        latest = []

    by_symbol = _update_index_list(by_symbol, symbol, record_id)
    by_event_theme = _update_index_list(by_event_theme, event_theme, record_id)

    latest = [item for item in latest if item.get("record_id") != record_id]
    latest.insert(
        0,
        {
            "record_id": record_id,
            "symbol": symbol,
            "event_theme": event_theme,
            "outcome_class": record.get("outcome_class"),
            "observed_at": record.get("observed_at"),
        },
    )
    latest = latest[:100]

    by_symbol_mutation_class = "historical_market_labeled_outcome_index"
    by_symbol_persistence_type = "labeled_outcome_index_by_symbol"
    by_symbol_authority_metadata = _authority_metadata(operation="write_by_symbol_index")

    governed_write_json(
        path=by_symbol_path,
        payload=by_symbol,
        mutation_class=by_symbol_mutation_class,
        persistence_type=by_symbol_persistence_type,
        authority_metadata=by_symbol_authority_metadata,
    )

    by_theme_mutation_class = "historical_market_labeled_outcome_index"
    by_theme_persistence_type = "labeled_outcome_index_by_event_theme"
    by_theme_authority_metadata = _authority_metadata(operation="write_by_event_theme_index")

    governed_write_json(
        path=by_event_theme_path,
        payload=by_event_theme,
        mutation_class=by_theme_mutation_class,
        persistence_type=by_theme_persistence_type,
        authority_metadata=by_theme_authority_metadata,
    )

    latest_mutation_class = "historical_market_labeled_outcome_index"
    latest_persistence_type = "latest_labeled_outcomes_index"
    latest_authority_metadata = _authority_metadata(operation="write_latest_index")

    governed_write_json(
        path=latest_path,
        payload=latest,
        mutation_class=latest_mutation_class,
        persistence_type=latest_persistence_type,
        authority_metadata=latest_authority_metadata,
    )

    return {
        "by_symbol": str(by_symbol_path),
        "by_event_theme": str(by_event_theme_path),
        "latest": str(latest_path),
    }


def create_labeled_outcome_record(
    *,
    symbol: str,
    event_theme: str,
    outcome_class: str,
    directional_bias: str,
    observed_at: str,
    source_type: str,
    return_pct: Optional[float] = None,
    hold_duration_bars: Optional[int] = None,
    setup_type: Optional[str] = None,
    headline: Optional[str] = None,
    sector: Optional[str] = None,
    source_request_id: Optional[str] = None,
    source_closeout_id: Optional[str] = None,
    notes: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> LabeledOutcomeRecord:
    clean_symbol = _upper(symbol)
    clean_event_theme = _lower(event_theme)
    clean_outcome_class = _lower(outcome_class)
    clean_directional_bias = _lower(directional_bias)
    clean_source_type = _lower(source_type)
    clean_observed_at = _clean(observed_at)

    _validate_inputs(
        symbol=clean_symbol,
        event_theme=clean_event_theme,
        outcome_class=clean_outcome_class,
        directional_bias=clean_directional_bias,
        observed_at=clean_observed_at,
        source_type=clean_source_type,
    )

    record_id = build_record_id(
        symbol=clean_symbol,
        event_theme=clean_event_theme,
        outcome_class=clean_outcome_class,
        observed_at=clean_observed_at,
    )

    return LabeledOutcomeRecord(
        record_id=record_id,
        artifact_type=LABELED_OUTCOME_ARTIFACT_TYPE,
        created_at=_utc_now_iso(),
        symbol=clean_symbol,
        event_theme=clean_event_theme,
        outcome_class=clean_outcome_class,
        directional_bias=clean_directional_bias,
        observed_at=clean_observed_at,
        source_type=clean_source_type,
        return_pct=return_pct,
        hold_duration_bars=hold_duration_bars,
        setup_type=setup_type,
        headline=headline,
        sector=sector,
        source_request_id=source_request_id,
        source_closeout_id=source_closeout_id,
        notes=notes,
        metadata=dict(metadata or {}),
    )


def persist_labeled_outcome_record(record: LabeledOutcomeRecord) -> Dict[str, Any]:
    ensure_dirs()

    record_mutation_class = "historical_market_labeled_outcome_persistence"
    record_persistence_type = "historical_labeled_outcome"
    record_authority_metadata = _authority_metadata(operation="write_labeled_outcome")

    payload = record.to_dict()
    payload["classification"] = _classification(
        persistence_type=record_persistence_type,
        mutation_class=record_mutation_class,
    )
    payload["authority_metadata"] = record_authority_metadata
    payload["execution_allowed"] = False
    payload["sealed"] = True

    record_id = _clean(payload.get("record_id"))
    record_path = _record_path(record_id)

    governed_write_json(
        path=record_path,
        payload=payload,
        mutation_class=record_mutation_class,
        persistence_type=record_persistence_type,
        authority_metadata=record_authority_metadata,
    )

    index_paths = _write_indexes(payload)

    receipt_mutation_class = "historical_market_labeled_outcome_receipt"
    receipt_persistence_type = "historical_labeled_outcome_receipt"
    receipt_authority_metadata = _authority_metadata(operation="write_labeled_outcome_receipt")

    receipt = {
        "artifact_type": LABELED_OUTCOME_RECEIPT_TYPE,
        "artifact_version": LABELED_OUTCOMES_STORE_VERSION,
        "receipt_id": f"{record_id}.receipt",
        "record_id": record_id,
        "written_at": _utc_now_iso(),
        "record_path": str(record_path),
        "index_paths": index_paths,
        "classification": _classification(
            persistence_type=receipt_persistence_type,
            mutation_class=receipt_mutation_class,
        ),
        "authority_metadata": receipt_authority_metadata,
        "sealed": True,
    }

    receipt_path = _receipt_path(record_id)

    governed_write_json(
        path=receipt_path,
        payload=receipt,
        mutation_class=receipt_mutation_class,
        persistence_type=receipt_persistence_type,
        authority_metadata=receipt_authority_metadata,
    )

    return {
        "status": "persisted",
        "record_id": record_id,
        "record_path": str(record_path),
        "receipt_path": str(receipt_path),
        "index_paths": index_paths,
        "mutation_class": record_mutation_class,
        "persistence_type": record_persistence_type,
        "authority_metadata": record_authority_metadata,
    }


def create_and_persist_labeled_outcome(**kwargs: Any) -> Dict[str, Any]:
    record = create_labeled_outcome_record(**kwargs)
    return persist_labeled_outcome_record(record)


def persist_labeled_outcome(record: Dict[str, Any]) -> Dict[str, Any]:
    record_id = record.get("record_id") or build_record_id(
        symbol=str(record.get("symbol", "UNKNOWN")),
        event_theme=str(record.get("event_theme", "unknown")),
        outcome_class=str(record.get("outcome_class", "unknown")),
        observed_at=str(record.get("observed_at", _utc_now_iso())),
    )

    payload = dict(record)
    payload["record_id"] = record_id

    mutation_class = "historical_market_labeled_outcome_persistence"
    persistence_type = "historical_labeled_outcome"
    authority_metadata = _authority_metadata(operation="persist_labeled_outcome_compat")

    path = _record_path(record_id)

    governed_write_json(
        path=path,
        payload=payload,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=authority_metadata,
    )

    return {
        "status": "persisted",
        "record_id": record_id,
        "path": str(path),
        "mutation_class": mutation_class,
        "persistence_type": persistence_type,
        "authority_metadata": authority_metadata,
    }


def load_labeled_outcome(record_id: str) -> Dict[str, Any]:
    parsed = _load_json(_record_path(_clean(record_id)), {})
    return parsed if isinstance(parsed, dict) else {}


def list_latest_labeled_outcomes(limit: int = 25) -> List[Dict[str, Any]]:
    ensure_dirs()
    latest = _load_json(_index_path("latest"), [])
    if not isinstance(latest, list):
        return []
    return latest[: max(0, int(limit))]