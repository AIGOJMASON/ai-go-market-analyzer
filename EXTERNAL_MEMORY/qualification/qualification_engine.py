from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List, Optional, Tuple

from .qualification_receipt_builder import build_qualification_receipt
from .qualification_registry import QUALIFICATION_REGISTRY


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stable_id(prefix: str, parts: List[str]) -> str:
    joined = "|".join(parts)
    digest = sha256(joined.encode("utf-8")).hexdigest()[:12]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}_{digest}"


@dataclass
class QualificationResult:
    record: Dict[str, Any]
    receipt: Dict[str, Any]


def _validate_required_fields(payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    required = QUALIFICATION_REGISTRY["required_fields"]
    for key in required:
        if key not in payload:
            return False, f"missing_required_field:{key}"
    return True, None


def _validate_artifact_type(payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    accepted = QUALIFICATION_REGISTRY["accepted_artifact_types"]
    if payload.get("artifact_type") not in accepted:
        return False, "invalid_input"
    return True, None


def _coerce_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    raise ValueError(f"non_numeric_weight:{value!r}")


def _payload_identity_parts(payload: Dict[str, Any]) -> List[str]:
    provenance = payload.get("provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}

    inner_payload = payload.get("payload", {})
    if not isinstance(inner_payload, dict):
        inner_payload = {}

    return [
        str(provenance.get("request_id", "")),
        str(provenance.get("source_ref", "")),
        str(inner_payload.get("symbol", "")),
        str(inner_payload.get("sector", "")),
        str(inner_payload.get("headline", "")),
        str(inner_payload.get("event_theme", "")),
        str(inner_payload.get("confirmation", "")),
    ]


def qualify_external_memory_candidate(payload: Dict[str, Any]) -> QualificationResult:
    valid_required, required_reason = _validate_required_fields(payload)
    if not valid_required:
        record = _build_rejection_record(
            payload=payload,
            rejection_reason="missing_required_fields",
            detail=required_reason,
        )
        return QualificationResult(record=record, receipt=build_qualification_receipt(record))

    valid_type, type_reason = _validate_artifact_type(payload)
    if not valid_type:
        record = _build_rejection_record(
            payload=payload,
            rejection_reason=type_reason or "invalid_input",
            detail="artifact_type_not_allowed",
        )
        return QualificationResult(record=record, receipt=build_qualification_receipt(record))

    constants = QUALIFICATION_REGISTRY["policy_constants"]
    blocked_trust_classes = set(QUALIFICATION_REGISTRY["blocked_trust_classes"])

    try:
        source_quality_weight = _coerce_number(payload["source_quality_weight"])
        signal_quality_weight = _coerce_number(payload["signal_quality_weight"])
        domain_relevance_weight = _coerce_number(payload["domain_relevance_weight"])
        persistence_value_weight = _coerce_number(payload["persistence_value_weight"])
        contamination_penalty = _coerce_number(payload["contamination_penalty"])
        redundancy_penalty = _coerce_number(payload["redundancy_penalty"])
    except ValueError as exc:
        record = _build_rejection_record(
            payload=payload,
            rejection_reason="invalid_input",
            detail=str(exc),
        )
        return QualificationResult(record=record, receipt=build_qualification_receipt(record))

    trust_class = str(payload["trust_class"]).strip().lower()
    if source_quality_weight < constants["source_quality_floor"]:
        record = _build_decision_record(
            payload=payload,
            source_quality_weight=source_quality_weight,
            signal_quality_weight=signal_quality_weight,
            domain_relevance_weight=domain_relevance_weight,
            persistence_value_weight=persistence_value_weight,
            contamination_penalty=contamination_penalty,
            redundancy_penalty=redundancy_penalty,
            trust_class=trust_class,
            adjusted_weight=_adjusted_weight(
                source_quality_weight,
                signal_quality_weight,
                domain_relevance_weight,
                persistence_value_weight,
                contamination_penalty,
                redundancy_penalty,
            ),
            decision="reject",
            rejection_reason="source_quality_below_floor",
        )
        return QualificationResult(record=record, receipt=build_qualification_receipt(record))

    if trust_class in blocked_trust_classes:
        record = _build_decision_record(
            payload=payload,
            source_quality_weight=source_quality_weight,
            signal_quality_weight=signal_quality_weight,
            domain_relevance_weight=domain_relevance_weight,
            persistence_value_weight=persistence_value_weight,
            contamination_penalty=contamination_penalty,
            redundancy_penalty=redundancy_penalty,
            trust_class=trust_class,
            adjusted_weight=_adjusted_weight(
                source_quality_weight,
                signal_quality_weight,
                domain_relevance_weight,
                persistence_value_weight,
                contamination_penalty,
                redundancy_penalty,
            ),
            decision="reject",
            rejection_reason="trust_class_blocked",
        )
        return QualificationResult(record=record, receipt=build_qualification_receipt(record))

    adjusted_weight = _adjusted_weight(
        source_quality_weight,
        signal_quality_weight,
        domain_relevance_weight,
        persistence_value_weight,
        contamination_penalty,
        redundancy_penalty,
    )

    if adjusted_weight >= constants["persist_threshold"]:
        decision = "persist_candidate"
        rejection_reason = None
    elif adjusted_weight >= constants["hold_threshold"]:
        decision = "hold"
        rejection_reason = None
    else:
        decision = "reject"
        rejection_reason = "persistence_weight_below_threshold"

    record = _build_decision_record(
        payload=payload,
        source_quality_weight=source_quality_weight,
        signal_quality_weight=signal_quality_weight,
        domain_relevance_weight=domain_relevance_weight,
        persistence_value_weight=persistence_value_weight,
        contamination_penalty=contamination_penalty,
        redundancy_penalty=redundancy_penalty,
        trust_class=trust_class,
        adjusted_weight=adjusted_weight,
        decision=decision,
        rejection_reason=rejection_reason,
    )
    return QualificationResult(record=record, receipt=build_qualification_receipt(record))


def _adjusted_weight(
    source_quality_weight: float,
    signal_quality_weight: float,
    domain_relevance_weight: float,
    persistence_value_weight: float,
    contamination_penalty: float,
    redundancy_penalty: float,
) -> float:
    base_weight = (
        source_quality_weight
        + signal_quality_weight
        + domain_relevance_weight
        + persistence_value_weight
    )
    return round(base_weight - contamination_penalty - redundancy_penalty, 2)


def _build_rejection_record(
    payload: Dict[str, Any],
    rejection_reason: str,
    detail: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": "external_memory_qualification_record",
        "qualification_record_id": _stable_id(
            "extmemqual",
            [
                str(payload.get("artifact_type", "unknown")),
                str(payload.get("source_type", "unknown")),
                rejection_reason,
                detail,
                *_payload_identity_parts(payload),
            ],
        ),
        "created_at": _utc_now(),
        "decision": "reject",
        "rejection_reason": rejection_reason,
        "detail": detail,
        "source_type": payload.get("source_type", "unknown"),
        "source_quality_weight": payload.get("source_quality_weight"),
        "signal_quality_weight": payload.get("signal_quality_weight"),
        "domain_relevance_weight": payload.get("domain_relevance_weight"),
        "persistence_value_weight": payload.get("persistence_value_weight"),
        "contamination_penalty": payload.get("contamination_penalty"),
        "redundancy_penalty": payload.get("redundancy_penalty"),
        "adjusted_weight": None,
        "trust_class": payload.get("trust_class"),
        "target_child_cores": payload.get("target_child_cores", []),
        "provenance": payload.get("provenance"),
        "payload": payload.get("payload"),
    }


def _build_decision_record(
    payload: Dict[str, Any],
    source_quality_weight: float,
    signal_quality_weight: float,
    domain_relevance_weight: float,
    persistence_value_weight: float,
    contamination_penalty: float,
    redundancy_penalty: float,
    trust_class: str,
    adjusted_weight: float,
    decision: str,
    rejection_reason: Optional[str],
) -> Dict[str, Any]:
    return {
        "artifact_type": "external_memory_qualification_record",
        "qualification_record_id": _stable_id(
            "extmemqual",
            [
                str(payload["artifact_type"]),
                str(payload["source_type"]),
                trust_class,
                decision,
                str(adjusted_weight),
                *_payload_identity_parts(payload),
            ],
        ),
        "created_at": _utc_now(),
        "decision": decision,
        "rejection_reason": rejection_reason,
        "source_type": payload["source_type"],
        "source_quality_weight": source_quality_weight,
        "signal_quality_weight": signal_quality_weight,
        "domain_relevance_weight": domain_relevance_weight,
        "persistence_value_weight": persistence_value_weight,
        "contamination_penalty": contamination_penalty,
        "redundancy_penalty": redundancy_penalty,
        "adjusted_weight": adjusted_weight,
        "trust_class": trust_class,
        "target_child_cores": payload["target_child_cores"],
        "provenance": payload["provenance"],
        "payload": payload["payload"],
    }