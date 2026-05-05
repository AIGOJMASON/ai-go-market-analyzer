from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.engines.engine_confidence_conservation import (
    evaluate_engine_confidence_conservation,
)
from AI_GO.engines.engine_drift_guard import evaluate_engine_drift
from AI_GO.engines.engine_output_registry import validate_engine_output_registry
from AI_GO.engines.engine_signal_contract import validate_engine_interpretation_packet


CROSS_CORE_ENFORCER_VERSION = "v5C.4"


ALLOWED_ROOT_SPINE_ORDER = [
    "RESEARCH_CORE",
    "engines",
    "child_core_consumption_adapter",
    "child_core",
]


RAW_EXTERNAL_FORBIDDEN_TARGETS = {
    "market_analyzer_v1",
    "contractor_builder_v1",
    "child_core",
    "child_cores",
}


FORBIDDEN_AUTHORITY_CLAIMS = {
    "execution_authority",
    "canon_authority",
    "governance_override",
    "watcher_override",
    "state_mutation_authority",
    "external_memory_write_authority",
    "raw_research_authority",
    "downstream_reweighting_authority",
    "child_core_reinterpretation_authority",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_bool(value: Any) -> bool:
    return value is True


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


def _lineage(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("lineage"))


def _authority(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("authority"))


def _source(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("source"))


def _engine_interpretation_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("engine_interpretation_packet"))


def _synthetic_research_packet_from_handoff(packet: Dict[str, Any]) -> Dict[str, Any]:
    source = _source(packet)
    return {
        "artifact_type": source.get("research_artifact_type", "synthetic_research_packet_view"),
        "research_packet_id": source.get("research_packet_id", ""),
        "screening": {
            "valid": source.get("screening_valid") is True
            or source.get("source_valid") is True,
        },
        "trust": {
            "trust_class": source.get("trust_class", ""),
            "pre_weight": source.get("pre_weight", 0.0),
        },
    }


def _engine_signal_integrity(packet: Dict[str, Any]) -> Dict[str, Any]:
    interpretation_packet = _engine_interpretation_packet(packet)

    if interpretation_packet:
        return validate_engine_interpretation_packet(interpretation_packet)

    return {
        "status": "blocked",
        "valid": False,
        "allowed": False,
        "errors": ["missing_engine_interpretation_packet"],
    }


def _engine_output_registry(packet: Dict[str, Any]) -> Dict[str, Any]:
    interpretation_packet = _engine_interpretation_packet(packet)

    if interpretation_packet:
        return validate_engine_output_registry(interpretation_packet)

    return {
        "status": "blocked",
        "valid": False,
        "allowed": False,
        "reasons": [
            {
                "code": "missing_engine_interpretation_packet",
                "message": "Cannot validate engine output registry without engine_interpretation_packet.",
            }
        ],
    }


def _engine_confidence_conservation(packet: Dict[str, Any]) -> Dict[str, Any]:
    interpretation_packet = _engine_interpretation_packet(packet)

    if not interpretation_packet:
        return {
            "status": "blocked",
            "valid": False,
            "allowed": False,
            "reasons": [
                {
                    "code": "missing_engine_interpretation_packet",
                    "message": "Cannot validate confidence conservation without engine_interpretation_packet.",
                }
            ],
        }

    return evaluate_engine_confidence_conservation(
        research_packet=_synthetic_research_packet_from_handoff(packet),
        engine_interpretation_packet=interpretation_packet,
    )


def _source_authority_is_lawful(source: Dict[str, Any]) -> bool:
    source_authority = _safe_str(source.get("source_authority"))
    root_spine_authority = _safe_str(source.get("root_spine_authority"))

    return (
        source_authority == "root_intelligence_spine"
        or (
            source_authority == "engines"
            and root_spine_authority == "root_intelligence_spine"
        )
    )


