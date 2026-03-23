from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Mapping, Tuple

from .ingress_receipt_builder import (
    build_ingress_failure_receipt,
    build_ingress_receipt,
)
from .ingress_state import IngressState

IngressHandler = Callable[[Dict[str, Any]], None]


def validate_ingress_readiness(
    dispatch_packet: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    destination_surface_map: Mapping[str, str],
    ingress_handler_map: Mapping[str, IngressHandler],
) -> Tuple[bool, str]:
    """
    Binary ingress gate for Stage 21.

    Returns:
        (True, "ready") on success
        (False, "<reason>") on failure
    """
    required_common = {
        "artifact_type",
        "dispatch_id",
        "source_decision_id",
        "dispatch_intent",
        "target_core",
        "destination_surface",
        "upstream_refs",
        "timestamp",
    }

    missing = sorted(field for field in required_common if field not in dispatch_packet)
    if missing:
        return False, f"missing_required_fields:{','.join(missing)}"

    if dispatch_packet.get("artifact_type") != "dispatch_packet":
        return False, "invalid_artifact_type"

    dispatch_intent = dispatch_packet.get("dispatch_intent")
    if not isinstance(dispatch_intent, str) or not dispatch_intent.strip():
        return False, "missing_dispatch_intent"

    upstream_refs = dispatch_packet.get("upstream_refs")
    if not isinstance(upstream_refs, list) or len(upstream_refs) == 0:
        return False, "missing_upstream_refs"

    ingress_blockers = dispatch_packet.get("ingress_blockers", [])
    if ingress_blockers:
        return False, "ingress_blockers_present"

    target_core = dispatch_packet.get("target_core")
    if not isinstance(target_core, str) or not target_core.strip():
        return False, "invalid_target_core"
    if target_core not in set(valid_child_core_ids):
        return False, "unknown_target_core"

    destination_surface = dispatch_packet.get("destination_surface")
    if not isinstance(destination_surface, str) or not destination_surface.strip():
        return False, "invalid_destination_surface"

    expected_surface = destination_surface_map.get(target_core)
    if not expected_surface:
        return False, "missing_declared_destination_surface"
    if destination_surface != expected_surface:
        return False, "destination_surface_target_mismatch"

    handler = ingress_handler_map.get(target_core)
    if handler is None:
        return False, "missing_ingress_handler"
    if not callable(handler):
        return False, "invalid_ingress_handler"

    return True, "ready"


def handoff_dispatch_to_ingress(
    dispatch_packet: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    destination_surface_map: Mapping[str, str],
    ingress_handler_map: Mapping[str, IngressHandler],
    state: IngressState | None = None,
) -> Dict[str, Any]:
    """
    Stage 21 entry point.

    Behavior:
    - validate binary ingress readiness
    - invoke declared ingress handler on success
    - emit ingress receipt on success
    - emit failure receipt on failure
    - update only minimal local state
    """
    ready, reason = validate_ingress_readiness(
        dispatch_packet=dispatch_packet,
        valid_child_core_ids=valid_child_core_ids,
        destination_surface_map=destination_surface_map,
        ingress_handler_map=ingress_handler_map,
    )

    if not ready:
        return build_ingress_failure_receipt(
            reason=reason,
            dispatch_packet=dispatch_packet,
        )

    target_core = dispatch_packet["target_core"]
    handler = ingress_handler_map[target_core]
    handler(dispatch_packet)

    receipt = build_ingress_receipt(dispatch_packet)

    if state is not None:
        state.update(
            ingress_id=receipt["ingress_id"],
            target_core=target_core,
        )

    return receipt