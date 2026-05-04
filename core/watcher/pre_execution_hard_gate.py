from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List


PRE_EXECUTION_HARD_GATE_VERSION = "v1.0"
ARTIFACT_TYPE = "pre_execution_hard_gate_decision"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _hash(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _reason(
    *,
    code: str,
    severity: str,
    message: str,
    details: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "details": details or {},
    }


def _check(
    *,
    check_id: str,
    passed: bool,
    severity: str,
    message: str,
    details: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "check_id": check_id,
        "passed": passed,
        "severity": severity,
        "message": message,
        "details": details or {},
    }


def _extract_watcher_enforcement(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(payload.get("watcher_enforcement_decision"))


def _extract_execution_gate(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(payload.get("execution_gate"))


def _extract_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(payload.get("state"))


def _extract_base_watcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(payload.get("watcher"))


def _validate_state(
    *,
    state: Dict[str, Any],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    valid = state.get("valid") is True

    checks.append(
        _check(
            check_id="state_valid",
            passed=valid,
            severity="blocker",
            message="Pre-execution hard gate requires state.valid=true.",
            details={"state": state},
        )
    )

    if not valid:
        reasons.append(
            _reason(
                code="state_invalid",
                severity="blocker",
                message="Pre-execution hard gate blocked execution because state validation did not pass.",
                details={"state": state},
            )
        )


def _validate_base_watcher(
    *,
    watcher: Dict[str, Any],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    valid = watcher.get("valid") is True

    checks.append(
        _check(
            check_id="base_watcher_valid",
            passed=valid,
            severity="blocker",
            message="Pre-execution hard gate requires base watcher.valid=true.",
            details={"watcher": watcher},
        )
    )

    if not valid:
        reasons.append(
            _reason(
                code="base_watcher_invalid",
                severity="blocker",
                message="Pre-execution hard gate blocked execution because base watcher validation did not pass.",
                details={"watcher": watcher},
            )
        )


def _validate_watcher_enforcement(
    *,
    watcher_enforcement: Dict[str, Any],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
    escalations: List[Dict[str, Any]],
) -> None:
    present = bool(watcher_enforcement)

    checks.append(
        _check(
            check_id="watcher_enforcement_present",
            passed=present,
            severity="blocker",
            message="Pre-execution hard gate requires watcher enforcement decision.",
            details={"watcher_enforcement_present": present},
        )
    )

    if not present:
        reasons.append(
            _reason(
                code="watcher_enforcement_missing",
                severity="blocker",
                message="Execution is blocked because watcher enforcement decision is missing.",
            )
        )
        return

    artifact_type = _clean(watcher_enforcement.get("artifact_type"))
    sealed = watcher_enforcement.get("sealed") is True
    allowed = watcher_enforcement.get("allowed") is True
    blocked = watcher_enforcement.get("blocked") is True
    status = _clean(watcher_enforcement.get("status"))
    decision = _clean(watcher_enforcement.get("decision"))
    decision_hash = _clean(watcher_enforcement.get("decision_hash"))

    valid_shape = (
        artifact_type == "watcher_enforcement_decision"
        and sealed
        and bool(decision_hash)
        and status in {"allowed", "allowed_with_escalation", "blocked"}
        and decision in {"allow", "allow_with_escalation", "block"}
    )

    checks.append(
        _check(
            check_id="watcher_enforcement_shape_valid",
            passed=valid_shape,
            severity="blocker",
            message="Watcher enforcement decision must be sealed and well-formed.",
            details={
                "artifact_type": artifact_type,
                "sealed": sealed,
                "status": status,
                "decision": decision,
                "decision_hash_present": bool(decision_hash),
            },
        )
    )

    if not valid_shape:
        reasons.append(
            _reason(
                code="watcher_enforcement_invalid_shape",
                severity="blocker",
                message="Execution is blocked because watcher enforcement decision is malformed.",
                details={
                    "artifact_type": artifact_type,
                    "sealed": sealed,
                    "status": status,
                    "decision": decision,
                    "decision_hash_present": bool(decision_hash),
                },
            )
        )
        return

    checks.append(
        _check(
            check_id="watcher_enforcement_allowed",
            passed=allowed and not blocked,
            severity="blocker",
            message="Watcher enforcement must allow execution before execution gate is used.",
            details={
                "allowed": allowed,
                "blocked": blocked,
                "status": status,
                "decision": decision,
            },
        )
    )

    if not allowed or blocked:
        reasons.append(
            _reason(
                code="watcher_enforcement_blocked",
                severity="blocker",
                message="Execution is blocked because watcher enforcement did not allow action.",
                details={
                    "allowed": allowed,
                    "blocked": blocked,
                    "status": status,
                    "decision": decision,
                    "reasons": _safe_list(watcher_enforcement.get("reasons")),
                },
            )
        )
        return

    if watcher_enforcement.get("escalation_required") is True:
        escalations.append(
            _reason(
                code="watcher_enforcement_escalation_required",
                severity="escalation",
                message="Watcher enforcement allowed execution with escalation.",
                details={
                    "status": status,
                    "decision": decision,
                    "escalations": _safe_list(watcher_enforcement.get("escalations")),
                },
            )
        )


def _validate_execution_gate(
    *,
    execution_gate: Dict[str, Any],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    allowed = execution_gate.get("allowed") is True

    checks.append(
        _check(
            check_id="execution_gate_allowed",
            passed=allowed,
            severity="blocker",
            message="Execution gate must allow execution after watcher enforcement passes.",
            details={"execution_gate": execution_gate},
        )
    )

    if not allowed:
        reasons.append(
            _reason(
                code="execution_gate_not_allowed",
                severity="blocker",
                message="Execution is blocked because execution gate did not allow action.",
                details={"execution_gate": execution_gate},
            )
        )


def evaluate_pre_execution_hard_gate(
    *,
    payload: Dict[str, Any],
    action: str,
    profile: str,
    actor: str = "pre_execution_hard_gate",
) -> Dict[str, Any]:
    """
    Phase 3.4 hard gate.

    Required order:
        state → base watcher → watcher enforcement → execution gate → executor

    This function does not execute.
    It only returns a sealed allow/block decision.
    """

    source = payload if isinstance(payload, dict) else {}

    state = _extract_state(source)
    watcher = _extract_base_watcher(source)
    watcher_enforcement = _extract_watcher_enforcement(source)
    execution_gate = _extract_execution_gate(source)

    checks: List[Dict[str, Any]] = []
    reasons: List[Dict[str, Any]] = []
    escalations: List[Dict[str, Any]] = []

    _validate_state(
        state=state,
        checks=checks,
        reasons=reasons,
    )
    _validate_base_watcher(
        watcher=watcher,
        checks=checks,
        reasons=reasons,
    )
    _validate_watcher_enforcement(
        watcher_enforcement=watcher_enforcement,
        checks=checks,
        reasons=reasons,
        escalations=escalations,
    )
    _validate_execution_gate(
        execution_gate=execution_gate,
        checks=checks,
        reasons=reasons,
    )

    blocked = bool(reasons)
    status = "blocked" if blocked else "allowed"
    decision = "block" if blocked else "allow"

    if not blocked and escalations:
        status = "allowed_with_escalation"
        decision = "allow_with_escalation"

    output = {
        "artifact_type": ARTIFACT_TYPE,
        "artifact_version": PRE_EXECUTION_HARD_GATE_VERSION,
        "created_at": _utc_now_iso(),
        "profile": _clean(profile),
        "action": _clean(action),
        "actor": _clean(actor) or "pre_execution_hard_gate",
        "status": status,
        "decision": decision,
        "allowed": not blocked,
        "blocked": blocked,
        "escalation_required": bool(escalations),
        "checks": checks,
        "reasons": reasons,
        "escalations": escalations,
        "source": {
            "state_hash": _hash(state) if state else "",
            "watcher_hash": _hash(watcher) if watcher else "",
            "watcher_enforcement_hash": watcher_enforcement.get("decision_hash", ""),
            "execution_gate_hash": _hash(execution_gate) if execution_gate else "",
        },
        "required_order": [
            "state",
            "base_watcher",
            "watcher_enforcement",
            "execution_gate",
            "executor",
        ],
        "authority": {
            "watcher_gate_owned": True,
            "may_block_execution": True,
            "may_execute": False,
            "may_mutate_state": False,
            "execution_permission_source": "watcher_enforcement_plus_execution_gate",
        },
        "constraints": {
            "decision_only": True,
            "no_direct_execution": True,
            "no_direct_state_mutation": True,
            "must_precede_executor": True,
            "missing_watcher_enforcement_blocks": True,
            "blocked_watcher_enforcement_blocks": True,
            "malformed_watcher_enforcement_blocks": True,
        },
        "sealed": True,
    }

    output["hard_gate_hash"] = _hash(
        {
            key: value
            for key, value in output.items()
            if key != "hard_gate_hash"
        }
    )

    return output


def assert_pre_execution_allowed(
    *,
    payload: Dict[str, Any],
    action: str,
    profile: str,
    actor: str = "pre_execution_hard_gate",
) -> Dict[str, Any]:
    decision = evaluate_pre_execution_hard_gate(
        payload=payload,
        action=action,
        profile=profile,
        actor=actor,
    )

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "pre_execution_hard_gate_blocked",
                "decision": decision,
            }
        )

    return decision