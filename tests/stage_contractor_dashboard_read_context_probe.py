from __future__ import annotations

import json
from pathlib import Path

from AI_GO.core.state_runtime.contractor_dashboard_read_context import (
    build_contractor_dashboard_read_context,
)


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload))
        handle.write("\n")


def run_probe() -> dict:
    project_id = "project-dashboard-read-probe"
    phase_id = "phase-dashboard-read-probe"

    root = Path("AI_GO/state/contractor_builder_v1/projects/by_project") / project_id

    _write_json(
        root / "project_profile.json",
        {
            "project_id": project_id,
            "project_name": "Dashboard Read Probe",
            "status": "active",
        },
    )

    _write_json(
        root / "baseline_lock.json",
        {
            "project_id": project_id,
            "lock_status": "locked",
            "baseline_refs": {},
        },
    )

    _write_json(
        root / "workflow" / "workflow_state.json",
        {
            "project_id": project_id,
            "workflow_status": "active",
            "current_phase_id": phase_id,
        },
    )

    _write_json(
        root / "workflow" / "phase_instances.json",
        [
            {
                "project_id": project_id,
                "phase_id": phase_id,
                "phase_name": "Dashboard Read Phase",
                "phase_status": "awaiting_signoff",
            }
        ],
    )

    _append_jsonl(
        root / "workflow" / "client_signoff_status.jsonl",
        {
            "project_id": project_id,
            "phase_id": phase_id,
            "status": "sent",
            "artifact_id": "artifact-dashboard-read-probe",
        },
    )

    _write_json(
        root / "delivery" / "email-dashboard-read-probe.json",
        {
            "delivery_id": "email-dashboard-read-probe",
            "project_id": project_id,
            "phase_id": phase_id,
            "delivery_status": "sent",
        },
    )

    result = build_contractor_dashboard_read_context(
        project_id=project_id,
        phase_id=phase_id,
        actor="stage_contractor_dashboard_read_context_probe",
        persist_packet=True,
    )

    assert result["status"] == "ok"
    assert result["mode"] == "governed_read"
    assert result["state"]["valid"] is True
    assert result["watcher"]["valid"] is True
    assert result["dashboard_read_state"]["project_profile"]["project_id"] == project_id
    assert result["dashboard_read_state"]["latest_signoff_status"]["status"] == "sent"
    assert result["dashboard_read_state"]["latest_delivery_record"]["delivery_id"] == "email-dashboard-read-probe"
    assert result["dashboard_read_state"]["read_only"] is True
    assert result["dashboard_read_state"]["mutation_allowed"] is False

    governance_decision = result.get("governance_decision", {})
    assert governance_decision.get("governance_packet_id")

    return {
        "status": "passed",
        "project_id": project_id,
        "phase_id": phase_id,
        "governance_packet_id": governance_decision.get("governance_packet_id"),
        "dashboard_read_state_keys": sorted(result["dashboard_read_state"].keys()),
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_DASHBOARD_READ_CONTEXT_PROBE: PASS")
    print(json.dumps(output, indent=2))