"""
Agent call registry for contractor_builder_v1 weekly cycle.

This registry declares the canonical read-only call surfaces the weekly cycle expects
to consume logically. It is a visibility and orchestration map, not an execution
engine by itself.
"""

from __future__ import annotations

from typing import Dict, List, Optional

CONTRACTOR_WEEKLY_AGENT_CALLS: Dict[str, Dict[str, str]] = {
    "workflow_snapshot": {
        "module": "workflow",
        "purpose": "collect current workflow posture for project weekly reporting",
    },
    "change_records": {
        "module": "change",
        "purpose": "collect change history and approved totals",
    },
    "compliance_snapshot": {
        "module": "comply",
        "purpose": "collect blocking compliance posture",
    },
    "router_snapshot": {
        "module": "router",
        "purpose": "collect routing conflict and cascade posture",
    },
    "oracle_snapshot": {
        "module": "oracle",
        "purpose": "collect external pressure posture",
    },
    "decision_records": {
        "module": "decision_log",
        "purpose": "collect internal decision governance history",
    },
    "risk_records": {
        "module": "risk_register",
        "purpose": "collect current risk posture",
    },
    "assumption_records": {
        "module": "assumption_log",
        "purpose": "collect current assumption posture",
    },
    "project_weekly_report": {
        "module": "report",
        "purpose": "build project weekly report from collected snapshots",
    },
    "portfolio_weekly_report": {
        "module": "report",
        "purpose": "aggregate project weekly reports into portfolio report",
    },
}


def list_registered_weekly_calls() -> List[str]:
    """
    Return the registered weekly call names.
    """
    return list(CONTRACTOR_WEEKLY_AGENT_CALLS.keys())


def get_registered_weekly_call(call_name: str) -> Optional[Dict[str, str]]:
    """
    Return one registered weekly call descriptor if present.
    """
    descriptor = CONTRACTOR_WEEKLY_AGENT_CALLS.get(call_name)
    return dict(descriptor) if descriptor else None