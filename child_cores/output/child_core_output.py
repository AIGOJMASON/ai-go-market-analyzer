from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Mapping, Tuple

from .output_receipt_builder import (
    build_output_artifact,
    build_output_failure_receipt,
    build_output_receipt,
)
from .output_state import OutputState

OutputBuilder = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any] | None]


def validate_output_readiness(
    runtime_receipt: Dict[str, Any],
    output_context: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    output_surface_map: Mapping[str, str],
    output_builder_map: Mapping[str, OutputBuilder],
) -> Tuple[bool, str]:
    """
    Binary output gate for Stage 23.

    Returns:
        (True, "ready") on success
        (False, "<reason>") on failure
    """
    required_runtime = {
        "artifact_type",
        "runtime_id",
        "source_ingress_id",
        "source_dispatch_id",
        "source_decision_id",
        "target_core",
        "execution_surface",
        "runtime_status",
        "timestamp",
    }

    missing_runtime = sorted(field for field in required_runtime if field not in runtime_receipt)
    if missing_runtime:
        return False, f"missing_runtime_fields:{','.join(missing_runtime)}"

    if runtime_receipt.get("artifact_type") != "runtime_receipt":
        return False, "invalid_artifact_type"

    if runtime_receipt.get("runtime_status") != "completed":
        return False, "runtime_not_completed"

    target_core = runtime_receipt.get("target_core")
    if not isinstance(target_core, str) or not target_core.strip():
        return False, "invalid_target_core"
    if target_core not in set(valid_child_core_ids):
        return False, "unknown_target_core"

    if not isinstance(output_context, dict):
        return False, "invalid_output_context"

    if "output_surface" not in output_context:
        return False, "missing_output_surface"

    output_surface = output_context.get("output_surface")
    if not isinstance(output_surface, str) or not output_surface.strip():
        return False, "invalid_output_surface"

    expected_surface = output_surface_map.get(target_core)
    if not expected_surface:
        return False, "missing_declared_output_surface"
    if output_surface != expected_surface:
        return False, "output_surface_target_mismatch"

    output_blockers = output_context.get("output_blockers", [])
    if output_blockers:
        return False, "output_blockers_present"

    builder = output_builder_map.get(target_core)
    if builder is None:
        return False, "missing_output_builder"
    if not callable(builder):
        return False, "invalid_output_builder"

    return True, "ready"


def handoff_runtime_to_output(
    runtime_receipt: Dict[str, Any],
    output_context: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    output_surface_map: Mapping[str, str],
    output_builder_map: Mapping[str, OutputBuilder],
    state: OutputState | None = None,
) -> Dict[str, Any]:
    """
    Stage 23 entry point.

    Behavior:
    - validate binary output readiness
    - invoke declared output builder on success
    - emit output artifact and output receipt on success
    - emit failure receipt on failure
    - update only minimal local state
    """
    ready, reason = validate_output_readiness(
        runtime_receipt=runtime_receipt,
        output_context=output_context,
        valid_child_core_ids=valid_child_core_ids,
        output_surface_map=output_surface_map,
        output_builder_map=output_builder_map,
    )

    if not ready:
        return build_output_failure_receipt(
            reason=reason,
            runtime_receipt=runtime_receipt,
        )

    target_core = runtime_receipt["target_core"]
    output_surface = output_context["output_surface"]
    builder = output_builder_map[target_core]

    try:
        builder_result = builder(runtime_receipt, output_context)
    except Exception as exc:
        return build_output_failure_receipt(
            reason=f"output_builder_exception:{exc.__class__.__name__}",
            runtime_receipt=runtime_receipt,
        )

    if builder_result is not None and not isinstance(builder_result, dict):
        return build_output_failure_receipt(
            reason="invalid_builder_result_type",
            runtime_receipt=runtime_receipt,
        )

    payload = None
    payload_ref = None

    if isinstance(builder_result, dict):
        payload_value = builder_result.get("payload")
        payload_ref_value = builder_result.get("payload_ref")

        if payload_value is not None and not isinstance(payload_value, dict):
            return build_output_failure_receipt(
                reason="invalid_payload_type",
                runtime_receipt=runtime_receipt,
            )

        if payload_ref_value is not None:
            if not isinstance(payload_ref_value, str) or not payload_ref_value.strip():
                return build_output_failure_receipt(
                    reason="invalid_payload_ref",
                    runtime_receipt=runtime_receipt,
                )
            payload_ref = payload_ref_value

        payload = payload_value if isinstance(payload_value, dict) else builder_result

    output_artifact = build_output_artifact(
        runtime_receipt=runtime_receipt,
        output_surface=output_surface,
        payload=payload,
        payload_ref=payload_ref,
    )
    output_receipt = build_output_receipt(output_artifact=output_artifact)

    if state is not None:
        state.update(
            output_id=output_artifact["output_id"],
            target_core=target_core,
        )

    return {
        "output_artifact": output_artifact,
        "output_receipt": output_receipt,
    }