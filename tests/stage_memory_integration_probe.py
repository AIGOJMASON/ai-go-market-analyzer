from __future__ import annotations

import json

from AI_GO.core.governance.governance_packet_store import persist_governance_packet
from AI_GO.core.governance.governance_packet_index import append_governance_index_entry
from AI_GO.core.memory.memory_integration import (
    integrate_governance_index_into_memory,
    load_system_memory_index,
    query_system_memory,
)


def _seed_governance_packet(
    *,
    governance_packet_id: str,
    profile: str,
    action: str,
    route: str,
    request_id: str,
    project_id: str,
    phase_id: str,
    status: str,
    allowed: bool,
    execution_gate_allowed: bool,
) -> dict:
    packet = {
        "artifact_type": "governed_request_packet",
        "artifact_version": "v2",
        "created_at": "2026-04-29T00:00:00+00:00",
        "profile": profile,
        "action": action,
        "project_id": project_id,
        "phase_id": phase_id,
        "status": status,
        "allowed": allowed,
        "request": {
            "request_id": request_id,
            "route": route,
            "project_id": project_id,
            "phase_id": phase_id,
        },
        "state": {
            "status": "passed",
            "valid": True,
        },
        "watcher": {
            "status": "passed" if allowed else "blocked",
            "valid": allowed,
        },
        "watcher_enforcement": {
            "status": "passed" if allowed else "blocked",
            "valid": allowed,
            "allowed": allowed,
        },
        "execution_gate": {
            "status": "passed" if execution_gate_allowed else "blocked",
            "valid": execution_gate_allowed,
            "allowed": execution_gate_allowed,
        },
        "sealed": True,
    }

    persisted = persist_governance_packet(
        packet=packet,
        profile=profile,
        governance_packet_id=governance_packet_id,
    )

    append_governance_index_entry(
        packet=persisted["packet"],
        packet_path=persisted["path"],
    )

    return persisted


def run_probe() -> dict:
    project_id = "project-memory-integration-probe"
    phase_id = "phase-memory"

    _seed_governance_packet(
        governance_packet_id="governance-memory-decision-001",
        profile="contractor_decision",
        action="decision_create",
        route="/contractor-builder/decision/create",
        request_id="request-memory-decision-001",
        project_id=project_id,
        phase_id=phase_id,
        status="allowed",
        allowed=True,
        execution_gate_allowed=True,
    )

    _seed_governance_packet(
        governance_packet_id="governance-memory-oracle-001",
        profile="contractor_oracle",
        action="oracle_projection",
        route="/contractor-builder/oracle/project-external-pressure",
        request_id="request-memory-oracle-001",
        project_id=project_id,
        phase_id=phase_id,
        status="allowed",
        allowed=True,
        execution_gate_allowed=True,
    )

    _seed_governance_packet(
        governance_packet_id="governance-memory-outcome-001",
        profile="contractor_phase_closeout",
        action="phase_closeout",
        route="/contractor-builder/phase-closeout/run",
        request_id="request-memory-outcome-001",
        project_id=project_id,
        phase_id=phase_id,
        status="blocked",
        allowed=False,
        execution_gate_allowed=False,
    )

    result = integrate_governance_index_into_memory(limit=500)
    index = load_system_memory_index()

    decision_memory = query_system_memory(
        memory_type="decision_memory",
        project_id=project_id,
        phase_id=phase_id,
    )

    oracle_memory = query_system_memory(
        memory_type="oracle_memory",
        project_id=project_id,
        phase_id=phase_id,
    )

    outcome_memory = query_system_memory(
        memory_type="outcome_memory",
        project_id=project_id,
        phase_id=phase_id,
    )

    assert result["status"] == "ok"
    assert result["visibility_mode"] == "read_only"
    assert result["authority"]["advisory_only"] is True
    assert result["authority"]["can_execute"] is False
    assert result["authority"]["can_mutate_state"] is False
    assert result["authority"]["can_override_governance"] is False

    assert index["artifact_type"] == "system_memory_index"
    assert index["authority"]["can_execute"] is False
    assert index["authority"]["can_mutate_state"] is False
    assert index["authority"]["can_override_governance"] is False

    assert decision_memory["matched_count"] >= 1
    assert oracle_memory["matched_count"] >= 1
    assert outcome_memory["matched_count"] >= 1

    for query_result in (decision_memory, oracle_memory, outcome_memory):
        for record in query_result["records"]:
            assert record["learning_posture"]["advisory_only"] is True
            assert record["learning_posture"]["can_execute"] is False
            assert record["learning_posture"]["can_mutate_state"] is False
            assert record["learning_posture"]["can_override_governance"] is False
            assert record["use_policy"]["may_bypass_watcher"] is False
            assert record["sealed"] is True

    return {
        "status": "passed",
        "phase": "Phase 4.2",
        "layer": "memory_integration",
        "records_created": result["records_created"],
        "memory_record_count": index["record_count"],
        "decision_memory_count": decision_memory["matched_count"],
        "oracle_memory_count": oracle_memory["matched_count"],
        "outcome_memory_count": outcome_memory["matched_count"],
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_MEMORY_INTEGRATION_PROBE: PASS")
    print(json.dumps(output, indent=2))