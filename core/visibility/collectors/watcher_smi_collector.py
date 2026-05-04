# AI_GO/core/visibility/collectors/watcher_smi_collector.py

from __future__ import annotations

from pathlib import Path
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _recent_json_files(root: Path, limit: int = 10) -> List[Path]:
    if not root.exists() or not root.is_dir():
        return []
    files = [path for path in root.rglob("*.json") if path.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def _mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_from_string(value: str) -> Optional[str]:
    if not value:
        return None

    value = str(value)

    patterns = [
        r"(20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)",
        r"(20\d{2}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)",
        r"(20\d{8}T\d{6}Z)",
        r"(20\d{6}T\d{6}Z)",
        r"(20\d{8})",
    ]

    for pattern in patterns:
        match = re.search(pattern, value)
        if not match:
            continue
        raw = match.group(1)

        if re.fullmatch(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", raw):
            return raw

        if re.fullmatch(r"20\d{2}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z", raw):
            return raw.replace("T", "T").replace("-", ":", 2) if False else f"{raw[0:10]}T{raw[11:13]}:{raw[14:16]}:{raw[17:19]}Z"

        if re.fullmatch(r"20\d{6}T\d{6}Z", raw) or re.fullmatch(r"20\d{8}T\d{6}Z", raw):
            date_part = raw[:8]
            time_part = raw[9:15]
            return f"{date_part[0:4]}-{date_part[4:6]}-{date_part[6:8]}T{time_part[0:2]}:{time_part[2:4]}:{time_part[4:6]}Z"

        if re.fullmatch(r"20\d{8}", raw):
            return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}T00:00:00Z"

    return None


def _best_timestamp(data: Dict[str, Any], path: Optional[Path] = None, *extra_values: Any) -> Optional[str]:
    candidate_keys = [
        "timestamp",
        "generated_at",
        "created_at",
        "updated_at",
        "observed_at",
        "event_timestamp",
    ]

    for key in candidate_keys:
        value = data.get(key)
        ts = _timestamp_from_string(str(value)) if value else None
        if ts:
            return ts

    for value in extra_values:
        if value:
            ts = _timestamp_from_string(str(value))
            if ts:
                return ts

    if path is not None:
        ts = _timestamp_from_string(path.name)
        if ts:
            return ts
        return _mtime_iso(path)

    return None


def _extract_record_list(data: Dict[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _normalize_record_dict_map(data: Dict[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for key in keys:
        value = data.get(key)
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                if isinstance(sub_val, dict):
                    item = dict(sub_val)
                    item.setdefault("id", sub_key)
                    results.append(item)
    return results


# ---------------------------------------------------------
# WATCHER
# ---------------------------------------------------------

def _collect_watcher_candidate_files(limit: int = 10) -> List[Path]:
    roots = [
        PROJECT_ROOT / "receipts",
        PROJECT_ROOT / "state" / "monitoring",
        PROJECT_ROOT / "child_cores",
        PROJECT_ROOT / "api",
    ]

    results: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            lowered = path.as_posix().lower()
            if "watcher" in lowered or "validation" in lowered or "closeout" in lowered:
                results.append(path)

    results = sorted(set(results), key=lambda p: p.stat().st_mtime, reverse=True)
    return results[:limit]


def _classify_watcher_status(data: Dict[str, Any], path: Path) -> str:
    for key in ("watcher_status", "validation_status", "closeout_status", "status"):
        value = data.get(key)
        if value:
            lowered = str(value).lower()
            if lowered in {"pass", "passed", "accepted", "ok", "success"}:
                return "pass"
            if lowered in {"fail", "failed", "rejected", "quarantined", "error"}:
                return "fail"

    lowered_path = path.as_posix().lower()
    if "quarantine" in lowered_path or "failed" in lowered_path:
        return "fail"

    return "pass"


def collect_watcher_view(limit: int = 10) -> Dict[str, Any]:
    files = _collect_watcher_candidate_files(limit=limit)

    pass_count = 0
    fail_count = 0
    latest_validations: List[Dict[str, Any]] = []
    failure_classes: List[str] = []
    quarantine_ids: List[str] = []
    closeout_status_summary = {
        "accepted": 0,
        "quarantined": 0,
        "rejected": 0,
    }

    for path in files:
        data = _read_json(path) or {}
        status = _classify_watcher_status(data, path)

        if status == "pass":
            pass_count += 1
        else:
            fail_count += 1

        validation_id = (
            data.get("validation_id")
            or data.get("watcher_validation_id")
            or data.get("closeout_id")
            or data.get("receipt_id")
            or path.stem
        )

        latest_validations.append(
            {
                "validation_id": str(validation_id),
                "timestamp": _best_timestamp(data, path, validation_id),
                "surface": data.get("surface") or data.get("core_id") or path.parent.name,
                "status": status,
                "artifact_type": data.get("artifact_type") or path.parent.name,
                "case_id": data.get("case_id") or data.get("request_id"),
            }
        )

        if status == "fail":
            failure_class = (
                data.get("failure_class")
                or data.get("reason")
                or data.get("closeout_status")
                or data.get("watcher_status")
                or "watcher_failure"
            )
            failure_classes.append(str(failure_class))

            quarantine_id = data.get("closeout_id") or data.get("receipt_id") or data.get("request_id")
            if quarantine_id:
                quarantine_ids.append(str(quarantine_id))

        closeout_status = str(data.get("closeout_status", "")).lower()
        if closeout_status == "accepted":
            closeout_status_summary["accepted"] += 1
        elif closeout_status == "quarantined":
            closeout_status_summary["quarantined"] += 1
        elif closeout_status == "rejected":
            closeout_status_summary["rejected"] += 1

    return {
        "recent_window_size": limit,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "latest_validations": latest_validations,
        "failure_classes": sorted(set(failure_classes)),
        "quarantine_indicators": {
            "count": len(quarantine_ids),
            "latest_ids": quarantine_ids[:5],
        },
        "closeout_status_summary": closeout_status_summary,
    }


# ---------------------------------------------------------
# SMI / CONTINUITY
# ---------------------------------------------------------

def _read_first_existing_json(paths: List[Path]) -> Tuple[Dict[str, Any], Optional[Path]]:
    for path in paths:
        data = _read_json(path)
        if isinstance(data, dict):
            return data, path
    return {}, None


def _collect_smi_candidate_files(limit: int = 25) -> List[Path]:
    roots = [
        PROJECT_ROOT / "state" / "smi",
        PROJECT_ROOT / "PM_CORE" / "state",
        PROJECT_ROOT / "core" / "child_flow",
        PROJECT_ROOT / "child_cores",
    ]

    results: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            lowered = path.as_posix().lower()
            if any(
                token in lowered
                for token in [
                    "smi",
                    "continuity",
                    "change_ledger",
                    "unresolved_queue",
                    "pm_continuity",
                    "pm_change_ledger",
                    "pm_unresolved_queue",
                ]
            ):
                results.append(path)

    results = sorted(set(results), key=lambda p: p.stat().st_mtime, reverse=True)
    return results[:limit]


def _collect_recent_accepted_events(limit: int = 10) -> Tuple[List[Dict[str, Any]], int]:
    candidate_paths = [
        PROJECT_ROOT / "state" / "smi" / "current" / "smi_state.json",
        PROJECT_ROOT / "state" / "smi" / "smi_state.json",
        PROJECT_ROOT / "PM_CORE" / "state" / "current" / "pm_continuity_state.json",
    ]

    continuity_keys = set()
    accepted: List[Dict[str, Any]] = []

    for path in candidate_paths:
        data = _read_json(path)
        if not isinstance(data, dict):
            continue

        record_lists = []
        record_lists.extend(
            _extract_record_list(
                data,
                ["accepted_events", "events", "records", "entries", "continuity_records", "continuity_events"],
            )
        )
        record_lists.extend(
            _normalize_record_dict_map(
                data,
                ["continuity_index", "continuity_records_by_key", "records_by_key"],
            )
        )

        for item in record_lists:
            continuity_key = (
                item.get("continuity_key")
                or item.get("key")
                or item.get("pattern_key")
                or item.get("id")
            )
            if continuity_key:
                continuity_keys.add(str(continuity_key))

            accepted.append(
                {
                    "event_id": item.get("event_id") or item.get("record_id") or item.get("id") or "unknown_event",
                    "timestamp": _best_timestamp(item, path, item.get("event_id"), item.get("record_id"), item.get("id")),
                    "event_class": item.get("event_class") or item.get("type") or item.get("record_type") or "accepted_event",
                    "source_surface": item.get("source_surface") or item.get("source") or item.get("core_id") or path.stem,
                    "continuity_key": continuity_key,
                }
            )

    accepted.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
    return accepted[:limit], len(continuity_keys)


def _collect_recent_change_ledger_entries(limit: int = 10) -> List[Dict[str, Any]]:
    direct_paths = [
        PROJECT_ROOT / "state" / "smi" / "current" / "change_ledger.json",
        PROJECT_ROOT / "PM_CORE" / "state" / "current" / "pm_change_ledger.json",
    ]

    entries: List[Dict[str, Any]] = []

    for path in direct_paths:
        data = _read_json(path)
        if not isinstance(data, dict):
            continue

        record_lists = _extract_record_list(data, ["entries", "records", "items"])
        if not record_lists:
            record_lists = [data]

        for item in record_lists:
            entries.append(
                {
                    "ledger_id": item.get("ledger_id") or item.get("id") or path.stem.upper(),
                    "timestamp": _best_timestamp(item, path, item.get("ledger_id"), item.get("id")),
                    "change_class": item.get("change_class") or item.get("type") or "change",
                    "summary": item.get("summary") or item.get("note") or item.get("description") or "change_ledger_entry",
                }
            )

    ledger_dirs = [
        PROJECT_ROOT / "state" / "smi" / "current" / "change_ledger",
    ]

    for directory in ledger_dirs:
        for path in _recent_json_files(directory, limit=limit):
            data = _read_json(path)
            if not isinstance(data, dict):
                continue
            entries.append(
                {
                    "ledger_id": data.get("ledger_id") or data.get("id") or path.stem,
                    "timestamp": _best_timestamp(data, path, path.stem),
                    "change_class": data.get("change_class") or data.get("type") or "change",
                    "summary": data.get("summary") or data.get("note") or data.get("description") or "change_ledger_entry",
                }
            )

    entries.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
    return entries[:limit]


def _collect_unresolved_entries(limit: int = 10) -> Tuple[List[Dict[str, Any]], List[str], Optional[str]]:
    candidate_paths = [
        PROJECT_ROOT / "state" / "smi" / "current" / "unresolved_queue.json",
        PROJECT_ROOT / "state" / "smi" / "unresolved" / "unresolved_queue.json",
        PROJECT_ROOT / "PM_CORE" / "state" / "current" / "pm_unresolved_queue.json",
    ]

    unresolved_entries: List[Dict[str, Any]] = []

    for path in candidate_paths:
        data = _read_json(path)
        if not isinstance(data, dict):
            continue

        record_lists = _extract_record_list(data, ["entries", "records", "items", "queue"])
        for item in record_lists:
            unresolved_entries.append(
                {
                    "id": item.get("id") or item.get("event_id") or item.get("record_id") or "unresolved_item",
                    "timestamp": _best_timestamp(item, path, item.get("id"), item.get("event_id")),
                    "class": item.get("class") or item.get("unresolved_class") or item.get("reason") or "unresolved",
                    "summary": item.get("summary") or item.get("note") or item.get("description") or "unresolved_entry",
                    "source_surface": item.get("source_surface") or item.get("source") or path.stem,
                }
            )

    unresolved_entries.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)

    seen_classes: List[str] = []
    timestamps: List[str] = []
    for item in unresolved_entries:
        cls = item.get("class")
        if cls:
            seen_classes.append(str(cls))
        ts = item.get("timestamp")
        if ts:
            timestamps.append(str(ts))

    top_classes = sorted(set(seen_classes))[:5]
    oldest_open_timestamp = sorted(timestamps)[0] if timestamps else None

    return unresolved_entries[:limit], top_classes, oldest_open_timestamp


def _detect_session_markers() -> int:
    candidate_paths = [
        PROJECT_ROOT / "state" / "smi" / "current" / "smi_state.json",
        PROJECT_ROOT / "PM_CORE" / "state" / "current" / "pm_continuity_state.json",
    ]

    count = 0
    for path in candidate_paths:
        data = _read_json(path)
        if not isinstance(data, dict):
            continue

        if isinstance(data.get("sessions"), list):
            count += len(data["sessions"])
        elif data.get("session_id"):
            count += 1
        elif data.get("active_session"):
            count += 1

    return count


def _detect_tracked_threads() -> int:
    candidate_paths = [
        PROJECT_ROOT / "state" / "smi" / "current" / "smi_state.json",
        PROJECT_ROOT / "PM_CORE" / "state" / "current" / "pm_continuity_state.json",
    ]

    total = 0
    for path in candidate_paths:
        data = _read_json(path)
        if not isinstance(data, dict):
            continue

        tracked = data.get("tracked_threads")
        if isinstance(tracked, list):
            total += len(tracked)
        elif isinstance(tracked, dict):
            total += len(tracked)

        continuity_index = data.get("continuity_index")
        if isinstance(continuity_index, dict):
            total += len(continuity_index)

    return total


def collect_smi_view(limit: int = 10) -> Dict[str, Any]:
    recent_accepted_events, continuity_key_count = _collect_recent_accepted_events(limit=limit)
    recent_change_ledger_entries = _collect_recent_change_ledger_entries(limit=limit)
    latest_unresolved_entries, top_classes, oldest_open_timestamp = _collect_unresolved_entries(limit=limit)

    unresolved_count = len(latest_unresolved_entries)

    if unresolved_count >= 10:
        continuity_status = "degraded"
        pressure_level = "high"
    elif unresolved_count > 0:
        continuity_status = "pressured"
        pressure_level = "medium"
    elif recent_accepted_events or recent_change_ledger_entries:
        continuity_status = "healthy"
        pressure_level = "low"
    else:
        continuity_status = "unknown"
        pressure_level = "low"

    return {
        "continuity_status": continuity_status,
        "current_state_summary": {
            "continuity_key_count": continuity_key_count,
            "active_session_markers": _detect_session_markers(),
            "tracked_threads": _detect_tracked_threads(),
        },
        "recent_accepted_events": recent_accepted_events,
        "recent_change_ledger_entries": recent_change_ledger_entries,
        "unresolved_queue": {
            "count": unresolved_count,
            "top_classes": top_classes,
            "oldest_open_timestamp": oldest_open_timestamp,
            "latest_entries": latest_unresolved_entries,
        },
        "continuity_pressure": {
            "level": pressure_level,
            "primary_driver": top_classes[0] if top_classes else None,
        },
    }


def collect_watcher_smi_bundle(limit: int = 10) -> Dict[str, Any]:
    return {
        "watcher": collect_watcher_view(limit=limit),
        "smi": collect_smi_view(limit=limit),
    }