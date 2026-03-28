from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from .return_path_registry import REGISTRY


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _missing_required_fields(payload: Dict[str, Any], required: Iterable[str]) -> List[str]:
    return [field for field in required if field not in payload]


def _build_success_receipt(
    target_core: str,
    requester_profile: str,
    advisory_posture: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "external_memory_return_receipt",
        "artifact_type": REGISTRY["emitted_artifact_type"],
        "status": "success",
        "target_core": target_core,
        "requester_profile": requester_profile,
        "advisory_posture": advisory_posture,
        "observed_at": _utc_now(),
    }


def _build_rejection_receipt(
    source_artifact_type: str,
    target_core: str,
    requester_profile: str,
    failure_reason: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "external_memory_return_rejection_receipt",
        "artifact_type": source_artifact_type,
        "status": "failed",
        "target_core": target_core,
        "requester_profile": requester_profile,
        "failure_reason": failure_reason,
        "observed_at": _utc_now(),
    }


def _advisory_posture_from_source(source_artifact: Dict[str, Any]) -> str:
    artifact_type = source_artifact["artifact_type"]
    if artifact_type == "external_memory_pattern_aggregation":
        posture = source_artifact["pattern_posture"]
        if posture == "strong_pattern_context":
            return "strong_context"
        if posture == "useful_pattern_context":
            return "useful_context"
        return "light_context"

    promoted_count = int(source_artifact["promoted_record_count"])
    if promoted_count >= 3:
        return "strong_context"
    if promoted_count == 2:
        return "useful_context"
    return "light_context"


def _return_panel_from_source(source_artifact: Dict[str, Any]) -> Dict[str, Any]:
    artifact_type = source_artifact["artifact_type"]
    if artifact_type == "external_memory_pattern_aggregation":
        return {
            "source_type": "pattern_aggregation",
            "recurrence_count": source_artifact["recurrence_count"],
            "temporal_span_days": source_artifact["temporal_span_days"],
            "dominant_symbol": source_artifact["dominant_symbol"],
            "dominant_sector": source_artifact["dominant_sector"],
            "pattern_strength": source_artifact["pattern_strength"],
            "historical_confirmation": source_artifact["historical_confirmation"],
            "pattern_summary": source_artifact["pattern_summary"],
            "promoted_memory_ids": source_artifact["promoted_memory_ids"],
        }

    promoted_records = source_artifact.get("promoted_records", [])
    promoted_memory_ids = [str(record.get("memory_id")) for record in promoted_records]
    return {
        "source_type": "promotion",
        "promoted_record_count": source_artifact["promoted_record_count"],
        "promoted_memory_ids": promoted_memory_ids,
    }


def build_return_packet(
    source_artifact: Dict[str, Any],
    source_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(source_artifact, dict):
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type="unknown",
                target_core="unknown",
                requester_profile="unknown",
                failure_reason="invalid_return_source_artifact_type",
            ),
        }

    target_core = str(source_artifact.get("target_core", "unknown"))
    requester_profile = str(source_artifact.get("requester_profile", "unknown"))
    artifact_type = str(source_artifact.get("artifact_type", "unknown"))

    if not isinstance(source_receipt, dict):
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="invalid_return_source_receipt_type",
            ),
        }

    if artifact_type not in REGISTRY["accepted_source_artifact_types"]:
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="invalid_return_source_artifact_type",
            ),
        }

    missing_artifact_common = _missing_required_fields(
        source_artifact,
        REGISTRY["required_common_artifact_fields"],
    )
    if missing_artifact_common:
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="missing_required_fields",
            ),
        }

    missing_receipt = _missing_required_fields(
        source_receipt,
        REGISTRY["required_common_receipt_fields"],
    )
    if missing_receipt:
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="missing_required_fields",
            ),
        }

    expected_receipt_type = REGISTRY["accepted_source_receipt_types"][artifact_type]
    if source_receipt["receipt_type"] != expected_receipt_type:
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="invalid_return_source_receipt_type",
            ),
        }

    if (
        source_receipt.get("artifact_type") != artifact_type
        or source_receipt.get("target_core") != target_core
        or source_receipt.get("requester_profile") != requester_profile
    ):
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="artifact_receipt_misalignment",
            ),
        }

    if target_core not in REGISTRY["allowed_target_cores"]:
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="target_not_allowed",
            ),
        }

    if requester_profile not in REGISTRY["allowed_requester_profiles"]:
        return {
            "status": "failed",
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_core=target_core,
                requester_profile=requester_profile,
                failure_reason="requester_profile_not_allowed",
            ),
        }

    if artifact_type == "external_memory_promotion":
        missing_specific = _missing_required_fields(
            source_artifact,
            REGISTRY["required_promotion_fields"],
        )
        if missing_specific:
            return {
                "status": "failed",
                "receipt": _build_rejection_receipt(
                    source_artifact_type=artifact_type,
                    target_core=target_core,
                    requester_profile=requester_profile,
                    failure_reason="missing_required_fields",
                ),
            }
        if source_artifact.get("promotion_status") != "promoted":
            return {
                "status": "failed",
                "receipt": _build_rejection_receipt(
                    source_artifact_type=artifact_type,
                    target_core=target_core,
                    requester_profile=requester_profile,
                    failure_reason="source_status_not_accepted",
                ),
            }

    if artifact_type == "external_memory_pattern_aggregation":
        missing_specific = _missing_required_fields(
            source_artifact,
            REGISTRY["required_pattern_aggregation_fields"],
        )
        if missing_specific:
            return {
                "status": "failed",
                "receipt": _build_rejection_receipt(
                    source_artifact_type=artifact_type,
                    target_core=target_core,
                    requester_profile=requester_profile,
                    failure_reason="missing_required_fields",
                ),
            }
        if source_artifact.get("aggregation_status") != "aggregated":
            return {
                "status": "failed",
                "receipt": _build_rejection_receipt(
                    source_artifact_type=artifact_type,
                    target_core=target_core,
                    requester_profile=requester_profile,
                    failure_reason="source_status_not_accepted",
                ),
            }

    advisory_posture = _advisory_posture_from_source(source_artifact)
    return_panel = _return_panel_from_source(source_artifact)

    artifact = {
        "artifact_type": REGISTRY["emitted_artifact_type"],
        "target_core": target_core,
        "requester_profile": requester_profile,
        "advisory_posture": advisory_posture,
        "external_memory_return_panel": return_panel,
        "external_memory_provenance_refs": list(source_artifact.get("provenance_refs", [])),
        "source_artifact_type": artifact_type,
    }

    receipt = _build_success_receipt(
        target_core=target_core,
        requester_profile=requester_profile,
        advisory_posture=advisory_posture,
    )

    return {
        "status": "ok",
        "artifact": artifact,
        "receipt": receipt,
    }