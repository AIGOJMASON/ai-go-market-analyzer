# AI_GO/api/pre_interface_smi.py

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ARTIFACT_TYPE = "pre_interface_smi_record"
SURFACE_NAME = "market_analyzer_v1.system_view"
CONTINUITY_KEY = "market_analyzer_v1.interface_exposure"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    micros = f"{datetime.now(timezone.utc).microsecond:06d}"
    return f"{prefix}_{stamp}_{micros}"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _record_dir() -> Path:
    return _project_root() / "receipts" / "market_analyzer_v1" / "pre_interface_smi"


def _collect_visible_panels(payload: Dict[str, Any]) -> List[str]:
    visible: List[str] = []
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
        if isinstance(payload.get(key), dict):
            visible.append(key)
    return visible


def build_pre_interface_smi_record(
    payload: Dict[str, Any],
    watcher_receipt: Dict[str, Any],
    upstream_refs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload_must_be_dict")
    if not isinstance(watcher_receipt, dict):
        raise ValueError("watcher_receipt_must_be_dict")
    if watcher_receipt.get("artifact_type") != "pre_interface_watcher_receipt":
        raise ValueError("invalid_watcher_receipt_type")
    if watcher_receipt.get("status") != "passed":
        raise ValueError("watcher_receipt_must_be_passed")

    case_panel = payload.get("case_panel", {}) if isinstance(payload.get("case_panel"), dict) else {}
    recommendation_panel = payload.get("recommendation_panel", {}) if isinstance(payload.get("recommendation_panel"), dict) else {}
    visible_panels = _collect_visible_panels(payload)

    recommendation_count = recommendation_panel.get("count")
    if not isinstance(recommendation_count, int):
        items = recommendation_panel.get("items")
        recommendation_count = len(items) if isinstance(items, list) else 0

    record: Dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "record_id": _new_id("pis"),
        "case_id": case_panel.get("case_id"),
        "request_id": payload.get("request_id") or case_panel.get("case_id"),
        "surface": SURFACE_NAME,
        "continuity_key": CONTINUITY_KEY,
        "watcher_receipt_id": watcher_receipt.get("receipt_id"),
        "watcher_status": watcher_receipt.get("status"),
        "timestamp": _utc_now(),
        "exposure_posture": "advisory_only",
        "visible_panels": visible_panels,
        "refinement_visible": "refinement_panel" in visible_panels,
        "external_memory_visible": "external_memory_panel" in visible_panels,
        "pm_workflow_visible": "pm_workflow_panel" in visible_panels,
        "recommendation_count": recommendation_count,
        "rejection_present": "rejection_panel" in visible_panels,
        "upstream_refs": deepcopy(upstream_refs or {}),
    }
    return record


def persist_pre_interface_smi_record(record: Dict[str, Any]) -> str:
    directory = _record_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{record['record_id']}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)


def run_pre_interface_smi(
    payload: Dict[str, Any],
    watcher_receipt: Dict[str, Any],
    upstream_refs: Optional[Dict[str, Any]] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    record = build_pre_interface_smi_record(
        payload=payload,
        watcher_receipt=watcher_receipt,
        upstream_refs=upstream_refs,
    )
    path = persist_pre_interface_smi_record(record) if persist else None
    return {
        "record": record,
        "path": path,
    }
