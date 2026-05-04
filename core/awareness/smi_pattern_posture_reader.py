
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from AI_GO.core.state_runtime.state_paths import project_root, state_root


SMI_PATTERN_POSTURE_READER_VERSION = "v1.0"

PM_STATE_CURRENT_PATH = project_root() / "PM_CORE" / "state" / "current"
PM_CONTINUITY_STATE_PATH = PM_STATE_CURRENT_PATH / "pm_continuity_state.json"
PM_CHANGE_LEDGER_PATH = PM_STATE_CURRENT_PATH / "pm_change_ledger.json"
PM_UNRESOLVED_QUEUE_PATH = PM_STATE_CURRENT_PATH / "pm_unresolved_queue.json"

SYSTEM_SMI_ROOT = state_root() / "system_smi"
SYSTEM_SMI_LATEST_PATH = SYSTEM_SMI_ROOT / "latest_system_smi_record.json"
SYSTEM_SMI_HISTORY_PATH = SYSTEM_SMI_ROOT / "system_smi_history.jsonl"


FORBIDDEN_AUTHORITY_FLAGS = {
    "can_execute",
    "can_mutate_state",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "execution_allowed",
    "mutation_allowed",
    "may_execute",
    "may_mutate_state",
    "may_override_governance",
    "may_change_execution_gate",
    "may_change_watcher",
    "may_change_state",
    "may_write_decisions",
    "may_dispatch_actions",
    "may_activate_child_cores",
    "can_route_work",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return _safe_dict(payload)
    except Exception:
        return {}


def _load_jsonl(path: Path, limit: int = 25) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    for line in lines[-max(1, int(limit)):]:
        clean = line.strip()
        if not clean:
            continue

        try:
            payload = json.loads(clean)
        except Exception:
            continue

        if isinstance(payload, dict):
            records.append(payload)

    return records


def _extract_pm_signals(
    *,
    pm_state: Dict[str, Any],
    pm_change_ledger: Dict[str, Any],
    pm_unresolved_queue: Dict[str, Any],
) -> List[Dict[str, Any]]:
    signals: List[Dict[str, Any]] = []

    posture = _safe_str(pm_state.get("posture"))
    if posture:
        signals.append(
            {
                "signal_type": "pm_continuity_posture",
                "value": posture,
                "source": "pm_continuity_state",
            }
        )

    for signal in _safe_list(pm_state.get("signals")):
        if isinstance(signal, dict):
            signals.append(
                {
                    "signal_type": _safe_str(signal.get("signal_type")) or "pm_signal",
                    "value": signal,
                    "source": "pm_continuity_state.signals",
                }
            )

    ledger_items = _safe_list(pm_change_ledger.get("changes")) or _safe_list(
        pm_change_ledger.get("records")
    )
    if ledger_items:
        signals.append(
            {
                "signal_type": "pm_change_ledger_present",
                "value": len(ledger_items),
                "source": "pm_change_ledger",
            }
        )

    unresolved_items = _safe_list(pm_unresolved_queue.get("items")) or _safe_list(
        pm_unresolved_queue.get("queue")
    )
    if unresolved_items:
        signals.append(
            {
                "signal_type": "pm_unresolved_queue_present",
                "value": len(unresolved_items),
                "source": "pm_unresolved_queue",
            }
        )

    return signals


def _extract_system_smi_signals(
    *,
    latest_record: Dict[str, Any],
    history: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    signals: List[Dict[str, Any]] = []

    latest_artifact_type = _safe_str(latest_record.get("artifact_type"))
    if latest_artifact_type:
        signals.append(
            {
                "signal_type": "latest_system_smi_artifact",
                "value": latest_artifact_type,
                "source": "system_smi_latest",
            }
        )

    system_brain_signal = _safe_dict(latest_record.get("system_brain_signal"))
    if system_brain_signal:
        signals.append(
            {
                "signal_type": "system_brain_signal",
                "value": system_brain_signal,
                "source": "system_smi_latest.system_brain_signal",
            }
        )

    continuity = _safe_dict(latest_record.get("continuity"))
    for key in ("child_core_id", "project_id", "phase_id", "interpretation_class"):
        value = _safe_str(continuity.get(key))
        if value:
            signals.append(
                {
                    "signal_type": f"latest_{key}",
                    "value": value,
                    "source": "system_smi_latest.continuity",
                }
            )

    if history:
        signals.append(
            {
                "signal_type": "system_smi_history_present",
                "value": len(history),
                "source": "system_smi_history",
            }
        )

    return signals


def _count_history_values(
    history: List[Dict[str, Any]],
    field_name: str,
) -> Dict[str, int]:
    counts: Dict[str, int] = {}

    for record in history:
        continuity = _safe_dict(record.get("continuity"))
        value = _safe_str(continuity.get(field_name))
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1

    return counts


def _build_pattern_signals(
    *,
    pm_signals: List[Dict[str, Any]],
    system_signals: List[Dict[str, Any]],
    history: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    pattern_signals: List[Dict[str, Any]] = []

    if not pm_signals and not system_signals and not history:
        pattern_signals.append(
            {
                "pattern_type": "cold_start",
                "severity": "info",
                "summary": "No continuity pattern is available yet.",
                "advisory_only": True,
            }
        )
        return pattern_signals

    if history:
        pattern_signals.append(
            {
                "pattern_type": "continuity_history_available",
                "severity": "info",
                "count": len(history),
                "summary": "System SMI history is available for posture reading.",
                "advisory_only": True,
            }
        )

    for field_name in ("child_core_id", "project_id", "phase_id", "interpretation_class"):
        counts = _count_history_values(history, field_name)
        for value, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            if count >= 2:
                pattern_signals.append(
                    {
                        "pattern_type": f"recurring_{field_name}",
                        "severity": "observe",
                        "value": value,
                        "count": count,
                        "summary": f"Recurring {field_name} observed across SMI history.",
                        "advisory_only": True,
                    }
                )

    unresolved_signal = any(
        signal.get("signal_type") == "pm_unresolved_queue_present"
        for signal in pm_signals
    )
    if unresolved_signal:
        pattern_signals.append(
            {
                "pattern_type": "unresolved_pm_queue_present",
                "severity": "caution",
                "summary": "PM continuity contains unresolved queued items.",
                "advisory_only": True,
            }
        )

    return pattern_signals


def _derive_posture(pattern_signals: List[Dict[str, Any]]) -> str:
    if not pattern_signals:
        return "stable"

    pattern_types = {_safe_str(signal.get("pattern_type")) for signal in pattern_signals}
    severities = {_safe_str(signal.get("severity")) for signal in pattern_signals}

    if "unresolved_pm_queue_present" in pattern_types:
        return "cautious"

    if "cold_start" in pattern_types:
        return "cold_start"

    if "caution" in severities:
        return "cautious"

    if any(pattern_type.startswith("recurring_") for pattern_type in pattern_types):
        return "pattern_observed"

    return "stable_observed"


def _derive_plain_summary(
    posture: str,
    pattern_signals: List[Dict[str, Any]],
) -> str:
    if posture == "cold_start":
        return "System posture cannot be inferred yet because continuity history is empty."

    if posture == "cautious":
        return "System posture is cautious because unresolved or repeated continuity pressure is visible."

    if posture == "pattern_observed":
        return "System posture shows recurring continuity patterns. This is advisory context only."

    return "System posture appears stable from available continuity records."


def _authority_block() -> Dict[str, Any]:
    return {
        "mode": "advisory_only",
        "can_execute": False,
        "can_mutate_state": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_route_work": False,
        "execution_allowed": False,
        "mutation_allowed": False,
    }


def _use_policy_block() -> Dict[str, Any]:
    return {
        "operator_may_read": True,
        "pm_may_read": True,
        "system_brain_may_read": True,
        "may_display_in_dashboard": True,
        "may_change_execution_gate": False,
        "may_change_watcher": False,
        "may_change_state": False,
        "may_write_decisions": False,
        "may_dispatch_actions": False,
        "may_activate_child_cores": False,
    }


def _find_authority_violations(packet: Dict[str, Any]) -> List[str]:
    violations: List[str] = []

    for block_name in ("authority", "use_policy"):
        block = _safe_dict(packet.get(block_name))
        for key, value in block.items():
            if key in FORBIDDEN_AUTHORITY_FLAGS and value is True:
                violations.append(f"{block_name}.{key}")

    return violations


def build_smi_pattern_posture_packet(
    *,
    pm_continuity_state: Optional[Dict[str, Any]] = None,
    pm_change_ledger: Optional[Dict[str, Any]] = None,
    pm_unresolved_queue: Optional[Dict[str, Any]] = None,
    system_smi_latest: Optional[Dict[str, Any]] = None,
    system_smi_history: Optional[List[Dict[str, Any]]] = None,
    history_limit: int = 25,
) -> Dict[str, Any]:
    pm_state = (
        _safe_dict(pm_continuity_state)
        if pm_continuity_state is not None
        else _load_json(PM_CONTINUITY_STATE_PATH)
    )
    pm_ledger = (
        _safe_dict(pm_change_ledger)
        if pm_change_ledger is not None
        else _load_json(PM_CHANGE_LEDGER_PATH)
    )
    pm_unresolved = (
        _safe_dict(pm_unresolved_queue)
        if pm_unresolved_queue is not None
        else _load_json(PM_UNRESOLVED_QUEUE_PATH)
    )

    latest_smi = (
        _safe_dict(system_smi_latest)
        if system_smi_latest is not None
        else _load_json(SYSTEM_SMI_LATEST_PATH)
    )
    smi_history = (
        _safe_list(system_smi_history)
        if system_smi_history is not None
        else _load_jsonl(SYSTEM_SMI_HISTORY_PATH, limit=history_limit)
    )

    pm_signals = _extract_pm_signals(
        pm_state=pm_state,
        pm_change_ledger=pm_ledger,
        pm_unresolved_queue=pm_unresolved,
    )
    system_signals = _extract_system_smi_signals(
        latest_record=latest_smi,
        history=smi_history,
    )
    pattern_signals = _build_pattern_signals(
        pm_signals=pm_signals,
        system_signals=system_signals,
        history=smi_history,
    )

    posture = _derive_posture(pattern_signals)

    packet: Dict[str, Any] = {
        "status": "ok",
        "artifact_type": "smi_pattern_posture_packet",
        "artifact_version": SMI_PATTERN_POSTURE_READER_VERSION,
        "generated_at": _utc_now_iso(),
        "sealed": True,
        "authority": _authority_block(),
        "use_policy": _use_policy_block(),
        "source_surfaces": {
            "pm_continuity_state": str(PM_CONTINUITY_STATE_PATH),
            "pm_change_ledger": str(PM_CHANGE_LEDGER_PATH),
            "pm_unresolved_queue": str(PM_UNRESOLVED_QUEUE_PATH),
            "system_smi_latest": str(SYSTEM_SMI_LATEST_PATH),
            "system_smi_history": str(SYSTEM_SMI_HISTORY_PATH),
        },
        "source_status": {
            "pm_continuity_state_present": bool(pm_state),
            "pm_change_ledger_present": bool(pm_ledger),
            "pm_unresolved_queue_present": bool(pm_unresolved),
            "system_smi_latest_present": bool(latest_smi),
            "system_smi_history_count": len(smi_history),
        },
        "summary": {
            "posture": posture,
            "plain_summary": _derive_plain_summary(posture, pattern_signals),
            "pattern_signal_count": len(pattern_signals),
            "pm_signal_count": len(pm_signals),
            "system_smi_signal_count": len(system_signals),
        },
        "pattern_signals": pattern_signals,
        "pm_signals": pm_signals,
        "system_smi_signals": system_signals,
    }

    authority_violations = _find_authority_violations(packet)
    packet["validation"] = {
        "valid": not authority_violations,
        "authority_violations": authority_violations,
    }

    return packet


def summarize_smi_pattern_posture(packet: Dict[str, Any]) -> Dict[str, Any]:
    safe_packet = _safe_dict(packet)
    summary = _safe_dict(safe_packet.get("summary"))

    return {
        "status": safe_packet.get("status", "unknown"),
        "posture": summary.get("posture", "unknown"),
        "plain_summary": summary.get("plain_summary", ""),
        "pattern_signal_count": summary.get("pattern_signal_count", 0),
        "advisory_only": True,
        "execution_allowed": False,
        "mutation_allowed": False,
    }

