from __future__ import annotations

from typing import Any, Dict, List

import AI_GO.EXTERNAL_MEMORY.retrieval.retrieval_runtime as retrieval_runtime

from AI_GO.EXTERNAL_MEMORY.authority.memory_authority_guard import (
    evaluate_memory_authority,
)
from AI_GO.EXTERNAL_MEMORY.retrieval.read_only_context import (
    build_external_memory_read_only_context,
)
from AI_GO.EXTERNAL_MEMORY.promotion.promotion_runtime import (
    run_external_memory_promotion,
)
from AI_GO.core.system_brain.system_brain import (
    build_system_brain_context,
    summarize_system_brain_context,
)
from AI_GO.core.awareness.operator_system_brain_surface import (
    build_operator_system_brain_surface,
)


def _fake_records() -> List[Dict[str, Any]]:
    return [
        {
            "memory_id": "memory-5f5-001",
            "qualification_record_id": "qual-5f5-001",
            "source_type": "verified_api",
            "trust_class": "verified",
            "source_quality_weight": 50.0,
            "signal_quality_weight": 20.0,
            "domain_relevance_weight": 20.0,
            "persistence_value_weight": 20.0,
            "contamination_penalty": 0.0,
            "redundancy_penalty": 0.0,
            "adjusted_weight": 100.0,
            "target_child_cores": ["market_analyzer_v1"],
            "provenance": {"source": "stage_5f5_probe"},
            "payload": {
                "request_id": "stage-5f5-001",
                "headline": "Verified energy signal one",
                "summary": "Full chain regression record one.",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "confirmation": "confirmed",
                "macro_bias": "constructive",
            },
            "created_at": "2026-05-01T00:00:00Z",
        },
        {
            "memory_id": "memory-5f5-002",
            "qualification_record_id": "qual-5f5-002",
            "source_type": "verified_api",
            "trust_class": "verified",
            "source_quality_weight": 50.0,
            "signal_quality_weight": 20.0,
            "domain_relevance_weight": 20.0,
            "persistence_value_weight": 20.0,
            "contamination_penalty": 0.0,
            "redundancy_penalty": 0.0,
            "adjusted_weight": 100.0,
            "target_child_cores": ["market_analyzer_v1"],
            "provenance": {"source": "stage_5f5_probe"},
            "payload": {
                "request_id": "stage-5f5-002",
                "headline": "Verified energy signal two",
                "summary": "Full chain regression record two.",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "confirmation": "confirmed",
                "macro_bias": "constructive",
            },
            "created_at": "2026-05-01T00:01:00Z",
        },
        {
            "memory_id": "memory-5f5-003",
            "qualification_record_id": "qual-5f5-003",
            "source_type": "verified_api",
            "trust_class": "verified",
            "source_quality_weight": 50.0,
            "signal_quality_weight": 20.0,
            "domain_relevance_weight": 20.0,
            "persistence_value_weight": 20.0,
            "contamination_penalty": 0.0,
            "redundancy_penalty": 0.0,
            "adjusted_weight": 100.0,
            "target_child_cores": ["market_analyzer_v1"],
            "provenance": {"source": "stage_5f5_probe"},
            "payload": {
                "request_id": "stage-5f5-003",
                "headline": "Verified energy signal three",
                "summary": "Full chain regression record three.",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "confirmation": "confirmed",
                "macro_bias": "constructive",
            },
            "created_at": "2026-05-01T00:02:00Z",
        },
    ]


def _patch_query() -> None:
    def fake_query_external_memory_records(**kwargs: Any) -> List[Dict[str, Any]]:
        assert kwargs["target_core_id"] == "market_analyzer_v1"
        assert kwargs["symbol"] == "XLE"
        assert kwargs["limit"] == 5
        return _fake_records()

    retrieval_runtime.query_external_memory_records = fake_query_external_memory_records


def _assert_no_authority(authority: Dict[str, Any]) -> None:
    assert authority.get("memory_is_truth") is False
    assert authority.get("memory_is_candidate_signal", True) is True
    assert authority.get("can_override_state_authority") is False
    assert authority.get("can_override_canon") is False
    assert authority.get("can_override_watcher") is False
    assert authority.get("can_override_execution_gate") is False
    assert authority.get("can_execute") is False
    assert authority.get("can_mutate_runtime") is False
    assert authority.get("can_mutate_state") is False


