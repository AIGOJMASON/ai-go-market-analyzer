from __future__ import annotations

from typing import Any, Dict, List


EXECUTION_GATE_VERSION = "northstar_execution_gate_v1.1"


def _is_true(context: Dict[str, Any], *keys: str) -> bool:
    for key in keys:
        if context.get(key) is True:
            return True
    return False


def _append_check(
    *,
    name: str,
    condition: bool,
    fail_reason: str,
    passed_checks: List[str],
    failed_checks: List[str],
    reasons: List[Dict[str, Any]],
) -> None:
    if condition:
        passed_checks.append(name)
        return

    failed_checks.append(name)
    reasons.append(
        {
            "code": name,
            "message": fail_reason,
        }
    )


def evaluate_execution_gate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Global pre-execution and pre-mutation gate.

    This gate does not replace State Authority, Watcher, Canon, Request Governor,
    or Cross-Core Integrity. It verifies that all required upstream approvals are
    present immediately before side effects.
    """

    if not isinstance(context, dict):
        context = {}

    reasons: List[Dict[str, Any]] = []
    passed_checks: List[str] = []
    failed_checks: List[str] = []

    check = lambda name, condition, message: _append_check(
        name=name,
        condition=condition,
        fail_reason=message,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        reasons=reasons,
    )

    check(
        "state_authority_required",
        _is_true(context, "state_authority_passed", "state_passed"),
        "State Authority must pass before mutation or execution.",
    )
    check(
        "watcher_required",
        _is_true(context, "watcher_passed"),
        "Watcher must pass before mutation or execution.",
    )
    check(
        "canon_required",
        _is_true(context, "canon_passed"),
        "Canon must pass before mutation or execution.",
    )
    check(
        "governor_required",
        _is_true(context, "governor_passed"),
        "Request Governor must pass before mutation or execution.",
    )
    check(
        "operator_approval_required",
        _is_true(context, "operator_approved"),
        "Explicit operator approval is required before mutation or execution.",
    )
    check(
        "receipt_required",
        _is_true(context, "receipt_planned", "receipt_ready", "receipt_present"),
        "A receipt must be planned or available before mutation or execution.",
    )
    check(
        "cross_core_integrity_required",
        _is_true(context, "cross_core_integrity_passed", "cross_core_passed"),
        "Cross-Core Integrity must pass before mutation or execution.",
    )

    if context.get("external_source") is True:
        check(
            "no_raw_external_input",
            context.get("raw_input") is not True,
            "Raw external input cannot execute or mutate directly.",
        )

    if context.get("requires_research_lineage") is True:
        check(
            "research_lineage_required",
            context.get("research_lineage") is True,
            "Execution requires RESEARCH_CORE lineage when external source lineage is required.",
        )
        check(
            "engine_processing_required",
            context.get("engine_processed") is True,
            "Execution requires governed engine processing when external source lineage is required.",
        )
        check(
            "adapter_required",
            context.get("adapter_applied") is True,
            "Execution requires adapter normalization when external source lineage is required.",
        )

    allowed = not reasons

    return {
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "execution_gate_version": EXECUTION_GATE_VERSION,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "reasons": reasons,
        "message": (
            "Execution gate passed."
            if allowed
            else "Execution blocked by pre-execution gate."
        ),
    }