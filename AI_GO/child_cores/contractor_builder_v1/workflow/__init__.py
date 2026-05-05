"""
Workflow surfaces for contractor_builder_v1.

This package owns the phase backbone for contractor projects:
- workflow schemas
- phase templates
- phase instances
- client signoff gates
- workflow runtime
- drift detection
- workflow receipts
"""

from .workflow_schema import WORKFLOW_SCHEMA_VERSION, get_workflow_record_template
from .phase_template_schema import (
    PHASE_TEMPLATE_SCHEMA_VERSION,
    build_phase_template,
    validate_phase_template,
)
from .phase_instance_schema import (
    PHASE_INSTANCE_SCHEMA_VERSION,
    build_phase_instance,
    validate_phase_instance,
)
from .client_gate_schema import (
    CLIENT_GATE_SCHEMA_VERSION,
    build_client_gate_requirement,
    build_client_signoff_record,
)
from .workflow_runtime import (
    build_workflow_state_record,
    get_phase_history_path,
    get_phase_instances_path,
    initialize_workflow_for_project,
    upsert_phase_instances,
)
from .phase_template_engine import generate_phase_instances_from_template
from .drift_detector import build_phase_drift_record, detect_phase_drift
from .signoff_runtime import append_client_signoff_record, get_client_signoffs_path
from .workflow_receipt_builder import build_workflow_receipt, write_workflow_receipt

__all__ = [
    "WORKFLOW_SCHEMA_VERSION",
    "get_workflow_record_template",
    "PHASE_TEMPLATE_SCHEMA_VERSION",
    "build_phase_template",
    "validate_phase_template",
    "PHASE_INSTANCE_SCHEMA_VERSION",
    "build_phase_instance",
    "validate_phase_instance",
    "CLIENT_GATE_SCHEMA_VERSION",
    "build_client_gate_requirement",
    "build_client_signoff_record",
    "build_workflow_state_record",
    "get_phase_history_path",
    "get_phase_instances_path",
    "initialize_workflow_for_project",
    "upsert_phase_instances",
    "generate_phase_instances_from_template",
    "build_phase_drift_record",
    "detect_phase_drift",
    "append_client_signoff_record",
    "get_client_signoffs_path",
    "build_workflow_receipt",
    "write_workflow_receipt",
]