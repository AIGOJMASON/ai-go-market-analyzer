from __future__ import annotations

from typing import Any, Dict, List

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_executor import (
    execute_create_decision,
    execute_sign_decision,
    execute_transition_decision,
)
from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_packet_builder import (
    build_pm_coupling_packet,
    extract_target_context,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.result_summary import build_result_summary
from AI_GO.core.watcher.cross_core_enforcement import enforce_cross_core_chain


PROFILE = "contractor_decision"
TARGET_SERVICE = "decision"
DOWNSTREAM_TARGET_SERVICE = "risk"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _project_id_from_payload(payload: Dict[str, Any]) -> str:
    entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
    entry = _safe_dict(payload.get("entry"))

    return (
        _clean(payload.get("project_id"))
        or _clean(entry_kwargs.get("project_id"))
        or _clean(entry.get("project_id"))
    )


def _phase_id_from_payload(payload: Dict[str, Any]) -> str:
    entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
    entry = _safe_dict(payload.get("entry"))
    context_lock = _safe_dict(entry.get("context_lock"))

    return (
        _clean(payload.get("phase_id"))
        or _clean(entry_kwargs.get("phase_id"))
        or _clean(context_lock.get("phase_id"))
    )


def _decision_id_from_payload(payload: Dict[str, Any]) -> str:
    entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
    entry = _safe_dict(payload.get("entry"))

    return (
        _clean(payload.get("decision_id"))
        or _clean(entry_kwargs.get("decision_id"))
        or _clean(entry.get("decision_id"))
    )


def _route_for_action(action: str) -> str:
    if action == "decision_create":
        return "/contractor-builder/decision/create"
    if action == "decision_sign":
        return "/contractor-builder/decision/sign"
    if action == "decision_transition":
        return "/contractor-builder/decision/transition"
    return "/contractor-builder/decision"


def _coupling_context_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    direct = _safe_dict(payload.get("coupling_context"))
    if direct:
        return direct

    pm_context = _safe_dict(payload.get("pm_coupling_context"))
    if pm_context:
        return pm_context

    context = _safe_dict(payload.get("context"))
    nested = _safe_dict(context.get("coupling_context"))
    if nested:
        return nested

    return {}


def _has_coupling_packets(coupling_context: Dict[str, Any]) -> bool:
    return bool(_safe_list(coupling_context.get("packets")))


def _extract_decision_target_context(coupling_context: Dict[str, Any]) -> Dict[str, Any]:
    if not _has_coupling_packets(coupling_context):
        return {
            "artifact_type": "contractor_pm_target_coupling_context",
            "target_service": TARGET_SERVICE,
            "packet_count": 0,
            "packets": [],
            "authority": {
                "context_only": True,
                "execution_allowed": False,
                "mutation_allowed": False,
                "downstream_service_must_revalidate": True,
            },
            "sealed": True,
        }

    return extract_target_context(
        coupling_context=coupling_context,
        target_service=TARGET_SERVICE,
    )


def _enforce_inbound_coupling(
    *,
    action: str,
    coupling_context: Dict[str, Any],
    actor: str,
) -> Dict[str, Any]:
    if not _has_coupling_packets(coupling_context):
        return {
            "artifact_type": "cross_core_enforcement_decision",
            "artifact_version": "v6c.1",
            "profile": PROFILE,
            "action": action,
            "actor": actor,
            "status": "not_required",
            "decision": "allow",
            "allowed": True,
            "blocked": False,
            "reason": "no_coupling_context_supplied",
            "authority": {
                "cross_core_gate": True,
                "may_block_propagation": True,
                "may_execute": False,
                "may_mutate_state": False,
            },
            "sealed": True,
        }

    decision = enforce_cross_core_chain(
        payload=coupling_context,
        action=action,
        profile="contractor_builder_v1",
        actor=actor,
    )

    if decision.get("allowed") is not True:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "decision_cross_core_coupling_blocked",
                "message": "Decision service refused to continue because inbound PM coupling failed enforcement.",
                "cross_core_decision": decision,
            },
        )

    return decision


def _build_state(
    *,
    profile: str,
    action: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    project_id = _project_id_from_payload(payload)
    decision_id = _decision_id_from_payload(payload)
    phase_id = _phase_id_from_payload(payload)

    errors: List[str] = []
    checks: Dict[str, Any] = {
        "project_id_present": bool(project_id),
        "action_present": bool(action),
        "profile_present": bool(profile),
        "state_mutation_declared": True,
    }

    if not project_id:
        errors.append("project_id_missing")

    if action in {"decision_sign", "decision_transition"}:
        checks["decision_id_present"] = bool(decision_id)
        if not decision_id:
            errors.append("decision_id_missing")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": profile,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "allowed": valid,
        "project_id": project_id,
        "phase_id": phase_id,
        "decision_id": decision_id,
        "checks": checks,
        "errors": errors,
        "read_only": False,
        "mutation_allowed": True,
        "sealed": True,
    }


