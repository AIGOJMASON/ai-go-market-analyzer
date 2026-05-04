from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


ENGINE_SIGNAL_CONTRACT_VERSION = "v5C.1"

APPROVED_INTERPRETATION_TYPES = {
    "market_event_context",
    "contractor_external_pressure",
    "governance_context",
    "unknown_context",
}

APPROVED_DIRECTIONS = {
    "positive",
    "negative",
    "neutral",
    "mixed",
    "unknown",
}

APPROVED_CONFIDENCE_BANDS = {
    "low",
    "medium",
    "high",
}

APPROVED_WEIGHT_BANDS = {
    "zero",
    "low",
    "medium",
    "high",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_0_1(value: Any) -> float:
    number = _safe_float(value, 0.0)
    if number < 0.0:
        return 0.0
    if number > 1.0:
        return 1.0
    return number


def confidence_band(value: float) -> str:
    clean = _clamp_0_1(value)
    if clean < 0.34:
        return "low"
    if clean < 0.67:
        return "medium"
    return "high"


def weight_band(value: float) -> str:
    clean = _clamp_0_1(value)
    if clean <= 0.0:
        return "zero"
    if clean < 0.34:
        return "low"
    if clean < 0.67:
        return "medium"
    return "high"


def build_engine_interpretation_packet(
    *,
    engine_id: str,
    source_research_packet: Dict[str, Any],
    interpretation_type: str,
    direction: str = "unknown",
    confidence: float = 0.0,
    weight: float = 0.0,
    classification: str = "unknown",
    summary: str = "",
    evidence_signals: List[str] | None = None,
    constraints: List[str] | None = None,
) -> Dict[str, Any]:
    research_packet = _safe_dict(source_research_packet)
    research_input = _safe_dict(research_packet.get("research_input"))
    trust = _safe_dict(research_packet.get("trust"))
    screening = _safe_dict(research_packet.get("screening"))

    clean_confidence = _clamp_0_1(confidence)
    clean_weight = _clamp_0_1(weight)

    research_packet_id = (
        _safe_str(research_packet.get("research_packet_id"))
        or _safe_str(research_packet.get("packet_id"))
        or _safe_str(research_packet.get("id"))
    )

    return {
        "artifact_type": "engine_interpretation_packet",
        "artifact_version": ENGINE_SIGNAL_CONTRACT_VERSION,
        "created_at": _utc_now_iso(),
        "engine_id": _safe_str(engine_id),
        "source_authority": "engines",
        "source_research_packet_id": research_packet_id,
        "origin_authority": "RESEARCH_CORE",
        "interpretation": {
            "type": _safe_str(interpretation_type) or "unknown_context",
            "classification": _safe_str(classification) or "unknown",
            "direction": _safe_str(direction) or "unknown",
            "confidence": clean_confidence,
            "confidence_band": confidence_band(clean_confidence),
            "weight": clean_weight,
            "weight_band": weight_band(clean_weight),
            "summary": _safe_str(summary),
            "evidence_signals": list(evidence_signals or []),
            "constraints": list(constraints or []),
        },
        "lineage": {
            "research_packet_id": research_packet_id,
            "provider": _safe_str(research_input.get("provider")),
            "provider_kind": _safe_str(research_input.get("provider_kind")),
            "signal_type": _safe_str(research_input.get("signal_type")),
            "trust_class": _safe_str(trust.get("trust_class")),
            "screening_valid": bool(screening.get("valid") is True),
        },
        "authority": {
            "can_execute": False,
            "can_mutate_state": False,
            "can_write_external_memory": False,
            "can_override_pm": False,
            "can_override_canon": False,
            "can_bypass_watcher": False,
            "can_reweight_downstream": False,
        },
        "bounded": True,
        "sealed": True,
    }


def validate_engine_interpretation_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(packet)
    interpretation = _safe_dict(source.get("interpretation"))
    lineage = _safe_dict(source.get("lineage"))
    authority = _safe_dict(source.get("authority"))

    errors: List[str] = []
    warnings: List[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(source.get("artifact_type") == "engine_interpretation_packet", "invalid_artifact_type")
    require(bool(_safe_str(source.get("engine_id"))), "missing_engine_id")
    require(source.get("origin_authority") == "RESEARCH_CORE", "missing_research_core_origin")
    require(bool(_safe_str(source.get("source_research_packet_id"))), "missing_source_research_packet_id")

    interpretation_type = _safe_str(interpretation.get("type"))
    direction = _safe_str(interpretation.get("direction"))
    confidence = interpretation.get("confidence")
    weight = interpretation.get("weight")

    require(interpretation_type in APPROVED_INTERPRETATION_TYPES, "invalid_interpretation_type")
    require(direction in APPROVED_DIRECTIONS, "invalid_direction")
    require(isinstance(confidence, (int, float)), "confidence_not_numeric")
    require(isinstance(weight, (int, float)), "weight_not_numeric")
    require(0.0 <= _safe_float(confidence, -1.0) <= 1.0, "confidence_out_of_range")
    require(0.0 <= _safe_float(weight, -1.0) <= 1.0, "weight_out_of_range")
    require(bool(_safe_str(interpretation.get("classification"))), "missing_classification")
    require(bool(_safe_str(interpretation.get("summary"))), "missing_summary")
    require(isinstance(interpretation.get("evidence_signals"), list), "evidence_signals_not_list")

    require(bool(_safe_str(lineage.get("research_packet_id"))), "missing_lineage_research_packet_id")
    require(lineage.get("screening_valid") is True, "source_screening_not_valid")

    forbidden_authority = [
        "can_execute",
        "can_mutate_state",
        "can_write_external_memory",
        "can_override_pm",
        "can_override_canon",
        "can_bypass_watcher",
        "can_reweight_downstream",
    ]

    for field in forbidden_authority:
        require(authority.get(field) is False, f"forbidden_authority_claim:{field}")

    require(source.get("bounded") is True, "packet_not_bounded")
    require(source.get("sealed") is True, "packet_not_sealed")

    allowed = len(errors) == 0

    return {
        "status": "passed" if allowed else "blocked",
        "valid": allowed,
        "allowed": allowed,
        "artifact_type": "engine_signal_integrity_decision",
        "artifact_version": ENGINE_SIGNAL_CONTRACT_VERSION,
        "checked_at": _utc_now_iso(),
        "errors": errors,
        "warnings": warnings,
        "policy": {
            "engine_interpretation_required": True,
            "downstream_reweighting_allowed": False,
            "child_core_reinterpretation_allowed": False,
            "execution_allowed": False,
            "mutation_allowed": False,
        },
    }


def assert_engine_interpretation_valid(packet: Dict[str, Any]) -> Dict[str, Any]:
    decision = validate_engine_interpretation_packet(packet)

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "engine_signal_integrity_blocked",
                "decision": decision,
            }
        )

    return decision