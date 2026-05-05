from __future__ import annotations


class RefinementConsumerInterfaceError(Exception):
    """Raised when refinement consumer interface input artifacts are invalid."""


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

ALLOWED_COMMIT_STATUS = {
    "committed",
}

ALLOWED_ROUTE_TARGETS = {
    "refinement_archive",
    "refinement_review_surface",
    "refinement_governance_memory",
}


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise RefinementConsumerInterfaceError(f"{name} must be dict")


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise RefinementConsumerInterfaceError(f"{name} payload must be dict")
    return payload


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise RefinementConsumerInterfaceError(
            f"invalid artifact_type: expected {expected}, got {value.get('artifact_type')}"
        )


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise RefinementConsumerInterfaceError(f"{name} must be sealed")


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise RefinementConsumerInterfaceError(
                f"{name} contains internal field: {key}"
            )


def _validate_route_targets(route_targets, name):
    if not isinstance(route_targets, list):
        raise RefinementConsumerInterfaceError(f"{name} route_targets must be list")
    for target in route_targets:
        if target not in ALLOWED_ROUTE_TARGETS:
            raise RefinementConsumerInterfaceError(
                f"{name} invalid route target: {target}"
            )


def _validate_committed_item(item, index):
    _require_dict(item, f"committed_items[{index}]")

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
        "commit_status",
        "commit_targets",
        "commit_reason",
        "lineage_source_artifact_type",
    ]
    for field in required_fields:
        if field not in item:
            raise RefinementConsumerInterfaceError(
                f"committed_items[{index}] missing required field: {field}"
            )

    if item["candidate_type"] not in CANDIDATE_PRIORITY:
        raise RefinementConsumerInterfaceError(
            f"committed_items[{index}] invalid candidate_type: {item['candidate_type']}"
        )

    if not isinstance(item["score_components"], list):
        raise RefinementConsumerInterfaceError(
            f"committed_items[{index}] score_components must be list"
        )

    if not isinstance(item["total_score"], int):
        raise RefinementConsumerInterfaceError(
            f"committed_items[{index}] total_score must be int"
        )

    if item["decision"] not in ALLOWED_DECISIONS:
        raise RefinementConsumerInterfaceError(
            f"committed_items[{index}] invalid decision: {item['decision']}"
        )

    if item["promotion_status"] not in ALLOWED_PROMOTION_STATUS:
        raise RefinementConsumerInterfaceError(
            f"committed_items[{index}] invalid promotion_status: {item['promotion_status']}"
        )

    if item["route_status"] not in ALLOWED_ROUTE_STATUS:
        raise RefinementConsumerInterfaceError(
            f"committed_items[{index}] invalid route_status: {item['route_status']}"
        )

    if item["commit_status"] not in ALLOWED_COMMIT_STATUS:
        raise RefinementConsumerInterfaceError(
            f"committed_items[{index}] invalid commit_status: {item['commit_status']}"
        )

    _validate_route_targets(item["route_targets"], f"committed_items[{index}]")
    _validate_route_targets(item["commit_targets"], f"committed_items[{index}]")

    return item


def _validate_commit_record(record):
    _require_dict(record, "refinement_persistence_commit_record")
    _require_artifact_type(record, "refinement_persistence_commit_record")
    payload = _require_payload(record, "refinement_persistence_commit_record")
    _reject_internal_fields(payload, "refinement_persistence_commit_record")
    _require_sealed(payload, "refinement_persistence_commit_record")

    required_fields = [
        "issuing_authority",
        "source_artifact_type",
        "committed_count",
        "visible_overflow_count",
        "visible_deferred_count",
        "visible_rejected_count",
        "committed_items",
        "visible_overflow_not_committed",
        "visible_deferred_not_committed",
        "visible_rejected_not_committed",
        "commit_notes",
    ]
    for field in required_fields:
        if field not in payload:
            raise RefinementConsumerInterfaceError(
                f"refinement_persistence_commit_record missing required field: {field}"
            )

    if not isinstance(payload["committed_items"], list):
        raise RefinementConsumerInterfaceError("committed_items must be list")
    if not isinstance(payload["commit_notes"], list):
        raise RefinementConsumerInterfaceError("commit_notes must be list")

    validated_committed_items = [
        _validate_committed_item(item, index)
        for index, item in enumerate(payload["committed_items"])
    ]

    return payload, validated_committed_items


def _sort_items(items):
    return sorted(
        items,
        key=lambda item: (
            -item["total_score"],
            CANDIDATE_PRIORITY[item["candidate_type"]],
            str(item["candidate_value"]),
        ),
    )


def _build_rosetta_entry(item):
    return {
        "guidance_type": item["candidate_type"],
        "guidance_text": (
            f"Committed refinement signal: {item['candidate_type']} "
            f"with score {item['total_score']} from {item['candidate_source']}"
        ),
        "source_candidate_type": item["candidate_type"],
        "total_score": item["total_score"],
        "commit_targets": list(item["commit_targets"]),
    }


def _build_curved_mirror_entry(item):
    return {
        "signal_type": item["candidate_type"],
        "signal_value": item["candidate_value"],
        "total_score": item["total_score"],
        "commit_targets": list(item["commit_targets"]),
        "source_candidate_type": item["candidate_type"],
    }


def build_refinement_consumer_packet(refinement_persistence_commit_record):
    payload, committed_items = _validate_commit_record(
        refinement_persistence_commit_record
    )

    for index, item in enumerate(committed_items):
        if item["decision"] != "approved":
            raise RefinementConsumerInterfaceError(
                f"committed_items[{index}] must carry decision='approved'"
            )
        if item["promotion_status"] != "promoted":
            raise RefinementConsumerInterfaceError(
                f"committed_items[{index}] must carry promotion_status='promoted'"
            )
        if item["route_status"] != "routed":
            raise RefinementConsumerInterfaceError(
                f"committed_items[{index}] must carry route_status='routed'"
            )
        if item["commit_status"] != "committed":
            raise RefinementConsumerInterfaceError(
                f"committed_items[{index}] must carry commit_status='committed'"
            )

    sorted_committed_items = _sort_items(committed_items)

    rosetta_packet = [_build_rosetta_entry(item) for item in sorted_committed_items]
    curved_mirror_packet = [
        _build_curved_mirror_entry(item) for item in sorted_committed_items
    ]

    consumer_notes = []
    if not sorted_committed_items:
        consumer_notes.append("no_consumer_items_available")

    return {
        "artifact_type": "refinement_consumer_packet",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_CONSUMER_INTERFACE",
            "source_artifact_type": "refinement_persistence_commit_record",
            "committed_input_count": len(sorted_committed_items),
            "rosetta_packet_count": len(rosetta_packet),
            "curved_mirror_packet_count": len(curved_mirror_packet),
            "rosetta_packet": rosetta_packet,
            "curved_mirror_packet": curved_mirror_packet,
            "consumer_notes": consumer_notes,
            "sealed": True,
        },
    }