def _build_watcher(
    *,
    profile: str,
    action: str,
    state: Dict[str, Any],
    payload: Dict[str, Any],
    target_coupling_context: Dict[str, Any],
    cross_core_decision: Dict[str, Any],
) -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, Any] = {
        "state_valid": bool(state.get("valid") is True),
        "mutation_declared": True,
        "execution_required": True,
        "coupling_context_bounded": True,
        "cross_core_enforcement_allowed": cross_core_decision.get("allowed") is True,
        "decision_target_context_only": (
            _safe_dict(target_coupling_context.get("authority")).get("execution_allowed") is False
            and _safe_dict(target_coupling_context.get("authority")).get("mutation_allowed") is False
        ),
    }

    if state.get("valid") is not True:
        errors.append("state_validation_failed")

    if cross_core_decision.get("allowed") is not True:
        errors.append("cross_core_enforcement_blocked")

    if checks["decision_target_context_only"] is not True:
        errors.append("decision_target_context_authority_invalid")

    if action == "decision_create":
        entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
        checks["entry_kwargs_present"] = bool(entry_kwargs)
        if not entry_kwargs:
            errors.append("entry_kwargs_missing")

    if action == "decision_sign":
        signer_type = _clean(payload.get("signer_type"))
        checks["valid_signer_type"] = signer_type in {"requester", "approver"}
        if signer_type not in {"requester", "approver"}:
            errors.append("invalid_signer_type")

    if action == "decision_transition":
        new_status = _clean(payload.get("new_status"))
        checks["new_status_present"] = bool(new_status)
        if not new_status:
            errors.append("new_status_missing")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": profile,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": state.get("project_id", ""),
        "phase_id": state.get("phase_id", ""),
        "decision_id": state.get("decision_id", ""),
        "checks": checks,
        "errors": errors,
        "coupling": {
            "target_service": TARGET_SERVICE,
            "target_packet_count": target_coupling_context.get("packet_count", 0),
            "cross_core_status": cross_core_decision.get("status"),
            "cross_core_decision": cross_core_decision.get("decision"),
        },
        "policy": {
            "read_only": False,
            "mutation_allowed": True,
            "execution_allowed": False,
            "requires_execution_gate": True,
            "requires_cross_core_enforcement_when_context_supplied": True,
        },
        "sealed": True,
    }


def _govern(
    *,
    action: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    actor = _clean(payload.get("actor")) or "contractor_decision_service"

    coupling_context = _coupling_context_from_payload(payload)
    target_coupling_context = _extract_decision_target_context(coupling_context)
    cross_core_decision = _enforce_inbound_coupling(
        action=action,
        coupling_context=coupling_context,
        actor=actor,
    )

    state = _build_state(profile=PROFILE, action=action, payload=payload)
    watcher = _build_watcher(
        profile=PROFILE,
        action=action,
        state=state,
        payload=payload,
        target_coupling_context=target_coupling_context,
        cross_core_decision=cross_core_decision,
    )

    context = build_governed_context(
        profile=PROFILE,
        action=action,
        route=_route_for_action(action),
        request={
            "actor": actor,
            "project_id": state.get("project_id", ""),
            "phase_id": state.get("phase_id", ""),
            "decision_id": state.get("decision_id", ""),
            "action": action,
        },
        state=state,
        watcher=watcher,
    )

    context["coupling"] = {
        "inbound_context_present": _has_coupling_packets(coupling_context),
        "target_context": target_coupling_context,
        "cross_core_decision": cross_core_decision,
        "consumed_as": TARGET_SERVICE,
        "authority": {
            "context_only": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "downstream_revalidation_required": True,
        },
    }

    if state.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "decision_state_validation_failed",
                "context": context,
            },
        )

    if watcher.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "decision_watcher_validation_failed",
                "context": context,
            },
        )

    return context


def _build_downstream_packet(
    *,
    action: str,
    context: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
    project_id = _clean(context.get("state", {}).get("project_id"))
    phase_id = _clean(context.get("state", {}).get("phase_id"))
    actor = _clean(context.get("request", {}).get("actor")) or "contractor_decision_service"

    if not project_id:
        return {
            "status": "not_created",
            "reason": "project_id_missing",
        }

    source_result = {
        "mode": "governed_execution",
        **context,
        **result,
    }

    return build_pm_coupling_packet(
        project_id=project_id,
        phase_id=phase_id,
        actor=actor,
        source_service=TARGET_SERVICE,
        target_service=DOWNSTREAM_TARGET_SERVICE,
        source_result=source_result,
        influence_summary=(
            "Decision output must inform downstream risk posture. "
            "This packet is context influence only and grants no execution authority."
        ),
    )


def _finish(
    *,
    action: str,
    context: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
    downstream_packet = _build_downstream_packet(
        action=action,
        context=context,
        result=result,
    )

    enriched_result = {
        **result,
        "pm_coupling_output": {
            "source_service": TARGET_SERVICE,
            "target_service": DOWNSTREAM_TARGET_SERVICE,
            "packet": downstream_packet,
            "authority": {
                "context_only": True,
                "execution_allowed": False,
                "mutation_allowed": False,
                "target_must_revalidate": True,
            },
        },
    }

    result_summary = build_result_summary(
        action=action,
        result=enriched_result,
        context=context,
    )

    return {
        "mode": "governed_execution",
        **context,
        **enriched_result,
        "result_summary": result_summary,
    }


def create_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="decision_create", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_create_decision(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="decision_create", context=context, result=result)


def sign_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="decision_sign", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_sign_decision(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="decision_sign", context=context, result=result)


def transition_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="decision_transition", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_transition_decision(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="decision_transition", context=context, result=result)