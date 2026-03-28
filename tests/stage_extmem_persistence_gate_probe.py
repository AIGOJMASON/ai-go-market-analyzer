from __future__ import annotations

import sqlite3
from pathlib import Path

from AI_GO.EXTERNAL_MEMORY.persistence.db_writer import DB_PATH, ensure_db
from AI_GO.EXTERNAL_MEMORY.persistence.persistence_gate import apply_persistence_gate
from AI_GO.EXTERNAL_MEMORY.qualification.qualification_engine import (
    qualify_external_memory_candidate,
)

TABLE_NAME = "external_memory_records"


def _reset_db() -> None:
    ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"DELETE FROM {TABLE_NAME}")


def _row_count() -> int:
    ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()
    return int(row[0])


def _base_payload() -> dict:
    return {
        "artifact_type": "governed_external_signal",
        "source_type": "news_feed",
        "source_quality_weight": 30,
        "signal_quality_weight": 20,
        "domain_relevance_weight": 15,
        "persistence_value_weight": 10,
        "contamination_penalty": 5,
        "redundancy_penalty": 0,
        "trust_class": "verified",
        "payload": {
            "headline": "Confirmed energy disruption event",
            "symbol": "XLE",
            "sector": "energy",
        },
        "target_child_cores": ["market_analyzer_v1"],
        "provenance": {
            "packet_id": "rpkt_test_002",
            "source_ref": "feed://energy/002",
            "ingested_at": "2026-03-28T12:05:00Z",
        },
    }


def case_01_persist_candidate_commits_to_db() -> dict:
    _reset_db()
    payload = _base_payload()

    qualification = qualify_external_memory_candidate(payload)
    persistence = apply_persistence_gate(qualification.record)

    passed = (
        qualification.record["decision"] == "persist_candidate"
        and persistence["artifact_type"] == "external_memory_persistence_receipt"
        and persistence["persistence_decision"] == "committed"
        and _row_count() == 1
    )
    return {
        "case": "case_01_persist_candidate_commits_to_db",
        "status": "passed" if passed else "failed",
        "details": {
            "qualification_decision": qualification.record["decision"],
            "persistence_artifact_type": persistence["artifact_type"],
            "persistence_decision": persistence["persistence_decision"],
            "row_count": _row_count(),
        },
    }


def case_02_hold_is_not_persisted_in_phase_1() -> dict:
    _reset_db()
    payload = _base_payload()
    payload["source_quality_weight"] = 28
    payload["signal_quality_weight"] = 12
    payload["domain_relevance_weight"] = 10
    payload["persistence_value_weight"] = 8
    payload["contamination_penalty"] = 4

    qualification = qualify_external_memory_candidate(payload)
    persistence = apply_persistence_gate(qualification.record)

    passed = (
        qualification.record["decision"] == "hold"
        and persistence["artifact_type"] == "external_memory_rejection_receipt"
        and persistence["rejection_reason"] == "held_not_persisted_in_phase_1"
        and _row_count() == 0
    )
    return {
        "case": "case_02_hold_is_not_persisted_in_phase_1",
        "status": "passed" if passed else "failed",
        "details": {
            "qualification_decision": qualification.record["decision"],
            "rejection_reason": persistence["rejection_reason"],
            "row_count": _row_count(),
        },
    }


def case_03_reject_does_not_commit() -> dict:
    _reset_db()
    payload = _base_payload()
    payload["source_quality_weight"] = 10

    qualification = qualify_external_memory_candidate(payload)
    persistence = apply_persistence_gate(qualification.record)

    passed = (
        qualification.record["decision"] == "reject"
        and persistence["artifact_type"] == "external_memory_rejection_receipt"
        and persistence["rejection_reason"] == "source_quality_below_floor"
        and _row_count() == 0
    )
    return {
        "case": "case_03_reject_does_not_commit",
        "status": "passed" if passed else "failed",
        "details": {
            "qualification_decision": qualification.record["decision"],
            "rejection_reason": persistence["rejection_reason"],
            "row_count": _row_count(),
        },
    }


def case_04_invalid_qualification_artifact_is_rejected() -> dict:
    _reset_db()
    invalid_record = {
        "artifact_type": "wrong_artifact",
        "decision": "persist_candidate",
        "qualification_record_id": "bad_001",
    }

    persistence = apply_persistence_gate(invalid_record)

    passed = (
        persistence["artifact_type"] == "external_memory_rejection_receipt"
        and persistence["rejection_reason"] == "invalid_input"
        and _row_count() == 0
    )
    return {
        "case": "case_04_invalid_qualification_artifact_is_rejected",
        "status": "passed" if passed else "failed",
        "details": {
            "artifact_type": persistence["artifact_type"],
            "rejection_reason": persistence["rejection_reason"],
            "row_count": _row_count(),
        },
    }


def run_probe() -> dict:
    cases = [
        case_01_persist_candidate_commits_to_db(),
        case_02_hold_is_not_persisted_in_phase_1(),
        case_03_reject_does_not_commit(),
        case_04_invalid_qualification_artifact_is_rejected(),
    ]
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = len(cases) - passed
    return {"passed": passed, "failed": failed, "results": cases}


if __name__ == "__main__":
    print(run_probe())