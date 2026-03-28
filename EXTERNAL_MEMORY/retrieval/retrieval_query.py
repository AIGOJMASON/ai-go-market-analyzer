from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

from AI_GO.EXTERNAL_MEMORY.persistence.db_writer import DB_PATH, ensure_db


def _row_to_record(row: sqlite3.Row) -> Dict[str, Any]:
    payload = json.loads(row["payload_json"])
    provenance = json.loads(row["provenance_json"])
    target_child_cores = json.loads(row["target_child_cores_json"])
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
        "target_child_cores": target_child_cores,
        "provenance": provenance,
        "payload": payload,
        "created_at": row["created_at"],
    }


def query_external_memory_records(request: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]]]:
    ensure_db()

    target_child_core = str(request["target_child_core"])
    limit = int(request["limit"])
    filters = []
    params: List[Any] = []

    filters.append("target_child_cores_json LIKE ?")
    params.append(f'%"{target_child_core}"%')

    if request.get("source_type"):
        filters.append("source_type = ?")
        params.append(str(request["source_type"]))

    if request.get("trust_class"):
        filters.append("trust_class = ?")
        params.append(str(request["trust_class"]).lower())

    if request.get("min_adjusted_weight") is not None:
        filters.append("adjusted_weight >= ?")
        params.append(float(request["min_adjusted_weight"]))

    if request.get("symbol"):
        filters.append("payload_json LIKE ?")
        params.append(f'%"symbol": "{request["symbol"]}"%')

    if request.get("sector"):
        filters.append("payload_json LIKE ?")
        params.append(f'%"sector": "{request["sector"]}"%')

    where_clause = " AND ".join(filters) if filters else "1=1"

    count_sql = f"""
        SELECT COUNT(*) AS row_count
        FROM external_memory_records
        WHERE {where_clause}
    """

    query_sql = f"""
        SELECT *
        FROM external_memory_records
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ?
    """

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        matched_count = int(conn.execute(count_sql, params).fetchone()["row_count"])
        rows = conn.execute(query_sql, [*params, limit]).fetchall()

    records = [_row_to_record(row) for row in rows]
    return matched_count, records