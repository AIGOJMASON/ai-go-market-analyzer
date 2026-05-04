from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


ENGINE_OUTPUT_REGISTRY_VERSION = "v5C.3"


APPROVED_ENGINE_IDS = {
    "curated_child_core_handoff_engine": {
        "engine_class": "curation",
        "approved_interpretation_types": {
            "market_event_context",
            "contractor_external_pressure",
            "governance_context",
            "unknown_context",
        },
        "approved_artifact_types": {
            "engine_interpretation_packet",
            "curated_child_core_handoff_packet",
            "engine_curated_packet",
        },
    }
}


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


FORBIDDEN_OUTPUT_KEYS = {
    "execute",
    "execution_command",
    "dispatch_command",
    "mutate_state",
    "state_patch",
    "pm_override",
    "canon_override",
    "watcher_override",
    "hidden_weight",
    "unbounded_reasoning",
}


REQUIRED_INTERPRETATION_KEYS = {
    "type",
    "classification",
    "direction",
    "confidence",
    "confidence_band",
    "weight",
    "weight_band",
    "summary",
    "evidence_signals",
    "constraints",
}


REQUIRED_AUTHORITY_KEYS_FALSE = {
    "can_execute",
    "can_mutate_state",
    "can_write_external_memory",
    "can_override_pm",
    "can_override_canon",
    "can_bypass_watcher",
    "can_reweight_downstream",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _reason(code: str, message: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "details": details or {},
    }


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


def _contains_forbidden_key(value: Any) -> List[str]:
    found: List[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            clean_key = _safe_str(key)
            if clean_key in FORBIDDEN_OUTPUT_KEYS:
                found.append(clean_key)
            found.extend(_contains_forbidden_key(child))

    elif isinstance(value, list):
        for child in value:
            found.extend(_contains_forbidden_key(child))

    return sorted(set(found))


def validate_engine_output_registry(packet: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(packet)
    interpretation = _safe_dict(source.get("interpretation"))
    authority = _safe_dict(source.get("authority"))

    checks: List[Dict[str, Any]] = []
    reasons: List[Dict[str, Any]] = []

    artifact_type = _safe_str(source.get("artifact_type"))
    engine_id = _safe_str(source.get("engine_id"))
    engine_record = APPROVED_ENGINE_IDS.get(engine_id)

    engine_known = engine_record is not None
    checks.append(
        _check(
            check_id="engine_id_registered",
            passed=engine_known,
            message="Engine output must come from a registered engine id.",
            details={"engine_id": engine_id},
        )
    )
    if not engine_known:
        reasons.append(
            _reason(
                "unregistered_engine_id",
                "Engine output blocked because engine_id is not registered.",
                {"engine_id": engine_id},
            )
        )

    approved_artifact_types = (
        set(engine_record.get("approved_artifact_types", set()))
        if engine_record
        else set()
    )
    artifact_type_ok = artifact_type in approved_artifact_types
    checks.append(
        _check(
            check_id="artifact_type_registered_for_engine",
            passed=artifact_type_ok,
            message="Engine artifact type must be approved for this engine.",
            details={
                "engine_id": engine_id,
                "artifact_type": artifact_type,
                "approved_artifact_types": sorted(approved_artifact_types),
            },
        )
    )
    if not artifact_type_ok:
        reasons.append(
            _reason(
                "unapproved_engine_artifact_type",
                "Engine output blocked because artifact_type is not approved for this engine.",
                {
                    "engine_id": engine_id,
                    "artifact_type": artifact_type,
                    "approved_artifact_types": sorted(approved_artifact_types),
                },
            )
        )

    interpretation_type = _safe_str(interpretation.get("type"))
    approved_interpretation_types = (
        set(engine_record.get("approved_interpretation_types", set()))
        if engine_record
        else set()
    )
    interpretation_type_ok = (
        interpretation_type in APPROVED_INTERPRETATION_TYPES
        and interpretation_type in approved_interpretation_types
    )

    checks.append(
        _check(
            check_id="interpretation_type_registered",
            passed=interpretation_type_ok,
            message="Interpretation type must be approved globally and for this engine.",
            details={
                "interpretation_type": interpretation_type,
                "approved_interpretation_types": sorted(approved_interpretation_types),
            },
        )
    )
    if not interpretation_type_ok:
        reasons.append(
            _reason(
                "unapproved_interpretation_type",
                "Engine output blocked because interpretation.type is not approved.",
                {
                    "interpretation_type": interpretation_type,
                    "approved_interpretation_types": sorted(approved_interpretation_types),
                },
            )
        )

    missing_interpretation_keys = sorted(
        key for key in REQUIRED_INTERPRETATION_KEYS if key not in interpretation
    )
    interpretation_shape_ok = not missing_interpretation_keys
    checks.append(
        _check(
            check_id="required_interpretation_keys_present",
            passed=interpretation_shape_ok,
            message="Engine interpretation must preserve the required output shape.",
            details={"missing": missing_interpretation_keys},
        )
    )
    if missing_interpretation_keys:
        reasons.append(
            _reason(
                "missing_required_interpretation_keys",
                "Engine output blocked because required interpretation keys are missing.",
                {"missing": missing_interpretation_keys},
            )
        )

    direction = _safe_str(interpretation.get("direction"))
    direction_ok = direction in APPROVED_DIRECTIONS
    checks.append(
        _check(
            check_id="direction_approved",
            passed=direction_ok,
            message="Interpretation direction must be approved.",
            details={"direction": direction},
        )
    )
    if not direction_ok:
        reasons.append(
            _reason(
                "unapproved_direction",
                "Engine output blocked because interpretation.direction is not approved.",
                {"direction": direction},
            )
        )

    confidence_band = _safe_str(interpretation.get("confidence_band"))
    confidence_band_ok = confidence_band in APPROVED_CONFIDENCE_BANDS
    checks.append(
        _check(
            check_id="confidence_band_approved",
            passed=confidence_band_ok,
            message="Confidence band must be approved.",
            details={"confidence_band": confidence_band},
        )
    )
    if not confidence_band_ok:
        reasons.append(
            _reason(
                "unapproved_confidence_band",
                "Engine output blocked because confidence_band is not approved.",
                {"confidence_band": confidence_band},
            )
        )

    weight_band = _safe_str(interpretation.get("weight_band"))
    weight_band_ok = weight_band in APPROVED_WEIGHT_BANDS
    checks.append(
        _check(
            check_id="weight_band_approved",
            passed=weight_band_ok,
            message="Weight band must be approved.",
            details={"weight_band": weight_band},
        )
    )
    if not weight_band_ok:
        reasons.append(
            _reason(
                "unapproved_weight_band",
                "Engine output blocked because weight_band is not approved.",
                {"weight_band": weight_band},
            )
        )

    authority_failures = sorted(
        key for key in REQUIRED_AUTHORITY_KEYS_FALSE if authority.get(key) is not False
    )
    authority_ok = not authority_failures
    checks.append(
        _check(
            check_id="authority_shape_non_executing",
            passed=authority_ok,
            message="Engine output authority keys must remain explicitly false.",
            details={"failures": authority_failures},
        )
    )
    if authority_failures:
        reasons.append(
            _reason(
                "engine_authority_shape_invalid",
                "Engine output blocked because one or more authority keys are not false.",
                {"failures": authority_failures},
            )
        )

    forbidden_keys = _contains_forbidden_key(source)
    forbidden_keys_ok = not forbidden_keys
    checks.append(
        _check(
            check_id="no_forbidden_output_keys",
            passed=forbidden_keys_ok,
            message="Engine output must not contain forbidden execution/mutation/override keys.",
            details={"forbidden_keys": forbidden_keys},
        )
    )
    if forbidden_keys:
        reasons.append(
            _reason(
                "forbidden_engine_output_keys",
                "Engine output blocked because forbidden output keys are present.",
                {"forbidden_keys": forbidden_keys},
            )
        )

    bounded = source.get("bounded") is True
    sealed = source.get("sealed") is True

    checks.append(
        _check(
            check_id="engine_output_bounded",
            passed=bounded,
            message="Engine output must be bounded.",
        )
    )
    if not bounded:
        reasons.append(
            _reason(
                "engine_output_not_bounded",
                "Engine output is not bounded.",
            )
        )

    checks.append(
        _check(
            check_id="engine_output_sealed",
            passed=sealed,
            message="Engine output must be sealed.",
        )
    )
    if not sealed:
        reasons.append(
            _reason(
                "engine_output_not_sealed",
                "Engine output is not sealed.",
            )
        )

    allowed = len(reasons) == 0

    return {
        "artifact_type": "engine_output_registry_decision",
        "artifact_version": ENGINE_OUTPUT_REGISTRY_VERSION,
        "checked_at": _utc_now_iso(),
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "engine_id": engine_id,
        "artifact_checked": artifact_type,
        "checks": checks,
        "reasons": reasons,
        "policy": {
            "registered_engine_required": True,
            "approved_interpretation_type_required": True,
            "approved_artifact_type_required": True,
            "approved_direction_required": True,
            "approved_confidence_band_required": True,
            "approved_weight_band_required": True,
            "execution_or_mutation_keys_allowed": False,
            "unregistered_output_shapes_allowed": False,
        },
    }


def assert_engine_output_registered(packet: Dict[str, Any]) -> Dict[str, Any]:
    decision = validate_engine_output_registry(packet)

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "engine_output_registry_blocked",
                "decision": decision,
            }
        )

    return decision