from __future__ import annotations

from AI_GO.core.governance.governance_packet_index import (
    get_governance_index_entry,
    query_governance_index,
)
from AI_GO.core.governance.governance_packet_store import (
    load_governance_packet,
    persist_governance_packet,
)


def run_probe() -> dict:
    packet = {
        "artifact_type": "governed_request_packet",
        "artifact_version": "v2",
        "governor_version": "v2.0",
        "created_at": "2026-04-29T00:00:00+00:00",
        "profile": "contractor_phase_closeout",
        "action": "phase_closeout",
        "project_id": "project-governance-index-probe",
        "phase_id": "phase-index-probe",
        "status": "allowed",
        "allowed": True,
        "request": {
            "request_id": "request-governance-index-probe",
            "route": "/contractor-builder/phase-closeout/run",
            "project_id": "project-governance-index-probe",
            "phase_id": "phase-index-probe",
        },
        "watcher": {"status": "passed", "valid": True},
        "state": {"status": "passed", "valid": True},
        "canon": {"status": "passed", "valid": True},
        "execution_gate": {"status": "passed", "valid": True, "allowed": True},
        "sealed": True,
    }

    persisted = persist_governance_packet(
        packet=packet,
        profile="contractor_phase_closeout",
    )

    packet_id = persisted["governance_packet_id"]

    index_entry = get_governance_index_entry(governance_packet_id=packet_id)
    loaded_packet = load_governance_packet(
        profile="contractor_phase_closeout",
        governance_packet_id=packet_id,
    )

    query_results = query_governance_index(
        request_id="request-governance-index-probe",
        project_id="project-governance-index-probe",
        phase_id="phase-index-probe",
        status="allowed",
        allowed=True,
    )

    assert index_entry["governance_packet_id"] == packet_id
    assert index_entry["pointer_only"] is True
    assert index_entry["packet_remains_truth"] is True
    assert loaded_packet["governance_packet_id"] == packet_id
    assert loaded_packet["_loaded_from_index"] is True
    assert len(query_results) >= 1

    return {
        "status": "passed",
        "governance_packet_id": packet_id,
        "packet_path": persisted["path"],
        "index_entry": index_entry,
        "query_result_count": len(query_results),
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_GOVERNANCE_INDEX_PROBE: PASS")
    print(result)