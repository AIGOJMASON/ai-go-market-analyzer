from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.EXTERNAL_MEMORY.promotion.promotion_runtime import (
    run_external_memory_promotion,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.promotion_path import (
    run_market_analyzer_external_memory_promotion,
)


def _record(
    *,
    memory_id: str,
    adjusted_weight: float = 100.0,
    trust_class: str = "verified",
    symbol: str = "XLE",
    sector: str = "energy",
) -> Dict[str, Any]:
    return {
        "memory_id": memory_id,
        "qualification_record_id": f"qual-{memory_id}",
        "source_type": "verified_api",
        "trust_class": trust_class,
        "source_quality_weight": 50.0,
        "signal_quality_weight": 20.0,
        "domain_relevance_weight": 20.0,
        "persistence_value_weight": 20.0,
        "contamination_penalty": 0.0,
        "redundancy_penalty": 0.0,
        "adjusted_weight": adjusted_weight,
        "target_child_cores": ["market_analyzer_v1"],
        "provenance": {"source": "probe"},
        "payload_summary": {
            "request_id": f"request-{memory_id}",
            "headline": "Verified energy signal",
            "summary": "Probe memory record.",
            "symbol": symbol,
            "sector": sector,
            "event_theme": "energy_rebound",
            "confirmation": "confirmed",
            "macro_bias": "constructive",
        },
        "created_at": "2026-05-01T00:00:00Z",
    }


def _artifact(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "artifact_type": "external_memory_retrieval_artifact",
        "artifact_version": "v5F.2",
        "status": "ok",
        "retrieval_mode": "read_only",
        "request_summary": {
            "requester_profile": "market_analyzer_reader",
            "target_child_core": "market_analyzer_v1",
            "limit": 10,
            "symbol": "XLE",
        },
        "matched_count": len(records),
        "returned_count": len(records),
        "records": records,
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "read_only_to_authority_chain": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_state": False,
        },
        "sealed": True,
    }


def _receipt(returned_count: int) -> Dict[str, Any]:
    return {
        "artifact_type": "external_memory_retrieval_receipt",
        "artifact_version": "v5F.2",
        "status": "ok",
        "receipt_id": "extmemread-probe",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
        "limit": 10,
        "matched_count": returned_count,
        "returned_count": returned_count,
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "read_only_to_authority_chain": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_state": False,
        },
        "sealed": True,
    }


def test_promotes_only_as_advisory_signal() -> None:
    records = [
        _record(memory_id="001"),
        _record(memory_id="002"),
        _record(memory_id="003"),
    ]

    result = run_external_memory_promotion(
        artifact=_artifact(records),
        receipt=_receipt(len(records)),
    )

    artifact = result["promotion_artifact"]

    assert result["status"] == "ok"
    assert artifact["promotion_decision"] == "promoted"
    assert artifact["reusable_advisory_signal"] is True
    assert artifact["authority"]["memory_is_truth"] is False
    assert artifact["authority"]["memory_is_candidate_signal"] is True
    assert artifact["authority"]["can_override_state_authority"] is False
    assert artifact["authority"]["can_override_canon"] is False
    assert artifact["authority"]["can_override_watcher"] is False
    assert artifact["authority"]["can_override_execution_gate"] is False
    assert artifact["authority"]["can_execute"] is False
    assert artifact["authority"]["can_mutate_runtime"] is False
    assert artifact["authority"]["can_mutate_state"] is False
    assert artifact["promotion_use_limits"]["may_feed_system_brain"] is True
    assert artifact["promotion_use_limits"]["may_change_recommendation"] is False
    assert artifact["memory_authority_guard"]["allowed"] is True


def test_blocks_missing_or_misaligned_retrieval_receipt() -> None:
    records = [_record(memory_id="001")]

    bad_receipt = _receipt(len(records))
    bad_receipt["target_child_core"] = "contractor_builder_v1"

    result = run_external_memory_promotion(
        artifact=_artifact(records),
        receipt=bad_receipt,
    )

    assert result["status"] == "rejected"
    assert result["failure_reason"] == "artifact_receipt_misalignment"
    assert result["promotion_artifact"]["authority"]["memory_is_truth"] is False
    assert result["promotion_artifact"]["authority"]["can_execute"] is False
    assert result["promotion_artifact"]["memory_authority_guard"]["allowed"] is True


def test_blocks_blocked_trust_class() -> None:
    records = [_record(memory_id="001", trust_class="blocked")]

    result = run_external_memory_promotion(
        artifact=_artifact(records),
        receipt=_receipt(len(records)),
    )

    assert result["status"] == "rejected"
    assert result["failure_reason"] == "blocked_trust_class_present"
    assert result["promotion_artifact"]["authority"]["memory_is_truth"] is False
    assert result["promotion_artifact"]["authority"]["can_mutate_state"] is False


def test_market_analyzer_promotion_path_is_advisory_only() -> None:
    records = [
        _record(memory_id="001"),
        _record(memory_id="002"),
        _record(memory_id="003"),
    ]

    result = run_market_analyzer_external_memory_promotion(
        retrieval_artifact=_artifact(records),
        retrieval_receipt=_receipt(len(records)),
    )

    panel = result["external_memory_promotion_panel"]

    assert result["status"] == "ok"
    assert panel["mode"] == "promotion_advisory"
    assert panel["advisory_only"] is True
    assert result["authority"]["memory_is_truth"] is False
    assert result["authority"]["can_execute"] is False
    assert result["authority"]["can_mutate_runtime"] is False
    assert result["authority"]["can_mutate_state"] is False


def run_probe() -> dict:
    test_promotes_only_as_advisory_signal()
    test_blocks_missing_or_misaligned_retrieval_receipt()
    test_blocks_blocked_trust_class()
    test_market_analyzer_promotion_path_is_advisory_only()

    return {
        "status": "passed",
        "phase": "Phase 5F.3",
        "layer": "external_memory_promotion_hardening",
        "promotion_requires_lawful_retrieval_pair": True,
        "blocked_trust_class_rejected": True,
        "promotion_advisory_only": True,
        "market_analyzer_promotion_path_advisory_only": True,
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_state": False,
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5F3_EXTERNAL_MEMORY_PROMOTION_HARDENING_PROBE: PASS")
    print(result)