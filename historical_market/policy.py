"""
AI_GO Historical Market Policy

Purpose:
    Defines hard rules for the historical market subsystem.

This module is intentionally lean and structural.
It does not perform runtime execution or source fetching.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Mapping, Set


@dataclass(frozen=True)
class HistoricalMarketPolicy:
    subsystem_id: str = "historical_market"
    append_only_required: bool = True
    public_write_allowed: bool = False
    execution_authority_allowed: bool = False
    recommendation_mutation_allowed: bool = False
    live_ingress_owner: bool = False
    raw_and_curated_must_be_separated: bool = True
    write_receipts_required: bool = True
    source_lineage_required: bool = True

    allowed_asset_classes: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "equity",
                "etf",
                "commodity",
                "index",
                "forex",
                "crypto",
            }
        )
    )

    allowed_timeframes: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "1m",
                "5m",
                "15m",
                "30m",
                "60m",
                "1d",
                "1wk",
                "1mo",
            }
        )
    )

    allowed_raw_record_types: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "market_bar_record",
            }
        )
    )

    allowed_curated_record_types: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "historical_intake_event",
                "historical_merge_event",
                "historical_outcome_event",
                "historical_setup_pattern",
                "historical_asset_relationship",
            }
        )
    )

    timestamp_fields_by_record_type: Mapping[str, str] = field(
        default_factory=lambda: {
            "market_bar_record": "bar_timestamp",
            "historical_intake_event": "intake_timestamp",
            "historical_merge_event": "merge_timestamp",
            "historical_outcome_event": "outcome_timestamp",
            "historical_setup_pattern": "detected_at",
            "historical_asset_relationship": "measured_at",
        }
    )

    required_common_fields: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "record_type",
                "source_lineage",
                "written_at",
            }
        )
    )


POLICY = HistoricalMarketPolicy()


def get_historical_market_policy() -> HistoricalMarketPolicy:
    """
    Return the canonical policy object.
    """
    return POLICY


def validate_asset_class(asset_class: str) -> None:
    if asset_class not in POLICY.allowed_asset_classes:
        raise ValueError(
            f"invalid_asset_class:{asset_class}; "
            f"allowed={sorted(POLICY.allowed_asset_classes)}"
        )


def validate_timeframe(timeframe: str) -> None:
    if timeframe not in POLICY.allowed_timeframes:
        raise ValueError(
            f"invalid_timeframe:{timeframe}; "
            f"allowed={sorted(POLICY.allowed_timeframes)}"
        )


def validate_record_type(record_type: str) -> None:
    allowed: Set[str] = set(POLICY.allowed_raw_record_types) | set(
        POLICY.allowed_curated_record_types
    )
    if record_type not in allowed:
        raise ValueError(f"invalid_record_type:{record_type}")


def get_required_timestamp_field(record_type: str) -> str:
    validate_record_type(record_type)
    timestamp_field = POLICY.timestamp_fields_by_record_type.get(record_type)
    if not timestamp_field:
        raise ValueError(f"missing_timestamp_policy_for_record_type:{record_type}")
    return timestamp_field


def validate_common_fields(record: Dict[str, object]) -> None:
    missing = [field for field in POLICY.required_common_fields if field not in record]
    if missing:
        raise ValueError(f"missing_common_fields:{','.join(missing)}")


def validate_timestamp_presence(record: Dict[str, object]) -> None:
    record_type = str(record.get("record_type", "")).strip()
    validate_record_type(record_type)
    timestamp_field = get_required_timestamp_field(record_type)
    if timestamp_field not in record:
        raise ValueError(
            f"missing_timestamp_field:{timestamp_field}:for_record_type:{record_type}"
        )


def validate_source_lineage(record: Dict[str, object]) -> None:
    value = record.get("source_lineage")
    if not value:
        raise ValueError("missing_source_lineage")


def validate_append_only_preconditions(record: Dict[str, object]) -> None:
    validate_common_fields(record)
    validate_timestamp_presence(record)
    validate_source_lineage(record)