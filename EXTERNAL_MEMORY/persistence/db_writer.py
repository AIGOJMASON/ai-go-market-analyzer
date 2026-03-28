from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict

DB_PATH = Path("AI_GO/state/external_memory/external_memory.db")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt_id(record: Dict[str, Any]) -> str:
    digest = sha256(repr(sorted(record.items())).encode("utf-8")).hexdigest()[:12]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"extmemdb_{ts}_{digest}"


def ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS external_memory_records (
                memory_id TEXT PRIMARY KEY,
                qualification_record_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                trust_class TEXT NOT NULL,
                source_quality_weight REAL NOT NULL,
                signal_quality_weight REAL NOT NULL,
                domain_relevance_weight REAL NOT NULL,
                persistence_value_weight REAL NOT NULL,
                contamination_penalty REAL NOT NULL,
                redundancy_penalty REAL NOT NULL,
                adjusted_weight REAL NOT NULL,
                target_child_cores_json TEXT NOT NULL,
                provenance_json TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def commit_external_memory_record(record: Dict[str, Any]) -> Dict[str, Any]:
    ensure_db()

    memory_id = f"extmem_{record['qualification_record_id']}"
    target_child_cores_json = json.dumps(record.get("target_child_cores", []), sort_keys=True)
    provenance_json = json.dumps(record.get("provenance", {}), sort_keys=True)
    payload_json = json.dumps(record.get("payload", {}), sort_keys=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO external_memory_records (
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                record["qualification_record_id"],
                record["source_type"],
                record["trust_class"],
                record["source_quality_weight"],
                record["signal_quality_weight"],
                record["domain_relevance_weight"],
                record["persistence_value_weight"],
                record["contamination_penalty"],
                record["redundancy_penalty"],
                record["adjusted_weight"],
                target_child_cores_json,
                provenance_json,
                payload_json,
                _utc_now(),
            ),
        )

    receipt = {
        "artifact_type": "external_memory_persistence_receipt",
        "receipt_id": _receipt_id(record),
        "created_at": _utc_now(),
        "persistence_decision": "committed",
        "memory_id": memory_id,
        "qualification_record_id": record["qualification_record_id"],
        "db_path": str(DB_PATH),
        "source_type": record["source_type"],
        "adjusted_weight": record["adjusted_weight"],
    }
    return receipt