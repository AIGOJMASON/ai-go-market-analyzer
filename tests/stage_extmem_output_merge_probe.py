from __future__ import annotations

from copy import deepcopy

from AI_GO.EXTERNAL_MEMORY.output_merge.output_merge_runtime import (
    merge_external_memory_into_operator_output,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.output_merge import (
    merge_market_analyzer_external_memory_output,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.runtime_path import (
    run_market_analyzer_external_memory_path,
)


def _seed_mergeable_records() -> None:
    run_market_analyzer_external_memory_path(
        request_id="seed-merge-001",
        symbol="XLE",
        headline="Confirmed energy disruption event",
        price_change_pct=2.8,
        sector="energy",
        confirmation="confirmed",
        event_theme="energy_rebound",
        macro_bias="neutral",
        route_mode="pm_route",
        source_type="official_filing",
    )
    run_market_analyzer_external_memory_path(
        request_id="seed-merge-002",
        symbol="XLE",
        headline="Confirmed energy production update",
        price_change_pct=2.3,
        sector="energy",
        confirmation="confirmed",
        event_theme="energy_update",
        macro_bias="neutral",
        route_mode="pm_route",
        source_type="official_filing",
    )


def _base_operator_response() -> dict:
    return {
        "status": "ok",
        "request_id": "merge-test-001",
        "route_mode": "pm_route",
        "execution_allowed": False,
        "approval_required": True,
        "case_panel": {
            "case_id": "merge-test-001",
            "title": "Energy rebound after necessity shock",
        },
        "runtime_panel": {
            "market_regime": "normal",
            "event_theme": "energy_rebound",
            "macro_bias": "neutral",
            "headline": "Energy rebound after necessity shock",
        },
        "recommendation_panel": {
            "state": "present",
            "count": 1,
            "items": [
                {
                    "symbol": "XLE",
                    "entry": "reclaim support",
                    "exit": "short-term resistance",
                    "confidence": "medium",
                }
            ],
        },
        "cognition_panel": {
            "state": "present",
            "refinement": {
                "state": "present",
                "summary": "bounded refinement summary",
            },
        },
        "pm_workflow_panel": {
            "state": "present",
            "workflow_state": "planning",
        },
        "governance_panel": {
            "watcher_passed": True,
            "approval_required": True,
        },
    }


def case_01_output_merge_adds_advisory_surfaces_safely() -> dict:
    _seed_mergeable_records()
    operator_response = _base_operator_response()
    original_recommendation_panel = deepcopy(operator_response["recommendation_panel"])

    result = merge_market_analyzer_external_memory_output(
        operator_response=operator_response,
        limit=10,
        requester_profile="market_analyzer_reader",
        symbol="XLE",
        min_adjusted_weight=70,
    )

    merged = result["merged_response"]
    receipt = result["receipt"]

    passed = (
        result["status"] == "ok"
        and merged is not None
        and receipt["artifact_type"] == "external_memory_output_merge_receipt"
        and merged["external_memory_merge_status"] == "merged"
        and merged["external_memory_return_panel"]["state"] == "present"
        and merged["cognition_panel"]["external_memory_advisory"]["state"] == "present"
        and merged["recommendation_panel"] == original_recommendation_panel
    )
    return {
        "case": "case_01_output_merge_adds_advisory_surfaces_safely",
        "status": "passed" if passed else "failed",
        "details": {
            "merge_status": merged["external_memory_merge_status"] if merged else None,
            "advisory_state": merged["cognition_panel"]["external_memory_advisory"]["state"] if merged else None,
            "recommendation_unchanged": merged["recommendation_panel"] == original_recommendation_panel if merged else False,
        },
    }


def case_02_output_merge_rejects_invalid_return_packet_type() -> dict:
    operator_response = _base_operator_response()
    bad_packet = {
        "artifact_type": "bad_type",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
    }
    good_receipt = {
        "artifact_type": "external_memory_return_receipt",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
    }

    result = merge_external_memory_into_operator_output(
        operator_response=operator_response,
        return_packet=bad_packet,
        return_receipt=good_receipt,
    )
    rej = result["receipt"]

    passed = (
        result["status"] == "failed"
        and rej["artifact_type"] == "external_memory_output_merge_rejection_receipt"
        and rej["failure_reason"] == "invalid_return_packet_type"
    )
    return {
        "case": "case_02_output_merge_rejects_invalid_return_packet_type",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result["status"],
            "failure_reason": rej["failure_reason"],
        },
    }


def case_03_output_merge_rejects_misaligned_return_inputs() -> dict:
    operator_response = _base_operator_response()
    packet = {
        "artifact_type": "external_memory_return_packet",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
        "promotion_score": 120.0,
        "record_count": 2,
        "advisory_summary": {
            "state": "present",
        },
        "memory_context_panel": {
            "state": "present",
        },
        "provenance_refs": [],
    }
    receipt = {
        "artifact_type": "external_memory_return_receipt",
        "requester_profile": "operator_reader",
        "target_child_core": "market_analyzer_v1",
    }

    result = merge_external_memory_into_operator_output(
        operator_response=operator_response,
        return_packet=packet,
        return_receipt=receipt,
    )
    rej = result["receipt"]

    passed = (
        result["status"] == "failed"
        and rej["artifact_type"] == "external_memory_output_merge_rejection_receipt"
        and rej["failure_reason"] == "artifact_receipt_misalignment"
    )
    return {
        "case": "case_03_output_merge_rejects_misaligned_return_inputs",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result["status"],
            "failure_reason": rej["failure_reason"],
        },
    }


def case_04_output_merge_rejects_non_dict_operator_response() -> dict:
    packet = {
        "artifact_type": "external_memory_return_packet",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
        "promotion_score": 120.0,
        "record_count": 2,
        "advisory_summary": {
            "state": "present",
        },
        "memory_context_panel": {
            "state": "present",
        },
        "provenance_refs": [],
    }
    receipt = {
        "artifact_type": "external_memory_return_receipt",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
    }

    result = merge_external_memory_into_operator_output(
        operator_response=[],
        return_packet=packet,
        return_receipt=receipt,
    )
    rej = result["receipt"]

    passed = (
        result["status"] == "failed"
        and rej["artifact_type"] == "external_memory_output_merge_rejection_receipt"
        and rej["failure_reason"] == "invalid_operator_response"
    )
    return {
        "case": "case_04_output_merge_rejects_non_dict_operator_response",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result["status"],
            "failure_reason": rej["failure_reason"],
        },
    }


def run_probe() -> dict:
    cases = [
        case_01_output_merge_adds_advisory_surfaces_safely(),
        case_02_output_merge_rejects_invalid_return_packet_type(),
        case_03_output_merge_rejects_misaligned_return_inputs(),
        case_04_output_merge_rejects_non_dict_operator_response(),
    ]
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = len(cases) - passed
    return {"passed": passed, "failed": failed, "results": cases}


if __name__ == "__main__":
    print(run_probe())