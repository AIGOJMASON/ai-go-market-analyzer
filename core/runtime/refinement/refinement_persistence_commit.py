from __future__ import annotations


class RefinementPersistenceCommitError(Exception):
    """Raised when refinement persistence commit input artifacts are invalid."""


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

ALLOWED_ROUTE_STATUS = {
    "routed",
}

ALLOWED_ROUTE_TARGETS = {
    "refinement_archive",
    "refinement_review_surface",
    "refinement_governance_memory",
}


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise RefinementPersistenceCommitError(f"{name} must be dict")


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise RefinementPersistenceCommitError(f"{name} payload must be dict")
    return payload


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise RefinementPersistenceCommitError(
            f"invalid artifact_type: expected {expected}, got {value.get('artifact_type')}"
        )


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise RefinementPersistenceCommitError(f"{name} must be sealed")


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise RefinementPersistenceCommitError(
                f"{name} contains internal field: {key}"
            )


def _validate_route_targets(route_targets, name):
    if not isinstance(route_targets, list):
        raise RefinementPersistenceCommitError(f"{name} route_targets must be list")
    for target in route_targets:
        if target not in ALLOWED_ROUTE_TARGETS:
            raise RefinementPersistenceCommitError(
                f"{name} invalid route target: {target}"
            )


def _validate_routed_item(item, index):
    _require_dict(item, f"routed_items[{index}]")

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
        "route_status",
        "route_targets",
        "routing_reason",
        "lineage_source_artifact_type",
    ]
    for field in required_fields:
        if field not in item:
            raise RefinementPersistenceCommitError(
                f"routed_items[{index}] missing required field: {field}"
            )

    if item["candidate_type"] not in CANDIDATE_PRIORITY:
        raise RefinementPersistenceCommitError(
            f"routed_items[{index}] invalid candidate_type: {item['candidate_type']}"
        )

    if not isinstance(item["score_components"], list):
        raise RefinementPersistenceCommitError(
            f"routed_items[{index}] score_components must be list"
        )

    if not isinstance(item["total_score"], int):
        raise RefinementPersistenceCommitError(
            f"routed_items[{index}] total_score must be int"
        )

    if item["decision"] not in ALLOWED_DECISIONS:
        raise RefinementPersistenceCommitError(
            f"routed_items[{index}] invalid decision: {item['decision']}"
        )

    if item["promotion_status"] not in ALLOWED_PROMOTION_STATUS:
        raise RefinementPersistenceCommitError(
            f"routed_items[{index}] invalid promotion_status: {item['promotion_status']}"
        )

    if item["route_status"] not in ALLOWED_ROUTE_STATUS:
        raise RefinementPersistenceCommitError(
            f"routed_items[{index}] invalid route_status: {item['route_status']}"
        )

    _validate_route_targets(item["route_targets"], f"routed_items[{index}]")

    return item


def _validate_route_record(record):
    _require_dict(record, "refinement_persistence_route_record")
    _require_artifact_type(record, "refinement_persistence_route_record")
    payload = _require_payload(record, "refinement_persistence_route_record")
    _reject_internal_fields(payload, "refinement_persistence_route_record")
    _require_sealed(payload, "refinement_persistence_route_record")

    required_fields = [
        "issuing_authority",
        "source_artifact_type",
        "routed_count",
        "visible_overflow_count",
        "visible_deferred_count",
        "visible_rejected_count",
        "routed_items",
        "visible_overflow_not_routed",
        "visible_deferred_not_routed",
        "visible_rejected_not_routed",
        "routing_notes",
    ]
    for field in required_fields:
        if field not in payload:
            raise RefinementPersistenceCommitError(
                f"refinement_persistence_route_record missing required field: {field}"
            )

    if not isinstance(payload["routed_items"], list):
        raise RefinementPersistenceCommitError("routed_items must be list")
    if not isinstance(payload["visible_overflow_not_routed"], list):
        raise RefinementPersistenceCommitError("visible_overflow_not_routed must be list")
    if not isinstance(payload["visible_deferred_not_routed"], list):
        raise RefinementPersistenceCommitError("visible_deferred_not_routed must be list")
    if not isinstance(payload["visible_rejected_not_routed"], list):
        raise RefinementPersistenceCommitError("visible_rejected_not_routed must be list")
    if not isinstance(payload["routing_notes"], list):
        raise RefinementPersistenceCommitError("routing_notes must be list")

    validated_routed_items = [
        _validate_routed_item(item, index)
        for index, item in enumerate(payload["routed_items"])
    ]

    return payload, validated_routed_items


def _sort_items(items):
    return sorted(
        items,
        key=lambda item: (
            -item["total_score"],
            CANDIDATE_PRIORITY[item["candidate_type"]],
            str(item["candidate_value"]),
        ),
    )


def build_refinement_persistence_commit_record(refinement_persistence_route_record):
    payload, routed_items = _validate_route_record(refinement_persistence_route_record)

    for index, item in enumerate(routed_items):
        if item["decision"] != "approved":
            raise RefinementPersistenceCommitError(
                f"routed_items[{index}] must carry decision='approved'"
            )
        if item["promotion_status"] != "promoted":
            raise RefinementPersistenceCommitError(
                f"routed_items[{index}] must carry promotion_status='promoted'"
            )
        if item["route_status"] != "routed":
            raise RefinementPersistenceCommitError(
                f"routed_items[{index}] must carry route_status='routed'"
            )

    sorted_routed_items = _sort_items(routed_items)

    committed_items = []
    for item in sorted_routed_items:
        committed_items.append(
            {
                **item,
                "commit_status": "committed",
                "commit_targets": list(item["route_targets"]),
                "commit_reason": "routed_for_durable_commit",
                "lineage_source_artifact_type": "refinement_persistence_route_record",
            }
        )

    commit_notes = []
    if not committed_items:
        commit_notes.append("no_items_committed")

    return {
        "artifact_type": "refinement_persistence_commit_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_PERSISTENCE_COMMIT",
            "source_artifact_type": "refinement_persistence_route_record",
            "committed_count": len(committed_items),
            "visible_overflow_count": payload["visible_overflow_count"],
            "visible_deferred_count": payload["visible_deferred_count"],
            "visible_rejected_count": payload["visible_rejected_count"],
            "committed_items": committed_items,
            "visible_overflow_not_committed": payload["visible_overflow_not_routed"],
            "visible_deferred_not_committed": payload["visible_deferred_not_routed"],
            "visible_rejected_not_committed": payload["visible_rejected_not_routed"],
            "commit_notes": commit_notes,
            "sealed": True,
        },
    }