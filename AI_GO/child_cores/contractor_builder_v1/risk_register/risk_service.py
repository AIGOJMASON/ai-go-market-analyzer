from __future__ import annotations

from typing import Any, Dict, List

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_packet_builder import (
    build_pm_coupling_packet,
    extract_target_context,
)
from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_executor import (
    execute_create_risk,
    execute_review_risk,
    execute_transition_risk,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.result_summary import build_result_summary
from AI_GO.core.watcher.cross_core_enforcement import enforce_cross_core_chain


PROFILE = "contractor_risk"
TARGET_SERVICE = "risk"
DOWNSTREAM_TARGET_SERVICE = "router"


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
        or _clean(entry.get("phase_id"))
        or _clean(context_lock.get("phase_id"))
    )


def _risk_id_from_payload(payload: Dict[str, Any]) -> str:
    entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
    entry = _safe_dict(payload.get("entry"))

    return (
        _clean(payload.get("risk_id"))
        or _clean(entry_kwargs.get("risk_id"))
        or _clean(entry.get("risk_id"))
    )


def _route_for_action(action: str) -> str:
    if action == "risk_create":
        return "/contractor-builder/risk/create"
    if action == "risk_review":
        return "/contractor-builder/risk/review"
    if action == "risk_transition":
        return "/contractor-builder/risk/transition"
    return "/contractor-builder/risk"


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


def _extract_risk_target_context(coupling_context: Dict[str, Any]) -> Dict[str, Any]:
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
                "error": "risk_cross_core_coupling_blocked",
                "message": "Risk service refused to continue because inbound PM coupling failed enforcement.",
                "cross_core_decision": decision,
            },
        )

    return decision


def _decision_influence_summary(target_coupling_context: Dict[str, Any]) -> Dict[str, Any]:
    packets = _safe_list(target_coupling_context.get("packets"))
    decision_packets = []

    for packet in packets:
        source = _safe_dict(packet.get("source"))
        if _clean(source.get("source_type")).lower() == "decision":
            decision_packets.append(packet)

    return {
        "source_service": "decision",
        "target_service": TARGET_SERVICE,
        "decision_packet_count": len(decision_packets),
        "influence_present": bool(decision_packets),
        "influence_summaries": [
            _clean(_safe_dict(packet.get("influence")).get("summary"))
            for packet in decision_packets
            if _clean(_safe_dict(packet.get("influence")).get("summary"))
        ],
        "source_ids": [
            _clean(_safe_dict(packet.get("source")).get("source_id"))
            for packet in decision_packets
            if _clean(_safe_dict(packet.get("source")).get("source_id"))
        ],
        "authority": {
            "context_only": True,
            "may_inform_risk": True,
            "may_execute_risk": False,
            "may_mutate_risk_without_gate": False,
        },
    }