def test_full_external_memory_chain_remains_advisory_only() -> None:
    _patch_query()

    retrieval_context = build_external_memory_read_only_context(
        {
            "artifact_type": "external_memory_retrieval_request",
            "requester_profile": "market_analyzer_reader",
            "target_child_core": "market_analyzer_v1",
            "limit": 5,
            "symbol": "XLE",
        }
    )

    assert retrieval_context["status"] == "ok"
    assert retrieval_context["returned_count"] == 3
    assert retrieval_context["memory_authority_guard"]["allowed"] is True
    _assert_no_authority(retrieval_context["authority"])

    retrieval_artifact = {
        "artifact_type": "external_memory_retrieval_artifact",
        "artifact_version": "v5F.2",
        "status": "ok",
        "retrieval_mode": "read_only",
        "request_summary": retrieval_context["request_summary"],
        "matched_count": retrieval_context["matched_count"],
        "returned_count": retrieval_context["returned_count"],
        "records": retrieval_context["records"],
        "authority": retrieval_context["authority"],
        "sealed": True,
    }

    retrieval_receipt = {
        "artifact_type": "external_memory_retrieval_receipt",
        "artifact_version": "v5F.2",
        "status": "ok",
        "receipt_id": retrieval_context["retrieval_receipt_id"] or "extmemread-5f5",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
        "limit": 5,
        "matched_count": retrieval_context["matched_count"],
        "returned_count": retrieval_context["returned_count"],
        "authority": retrieval_context["authority"],
        "sealed": True,
    }

    promotion_result = run_external_memory_promotion(
        artifact=retrieval_artifact,
        receipt=retrieval_receipt,
    )

    assert promotion_result["status"] == "ok"
    promotion_artifact = promotion_result["promotion_artifact"]
    assert promotion_artifact["promotion_decision"] == "promoted"
    assert promotion_artifact["reusable_advisory_signal"] is True
    assert promotion_artifact["memory_authority_guard"]["allowed"] is True
    _assert_no_authority(promotion_artifact["authority"])

    system_brain_context = build_system_brain_context(
        external_memory_context=retrieval_context,
        external_memory_promotion=promotion_artifact,
    )

    assert system_brain_context["artifact_type"] == "system_brain_context"
    assert system_brain_context["mode"] == "read_only"
    assert system_brain_context["authority"]["read_only"] is True
    assert system_brain_context["authority"]["advisory_only"] is True
    assert system_brain_context["authority"]["can_execute"] is False
    assert system_brain_context["authority"]["can_mutate_state"] is False
    assert system_brain_context["authority"]["can_mutate_runtime"] is False
    assert system_brain_context["authority"]["can_override_state_authority"] is False
    assert system_brain_context["authority"]["can_override_canon"] is False
    assert system_brain_context["authority"]["can_override_watcher"] is False
    assert system_brain_context["authority"]["can_override_execution_gate"] is False
    assert system_brain_context["authority"]["can_block_request"] is False
    assert system_brain_context["authority"]["can_allow_request"] is False
    assert system_brain_context["use_policy"]["may_change_recommendations"] is False
    assert system_brain_context["use_policy"]["may_change_pm_strategy"] is False
    assert system_brain_context["use_policy"]["may_dispatch_actions"] is False

    external_memory_panel = system_brain_context["external_memory"]
    assert external_memory_panel["pattern_context_available"] is True
    assert external_memory_panel["pattern_strength"] == "strong"
    assert external_memory_panel["authority"]["memory_is_truth"] is False
    assert external_memory_panel["authority"]["can_execute"] is False
    assert external_memory_panel["authority"]["can_mutate_state"] is False

    summary = summarize_system_brain_context(system_brain_context)

    assert summary["artifact_type"] == "system_brain_summary"
    assert summary["mode"] == "read_only"
    assert summary["external_memory"]["pattern_strength"] == "strong"
    assert summary["external_memory"]["pattern_context_available"] is True
    assert summary["authority"]["can_execute"] is False
    assert summary["authority"]["can_mutate_state"] is False


