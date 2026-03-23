from __future__ import annotations

from typing import Any, Dict, Iterable, Set, Tuple

from .routing_packet_builder import build_failure_receipt, build_routing_packet
from .routing_state import RoutingState

# Keep bounded and explicit. Do not infer beyond this.
MAX_RATIONALE_CHARS = 500


def validate_routing_readiness(
    pm_decision_packet: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
) -> Tuple[bool, str]:
    """
    Binary readiness gate for Stage 19.

    Returns:
        (True, "ready") on success
        (False, "<reason>") on failure
    """
    required_common = {
        "decision_id",
        "intent",
        "target_mode",
        "rationale_summary",
        "upstream_refs",
        "timestamp",
    }

    missing = sorted(field for field in required_common if field not in pm_decision_packet)
    if missing:
        return False, f"missing_required_fields:{','.join(missing)}"

    intent = pm_decision_packet.get("intent")
    if not isinstance(intent, str) or not intent.strip():
        return False, "intent_not_defined"

    target_mode = pm_decision_packet.get("target_mode")
    if target_mode not in {"single", "candidate_set"}:
        return False, "invalid_target_mode"

    rationale_summary = pm_decision_packet.get("rationale_summary")
    if not isinstance(rationale_summary, str) or not rationale_summary.strip():
        return False, "empty_rationale_summary"
    if len(rationale_summary) > MAX_RATIONALE_CHARS:
        return False, "rationale_not_bounded"

    upstream_refs = pm_decision_packet.get("upstream_refs")
    if not isinstance(upstream_refs, list) or len(upstream_refs) == 0:
        return False, "missing_upstream_refs"

    unresolved_dependencies = pm_decision_packet.get("unresolved_dependencies", [])
    if unresolved_dependencies:
        return False, "unresolved_dependencies_present"

    valid_ids: Set[str] = set(valid_child_core_ids)

    if target_mode == "single":
        if "target" not in pm_decision_packet:
            return False, "missing_target"
        if "candidate_targets" in pm_decision_packet:
            return False, "candidate_targets_not_allowed_in_single_mode"

        target = pm_decision_packet["target"]
        if not isinstance(target, str) or not target.strip():
            return False, "invalid_target"
        if target not in valid_ids:
            return False, "unknown_target"

        return True, "ready"

    # candidate_set mode
    required_candidate = {"candidate_targets", "candidate_set_controls"}
    missing_candidate = sorted(
        field for field in required_candidate if field not in pm_decision_packet
    )
    if missing_candidate:
        return False, f"missing_candidate_set_fields:{','.join(missing_candidate)}"

    candidate_targets = pm_decision_packet["candidate_targets"]
    controls = pm_decision_packet["candidate_set_controls"]

    if not isinstance(candidate_targets, list) or len(candidate_targets) == 0:
        return False, "empty_candidate_targets"
    if len(set(candidate_targets)) != len(candidate_targets):
        return False, "duplicate_candidate_targets"
    if not all(isinstance(item, str) and item.strip() for item in candidate_targets):
        return False, "invalid_candidate_target_entry"
    if not all(item in valid_ids for item in candidate_targets):
        return False, "unknown_candidate_target"

    if not isinstance(controls, dict):
        return False, "invalid_candidate_set_controls"
    if "max_candidates" not in controls or "ranking_required" not in controls:
        return False, "incomplete_candidate_set_controls"

    max_candidates = controls["max_candidates"]
    ranking_required = controls["ranking_required"]

    if not isinstance(max_candidates, int) or max_candidates < 1:
        return False, "invalid_max_candidates"
    if len(candidate_targets) > max_candidates:
        return False, "candidate_count_exceeds_max"
    if not isinstance(ranking_required, bool):
        return False, "invalid_ranking_required"

    if "target" in pm_decision_packet:
        return False, "target_not_allowed_in_candidate_set_mode"

    return True, "ready"


def handoff_decision_to_routing(
    pm_decision_packet: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    state: RoutingState | None = None,
) -> Dict[str, Any]:
    """
    Stage 19 entry point.

    Behavior:
    - validate binary readiness
    - emit routing packet on success
    - emit failure receipt on failure
    - update only minimal local state
    """
    ready, reason = validate_routing_readiness(pm_decision_packet, valid_child_core_ids)

    if not ready:
        return build_failure_receipt(reason=reason, pm_decision_packet=pm_decision_packet)

    routing_packet = build_routing_packet(pm_decision_packet)

    if state is not None:
        state.update(
            packet_id=routing_packet["source_decision_id"],
            target_set=routing_packet["target_set"],
        )

    return routing_packet