def _build_state(
    *,
    profile: str,
    action: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    project_id = _project_id_from_payload(payload)
    phase_id = _phase_id_from_payload(payload)
    risk_id = _risk_id_from_payload(payload)

    errors: List[str] = []
    checks: Dict[str, Any] = {
        "project_id_present": bool(project_id),
        "action_present": bool(action),
        "profile_present": bool(profile),
        "state_mutation_declared": True,
    }

    if not project_id:
        errors.append("project_id_missing")

    if action in {"risk_review", "risk_transition"}:
        checks["risk_id_present"] = bool(risk_id)
        if not risk_id:
            errors.append("risk_id_missing")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": profile,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "allowed": valid,
        "project_id": project_id,
        "phase_id": phase_id,
        "risk_id": risk_id,
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

    decision_influence = _decision_influence_summary(target_coupling_context)

    checks: Dict[str, Any] = {
        "state_valid": state.get("valid") is True,
        "mutation_declared": True,
        "execution_required": True,
        "coupling_context_bounded": True,
        "cross_core_enforcement_allowed": cross_core_decision.get("allowed") is True,
        "risk_target_context_only": (
            _safe_dict(target_coupling_context.get("authority")).get("execution_allowed") is False
            and _safe_dict(target_coupling_context.get("authority")).get("mutation_allowed") is False
        ),
        "decision_influence_context_safe": (
            decision_influence["authority"]["may_inform_risk"] is True
            and decision_influence["authority"]["may_execute_risk"] is False
        ),
    }

    if state.get("valid") is not True:
        errors.append("state_validation_failed")

    if cross_core_decision.get("allowed") is not True:
        errors.append("cross_core_enforcement_blocked")

    if checks["risk_target_context_only"] is not True:
        errors.append("risk_target_context_authority_invalid")

    if action == "risk_create":
        entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
        checks["entry_kwargs_present"] = bool(entry_kwargs)
        if not entry_kwargs:
            errors.append("entry_kwargs_missing")

    if action == "risk_review":
        reviewer_name = _clean(payload.get("reviewer_name"))
        reviewer_role = _clean(payload.get("reviewer_role"))
        checks["reviewer_name_present"] = bool(reviewer_name)
        checks["reviewer_role_present"] = bool(reviewer_role)
        if not reviewer_name:
            errors.append("reviewer_name_missing")
        if not reviewer_role:
            errors.append("reviewer_role_missing")

    if action == "risk_transition":
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
        "risk_id": state.get("risk_id", ""),
        "checks": checks,
        "errors": errors,
        "coupling": {
            "target_service": TARGET_SERVICE,
            "target_packet_count": target_coupling_context.get("packet_count", 0),
            "cross_core_status": cross_core_decision.get("status"),
            "cross_core_decision": cross_core_decision.get("decision"),
            "decision_influence": decision_influence,
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
    actor = _clean(payload.get("actor")) or "contractor_risk_service"

    coupling_context = _coupling_context_from_payload(payload)
    target_coupling_context = _extract_risk_target_context(coupling_context)
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

    request = {
        "actor": actor,
        "project_id": state.get("project_id", ""),
        "phase_id": state.get("phase_id", ""),
        "risk_id": state.get("risk_id", ""),
        "action": action,
        "action_type": action,
        "action_class": "write_state",
        "target": PROFILE,
        "child_core_id": "contractor_builder_v1",
        "state_mutation_declared": True,
        "mutation_declared": True,
        "receipt_planned": True,
        "operator_approved": True,
        "approval_granted": True,
        "watcher_passed": watcher.get("valid") is True,
        "state_passed": state.get("valid") is True,
        "watcher_result": watcher,
        "state_decision": state,
        "state": state,
        "bounded_context": True,
        "declared_intent": "governed contractor risk state mutation",
        "context": {
            "coupling_context": coupling_context,
            "target_coupling_context": target_coupling_context,
            "cross_core_decision": cross_core_decision,
        },
    }

    context = build_governed_context(
        profile=PROFILE,
        action=action,
        route=_route_for_action(action),
        request=request,
        state=state,
        watcher=watcher,
    )

    context["coupling"] = {
        "inbound_context_present": _has_coupling_packets(coupling_context),
        "target_context": target_coupling_context,
        "cross_core_decision": cross_core_decision,
        "consumed_as": TARGET_SERVICE,
        "decision_influence": _decision_influence_summary(target_coupling_context),
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
                "error": "risk_state_validation_failed",
                "context": context,
            },
        )

    if watcher.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "risk_watcher_validation_failed",
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
    project_id = _clean(_safe_dict(context.get("state")).get("project_id"))
    phase_id = _clean(_safe_dict(context.get("state")).get("phase_id"))
    actor = _clean(_safe_dict(context.get("request")).get("actor")) or "contractor_risk_service"

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
            "Risk output must inform downstream router posture. "
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


def create_risk(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="risk_create", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_create_risk(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="risk_create", context=context, result=result)


def review_risk(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="risk_review", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_review_risk(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="risk_review", context=context, result=result)


def transition_risk(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="risk_transition", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_transition_risk(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="risk_transition", context=context, result=result)