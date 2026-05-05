from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List


CONTROLLED_BEHAVIOR_VERSION = "v1.0"
ARTIFACT_TYPE = "contractor_pm_controlled_behavior_application"
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


def _build_application_id(
    *,
    project_id: str,
    target_service: str,
    refinement_context_hash: str,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = _hash(
        {
            "project_id": project_id,
            "target_service": target_service,
            "refinement_context_hash": refinement_context_hash,
            "ts": ts,
        }
    )[:12]
    safe_project_id = project_id or "unknown_project"
    safe_target = target_service or "unknown_target"
    return f"pm_behavior_{safe_project_id}_{safe_target}_{ts}_{digest}"


def _refinement_payload(refinement_record: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(refinement_record.get("refinement"))


def _refinement_type(refinement_record: Dict[str, Any]) -> str:
    return _clean(_refinement_payload(refinement_record).get("refinement_type"))


def _caution_level(refinement_record: Dict[str, Any]) -> str:
    return _clean(_refinement_payload(refinement_record).get("caution_level"))


def _is_usable_refinement(refinement_record: Dict[str, Any]) -> bool:
    authority = _safe_dict(refinement_record.get("authority"))

    return all(
        [
            refinement_record.get("sealed") is True,
            refinement_record.get("packet_governed") is True,
            authority.get("pm_owned") is True,
            authority.get("context_only") is True,
            authority.get("execution_allowed") is False,
            authority.get("mutation_allowed") is False,
            authority.get("grants_authority") is False,
            authority.get("downstream_service_must_revalidate") is True,
        ]
    )


def _decision_behavior(refinement_record: Dict[str, Any]) -> Dict[str, Any]:
    payload = _refinement_payload(refinement_record)
    fields = _safe_dict(payload.get("fields"))
    caution = _caution_level(refinement_record)

    advisory_flags: List[str] = []
    notes: List[str] = []

    if caution in {"heightened_caution", "context_required"}:
        advisory_flags.append("requires_pm_caution_note")
        notes.append(
            "Decision should preserve PM refinement lineage and avoid overconfident approval language."
        )

    if _refinement_type(refinement_record) == "assumption_uncertainty_refinement":
        advisory_flags.append("unverified_assumption_present")
        notes.append(
            "Decision should reference the unverified assumption before owner-facing reliance."
        )

    if _refinement_type(refinement_record) == "oracle_pressure_refinement":
        advisory_flags.append("external_pressure_context_present")
        notes.append(
            "Decision should reference oracle pressure as context, not as approval authority."
        )

    return {
        "target_service": "decision",
        "behavior_class": "decision_annotation_guidance",
        "advisory_flags": advisory_flags,
        "suggested_note_fragments": notes,
        "suggested_payload_annotations": {
            "pm_behavior_caution_level": caution or "standard_caution",
            "pm_behavior_source": _refinement_type(refinement_record),
            "pm_behavior_fields": fields,
        },
        "may_block": False,
        "may_mutate": False,
        "may_execute": False,
    }


def _risk_behavior(refinement_record: Dict[str, Any]) -> Dict[str, Any]:
    payload = _refinement_payload(refinement_record)
    fields = _safe_dict(payload.get("fields"))
    caution = _caution_level(refinement_record)

    advisory_flags: List[str] = []
    notes: List[str] = []

    if caution in {"heightened_caution", "routing_caution", "context_required"}:
        advisory_flags.append("requires_risk_review_note")
        notes.append(
            "Risk should preserve upstream decision or assumption lineage before severity interpretation."
        )

    if _refinement_type(refinement_record) == "decision_risk_refinement":
        advisory_flags.append("decision_context_present")
        notes.append(
            "Risk should link to the decision where relevant, especially if the decision changes scope, cost, schedule, or compliance exposure."
        )

    if _refinement_type(refinement_record) == "assumption_uncertainty_refinement":
        advisory_flags.append("unverified_assumption_present")
        notes.append(
            "Risk should treat the assumption as uncertainty context, not confirmed fact."
        )

    return {
        "target_service": "risk",
        "behavior_class": "risk_annotation_guidance",
        "advisory_flags": advisory_flags,
        "suggested_note_fragments": notes,
        "suggested_payload_annotations": {
            "pm_behavior_caution_level": caution or "standard_caution",
            "pm_behavior_source": _refinement_type(refinement_record),
            "pm_behavior_fields": fields,
        },
        "may_block": False,
        "may_mutate": False,
        "may_execute": False,
    }


def _router_behavior(refinement_record: Dict[str, Any]) -> Dict[str, Any]:
    payload = _refinement_payload(refinement_record)
    fields = _safe_dict(payload.get("fields"))
    caution = _caution_level(refinement_record)

    advisory_flags: List[str] = []
    notes: List[str] = []

    if caution in {"routing_caution", "heightened_caution"}:
        advisory_flags.append("requires_router_constraint_note")
        notes.append(
            "Router should surface upstream risk or assumption lineage before schedule block commitment."
        )

    if _refinement_type(refinement_record) == "risk_routing_refinement":
        advisory_flags.append("risk_context_present")
        notes.append(
            "Router should preserve risk_id in schedule block notes when relevant."
        )

    if _refinement_type(refinement_record) == "assumption_uncertainty_refinement":
        advisory_flags.append("unverified_assumption_present")
        notes.append(
            "Router should avoid treating unverified assumption as confirmed schedule truth."
        )

    return {
        "target_service": "router",
        "behavior_class": "router_annotation_guidance",
        "advisory_flags": advisory_flags,
        "suggested_note_fragments": notes,
        "suggested_payload_annotations": {
            "pm_behavior_caution_level": caution or "standard_caution",
            "pm_behavior_source": _refinement_type(refinement_record),
            "pm_behavior_fields": fields,
        },
        "may_block": False,
        "may_mutate": False,
        "may_execute": False,
    }


def _generic_behavior(
    refinement_record: Dict[str, Any],
    target_service: str,
) -> Dict[str, Any]:
    payload = _refinement_payload(refinement_record)

    return {
        "target_service": target_service,
        "behavior_class": "generic_annotation_guidance",
        "advisory_flags": ["bounded_pm_context_present"],
        "suggested_note_fragments": [
            "Preserve PM refinement lineage. Treat as context only."
        ],
        "suggested_payload_annotations": {
            "pm_behavior_caution_level": _caution_level(refinement_record)
            or "standard_caution",
            "pm_behavior_source": _refinement_type(refinement_record),
            "pm_behavior_fields": _safe_dict(payload.get("fields")),
        },
        "may_block": False,
        "may_mutate": False,
        "may_execute": False,
    }


def build_behavior_application(
    *,
    refinement_context: Dict[str, Any],
    target_service: str,
    actor: str = ISSUING_LAYER,
) -> Dict[str, Any]:
    normalized_target = _clean(target_service).lower()
    if not normalized_target:
        raise ValueError("target_service_required")

    refinements = _safe_list(refinement_context.get("refinements"))

    usable_refinements = [
        _safe_dict(item)
        for item in refinements
        if _is_usable_refinement(_safe_dict(item))
    ]

    blocked_refinements = [
        _safe_dict(item)
        for item in refinements
        if not _is_usable_refinement(_safe_dict(item))
    ]

    behavior_items: List[Dict[str, Any]] = []

    for record in usable_refinements:
        if normalized_target == "decision":
            behavior_items.append(_decision_behavior(record))
        elif normalized_target == "risk":
            behavior_items.append(_risk_behavior(record))
        elif normalized_target == "router":
            behavior_items.append(_router_behavior(record))
        else:
            behavior_items.append(_generic_behavior(record, normalized_target))

    application = {
        "artifact_type": ARTIFACT_TYPE,
        "artifact_version": CONTROLLED_BEHAVIOR_VERSION,
        "application_id": _build_application_id(
            project_id=_clean(refinement_context.get("project_id")),
            target_service=normalized_target,
            refinement_context_hash=_clean(
                refinement_context.get("refinement_context_hash")
            ),
        ),
        "created_at": _utc_now_iso(),
        "child_core_id": CHILD_CORE_ID,
        "issuing_layer": ISSUING_LAYER,
        "actor": _clean(actor) or ISSUING_LAYER,
        "project_id": refinement_context.get("project_id", ""),
        "phase_id": refinement_context.get("phase_id", ""),
        "target_service": normalized_target,
        "source_refinement_context_hash": refinement_context.get(
            "refinement_context_hash",
            "",
        ),
        "usable_refinement_count": len(usable_refinements),
        "blocked_refinement_count": len(blocked_refinements),
        "behavior_items": behavior_items,
        "authority": {
            "pm_owned": True,
            "advisory_only": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "grants_authority": False,
            "downstream_service_must_revalidate": True,
            "downstream_governance_required": True,
        },
        "constraints": {
            "no_direct_state_mutation": True,
            "no_direct_external_action": True,
            "no_auto_blocking": True,
            "no_auto_execution": True,
            "annotation_only": True,
        },
        "sealed": True,
    }

    application["application_hash"] = _hash(
        {
            key: value
            for key, value in application.items()
            if key != "application_hash"
        }
    )

    return application


def apply_behavior_annotations_to_payload(
    *,
    payload: Dict[str, Any],
    behavior_application: Dict[str, Any],
    note_field: str = "notes_internal",
) -> Dict[str, Any]:
    updated = dict(payload)
    entry_kwargs = dict(updated.get("entry_kwargs", {}))

    behavior_items = _safe_list(behavior_application.get("behavior_items"))

    note_fragments: List[str] = []
    advisory_flags: List[str] = []

    for item in behavior_items:
        item_dict = _safe_dict(item)
        advisory_flags.extend(_safe_list(item_dict.get("advisory_flags")))
        note_fragments.extend(_safe_list(item_dict.get("suggested_note_fragments")))

    existing_note = _clean(entry_kwargs.get(note_field))
    behavior_note = " ".join(fragment for fragment in note_fragments if fragment)

    flag_note = ""
    if advisory_flags:
        flag_note = " PM behavior flags: " + ", ".join(sorted(set(advisory_flags))) + "."

    if behavior_note or flag_note:
        combined_guidance = f"PM behavior guidance: {behavior_note}{flag_note}".strip()

        if existing_note:
            entry_kwargs[note_field] = f"{existing_note} {combined_guidance}"
        else:
            entry_kwargs[note_field] = combined_guidance

    updated["entry_kwargs"] = entry_kwargs

    # Keep this outside schema-bound entry_kwargs.
    updated["pm_behavior_application"] = behavior_application

    return updated