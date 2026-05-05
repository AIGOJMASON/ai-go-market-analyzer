from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.testclient import TestClient


def _build_app() -> FastAPI:
    from AI_GO.api.contractor_builder_api import router as contractor_router

    app = FastAPI(title="contractor_end_to_end_probe_app")
    app.include_router(contractor_router)
    return app


def _now() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _post(client: TestClient, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = client.post(path, json=payload)
    if response.status_code != 200:
        raise AssertionError(f"{path} failed: {response.status_code} {response.text}")
    return response.json()


def run_probe() -> Dict[str, Any]:
    from AI_GO.child_cores.contractor_builder_v1.ui.contractor_dashboard_runner import (
        run_contractor_dashboard,
    )

    app = _build_app()
    client = TestClient(app)

    uid = _now()
    portfolio_id = "portfolio-e2e"
    reporting_period = "2026-W16"

    project = _post(
        client,
        "/contractor-builder/projects/create",
        {
            "project_name": f"E2E Probe {uid}",
            "project_type": "Kitchen Remodel",
            "client_name": "Client",
            "pm_name": "PM",
            "jurisdiction": {
                "jurisdiction_id": "scottsburg-in",
                "authority_name": "Scottsburg Building Department",
                "city": "Scottsburg",
                "county": "Scott",
                "state": "IN",
            },
            "baseline_refs": {
                "schedule_baseline_id": f"s-{uid}",
                "budget_baseline_id": f"b-{uid}",
                "compliance_snapshot_id": f"c-{uid}",
            },
            "portfolio_id": portfolio_id,
        },
    )

    project_id = project["project_id"]
    baseline_lock = project["baseline_lock"]
    baseline_refs = baseline_lock["baseline_refs"]

    wf = _post(
        client,
        "/contractor-builder/workflow/initialize",
        {
            "project_id": project_id,
            "phase_templates": [
                {
                    "template_id": "t1",
                    "project_type": "Kitchen Remodel",
                    "phase_name": "Demo",
                    "expected_duration_days": 3,
                    "dependencies": [],
                    "role_expectations": {
                        "crew": ["demo crew"],
                        "management": ["pm oversight"],
                    },
                    "management_checkpoints": [],
                    "client_gate_requirement": {
                        "required": False,
                        "checklist": [],
                    },
                    "notes": "Demo phase",
                }
            ],
            "overwrite": False,
        },
    )

    if wf.get("status") != "initialized":
        raise AssertionError(f"workflow_initialize expected initialized, got: {wf}")

    phase_id = wf["phase_instances"][0]["phase_id"]

    change = _post(
        client,
        "/contractor-builder/change/create",
        {
            "packet_kwargs": {
                "change_packet_id": f"cp-{uid}",
                "project_id": project_id,
                "phase_id": phase_id,
                "title": "Change",
                "originator_name": "PM",
                "originator_role": "PM",
                "originator_org": "Org",
                "workflow_phase_state_snapshot_id": "snap",
                "compliance_snapshot_id": baseline_refs["compliance_snapshot_id"],
                "drawing_revision_id": "d",
                "budget_baseline_id": baseline_refs["budget_baseline_id"],
                "schedule_baseline_id": baseline_refs["schedule_baseline_id"],
                "scope_delta_description": "test",
                "added_items": [],
                "removed_items": [],
                "phase_status": "not_started",
                "disruption_multiplier": 1.0,
                "factors_applied": [],
            }
        },
    )

    if change.get("status") != "created":
        raise AssertionError(f"change_create expected created, got: {change}")

    change_id = change["packet"]["change_packet_id"]

    decision = _post(
        client,
        "/contractor-builder/decision/create",
        {
            "entry_kwargs": {
                "decision_id": f"d-{uid}",
                "project_id": project_id,
                "title": "Decision",
                "decision_type": "Schedule_Adjustment",
                "phase_id": phase_id,
                "linked_change_packet_id": change_id,
                "compliance_snapshot_id": baseline_refs["compliance_snapshot_id"],
                "schedule_baseline_id": baseline_refs["schedule_baseline_id"],
                "budget_baseline_id": baseline_refs["budget_baseline_id"],
                "drawing_revision_id": f"drawing-{uid}",
                "oracle_snapshot_id": "snapshot-lumber-watch",
                "expected_schedule_delta_days": 1.0,
                "expected_cost_delta_amount": 100.0,
                "expected_margin_delta_percent": None,
                "expected_risk_level": "Moderate",
                "notes_on_assumptions": "probe",
                "may_reference_in_owner_reports": True,
                "owner_report_reference_label": "probe",
                "notes_internal": "probe",
                "attachments_refs": [],
            }
        },
    )

    if decision.get("status") != "created":
        raise AssertionError(f"decision_create expected created, got: {decision}")

    decision_id = decision["entry"]["decision_id"]

    risk = _post(
        client,
        "/contractor-builder/risk/create",
        {
            "entry_kwargs": {
                "risk_id": f"r-{uid}",
                "project_id": project_id,
                "category": "Access_Logistics",
                "description": "Risk",
                "probability": "Moderate",
                "impact_level": "Moderate",
                "mitigation_strategy": "Plan",
                "mitigation_owner": "PM",
                "review_frequency": "weekly",
                "linked_decision_ids": [decision_id],
                "linked_change_packet_ids": [change_id],
            }
        },
    )

    if risk.get("status") != "created":
        raise AssertionError(f"risk_create expected created, got: {risk}")

    risk_id = risk["entry"]["risk_id"]

    assumption = _post(
        client,
        "/contractor-builder/assumption/create",
        {
            "entry_kwargs": {
                "assumption_id": f"a-{uid}",
                "project_id": project_id,
                "statement": "Test assumption",
                "source_type": "Verbal",
                "source_reference": "call",
                "logged_by": "PM",
                "owner_acknowledged": "Yes",
                "validation_status": "Unverified",
                "impact_if_false": "delay",
                "linked_decision_ids": [decision_id],
                "linked_change_packet_ids": [change_id],
                "linked_risk_ids": [risk_id],
            }
        },
    )

    if assumption.get("status") != "created":
        raise AssertionError(f"assumption_create expected created, got: {assumption}")

    cycle = _post(
        client,
        "/contractor-builder/weekly-cycle/run",
        {
            "reporting_period_label": reporting_period,
            "project_payloads": [
                {
                    "project_id": project_id,
                    "workflow_snapshot": wf["workflow_state"],
                    "change_records": [change["packet"]],
                    "compliance_snapshot": {
                        "project_id": project_id,
                        "blocking": False,
                        "blocking_count": 0,
                        "permits": [],
                        "inspections": [],
                    },
                    "router_snapshot": {
                        "conflict_count": 0,
                        "capacity_record_count": 0,
                        "cascade_risk": {
                            "cascade_risk_label": "none",
                            "conflict_count": 0,
                            "dependency_violation_count": 0,
                            "overloaded_resource_count": 0,
                        },
                    },
                    "oracle_snapshot": {
                        "summary_label": "stable_external_pressure",
                        "procurement_posture": "Watch",
                        "market_domain": "Lumber",
                        "shock_direction": "flat",
                        "shock_severity": "none",
                    },
                    "decision_records": [decision["entry"]],
                    "risk_records": [risk["entry"]],
                    "assumption_records": [],
                }
            ],
            "portfolio_project_map": {portfolio_id: [project_id]},
        },
    )

    if cycle["status"] != "completed":
        raise AssertionError(f"Weekly cycle failed: {cycle}")

    cycle_record = cycle["cycle_record"]

    if cycle_record.get("project_report_count") != 1:
        raise AssertionError(
            f"Expected project_report_count=1, got: {cycle_record.get('project_report_count')}"
        )

    if cycle_record.get("portfolio_report_count") != 1:
        raise AssertionError(
            f"Expected portfolio_report_count=1, got: {cycle_record.get('portfolio_report_count')}"
        )

    if cycle_record.get("errors"):
        raise AssertionError(f"Expected no cycle errors, got: {cycle_record.get('errors')}")

    project_report = cycle_record["project_reports"][0]
    portfolio_report = cycle_record["portfolio_reports"][0]

    dashboard = run_contractor_dashboard(
        request_id=uid,
        project_profile={
            "project_id": project_id,
            "project_name": "E2E Probe",
            "project_type": "Kitchen Remodel",
            "status": "active",
            "client": {"name": "Client"},
            "pm": {"name": "PM"},
            "jurisdiction": {
                "jurisdiction_id": "scottsburg-in",
                "authority_name": "Scottsburg Building Department",
                "city": "Scottsburg",
                "county": "Scott",
                "state": "IN",
            },
        },
        baseline_lock=baseline_lock,
        workflow_snapshot=wf["workflow_state"],
        latest_project_report=project_report,
        portfolio_report=portfolio_report,
        decision_records=[decision["entry"]],
        change_records=[change["packet"]],
        compliance_snapshot={
            "blocking": False,
            "blocking_count": 0,
            "permits": [],
            "inspections": [],
        },
        risk_records=[risk["entry"]],
    )

    validate = _post(
        client,
        "/contractor-builder/pre-interface/validate",
        {"payload": dashboard},
    )

    if validate["status"] != "ok":
        raise AssertionError(f"Watcher failed: {validate}")

    if validate.get("valid") is not True:
        raise AssertionError(f"Watcher valid flag false: {validate}")

    if dashboard["mode"] != "advisory":
        raise AssertionError("Mode violation")

    if dashboard["execution_allowed"] is not False:
        raise AssertionError("Execution violation")

    if dashboard["approval_required"] is not True:
        raise AssertionError("Approval violation")

    return {
        "status": "passed",
        "project_id": project_id,
        "cycle_id": cycle_record["cycle_id"],
        "project_report_id": project_report["report_id"],
        "portfolio_report_id": portfolio_report["report_id"],
    }


def main() -> None:
    try:
        result = run_probe()
        print(json.dumps(result, indent=2))
        print("STAGE_CONTRACTOR_END_TO_END_PROBE: PASS")
    except Exception as exc:
        print("STAGE_CONTRACTOR_END_TO_END_PROBE: FAIL")
        print(exc)
        raise


if __name__ == "__main__":
    main()