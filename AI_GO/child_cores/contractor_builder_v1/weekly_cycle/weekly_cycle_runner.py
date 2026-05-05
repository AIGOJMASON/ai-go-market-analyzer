"""
Weekly cycle runner for contractor_builder_v1.

Coordinates project weekly reports, portfolio reports, and current cycle visibility.

Northstar posture:
- state paths are anchored through state_paths
- writes are governed
- upstream project truth is not mutated here
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root

from ..governance.identity import build_receipt_id
from .portfolio_aggregator import aggregate_portfolio_weekly_reports
from .project_report_orchestrator import orchestrate_project_weekly_report
from .weekly_cycle_schema import build_weekly_cycle_record, validate_weekly_cycle_record


WEEKLY_CYCLE_ROOT = state_root() / "contractor_builder_v1" / "weekly_cycle"
STATE_ROOT = WEEKLY_CYCLE_ROOT / "current"
RECEIPTS_ROOT = WEEKLY_CYCLE_ROOT / "receipts"


MUTATION_CLASS = "contractor_weekly_cycle_persistence"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if isinstance(parsed, dict) and parsed.get("artifact_type") == "governed_persistence_envelope":
        payload = parsed.get("payload")
        return payload if isinstance(payload, dict) else {}

    return parsed if isinstance(parsed, dict) else {}


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------


def get_weekly_cycle_state_path() -> Path:
    return STATE_ROOT / "weekly_cycle_state.json"


def get_latest_weekly_cycle_response_path() -> Path:
    return STATE_ROOT / "latest_weekly_cycle_response.json"


def get_weekly_cycle_receipts_root() -> Path:
    return RECEIPTS_ROOT


# -----------------------------------------------------------------------------
# Classification / authority
# -----------------------------------------------------------------------------


def _classification_block(persistence_type: str) -> Dict[str, Any]:
    return {
        "persistence_type": persistence_type,
        "mutation_class": MUTATION_CLASS,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "upstream_truth_mutation_allowed": False,
        "advisory_only": False,
    }


def _authority_metadata(operation: str, cycle_id: str = "") -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6b",
        "operation": _safe_str(operation),
        "child_core_id": "contractor_builder_v1",
        "layer": "weekly_cycle.weekly_cycle_runner",
        "cycle_id": _safe_str(cycle_id),
        "can_execute": False,
        "can_mutate_upstream_truth": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
    }


def _prepare_payload(
    *,
    payload: Dict[str, Any],
    persistence_type: str,
    operation: str,
    cycle_id: str,
) -> Dict[str, Any]:
    body = dict(payload)
    body["classification"] = _classification_block(persistence_type)
    body["authority_metadata"] = _authority_metadata(operation, cycle_id)
    body["sealed"] = True
    return body


def _persist_json(
    *,
    path: Path,
    payload: Dict[str, Any],
    persistence_type: str,
    operation: str,
    cycle_id: str,
) -> None:
    governed_write_json(
        path=path,
        payload=_prepare_payload(
            payload=payload,
            persistence_type=persistence_type,
            operation=operation,
            cycle_id=cycle_id,
        ),
        mutation_class=MUTATION_CLASS,
        persistence_type=persistence_type,
        authority_metadata=_authority_metadata(operation, cycle_id),
    )


# -----------------------------------------------------------------------------
# Runner
# -----------------------------------------------------------------------------


def run_weekly_cycle(
    *,
    reporting_period_label: str,
    project_payloads: List[Dict[str, Any]],
    portfolio_project_map: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    cycle_id = build_receipt_id("weekly_cycle", "run_weekly_cycle")
    portfolio_project_map = portfolio_project_map or {}

    project_ids = [str(payload.get("project_id", "")) for payload in project_payloads]
    portfolio_ids = list(portfolio_project_map.keys())

    cycle_record = build_weekly_cycle_record(
        cycle_id=cycle_id,
        reporting_period_label=reporting_period_label,
        project_ids=project_ids,
        portfolio_ids=portfolio_ids,
    )
    cycle_record["cycle_status"] = "running"
    cycle_record["started_at"] = _utc_now_iso()

    project_reports: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []

    for payload in project_payloads:
        try:
            report = orchestrate_project_weekly_report(
                project_id=str(payload["project_id"]),
                reporting_period_label=reporting_period_label,
                workflow_snapshot=dict(payload.get("workflow_snapshot", {})),
                change_records=list(payload.get("change_records", [])),
                compliance_snapshot=dict(payload.get("compliance_snapshot", {})),
                router_snapshot=dict(payload.get("router_snapshot", {})),
                oracle_snapshot=dict(payload.get("oracle_snapshot", {})),
                decision_records=list(payload.get("decision_records", [])),
                risk_records=list(payload.get("risk_records", [])),
                assumption_records=list(payload.get("assumption_records", [])),
            )
            project_reports.append(report)
        except Exception as exc:
            errors.append(
                {
                    "project_id": str(payload.get("project_id", "")),
                    "error": str(exc),
                }
            )

    portfolio_reports: List[Dict[str, Any]] = []
    for portfolio_id, mapped_project_ids in portfolio_project_map.items():
        selected_reports = [
            report
            for report in project_reports
            if str(report.get("subject_id", "")) in set(mapped_project_ids)
        ]

        try:
            portfolio_reports.append(
                aggregate_portfolio_weekly_reports(
                    portfolio_id=portfolio_id,
                    reporting_period_label=reporting_period_label,
                    project_reports=selected_reports,
                )
            )
        except Exception as exc:
            errors.append(
                {
                    "portfolio_id": str(portfolio_id),
                    "error": str(exc),
                }
            )

    cycle_record["cycle_status"] = "completed_with_errors" if errors else "completed"
    cycle_record["completed_at"] = _utc_now_iso()
    cycle_record["project_report_count"] = len(project_reports)
    cycle_record["portfolio_report_count"] = len(portfolio_reports)
    cycle_record["error_count"] = len(errors)

    validation_errors = validate_weekly_cycle_record(cycle_record)
    if validation_errors:
        cycle_record["cycle_status"] = "invalid"
        cycle_record["validation_errors"] = validation_errors

    response = {
        "artifact_type": "contractor_weekly_cycle_response",
        "artifact_version": "northstar_weekly_cycle_response_v1",
        "status": cycle_record["cycle_status"],
        "cycle_record": cycle_record,
        "project_reports": project_reports,
        "portfolio_reports": portfolio_reports,
        "errors": errors,
        "execution_allowed": False,
        "approval_required": True,
    }

    _persist_json(
        path=get_weekly_cycle_state_path(),
        payload=cycle_record,
        persistence_type="contractor_weekly_cycle_state",
        operation="persist_weekly_cycle_state",
        cycle_id=cycle_id,
    )
    _persist_json(
        path=get_latest_weekly_cycle_response_path(),
        payload=response,
        persistence_type="contractor_latest_weekly_cycle_response",
        operation="persist_latest_weekly_cycle_response",
        cycle_id=cycle_id,
    )

    return response


# -----------------------------------------------------------------------------
# Readers
# -----------------------------------------------------------------------------


def load_weekly_cycle_state() -> Dict[str, Any]:
    return _load_json(get_weekly_cycle_state_path())


def load_latest_weekly_cycle_response() -> Dict[str, Any]:
    return _load_json(get_latest_weekly_cycle_response_path())