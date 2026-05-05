"""
Report surfaces for contractor_builder_v1.

This package owns the PM-gated reporting branch for contractor projects:
- report schema
- deterministic block builders
- project weekly reports
- portfolio weekly reports
- summary draft generation
- approval runtime
- report receipts
"""

from .report_schema import (
    REPORT_SCHEMA_VERSION,
    REPORT_TYPE_ENUM,
    REPORT_STATUS_ENUM,
    build_report_shell,
    validate_report_record,
    get_report_template,
)
from .deterministic_block_builder import (
    build_project_deterministic_block,
    build_portfolio_deterministic_block,
)
from .project_weekly_builder import (
    build_project_weekly_report,
)
from .portfolio_weekly_builder import (
    build_portfolio_weekly_report,
)
from .summary_draft_builder import (
    build_project_summary_draft,
    build_portfolio_summary_draft,
)
from .approval_runtime import (
    apply_report_pm_approval,
    can_approve_report,
    can_archive_report,
    transition_report_status,
)
from .report_receipt_builder import (
    build_report_receipt,
    write_report_receipt,
)

__all__ = [
    "REPORT_SCHEMA_VERSION",
    "REPORT_TYPE_ENUM",
    "REPORT_STATUS_ENUM",
    "build_report_shell",
    "validate_report_record",
    "get_report_template",
    "build_project_deterministic_block",
    "build_portfolio_deterministic_block",
    "build_project_weekly_report",
    "build_portfolio_weekly_report",
    "build_project_summary_draft",
    "build_portfolio_summary_draft",
    "apply_report_pm_approval",
    "can_approve_report",
    "can_archive_report",
    "transition_report_status",
    "build_report_receipt",
    "write_report_receipt",
]