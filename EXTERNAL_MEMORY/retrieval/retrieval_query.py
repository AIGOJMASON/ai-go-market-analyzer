from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from AI_GO.EXTERNAL_MEMORY.persistence.db_writer import DB_PATH, ensure_db
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.persistence.db_writer import DB_PATH, ensure_db


def _row_to_record(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "memory_id": row["memory_id"],
        "qualification_record_id": row["qualification_record_id"],
        "source_type": row["source_type"],
        "trust_class": row["trust_class"],
        "source_quality_weight": row["source_quality_weight"],
        "signal_quality_weight": row["signal_quality_weight"],
        "domain_relevance_weight": row["domain_relevance_weight"],
        "persistence_value_weight": row["persistence_value_weight"],
        "contamination_penalty": row["contamination_penalty"],
        "redundancy_penalty": row["redundancy_penalty"],
        "adjusted_weight": row["adjusted_weight"],
        "target_child_cores": json.loads(row["target_child_cores_json"]),
        "provenance": json.loads(row["provenance_json"]),
        "payload": json.loads(row["payload_json"]),
        "created_at": row["created_at"],
    }


def query_external_memory_records(
    *,
    target_core_id: str,
    symbol: Optional[str] = None,
    sector: Optional[str] = None,
    trust_class: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 10,
    min_adjusted_weight: Optional[float] = None,
) -> List[Dict[str, Any]]:
    ensure_db()

    sql = """
        SELECT
            memory_id,
            qualification_record_id,
            source_type,
            trust_class,
            source_quality_weight,
            signal_quality_weight,
            domain_relevance_weight,
            persistence_value_weight,
            contamination_penalty,
            redundancy_penalty,
            adjusted_weight,
            target_child_cores_json,
            provenance_json,
            payload_json,
            created_at
        FROM external_memory_records
        WHERE 1=1
    """
    params: list[Any] = []

    if trust_class:
        sql += " AND trust_class = ?"
        params.append(trust_class)

    if source_type:
        sql += " AND source_type = ?"
        params.append(source_type)

    if min_adjusted_weight is not None:
        sql += " AND adjusted_weight >= ?"
        params.append(min_adjusted_weight)

    sql += " ORDER BY adjusted_weight DESC, created_at DESC LIMIT ?"
    params.append(limit)

    records: List[Dict[str, Any]] = []
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()

    for row in rows:
        record = _row_to_record(row)

        targets = record.get("target_child_cores", [])
        if target_core_id not in targets:
            continue

        payload = record.get("payload", {})

        if symbol and payload.get("symbol") != symbol:
            continue

        if sector and payload.get("sector") != sector:
            continue

        records.append(record)

    return records