from __future__ import annotations


class RefinementPromotionError(Exception):
    """Raised when refinement promotion input artifacts are invalid."""


CANDIDATE_PRIORITY = {
    "pattern_note": 1,
    "target_child_core_count": 2,
    "closeout_count": 3,
    "intake_count": 4,
}

APPROVED_DECISIONS = {
    "approved",
    "deferred",
    "rejected",
}


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise RefinementPromotionError(f"{name} must be dict")


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise RefinementPromotionError(f"{name} payload must be dict")
    return payload


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise RefinementPromotionError(
            f"invalid artifact_type: expected {expected}, got {value.get('artifact_type')}"
        )


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise RefinementPromotionError(f"{name} must be sealed")


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise RefinementPromotionError(f"{name} contains internal field: {key}")


def _validate_decision_item(item, index, section_name):
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
    ]
    for field in required_fields:
        if field not in item:
            raise RefinementPromotionError(
                f"{section_name}[{index}] missing required field: {field}"
            )

    if item["candidate_type"] not in CANDIDATE_PRIORITY:
        raise RefinementPromotionError(
            f"{section_name}[{index}] invalid candidate_type: {item['candidate_type']}"
        )

    if not isinstance(item["score_components"], list):
        raise RefinementPromotionError(
            f"{section_name}[{index}] score_components must be list"
        )

    if not isinstance(item["total_score"], int):
        raise RefinementPromotionError(
            f"{section_name}[{index}] total_score must be int"
        )

    if item["decision"] not in APPROVED_DECISIONS:
        raise RefinementPromotionError(
            f"{section_name}[{index}] invalid decision: {item['decision']}"
        )

    return item


def _validate_decision_record(record):
    _require_dict(record, "refinement_decision_record")
    _require_artifact_type(record, "refinement_decision_record")
    payload = _require_payload(record, "refinement_decision_record")
    _reject_internal_fields(payload, "refinement_decision_record")
    _require_sealed(payload, "refinement_decision_record")

    required_fields = [
        "issuing_authority",
        "source_artifact_type",
        "approved_count",
        "deferred_count",
        "rejected_count",
        "approved",
        "deferred",
        "rejected",
        "arbitration_notes",
    ]
    for field in required_fields:
        if field not in payload:
            raise RefinementPromotionError(
                f"refinement_decision_record missing required field: {field}"
            )

    if not isinstance(payload["approved"], list):
        raise RefinementPromotionError("approved must be list")
    if not isinstance(payload["deferred"], list):
        raise RefinementPromotionError("deferred must be list")
    if not isinstance(payload["rejected"], list):
        raise RefinementPromotionError("rejected must be list")
    if not isinstance(payload["arbitration_notes"], list):
        raise RefinementPromotionError("arbitration_notes must be list")

    validated_approved = [
        _validate_decision_item(item, index, "approved")
        for index, item in enumerate(payload["approved"])
    ]
    validated_deferred = [
        _validate_decision_item(item, index, "deferred")
        for index, item in enumerate(payload["deferred"])
    ]
    validated_rejected = [
        _validate_decision_item(item, index, "rejected")
        for index, item in enumerate(payload["rejected"])
    ]

    return payload, validated_approved, validated_deferred, validated_rejected


def _sort_items(items):
    return sorted(
        items,
        key=lambda item: (
            -item["total_score"],
            CANDIDATE_PRIORITY[item["candidate_type"]],
            str(item["candidate_value"]),
        ),
    )


def build_refinement_promotion_record(refinement_decision_record):
    payload, approved, deferred, rejected = _validate_decision_record(
        refinement_decision_record
    )

    for index, item in enumerate(approved):
        if item["decision"] != "approved":
            raise RefinementPromotionError(
                f"approved[{index}] must carry decision='approved'"
            )
    for index, item in enumerate(deferred):
        if item["decision"] != "deferred":
            raise RefinementPromotionError(
                f"deferred[{index}] must carry decision='deferred'"
            )
    for index, item in enumerate(rejected):
        if item["decision"] != "rejected":
            raise RefinementPromotionError(
                f"rejected[{index}] must carry decision='rejected'"
            )

    sorted_approved = _sort_items(approved)

    promoted = []
    overflow_not_promoted = []

    for index, item in enumerate(sorted_approved):
        promoted_item = {
            **item,
            "promotion_status": "promoted" if index < 3 else "not_promoted_cap_exceeded",
            "promotion_reason": "approved_for_controlled_persistence"
            if index < 3
            else "promotion_cap_exceeded",
            "lineage_source_artifact_type": "refinement_decision_record",
        }
        if index < 3:
            promoted.append(promoted_item)
        else:
            overflow_not_promoted.append(promoted_item)

    promotion_notes = []
    if not promoted:
        promotion_notes.append("no_items_promoted")
    if overflow_not_promoted:
        promotion_notes.append("promotion_cap_enforced")

    return {
        "artifact_type": "refinement_promotion_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_PROMOTION",
            "source_artifact_type": "refinement_decision_record",
            "promoted_count": len(promoted),
            "overflow_not_promoted_count": len(overflow_not_promoted),
            "deferred_visible_count": len(deferred),
            "rejected_visible_count": len(rejected),
            "promoted": promoted,
            "overflow_not_promoted": overflow_not_promoted,
            "deferred_visible": deferred,
            "rejected_visible": rejected,
            "promotion_notes": promotion_notes,
            "sealed": True,
        },
    }