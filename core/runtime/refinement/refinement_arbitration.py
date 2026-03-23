from __future__ import annotations


class RefinementArbitrationError(Exception):
    pass


CANDIDATE_PRIORITY = {
    "pattern_note": 1,
    "target_child_core_count": 2,
    "closeout_count": 3,
    "intake_count": 4,
}


def _require_dict(value, name):
    if not isinstance(value, dict):
        raise RefinementArbitrationError(f"{name} must be dict")


def _require_payload(value, name):
    payload = value.get("payload")
    if not isinstance(payload, dict):
        raise RefinementArbitrationError(f"{name} payload must be dict")
    return payload


def _require_artifact_type(value, expected):
    if value.get("artifact_type") != expected:
        raise RefinementArbitrationError(
            f"invalid artifact_type: expected {expected}"
        )


def _require_sealed(payload, name):
    if payload.get("sealed") is not True:
        raise RefinementArbitrationError(f"{name} must be sealed")


def _reject_internal_fields(payload, name):
    for key in payload:
        if str(key).startswith("_"):
            raise RefinementArbitrationError(f"{name} contains internal field: {key}")


def _validate_scoring_record(record):
    _require_dict(record, "refinement_scoring_record")
    _require_artifact_type(record, "refinement_scoring_record")
    payload = _require_payload(record, "refinement_scoring_record")
    _reject_internal_fields(payload, "refinement_scoring_record")
    _require_sealed(payload, "refinement_scoring_record")

    required = ["scored_candidates"]
    for field in required:
        if field not in payload:
            raise RefinementArbitrationError(f"missing field: {field}")

    if not isinstance(payload["scored_candidates"], list):
        raise RefinementArbitrationError("scored_candidates must be list")

    return payload


def _validate_scored_candidate(candidate, index):
    _require_dict(candidate, f"scored_candidate[{index}]")

    required_fields = [
        "candidate_type",
        "candidate_source",
        "candidate_value",
        "selection_reason",
        "score_components",
        "total_score",
    ]
    for field in required_fields:
        if field not in candidate:
            raise RefinementArbitrationError(
                f"scored_candidate[{index}] missing required field: {field}"
            )

    candidate_type = candidate["candidate_type"]
    if candidate_type not in CANDIDATE_PRIORITY:
        raise RefinementArbitrationError(
            f"scored_candidate[{index}] has invalid candidate_type: {candidate_type}"
        )

    if not isinstance(candidate["score_components"], list):
        raise RefinementArbitrationError(
            f"scored_candidate[{index}] score_components must be list"
        )

    if not isinstance(candidate["total_score"], int):
        raise RefinementArbitrationError(
            f"scored_candidate[{index}] total_score must be int"
        )

    return candidate


def _decision_from_score(score):
    if score >= 4:
        return "approved"
    if score == 3:
        return "deferred"
    return "rejected"


def _sort_candidates(candidates):
    return sorted(
        candidates,
        key=lambda c: (
            -c["total_score"],
            CANDIDATE_PRIORITY[c["candidate_type"]],
            str(c["candidate_value"]),
        ),
    )


def build_refinement_decision_record(refinement_scoring_record):
    payload = _validate_scoring_record(refinement_scoring_record)

    validated_candidates = [
        _validate_scored_candidate(candidate, index)
        for index, candidate in enumerate(payload["scored_candidates"])
    ]

    sorted_candidates = _sort_candidates(validated_candidates)

    approved = []
    deferred = []
    rejected = []

    for candidate in sorted_candidates:
        score = candidate["total_score"]
        decision = _decision_from_score(score)

        enriched = {
            **candidate,
            "decision": decision,
            "decision_reason": f"score_{score}",
        }

        if decision == "approved":
            approved.append(enriched)
        elif decision == "deferred":
            deferred.append(enriched)
        else:
            rejected.append(enriched)

    approved = approved[:3]

    return {
        "artifact_type": "refinement_decision_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_ARBITRATION",
            "source_artifact_type": "refinement_scoring_record",
            "approved_count": len(approved),
            "deferred_count": len(deferred),
            "rejected_count": len(rejected),
            "approved": approved,
            "deferred": deferred,
            "rejected": rejected,
            "arbitration_notes": [],
            "sealed": True,
        },
    }