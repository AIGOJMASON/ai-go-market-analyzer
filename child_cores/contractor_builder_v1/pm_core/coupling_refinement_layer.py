from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List


REFINEMENT_LAYER_VERSION = "v1.0"
ARTIFACT_TYPE = "contractor_pm_coupling_refinement"
CHILD_CORE_ID = "contractor_builder_v1"
ISSUING_LAYER = "PM_CORE"


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


def _packet_source_type(packet: Dict[str, Any]) -> str:
    return _clean(_safe_dict(packet.get("source")).get("source_type")).lower()


def _packet_target_service(packet: Dict[str, Any]) -> str:
    return _clean(_safe_dict(packet.get("target")).get("target_service")).lower()


def _packet_influence_type(packet: Dict[str, Any]) -> str:
    return _clean(_safe_dict(packet.get("influence")).get("influence_type")).lower()


def _packet_governance_refs(packet: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(packet.get("source"))
    return _safe_dict(source.get("governance_refs"))


def _packet_authority(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("authority"))


def _packet_constraints(packet: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(packet.get("constraints"))


def _is_governed_packet(packet: Dict[str, Any]) -> bool:
    refs = _packet_governance_refs(packet)
    authority = _packet_authority(packet)
    constraints = _packet_constraints(packet)

    return all(
        [
            bool(packet.get("sealed") is True),
            bool(refs.get("watcher_valid") is True),
            bool(refs.get("state_valid") is True),
            bool(refs.get("execution_gate_allowed") is True),
            bool(refs.get("result_effect") == "execution_completed"),
            bool(authority.get("pm_owned") is True),
            bool(authority.get("downstream_execution_allowed") is False),
            bool(authority.get("downstream_mutation_allowed") is False),
            bool(authority.get("grants_authority") is False),
            bool(authority.get("requires_downstream_governance") is True),
            bool(authority.get("requires_downstream_watcher") is True),
            bool(authority.get("requires_downstream_execution_gate") is True),
            bool(constraints.get("no_lateral_service_call") is True),
            bool(constraints.get("no_direct_state_mutation") is True),
            bool(constraints.get("packet_remains_context_not_truth") is True),
        ]
    )


def _refine_assumption(packet: Dict[str, Any]) -> Dict[str, Any]:
    influence = _safe_dict(packet.get("influence"))
    assumption_context = _safe_dict(influence.get("assumption_context"))
    validation_status = _clean(assumption_context.get("validation_status"))

    caution = "standard_caution"
    if validation_status.lower() in {"unverified", "unknown", ""}:
        caution = "heightened_caution"

    return {
        "refinement_type": "assumption_uncertainty_refinement",
        "signal": "assumption_context_present",
        "caution_level": caution,
        "application_mode": "annotate_and_require_lineage",
        "recommended_application": [
            "preserve assumption lineage in downstream artifact notes",
            "avoid overconfident downstream interpretation",
            "do not auto-block unless watcher policy later requires escalation",
        ],
        "fields": {
            "assumption_id": assumption_context.get("assumption_id"),
            "validation_status": validation_status or "unknown",
            "impact_if_false": assumption_context.get("impact_if_false"),
        },
    }


def _refine_oracle_to_decision(packet: Dict[str, Any]) -> Dict[str, Any]:
    influence = _safe_dict(packet.get("influence"))
    decision_context = _safe_dict(influence.get("decision_context"))

    return {
        "refinement_type": "oracle_pressure_refinement",
        "signal": "oracle_context_present",
        "caution_level": "context_required",
        "application_mode": "attach_external_pressure_context",
        "recommended_application": [
            "include oracle lineage in decision notes",
            "review cost, schedule, procurement, or compliance exposure",
            "do not approve solely from oracle pressure",
        ],
        "fields": decision_context,
    }


def _refine_decision_to_risk(packet: Dict[str, Any]) -> Dict[str, Any]:
    influence = _safe_dict(packet.get("influence"))
    risk_context = _safe_dict(influence.get("risk_context"))

    decision_status = _clean(risk_context.get("decision_status")).lower()
    caution = "standard_caution"
    if decision_status in {"draft", "pending", "unknown", ""}:
        caution = "heightened_caution"

    return {
        "refinement_type": "decision_risk_refinement",
        "signal": "decision_context_present",
        "caution_level": caution,
        "application_mode": "link_decision_to_risk_context",
        "recommended_application": [
            "link risk to decision_id when relevant",
            "review whether decision changes scope, cost, schedule, compliance, or owner exposure",
            "do not treat draft decisions as final approval authority",
        ],
        "fields": risk_context,
    }


def _refine_risk_to_router(packet: Dict[str, Any]) -> Dict[str, Any]:
    influence = _safe_dict(packet.get("influence"))
    router_context = _safe_dict(influence.get("router_context"))

    probability = _clean(router_context.get("probability")).lower()
    risk_status = _clean(router_context.get("risk_status")).lower()

    caution = "standard_caution"
    if probability in {"high", "moderate"} and risk_status in {"open", "active", ""}:
        caution = "routing_caution"

    return {
        "refinement_type": "risk_routing_refinement",
        "signal": "risk_context_present",
        "caution_level": caution,
        "application_mode": "surface_routing_constraint",
        "recommended_application": [
            "surface risk lineage before committing route or schedule block",
            "preserve risk_id in router notes when relevant",
            "do not change schedule automatically without router governance",
        ],
        "fields": router_context,
    }


def _refine_generic(packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "refinement_type": "generic_context_refinement",
        "signal": "bounded_pm_context_present",
        "caution_level": "standard_caution",
        "application_mode": "annotation_only",
        "recommended_application": [
            "preserve packet lineage",
            "use as context only",
            "do not mutate downstream state directly",
        ],
        "fields": {},
    }


def refine_coupling_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    source_type = _packet_source_type(packet)
    target_service = _packet_target_service(packet)
    influence_type = _packet_influence_type(packet)
    governed = _is_governed_packet(packet)

    if not governed:
        refinement = {
            "refinement_type": "blocked_refinement",
            "signal": "invalid_or_ungoverned_packet",
            "caution_level": "blocked",
            "application_mode": "do_not_apply",
            "recommended_application": [
                "reject packet influence",
                "require valid PM coupling packet",
                "do not pass to downstream service",
            ],
            "fields": {},
        }
    elif source_type == "assumption":
        refinement = _refine_assumption(packet)
    elif influence_type == "oracle_to_decision":
        refinement = _refine_oracle_to_decision(packet)
    elif influence_type == "decision_to_risk":
        refinement = _refine_decision_to_risk(packet)
    elif influence_type == "risk_to_router":
        refinement = _refine_risk_to_router(packet)
    else:
        refinement = _refine_generic(packet)

    return {
        "artifact_type": ARTIFACT_TYPE,
        "artifact_version": REFINEMENT_LAYER_VERSION,
        "created_at": _utc_now_iso(),
        "child_core_id": CHILD_CORE_ID,
        "issuing_layer": ISSUING_LAYER,
        "source_type": source_type,
        "target_service": target_service,
        "influence_type": influence_type,
        "packet_id": packet.get("packet_id", ""),
        "packet_hash": packet.get("packet_hash", ""),
        "packet_governed": governed,
        "refinement": refinement,
        "authority": {
            "pm_owned": True,
            "context_only": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "grants_authority": False,
            "downstream_service_must_revalidate": True,
        },
        "sealed": True,
    }


def build_coupling_refinement_context(
    *,
    coupling_context: Dict[str, Any],
    target_service: str = "",
    actor: str = ISSUING_LAYER,
) -> Dict[str, Any]:
    packets = _safe_list(coupling_context.get("packets"))

    if target_service:
        normalized_target = _clean(target_service).lower()
        packets = [
            packet for packet in packets
            if _packet_target_service(_safe_dict(packet)) == normalized_target
        ]

    refinements = [
        refine_coupling_packet(_safe_dict(packet))
        for packet in packets
    ]

    blocked_count = sum(
        1 for item in refinements
        if _safe_dict(item.get("refinement")).get("application_mode") == "do_not_apply"
    )

    context = {
        "artifact_type": "contractor_pm_coupling_refinement_context",
        "artifact_version": REFINEMENT_LAYER_VERSION,
        "created_at": _utc_now_iso(),
        "child_core_id": CHILD_CORE_ID,
        "issuing_layer": ISSUING_LAYER,
        "actor": _clean(actor) or ISSUING_LAYER,
        "project_id": coupling_context.get("project_id", ""),
        "phase_id": coupling_context.get("phase_id", ""),
        "target_service": _clean(target_service).lower(),
        "source_context_hash": coupling_context.get("context_hash", ""),
        "packet_count": len(packets),
        "refinement_count": len(refinements),
        "blocked_count": blocked_count,
        "refinements": refinements,
        "authority": {
            "pm_owned": True,
            "context_only": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "grants_authority": False,
            "downstream_services_must_revalidate": True,
        },
        "sealed": True,
    }

    context["refinement_context_hash"] = _hash(
        {
            key: value
            for key, value in context.items()
            if key != "refinement_context_hash"
        }
    )

    return context


def attach_refinement_to_payload(
    *,
    payload: Dict[str, Any],
    refinement_context: Dict[str, Any],
) -> Dict[str, Any]:
    updated = dict(payload)
    updated["pm_refinement_context"] = refinement_context
    return updated