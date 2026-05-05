from __future__ import annotations

from typing import Any, Dict, List

import AI_GO.EXTERNAL_MEMORY.retrieval.retrieval_runtime as retrieval_runtime
from AI_GO.EXTERNAL_MEMORY.retrieval.read_only_context import (
    build_external_memory_read_only_context,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.retrieval_path import (
    run_market_analyzer_external_memory_retrieval,
)


def _fake_records() -> List[Dict[str, Any]]:
    return [
        {
            "memory_id": "memory-test-001",
            "qualification_record_id": "qual-test-001",
            "source_type": "verified_api",
            "trust_class": "verified",
            "source_quality_weight": 45.0,
            "signal_quality_weight": 20.0,
            "domain_relevance_weight": 15.0,
            "persistence_value_weight": 15.0,
            "contamination_penalty": 0.0,
            "redundancy_penalty": 0.0,
            "adjusted_weight": 95.0,
            "target_child_cores": ["market_analyzer_v1"],
            "provenance": {"source": "probe"},
            "payload": {
                "request_id": "probe-request-001",
                "headline": "Verified energy signal",
                "summary": "Probe memory record.",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "confirmation": "confirmed",
                "macro_bias": "constructive",
            },
            "created_at": "2026-05-01T00:00:00Z",
        }
    ]


def _patch_query() -> None:
    def fake_query_external_memory_records(**kwargs: Any) -> List[Dict[str, Any]]:
        assert kwargs["target_core_id"] == "market_analyzer_v1"
        assert kwargs["symbol"] == "XLE"
        assert kwargs["limit"] == 5
        return _fake_records()

    retrieval_runtime.query_external_memory_records = fake_query_external_memory_records


def test_read_only_context_returns_guarded_advisory_context() -> None:
    _patch_query()

    context = build_external_memory_read_only_context(
        {
            "artifact_type": "external_memory_retrieval_request",
            "requester_profile": "market_analyzer_reader",
            "target_child_core": "market_analyzer_v1",
            "limit": 5,
            "symbol": "XLE",
        }
    )

    assert context["status"] == "ok"
    assert context["returned_count"] == 1
    assert context["advisory_panel"]["advisory_only"] is True
    assert context["authority"]["memory_is_truth"] is False
    assert context["authority"]["memory_is_candidate_signal"] is True
    assert context["authority"]["can_override_state_authority"] is False
    assert context["authority"]["can_override_canon"] is False
    assert context["authority"]["can_override_watcher"] is False
    assert context["authority"]["can_override_execution_gate"] is False
    assert context["authority"]["can_execute"] is False
    assert context["authority"]["can_mutate_state"] is False
    assert context["memory_authority_guard"]["allowed"] is True


def test_market_analyzer_retrieval_path_is_read_only() -> None:
    _patch_query()

    result = run_market_analyzer_external_memory_retrieval(
        requester_profile="market_analyzer_reader",
        symbol="XLE",
        limit=5,
    )

    assert result["status"] == "ok"
    assert result["external_memory_panel"]["mode"] == "read_only"
    assert result["external_memory_panel"]["advisory_only"] is True
    assert result["authority"]["memory_is_truth"] is False
    assert result["authority"]["can_execute"] is False
    assert result["authority"]["can_mutate_runtime"] is False
    assert result["authority"]["can_mutate_state"] is False


def test_invalid_profile_fails_closed_without_db_query() -> None:
    result = retrieval_runtime.run_external_memory_retrieval(
        {
            "artifact_type": "external_memory_retrieval_request",
            "requester_profile": "unauthorized_reader",
            "target_child_core": "market_analyzer_v1",
            "limit": 5,
        }
    )

    assert result["status"] == "failed"
    assert result["failure_reason"] == "invalid_requester_profile"
    assert result["receipt"]["authority"]["memory_is_truth"] is False
    assert result["receipt"]["authority"]["can_execute"] is False
    assert result["receipt"]["memory_authority_guard"]["allowed"] is True


def run_probe() -> dict:
    test_read_only_context_returns_guarded_advisory_context()
    test_market_analyzer_retrieval_path_is_read_only()
    test_invalid_profile_fails_closed_without_db_query()

    return {
        "status": "passed",
        "phase": "Phase 5F.2",
        "layer": "external_memory_read_only_retrieval_integration",
        "read_only_context_guarded": True,
        "market_analyzer_retrieval_read_only": True,
        "invalid_profile_failed_closed": True,
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
    print("STAGE_5F2_EXTERNAL_MEMORY_READ_ONLY_RETRIEVAL_PROBE: PASS")
    print(result)