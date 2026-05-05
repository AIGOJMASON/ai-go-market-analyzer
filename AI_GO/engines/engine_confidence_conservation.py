from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


ENGINE_CONFIDENCE_CONSERVATION_VERSION = "v5C.4"

APPROVED_UPLIFT_REASONS = {
    "multi_source_confirmation",
    "verified_provider_consensus",
    "operator_verified_corroboration",
}

MAX_UPLIFT_WITHOUT_APPROVAL = 0.10
MAX_TOTAL_CONFIDENCE = 1.0
MAX_TOTAL_WEIGHT = 1.0


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


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


def _reason(code: str, message: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {"code": code, "message": message, "details": details or {}}


def _check(
    *,
    check_id: str,
    passed: bool,
    message: str,
    details: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "check_id": check_id,
        "passed": passed,
        "message": message,
        "details": details or {},
    }


def _approved_uplift_amount(uplift_record: Dict[str, Any]) -> float:
    record = _safe_dict(uplift_record)
    reason = str(record.get("reason", "")).strip()
    approved = record.get("approved") is True
    amount = _clamp_0_1(record.get("amount", 0.0))

    if not approved:
        return 0.0

    if reason not in APPROVED_UPLIFT_REASONS:
        return 0.0

    return min(amount, MAX_UPLIFT_WITHOUT_APPROVAL)


def evaluate_engine_confidence_conservation(
    *,
    research_packet: Dict[str, Any],
    engine_interpretation_packet: Dict[str, Any],
    uplift_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    research = _safe_dict(research_packet)
    trust = _safe_dict(research.get("trust"))
    interpretation_packet = _safe_dict(engine_interpretation_packet)
    interpretation = _safe_dict(interpretation_packet.get("interpretation"))

    checks: List[Dict[str, Any]] = []
    reasons: List[Dict[str, Any]] = []

    research_pre_weight = _clamp_0_1(trust.get("pre_weight", 0.0))
    confidence = _clamp_0_1(interpretation.get("confidence", 0.0))
    weight = _clamp_0_1(interpretation.get("weight", 0.0))

    uplift = _approved_uplift_amount(_safe_dict(uplift_record))
    lawful_ceiling = min(research_pre_weight + uplift, 1.0)

    confidence_conserved = confidence <= lawful_ceiling
    checks.append(
        _check(
            check_id="confidence_not_above_lawful_ceiling",
            passed=confidence_conserved,
            message="Engine confidence may not exceed RESEARCH_CORE pre_weight plus lawful uplift.",
            details={
                "research_pre_weight": research_pre_weight,
                "confidence": confidence,
                "uplift": uplift,
                "lawful_ceiling": lawful_ceiling,
            },
        )
    )
    if not confidence_conserved:
        reasons.append(
            _reason(
                "unearned_confidence_detected",
                "Engine confidence exceeds conserved trust ceiling.",
                {
                    "research_pre_weight": research_pre_weight,
                    "confidence": confidence,
                    "uplift": uplift,
                    "lawful_ceiling": lawful_ceiling,
                },
            )
        )

    weight_conserved = weight <= lawful_ceiling
    checks.append(
        _check(
            check_id="weight_not_above_lawful_ceiling",
            passed=weight_conserved,
            message="Engine weight may not exceed RESEARCH_CORE pre_weight plus lawful uplift.",
            details={
                "research_pre_weight": research_pre_weight,
                "weight": weight,
                "uplift": uplift,
                "lawful_ceiling": lawful_ceiling,
            },
        )
    )
    if not weight_conserved:
        reasons.append(
            _reason(
                "unearned_weight_detected",
                "Engine weight exceeds conserved trust ceiling.",
                {
                    "research_pre_weight": research_pre_weight,
                    "weight": weight,
                    "uplift": uplift,
                    "lawful_ceiling": lawful_ceiling,
                },
            )
        )

    confidence_range_ok = 0.0 <= confidence <= MAX_TOTAL_CONFIDENCE
    weight_range_ok = 0.0 <= weight <= MAX_TOTAL_WEIGHT

    checks.append(
        _check(
            check_id="confidence_range_valid",
            passed=confidence_range_ok,
            message="Engine confidence must remain between 0 and 1.",
            details={"confidence": confidence},
        )
    )
    if not confidence_range_ok:
        reasons.append(
            _reason(
                "confidence_out_of_range",
                "Engine confidence is outside allowed range.",
                {"confidence": confidence},
            )
        )

    checks.append(
        _check(
            check_id="weight_range_valid",
            passed=weight_range_ok,
            message="Engine weight must remain between 0 and 1.",
            details={"weight": weight},
        )
    )
    if not weight_range_ok:
        reasons.append(
            _reason(
                "weight_out_of_range",
                "Engine weight is outside allowed range.",
                {"weight": weight},
            )
        )

    allowed = len(reasons) == 0

    return {
        "artifact_type": "engine_confidence_conservation_decision",
        "artifact_version": ENGINE_CONFIDENCE_CONSERVATION_VERSION,
        "checked_at": _utc_now_iso(),
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "research_pre_weight": research_pre_weight,
        "engine_confidence": confidence,
        "engine_weight": weight,
        "approved_uplift": uplift,
        "lawful_ceiling": lawful_ceiling,
        "checks": checks,
        "reasons": reasons,
        "policy": {
            "confidence_must_be_conserved": True,
            "weight_must_be_conserved": True,
            "unearned_weight_allowed": False,
            "unearned_confidence_allowed": False,
            "approved_uplift_reasons": sorted(APPROVED_UPLIFT_REASONS),
            "max_uplift_without_approval": MAX_UPLIFT_WITHOUT_APPROVAL,
        },
    }


def assert_engine_confidence_conserved(
    *,
    research_packet: Dict[str, Any],
    engine_interpretation_packet: Dict[str, Any],
    uplift_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    decision = evaluate_engine_confidence_conservation(
        research_packet=research_packet,
        engine_interpretation_packet=engine_interpretation_packet,
        uplift_record=uplift_record,
    )

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "engine_confidence_conservation_blocked",
                "decision": decision,
            }
        )

    return decision