def evaluate_cross_core_handoff(
    packet: Dict[str, Any],
    *,
    original_handoff_packet: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    source_packet = _safe_dict(packet)
    lineage = _lineage(source_packet)
    authority = _authority(source_packet)

    checks: List[Dict[str, Any]] = []
    reasons: List[Dict[str, Any]] = []

    source_authority = _safe_str(source_packet.get("source_authority"))
    root_spine_authority = _safe_str(source_packet.get("root_spine_authority"))
    source_ok = _source_authority_is_lawful(source_packet)

    checks.append(
        _check(
            check_id="source_authority_root_spine_or_engine_with_root_spine",
            passed=source_ok,
            message=(
                "Cross-core handoff must originate from root_intelligence_spine "
                "or from engines with root_spine_authority=root_intelligence_spine."
            ),
            details={
                "source_authority": source_authority,
                "root_spine_authority": root_spine_authority,
            },
        )
    )

    if not source_ok:
        reasons.append(
            _reason(
                "invalid_source_authority",
                "Cross-core handoff blocked because source authority does not prove the governed root spine path.",
                {
                    "source_authority": source_authority,
                    "root_spine_authority": root_spine_authority,
                },
            )
        )

    authority_id_ok = authority.get("authority_id") == "engines"
    checks.append(
        _check(
            check_id="authority_id_engines",
            passed=authority_id_ok,
            message="Cross-core handoff must preserve authority.authority_id=engines.",
            details={"authority_id": authority.get("authority_id")},
        )
    )
    if not authority_id_ok:
        reasons.append(
            _reason(
                "missing_engines_authority_id",
                "Cross-core handoff blocked because authority.authority_id is not engines.",
                {"authority": authority},
            )
        )

    curates_before_child_core_ok = authority.get("curates_before_child_core") is True
    checks.append(
        _check(
            check_id="authority_curates_before_child_core",
            passed=curates_before_child_core_ok,
            message="Cross-core handoff requires authority.curates_before_child_core=true.",
            details={"curates_before_child_core": authority.get("curates_before_child_core")},
        )
    )
    if not curates_before_child_core_ok:
        reasons.append(
            _reason(
                "missing_curates_before_child_core",
                "Cross-core handoff blocked because authority.curates_before_child_core is not true.",
                {"authority": authority},
            )
        )

    spine_order = _safe_list(source_packet.get("spine_order"))
    spine_ok = spine_order == ALLOWED_ROOT_SPINE_ORDER

    checks.append(
        _check(
            check_id="spine_order_valid",
            passed=spine_ok,
            message="Cross-core handoff must preserve RESEARCH_CORE to engines to adapter to child_core order.",
            details={"spine_order": spine_order},
        )
    )

    if not spine_ok:
        reasons.append(
            _reason(
                "invalid_spine_order",
                "Cross-core handoff blocked because spine order is invalid.",
                {"expected": ALLOWED_ROOT_SPINE_ORDER, "actual": spine_order},
            )
        )

    research_packet_id = _safe_str(lineage.get("research_packet_id"))
    interpretation_packet_id = _safe_str(lineage.get("interpretation_packet_id"))
    adapter_id = _safe_str(lineage.get("adapter_id"))

    lineage_required = {
        "research_packet_id": bool(research_packet_id),
        "interpretation_packet_id": bool(interpretation_packet_id),
        "adapter_id": bool(adapter_id),
    }

    for key, passed in lineage_required.items():
        checks.append(
            _check(
                check_id=f"lineage_{key}_present",
                passed=passed,
                message=f"Cross-core handoff requires lineage.{key}.",
            )
        )
        if not passed:
            reasons.append(
                _reason(
                    f"missing_lineage_{key}",
                    f"Cross-core handoff blocked because lineage.{key} is missing.",
                )
            )

    interpretation_packet = _engine_interpretation_packet(source_packet)
    has_interpretation = bool(interpretation_packet)

    checks.append(
        _check(
            check_id="engine_interpretation_present",
            passed=has_interpretation,
            message="Cross-core handoff requires engine_interpretation_packet.",
        )
    )

    if not has_interpretation:
        reasons.append(
            _reason(
                "engine_interpretation_missing",
                "Cross-core handoff blocked because engine meaning was not assigned.",
            )
        )

    integrity = _engine_signal_integrity(source_packet)
    integrity_ok = integrity.get("allowed") is True

    checks.append(
        _check(
            check_id="engine_signal_integrity_passed",
            passed=integrity_ok,
            message="Cross-core handoff requires valid engine signal integrity.",
            details=integrity,
        )
    )

    if not integrity_ok:
        reasons.append(
            _reason(
                "engine_signal_integrity_failed",
                "Cross-core handoff blocked because engine signal integrity failed.",
                {"engine_signal_integrity": integrity},
            )
        )

    registry = _engine_output_registry(source_packet)
    registry_ok = registry.get("allowed") is True

    checks.append(
        _check(
            check_id="engine_output_registry_passed",
            passed=registry_ok,
            message="Engine output must match approved registry.",
            details=registry,
        )
    )

    if not registry_ok:
        reasons.append(
            _reason(
                "engine_output_registry_failed",
                "Cross-core handoff blocked because engine output registry validation failed.",
                {"engine_output_registry": registry},
            )
        )

    conservation = _engine_confidence_conservation(source_packet)
    conservation_ok = conservation.get("allowed") is True

    checks.append(
        _check(
            check_id="engine_confidence_conservation_passed",
            passed=conservation_ok,
            message="Engine confidence and weight must not exceed conserved RESEARCH_CORE trust.",
            details=conservation,
        )
    )

    if not conservation_ok:
        reasons.append(
            _reason(
                "engine_confidence_conservation_failed",
                "Cross-core handoff blocked because engine confidence or weight violated conservation.",
                {"engine_confidence_conservation": conservation},
            )
        )

    if original_handoff_packet is not None:
        drift = evaluate_engine_drift(
            original_handoff_packet=original_handoff_packet,
            candidate_handoff_packet=source_packet,
        )
        drift_ok = drift.get("allowed") is True

        checks.append(
            _check(
                check_id="engine_drift_guard_passed",
                passed=drift_ok,
                message="Candidate handoff may not reinterpret or reweight engine meaning.",
                details=drift,
            )
        )

        if not drift_ok:
            reasons.append(
                _reason(
                    "engine_drift_detected",
                    "Cross-core handoff blocked because engine interpretation changed downstream.",
                    {"engine_drift_guard": drift},
                )
            )

    target_child_core = _safe_str(source_packet.get("target_child_core"))
    has_target = bool(target_child_core)

    checks.append(
        _check(
            check_id="target_child_core_present",
            passed=has_target,
            message="Cross-core handoff requires target_child_core.",
            details={"target_child_core": target_child_core},
        )
    )

    if not has_target:
        reasons.append(
            _reason(
                "missing_target_child_core",
                "Cross-core handoff blocked because target_child_core is missing.",
            )
        )

    raw_input = _safe_bool(source_packet.get("raw_input")) or _safe_bool(
        source_packet.get("raw_external_input")
    )
    external_source = _safe_bool(source_packet.get("external_source"))

    raw_target_blocked = (
        raw_input
        and external_source
        and target_child_core in RAW_EXTERNAL_FORBIDDEN_TARGETS
    )

    checks.append(
        _check(
            check_id="raw_external_not_sent_to_child_core",
            passed=not raw_target_blocked,
            message="Raw external input may not be handed directly to child cores.",
            details={
                "raw_input": raw_input,
                "external_source": external_source,
                "target_child_core": target_child_core,
            },
        )
    )

    if raw_target_blocked:
        reasons.append(
            _reason(
                "raw_external_child_core_bypass",
                "Cross-core handoff blocked because raw external input targeted a child core.",
                {
                    "raw_input": raw_input,
                    "external_source": external_source,
                    "target_child_core": target_child_core,
                },
            )
        )

    for claim in sorted(FORBIDDEN_AUTHORITY_CLAIMS):
        claim_value = authority.get(claim)
        claim_ok = claim_value is False

        checks.append(
            _check(
                check_id=f"authority_claim_false:{claim}",
                passed=claim_ok,
                message=f"Cross-core packet may not claim {claim}.",
                details={"value": claim_value},
            )
        )

        if not claim_ok:
            reasons.append(
                _reason(
                    f"forbidden_authority_claim:{claim}",
                    f"Cross-core handoff blocked because authority.{claim} is not false.",
                    {"value": claim_value},
                )
            )

    bounded = source_packet.get("bounded") is True
    sealed = source_packet.get("sealed") is True

    checks.append(
        _check(
            check_id="packet_bounded",
            passed=bounded,
            message="Cross-core handoff packet must be bounded.",
        )
    )
    if not bounded:
        reasons.append(
            _reason(
                "packet_not_bounded",
                "Cross-core handoff blocked because packet is not bounded.",
            )
        )

    checks.append(
        _check(
            check_id="packet_sealed",
            passed=sealed,
            message="Cross-core handoff packet must be sealed.",
        )
    )
    if not sealed:
        reasons.append(
            _reason(
                "packet_not_sealed",
                "Cross-core handoff blocked because packet is not sealed.",
            )
        )

    allowed = len(reasons) == 0

    return {
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "artifact_type": "cross_core_enforcement_decision",
        "artifact_version": CROSS_CORE_ENFORCER_VERSION,
        "checked_at": _utc_now_iso(),
        "target_child_core": target_child_core,
        "checks": checks,
        "reasons": reasons,
        "policy": {
            "root_spine_required": True,
            "engines_authority_required": True,
            "curates_before_child_core_required": True,
            "research_core_lineage_required": True,
            "engine_interpretation_required": True,
            "engine_signal_integrity_required": True,
            "engine_output_registry_required": True,
            "engine_confidence_conservation_required": True,
            "engine_drift_guard_required_when_candidate_supplied": True,
            "adapter_required": True,
            "raw_external_to_child_core_allowed": False,
            "downstream_reweighting_allowed": False,
            "child_core_reinterpretation_allowed": False,
            "execution_allowed": False,
            "mutation_allowed": False,
        },
        "message": (
            "Cross-core handoff allowed."
            if allowed
            else "Cross-core handoff blocked."
        ),
    }


def enforce_cross_core_handoff(
    packet: Dict[str, Any],
    *,
    original_handoff_packet: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    decision = evaluate_cross_core_handoff(
        packet,
        original_handoff_packet=original_handoff_packet,
    )

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "cross_core_handoff_blocked",
                "decision": decision,
            }
        )

    return decision