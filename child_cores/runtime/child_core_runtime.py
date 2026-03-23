from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Mapping, Tuple

from .runtime_receipt_builder import (
    build_runtime_failure_receipt,
    build_runtime_receipt,
)
from .runtime_state import RuntimeState

ExecutionHandler = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any] | None]


def validate_runtime_readiness(
    ingress_receipt: Dict[str, Any],
    runtime_context: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    execution_surface_map: Mapping[str, str],
    execution_handler_map: Mapping[str, ExecutionHandler],
) -> Tuple[bool, str]:
    """
    Binary runtime gate for Stage 22.

    Returns:
        (True, "ready") on success
        (False, "<reason>") on failure
    """
    required_ingress = {
        "artifact_type",
        "ingress_id",
        "source_dispatch_id",
        "source_decision_id",
        "target_core",
        "destination_surface",
        "handoff_status",
        "timestamp",
    }

    missing_ingress = sorted(field for field in required_ingress if field not in ingress_receipt)
    if missing_ingress:
        return False, f"missing_ingress_fields:{','.join(missing_ingress)}"

    if ingress_receipt.get("artifact_type") != "ingress_receipt":
        return False, "invalid_artifact_type"

    if ingress_receipt.get("handoff_status") != "accepted":
        return False, "ingress_not_accepted"

    target_core = ingress_receipt.get("target_core")
    if not isinstance(target_core, str) or not target_core.strip():
        return False, "invalid_target_core"
    if target_core not in set(valid_child_core_ids):
        return False, "unknown_target_core"

    if not isinstance(runtime_context, dict):
        return False, "invalid_runtime_context"

    if "execution_surface" not in runtime_context:
        return False, "missing_execution_surface"

    execution_surface = runtime_context.get("execution_surface")
    if not isinstance(execution_surface, str) or not execution_surface.strip():
        return False, "invalid_execution_surface"

    expected_surface = execution_surface_map.get(target_core)
    if not expected_surface:
        return False, "missing_declared_execution_surface"
    if execution_surface != expected_surface:
        return False, "execution_surface_target_mismatch"

    runtime_blockers = runtime_context.get("runtime_blockers", [])
    if runtime_blockers:
        return False, "runtime_blockers_present"

    handler = execution_handler_map.get(target_core)
    if handler is None:
        return False, "missing_execution_handler"
    if not callable(handler):
        return False, "invalid_execution_handler"

    return True, "ready"


def handoff_ingress_to_runtime(
    ingress_receipt: Dict[str, Any],
    runtime_context: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    execution_surface_map: Mapping[str, str],
    execution_handler_map: Mapping[str, ExecutionHandler],
    state: RuntimeState | None = None,
) -> Dict[str, Any]:
    """
    Stage 22 entry point.

    Behavior:
    - validate binary runtime readiness
    - invoke declared execution handler on success
    - emit runtime receipt on success
    - emit failure receipt on failure
    - update only minimal local state
    """
    ready, reason = validate_runtime_readiness(
        ingress_receipt=ingress_receipt,
        runtime_context=runtime_context,
        valid_child_core_ids=valid_child_core_ids,
        execution_surface_map=execution_surface_map,
        execution_handler_map=execution_handler_map,
    )

    if not ready:
        return build_runtime_failure_receipt(
            reason=reason,
            ingress_receipt=ingress_receipt,
        )

    target_core = ingress_receipt["target_core"]
    execution_surface = runtime_context["execution_surface"]
    handler = execution_handler_map[target_core]

    try:
        handler_result = handler(ingress_receipt, runtime_context)
    except Exception as exc:
        return build_runtime_failure_receipt(
            reason=f"execution_handler_exception:{exc.__class__.__name__}",
            ingress_receipt=ingress_receipt,
        )

    if handler_result is not None and not isinstance(handler_result, dict):
        return build_runtime_failure_receipt(
            reason="invalid_handler_result_type",
            ingress_receipt=ingress_receipt,
        )

    result_ref = None
    if isinstance(handler_result, dict):
        result_ref_value = handler_result.get("result_ref")
        if result_ref_value is not None:
            if not isinstance(result_ref_value, str) or not result_ref_value.strip():
                return build_runtime_failure_receipt(
                    reason="invalid_result_ref",
                    ingress_receipt=ingress_receipt,
                )
            result_ref = result_ref_value

    receipt = build_runtime_receipt(
        ingress_receipt=ingress_receipt,
        execution_surface=execution_surface,
        result_ref=result_ref,
    )

    if state is not None:
        state.update(
            runtime_id=receipt["runtime_id"],
            target_core=target_core,
        )

    return receipt