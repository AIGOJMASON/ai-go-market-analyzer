"""
Phase closeout gate for contractor_builder_v1 workflow.

This module owns the explicit gate for whether a phase closeout may be sent.

It provides:
- checklist readiness validation
- canonical current phase validation
- phase signoff posture validation
- previous signoff status validation
- blocking unresolved change validation hook

It does NOT:
- persist checklist state
- advance workflow
- record signoff
- generate closeout artifacts
- send email
- replace workflow authority

Division of responsibility:
- checklist_runtime.py -> computes checklist summary
- phase_closeout_gate.py -> decides whether closeout send is allowed
- workflow_runtime.py -> owns workflow state and reconciliation
- client_signoff_status_runtime.py -> owns signoff status records
- contractor_phase_closeout_api.py -> orchestrates PDF/email/send only
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .checklist_schema import PhaseChecklist


_ALLOWED_RESEND_STATUSES: set[str] = {"sent", "declined"}
_BLOCKING_SIGNOFF_STATUSES: set[str] = {"signed"}


@dataclass(frozen=True)
class PhaseCloseoutGateResult:
    allowed: bool
    reason: str
    error: str = ""
    phase_id: str = ""
    current_phase_id: str = ""
    phase_status: str = ""
    signoff_status: str = ""
    workflow_status: str = ""
    checklist_ready: bool = False
    change_blocked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "error": self.error,
            "phase_id": self.phase_id,
            "current_phase_id": self.current_phase_id,
            "phase_status": self.phase_status,
            "signoff_status": self.signoff_status,
            "workflow_status": self.workflow_status,
            "checklist_ready": self.checklist_ready,
            "change_blocked": self.change_blocked,
        }


def is_phase_ready_for_signoff(checklist: PhaseChecklist) -> bool:
    """
    Return True only when the supplied PhaseChecklist is signoff-ready.

    The checklist object itself is the authority for:
    - required_item_count
    - completed_required_count
    - ready_for_signoff
    """
    if not isinstance(checklist, PhaseChecklist):
        raise ValueError("checklist must be a PhaseChecklist")

    return bool(checklist.ready_for_signoff)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _lower(value: Any) -> str:
    return _clean(value).lower()


def evaluate_phase_closeout_gate(
    *,
    phase_id: str,
    workflow_state: Dict[str, Any],
    phase_instance: Dict[str, Any],
    checklist: Optional[PhaseChecklist],
    latest_signoff_status: Optional[Dict[str, Any]] = None,
    change_closeout_guard: Optional[Dict[str, Any]] = None,
    allow_resend_if_sent: bool = True,
) -> PhaseCloseoutGateResult:
    """
    Evaluate whether a phase closeout may be sent.

    This function is pure validation:
    - no file writes
    - no workflow transition
    - no signoff mutation
    - no receipt creation
    """
    requested_phase_id = _clean(phase_id)
    current_phase_id = _clean(workflow_state.get("current_phase_id"))
    workflow_status = _clean(workflow_state.get("workflow_status"))
    phase_status = _clean(phase_instance.get("phase_status"))

    signoff_status = ""
    if isinstance(latest_signoff_status, dict):
        signoff_status = _lower(latest_signoff_status.get("status"))

    change_blocked = False
    if isinstance(change_closeout_guard, dict):
        change_blocked = bool(
            change_closeout_guard.get("phase_has_blocking_unresolved_changes", False)
        )

    checklist_ready = False
    if checklist is not None:
        checklist_ready = is_phase_ready_for_signoff(checklist)

    base = {
        "phase_id": requested_phase_id,
        "current_phase_id": current_phase_id,
        "phase_status": phase_status,
        "signoff_status": signoff_status,
        "workflow_status": workflow_status,
        "checklist_ready": checklist_ready,
        "change_blocked": change_blocked,
    }

    if not requested_phase_id:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="phase_id is required",
            error="missing_phase_id",
            **base,
        )

    if not current_phase_id:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="Workflow has no canonical current_phase_id.",
            error="missing_current_phase_id",
            **base,
        )

    if current_phase_id != requested_phase_id:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="Phase closeout may only run for the canonical current workflow phase.",
            error="phase_id_not_canonical_current_phase",
            **base,
        )

    if phase_status != "awaiting_signoff":
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="Phase closeout may only run when workflow has placed the phase into awaiting_signoff.",
            error="phase_not_in_signoff_posture",
            **base,
        )

    if checklist is None:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="Checklist is required before phase closeout.",
            error="missing_checklist",
            **base,
        )

    if not checklist_ready:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="Checklist is not ready for signoff.",
            error="checklist_not_ready_for_signoff",
            **base,
        )

    if change_blocked:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="Blocking unresolved customer-impacting changes exist for this phase.",
            error="blocking_unresolved_change_exists",
            **base,
        )

    if signoff_status in _BLOCKING_SIGNOFF_STATUSES:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="A signed phase may not be resent for signoff.",
            error="phase_already_signed",
            **base,
        )

    if signoff_status == "sent" and not allow_resend_if_sent:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="A signoff request has already been sent for this phase.",
            error="phase_closeout_already_sent",
            **base,
        )

    if signoff_status and signoff_status not in _ALLOWED_RESEND_STATUSES:
        return PhaseCloseoutGateResult(
            allowed=False,
            reason="Current signoff posture does not allow closeout send.",
            error="signoff_status_not_sendable",
            **base,
        )

    return PhaseCloseoutGateResult(
        allowed=True,
        reason="Phase closeout send is allowed.",
        **base,
    )


def require_phase_closeout_allowed(
    *,
    phase_id: str,
    workflow_state: Dict[str, Any],
    phase_instance: Dict[str, Any],
    checklist: Optional[PhaseChecklist],
    latest_signoff_status: Optional[Dict[str, Any]] = None,
    change_closeout_guard: Optional[Dict[str, Any]] = None,
    allow_resend_if_sent: bool = True,
) -> PhaseCloseoutGateResult:
    """
    Return gate result if allowed, otherwise raise ValueError with the gate error.

    API layers may convert this ValueError into HTTP 409.
    """
    result = evaluate_phase_closeout_gate(
        phase_id=phase_id,
        workflow_state=workflow_state,
        phase_instance=phase_instance,
        checklist=checklist,
        latest_signoff_status=latest_signoff_status,
        change_closeout_guard=change_closeout_guard,
        allow_resend_if_sent=allow_resend_if_sent,
    )

    if not result.allowed:
        raise ValueError(result.error or result.reason)

    return result