from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.engines.engine_signal_contract import validate_engine_interpretation_packet


ROUTE_ENFORCEMENT_VERSION = "v5C.1"


HARD_BLOCKED_ROUTES = {
    "/market-analyzer/run/live": {
        "reason": "legacy_raw_live_route_disabled",
        "message": (
            "Direct live Market Analyzer route is disabled. "
            "Use /market-analyzer/run/curated-live with a governed engine_handoff_packet."
        ),
    },
}


CURATED_ROUTE_REQUIREMENTS = {
    "/market-analyzer/run/curated-live": {
        "required_packet": "engine_handoff_packet",
        "target_child_core": "market_analyzer_v1",
    },
}


RAW_LIVE_FIELDS = {
    "symbol",
    "headline",
    "price_change_pct",
    "sector",
    "confirmation",
    "provider_payload",
    "raw_provider_payload",
    "raw_external_input",
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


def _payload_has_raw_live_shape(payload: Dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False

    present = {key for key in payload.keys() if key in RAW_LIVE_FIELDS}
    return len(present) >= 3


def _engine_handoff_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    packet = _safe_dict(payload.get("engine_handoff_packet"))
    if packet:
        return packet

    return _safe_dict(payload.get("curated_child_core_handoff_packet"))


def _engine_handoff_targets_market_analyzer(packet: Dict[str, Any]) -> bool:
    return _safe_str(packet.get("target_child_core")) == "market_analyzer_v1"


def _engine_interpretation_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("engine_interpretation_packet"))


def _engine_signal_integrity(packet: Dict[str, Any]) -> Dict[str, Any]:
    existing = _safe_dict(packet.get("engine_signal_integrity"))
    if existing:
        return existing

    interpretation_packet = _engine_interpretation_packet(packet)
    if interpretation_packet:
        return validate_engine_interpretation_packet(interpretation_packet)

    return {
        "status": "blocked",
        "valid": False,
        "allowed": False,
        "errors": ["missing_engine_interpretation_packet"],
    }


def evaluate_route_level_access(
    *,
    route: str,
    method: str,
    payload: Dict[str, Any],
    actor: str = "unknown",
) -> Dict[str, Any]:
    """
    Phase 5C.1 route-level guard.

    This preserves 5B blocking and adds engine meaning enforcement.
    Curated routes may pass only with a valid engine interpretation packet.
    """

    clean_route = _safe_str(route)
    clean_method = _safe_str(method).upper()
    source_payload = payload if isinstance(payload, dict) else {}

    checks: List[Dict[str, Any]] = []
    reasons: List[Dict[str, Any]] = []

    hard_block = HARD_BLOCKED_ROUTES.get(clean_route)
    if hard_block:
        checks.append(
            _check(
                check_id="route_not_hard_blocked",
                passed=False,
                message="Route is hard-blocked by Phase 5B.3.",
                details={
                    "route": clean_route,
                    "reason": hard_block["reason"],
                },
            )
        )
        reasons.append(
            _reason(
                hard_block["reason"],
                hard_block["message"],
                {
                    "route": clean_route,
                    "method": clean_method,
                    "actor": actor,
                },
            )
        )

    curated_requirements = CURATED_ROUTE_REQUIREMENTS.get(clean_route)
    if curated_requirements:
        packet_name = curated_requirements["required_packet"]
        packet = _engine_handoff_packet(source_payload)
        has_packet = bool(packet)

        checks.append(
            _check(
                check_id="curated_engine_handoff_packet_present",
                passed=has_packet,
                message="Curated live route requires engine_handoff_packet.",
                details={"required_packet": packet_name},
            )
        )

        if not has_packet:
            reasons.append(
                _reason(
                    "curated_engine_handoff_packet_missing",
                    "Curated live route requires governed engine_handoff_packet.",
                    {"required_packet": packet_name},
                )
            )

        targets_market_analyzer = _engine_handoff_targets_market_analyzer(packet)
        checks.append(
            _check(
                check_id="curated_packet_targets_market_analyzer",
                passed=targets_market_analyzer,
                message="Engine handoff packet must target market_analyzer_v1.",
                details={"target_child_core": packet.get("target_child_core")},
            )
        )

        if has_packet and not targets_market_analyzer:
            reasons.append(
                _reason(
                    "curated_packet_wrong_target",
                    "Curated live route blocked because engine_handoff_packet does not target market_analyzer_v1.",
                    {"target_child_core": packet.get("target_child_core")},
                )
            )

        interpretation_packet = _engine_interpretation_packet(packet)
        has_interpretation = bool(interpretation_packet)

        checks.append(
            _check(
                check_id="engine_interpretation_packet_present",
                passed=has_interpretation,
                message="Curated route requires engine interpretation packet.",
            )
        )

        if has_packet and not has_interpretation:
            reasons.append(
                _reason(
                    "engine_interpretation_packet_missing",
                    "Curated route blocked because engine meaning was not assigned.",
                    {"route": clean_route},
                )
            )

        integrity = _engine_signal_integrity(packet)
        integrity_allowed = bool(integrity.get("allowed") is True)

        checks.append(
            _check(
                check_id="engine_signal_integrity_passed",
                passed=integrity_allowed,
                message="Engine signal integrity must pass before curated route can continue.",
                details=integrity,
            )
        )

        if has_packet and not integrity_allowed:
            reasons.append(
                _reason(
                    "engine_signal_integrity_failed",
                    "Curated route blocked because engine signal integrity failed.",
                    {"engine_signal_integrity": integrity},
                )
            )

        raw_shape = _payload_has_raw_live_shape(source_payload) and not has_packet
        checks.append(
            _check(
                check_id="curated_route_rejects_raw_live_shape",
                passed=not raw_shape,
                message="Curated route may not receive raw live payload shape.",
            )
        )

        if raw_shape:
            reasons.append(
                _reason(
                    "raw_live_payload_rejected",
                    "Raw live payloads must enter through RESEARCH_CORE and engines before curated-live.",
                    {"route": clean_route},
                )
            )

    allowed = len(reasons) == 0

    return {
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "artifact_type": "route_level_enforcement_decision",
        "artifact_version": ROUTE_ENFORCEMENT_VERSION,
        "checked_at": _utc_now_iso(),
        "route": clean_route,
        "method": clean_method,
        "actor": actor,
        "checks": checks,
        "reasons": reasons,
        "policy": {
            "legacy_raw_live_route_allowed": False,
            "curated_live_requires_engine_handoff": True,
            "curated_live_requires_engine_interpretation": True,
            "curated_live_requires_engine_signal_integrity": True,
            "raw_provider_payload_to_child_core_allowed": False,
            "child_core_reinterpretation_allowed": False,
            "downstream_reweighting_allowed": False,
        },
        "message": (
            "Route-level access allowed."
            if allowed
            else "Route-level access blocked."
        ),
    }


def enforce_route_level_access(
    *,
    route: str,
    method: str,
    payload: Dict[str, Any],
    actor: str = "unknown",
) -> Dict[str, Any]:
    decision = evaluate_route_level_access(
        route=route,
        method=method,
        payload=payload,
        actor=actor,
    )

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "route_level_access_blocked",
                "decision": decision,
            }
        )

    return decision