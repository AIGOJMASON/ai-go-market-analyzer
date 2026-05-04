from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List


WATCHER_ENFORCEMENT_VERSION = "v1.0"
ARTIFACT_TYPE = "watcher_enforcement_decision"


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


def _extract_base_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "state": _safe_dict(payload.get("state")),
        "watcher": _safe_dict(payload.get("watcher")),
        "execution_gate": _safe_dict(payload.get("execution_gate")),
        "governance_decision": _safe_dict(payload.get("governance_decision")),
        "result_summary": _safe_dict(payload.get("result_summary")),
        "pm_behavior_application": _safe_dict(payload.get("pm_behavior_application")),
        "pm_refinement_context": _safe_dict(payload.get("pm_refinement_context")),
        "pm_context": _safe_dict(payload.get("pm_context")),
    }


def _behavior_flags(pm_behavior_application: Dict[str, Any]) -> List[str]:
    flags: List[str] = []

    for item in _safe_list(pm_behavior_application.get("behavior_items")):
        item_dict = _safe_dict(item)
        for flag in _safe_list(item_dict.get("advisory_flags")):
            cleaned = _clean(flag)
            if cleaned:
                flags.append(cleaned)

    return sorted(set(flags))


def _behavior_may_fields(pm_behavior_application: Dict[str, Any]) -> Dict[str, bool]:
    may_block = False
    may_mutate = False
    may_execute = False

    for item in _safe_list(pm_behavior_application.get("behavior_items")):
        item_dict = _safe_dict(item)
        may_block = may_block or bool(item_dict.get("may_block") is True)
        may_mutate = may_mutate or bool(item_dict.get("may_mutate") is True)
        may_execute = may_execute or bool(item_dict.get("may_execute") is True)

    return {
        "may_block": may_block,
        "may_mutate": may_mutate,
        "may_execute": may_execute,
    }


def _evaluate_state(
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
            message="State validation must pass before watcher enforcement can allow action.",
            details={"state": state},
        )
    )

    if not valid:
        reasons.append(
            _reason(
                code="state_invalid",
                severity="blocker",
                message="Watcher Enforcement blocked action because state validation did not pass.",
                details={"state": state},
            )
        )


def _evaluate_watcher(
    *,
    watcher: Dict[str, Any],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    valid = watcher.get("valid") is True

    checks.append(
        _check(
            check_id="watcher_valid",
            passed=valid,
            severity="blocker",
            message="Base watcher validation must pass before watcher enforcement can allow action.",
            details={"watcher": watcher},
        )
    )

    if not valid:
        reasons.append(
            _reason(
                code="watcher_invalid",
                severity="blocker",
                message="Watcher Enforcement blocked action because base watcher validation did not pass.",
                details={"watcher": watcher},
            )
        )


def _evaluate_execution_gate(
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
            message="Execution gate must be allowed before watcher enforcement can allow action.",
            details={"execution_gate": execution_gate},
        )
    )

    if not allowed:
        reasons.append(
            _reason(
                code="execution_gate_not_allowed",
                severity="blocker",
                message="Watcher Enforcement blocked action because execution gate did not allow execution.",
                details={"execution_gate": execution_gate},
            )
        )


