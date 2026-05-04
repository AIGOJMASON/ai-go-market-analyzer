# AI_GO/EXTERNAL_MEMORY/return_path/return_path_runtime.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from .return_path_registry import REGISTRY


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _missing_required_fields(payload: Dict[str, Any], required: Iterable[str]) -> List[str]:
    return [field for field in required if field not in payload]


def _target_child_core_from_source(source_artifact: Dict[str, Any]) -> str:
    return str(
        source_artifact.get("target_child_core")
        or source_artifact.get("target_core")
        or "unknown"
    )


def _build_success_receipt(
    target_child_core: str,
    requester_profile: str,
    advisory_posture: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": REGISTRY["emitted_receipt_type"],
        "receipt_type": REGISTRY["emitted_receipt_type"],
        "status": "success",
        "target_child_core": target_child_core,
        "requester_profile": requester_profile,
        "advisory_posture": advisory_posture,
        "observed_at": _utc_now(),
    }


def _build_rejection_receipt(
    source_artifact_type: str,
    target_child_core: str,
    requester_profile: str,
    failure_reason: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": REGISTRY["emitted_rejection_receipt_type"],
        "receipt_type": REGISTRY["emitted_rejection_receipt_type"],
        "status": "failed",
        "source_artifact_type": source_artifact_type,
        "target_child_core": target_child_core,
        "requester_profile": requester_profile,
        "failure_reason": failure_reason,
        "observed_at": _utc_now(),
    }


def _advisory_posture_from_source(source_artifact: Dict[str, Any]) -> str:
    artifact_type = str(source_artifact["artifact_type"])

    if artifact_type == "external_memory_pattern_aggregation":
        posture = str(source_artifact.get("pattern_posture", "light_pattern_context"))
        if posture == "strong_pattern_context":
            return "strong_context"
        if posture == "useful_pattern_context":
            return "useful_context"
        return "light_context"

    record_count = int(source_artifact.get("record_count", 0))
    if record_count >= 3:
        return "strong_context"
    if record_count == 2:
        return "useful_context"
    return "light_context"


def _memory_context_panel_from_source(source_artifact: Dict[str, Any]) -> Dict[str, Any]:
    artifact_type = str(source_artifact["artifact_type"])

    if artifact_type == "external_memory_pattern_aggregation":
        return {
            "state": "present",
            "source_type": "pattern_aggregation",
            "recurrence_count": source_artifact["recurrence_count"],
            "temporal_span_days": source_artifact["temporal_span_days"],
            "recency_weight": source_artifact["recency_weight"],
            "dominant_symbol": source_artifact["dominant_symbol"],
            "dominant_sector": source_artifact["dominant_sector"],
            "pattern_strength": source_artifact["pattern_strength"],
            "pattern_posture": source_artifact["pattern_posture"],
            "historical_confirmation": source_artifact["historical_confirmation"],
            "pattern_summary": source_artifact["pattern_summary"],
            "promoted_memory_ids": list(source_artifact["promoted_memory_ids"]),
        }

    promoted_records = source_artifact.get("promoted_records", [])
    promoted_memory_ids = [str(record.get("memory_id")) for record in promoted_records]

    return {
        "state": "present",
        "source_type": "promotion",
        "promotion_score": source_artifact["promotion_score"],
        "record_count": source_artifact["record_count"],
        "coherence_flags": list(source_artifact.get("coherence_flags", [])),
        "promoted_memory_ids": promoted_memory_ids,
    }


def _advisory_summary_from_source(
    source_artifact: Dict[str, Any],
    advisory_posture: str,
    target_child_core: str,
) -> Dict[str, Any]:
    artifact_type = str(source_artifact["artifact_type"])

    if artifact_type == "external_memory_pattern_aggregation":
        return {
            "state": "present",
            "source_type": "pattern_aggregation",
            "advisory_posture": advisory_posture,
            "target_child_core": target_child_core,
            "pattern_strength": source_artifact["pattern_strength"],
            "historical_confirmation": source_artifact["historical_confirmation"],
            "summary": source_artifact["pattern_summary"],
        }

    existing = source_artifact.get("advisory_summary")
    if isinstance(existing, dict):
        advisory = dict(existing)
        advisory["state"] = "present"
        advisory["advisory_posture"] = advisory_posture
        advisory["target_child_core"] = target_child_core
        return advisory

    return {
        "state": "present",
        "source_type": "promotion",
        "advisory_posture": advisory_posture,
        "target_child_core": target_child_core,
        "decision": source_artifact["decision"],
        "promotion_score": source_artifact["promotion_score"],
        "record_count": source_artifact["record_count"],
    }


