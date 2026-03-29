# child_cores/market_analyzer_v1/ui/operator_dashboard_runner.py

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, Optional

try:
    from AI_GO.api.pre_interface_smi import run_pre_interface_smi
    from AI_GO.api.pre_interface_watcher import run_pre_interface_watcher
except ModuleNotFoundError:
    from api.pre_interface_smi import run_pre_interface_smi
    from api.pre_interface_watcher import run_pre_interface_watcher


BUILDER_CANDIDATES = (
    "build_operator_dashboard_payload",
    "build_operator_dashboard",
    "build_system_view_payload",
    "build_system_view",
)


def _resolve_builder() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    try:
        from AI_GO.child_cores.market_analyzer_v1.ui import operator_dashboard_builder as builder_module
    except ModuleNotFoundError:
        from child_cores.market_analyzer_v1.ui import operator_dashboard_builder as builder_module

    for name in BUILDER_CANDIDATES:
        candidate = getattr(builder_module, name, None)
        if callable(candidate):
            return candidate

    raise RuntimeError(
        "operator_dashboard_builder_missing_supported_builder;"
        f" tried={','.join(BUILDER_CANDIDATES)}"
    )


def _build_pre_interface_rejection_payload(
    base_payload: Dict[str, Any],
    watcher_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    case_panel = deepcopy(base_payload.get("case_panel", {})) if isinstance(base_payload.get("case_panel"), dict) else {}
    governance_panel = deepcopy(base_payload.get("governance_panel", {})) if isinstance(base_payload.get("governance_panel"), dict) else {}

    governance_panel["watcher_passed"] = False
    governance_panel["pre_interface_status"] = "rejected"

    rejection_panel = {
        "reason": "pre_interface_watcher_failed",
        "failures": watcher_receipt.get("failures", []),
    }

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
        "rejection_panel": rejection_panel,
        "pre_interface_watcher": watcher_receipt,
    }


def finalize_operator_dashboard_payload(
    base_payload: Dict[str, Any],
    upstream_refs: Optional[Dict[str, Any]] = None,
    persist_receipts: bool = True,
) -> Dict[str, Any]:
    payload = deepcopy(base_payload)

    watcher_result = run_pre_interface_watcher(
        payload=payload,
        upstream_refs=upstream_refs,
        persist=persist_receipts,
    )
    watcher_receipt = watcher_result["receipt"]

    if watcher_receipt["status"] != "passed":
        return _build_pre_interface_rejection_payload(
            base_payload=payload,
            watcher_receipt=watcher_receipt,
        )

    smi_result = run_pre_interface_smi(
        payload=payload,
        watcher_receipt=watcher_receipt,
        upstream_refs=upstream_refs,
        persist=persist_receipts,
    )

    payload["pre_interface_watcher"] = watcher_receipt
    payload["pre_interface_smi"] = smi_result["record"]
    return payload


def run_operator_dashboard(
    upstream_result: Dict[str, Any],
    upstream_refs: Optional[Dict[str, Any]] = None,
    persist_receipts: bool = True,
) -> Dict[str, Any]:
    builder = _resolve_builder()
    base_payload = builder(upstream_result)
    return finalize_operator_dashboard_payload(
        base_payload=base_payload,
        upstream_refs=upstream_refs,
        persist_receipts=persist_receipts,
    )
