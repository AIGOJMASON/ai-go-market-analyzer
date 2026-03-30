
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .retrieval_query import query_external_memory_records
from .retrieval_receipt_builder import (
    build_retrieval_failure_receipt,
    build_retrieval_receipt,
)
from .retrieval_registry import RETRIEVAL_REGISTRY


def _validate_request(request: Dict[str, Any]) -> Tuple[bool, str, str]:
    request_type = request.get("artifact_type", "external_memory_retrieval_request")
    if request_type != RETRIEVAL_REGISTRY["accepted_request_type"]:
        return False, "invalid_request_type", "artifact_type_not_allowed"

    for field in RETRIEVAL_REGISTRY["required_fields"]:
        if field not in request:
            return False, "missing_required_fields", f"missing_required_field:{field}"

    requester_profile = str(request["requester_profile"])
    target_child_core = str(request["target_child_core"])

    profiles = RETRIEVAL_REGISTRY["allowed_requester_profiles"]
    if requester_profile not in profiles:
        return False, "invalid_requester_profile", "requester_profile_not_registered"

    if target_child_core not in RETRIEVAL_REGISTRY["allowed_target_child_cores"]:
        return False, "invalid_target_child_core", "target_child_core_not_registered"

    try:
        limit = int(request["limit"])
    except (TypeError, ValueError):
        return False, "invalid_limit", "limit_not_integer"

    if limit < 1:
        return False, "invalid_limit", "limit_below_minimum"

    profile_config = profiles[requester_profile]
    max_records = int(profile_config["max_records"])
    if limit > max_records:
        return False, "limit_exceeds_profile_max", f"max_records:{max_records}"

    allowed_targets = profile_config["allowed_targets"]
    if allowed_targets != "*" and target_child_core not in allowed_targets:
        return False, "target_not_allowed_for_profile", "profile_target_mismatch"

    return True, "", ""


def _build_artifact(
    request: Dict[str, Any],
    matched_count: int,
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    bounded_records = []
    for record in records:
        bounded_records.append(
            {
                "memory_id": record["memory_id"],
                "qualification_record_id": record["qualification_record_id"],
                "source_type": record["source_type"],
                "trust_class": record["trust_class"],
                "source_quality_weight": record["source_quality_weight"],
                "adjusted_weight": record["adjusted_weight"],
                "target_child_cores": record["target_child_cores"],
                "provenance": record["provenance"],
                "payload_summary": {
                    "request_id": record["payload"].get("request_id"),
                    "headline": record["payload"].get("headline"),
                    "symbol": record["payload"].get("symbol"),
                    "sector": record["payload"].get("sector"),
                    "confirmation": record["payload"].get("confirmation"),
                },
                "created_at": record["created_at"],
            }
        )

    return {
        "artifact_type": "external_memory_retrieval_artifact",
        "request_summary": {
            "requester_profile": request["requester_profile"],
            "target_child_core": request["target_child_core"],
            "limit": int(request["limit"]),
            "source_type": request.get("source_type"),
            "trust_class": request.get("trust_class"),
            "min_adjusted_weight": request.get("min_adjusted_weight"),
            "symbol": request.get("symbol"),
            "sector": request.get("sector"),
        },
        "matched_count": matched_count,
        "returned_count": len(bounded_records),
        "records": bounded_records,
    }


def run_external_memory_retrieval(
    request: Dict[str, Any],
) -> Dict[str, Any]:
    valid, failure_reason, detail = _validate_request(request)
    if not valid:
        failure_receipt = build_retrieval_failure_receipt(request, failure_reason, detail)
        return {
            "status": "failed",
            "artifact": None,
            "receipt": failure_receipt,
        }

    records = query_external_memory_records(
        target_core_id=str(request["target_child_core"]),
        symbol=request.get("symbol"),
        sector=request.get("sector"),
        trust_class=request.get("trust_class"),
        source_type=request.get("source_type"),
        limit=int(request["limit"]),
        min_adjusted_weight=request.get("min_adjusted_weight"),
    )
    matched_count = len(records)

    artifact = _build_artifact(request, matched_count, records)
    receipt = build_retrieval_receipt(
        request=request,
        matched_count=matched_count,
        returned_count=len(records),
    )
    return {
        "status": "ok",
        "artifact": artifact,
        "receipt": receipt,
    }