from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json


class DBWriterError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[3]


def _state_dir() -> Path:
    return _root_dir() / "state" / "external_memory" / "market_analyzer_v1"


def _records_dir() -> Path:
    return _state_dir() / "db" / "records"


def _indexes_dir() -> Path:
    return _state_dir() / "db" / "indexes"


def _db_receipts_dir() -> Path:
    return _state_dir() / "db" / "receipts"


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _as_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def _persist_json(
    *,
    path: Path,
    payload: Dict[str, Any] | List[Dict[str, Any]],
    operation: str,
) -> None:
    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="external_memory_db_persistence",
        persistence_type="external_memory_db",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": operation,
            "child_core_id": "market_analyzer_v1",
            "layer": "external_memory.db_writer",
        },
    )


def _build_receipt_id(record_id: str) -> str:
    digest = sha256(f"{record_id}|db_writer".encode("utf-8")).hexdigest()[:12]
    return f"db_write_{record_id}_{digest}"


def _build_index(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    index: List[Dict[str, Any]] = []

    for record in records:
        ingress = _as_dict(record.get("external_memory_ingress_record"))
        record_id = _safe_str(record.get("record_id"))
        if not record_id:
            continue

        index.append(
            {
                "record_id": record_id,
                "persisted_at": record.get("persisted_at"),
                "target_child_core_id": record.get("target_child_core_id"),
                "source_type": ingress.get("source_type"),
                "symbol": ingress.get("symbol"),
                "sector": ingress.get("sector"),
                "trust_class": ingress.get("trust_class"),
                "record_path": str(_records_dir() / f"{record_id}.json"),
            }
        )

    return index


def run_db_writer(
    external_memory_ingress_record: Dict[str, Any],
    qualification_result: Dict[str, Any],
    persistence_gate_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(external_memory_ingress_record, dict):
        raise DBWriterError("external_memory_ingress_record must be a dict")
    if not isinstance(qualification_result, dict):
        raise DBWriterError("qualification_result must be a dict")
    if not isinstance(persistence_gate_result, dict):
        raise DBWriterError("persistence_gate_result must be a dict")

    record = deepcopy(external_memory_ingress_record)
    qualification = deepcopy(qualification_result)
    gate = deepcopy(persistence_gate_result)

    record_id = _safe_str(record.get("record_id"))
    if not record_id:
        raise DBWriterError("external_memory_ingress_record is missing record_id")

    if gate.get("allow_persist") is not True:
        raise DBWriterError("persistence_gate_result does not allow persistence")

    persisted_at = _utc_now_iso()

    persisted_record = {
        "record_type": "external_memory_persisted_record",
        "record_version": "v1",
        "record_id": record_id,
        "persisted_at": persisted_at,
        "target_child_core_id": _safe_str(record.get("target_child_core_id")),
        "external_memory_ingress_record": record,
        "qualification_artifact": _as_dict(
            qualification.get("external_memory_qualification_artifact")
        ),
        "persistence_gate_artifact": _as_dict(
            gate.get("external_memory_persistence_gate_artifact")
        ),
        "classification": {
            "persistence_type": "external_memory_db",
            "mutation_class": "external_memory_db_persistence",
            "execution_allowed": False,
            "runtime_mutation_allowed": False,
            "recommendation_mutation_allowed": False,
            "authority_mutation_allowed": False,
            "advisory_only": True,
        },
        "sealed": True,
    }

    record_path = _records_dir() / f"{record_id}.json"
    _persist_json(
        path=record_path,
        payload=persisted_record,
        operation="persist_external_memory_record",
    )

    latest_path = _indexes_dir() / "latest_persisted_record.json"
    _persist_json(
        path=latest_path,
        payload=persisted_record,
        operation="persist_latest_external_memory_record",
    )

    index_path = _indexes_dir() / "persisted_index.json"
    existing_index = _read_json_list(index_path)
    records_for_index = [
        item for item in existing_index if _safe_str(item.get("record_id")) != record_id
    ]
    records_for_index.append(
        {
            "record_id": record_id,
            "persisted_at": persisted_at,
            "target_child_core_id": persisted_record["target_child_core_id"],
            "source_type": record.get("source_type"),
            "symbol": record.get("symbol"),
            "sector": record.get("sector"),
            "trust_class": record.get("trust_class"),
            "record_path": str(record_path),
        }
    )

    _persist_json(
        path=index_path,
        payload=records_for_index,
        operation="persist_external_memory_index",
    )

    receipt_id = _build_receipt_id(record_id)
    receipt_path = _db_receipts_dir() / f"{receipt_id}.json"

    receipt = {
        "receipt_id": receipt_id,
        "receipt_type": "external_memory_db_write_receipt",
        "receipt_version": "v1",
        "status": "written",
        "created_at": persisted_at,
        "record_id": record_id,
        "record_path": str(record_path),
        "index_path": str(index_path),
        "classification": {
            "persistence_type": "external_memory_db_receipt",
            "mutation_class": "external_memory_db_persistence",
            "execution_allowed": False,
            "runtime_mutation_allowed": False,
            "recommendation_mutation_allowed": False,
            "authority_mutation_allowed": False,
            "advisory_only": True,
        },
        "sealed": True,
    }

    _persist_json(
        path=receipt_path,
        payload=receipt,
        operation="persist_external_memory_db_receipt",
    )

    return {
        "status": "written",
        "record_id": record_id,
        "record_path": str(record_path),
        "latest_path": str(latest_path),
        "index_path": str(index_path),
        "receipt_id": receipt_id,
        "receipt_path": str(receipt_path),
        "external_memory_db_record": persisted_record,
        "external_memory_db_receipt": receipt,
        "sealed": True,
    }