# AI_GO/core/execution_gate/runtime_execution_gate.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ExecutionGateError(RuntimeError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalize_status(value: Any) -> str:
    return _safe_str(value).lower()


def _is_pass_status(value: Any) -> bool:
    return _normalize_status(value) in {
        "pass",
        "passed",
        "ok",
        "valid",
        "allowed",
        "approved",
    }


def _is_true(value: Any) -> bool:
    return value is True


def _collect_block_reason(
    *,
    reasons: List[str],
    condition: bool,
    reason: str,
) -> None:
    if condition:
        reasons.append(reason)


def evaluate_execution_gate(
    *,
    watcher: Dict[str, Any],
    state: Dict[str, Any],
    canon: Dict[str, Any],
    request: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Final execution authority.

    This gate must run after:
    - Watcher validation
    - State validation
    - Canon validation

    This gate must run before:
    - File writes
    - Receipt writes
    - Email delivery
    - Workflow mutation
    - Artifact creation

    No side effect is lawful unless this returns allowed=True.
    """

    watcher_payload = _safe_dict(watcher)
    state_payload = _safe_dict(state)
    canon_payload = _safe_dict(canon)
    request_payload = _safe_dict(request)

    watcher_status = watcher_payload.get("status")
    state_status = state_payload.get("status")
    canon_status = canon_payload.get("status")

    watcher_valid = (
        _is_true(watcher_payload.get("valid"))
        or _is_pass_status(watcher_status)
        or _is_pass_status(watcher_payload.get("watcher_status"))
    )

    state_valid = (
        _is_true(state_payload.get("valid"))
        or _is_pass_status(state_status)
        or _is_pass_status(state_payload.get("state_status"))
    )

    canon_valid = (
        _is_true(canon_payload.get("valid"))
        or _is_pass_status(canon_status)
        or _is_pass_status(canon_payload.get("canon_status"))
    )

    execution_allowed = (
        _is_true(canon_payload.get("execution_allowed"))
        or _is_true(canon_payload.get("execution_permitted"))
        or _is_true(canon_payload.get("allow_execution"))
    )

    approval_required = canon_payload.get("approval_required", True)
    approval_present = (
        _is_true(canon_payload.get("approved"))
        or _is_true(canon_payload.get("operator_approved"))
        or _is_pass_status(canon_payload.get("approval_status"))
    )

    reasons: List[str] = []

    _collect_block_reason(
        reasons=reasons,
        condition=not watcher_valid,
        reason="watcher_not_passed",
    )
    _collect_block_reason(
        reasons=reasons,
        condition=not state_valid,
        reason="state_not_passed",
    )
    _collect_block_reason(
        reasons=reasons,
        condition=not canon_valid,
        reason="canon_not_passed",
    )
    _collect_block_reason(
        reasons=reasons,
        condition=not execution_allowed,
        reason="execution_not_permitted_by_canon",
    )
    _collect_block_reason(
        reasons=reasons,
        condition=approval_required is True and not approval_present,
        reason="required_approval_missing",
    )

    allowed = len(reasons) == 0

    return {
        "artifact_type": "execution_gate_decision",
        "artifact_version": "v1",
        "evaluated_at": _utc_now_iso(),
        "status": "pass" if allowed else "blocked",
        "allowed": allowed,
        "reasons": reasons,
        "request": {
            "request_id": request_payload.get("request_id"),
            "route": request_payload.get("route"),
            "action": request_payload.get("action"),
            "project_id": request_payload.get("project_id"),
            "phase_id": request_payload.get("phase_id"),
        },
        "inputs": {
            "watcher_status": watcher_status,
            "watcher_valid": watcher_valid,
            "state_status": state_status,
            "state_valid": state_valid,
            "canon_status": canon_status,
            "canon_valid": canon_valid,
            "execution_allowed": execution_allowed,
            "approval_required": approval_required,
            "approval_present": approval_present,
        },
        "authority": {
            "side_effects_allowed_after_pass": [
                "file_write",
                "receipt_write",
                "artifact_creation",
                "email_delivery",
                "workflow_mutation",
            ],
            "side_effects_allowed_before_pass": [],
            "bypass_allowed": False,
        },
        "sealed": True,
    }


def enforce_execution_gate(decision: Dict[str, Any]) -> None:
    """
    Hard stop.

    If this raises, caller must not perform any side effects.
    """

    if not isinstance(decision, dict):
        raise ExecutionGateError("Execution blocked: invalid gate decision")

    if decision.get("allowed") is not True:
        reasons = decision.get("reasons", [])
        raise ExecutionGateError(f"Execution blocked by gate: {reasons}")


def assert_execution_allowed(
    *,
    watcher: Dict[str, Any],
    state: Dict[str, Any],
    canon: Dict[str, Any],
    request: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience wrapper.

    Returns the gate decision only if execution is allowed.
    Raises ExecutionGateError otherwise.
    """

    decision = evaluate_execution_gate(
        watcher=watcher,
        state=state,
        canon=canon,
        request=request,
    )
    enforce_execution_gate(decision)
    return decision