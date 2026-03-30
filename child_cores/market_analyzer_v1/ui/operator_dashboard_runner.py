from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

try:
    from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
        build_operator_dashboard,
    )
except ImportError:
    from child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (  # type: ignore
        build_operator_dashboard,
    )

try:
    from AI_GO.api.pre_interface_watcher import run_pre_interface_watcher
except ImportError:
    from api.pre_interface_watcher import run_pre_interface_watcher  # type: ignore

try:
    from AI_GO.api.pre_interface_smi import record_pre_interface_exposure
except ImportError:
    from api.pre_interface_smi import record_pre_interface_exposure  # type: ignore


def _ensure_runtime_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Existing lightweight ingress normalization bridge.

    This function is intentionally minimal here because the request payload shape
    is already governed elsewhere in the live ingress path. The runner simply
    preserves a stable internal dict contract.
    """
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")
    return deepcopy(payload)


def _attach_external_memory_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Projects already-generated external-memory advisory context into the runtime
    result shape expected by the dashboard builder.

    Accepted sources:
    - external_memory_merge.external_memory_panel
    - external_memory_merge.panel
    - external_memory_return_packet.memory_context_panel

    This function does not compute memory. It only exposes bounded existing truth.
    """
    result = deepcopy(runtime_result)

    if isinstance(result.get("external_memory_panel"), dict):
        return result

    merge_payload = result.get("external_memory_merge")
    return_packet = result.get("external_memory_return_packet")

    panel = None
    if isinstance(merge_payload, dict):
        if isinstance(merge_payload.get("external_memory_panel"), dict):
            panel = deepcopy(merge_payload["external_memory_panel"])
        elif isinstance(merge_payload.get("panel"), dict):
            panel = deepcopy(merge_payload["panel"])

    if panel is None and isinstance(return_packet, dict):
        if isinstance(return_packet.get("memory_context_panel"), dict):
            panel = deepcopy(return_packet["memory_context_panel"])

    if isinstance(panel, dict):
        panel.setdefault("source", "external_memory")
        panel["advisory_only"] = True
        result["external_memory_panel"] = panel

    return result


def _run_runtime(runtime_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder orchestration boundary.

    In the real project this should continue to call the existing governed live
    runtime path. This wrapper exists only so the runner remains explicit and
    testable.
    """
    if "runtime_result" in runtime_payload and isinstance(runtime_payload["runtime_result"], dict):
        return deepcopy(runtime_payload["runtime_result"])
    return deepcopy(runtime_payload)


def run_operator_dashboard(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Canonical operator-facing dashboard runner.

    Flow:
    ingress payload
    -> governed runtime result
    -> optional external-memory advisory visibility
    -> dashboard build
    -> pre-interface watcher
    -> pre-interface smi
    -> final response
    """
    runtime_payload = _ensure_runtime_payload(payload)
    runtime_result = _run_runtime(runtime_payload)
    runtime_result = _attach_external_memory_panel(runtime_result)

    dashboard = build_operator_dashboard(runtime_result)

    watcher_receipt = run_pre_interface_watcher(dashboard)
    dashboard["pre_interface_watcher"] = watcher_receipt

    smi_receipt = record_pre_interface_exposure(dashboard, watcher_receipt)
    dashboard["pre_interface_smi"] = smi_receipt

    return dashboard