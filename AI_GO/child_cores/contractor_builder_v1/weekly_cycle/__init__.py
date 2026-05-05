"""
Weekly cycle surfaces for contractor_builder_v1.

This package owns the read-only orchestration branch for contractor projects:
- weekly cycle schema
- snapshot collection
- agent call registry
- project report orchestration
- portfolio aggregation
- weekly cycle receipts
"""

from .weekly_cycle_schema import (
    WEEKLY_CYCLE_SCHEMA_VERSION,
    WEEKLY_CYCLE_STATUS_ENUM,
    build_weekly_cycle_record,
    validate_weekly_cycle_record,
    get_weekly_cycle_template,
)
from .snapshot_collector import (
    build_project_module_snapshot,
    collect_project_snapshots,
)
from .agent_call_registry import (
    CONTRACTOR_WEEKLY_AGENT_CALLS,
    list_registered_weekly_calls,
    get_registered_weekly_call,
)
from .project_report_orchestrator import (
    orchestrate_project_weekly_report,
)
from .portfolio_aggregator import (
    aggregate_portfolio_weekly_reports,
)
from .weekly_cycle_runner import (
    get_weekly_cycle_state_path,
    get_latest_weekly_cycle_response_path,
    get_weekly_cycle_receipts_root,
    run_weekly_cycle,
)
from .weekly_cycle_receipt_builder import (
    build_weekly_cycle_receipt,
    write_weekly_cycle_receipt,
)

__all__ = [
    "WEEKLY_CYCLE_SCHEMA_VERSION",
    "WEEKLY_CYCLE_STATUS_ENUM",
    "build_weekly_cycle_record",
    "validate_weekly_cycle_record",
    "get_weekly_cycle_template",
    "build_project_module_snapshot",
    "collect_project_snapshots",
    "CONTRACTOR_WEEKLY_AGENT_CALLS",
    "list_registered_weekly_calls",
    "get_registered_weekly_call",
    "orchestrate_project_weekly_report",
    "aggregate_portfolio_weekly_reports",
    "get_weekly_cycle_state_path",
    "get_latest_weekly_cycle_response_path",
    "get_weekly_cycle_receipts_root",
    "run_weekly_cycle",
    "build_weekly_cycle_receipt",
    "write_weekly_cycle_receipt",
]