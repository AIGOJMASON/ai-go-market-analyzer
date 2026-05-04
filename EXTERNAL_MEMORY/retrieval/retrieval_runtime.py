# AI_GO/EXTERNAL_MEMORY/retrieval/retrieval_runtime.py

from __future__ import annotations

from typing import Any, Dict, List, Tuple

try:
    from AI_GO.EXTERNAL_MEMORY.authority.memory_authority_guard import (
        apply_memory_authority_guard,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.authority.memory_authority_guard import (
        apply_memory_authority_guard,
    )

from .retrieval_query import query_external_memory_records
from .retrieval_receipt_builder import (
    build_retrieval_failure_receipt,
    build_retrieval_receipt,
)
from .retrieval_registry import RETRIEVAL_REGISTRY


RETRIEVAL_RUNTIME_VERSION = "v5F.2"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_int(value: Any, default: int = 10) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def _build_bounded_record(record: Dict[str, Any]) -> Dict[str, Any]:
    payload = _safe_dict(record.get("payload"))
    provenance = _safe_dict(record.get("provenance"))

    return {
        "memory_id": record.get("memory_id"),
        "qualification_record_id": record.get("qualification_record_id"),
        "source_type": record.get("source_type"),
        "trust_class": record.get("trust_class"),
        "source_quality_weight": record.get("source_quality_weight"),
        "signal_quality_weight": record.get("signal_quality_weight"),
        "domain_relevance_weight": record.get("domain_relevance_weight"),
        "persistence_value_weight": record.get("persistence_value_weight"),
        "contamination_penalty": record.get("contamination_penalty"),
        "redundancy_penalty": record.get("redundancy_penalty"),
        "adjusted_weight": record.get("adjusted_weight"),
        "target_child_cores": record.get("target_child_cores", []),
        "provenance": provenance,
        "payload_summary": {
            "request_id": payload.get("request_id"),
            "headline": payload.get("headline") or payload.get("title"),
            "summary": payload.get("summary"),
            "symbol": payload.get("symbol"),
            "sector": payload.get("sector"),
            "event_theme": payload.get("event_theme"),
            "confirmation": payload.get("confirmation"),
            "macro_bias": payload.get("macro_bias"),
        },
        "created_at": record.get("created_at"),
    }


def _request_summary(request: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "requester_profile": request.get("requester_profile"),
        "target_child_core": request.get("target_child_core"),
        "limit": request.get("limit"),
        "source_type": request.get("source_type"),
        "trust_class": request.get("trust_class"),
        "min_adjusted_weight": request.get("min_adjusted_weight"),
        "symbol": request.get("symbol"),
        "sector": request.get("sector"),
    }


def _build_retrieval_artifact(
    *,
    request: Dict[str, Any],
    raw_records: List[Dict[str, Any]],
    bounded_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    artifact = {
        "artifact_type": "external_memory_retrieval_artifact",
        "artifact_version": RETRIEVAL_RUNTIME_VERSION,
        "status": "ok",
        "retrieval_mode": "read_only",
        "request_summary": _request_summary(request),
        "requester_profile": request.get("requester_profile"),
        "target_child_core": request.get("target_child_core"),
        "matched_count": len(raw_records),
        "returned_count": len(bounded_records),
        "records": bounded_records,
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "read_only_to_authority_chain": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_state": False,
            "can_mutate_operational_state": False,
            "can_mutate_child_core_state": False,
        },
        "limitations": [
            "retrieval_only",
            "no_promotion",
            "no_runtime_mutation",
            "no_recommendation_mutation",
            "no_authority_override",
        ],
        "sealed": True,
    }
    return apply_memory_authority_guard(artifact)


def _failure_result(
    *,
    request: Dict[str, Any],
    failure_reason: str,
    detail: str,
) -> Dict[str, Any]:
    receipt = build_retrieval_failure_receipt(
        request=request,
        failure_reason=failure_reason,
        detail=detail,
    )
    guarded_receipt = apply_memory_authority_guard(receipt)

    return {
        "status": "failed",
        "retrieval_artifact": None,
        "retrieval_receipt": guarded_receipt,
        "artifact": None,
        "receipt": guarded_receipt,
        "failure_reason": failure_reason,
        "detail": detail,
        "authority": guarded_receipt.get("authority", {}),
    }


def run_external_memory_retrieval(request: Dict[str, Any]) -> Dict[str, Any]:
    source_request = _safe_dict(request)

    valid, failure_reason, detail = _validate_request(source_request)
    if not valid:
        return _failure_result(
            request=source_request,
            failure_reason=failure_reason,
            detail=detail,
        )

    limit = _safe_int(source_request.get("limit"), 10)

    raw_records = query_external_memory_records(
        target_core_id=str(source_request.get("target_child_core", "")),
        symbol=source_request.get("symbol"),
        sector=source_request.get("sector"),
        trust_class=source_request.get("trust_class"),
        source_type=source_request.get("source_type"),
        limit=limit,
        min_adjusted_weight=_safe_float_or_none(source_request.get("min_adjusted_weight")),
    )

    bounded_records = [_build_bounded_record(record) for record in raw_records[:limit]]

    artifact = _build_retrieval_artifact(
        request=source_request,
        raw_records=raw_records,
        bounded_records=bounded_records,
    )

    receipt = build_retrieval_receipt(
        request=source_request,
        matched_count=len(raw_records),
        returned_count=len(bounded_records),
    )
    guarded_receipt = apply_memory_authority_guard(receipt)

    return {
        "status": "ok",
        "retrieval_artifact": artifact,
        "retrieval_receipt": guarded_receipt,
        "artifact": artifact,
        "receipt": guarded_receipt,
        "authority": artifact.get("authority", {}),
    }