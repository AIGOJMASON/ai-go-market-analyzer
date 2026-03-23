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


def _build_market_analyzer_fusion_record() -> dict:
    return {
        "artifact_type": "execution_fusion_record",
        "sealed": True,
        "fusion_id": "EFR-STAGE76-001",
        "runtime_mode": {
            "mode": "runtime_refined",
        },
        "combined_weights": {
            "combined_weight": 0.82,
            "rosetta_weight": 0.79,
            "curved_mirror_weight": 0.85,
        },
        "child_core_handoff": "child_core_ready",
        "receipt": {
            "receipt_type": "execution_fusion_receipt",
            "fusion_id": "EFR-STAGE76-001",
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
                    "event_id": "STAGE76-EVT-001",
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

    case_01_pass = isinstance(adapter_packet, dict)
    results.append(
        {
            "case": "case_01_valid_child_core_adapter_packet_dict",
            "status": "passed" if case_01_pass else "failed",
        }
    )

    case_02_pass = (
        adapter_packet.get("artifact_type") == "child_core_adapter_packet"
        and adapter_packet.get("sealed") is True
    )
    results.append(
        {
            "case": "case_02_valid_adapter_packet_artifact_type_and_sealed",
            "status": "passed" if case_02_pass else "failed",
        }
    )

    case_03_pass = (
        adapter_packet.get("source_artifact_type") == "child_core_execution_result"
        and adapter_packet.get("target_core") == "market_analyzer_v1"
        and adapter_packet.get("adapter_class") == "market_analyzer_adapter"
        and adapter_packet.get("target_surface_class") == "market_analyzer_surface"
    )
    results.append(
        {
            "case": "case_03_target_core_and_adapter_classes_resolved",
            "status": "passed" if case_03_pass else "failed",
        }
    )

    source_lineage = adapter_packet.get("source_lineage", {})
    case_04_pass = (
        isinstance(source_lineage, dict)
        and source_lineage.get("result_id") == execution_result.get("result_id")
    )
    results.append(
        {
            "case": "case_04_source_lineage_preserved_from_execution_result",
            "status": "passed" if case_04_pass else "failed",
        }
    )

    case_05_pass = (
        adapter_packet.get("adapter_status") == "adapted"
        and adapter_packet.get("downstream_status") == "ready_for_target_surface"
        and adapter_packet.get("runtime_error") is None
    )
    results.append(
        {
            "case": "case_05_successful_execution_result_adapts_cleanly",
            "status": "passed" if case_05_pass else "failed",
        }
    )

    runtime_mode = adapter_packet.get("runtime_mode", {})
    combined_weights = adapter_packet.get("combined_weights", {})
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

    adapter_payload = adapter_packet.get("adapter_payload", {})
    recommendations = adapter_payload.get("recommendations", {})
    approval_gate = adapter_payload.get("approval_gate", {})
    case_07_pass = (
        isinstance(adapter_payload, dict)
        and adapter_payload.get("market_regime", {}).get("regime") in {"volatile", "normal", "crisis"}
        and recommendations.get("recommendation_count", 0) >= 1
        and approval_gate.get("execution_allowed") is False
    )
    results.append(
        {
            "case": "case_07_adapter_payload_contains_market_analyzer_surface_data",
            "status": "passed" if case_07_pass else "failed",
        }
    )

    recommendation_items = recommendations.get("items", [])
    recommendation_symbols = [
        item.get("symbol")
        for item in recommendation_items
        if isinstance(item, dict)
    ]
    case_08_pass = "XLE" in recommendation_symbols
    results.append(
        {
            "case": "case_08_expected_recommendation_symbol_preserved",
            "status": "passed" if case_08_pass else "failed",
        }
    )

    receipt = adapter_packet.get("receipt", {})
    case_09_pass = (
        isinstance(receipt, dict)
        and receipt.get("receipt_type") == "child_core_adapter_surface_receipt"
        and receipt.get("adapter_packet_id") == adapter_packet.get("adapter_packet_id")
    )
    results.append(
        {
            "case": "case_09_receipt_present_and_bound_to_packet",
            "status": "passed" if case_09_pass else "failed",
        }
    )

    recommendations_execution_allowed = recommendations.get("execution_allowed")
    case_10_pass = recommendations_execution_allowed is False
    results.append(
        {
            "case": "case_10_no_execution_authority_introduced_by_adapter_surface",
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