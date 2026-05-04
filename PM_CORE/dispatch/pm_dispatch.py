from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Tuple

from .dispatch_packet_builder import (
    build_dispatch_failure_receipt,
    build_dispatch_packet,
)
from .dispatch_state import DispatchState

# Bound narrative spillover.
MAX_RATIONALE_CHARS = 500


def validate_dispatch_readiness(
    pm_routing_packet: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    destination_surface_map: Mapping[str, str],
) -> Tuple[bool, str]:
    """
    Binary dispatch gate for Stage 20.

    Returns:
        (True, "ready") on success
        (False, "<reason>") on failure
    """
    required_common = {
        "artifact_type",
        "source_decision_id",
        "intent",
        "target_mode",
        "rationale_summary",
        "upstream_refs",
        "timestamp",
        "routing_readiness",
    }

    missing = sorted(field for field in required_common if field not in pm_routing_packet)
    if missing:
        return False, f"missing_required_fields:{','.join(missing)}"

    if pm_routing_packet.get("artifact_type") != "pm_routing_packet":
        return False, "invalid_artifact_type"

    if pm_routing_packet.get("routing_readiness") != "ready":
        return False, "routing_not_ready"

    rationale_summary = pm_routing_packet.get("rationale_summary")
    if not isinstance(rationale_summary, str) or not rationale_summary.strip():
        return False, "empty_rationale_summary"
    if len(rationale_summary) > MAX_RATIONALE_CHARS:
        return False, "rationale_not_bounded"

    upstream_refs = pm_routing_packet.get("upstream_refs")
    if not isinstance(upstream_refs, list) or len(upstream_refs) == 0:
        return False, "missing_upstream_refs"

    execution_blockers = pm_routing_packet.get("execution_blockers", [])
    if execution_blockers:
        return False, "execution_blockers_present"

    target_mode = pm_routing_packet.get("target_mode")
    if target_mode != "single":
        if target_mode == "candidate_set":
            return False, "candidate_set_not_dispatchable"
        return False, "invalid_target_mode"

    if "target" not in pm_routing_packet:
        return False, "missing_target"

    target = pm_routing_packet["target"]
    if not isinstance(target, str) or not target.strip():
        return False, "invalid_target"
    if target not in set(valid_child_core_ids):
        return False, "unknown_target"

    destination_surface = destination_surface_map.get(target)
    if not destination_surface:
        return False, "missing_destination_surface"
    if not isinstance(destination_surface, str) or not destination_surface.strip():
        return False, "invalid_destination_surface"

    return True, "ready"


def handoff_routing_to_dispatch(
    pm_routing_packet: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    destination_surface_map: Mapping[str, str],
    state: DispatchState | None = None,
) -> Dict[str, Any]:
    """
    Stage 20 entry point.

    Behavior:
    - validate binary dispatch readiness
    - emit dispatch packet on success
    - emit failure receipt on failure
    - update only minimal local state
    """
    ready, reason = validate_dispatch_readiness(
        pm_routing_packet=pm_routing_packet,
        valid_child_core_ids=valid_child_core_ids,
        destination_surface_map=destination_surface_map,
    )

    if not ready:
        return build_dispatch_failure_receipt(
            reason=reason,
            pm_routing_packet=pm_routing_packet,
        )

    destination_surface = destination_surface_map[pm_routing_packet["target"]]
    dispatch_packet = build_dispatch_packet(
        pm_routing_packet=pm_routing_packet,
        destination_surface=destination_surface,
    )

    if state is not None:
        state.update(
            dispatch_id=dispatch_packet["dispatch_id"],
            target=dispatch_packet["target_core"],
        )

    return dispatch_packet