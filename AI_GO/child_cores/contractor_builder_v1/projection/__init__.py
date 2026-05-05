"""
Projection surfaces for contractor_builder_v1.

This package owns the final read-only payload assembly branch for contractor views:
- operator projection runtime
- project projection
- portfolio projection
- decision projection
- change projection
- compliance projection
- risk projection
- latest payload state persistence
"""

from .operator_projection_runtime import build_contractor_operator_payload
from .project_projection import build_project_projection
from .portfolio_projection import build_portfolio_projection
from .decision_projection import build_decision_projection
from .change_projection import build_change_projection
from .compliance_projection import build_compliance_projection
from .risk_projection import build_risk_projection
from .latest_payload_state import (
    get_latest_payload_path,
    get_by_request_root,
    persist_latest_operator_payload,
)

__all__ = [
    "build_contractor_operator_payload",
    "build_project_projection",
    "build_portfolio_projection",
    "build_decision_projection",
    "build_change_projection",
    "build_compliance_projection",
    "build_risk_projection",
    "get_latest_payload_path",
    "get_by_request_root",
    "persist_latest_operator_payload",
]