def build_return_packet(
    source_artifact: Dict[str, Any],
    source_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(source_artifact, dict):
        return {
            "status": "failed",
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type="unknown",
                target_child_core="unknown",
                requester_profile="unknown",
                failure_reason="invalid_return_source_artifact_type",
            ),
        }

    artifact_type = str(source_artifact.get("artifact_type", "unknown"))
    requester_profile = str(source_artifact.get("requester_profile", "unknown"))
    target_child_core = _target_child_core_from_source(source_artifact)

    if not isinstance(source_receipt, dict):
        return {
            "status": "failed",
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_child_core=target_child_core,
                requester_profile=requester_profile,
                failure_reason="invalid_return_source_receipt_type",
            ),
        }

    if artifact_type not in REGISTRY["accepted_source_artifact_types"]:
        return {
            "status": "failed",
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_child_core=target_child_core,
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
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_child_core=target_child_core,
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
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_child_core=target_child_core,
                requester_profile=requester_profile,
                failure_reason="missing_required_fields",
            ),
        }

    expected_receipt_type = REGISTRY["accepted_source_receipt_types"][artifact_type]
    receipt_type = str(source_receipt.get("receipt_type") or source_receipt.get("artifact_type") or "")
    if receipt_type != expected_receipt_type:
        return {
            "status": "failed",
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_child_core=target_child_core,
                requester_profile=requester_profile,
                failure_reason="invalid_return_source_receipt_type",
            ),
        }

    receipt_requester_profile = str(source_receipt.get("requester_profile", ""))
    receipt_target_child_core = str(
        source_receipt.get("target_child_core")
        or source_receipt.get("target_core")
        or ""
    )

    if receipt_requester_profile != requester_profile or receipt_target_child_core != target_child_core:
        return {
            "status": "failed",
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_child_core=target_child_core,
                requester_profile=requester_profile,
                failure_reason="artifact_receipt_misalignment",
            ),
        }

    if target_child_core not in REGISTRY["allowed_target_child_cores"]:
        return {
            "status": "failed",
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_child_core=target_child_core,
                requester_profile=requester_profile,
                failure_reason="target_not_allowed",
            ),
        }

    if requester_profile not in REGISTRY["allowed_requester_profiles"]:
        return {
            "status": "failed",
            "artifact": None,
            "receipt": _build_rejection_receipt(
                source_artifact_type=artifact_type,
                target_child_core=target_child_core,
                requester_profile=requester_profile,
                failure_reason="requester_profile_not_allowed",
            ),
        }

    if artifact_type == "external_memory_promotion_artifact":
        missing_specific = _missing_required_fields(
            source_artifact,
            REGISTRY["required_promotion_fields"],
        )
        if missing_specific:
            return {
                "status": "failed",
                "artifact": None,
                "receipt": _build_rejection_receipt(
                    source_artifact_type=artifact_type,
                    target_child_core=target_child_core,
                    requester_profile=requester_profile,
                    failure_reason="missing_required_fields",
                ),
            }
        if source_artifact.get("decision") != "promoted":
            return {
                "status": "failed",
                "artifact": None,
                "receipt": _build_rejection_receipt(
                    source_artifact_type=artifact_type,
                    target_child_core=target_child_core,
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
                "artifact": None,
                "receipt": _build_rejection_receipt(
                    source_artifact_type=artifact_type,
                    target_child_core=target_child_core,
                    requester_profile=requester_profile,
                    failure_reason="missing_required_fields",
                ),
            }
        if source_artifact.get("aggregation_status") != "aggregated":
            return {
                "status": "failed",
                "artifact": None,
                "receipt": _build_rejection_receipt(
                    source_artifact_type=artifact_type,
                    target_child_core=target_child_core,
                    requester_profile=requester_profile,
                    failure_reason="source_status_not_accepted",
                ),
            }

    advisory_posture = _advisory_posture_from_source(source_artifact)
    memory_context_panel = _memory_context_panel_from_source(source_artifact)
    advisory_summary = _advisory_summary_from_source(
        source_artifact=source_artifact,
        advisory_posture=advisory_posture,
        target_child_core=target_child_core,
    )

    artifact = {
        "artifact_type": REGISTRY["emitted_artifact_type"],
        "target_child_core": target_child_core,
        "requester_profile": requester_profile,
        "advisory_posture": advisory_posture,
        "advisory_summary": advisory_summary,
        "memory_context_panel": memory_context_panel,
        "provenance_refs": list(source_artifact.get("provenance_refs", [])),
        "source_artifact_type": artifact_type,
    }

    receipt = _build_success_receipt(
        target_child_core=target_child_core,
        requester_profile=requester_profile,
        advisory_posture=advisory_posture,
    )

    return {
        "status": "ok",
        "artifact": artifact,
        "receipt": receipt,
    }