from __future__ import annotations

from typing import Dict, Any, List

from PM_CORE.routing.pm_routing import handoff_decision_to_routing
from PM_CORE.routing.routing_state import RoutingState


def build_valid_decision_packet() -> Dict[str, Any]:
    return {
        "decision_id": "PM-DECISION-TEST-001",
        "intent": "route_to_proposal_builder",
        "target_mode": "single",
        "target": "contractor_proposals_core",
        "rationale_summary": "Validated contractor demand signal requires proposal generation.",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-001"],
        "timestamp": "2026-03-18T00:00:00Z",
    }


def build_candidate_set_packet() -> Dict[str, Any]:
    return {
        "decision_id": "PM-DECISION-TEST-002",
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
        "rationale_summary": "Ambiguous routing between proposal generation and GIS enrichment.",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-002"],
        "timestamp": "2026-03-18T00:00:00Z",
    }


def build_invalid_packet_missing_target() -> Dict[str, Any]:
    return {
        "decision_id": "PM-DECISION-TEST-003",
        "intent": "invalid_missing_target",
        "target_mode": "single",
        "rationale_summary": "Missing target field should fail readiness.",
        "upstream_refs": ["WR-RESEARCH-PACKET-TEST-003"],
        "timestamp": "2026-03-18T00:00:00Z",
    }


def run_stage19_closeout_probe() -> Dict[str, Any]:
    valid_child_cores: List[str] = [
        "contractor_proposals_core",
        "louisville_gis_core",
    ]

    state = RoutingState()

    results = {}

    # TEST 1: Valid single target routing
    packet1 = build_valid_decision_packet()
    result1 = handoff_decision_to_routing(packet1, valid_child_cores, state)

    results["test_valid_single"] = {
        "passed": result1.get("artifact_type") == "pm_routing_packet",
        "artifact": result1,
    }

    # TEST 2: Valid candidate set routing
    packet2 = build_candidate_set_packet()
    result2 = handoff_decision_to_routing(packet2, valid_child_cores, state)

    results["test_candidate_set"] = {
        "passed": result2.get("artifact_type") == "pm_routing_packet"
        and result2.get("target_mode") == "candidate_set",
        "artifact": result2,
    }

    # TEST 3: Invalid packet (missing target)
    packet3 = build_invalid_packet_missing_target()
    result3 = handoff_decision_to_routing(packet3, valid_child_cores, state)

    results["test_invalid_missing_target"] = {
        "passed": result3.get("artifact_type") == "pm_routing_failure_receipt",
        "artifact": result3,
    }

    # TEST 4: No execution leakage check
    execution_leak = any(
        key in result1 for key in ["execution", "dispatch", "activated_core"]
    )

    results["test_no_execution_leakage"] = {
        "passed": execution_leak is False
    }

    # TEST 5: Strict state minimality check
    results["test_state_minimal"] = {
        "passed": set(vars(state).keys()) == {
            "last_packet_id",
            "last_target_set",
            "last_timestamp",
        }
    }

    return {
        "stage": "STAGE_19_CLOSEOUT",
        "status": "complete",
        "results": results,
    }


if __name__ == "__main__":
    output = run_stage19_closeout_probe()
    import json
    print(json.dumps(output, indent=2))