from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .continuity_receipt_builder import (
    build_continuity_failure_receipt,
    build_continuity_hold_receipt,
    build_continuity_intake_receipt,
)
from .continuity_registry import (
    CURRENT_POLICY_VERSION,
    is_allowed_policy_version,
    is_allowed_scope,
    is_registered_target,
)
from .continuity_state import ContinuityState, update_state


REQUIRED_CONTEXT_KEYS = {
    "target_core",
    "watcher_id",
    "watcher_receipt_ref",
    "output_disposition_ref",
    "runtime_ref",
    "event_timestamp",
    "continuity_scope",
    "intake_reason",
    "admission_policy_version",
}

LINEAGE_CONTEXT_KEYS = {
    "watcher_receipt_ref",
    "output_disposition_ref",
    "runtime_ref",
}


@dataclass(frozen=True)
class ContinuityDecision:
    disposition: str
    reason: str
    rejection_code: Optional[str] = None
    admission_basis: Optional[str] = None
    hold_release_condition: Optional[str] = None
    hold_review_window: Optional[str] = None


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _validate_watcher_result(watcher_result: Any) -> Tuple[bool, Optional[str], str]:
    if not isinstance(watcher_result, dict):
        return False, "structural_invalid", "watcher_result must be a dictionary"

    if "findings" not in watcher_result:
        return False, "structural_invalid", "watcher_result missing findings"

    findings = watcher_result.get("findings")
    if not isinstance(findings, dict):
        return False, "structural_invalid", "watcher_result findings must be a dictionary"

    if not findings:
        return False, "insufficient_signal", "watcher_result findings may not be empty"

    return True, None, "valid"


def _validate_continuity_context(context: Any) -> Tuple[bool, Optional[str], str]:
    if not isinstance(context, dict):
        return False, "structural_invalid", "continuity_context must be a dictionary"

    missing = [key for key in sorted(REQUIRED_CONTEXT_KEYS) if key not in context]
    if missing:
        return False, "structural_invalid", f"continuity_context missing keys: {', '.join(missing)}"

    non_lineage_keys = REQUIRED_CONTEXT_KEYS - LINEAGE_CONTEXT_KEYS
    bad_keys = [key for key in non_lineage_keys if not _is_non_empty_string(context.get(key))]
    if bad_keys:
        return False, "structural_invalid", f"continuity_context keys must be non-empty strings: {', '.join(sorted(bad_keys))}"

    return True, None, "valid"


def _validate_registry(context: Dict[str, Any]) -> Tuple[bool, Optional[str], str]:
    target_core = context["target_core"]
    continuity_scope = context["continuity_scope"]
    policy_version = context["admission_policy_version"]

    if not is_registered_target(target_core):
        return False, "scope_unlawful", f"target core is not registered: {target_core}"

    if not is_allowed_scope(target_core, continuity_scope):
        return False, "scope_unlawful", f"continuity scope is not allowed for target core: {continuity_scope}"

    if not is_allowed_policy_version(target_core, policy_version):
        return False, "policy_version_invalid", f"policy version is not allowed: {policy_version}"

    return True, None, "valid"


def _validate_lineage(context: Dict[str, Any]) -> Tuple[bool, Optional[str], str]:
    bad_refs = [key for key in sorted(LINEAGE_CONTEXT_KEYS) if not _is_non_empty_string(context.get(key))]
    if bad_refs:
        return False, "lineage_broken", f"required lineage refs missing or empty: {', '.join(bad_refs)}"
    return True, None, "valid"


