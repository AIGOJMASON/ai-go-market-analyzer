"""
Router surfaces for contractor_builder_v1.

This package owns the routing and conflict advisory branch for contractor projects:
- router schema
- schedule block persistence
- conflict detection
- capacity detection
- cascade risk classification
- router receipts
"""

from .router_schema import (
    ROUTER_SCHEMA_VERSION,
    BLOCK_TYPE_ENUM,
    CONFLICT_TYPE_ENUM,
    CAPACITY_STATUS_ENUM,
    CASCADE_RISK_ENUM,
    build_schedule_block,
    validate_schedule_block,
    build_conflict_record,
    build_capacity_record,
    build_cascade_risk_record,
    get_schedule_block_template,
)
from .schedule_block_runtime import (
    get_schedule_blocks_path,
    create_schedule_block_record,
    upsert_schedule_blocks,
    load_schedule_blocks,
)
from .conflict_detector import (
    detect_schedule_conflicts,
)
from .capacity_detector import (
    build_capacity_snapshot,
    detect_capacity_status,
)
from .cascade_risk_runtime import (
    classify_cascade_risk,
    build_cascade_risk_from_conflicts,
)
from .router_receipt_builder import (
    build_router_receipt,
    write_router_receipt,
)

__all__ = [
    "ROUTER_SCHEMA_VERSION",
    "BLOCK_TYPE_ENUM",
    "CONFLICT_TYPE_ENUM",
    "CAPACITY_STATUS_ENUM",
    "CASCADE_RISK_ENUM",
    "build_schedule_block",
    "validate_schedule_block",
    "build_conflict_record",
    "build_capacity_record",
    "build_cascade_risk_record",
    "get_schedule_block_template",
    "get_schedule_blocks_path",
    "create_schedule_block_record",
    "upsert_schedule_blocks",
    "load_schedule_blocks",
    "detect_schedule_conflicts",
    "build_capacity_snapshot",
    "detect_capacity_status",
    "classify_cascade_risk",
    "build_cascade_risk_from_conflicts",
    "build_router_receipt",
    "write_router_receipt",
]