# AI_GO/api/pre_interface_watcher.py

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ARTIFACT_TYPE = "pre_interface_watcher_receipt"
SURFACE_NAME = "market_analyzer_v1.system_view"
REQUIRED_PANELS = ("case_panel", "governance_panel")
OPTIONAL_PANEL_KEYS = (
    "market_panel",
    "runtime_panel",
    "candidate_panel",
    "recommendation_panel",
    "rejection_panel",
    "refinement_panel",
    "external_memory_panel",
    "pm_workflow_panel",
)
FORBIDDEN_KEYS = {
    "raw_packet",
    "raw_request",
    "internal_state",
    "debug_trace",
    "runtime_context",
    "policy_override",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    micros = f"{datetime.now(timezone.utc).microsecond:06d}"
    return f"{prefix}_{stamp}_{micros}"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _receipt_dir() -> Path:
    return _project_root() / "receipts" / "market_analyzer_v1" / "pre_interface_watcher"


def _is_panel_dict(value: Any) -> bool:
    return isinstance(value, dict)


def _contains_forbidden_key(payload: Dict[str, Any]) -> Optional[str]:
    for key in payload.keys():
        if key in FORBIDDEN_KEYS or key.startswith("_internal"):
            return key
    return None


def _validate_required_panels(payload: Dict[str, Any], failures: List[str]) -> None:
    for key in REQUIRED_PANELS:
        if key not in payload:
            failures.append(f"missing_required_panel:{key}")
            continue
        if not _is_panel_dict(payload[key]):
            failures.append(f"invalid_required_panel_shape:{key}")


def _validate_optional_panels(payload: Dict[str, Any], failures: List[str]) -> None:
    for key in OPTIONAL_PANEL_KEYS:
        if key in payload and not _is_panel_dict(payload[key]):
            failures.append(f"invalid_optional_panel_shape:{key}")


def _validate_advisory_posture(payload: Dict[str, Any], failures: List[str]) -> None:
    if payload.get("execution_allowed") is not False:
        failures.append("execution_allowed_must_be_false")
    mode = payload.get("mode")
    if mode is not None and mode != "advisory":
        failures.append("mode_must_be_advisory")
    dashboard_type = payload.get("dashboard_type")
    if dashboard_type is not None and dashboard_type != "market_analyzer_v1_operator_dashboard":
        failures.append("invalid_dashboard_type")


def _validate_governance_panel(payload: Dict[str, Any], failures: List[str]) -> None:
    governance = payload.get("governance_panel")
    if not isinstance(governance, dict):
        return
    if "watcher_passed" in governance and not isinstance(governance["watcher_passed"], bool):
        failures.append("governance_panel.watcher_passed_must_be_bool")
    if "approval_required" in governance and not isinstance(governance["approval_required"], bool):
        failures.append("governance_panel.approval_required_must_be_bool")


def _validate_recommendation_panel(payload: Dict[str, Any], failures: List[str]) -> None:
    recommendation = payload.get("recommendation_panel")
    if recommendation is None:
        return
    if not isinstance(recommendation, dict):
        failures.append("recommendation_panel_must_be_dict")
        return

    if "count" in recommendation and not isinstance(recommendation["count"], int):
        failures.append("recommendation_panel.count_must_be_int")

    items = recommendation.get("items")
    if items is not None and not isinstance(items, list):
        failures.append("recommendation_panel.items_must_be_list")

    if isinstance(items, list):
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                failures.append(f"recommendation_panel.items[{index}]_must_be_dict")


def _validate_additive_panels(payload: Dict[str, Any], failures: List[str]) -> None:
    for key in ("refinement_panel", "external_memory_panel", "pm_workflow_panel"):
        if key in payload and not isinstance(payload[key], dict):
            failures.append(f"{key}_must_be_dict")


def _collect_visible_panels(payload: Dict[str, Any]) -> List[str]:
    ordered = []
    for key in (
        "case_panel",
        "market_panel",
        "runtime_panel",
        "candidate_panel",
        "recommendation_panel",
        "governance_panel",
        "rejection_panel",
        "refinement_panel",
        "external_memory_panel",
        "pm_workflow_panel",
    ):
        if key in payload and isinstance(payload[key], dict):
            ordered.append(key)
    return ordered


def build_pre_interface_watcher_receipt(
    payload: Dict[str, Any],
    upstream_refs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    failures: List[str] = []

    if not isinstance(payload, dict):
        failures.append("payload_must_be_dict")
        payload = {}

    forbidden_key = _contains_forbidden_key(payload)
    if forbidden_key is not None:
        failures.append(f"forbidden_key_present:{forbidden_key}")

    _validate_required_panels(payload, failures)
    _validate_optional_panels(payload, failures)
    _validate_advisory_posture(payload, failures)
    _validate_governance_panel(payload, failures)
    _validate_recommendation_panel(payload, failures)
    _validate_additive_panels(payload, failures)

    status = "passed" if not failures else "failed"

    receipt: Dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "receipt_id": _new_id("piw"),
        "case_id": payload.get("case_panel", {}).get("case_id"),
        "request_id": payload.get("request_id") or payload.get("case_panel", {}).get("case_id"),
        "status": status,
        "surface": SURFACE_NAME,
        "timestamp": _utc_now(),
        "visible_panels": _collect_visible_panels(payload),
        "checks": {
            "required_sections": all(not item.startswith("missing_required_panel") and not item.startswith("invalid_required_panel_shape") for item in failures),
            "advisory_only": "execution_allowed_must_be_false" not in failures and "mode_must_be_advisory" not in failures,
            "internal_leakage_absent": not any(item.startswith("forbidden_key_present") for item in failures),
            "governance_panel_valid": not any(item.startswith("governance_panel") for item in failures),
            "recommendation_panel_valid": not any(item.startswith("recommendation_panel") for item in failures),
        },
        "failures": failures,
        "upstream_refs": deepcopy(upstream_refs or {}),
    }
    return receipt


def persist_pre_interface_watcher_receipt(receipt: Dict[str, Any]) -> str:
    directory = _receipt_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{receipt['receipt_id']}.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)


def run_pre_interface_watcher(
    payload: Dict[str, Any],
    upstream_refs: Optional[Dict[str, Any]] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    receipt = build_pre_interface_watcher_receipt(payload=payload, upstream_refs=upstream_refs)
    path = persist_pre_interface_watcher_receipt(receipt) if persist else None
    return {
        "receipt": receipt,
        "path": path,
    }