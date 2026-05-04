from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.weekly_cycle.weekly_cycle_runner import (
    run_weekly_cycle,
)
from AI_GO.child_cores.contractor_builder_v1.weekly_cycle.weekly_cycle_receipt_builder import (
    build_weekly_cycle_receipt,
    write_weekly_cycle_receipt,
)


def execute_weekly_cycle_run(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])

    cycle_record = run_weekly_cycle(
        reporting_period_label=request["reporting_period_label"],
        project_payloads=request.get("project_payloads", []),
        portfolio_project_map=request.get("portfolio_project_map", {}),
    )

    receipt = build_weekly_cycle_receipt(
        event_type="run_weekly_cycle",
        cycle_id=cycle_record["cycle_id"],
        artifact_path="AI_GO/state/contractor_builder_v1/weekly_cycle/current/latest_weekly_cycle_response.json",
        actor=str(request.get("actor", "weekly_cycle_executor")),
        details={
            "project_report_count": cycle_record["project_report_count"],
            "portfolio_report_count": cycle_record["portfolio_report_count"],
            "cycle_status": cycle_record["cycle_status"],
        },
    )
    receipt_path = write_weekly_cycle_receipt(receipt)

    return {
        "status": cycle_record["cycle_status"],
        "cycle_record": cycle_record,
        "receipt_path": str(receipt_path),
    }