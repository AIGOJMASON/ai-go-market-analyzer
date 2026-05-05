from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.testclient import TestClient


def _build_app() -> FastAPI:
    from AI_GO.api.contractor_pre_interface_watcher import router as watcher_router

    app = FastAPI(title="contractor_projection_probe_app")
    app.include_router(watcher_router)
    return app


def _now() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def run_probe() -> Dict[str, Any]:
    from AI_GO.child_cores.contractor_builder_v1.ui.contractor_dashboard_runner import (
        run_contractor_dashboard,
    )
    from AI_GO.child_cores.contractor_builder_v1.projection.latest_payload_state import (
        persist_latest_operator_payload,
    )

    app = _build_app()
    client = TestClient(app)

    uid = _now()
    project_id = f"project-projection-{uid}"

    project_profile = {
        "project_id": project_id,
        "project_name": "Projection Probe",
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
    }

    baseline_lock = {
        "baseline_refs": {
            "schedule_baseline_id": "schedule-probe",
            "budget_baseline_id": "budget-probe",
            "compliance_snapshot_id": "compliance-probe",
        }
    }

    workflow_snapshot = {
        "workflow_status": "initialized",
        "phase_count": 1,
        "current_phase_id": "",
    }

    latest_project_report = {
        "report_id": f"report-{uid}",
        "report_type": "Project_Weekly",
        "subject_id": project_id,
        "report_status": "pm_review",
        "reporting_period_label": "2026-W16",
        "deterministic_block": {
            "change": {
                "approved_change_total_amount": 0.0,
            },
            "compliance": {
                "blocking": False,
            },
            "router": {
                "conflict_count": 0,
            },
            "risk": {
                "open_or_monitoring_count": 0,
            },
        },
        "summary_draft": {
            "headline": "Projection probe weekly report",
            "bullets": [],
        },
    }

    portfolio_report = {
        "subject_id": "portfolio-projection-probe",
        "report_id": f"portfolio-{uid}",
        "report_status": "pm_review",
        "reporting_period_label": "2026-W16",
        "deterministic_block": {
            "project_count": 1,
            "blocking_project_count": 0,
            "total_conflict_count": 0,
            "total_open_or_monitoring_risks": 0,
            "approved_change_total_amount": 0.0,
        },
        "summary_draft": {
            "headline": "Projection probe portfolio report",
            "bullets": [],
        },
    }

    compliance_snapshot = {
        "blocking": False,
        "blocking_count": 0,
        "permits": [],
        "inspections": [],
    }

    dashboard = run_contractor_dashboard(
        request_id=uid,
        project_profile=project_profile,
        baseline_lock=baseline_lock,
        workflow_snapshot=workflow_snapshot,
        latest_project_report=latest_project_report,
        portfolio_report=portfolio_report,
        decision_records=[],
        change_records=[],
        compliance_snapshot=compliance_snapshot,
        risk_records=[],
    )

    required_top_level = [
        "generated_at",
        "request_id",
        "child_core_id",
        "mode",
        "approval_required",
        "execution_allowed",
        "summary_panel",
        "project_panel",
        "portfolio_panel",
        "decisions_panel",
        "changes_panel",
        "compliance_panel",
        "risks_panel",
        "explanation_panel",
    ]
    for field in required_top_level:
        if field not in dashboard:
            raise AssertionError(f"Missing required dashboard field: {field}")

    if dashboard["child_core_id"] != "contractor_builder_v1":
        raise AssertionError(
            f"Unexpected child_core_id: {dashboard['child_core_id']}"
        )

    if dashboard["mode"] != "advisory":
        raise AssertionError(f"Unexpected mode: {dashboard['mode']}")

    if dashboard["approval_required"] is not True:
        raise AssertionError("approval_required must be True")

    if dashboard["execution_allowed"] is not False:
        raise AssertionError("execution_allowed must be False")

    paths = persist_latest_operator_payload(
        payload=dashboard,
        request_id=uid,
        project_id=project_id,
    )

    for label, path_str in paths.items():
        path = Path(path_str)
        if not path.exists():
            raise AssertionError(f"Missing persisted file: {label} -> {path}")

    validate_response = client.post(
        "/pre-interface/validate",
        json={"payload": dashboard},
    )

    if validate_response.status_code != 200:
        raise AssertionError(
            f"/pre-interface/validate failed: "
            f"{validate_response.status_code} {validate_response.text}"
        )

    validation = validate_response.json()

    if validation.get("status") != "ok":
        raise AssertionError(f"Pre-interface invalid: {validation}")

    if validation.get("valid") is not True:
        raise AssertionError(f"Pre-interface valid flag false: {validation}")

    return {
        "status": "passed",
        "project_id": project_id,
        "request_id": uid,
        "persisted_paths": paths,
    }


def main() -> None:
    try:
        result = run_probe()
        print(json.dumps(result, indent=2))
        print("STAGE_CONTRACTOR_PROJECTION_PROBE: PASS")
    except Exception as exc:
        print("STAGE_CONTRACTOR_PROJECTION_PROBE: FAIL")
        print(exc)
        raise


if __name__ == "__main__":
    main()