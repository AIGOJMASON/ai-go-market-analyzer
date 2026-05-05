# AI_GO/core/visibility/normalizers/summary_normalizer.py

from __future__ import annotations

from typing import Any, Dict


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def build_summary(runtime: Dict[str, Any], watcher: Dict[str, Any], smi: Dict[str, Any]) -> Dict[str, Any]:
    runtime_status = str(runtime.get("runtime_status") or "unknown").lower()

    watcher_failures = _safe_int(watcher.get("fail_count", 0))
    unresolved_count = _safe_int(smi.get("unresolved_queue", {}).get("count", 0))
    quarantine_count = _safe_int(watcher.get("quarantine_indicators", {}).get("count", 0))
    active_child_core_count = len(runtime.get("active_child_cores", []))

    if watcher_failures > 0 or quarantine_count > 0:
        system_status = "degraded"
    elif unresolved_count > 0:
        system_status = "warning"
    elif runtime_status in {"active", "initializing", "healthy"}:
        system_status = "stable"
    else:
        system_status = "unknown"

    last_successful_run = runtime.get("last_successful_run") or {}
    most_recent_success_path = None
    if isinstance(last_successful_run, dict):
        core_id = last_successful_run.get("core_id")
        run_id = last_successful_run.get("run_id")
        if core_id and run_id:
            most_recent_success_path = f"{core_id}:{run_id}"
        elif core_id:
            most_recent_success_path = str(core_id)
        elif run_id:
            most_recent_success_path = str(run_id)

    top_pressure_class = smi.get("continuity_pressure", {}).get("primary_driver")

    return {
        "current_stage": runtime.get("current_stage"),
        "system_status": system_status,
        "active_child_core_count": active_child_core_count,
        "recent_failure_count": watcher_failures,
        "recent_watcher_failures": watcher_failures,
        "recent_unresolved_count": unresolved_count,
        "recent_quarantine_count": quarantine_count,
        "top_pressure_class": top_pressure_class,
        "most_recent_success_path": most_recent_success_path,
    }