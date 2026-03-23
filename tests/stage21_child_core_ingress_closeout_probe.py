from __future__ import annotations

from typing import Any, Dict, List, Mapping

from child_cores.ingress.child_core_ingress import handoff_dispatch_to_ingress
from child_cores.ingress.ingress_state import IngressState


def build_valid_dispatch_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "dispatch_packet",
        "dispatch_id": "DISPATCH-TEST-001",
        "source_decision_id": "PM-DECISION-TEST-001",
        "dispatch_intent": "route_to_proposal_builder",
        "target_core": "contractor_proposals_core",
        "destination_surface": "execution.ingress_processor",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-001"],
        "timestamp": "2026-03-18T00:00:00Z",
    }


def build_unknown_target_dispatch_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "dispatch_packet",
        "dispatch_id": "DISPATCH-TEST-002",
        "source_decision_id": "PM-DECISION-TEST-002",
        "dispatch_intent": "route_to_unknown_core",
        "target_core": "unknown_core",
        "destination_surface": "execution.ingress_processor",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-002"],
        "timestamp": "2026-03-18T00:00:00Z",
    }


def build_surface_mismatch_dispatch_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "dispatch_packet",
        "dispatch_id": "DISPATCH-TEST-003",
        "source_decision_id": "PM-DECISION-TEST-003",
        "dispatch_intent": "route_to_gis_core",
        "target_core": "louisville_gis_core",
        "destination_surface": "execution.wrong_surface",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-003"],
        "timestamp": "2026-03-18T00:00:00Z",
    }


def build_missing_handler_dispatch_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "dispatch_packet",
        "dispatch_id": "DISPATCH-TEST-004",
        "source_decision_id": "PM-DECISION-TEST-004",
        "dispatch_intent": "route_to_gis_core",
        "target_core": "louisville_gis_core",
        "destination_surface": "execution.ingress_processor",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-004"],
        "timestamp": "2026-03-18T00:00:00Z",
    }


def run_stage21_closeout_probe() -> Dict[str, Any]:
    valid_child_cores: List[str] = [
        "contractor_proposals_core",
        "louisville_gis_core",
    ]

    destination_surface_map: Mapping[str, str] = {
        "contractor_proposals_core": "execution.ingress_processor",
        "louisville_gis_core": "execution.ingress_processor",
    }

    handler_calls: List[Dict[str, Any]] = []

    def contractor_handler(dispatch_packet: Dict[str, Any]) -> None:
        handler_calls.append(
            {
                "target_core": dispatch_packet["target_core"],
                "dispatch_id": dispatch_packet["dispatch_id"],
            }
        )

    ingress_handler_map = {
        "contractor_proposals_core": contractor_handler,
        # intentionally omit louisville_gis_core for negative test
    }

    state = IngressState()
    results: Dict[str, Any] = {}

    # TEST 1: Valid ingress handoff
    packet1 = build_valid_dispatch_packet()
    result1 = handoff_dispatch_to_ingress(
        dispatch_packet=packet1,
        valid_child_core_ids=valid_child_cores,
        destination_surface_map=destination_surface_map,
        ingress_handler_map=ingress_handler_map,
        state=state,
    )
    results["test_valid_ingress_handoff"] = {
        "passed": result1.get("artifact_type") == "ingress_receipt"
        and result1.get("target_core") == "contractor_proposals_core"
        and result1.get("destination_surface") == "execution.ingress_processor"
        and len(handler_calls) == 1
        and handler_calls[0]["dispatch_id"] == "DISPATCH-TEST-001",
        "artifact": result1,
    }

    # TEST 2: Unknown target fails
    packet2 = build_unknown_target_dispatch_packet()
    result2 = handoff_dispatch_to_ingress(
        dispatch_packet=packet2,
        valid_child_core_ids=valid_child_cores,
        destination_surface_map=destination_surface_map,
        ingress_handler_map=ingress_handler_map,
        state=state,
    )
    results["test_unknown_target_fails"] = {
        "passed": result2.get("artifact_type") == "ingress_failure_receipt"
        and result2.get("reason") == "unknown_target_core",
        "artifact": result2,
    }

    # TEST 3: Destination surface mismatch fails
    packet3 = build_surface_mismatch_dispatch_packet()
    result3 = handoff_dispatch_to_ingress(
        dispatch_packet=packet3,
        valid_child_core_ids=valid_child_cores,
        destination_surface_map=destination_surface_map,
        ingress_handler_map=ingress_handler_map,
        state=state,
    )
    results["test_destination_surface_mismatch_fails"] = {
        "passed": result3.get("artifact_type") == "ingress_failure_receipt"
        and result3.get("reason") == "destination_surface_target_mismatch",
        "artifact": result3,
    }

    # TEST 4: Missing ingress handler fails
    packet4 = build_missing_handler_dispatch_packet()
    result4 = handoff_dispatch_to_ingress(
        dispatch_packet=packet4,
        valid_child_core_ids=valid_child_cores,
        destination_surface_map=destination_surface_map,
        ingress_handler_map=ingress_handler_map,
        state=state,
    )
    results["test_missing_ingress_handler_fails"] = {
        "passed": result4.get("artifact_type") == "ingress_failure_receipt"
        and result4.get("reason") == "missing_ingress_handler",
        "artifact": result4,
    }

    # TEST 5: No domain execution leakage
    execution_leak_keys = [
        "execution_result",
        "runtime_result",
        "child_core_output",
        "final_output",
    ]
    execution_leak = any(key in result1 for key in execution_leak_keys)
    results["test_no_domain_execution_leakage"] = {
        "passed": execution_leak is False
    }

    # TEST 6: Exact minimal state shape
    results["test_state_minimal_exact"] = {
        "passed": set(vars(state).keys()) == {
            "last_ingress_id",
            "last_target_core",
            "last_timestamp",
        }
    }

    return {
        "stage": "STAGE_21_CLOSEOUT",
        "status": "complete",
        "results": results,
    }


if __name__ == "__main__":
    output = run_stage21_closeout_probe()
    import json
    print(json.dumps(output, indent=2))