def _evaluate_result_summary(
    *,
    result_summary: Dict[str, Any],
    checks: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    if not result_summary:
        checks.append(
            _check(
                check_id="result_summary_present",
                passed=True,
                severity="info",
                message="No result summary present. Pre-execution enforcement may continue.",
            )
        )
        return

    sealed = result_summary.get("sealed") is True
    artifact_type = _clean(result_summary.get("artifact_type"))
    effect = _clean(result_summary.get("effect"))

    valid_summary = (
        sealed
        and artifact_type == "post_execution_result_summary"
        and effect in {
            "execution_completed",
            "execution_partial_delivery_failed",
            "execution_blocked",
            "execution_result_unknown",
        }
    )

    checks.append(
        _check(
            check_id="result_summary_valid",
            passed=valid_summary,
            severity="blocker",
            message="Post-execution result summaries must be sealed and use approved effects.",
            details={"result_summary": result_summary},
        )
    )

    if not valid_summary:
        reasons.append(
            _reason(
                code="result_summary_invalid",
                severity="blocker",
                message="Watcher Enforcement blocked continuation because result summary is invalid.",
                details={"result_summary": result_summary},
            )
        )


def _evaluate_pm_behavior(
    *,
    pm_behavior_application: Dict[str, Any],
    checks: List[Dict[str, Any]],
    escalations: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
) -> None:
    if not pm_behavior_application:
        checks.append(
            _check(
                check_id="pm_behavior_application_present",
                passed=True,
                severity="info",
                message="No PM behavior application present. Enforcement continues without PM behavior escalation.",
            )
        )
        return

    sealed = pm_behavior_application.get("sealed") is True
    authority = _safe_dict(pm_behavior_application.get("authority"))
    constraints = _safe_dict(pm_behavior_application.get("constraints"))
    may_fields = _behavior_may_fields(pm_behavior_application)
    flags = _behavior_flags(pm_behavior_application)

    safe_authority = all(
        [
            authority.get("pm_owned") is True,
            authority.get("advisory_only") is True,
            authority.get("execution_allowed") is False,
            authority.get("mutation_allowed") is False,
            authority.get("grants_authority") is False,
            constraints.get("annotation_only") is True,
            constraints.get("no_auto_execution") is True,
            constraints.get("no_direct_state_mutation") is True,
            may_fields["may_block"] is False,
            may_fields["may_mutate"] is False,
            may_fields["may_execute"] is False,
        ]
    )

    checks.append(
        _check(
            check_id="pm_behavior_safe_authority",
            passed=sealed and safe_authority,
            severity="blocker",
            message="PM behavior application must remain advisory-only and non-mutating.",
            details={
                "sealed": sealed,
                "authority": authority,
                "constraints": constraints,
                "may_fields": may_fields,
                "advisory_flags": flags,
            },
        )
    )

    if not sealed or not safe_authority:
        reasons.append(
            _reason(
                code="pm_behavior_authority_violation",
                severity="blocker",
                message="Watcher Enforcement blocked action because PM behavior attempted to exceed advisory authority.",
                details={
                    "sealed": sealed,
                    "authority": authority,
                    "constraints": constraints,
                    "may_fields": may_fields,
                },
            )
        )
        return

    caution_flags = {
        "unverified_assumption_present",
        "requires_pm_caution_note",
        "requires_risk_review_note",
        "requires_router_constraint_note",
    }

    active_caution_flags = sorted(set(flags).intersection(caution_flags))

    if active_caution_flags:
        escalations.append(
            _reason(
                code="pm_behavior_caution_escalation",
                severity="escalation",
                message="PM behavior guidance contains caution flags. Continue only as governed advisory context.",
                details={"advisory_flags": active_caution_flags},
            )
        )


def enforce_watcher_decision(
    *,
    payload: Dict[str, Any],
    action: str,
    profile: str,
    actor: str = "watcher_enforcement",
) -> Dict[str, Any]:
    """
    Phase 3 watcher enforcement.

    This function does not execute anything.
    It returns a blocking / allowed / escalation decision that can sit between
    existing watcher validation and execution gate use.
    """

    source = payload if isinstance(payload, dict) else {}
    context = _extract_base_context(source)

    checks: List[Dict[str, Any]] = []
    reasons: List[Dict[str, Any]] = []
    escalations: List[Dict[str, Any]] = []

    _evaluate_state(
        state=context["state"],
        checks=checks,
        reasons=reasons,
    )
    _evaluate_watcher(
        watcher=context["watcher"],
        checks=checks,
        reasons=reasons,
    )
    _evaluate_execution_gate(
        execution_gate=context["execution_gate"],
        checks=checks,
        reasons=reasons,
    )
    _evaluate_result_summary(
        result_summary=context["result_summary"],
        checks=checks,
        reasons=reasons,
    )
    _evaluate_pm_behavior(
        pm_behavior_application=context["pm_behavior_application"],
        checks=checks,
        escalations=escalations,
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
        "artifact_version": WATCHER_ENFORCEMENT_VERSION,
        "created_at": _utc_now_iso(),
        "profile": _clean(profile),
        "action": _clean(action),
        "actor": _clean(actor) or "watcher_enforcement",
        "status": status,
        "decision": decision,
        "allowed": not blocked,
        "blocked": blocked,
        "escalation_required": bool(escalations),
        "rollback_recommended": blocked,
        "checks": checks,
        "reasons": reasons,
        "escalations": escalations,
        "authority": {
            "watcher_owned": True,
            "may_block": True,
            "may_escalate": True,
            "may_recommend_rollback": True,
            "may_execute_rollback": False,
            "may_mutate_state": False,
            "execution_allowed": False,
        },
        "constraints": {
            "decision_only": True,
            "no_direct_execution": True,
            "no_direct_state_mutation": True,
            "must_precede_execution": True,
        },
        "sealed": True,
    }

    output["decision_hash"] = _hash(
        {
            key: value
            for key, value in output.items()
            if key != "decision_hash"
        }
    )

    return output


def assert_watcher_allowed(
    *,
    payload: Dict[str, Any],
    action: str,
    profile: str,
    actor: str = "watcher_enforcement",
) -> Dict[str, Any]:
    decision = enforce_watcher_decision(
        payload=payload,
        action=action,
        profile=profile,
        actor=actor,
    )

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "watcher_enforcement_blocked",
                "decision": decision,
            }
        )

    return decision