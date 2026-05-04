from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Set, Tuple

from .review_receipt_builder import (
    build_output_disposition_receipt,
    build_review_failure_receipt,
    build_review_hold_receipt,
)
from .review_state import ReviewState


def validate_review_readiness(
    output_artifact: Dict[str, Any],
    review_context: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    allowed_downstream_targets: Mapping[str, Set[str]],
) -> Tuple[bool, str]:
    """
    Binary review gate for Stage 24.

    Returns:
        (True, "ready") on success
        (False, "<reason>") on failure
    """
    required_output = {
        "artifact_type",
        "output_id",
        "source_runtime_id",
        "target_core",
        "output_surface",
        "output_status",
        "timestamp",
    }

    missing_output = sorted(field for field in required_output if field not in output_artifact)
    if missing_output:
        return False, f"missing_output_fields:{','.join(missing_output)}"

    if output_artifact.get("artifact_type") != "output_artifact":
        return False, "invalid_artifact_type"

    if output_artifact.get("output_status") != "constructed":
        return False, "output_not_constructed"

    target_core = output_artifact.get("target_core")
    if not isinstance(target_core, str) or not target_core.strip():
        return False, "invalid_target_core"
    if target_core not in set(valid_child_core_ids):
        return False, "unknown_target_core"

    if not isinstance(review_context, dict):
        return False, "invalid_review_context"

    if "requested_target" not in review_context:
        return False, "missing_requested_target"

    requested_target = review_context.get("requested_target")
    if not isinstance(requested_target, str) or not requested_target.strip():
        return False, "invalid_requested_target"

    allowed_targets = allowed_downstream_targets.get(target_core)
    if not allowed_targets:
        return False, "missing_allowed_downstream_targets"

    if requested_target not in allowed_targets and requested_target not in {"hold", "terminate"}:
        return False, "requested_target_not_allowed"

    review_blockers = review_context.get("review_blockers", [])
    if review_blockers:
        return False, "review_blockers_present"

    return True, "ready"


def handoff_output_to_review(
    output_artifact: Dict[str, Any],
    review_context: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    allowed_downstream_targets: Mapping[str, Set[str]],
    default_targets: Mapping[str, str],
    state: ReviewState | None = None,
) -> Dict[str, Any]:
    """
    Stage 24 entry point.

    Behavior:
    - validate binary review readiness
    - apply bounded routing/hold logic
    - emit disposition, hold, or failure receipt
    - update only minimal local state
    """
    ready, reason = validate_review_readiness(
        output_artifact=output_artifact,
        review_context=review_context,
        valid_child_core_ids=valid_child_core_ids,
        allowed_downstream_targets=allowed_downstream_targets,
    )

    if not ready:
        return build_review_failure_receipt(
            reason=reason,
            output_artifact=output_artifact,
        )

    target_core = output_artifact["target_core"]
    requested_target = review_context["requested_target"]

    route_overrides = review_context.get("route_overrides", {})
    selected_target = route_overrides.get(target_core, requested_target)

    review_flags = review_context.get("review_flags", [])

    if selected_target == "hold" or "hold" in review_flags:
        receipt = build_review_hold_receipt(
            output_artifact=output_artifact,
            requested_target=requested_target,
            reason="held_by_review_policy",
        )
        if state is not None:
            state.update(
                review_id=receipt["review_id"],
                target_core=target_core,
                disposition="held",
            )
        return receipt

    if selected_target == "terminate":
        receipt = build_review_failure_receipt(
            reason="terminated_by_review_policy",
            output_artifact=output_artifact,
        )
        if state is not None:
            state.update(
                review_id=f"REVIEW-FAILED-{output_artifact['output_id']}",
                target_core=target_core,
                disposition="terminated",
            )
        return receipt

    allowed_targets = allowed_downstream_targets[target_core]
    if selected_target not in allowed_targets:
        fallback_target = default_targets.get(target_core)
        if not fallback_target or fallback_target not in allowed_targets:
            return build_review_failure_receipt(
                reason="no_lawful_downstream_target",
                output_artifact=output_artifact,
            )
        selected_target = fallback_target

    receipt = build_output_disposition_receipt(
        output_artifact=output_artifact,
        requested_target=requested_target,
        selected_target=selected_target,
        disposition_status="routed",
    )

    if state is not None:
        state.update(
            review_id=receipt["review_id"],
            target_core=target_core,
            disposition="routed",
        )

    return receipt