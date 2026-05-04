from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter


router = APIRouter(prefix="/system", tags=["system-state"])

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"

SYSTEM_CYCLE_STATUS_PATH = STATE / "system_cycle" / "current" / "system_cycle_status.json"
SYSTEM_EYES_PACKET_PATH = STATE / "system_visibility" / "SYSTEM_EYES_PACKET.latest.json"
CONTINUITY_WEIGHTING_RECORD_PATH = (
    STATE / "continuity_weighting" / "current" / "continuity_weighting_record.json"
)
CONTINUITY_WEIGHTING_REFINEMENT_PACKET_PATH = (
    STATE / "refinement" / "current" / "continuity_weighting_refinement_packet.json"
)
PM_REFINEMENT_INTAKE_RECORD_PATH = (
    STATE / "pm_refinement" / "current" / "pm_refinement_intake_record.json"
)
LIVE_TRIGGER_STATE_PATH = STATE / "live_trigger" / "current" / "live_trigger_state.json"
LATEST_LIVE_TRIGGER_RESPONSE_PATH = (
    STATE / "live_trigger" / "current" / "latest_live_trigger_response.json"
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _artifact_meta(path: Path) -> Dict[str, Any]:
    exists = path.exists()
    if not exists:
        return {
            "exists": False,
            "modified_at": None,
            "size_bytes": None,
            "path": str(path),
        }

    stat = path.stat()
    modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    return {
        "exists": True,
        "modified_at": modified_at.isoformat(),
        "size_bytes": stat.st_size,
        "path": str(path),
    }


def _artifact_entry(path: Path) -> Dict[str, Any]:
    return {
        "meta": _artifact_meta(path),
        "payload": _safe_read_json(path),
    }


def _normalize_live_trigger_state(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "status": "missing",
            "last_request_id": None,
            "last_triggered_at": None,
            "total_triggers": 0,
            "total_successes": 0,
            "total_failures": 0,
            "last_http_status": None,
            "last_target_url": None,
        }

    return {
        "status": payload.get("last_status", "unknown"),
        "last_request_id": payload.get("last_request_id"),
        "last_triggered_at": payload.get("last_triggered_at"),
        "total_triggers": payload.get("total_triggers", 0),
        "total_successes": payload.get("total_successes", 0),
        "total_failures": payload.get("total_failures", 0),
        "last_http_status": payload.get("last_http_status"),
        "last_target_url": payload.get("last_target_url"),
    }


def _build_artifacts() -> Dict[str, Any]:
    return {
        "system_cycle_status": _artifact_entry(SYSTEM_CYCLE_STATUS_PATH),
        "system_eyes_packet": _artifact_entry(SYSTEM_EYES_PACKET_PATH),
        "continuity_weighting_record": _artifact_entry(CONTINUITY_WEIGHTING_RECORD_PATH),
        "continuity_weighting_refinement_packet": _artifact_entry(
            CONTINUITY_WEIGHTING_REFINEMENT_PACKET_PATH
        ),
        "pm_refinement_intake_record": _artifact_entry(PM_REFINEMENT_INTAKE_RECORD_PATH),
        "live_trigger_state": _artifact_entry(LIVE_TRIGGER_STATE_PATH),
        "latest_live_trigger_response": _artifact_entry(LATEST_LIVE_TRIGGER_RESPONSE_PATH),
    }


def _build_summary_payload() -> Dict[str, Any]:
    artifacts = _build_artifacts()

    cycle_payload = artifacts["system_cycle_status"]["payload"] or {}
    eyes_payload = artifacts["system_eyes_packet"]["payload"] or {}
    eyes_summary = eyes_payload.get("summary", {}) if isinstance(eyes_payload.get("summary"), dict) else {}
    runtime_view = eyes_payload.get("runtime_view", {}) if isinstance(eyes_payload.get("runtime_view"), dict) else {}
    smi_view = eyes_payload.get("smi_view", {}) if isinstance(eyes_payload.get("smi_view"), dict) else {}
    inventory_view = eyes_payload.get("inventory_view", {}) if isinstance(eyes_payload.get("inventory_view"), dict) else {}

    continuity_pressure = smi_view.get("continuity_pressure", {})
    if not isinstance(continuity_pressure, dict):
        continuity_pressure = {}

    active_child_cores = runtime_view.get("active_child_cores", [])
    if not isinstance(active_child_cores, list):
        active_child_cores = []

    step_statuses = cycle_payload.get("step_statuses", {})
    if not isinstance(step_statuses, dict):
        step_statuses = {}

    live_trigger_summary = _normalize_live_trigger_state(artifacts["live_trigger_state"]["payload"])

    return {
        "generated_at": _utc_now_iso(),
        "latest_cycle_id": cycle_payload.get("latest_cycle_id"),
        "latest_cycle_status": cycle_payload.get("latest_status"),
        "latest_started_at": cycle_payload.get("latest_started_at"),
        "latest_ended_at": cycle_payload.get("latest_ended_at"),
        "eyes_generated_at": eyes_payload.get("generated_at"),
        "system_status": eyes_summary.get("system_status", "unknown"),
        "runtime_status": runtime_view.get("runtime_status", "unknown"),
        "current_stage": runtime_view.get("current_stage"),
        "continuity_status": smi_view.get("continuity_status", "unknown"),
        "continuity_pressure": continuity_pressure.get("level", "unknown"),
        "active_child_core_count": eyes_summary.get("active_child_core_count", len(active_child_cores)),
        "active_child_cores": active_child_cores,
        "recent_failure_count": eyes_summary.get("recent_failure_count", 0),
        "recent_watcher_failures": eyes_summary.get("recent_watcher_failures", 0),
        "step_statuses": step_statuses,
        "live_trigger_status": live_trigger_summary["status"],
        "live_trigger_last_request_id": live_trigger_summary["last_request_id"],
        "live_trigger_last_triggered_at": live_trigger_summary["last_triggered_at"],
        "live_trigger_total_triggers": live_trigger_summary["total_triggers"],
        "live_trigger_total_successes": live_trigger_summary["total_successes"],
        "live_trigger_total_failures": live_trigger_summary["total_failures"],
        "live_trigger_last_http_status": live_trigger_summary["last_http_status"],
        "live_trigger_last_target_url": live_trigger_summary["last_target_url"],
        "inventory_child_cores_present": inventory_view.get("child_cores_present", []),
    }


@router.get("/health")
def system_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "system_state_api",
        "generated_at": _utc_now_iso(),
    }


@router.get("/summary")
def system_summary() -> Dict[str, Any]:
    return _build_summary_payload()


@router.get("/state")
def system_state() -> Dict[str, Any]:
    artifacts = _build_artifacts()
    return {
        "generated_at": _utc_now_iso(),
        "summary": _build_summary_payload(),
        "artifacts": artifacts,
    }