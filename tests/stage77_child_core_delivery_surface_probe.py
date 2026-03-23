from __future__ import annotations

from AI_GO.core.runtime.refinement.child_core_execution_intake import (
    construct_child_core_execution_packet,
)
from AI_GO.core.runtime.refinement.child_core_execution_surface import (
    construct_child_core_execution_result,
)
from AI_GO.core.runtime.refinement.child_core_adapter import (
    construct_child_core_adapter_packet,
)
from AI_GO.core.runtime.refinement.child_core_delivery import (
    construct_child_core_delivery_packet,
)


def _build_market_analyzer_fusion_record() -> dict:
    return {
        "artifact_type": "execution_fusion_record",
        "sealed": True,
        "fusion_id": "EFR-STAGE77-001",
        "runtime_mode": {
            "mode": "runtime_refined",
        },
        "combined_weights": {
            "combined_weight": 0.84,
            "rosetta_weight": 0.81,
            "curved_mirror_weight": 0.87,
        },
        "child_core_handoff": "child_core_ready",
        "receipt": {
            "receipt_type": "execution_fusion_receipt",
            "fusion_id": "EFR-STAGE77-001",
        },
        "child_core_payloads": {
            "market_analyzer_v1": {
                "conditioning": {
                    "holding_window_hours": 24,
                    "liquidity_preference": "high",
                },
                "market_context": {
                    "volatility_level": "high",
                    "liquidity_level": "high",
                    "stress_level": "high",
                },
                "event": {
                    "event_id": "STAGE77-EVT-001",
                    "event_type": "supply_shock",
                    "propagation_speed": "fast",
                    "ripple_depth": "primary",
                    "shock_confirmed": True,
                },
                "macro_bias": {
                    "direction": "neutral",
                },
                "candidates": [
                    {
                        "symbol": "XLE",
                        "sector": "energy",
                        "liquidity": "high",
                        "stabilization": True,
                        "reclaim": True,
                        "confirmation": True,
                        "entry_signal": "confirmation_reclaim",
                        "exit_rule": "quick_exit_on_rebound_completion",
                        "time_horizon_hours": 24,
                    },
                    {
                        "symbol": "NTR",
                        "sector": "fertilizer",
                        "liquidity": "medium",
                        "stabilization": True,
                        "reclaim": True,
                        "confirmation": True,
                        "entry_signal": "confirmation_reclaim",
                        "exit_rule": "quick_exit_on_rebound_completion",
                        "time_horizon_hours": 24,
                    },
                ],
            }
        },
    }


def run_probe() -> dict:
    results: list[dict] = []

    fusion_record = _build_market_analyzer_fusion_record()
    execution_packet = construct_child_core_execution_packet(
        execution_fusion_record=fusion_record,
        target_core="market_analyzer_v1",
    )
    execution_result = construct_child_core_execution_result(execution_packet)
    adapter_packet = construct_child_core_adapter_packet(execution_result)
    delivery_packet = construct_child_core_delivery_packet(adapter_packet)

    case_01_pass = isinstance(delivery_packet, dict)
    results.append(
        {
            "case": "case_01_valid_child_core_delivery_packet_dict",
            "status": "passed" if case_01_pass else "failed",
        }
    )

    case_02_pass = (
        delivery_packet.get("artifact_type") == "child_core_delivery_packet"
        and delivery_packet.get("sealed") is True
    )
    results.append(
        {
            "case": "case_02_valid_delivery_packet_artifact_type_and_sealed",
            "status": "passed" if case_02_pass else "failed",
        }
    )

    case_03_pass = (
        delivery_packet.get("source_artifact_type") == "child_core_adapter_packet"
        and delivery_packet.get("target_core") == "market_analyzer_v1"
        and delivery_packet.get("delivery_class") == "market_analyzer_delivery"
        and delivery_packet.get("target_surface_class") == "market_analyzer_surface"
    )
    results.append(
        {
            "case": "case_03_target_core_and_delivery_classes_resolved",
            "status": "passed" if case_03_pass else "failed",
        }
    )

    source_lineage = delivery_packet.get("source_lineage", {})
    case_04_pass = (
        isinstance(source_lineage, dict)
        and source_lineage.get("adapter_packet_id") == adapter_packet.get("adapter_packet_id")
    )
    results.append(
        {
            "case": "case_04_source_lineage_preserved_from_adapter_packet",
            "status": "passed" if case_04_pass else "failed",
        }
    )

    case_05_pass = (
        delivery_packet.get("delivery_status") == "delivered"
        and delivery_packet.get("downstream_status") == "ready_for_target_consumer"
        and delivery_packet.get("runtime_error") is None
    )
    results.append(
        {
            "case": "case_05_successful_adapter_packet_delivers_cleanly",
            "status": "passed" if case_05_pass else "failed",
        }
    )

    runtime_mode = delivery_packet.get("runtime_mode", {})
    combined_weights = delivery_packet.get("combined_weights", {})
    case_06_pass = (
        isinstance(runtime_mode, dict)
        and runtime_mode.get("mode") == "runtime_refined"
        and isinstance(combined_weights, dict)
        and set(("combined_weight", "rosetta_weight", "curved_mirror_weight")).issubset(combined_weights.keys())
    )
    results.append(
        {
            "case": "case_06_runtime_mode_and_weights_preserved",
            "status": "passed" if case_06_pass else "failed",
        }
    )

    delivery_payload = delivery_packet.get("delivery_payload", {})
    summary = delivery_payload.get("delivery_summary", {})
    recommendations = delivery_payload.get("recommendations", {})
    approval_gate = delivery_payload.get("approval_gate", {})
    case_07_pass = (
        isinstance(delivery_payload, dict)
        and summary.get("recommendation_count", 0) >= 1
        and "XLE" in summary.get("recommendation_symbols", [])
        and recommendations.get("recommendation_count", 0) >= 1
        and approval_gate.get("execution_allowed") is False
    )
    results.append(
        {
            "case": "case_07_delivery_payload_contains_market_analyzer_delivery_data",
            "status": "passed" if case_07_pass else "failed",
        }
    )

    market_context = delivery_payload.get("market_context", {})
    event_context = delivery_payload.get("event_context", {})
    case_08_pass = (
        market_context.get("regime") in {"volatile", "normal", "crisis"}
        and event_context.get("event_type") == "supply_shock"
        and event_context.get("shock_confirmed") is True
    )
    results.append(
        {
            "case": "case_08_market_and_event_context_preserved",
            "status": "passed" if case_08_pass else "failed",
        }
    )

    receipt = delivery_packet.get("receipt", {})
    case_09_pass = (
        isinstance(receipt, dict)
        and receipt.get("receipt_type") == "child_core_delivery_surface_receipt"
        and receipt.get("delivery_packet_id") == delivery_packet.get("delivery_packet_id")
    )
    results.append(
        {
            "case": "case_09_receipt_present_and_bound_to_packet",
            "status": "passed" if case_09_pass else "failed",
        }
    )

    summary_execution_allowed = summary.get("execution_allowed")
    recommendations_execution_allowed = recommendations.get("execution_allowed")
    case_10_pass = (
        summary_execution_allowed is False
        and recommendations_execution_allowed is False
    )
    results.append(
        {
            "case": "case_10_no_execution_authority_introduced_by_delivery_surface",
            "status": "passed" if case_10_pass else "failed",
        }
    )

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())