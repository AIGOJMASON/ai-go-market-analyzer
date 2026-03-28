from __future__ import annotations

from AI_GO.EXTERNAL_MEMORY.qualification.qualification_engine import (
    qualify_external_memory_candidate,
)


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
            "headline": "Energy infrastructure disruption confirmed",
            "symbol": "XLE",
            "sector": "energy",
        },
        "target_child_cores": ["market_analyzer_v1"],
        "provenance": {
            "packet_id": "rpkt_test_001",
            "source_ref": "feed://energy/001",
            "ingested_at": "2026-03-28T12:00:00Z",
        },
    }


def case_01_valid_persist_candidate() -> dict:
    payload = _base_payload()
    result = qualify_external_memory_candidate(payload)

    passed = (
        result.record["decision"] == "persist_candidate"
        and result.record["adjusted_weight"] == 70.0
    )
    return {"case": "case_01_valid_persist_candidate", "status": "passed" if passed else "failed"}


def case_02_valid_hold_candidate() -> dict:
    payload = _base_payload()
    payload["source_quality_weight"] = 28
    payload["signal_quality_weight"] = 12
    payload["domain_relevance_weight"] = 10
    payload["persistence_value_weight"] = 8
    payload["contamination_penalty"] = 4

    result = qualify_external_memory_candidate(payload)

    passed = result.record["decision"] == "hold"
    return {"case": "case_02_valid_hold_candidate", "status": "passed" if passed else "failed"}


def case_03_reject_source_quality_below_floor() -> dict:
    payload = _base_payload()
    payload["source_quality_weight"] = 20

    result = qualify_external_memory_candidate(payload)

    passed = result.record["decision"] == "reject"
    return {"case": "case_03_reject_source_quality_below_floor", "status": "passed" if passed else "failed"}


def case_04_reject_blocked_trust_class() -> dict:
    payload = _base_payload()
    payload["trust_class"] = "blocked"

    result = qualify_external_memory_candidate(payload)

    passed = result.record["decision"] == "reject"
    return {"case": "case_04_reject_blocked_trust_class", "status": "passed" if passed else "failed"}


def case_05_reject_missing_required_fields() -> dict:
    payload = _base_payload()
    payload.pop("payload")

    result = qualify_external_memory_candidate(payload)

    passed = result.record["decision"] == "reject"
    return {"case": "case_05_reject_missing_required_fields", "status": "passed" if passed else "failed"}


def case_06_reject_invalid_artifact_type() -> dict:
    payload = _base_payload()
    payload["artifact_type"] = "invalid_type"

    result = qualify_external_memory_candidate(payload)

    passed = result.record["decision"] == "reject"
    return {"case": "case_06_reject_invalid_artifact_type", "status": "passed" if passed else "failed"}


def run_probe():
    cases = [
        case_01_valid_persist_candidate(),
        case_02_valid_hold_candidate(),
        case_03_reject_source_quality_below_floor(),
        case_04_reject_blocked_trust_class(),
        case_05_reject_missing_required_fields(),
        case_06_reject_invalid_artifact_type(),
    ]

    passed = sum(1 for c in cases if c["status"] == "passed")
    failed = len(cases) - passed

    return {"passed": passed, "failed": failed, "results": cases}


if __name__ == "__main__":
    print(run_probe())