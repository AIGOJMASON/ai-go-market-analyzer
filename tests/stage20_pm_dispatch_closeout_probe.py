from __future__ import annotations

from typing import Any, Dict, List, Mapping

from PM_CORE.dispatch.pm_dispatch import handoff_routing_to_dispatch
from PM_CORE.dispatch.dispatch_state import DispatchState


def build_valid_single_target_routing_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "pm_routing_packet",
        "routing_packet_id": "PM-ROUTING-TEST-001",
        "source_decision_id": "PM-DECISION-TEST-001",
        "intent": "route_to_proposal_builder",
        "target_mode": "single",
        "target": "contractor_proposals_core",
        "rationale_summary": "Routing packet is valid and ready for dispatch.",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-001"],
        "timestamp": "2026-03-18T00:00:00Z",
        "routing_readiness": "ready",
    }


def build_candidate_set_routing_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "pm_routing_packet",
        "routing_packet_id": "PM-ROUTING-TEST-002",
        "source_decision_id": "PM-DECISION-TEST-002",
        "intent": "route_to_domain_analysis",
        "target_mode": "candidate_set",
        "candidate_targets": [
            "contractor_proposals_core",
            "louisville_gis_core",
        ],
        "candidate_set_controls": {
            "max_candidates": 3,
            "ranking_required": False,
        },
        "rationale_summary": "Candidate-set routing should not be dispatchable.",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-002"],
        "timestamp": "2026-03-18T00:00:00Z",
        "routing_readiness": "ready",
    }


def build_unknown_target_routing_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "pm_routing_packet",
        "routing_packet_id": "PM-ROUTING-TEST-003",
        "source_decision_id": "PM-DECISION-TEST-003",
        "intent": "route_to_unknown_core",
        "target_mode": "single",
        "target": "unknown_core",
        "rationale_summary": "Unknown target should fail dispatch validation.",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-003"],
        "timestamp": "2026-03-18T00:00:00Z",
        "routing_readiness": "ready",
    }


def build_missing_destination_surface_routing_packet() -> Dict[str, Any]:
    return {
        "artifact_type": "pm_routing_packet",
        "routing_packet_id": "PM-ROUTING-TEST-004",
        "source_decision_id": "PM-DECISION-TEST-004",
        "intent": "route_to_gis_core",
        "target_mode": "single",
        "target": "louisville_gis_core",
        "rationale_summary": "Known target without declared destination surface should fail.",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-004"],
        "timestamp": "2026-03-18T00:00:00Z",
        "routing_readiness": "ready",
    }


def run_stage20_closeout_probe() -> Dict[str, Any]:
    valid_child_cores: List[str] = [
        "contractor_proposals_core",
        "louisville_gis_core",
    ]

    destination_surface_map: Mapping[str, str] = {
        "contractor_proposals_core": "execution.ingress_processor",
        # intentionally omit louisville_gis_core for negative test
    }

    state = DispatchState()
    results: Dict[str, Any] = {}

    # TEST 1: Valid single-target dispatch
    packet1 = build_valid_single_target_routing_packet()
    result1 = handoff_routing_to_dispatch(
        pm_routing_packet=packet1,
        valid_child_core_ids=valid_child_cores,
        destination_surface_map=destination_surface_map,
        state=state,
    )
    results["test_valid_single_target_dispatch"] = {
        "passed": result1.get("artifact_type") == "dispatch_packet"
        and result1.get("target_core") == "contractor_proposals_core"
        and result1.get("destination_surface") == "execution.ingress_processor",
        "artifact": result1,
    }

    # TEST 2: Candidate-set routing must not dispatch
    packet2 = build_candidate_set_routing_packet()
    result2 = handoff_routing_to_dispatch(
        pm_routing_packet=packet2,
        valid_child_core_ids=valid_child_cores,
        destination_surface_map=destination_surface_map,
        state=state,
    )
    results["test_candidate_set_not_dispatchable"] = {
        "passed": result2.get("artifact_type") == "dispatch_failure_receipt"
        and result2.get("reason") == "candidate_set_not_dispatchable",
        "artifact": result2,
    }

    # TEST 3: Unknown target fails
    packet3 = build_unknown_target_routing_packet()
    result3 = handoff_routing_to_dispatch(
        pm_routing_packet=packet3,
        valid_child_core_ids=valid_child_cores,
        destination_surface_map=destination_surface_map,
        state=state,
    )
    results["test_unknown_target_fails"] = {
        "passed": result3.get("artifact_type") == "dispatch_failure_receipt"
        and result3.get("reason") == "unknown_target",
        "artifact": result3,
    }

    # TEST 4: Missing destination surface fails
    packet4 = build_missing_destination_surface_routing_packet()
    result4 = handoff_routing_to_dispatch(
        pm_routing_packet=packet4,
        valid_child_core_ids=valid_child_cores,
        destination_surface_map=destination_surface_map,
        state=state,
    )
    results["test_missing_destination_surface_fails"] = {
        "passed": result4.get("artifact_type") == "dispatch_failure_receipt"
        and result4.get("reason") == "missing_destination_surface",
        "artifact": result4,
    }

    # TEST 5: No child-core execution leakage
    execution_leak_keys = [
        "execution_result",
        "activated_core",
        "runtime_result",
        "child_core_output",
    ]
    execution_leak = any(key in result1 for key in execution_leak_keys)
    results["test_no_child_core_execution_leakage"] = {
        "passed": execution_leak is False
    }

    # TEST 6: Exact minimal state shape
    results["test_state_minimal_exact"] = {
        "passed": set(vars(state).keys()) == {
            "last_dispatch_id",
            "last_target",
            "last_timestamp",
        }
    }

    return {
        "stage": "STAGE_20_CLOSEOUT",
        "status": "complete",
        "results": results,
    }


if __name__ == "__main__":
    output = run_stage20_closeout_probe()
    import json
    print(json.dumps(output, indent=2))