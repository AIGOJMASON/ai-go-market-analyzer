from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Tuple

from .pattern_aggregation_receipt_builder import (
    build_rejection_receipt,
    build_success_receipt,
)
from .pattern_aggregation_registry import REGISTRY


def _parse_iso8601(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _missing_required_fields(payload: Dict[str, Any], required: Iterable[str]) -> List[str]:
    return [field for field in required if field not in payload]


def _validate_promoted_record(record: Dict[str, Any]) -> bool:
    required = REGISTRY["required_promoted_record_fields"]
    return isinstance(record, dict) and not _missing_required_fields(record, required)


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def _recency_weight(span_days: int) -> float:
    if span_days <= 2:
        return 1.00
    if span_days <= 7:
        return 0.85
    if span_days <= 14:
        return 0.70
    if span_days <= 30:
        return 0.50
    return 0.20


def _choose_dominant_value(
    records: List[Dict[str, Any]],
    field_name: str,
) -> str:
    counts: Counter[str] = Counter()
    weights: defaultdict[str, float] = defaultdict(float)
    for record in records:
        value = str(record.get(field_name, "") or "").strip()
        if not value:
            continue
        counts[value] += 1
        try:
            weights[value] += float(record.get("adjusted_weight", 0.0))
        except (TypeError, ValueError):
            pass

    if not counts:
        return ""

    most_common_count = max(counts.values())
    candidates = [key for key, count in counts.items() if count == most_common_count]
    if len(candidates) == 1:
        return candidates[0]

    candidates.sort(key=lambda key: weights[key], reverse=True)
    return candidates[0]


def _pattern_strength(score: float) -> str:
    if score < 0.35:
        return "weak_pattern"
    if score < 0.60:
        return "forming_pattern"
    if score < 0.82:
        return "strong_pattern"
    return "dominant_pattern"


def _pattern_posture(strength: str) -> str:
    if strength == "weak_pattern":
        return "light_pattern_context"
    if strength == "forming_pattern":
        return "useful_pattern_context"
    return "strong_pattern_context"


def _historical_confirmation(recurrence_count: int) -> str:
    if recurrence_count <= 1:
        return "low_confirmation"
    if recurrence_count <= 3:
        return "moderate_confirmation"
    return "high_confirmation"


def _pattern_summary(
    recurrence_count: int,
    dominant_symbol: str,
    dominant_sector: str,
    temporal_span_days: int,
    pattern_strength: str,
    historical_confirmation: str,
) -> str:
    focus = dominant_symbol or dominant_sector or "mixed memory context"
    return (
        f"{recurrence_count} promoted records around {focus} across "
        f"{temporal_span_days} day span; {pattern_strength}; {historical_confirmation}."
    )


def aggregate_pattern(
    promotion_artifact: Dict[str, Any],
    promotion_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(promotion_artifact, dict):
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type="unknown",
                target_core="unknown",
                requester_profile="unknown",
                failure_reason="invalid_promotion_artifact_type",
            ),
        }

    target_core = str(promotion_artifact.get("target_core", "unknown"))
    requester_profile = str(promotion_artifact.get("requester_profile", "unknown"))

    if not isinstance(promotion_receipt, dict):
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact.get("artifact_type", "unknown"),
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="invalid_promotion_receipt_type",
            ),
        }

    missing_artifact = _missing_required_fields(
        promotion_artifact,
        REGISTRY["required_promotion_artifact_fields"],
    )
    if missing_artifact:
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact.get("artifact_type", "unknown"),
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="missing_required_fields",
            ),
        }

    missing_receipt = _missing_required_fields(
        promotion_receipt,
        REGISTRY["required_promotion_receipt_fields"],
    )
    if missing_receipt:
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="missing_required_fields",
            ),
        }

    if promotion_artifact["artifact_type"] != REGISTRY["accepted_artifact_type"]:
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="invalid_promotion_artifact_type",
            ),
        }

    if promotion_receipt["receipt_type"] != REGISTRY["accepted_receipt_type"]:
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="invalid_promotion_receipt_type",
            ),
        }

    if (
        promotion_receipt.get("artifact_type") != promotion_artifact["artifact_type"]
        or promotion_receipt.get("target_core") != target_core
        or promotion_receipt.get("requester_profile") != requester_profile
    ):
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="artifact_receipt_misalignment",
            ),
        }

    if target_core not in REGISTRY["allowed_target_cores"]:
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="target_not_allowed",
            ),
        }

    if requester_profile not in REGISTRY["allowed_requester_profiles"]:
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="requester_profile_not_allowed",
            ),
        }

    if promotion_artifact.get("promotion_status") != "promoted":
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="promotion_status_not_promoted",
            ),
        }

    promoted_records = promotion_artifact.get("promoted_records", [])
    if not isinstance(promoted_records, list) or not promoted_records:
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="empty_promoted_records",
            ),
        }

    if any(not _validate_promoted_record(record) for record in promoted_records):
        return {
            "status": "failed",
            "receipt": build_rejection_receipt(
                artifact_type=promotion_artifact["artifact_type"],
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="invalid_record_shape",
            ),
        }

    recurrence_count = len(promoted_records)
    adjusted_weights = [float(record["adjusted_weight"]) for record in promoted_records]
    observed_times = [_parse_iso8601(str(record["observed_at"])) for record in promoted_records]
    earliest = min(observed_times)
    latest = max(observed_times)
    temporal_span_days = max((latest - earliest).days, 0)
    recency_weight = _recency_weight(temporal_span_days)

    normalized_recurrence_strength = min(recurrence_count / 5.0, 1.0)
    normalized_adjusted_weight_mean = min(_mean(adjusted_weights) / 100.0, 1.0)
    aggregation_score = round(
        (
            normalized_recurrence_strength * 0.45
            + normalized_adjusted_weight_mean * 0.35
            + recency_weight * 0.20
        ),
        4,
    )

    dominant_symbol = _choose_dominant_value(promoted_records, "symbol")
    dominant_sector = _choose_dominant_value(promoted_records, "sector")
    pattern_strength = _pattern_strength(aggregation_score)
    pattern_posture = _pattern_posture(pattern_strength)
    historical_confirmation = _historical_confirmation(recurrence_count)
    promoted_memory_ids = [str(record["memory_id"]) for record in promoted_records]
    pattern_summary = _pattern_summary(
        recurrence_count=recurrence_count,
        dominant_symbol=dominant_symbol,
        dominant_sector=dominant_sector,
        temporal_span_days=temporal_span_days,
        pattern_strength=pattern_strength,
        historical_confirmation=historical_confirmation,
    )

    artifact = {
        "artifact_type": REGISTRY["emitted_artifact_type"],
        "source_artifact_type": promotion_artifact["artifact_type"],
        "target_core": target_core,
        "requester_profile": requester_profile,
        "aggregation_status": "aggregated",
        "promoted_record_count": promotion_artifact["promoted_record_count"],
        "recurrence_count": recurrence_count,
        "temporal_span_days": temporal_span_days,
        "recency_weight": recency_weight,
        "dominant_symbol": dominant_symbol,
        "dominant_sector": dominant_sector,
        "pattern_strength": pattern_strength,
        "pattern_posture": pattern_posture,
        "historical_confirmation": historical_confirmation,
        "promoted_memory_ids": promoted_memory_ids,
        "aggregation_score": aggregation_score,
        "pattern_summary": pattern_summary,
        "provenance_refs": list(promotion_artifact.get("provenance_refs", [])),
        "upstream_receipt_type": promotion_receipt["receipt_type"],
    }

    receipt = build_success_receipt(
        artifact_type=artifact["artifact_type"],
        target_core=target_core,
        requester_profile=requester_profile,
        recurrence_count=recurrence_count,
        pattern_strength=pattern_strength,
        historical_confirmation=historical_confirmation,
    )

    return {
        "status": "ok",
        "artifact": artifact,
        "receipt": receipt,
    }