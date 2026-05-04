"""
Root API router for contractor_builder_v1.

This module mounts contractor_builder_v1 API surfaces under one canonical router.

Authority rule:
- This file only mounts routes.
- It does not own workflow, signoff, closeout, project record, dashboard,
  root-spine, state-authority, system-watcher, or external-pressure logic.
- Missing optional routes must not prevent the health route from loading.
"""

from __future__ import annotations

import importlib
from typing import Any, Dict, List, Optional

from fastapi import APIRouter


router = APIRouter(prefix="/contractor-builder", tags=["contractor_builder_v1"])

_ROUTE_STATUS: List[Dict[str, Any]] = []


def _include_optional_router(
    *,
    module_name: str,
    label: str,
    required: bool = False,
) -> bool:
    try:
        module = importlib.import_module(module_name)
        child_router = getattr(module, "router", None)

        if child_router is None:
            raise AttributeError("missing router attribute")

        router.include_router(child_router)

        _ROUTE_STATUS.append(
            {
                "label": label,
                "module": module_name,
                "included": True,
                "required": required,
                "reason": None,
            }
        )

        print(f"[CONTRACTOR ROUTE INCLUDED] {label}: {module_name}")
        return True

    except Exception as exc:
        reason = f"{type(exc).__name__}: {exc}"

        _ROUTE_STATUS.append(
            {
                "label": label,
                "module": module_name,
                "included": False,
                "required": required,
                "reason": reason,
            }
        )

        print(f"[CONTRACTOR ROUTE SKIPPED] {label}: {reason}")

        if required:
            raise

        return False


_PROJECTS_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_projects_api",
    label="projects",
)

_INTAKE_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_intake_api",
    label="intake",
)

_PROJECT_RECORD_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_project_record_api",
    label="project_record",
)

_WORKFLOW_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_workflow_api",
    label="workflow",
)

_CHANGE_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_change_api",
    label="change",
)

_CHANGE_SIGNOFF_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_change_signoff_api",
    label="change_signoff",
)

_DECISION_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_decision_api",
    label="decision",
)

_RISK_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_risk_api",
    label="risk",
)

_ASSUMPTION_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_assumption_api",
    label="assumption",
)

_COMPLY_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_comply_api",
    label="comply",
)

_ROUTER_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_router_api",
    label="router",
)

_ORACLE_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_oracle_api",
    label="oracle",
)

_REPORT_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_report_api",
    label="report",
)

_WEEKLY_CYCLE_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_weekly_cycle_api",
    label="weekly_cycle",
)

_PRE_INTERFACE_WATCHER_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_pre_interface_watcher",
    label="pre_interface_watcher",
)

_SIGNOFF_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_signoff_api",
    label="signoff",
)

_LIVE_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_live_dashboard_api",
    label="live_dashboard",
)

_PHASE_CLOSEOUT_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_phase_closeout_api",
    label="phase_closeout",
)

_DASHBOARD_READ_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_dashboard_read_api",
    label="dashboard_read",
)

_STATE_AUTHORITY_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_state_authority_api",
    label="state_authority",
)

_SYSTEM_WATCHER_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_system_watcher_api",
    label="system_watcher",
)

_ROOT_SPINE_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_root_spine_api",
    label="root_spine",
)

_EXTERNAL_PRESSURE_AVAILABLE = _include_optional_router(
    module_name="AI_GO.api.contractor_external_pressure_api",
    label="external_pressure",
)


def _route_available(label: str) -> bool:
    for item in _ROUTE_STATUS:
        if item.get("label") == label:
            return bool(item.get("included"))
    return False


def _route_reason(label: str) -> Optional[str]:
    for item in _ROUTE_STATUS:
        if item.get("label") == label:
            reason = item.get("reason")
            return str(reason) if reason else None
    return None


def _route_map() -> Dict[str, bool]:
    return {
        "projects": _route_available("projects"),
        "intake": _route_available("intake"),
        "project_record": _route_available("project_record"),
        "workflow": _route_available("workflow"),
        "change": _route_available("change"),
        "change_signoff": _route_available("change_signoff"),
        "decision": _route_available("decision"),
        "risk": _route_available("risk"),
        "assumption": _route_available("assumption"),
        "comply": _route_available("comply"),
        "router": _route_available("router"),
        "oracle": _route_available("oracle"),
        "report": _route_available("report"),
        "weekly_cycle": _route_available("weekly_cycle"),
        "pre_interface_watcher": _route_available("pre_interface_watcher"),
        "signoff": _route_available("signoff"),
        "live_dashboard": _route_available("live_dashboard"),
        "phase_closeout": _route_available("phase_closeout"),
        "dashboard_read": _route_available("dashboard_read"),
        "state_authority": _route_available("state_authority"),
        "system_watcher": _route_available("system_watcher"),
        "root_spine": _route_available("root_spine"),
        "external_pressure": _route_available("external_pressure"),
    }


def _missing_routes() -> List[Dict[str, Any]]:
    missing: List[Dict[str, Any]] = []

    for item in _ROUTE_STATUS:
        if item.get("included") is True:
            continue

        missing.append(
            {
                "label": item.get("label"),
                "module": item.get("module"),
                "required": bool(item.get("required")),
                "reason": item.get("reason"),
            }
        )

    return missing


@router.get("/health")
def contractor_builder_health() -> dict:
    return {
        "child_core_id": "contractor_builder_v1",
        "status": "ok",
        "mode": "advisory",
        "approval_required": True,
        "execution_allowed": False,
        "mutation_allowed": False,
        "router_role": "mount_only",
        "routes": _route_map(),
        "missing_routes": _missing_routes(),
        "route_status": _ROUTE_STATUS,
    }