def test_illegal_memory_truth_claim_is_blocked_before_authority() -> None:
    illegal_artifact = {
        "artifact_type": "external_memory_promotion_artifact",
        "authority": {
            "memory_is_truth": True,
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
    }

    decision = evaluate_memory_authority(illegal_artifact)

    assert decision["allowed"] is False
    assert decision["status"] == "blocked"

    codes = {error["code"] for error in decision["errors"]}
    assert "memory_authority_claim_must_be_false:memory_is_truth" in codes
    assert "forbidden_memory_authority_claim:memory_is_truth" in codes


def test_promotion_rejects_misaligned_receipt_end_to_end() -> None:
    _patch_query()

    retrieval_context = build_external_memory_read_only_context(
        {
            "artifact_type": "external_memory_retrieval_request",
            "requester_profile": "market_analyzer_reader",
            "target_child_core": "market_analyzer_v1",
            "limit": 5,
            "symbol": "XLE",
        }
    )

    retrieval_artifact = {
        "artifact_type": "external_memory_retrieval_artifact",
        "artifact_version": "v5F.2",
        "status": "ok",
        "retrieval_mode": "read_only",
        "request_summary": retrieval_context["request_summary"],
        "matched_count": retrieval_context["matched_count"],
        "returned_count": retrieval_context["returned_count"],
        "records": retrieval_context["records"],
        "authority": retrieval_context["authority"],
        "sealed": True,
    }

    bad_receipt = {
        "artifact_type": "external_memory_retrieval_receipt",
        "artifact_version": "v5F.2",
        "status": "ok",
        "receipt_id": "extmemread-bad-5f5",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "contractor_builder_v1",
        "limit": 5,
        "matched_count": retrieval_context["matched_count"],
        "returned_count": retrieval_context["returned_count"],
        "authority": retrieval_context["authority"],
        "sealed": True,
    }

    promotion_result = run_external_memory_promotion(
        artifact=retrieval_artifact,
        receipt=bad_receipt,
    )

    assert promotion_result["status"] == "rejected"
    assert promotion_result["failure_reason"] == "artifact_receipt_misalignment"

    rejected_artifact = promotion_result["promotion_artifact"]
    assert rejected_artifact["authority"]["memory_is_truth"] is False
    assert rejected_artifact["authority"]["can_execute"] is False
    assert rejected_artifact["authority"]["can_mutate_state"] is False
    assert rejected_artifact["memory_authority_guard"]["allowed"] is True


def test_operator_surface_still_has_no_execution_authority() -> None:
    surface = build_operator_system_brain_surface(limit=10)

    assert surface["artifact_type"] == "operator_system_brain_surface"
    assert surface["mode"] == "operator_read_only_surface"
    assert surface["sealed"] is True

    assert surface["authority"]["read_only"] is True
    assert surface["authority"]["advisory_only"] is True
    assert surface["authority"]["can_execute"] is False
    assert surface["authority"]["can_mutate_state"] is False
    assert surface["authority"]["can_mutate_runtime"] is False
    assert surface["authority"]["can_override_governance"] is False
    assert surface["authority"]["can_override_state_authority"] is False
    assert surface["authority"]["can_override_canon"] is False
    assert surface["authority"]["can_override_watcher"] is False
    assert surface["authority"]["can_override_execution_gate"] is False
    assert surface["authority"]["execution_allowed"] is False
    assert surface["authority"]["mutation_allowed"] is False

    assert "external_memory_panel" in surface
    assert surface["external_memory_panel"]["advisory_only"] is True
    assert surface["use_policy"]["may_change_recommendations"] is False
    assert surface["use_policy"]["may_change_pm_strategy"] is False
    assert surface["use_policy"]["may_dispatch_actions"] is False


def run_probe() -> dict:
    test_full_external_memory_chain_remains_advisory_only()
    test_illegal_memory_truth_claim_is_blocked_before_authority()
    test_promotion_rejects_misaligned_receipt_end_to_end()
    test_operator_surface_still_has_no_execution_authority()

    return {
        "status": "passed",
        "phase": "Phase 5F.5",
        "layer": "full_external_memory_regression_probe",
        "authority_guard_confirmed": True,
        "retrieval_read_only_confirmed": True,
        "promotion_advisory_only_confirmed": True,
        "misaligned_receipt_rejected": True,
        "system_brain_advisory_only_confirmed": True,
        "operator_surface_no_execution_authority": True,
        "northstar_memory_law": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "external_memory_can_override_state_authority": False,
            "external_memory_can_override_canon": False,
            "external_memory_can_override_watcher": False,
            "external_memory_can_override_execution_gate": False,
            "external_memory_can_execute": False,
            "external_memory_can_mutate_state": False,
            "external_memory_can_mutate_runtime": False,
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5F5_FULL_EXTERNAL_MEMORY_REGRESSION_PROBE: PASS")
    print(result)