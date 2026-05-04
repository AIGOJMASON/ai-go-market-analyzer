# AI_GO/core/visibility/collectors/runtime_collector.py

from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _find_first_json(paths: List[Path]) -> Optional[Dict[str, Any]]:
    for path in paths:
        data = _read_json(path)
        if data is not None:
            return data
    return None


def _safe_recent_json_files(root: Path, limit: int = 10) -> List[Path]:
    if not root.exists() or not root.is_dir():
        return []
    files = [path for path in root.rglob("*.json") if path.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def _detect_current_stage() -> Optional[str]:
    candidates = [
        PROJECT_ROOT / "state" / "runtime" / "status" / "system_status.json",
        PROJECT_ROOT / "state" / "runtime" / "system_status.json",
        PROJECT_ROOT / "state" / "system_visibility" / "SYSTEM_EYES_PACKET.latest.json",
    ]
    data = _find_first_json(candidates)
    if not data:
        return None

    for key in ("current_stage", "stage", "milestone", "system_version"):
        value = data.get(key)
        if value:
            return str(value)

    summary = data.get("summary")
    if isinstance(summary, dict):
        value = summary.get("current_stage")
        if value:
            return str(value)

    return None


def _detect_active_layers() -> List[str]:
    layer_paths = [
        PROJECT_ROOT / "core" / "runtime",
        PROJECT_ROOT / "core" / "continuity",
        PROJECT_ROOT / "core" / "monitoring",
        PROJECT_ROOT / "core" / "visibility",
        PROJECT_ROOT / "RESEARCH_CORE",
        PROJECT_ROOT / "PM_CORE",
        PROJECT_ROOT / "engines",
        PROJECT_ROOT / "child_cores",
    ]
    results: List[str] = []
    for path in layer_paths:
        if path.exists():
            results.append(path.relative_to(PROJECT_ROOT).as_posix())
    return results


def _detect_active_child_cores() -> List[str]:
    registry_candidates = [
        PROJECT_ROOT / "PM_CORE" / "state" / "child_core_registry.json",
        PROJECT_ROOT / "child_cores" / "child_core_registry.json",
    ]

    active: List[str] = []

    for path in registry_candidates:
        data = _read_json(path)
        if not isinstance(data, dict):
            continue

        for key in ("child_cores", "cores", "items", "records"):
            records = data.get(key)
            if isinstance(records, list):
                for item in records:
                    if not isinstance(item, dict):
                        continue
                    core_id = item.get("core_id") or item.get("id") or item.get("name")
                    lifecycle = item.get("lifecycle_state") or item.get("state") or item.get("status")
                    if core_id and str(lifecycle).lower() == "active":
                        active.append(str(core_id))
            elif isinstance(records, dict):
                for core_id, item in records.items():
                    if not isinstance(item, dict):
                        continue
                    lifecycle = item.get("lifecycle_state") or item.get("state") or item.get("status")
                    if str(lifecycle).lower() == "active":
                        active.append(str(core_id))

    if active:
        return sorted(set(active))

    child_root = PROJECT_ROOT / "child_cores"
    if not child_root.exists():
        return []

    fallback: List[str] = []
    excluded = {"interfaces", "ingress", "runtime", "output", "review", "watcher"}
    for entry in child_root.iterdir():
        if entry.is_dir() and not entry.name.startswith("_") and entry.name not in excluded:
            fallback.append(entry.name)
    return sorted(fallback)


def _detect_active_api_surfaces() -> List[str]:
    results: List[str] = []
    app_path = PROJECT_ROOT / "app.py"
    if app_path.exists():
        results.append("app.py")

    api_root = PROJECT_ROOT / "api"
    if api_root.exists():
        for path in sorted(api_root.rglob("*.py")):
            if path.name.endswith("_api.py"):
                results.append(path.relative_to(PROJECT_ROOT).as_posix())

    return results


def _detect_last_runtime_state() -> Optional[Dict[str, Any]]:
    candidates = [
        PROJECT_ROOT / "state" / "runtime" / "status" / "system_status.json",
        PROJECT_ROOT / "state" / "runtime" / "system_status.json",
        PROJECT_ROOT / "state" / "monitoring" / "current" / "sentinel_status.json",
    ]
    return _find_first_json(candidates)


def _detect_last_successful_run() -> Optional[Dict[str, Any]]:
    log_path = PROJECT_ROOT / "logs" / "market_analyzer_requests.jsonl"
    if log_path.exists():
        try:
            lines = [line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            for line in reversed(lines):
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                status = str(record.get("status", "")).lower()
                watcher_status = str(record.get("watcher_status", "")).lower()
                if status in {"ok", "success", "passed"} or watcher_status == "passed":
                    return {
                        "run_id": record.get("request_id"),
                        "core_id": record.get("core_id"),
                        "timestamp": record.get("timestamp") or record.get("observed_at"),
                        "status": record.get("status") or record.get("watcher_status"),
                        "summary": record.get("headline") or record.get("event_theme") or "successful logged run",
                    }
        except Exception:
            pass

    receipts_root = PROJECT_ROOT / "receipts"
    for path in _safe_recent_json_files(receipts_root, limit=20):
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        status = str(data.get("status", "")).lower()
        watcher_status = str(data.get("watcher_status", "")).lower()
        if status in {"ok", "success", "passed"} or watcher_status == "passed":
            return {
                "run_id": data.get("request_id") or data.get("case_id") or data.get("receipt_id"),
                "core_id": data.get("core_id"),
                "timestamp": data.get("timestamp") or data.get("generated_at"),
                "status": data.get("status") or data.get("watcher_status"),
                "summary": data.get("headline") or data.get("title") or path.relative_to(PROJECT_ROOT).as_posix(),
            }

    return None


def _detect_runtime_flags() -> Dict[str, Any]:
    return {
        "app_present": (PROJECT_ROOT / "app.py").exists(),
        "api_present": (PROJECT_ROOT / "api").exists(),
        "visibility_present": (PROJECT_ROOT / "core" / "visibility").exists(),
        "child_cores_present": (PROJECT_ROOT / "child_cores").exists(),
    }


def _infer_runtime_status(last_state: Optional[Dict[str, Any]], active_child_cores: List[str], active_api_surfaces: List[str]) -> str:
    if isinstance(last_state, dict):
        for key in ("runtime_status", "status", "health_level", "sentinel_status"):
            value = last_state.get(key)
            if value:
                return str(value)

    if active_child_cores or active_api_surfaces:
        return "active"

    return "unknown"


def collect_runtime_view() -> Dict[str, Any]:
    active_child_cores = _detect_active_child_cores()
    active_api_surfaces = _detect_active_api_surfaces()
    last_state = _detect_last_runtime_state()

    return {
        "runtime_status": _infer_runtime_status(last_state, active_child_cores, active_api_surfaces),
        "current_stage": _detect_current_stage(),
        "active_layers": _detect_active_layers(),
        "active_child_cores": active_child_cores,
        "active_api_surfaces": active_api_surfaces,
        "last_route_mode": (last_state or {}).get("route_mode"),
        "last_execution_mode": (last_state or {}).get("mode"),
        "last_successful_run": _detect_last_successful_run(),
        "runtime_flags": _detect_runtime_flags(),
        "open_targets": [f"child_core:{core_id}" for core_id in active_child_cores],
    }