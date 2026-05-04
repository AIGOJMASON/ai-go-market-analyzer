from __future__ import annotations

from AI_GO.core.governance.governance_index_awareness import (
    build_governance_index_awareness_packet,
    summarize_governance_index_awareness,
)
from AI_GO.core.governance.governance_packet_store import persist_governance_packet


def _seed_packet(
    *,
    governance_packet_id: str,
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
        "governor_version": "v2.0",
        "created_at": "2026-04-29T00:00:00+00:00",
        "profile": "contractor_phase_closeout",
        "action": "phase_closeout",
        "project_id": project_id,
        "phase_id": phase_id,
        "status": status,
        "allowed": allowed,
        "request": {
            "request_id": request_id,
            "route": "/contractor-builder/phase-closeout/run",
            "project_id": project_id,
            "phase_id": phase_id,
        },
        "watcher": {"status": "passed" if allowed else "blocked", "valid": allowed},
        "state": {"status": "passed", "valid": True},
        "canon": {"status": "passed", "valid": True},
        "execution_gate": {
            "status": "passed" if execution_gate_allowed else "blocked",
            "valid": execution_gate_allowed,
            "allowed": execution_gate_allowed,
        },
        "sealed": True,
    }

    return persist_governance_packet(
        packet=packet,
        profile="contractor_phase_closeout",
        governance_packet_id=governance_packet_id,
    )


def run_probe() -> dict:
    _seed_packet(
        governance_packet_id="governance-phase4-awareness-001",
        request_id="request-phase4-awareness-001",
        project_id="project-phase4-awareness",
        phase_id="phase-awareness",
        status="allowed",
        allowed=True,
        execution_gate_allowed=True,
    )

    _seed_packet(
        governance_packet_id="governance-phase4-awareness-duplicate-001",
        request_id="request-phase4-awareness-duplicate",
        project_id="project-phase4-awareness",
        phase_id="phase-awareness",
        status="blocked",
        allowed=False,
        execution_gate_allowed=False,
    )

    _seed_packet(
        governance_packet_id="governance-phase4-awareness-duplicate-002",
        request_id="request-phase4-awareness-duplicate",
        project_id="project-phase4-awareness",
        phase_id="phase-awareness",
        status="blocked",
        allowed=False,
        execution_gate_allowed=False,
    )

    awareness = build_governance_index_awareness_packet(limit=200)
    summary = summarize_governance_index_awareness(limit=200)

    assert awareness["artifact_type"] == "governance_index_awareness_packet"
    assert awareness["visibility_mode"] == "read_only"
    assert awareness["authority"]["can_execute"] is False
    assert awareness["authority"]["can_mutate_state"] is False
    assert awareness["authority"]["can_modify_governance_packets"] is False
    assert awareness["authority"]["index_is_awareness_only"] is True

    assert "trend_detection" in awareness
    assert "anomaly_detection" in awareness
    assert "cross_run_correlation" in awareness
    assert "replay_analysis" in awareness
    assert "temporal_awareness" in awareness

    assert awareness["trend_detection"]["entry_count"] >= 1
    assert summary["status"] == "ok"

    duplicate_flags = [
        flag
        for flag in awareness["anomaly_detection"]["flags"]
        if str(flag.get("class")) == "replay_or_duplicate"
    ]

    assert len(duplicate_flags) >= 1

    return {
        "status": "passed",
        "phase": "Phase 4.1",
        "layer": "governance_index_awareness",
        "awareness_status": awareness["summary"]["system_awareness_status"],
        "anomaly_count": awareness["summary"]["anomaly_count"],
        "replay_candidate_count": awareness["summary"]["replay_candidate_count"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_GOVERNANCE_INDEX_AWARENESS_PROBE: PASS")
    print(result)