def _classify_signal(findings: Dict[str, Any]) -> ContinuityDecision:
    if findings.get("critical_failure") is True:
        return ContinuityDecision(
            disposition="accepted",
            reason="critical operational failure is continuity-worthy",
            admission_basis="critical_operational_failure",
        )

    if findings.get("policy_violation") is True:
        return ContinuityDecision(
            disposition="accepted",
            reason="policy violation is continuity-worthy",
            admission_basis="policy_violation",
        )

    if findings.get("durable_relevance") is True:
        return ContinuityDecision(
            disposition="accepted",
            reason="durable domain relevance established",
            admission_basis="durable_domain_relevance",
        )

    if findings.get("requires_survival") is True:
        return ContinuityDecision(
            disposition="accepted",
            reason="issue requires survival beyond current run",
            admission_basis="requires_survival_beyond_run",
        )

    if findings.get("duplicate_event") is True:
        return ContinuityDecision(
            disposition="rejected",
            reason="event appears duplicate",
            rejection_code="duplicate_event",
        )

    if findings.get("stale_event") is True:
        return ContinuityDecision(
            disposition="rejected",
            reason="event appears stale",
            rejection_code="stale_event",
        )

    if findings.get("entropy_block") is True:
        return ContinuityDecision(
            disposition="rejected",
            reason="intake blocked by entropy discipline",
            rejection_code="entropy_block",
        )

    if findings.get("repeated_signal") is True:
        return ContinuityDecision(
            disposition="held",
            reason="repeated signal detected but corroboration still required",
            hold_release_condition="confirm repeated pattern across corroborating run or review decision",
            hold_review_window="next_review_cycle",
        )

    return ContinuityDecision(
        disposition="rejected",
        reason="findings do not establish continuity-worthiness",
        rejection_code="insufficient_signal",
    )


