from __future__ import annotations


class RefinementPersistenceRoutingError(Exception):
    """Raised when refinement persistence routing input artifacts are invalid."""


CANDIDATE_PRIORITY = {
    "pattern_note": 1,
    "target_child_core_count": 2,
    "closeout_count": 3,
    "intake_count": 4,
}

ALLOWED_DECISIONS = {
    "approved",
    "deferred",
    "rejected",
}

ALLOWED_PROMOTION_STATUS = {
    "promoted",
    "not_promoted_cap_exceeded",
}

ALLOWED_ROUTE_TARGETS = {
    "refinement_archive",
    "refinement_review_surface",
    "refinement_governance_memory",
}


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise RefinementPersistenceRoutingError(f"{name} must be dict")


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise RefinementPersistenceRoutingError(f"{name} payload must be dict")
    return payload


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise RefinementPersistenceRoutingError(
            f"invalid artifact_type: expected {expected}, got {value.get('artifact_type')}"
        )


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise RefinementPersistenceRoutingError(f"{name} must be sealed")


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise RefinementPersistenceRoutingError(
                f"{name} contains internal field: {key}"
            )


def _validate_promoted_item(item, index, section_name):
    _require_dict(item, f"{section_name}[{index}]")

    required_fields = [
        "candidate_type",
        "candidate_source",
        "candidate_value",
        "selection_reason",
        "score_components",
        "total_score",
        "decision",
        "decision_reason",
        "promotion_status",
        "promotion_reason",
        "lineage_source_artifact_type",
    ]
    for field in required_fields:
        if field not in item:
            raise RefinementPersistenceRoutingError(
                f"{section_name}[{index}] missing required field: {field}"
            )

    if item["candidate_type"] not in CANDIDATE_PRIORITY:
        raise RefinementPersistenceRoutingError(
            f"{section_name}[{index}] invalid candidate_type: {item['candidate_type']}"
        )

    if not isinstance(item["score_components"], list):
        raise RefinementPersistenceRoutingError(
            f"{section_name}[{index}] score_components must be list"
        )

    if not isinstance(item["total_score"], int):
        raise RefinementPersistenceRoutingError(
            f"{section_name}[{index}] total_score must be int"
        )

    if item["decision"] not in ALLOWED_DECISIONS:
        raise RefinementPersistenceRoutingError(
            f"{section_name}[{index}] invalid decision: {item['decision']}"
        )

    if item["promotion_status"] not in ALLOWED_PROMOTION_STATUS:
        raise RefinementPersistenceRoutingError(
            f"{section_name}[{index}] invalid promotion_status: {item['promotion_status']}"
        )

    return item


def _validate_promotion_record(record):
    _require_dict(record, "refinement_promotion_record")
    _require_artifact_type(record, "refinement_promotion_record")
    payload = _require_payload(record, "refinement_promotion_record")
    _reject_internal_fields(payload, "refinement_promotion_record")
    _require_sealed(payload, "refinement_promotion_record")

    required_fields = [
        "issuing_authority",
        "source_artifact_type",
        "promoted_count",
        "overflow_not_promoted_count",
        "deferred_visible_count",
        "rejected_visible_count",
        "promoted",
        "overflow_not_promoted",
        "deferred_visible",
        "rejected_visible",
        "promotion_notes",
    ]
    for field in required_fields:
        if field not in payload:
            raise RefinementPersistenceRoutingError(
                f"refinement_promotion_record missing required field: {field}"
            )

    if not isinstance(payload["promoted"], list):
        raise RefinementPersistenceRoutingError("promoted must be list")
    if not isinstance(payload["overflow_not_promoted"], list):
        raise RefinementPersistenceRoutingError("overflow_not_promoted must be list")
    if not isinstance(payload["deferred_visible"], list):
        raise RefinementPersistenceRoutingError("deferred_visible must be list")
    if not isinstance(payload["rejected_visible"], list):
        raise RefinementPersistenceRoutingError("rejected_visible must be list")
    if not isinstance(payload["promotion_notes"], list):
        raise RefinementPersistenceRoutingError("promotion_notes must be list")

    validated_promoted = [
        _validate_promoted_item(item, index, "promoted")
        for index, item in enumerate(payload["promoted"])
    ]

    return payload, validated_promoted


def _sort_items(items):
    return sorted(
        items,
        key=lambda item: (
            -item["total_score"],
            CANDIDATE_PRIORITY[item["candidate_type"]],
            str(item["candidate_value"]),
        ),
    )


def _build_route_targets(item):
    targets = [
        "refinement_archive",
        "refinement_review_surface",
    ]
    if item["total_score"] >= 5:
        targets.append("refinement_governance_memory")

    for target in targets:
        if target not in ALLOWED_ROUTE_TARGETS:
            raise RefinementPersistenceRoutingError(
                f"invalid route target produced: {target}"
            )
    return targets


def build_refinement_persistence_route_record(refinement_promotion_record):
    payload, promoted = _validate_promotion_record(refinement_promotion_record)

    for index, item in enumerate(promoted):
        if item["decision"] != "approved":
            raise RefinementPersistenceRoutingError(
                f"promoted[{index}] must carry decision='approved'"
            )
        if item["promotion_status"] != "promoted":
            raise RefinementPersistenceRoutingError(
                f"promoted[{index}] must carry promotion_status='promoted'"
            )

    sorted_promoted = _sort_items(promoted)[:3]

    routed_items = []
    for item in sorted_promoted:
        routed_items.append(
            {
                **item,
                "route_status": "routed",
                "route_targets": _build_route_targets(item),
                "routing_reason": "promoted_for_durable_distribution",
                "lineage_source_artifact_type": "refinement_promotion_record",
            }
        )

    routing_notes = []
    if not routed_items:
        routing_notes.append("no_items_routed")

    return {
        "artifact_type": "refinement_persistence_route_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_PERSISTENCE_ROUTING",
            "source_artifact_type": "refinement_promotion_record",
            "routed_count": len(routed_items),
            "visible_overflow_count": payload["overflow_not_promoted_count"],
            "visible_deferred_count": payload["deferred_visible_count"],
            "visible_rejected_count": payload["rejected_visible_count"],
            "routed_items": routed_items,
            "visible_overflow_not_routed": payload["overflow_not_promoted"],
            "visible_deferred_not_routed": payload["deferred_visible"],
            "visible_rejected_not_routed": payload["rejected_visible"],
            "routing_notes": routing_notes,
            "sealed": True,
        },
    }