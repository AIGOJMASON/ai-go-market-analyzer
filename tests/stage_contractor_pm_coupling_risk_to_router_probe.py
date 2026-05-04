from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_packet_builder import (
    build_pm_coupling_context,
    extract_target_context,
)
from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_service import (
    create_risk,
)
from AI_GO.child_cores.contractor_builder_v1.router.router_service import (
    persist_schedule_blocks_governed,
)


def run_probe() -> dict:
    project_id = "project-pm-coupling-risk-router-probe"
    phase_id = "phase-pm-coupling-risk-router-probe"
    risk_id = "risk-pm-coupling-risk-router-probe-001"

    risk_result = create_risk(
        {
            "actor": "stage_contractor_pm_coupling_risk_to_router_probe",
            "entry_kwargs": {
                "risk_id": risk_id,
                "project_id": project_id,
                "category": "Other",
                "description": (
                    "Risk created to verify risk output can become bounded PM "
                    "context for router schedule constraints."
                ),
                "probability": "Moderate",
                "impact_level": "High",
                "mitigation_strategy": (
                    "Router should see this as PM context before schedule block "
                    "planning, but must still execute through its own governance."
                ),
                "mitigation_owner": "Project Manager",
                "review_frequency": "weekly",
                "linked_decision_ids": [],
                "linked_change_packet_ids": [],
                "notes": (
                    "Phase 2G.3 probe. Risk should influence router through "
                    "pm_context only. No direct risk-to-router mutation."
                ),
            },
        }
    )

    assert risk_result["mode"] == "governed_execution"
    assert risk_result["status"] == "created"
    assert risk_result["state"]["valid"] is True
    assert risk_result["watcher"]["valid"] is True
    assert risk_result["execution_gate"]["allowed"] is True
    assert risk_result["result_summary"]["artifact_type"] == "post_execution_result_summary"
    assert risk_result["result_summary"]["effect"] == "execution_completed"

    coupling_context = build_pm_coupling_context(
        project_id=project_id,
        phase_id=phase_id,
        risk_records=[risk_result],
        actor="PM_CORE",
    )

    router_pm_context = extract_target_context(
        coupling_context=coupling_context,
        target_service="router",
    )

    assert router_pm_context["packet_count"] >= 1
    assert router_pm_context["packets"][0]["source"]["source_type"] == "risk"
    assert router_pm_context["packets"][0]["target"]["target_service"] == "router"
    assert (
        router_pm_context["packets"][0]["influence"]["influence_type"]
        == "risk_to_router"
    )

    router_result = persist_schedule_blocks_governed(
        {
            "actor": "stage_contractor_pm_coupling_risk_to_router_probe",
            "project_id": project_id,
            "pm_context": router_pm_context,
            "blocks": [
                {
                    "block_id": "block-pm-coupling-risk-router-probe-001",
                    "project_id": project_id,
                    "phase_id": phase_id,
                    "block_type": "Crew_Assignment",
                    "start_date": "2026-04-30",
                    "end_date": "2026-05-01",
                    "resource_name": "Shared Crew Alpha",
                    "resource_type": "crew",
                    "dependency_phase_ids": [],
                    "notes": (
                        "Phase 2G.3 probe. Router received risk influence through "
                        "pm_context only. Schedule block still written by router "
                        "governed execution."
                    ),
                }
            ],
        }
    )

    assert router_result["mode"] == "governed_execution"
    assert router_result["status"] == "stored"
    assert router_result["state"]["valid"] is True
    assert router_result["watcher"]["valid"] is True
    assert router_result["execution_gate"]["allowed"] is True
    assert router_result["project_id"] == project_id
    assert router_result["artifact_path"]
    assert router_result["receipt_path"]
    assert router_result["result_summary"]["artifact_type"] == "post_execution_result_summary"
    assert router_result["result_summary"]["effect"] == "execution_completed"
    assert router_result["result_summary"]["counts"]["state_mutations"] == 1
    assert router_result["result_summary"]["counts"]["artifacts_created"] == 1

    return {
        "status": "passed",
        "phase": "2G.3",
        "link": "risk_to_router",
        "risk": {
            "risk_id": risk_result["entry"]["risk_id"],
            "artifact_path": risk_result["artifact_path"],
            "receipt_path": risk_result["receipt_path"],
            "result_summary": risk_result["result_summary"],
        },
        "coupling": {
            "context_hash": coupling_context["context_hash"],
            "packet_count": coupling_context["packet_count"],
            "router_packet_count": router_pm_context["packet_count"],
            "first_packet": router_pm_context["packets"][0],
        },
        "router": {
            "artifact_path": router_result["artifact_path"],
            "receipt_path": router_result["receipt_path"],
            "result_summary": router_result["result_summary"],
        },
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_PM_COUPLING_RISK_TO_ROUTER_PROBE: PASS")
    print(json.dumps(output, indent=2))