"""
Explanation surfaces for contractor_builder_v1.

This package owns the bounded explanation branch for contractor operator views:
- operator explainer
- weekly report interpreter
- explanation layer doctrine
"""

from .operator_explainer import build_contractor_operator_explanation
from .weekly_report_interpreter import (
    interpret_project_weekly_report,
    interpret_portfolio_weekly_report,
)

__all__ = [
    "build_contractor_operator_explanation",
    "interpret_project_weekly_report",
    "interpret_portfolio_weekly_report",
]