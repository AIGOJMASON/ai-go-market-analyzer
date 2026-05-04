"""
UI runtime surfaces for contractor_builder_v1.

This package owns:
- contractor dashboard runtime
- project intake/project record surfaces
- project record runtime loading
"""

from .contractor_dashboard_runner import run_contractor_dashboard
from .contractor_dashboard_builder import build_contractor_dashboard_view
from .project_intake_runner import create_project_from_form
from .project_intake_builder import build_project_intake_created_view
from .project_record_builder import (
    build_project_record_view,
    build_persistent_project_record_view,
)
from .project_record_runtime import load_project_record

__all__ = [
    "run_contractor_dashboard",
    "build_contractor_dashboard_view",
    "create_project_from_form",
    "build_project_intake_created_view",
    "build_project_record_view",
    "build_persistent_project_record_view",
    "load_project_record",
]