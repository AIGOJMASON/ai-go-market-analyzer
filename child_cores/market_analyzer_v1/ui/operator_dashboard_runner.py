# child_cores/market_analyzer_v1/ui/operator_dashboard_runner.py

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

try:
    from AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner import run_live_payload
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.ui.live_data_runner import run_live_payload

try:
    from AI_GO.api.pre_interface_smi import run_pre_interface_smi
    from AI_GO.api.pre_interface_watcher import run_pre_interface_watcher
except ModuleNotFoundError:
    from api.pre_interface_smi import run_pre_interface_smi
    from api.pre_interface_watcher import run_pre_interface_watcher

try:
    from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_builder import build_operator_dashboard
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.ui.operator_dashboard_builder import build_operator_dashboard


def _ensure_runtime_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    runtime_payload = deepcopy(payload)

    request_id = runtime_payload.get("request_id")
    if not isinstance(request_id, str) or not request_id.strip():
        request_id = "live-request"
        runtime_payload["request_id"] = request_id

    case_id = runtime_payload.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        runtime_payload["case_id"] = request_id

    return runtime_payload


def _build_pre_interface_rejection_payload(
    base_payload: Dict[str, Any],
    watcher_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    case_panel = deepcopy(base_payload.get("case_panel", {})) if isinstance(base_payload.get("case_panel"), dict) else {}
    governance_panel = deepcopy(base_payload.get("governance_panel", {})) if isinstance(base_payload.get("governance_panel"), dict) else {}

    governance_panel["watcher_passed"] = False
    governance_panel["pre_interface_status"] = "rejected"

    return {
        "status": "rejected",
        "request_id": base_payload.get("request_id") or case_panel.get("case_id"),
        "core_id": base_payload.get("core_id", "market_analyzer_v1"),
        "route_mode": base_payload.get("route_mode"),
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": base_payload.get("approval_required", True),
        "dashboard_type": "market_analyzer_v1_operator_dashboard",
        "case_panel": case_panel,
        "governance_panel": governance_panel,
        "rejection_panel": {
            "reason": "pre_interface_watcher_failed",
            "failures": watcher_receipt.get("failures", []),
        },
        "pre_interface_watcher": watcher_receipt,
    }


def run_operator_dashboard(
    payload: Dict[str, Any],
    upstream_refs: Optional[Dict[str, Any]] = None,
    persist_receipts: bool = True,
) -> Dict[str, Any]:
    runtime_payload = _ensure_runtime_payload(payload)

    runtime_result = run_live_payload(runtime_payload)
    base_payload = build_operator_dashboard(runtime_result)

    watcher_result = run_pre_interface_watcher(
        payload=base_payload,
        upstream_refs=upstream_refs,
        persist=persist_receipts,
    )
    watcher_receipt = watcher_result["receipt"]

    if watcher_receipt["status"] != "passed":
        return _build_pre_interface_rejection_payload(
            base_payload=base_payload,
            watcher_receipt=watcher_receipt,
        )

    smi_result = run_pre_interface_smi(
        payload=base_payload,
        watcher_receipt=watcher_receipt,
        upstream_refs=upstream_refs,
        persist=persist_receipts,
    )

    base_payload["pre_interface_watcher"] = watcher_receipt
    base_payload["pre_interface_smi"] = smi_result["record"]

    return base_payload
