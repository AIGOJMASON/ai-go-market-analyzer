from __future__ import annotations

from copy import deepcopy

from AI_GO.EXTERNAL_MEMORY.output_merge.output_merge_runtime import (
    merge_external_memory_into_operator_output,
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


def _valid_return_packet() -> dict:
    return {
        "artifact_type": "external_memory_return_packet",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
        "promotion_score": 140.4,
        "record_count": 10,
        "advisory_summary": {
            "state": "present",
            "summary": "Historical memory context supports bounded advisory reinforcement.",
        },
        "memory_context_panel": {
            "state": "present",
            "items": [
                {
                    "symbol": "XLE",
                    "event_theme": "energy_rebound",
                    "confidence_posture": "medium",
                }
            ],
        },
        "provenance_refs": [
            {
                "record_id": "external_memory_ingress_probe-A-002_b7b8f14a65c6",
                "source_type": "child_core_output",
            }
        ],
    }


def _valid_return_receipt() -> dict:
    return {
        "artifact_type": "external_memory_return_receipt",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
    }


def case_01_output_merge_adds_advisory_surfaces_safely() -> dict:
    operator_response = _base_operator_response()
    original_recommendation_panel = deepcopy(operator_response["recommendation_panel"])

    result = merge_external_memory_into_operator_output(
        operator_response=operator_response,
        return_packet=_valid_return_packet(),
        return_receipt=_valid_return_receipt(),
    )

    merged = result.get("merged_response")
    receipt = result.get("receipt", {})

    passed = (
        result.get("status") == "ok"
        and isinstance(merged, dict)
        and receipt.get("artifact_type") == "external_memory_output_merge_receipt"
        and merged.get("external_memory_merge_status") == "merged"
        and merged.get("external_memory_return_panel", {}).get("state") == "present"
        and merged.get("cognition_panel", {}).get("external_memory_advisory", {}).get("state") == "present"
        and merged.get("recommendation_panel") == original_recommendation_panel
    )
    return {
        "case": "case_01_output_merge_adds_advisory_surfaces_safely",
        "status": "passed" if passed else "failed",
        "details": {
            "merge_status": merged.get("external_memory_merge_status") if isinstance(merged, dict) else None,
            "advisory_state": (
                merged.get("cognition_panel", {})
                .get("external_memory_advisory", {})
                .get("state")
                if isinstance(merged, dict)
                else None
            ),
            "recommendation_unchanged": (
                merged.get("recommendation_panel") == original_recommendation_panel
                if isinstance(merged, dict)
                else False
            ),
        },
    }


def case_02_output_merge_rejects_invalid_return_packet_type() -> dict:
    operator_response = _base_operator_response()
    bad_packet = {
        "artifact_type": "bad_type",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
    }
    good_receipt = _valid_return_receipt()

    result = merge_external_memory_into_operator_output(
        operator_response=operator_response,
        return_packet=bad_packet,
        return_receipt=good_receipt,
    )
    rej = result.get("receipt", {})

    passed = (
        result.get("status") == "failed"
        and rej.get("artifact_type") == "external_memory_output_merge_rejection_receipt"
        and rej.get("failure_reason") == "invalid_return_packet_type"
    )
    return {
        "case": "case_02_output_merge_rejects_invalid_return_packet_type",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result.get("status"),
            "failure_reason": rej.get("failure_reason"),
        },
    }


def case_03_output_merge_rejects_misaligned_return_inputs() -> dict:
    operator_response = _base_operator_response()
    packet = _valid_return_packet()
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
    rej = result.get("receipt", {})

    passed = (
        result.get("status") == "failed"
        and rej.get("artifact_type") == "external_memory_output_merge_rejection_receipt"
        and rej.get("failure_reason") == "artifact_receipt_misalignment"
    )
    return {
        "case": "case_03_output_merge_rejects_misaligned_return_inputs",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result.get("status"),
            "failure_reason": rej.get("failure_reason"),
        },
    }


def case_04_output_merge_rejects_non_dict_operator_response() -> dict:
    result = merge_external_memory_into_operator_output(
        operator_response=[],
        return_packet=_valid_return_packet(),
        return_receipt=_valid_return_receipt(),
    )
    rej = result.get("receipt", {})

    passed = (
        result.get("status") == "failed"
        and rej.get("artifact_type") == "external_memory_output_merge_rejection_receipt"
        and rej.get("failure_reason") == "invalid_operator_response"
    )
    return {
        "case": "case_04_output_merge_rejects_non_dict_operator_response",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result.get("status"),
            "failure_reason": rej.get("failure_reason"),
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