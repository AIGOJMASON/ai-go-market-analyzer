"""
Oracle surfaces for contractor_builder_v1.

This package owns the external pressure advisory branch for contractor projects:
- market snapshot registry
- snapshot publication
- shock classification
- exposure profiles
- projection engine
- risk radar
- procurement advisory
- oracle receipts
"""

from .oracle_schema import (
    ORACLE_SCHEMA_VERSION,
    MARKET_DOMAIN_ENUM,
    SHOCK_DIRECTION_ENUM,
    SHOCK_SEVERITY_ENUM,
    EXPOSURE_LEVEL_ENUM,
    PROCUREMENT_POSTURE_ENUM,
    build_market_snapshot,
    build_shock_record,
    build_exposure_profile,
    build_projection_record,
    build_risk_radar_record,
    build_procurement_advisory_record,
    validate_market_snapshot,
    validate_exposure_profile,
)
from .market_snapshot_registry import (
    ORACLE_MARKET_SNAPSHOT_REGISTRY,
    get_registered_snapshot,
    list_registered_snapshots,
)
from .snapshot_publisher import (
    publish_market_snapshot,
)
from .shock_classifier import (
    classify_shock_record,
)
from .exposure_profile_runtime import (
    build_project_exposure_profile,
)
from .projection_engine import (
    build_oracle_projection,
)
from .risk_radar_runtime import (
    build_risk_radar,
)
from .procurement_advisory import (
    build_procurement_advisory,
)
from .oracle_receipt_builder import (
    build_oracle_receipt,
    write_oracle_receipt,
)

__all__ = [
    "ORACLE_SCHEMA_VERSION",
    "MARKET_DOMAIN_ENUM",
    "SHOCK_DIRECTION_ENUM",
    "SHOCK_SEVERITY_ENUM",
    "EXPOSURE_LEVEL_ENUM",
    "PROCUREMENT_POSTURE_ENUM",
    "build_market_snapshot",
    "build_shock_record",
    "build_exposure_profile",
    "build_projection_record",
    "build_risk_radar_record",
    "build_procurement_advisory_record",
    "validate_market_snapshot",
    "validate_exposure_profile",
    "ORACLE_MARKET_SNAPSHOT_REGISTRY",
    "get_registered_snapshot",
    "list_registered_snapshots",
    "publish_market_snapshot",
    "classify_shock_record",
    "build_project_exposure_profile",
    "build_oracle_projection",
    "build_risk_radar",
    "build_procurement_advisory",
    "build_oracle_receipt",
    "write_oracle_receipt",
]