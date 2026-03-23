from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Mapping, Tuple

from .watcher_receipt_builder import (
    build_watcher_failure_receipt,
    build_watcher_receipt,
    build_watcher_result,
)
from .watcher_state import WatcherState

WatcherHandler = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any] | None]


def validate_watcher_readiness(
    disposition_receipt: Dict[str, Any],
    watcher_context: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    watcher_target: str,
    watcher_handler_map: Mapping[str, WatcherHandler],
) -> Tuple[bool, str]:
    """
    Binary watcher gate for Stage 25.

    Returns:
        (True, "ready") on success
        (False, "<reason>") on failure
    """
    required_disposition = {
        "artifact_type",
        "review_id",
        "source_output_id",
        "source_runtime_id",
        "target_core",
        "requested_target",
        "selected_target",
        "disposition_status",
        "timestamp",
    }

    missing_disposition = sorted(field for field in required_disposition if field not in disposition_receipt)
    if missing_disposition:
        return False, f"missing_disposition_fields:{','.join(missing_disposition)}"

    if disposition_receipt.get("artifact_type") != "output_disposition_receipt":
        return False, "invalid_artifact_type"

    if disposition_receipt.get("disposition_status") != "routed":
        return False, "disposition_not_routed"

    if disposition_receipt.get("selected_target") != watcher_target:
        return False, "selected_target_not_watcher"

    target_core = disposition_receipt.get("target_core")
    if not isinstance(target_core, str) or not target_core.strip():
        return False, "invalid_target_core"
    if target_core not in set(valid_child_core_ids):
        return False, "unknown_target_core"

    if not isinstance(watcher_context, dict):
        return False, "invalid_watcher_context"

    watcher_blockers = watcher_context.get("watcher_blockers", [])
    if watcher_blockers:
        return False, "watcher_blockers_present"

    handler = watcher_handler_map.get(target_core)
    if handler is None:
        return False, "missing_watcher_handler"
    if not callable(handler):
        return False, "invalid_watcher_handler"

    return True, "ready"


def handoff_review_to_watcher(
    disposition_receipt: Dict[str, Any],
    watcher_context: Dict[str, Any],
    valid_child_core_ids: Iterable[str],
    watcher_target: str,
    watcher_handler_map: Mapping[str, WatcherHandler],
    state: WatcherState | None = None,
) -> Dict[str, Any]:
    """
    Stage 25 entry point.

    Behavior:
    - validate binary watcher readiness
    - invoke declared watcher handler on success
    - require strict findings payload on success
    - emit watcher result and watcher receipt on success
    - emit failure receipt on failure
    - update only minimal local state
    """
    ready, reason = validate_watcher_readiness(
        disposition_receipt=disposition_receipt,
        watcher_context=watcher_context,
        valid_child_core_ids=valid_child_core_ids,
        watcher_target=watcher_target,
        watcher_handler_map=watcher_handler_map,
    )

    if not ready:
        return build_watcher_failure_receipt(
            reason=reason,
            disposition_receipt=disposition_receipt,
        )

    target_core = disposition_receipt["target_core"]
    handler = watcher_handler_map[target_core]

    try:
        handler_result = handler(disposition_receipt, watcher_context)
    except Exception as exc:
        return build_watcher_failure_receipt(
            reason=f"watcher_handler_exception:{exc.__class__.__name__}",
            disposition_receipt=disposition_receipt,
        )

    if handler_result is None:
        return build_watcher_failure_receipt(
            reason="missing_findings_payload",
            disposition_receipt=disposition_receipt,
        )

    if not isinstance(handler_result, dict):
        return build_watcher_failure_receipt(
            reason="invalid_watcher_result_type",
            disposition_receipt=disposition_receipt,
        )

    if "findings" not in handler_result:
        return build_watcher_failure_receipt(
            reason="missing_findings_key",
            disposition_receipt=disposition_receipt,
        )

    findings_value = handler_result.get("findings")
    findings_ref_value = handler_result.get("findings_ref")

    if not isinstance(findings_value, dict):
        return build_watcher_failure_receipt(
            reason="invalid_findings_type",
            disposition_receipt=disposition_receipt,
        )

    findings_ref = None
    if findings_ref_value is not None:
        if not isinstance(findings_ref_value, str) or not findings_ref_value.strip():
            return build_watcher_failure_receipt(
                reason="invalid_findings_ref",
                disposition_receipt=disposition_receipt,
            )
        findings_ref = findings_ref_value

    watcher_result = build_watcher_result(
        disposition_receipt=disposition_receipt,
        findings=findings_value,
        findings_ref=findings_ref,
        watcher_status="completed",
    )
    watcher_receipt = build_watcher_receipt(watcher_result=watcher_result)

    if state is not None:
        state.update(
            watcher_id=watcher_result["watcher_id"],
            target_core=target_core,
            watcher_status=watcher_result["watcher_status"],
        )

    return {
        "watcher_result": watcher_result,
        "watcher_receipt": watcher_receipt,
    }