def process_watcher_to_continuity(
    *,
    watcher_result: Dict[str, Any],
    continuity_context: Dict[str, Any],
    state: Optional[ContinuityState] = None,
) -> Dict[str, Any]:
    current_state = state or ContinuityState()

    watcher_ok, watcher_code, watcher_reason = _validate_watcher_result(watcher_result)
    if not watcher_ok:
        failure = build_continuity_failure_receipt(
            target_core=continuity_context.get("target_core") if isinstance(continuity_context, dict) else None,
            rejection_code=watcher_code or "structural_invalid",
            rejection_reason=watcher_reason,
            watcher_receipt_ref=continuity_context.get("watcher_receipt_ref") if isinstance(continuity_context, dict) else None,
            output_disposition_ref=continuity_context.get("output_disposition_ref") if isinstance(continuity_context, dict) else None,
            runtime_ref=continuity_context.get("runtime_ref") if isinstance(continuity_context, dict) else None,
            policy_version=continuity_context.get("admission_policy_version") if isinstance(continuity_context, dict) else None,
        )
        update_state(
            current_state,
            intake_id=failure["failure_id"],
            target_core=failure.get("target_core") or "unknown",
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            receipt_ref=failure.get("receipt_ref"),
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    context_ok, context_code, context_reason = _validate_continuity_context(continuity_context)
    if not context_ok:
        failure = build_continuity_failure_receipt(
            target_core=continuity_context.get("target_core") if isinstance(continuity_context, dict) else None,
            rejection_code=context_code or "structural_invalid",
            rejection_reason=context_reason,
            watcher_receipt_ref=continuity_context.get("watcher_receipt_ref") if isinstance(continuity_context, dict) else None,
            output_disposition_ref=continuity_context.get("output_disposition_ref") if isinstance(continuity_context, dict) else None,
            runtime_ref=continuity_context.get("runtime_ref") if isinstance(continuity_context, dict) else None,
            policy_version=continuity_context.get("admission_policy_version") if isinstance(continuity_context, dict) else None,
        )
        update_state(
            current_state,
            intake_id=failure["failure_id"],
            target_core=failure.get("target_core") or "unknown",
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            receipt_ref=failure.get("receipt_ref"),
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    registry_ok, registry_code, registry_reason = _validate_registry(continuity_context)
    if not registry_ok:
        failure = build_continuity_failure_receipt(
            target_core=continuity_context["target_core"],
            rejection_code=registry_code or "scope_unlawful",
            rejection_reason=registry_reason,
            watcher_receipt_ref=continuity_context.get("watcher_receipt_ref"),
            output_disposition_ref=continuity_context.get("output_disposition_ref"),
            runtime_ref=continuity_context.get("runtime_ref"),
            policy_version=continuity_context["admission_policy_version"],
        )
        update_state(
            current_state,
            intake_id=failure["failure_id"],
            target_core=continuity_context["target_core"],
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            receipt_ref=failure.get("receipt_ref"),
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    lineage_ok, lineage_code, lineage_reason = _validate_lineage(continuity_context)
    if not lineage_ok:
        failure = build_continuity_failure_receipt(
            target_core=continuity_context["target_core"],
            rejection_code=lineage_code or "lineage_broken",
            rejection_reason=lineage_reason,
            watcher_receipt_ref=continuity_context.get("watcher_receipt_ref"),
            output_disposition_ref=continuity_context.get("output_disposition_ref"),
            runtime_ref=continuity_context.get("runtime_ref"),
            policy_version=continuity_context["admission_policy_version"],
        )
        update_state(
            current_state,
            intake_id=failure["failure_id"],
            target_core=continuity_context["target_core"],
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            receipt_ref=failure.get("receipt_ref"),
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    if continuity_context["admission_policy_version"] != CURRENT_POLICY_VERSION:
        failure = build_continuity_failure_receipt(
            target_core=continuity_context["target_core"],
            rejection_code="policy_version_invalid",
            rejection_reason="continuity intake policy version mismatch",
            watcher_receipt_ref=continuity_context["watcher_receipt_ref"],
            output_disposition_ref=continuity_context["output_disposition_ref"],
            runtime_ref=continuity_context["runtime_ref"],
            policy_version=continuity_context["admission_policy_version"],
        )
        update_state(
            current_state,
            intake_id=failure["failure_id"],
            target_core=continuity_context["target_core"],
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            receipt_ref=failure.get("receipt_ref"),
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    findings = watcher_result["findings"]
    decision = _classify_signal(findings)

    if decision.disposition == "accepted":
        receipt = build_continuity_intake_receipt(
            target_core=continuity_context["target_core"],
            continuity_scope=continuity_context["continuity_scope"],
            admission_basis=decision.admission_basis or "continuity_worthy_signal",
            watcher_receipt_ref=continuity_context["watcher_receipt_ref"],
            output_disposition_ref=continuity_context["output_disposition_ref"],
            runtime_ref=continuity_context["runtime_ref"],
            policy_version=continuity_context["admission_policy_version"],
        )
        update_state(
            current_state,
            intake_id=receipt["intake_id"],
            target_core=continuity_context["target_core"],
            disposition="accepted",
            receipt_type=receipt["receipt_type"],
            receipt_ref=receipt.get("receipt_ref"),
            timestamp=receipt["timestamp"],
        )
        return {"status": "accepted", "receipt": receipt, "state": current_state.to_dict()}

    if decision.disposition == "held":
        receipt = build_continuity_hold_receipt(
            target_core=continuity_context["target_core"],
            hold_reason=decision.reason,
            release_condition=decision.hold_release_condition or "human review required",
            watcher_receipt_ref=continuity_context["watcher_receipt_ref"],
            output_disposition_ref=continuity_context["output_disposition_ref"],
            runtime_ref=continuity_context["runtime_ref"],
            policy_version=continuity_context["admission_policy_version"],
            review_window=decision.hold_review_window,
        )
        update_state(
            current_state,
            intake_id=receipt["hold_id"],
            target_core=continuity_context["target_core"],
            disposition="held",
            receipt_type=receipt["receipt_type"],
            receipt_ref=receipt.get("receipt_ref"),
            timestamp=receipt["timestamp"],
        )
        return {"status": "held", "receipt": receipt, "state": current_state.to_dict()}

    receipt = build_continuity_failure_receipt(
        target_core=continuity_context["target_core"],
        rejection_code=decision.rejection_code or "insufficient_signal",
        rejection_reason=decision.reason,
        watcher_receipt_ref=continuity_context["watcher_receipt_ref"],
        output_disposition_ref=continuity_context["output_disposition_ref"],
        runtime_ref=continuity_context["runtime_ref"],
        policy_version=continuity_context["admission_policy_version"],
    )
    update_state(
        current_state,
        intake_id=receipt["failure_id"],
        target_core=continuity_context["target_core"],
        disposition="rejected",
        receipt_type=receipt["receipt_type"],
        receipt_ref=receipt.get("receipt_ref"),
        timestamp=receipt["timestamp"],
    )
    return {"status": "rejected", "receipt": receipt, "state": current_state.to_dict()}