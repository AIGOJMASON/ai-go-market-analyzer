from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


MEMORY_INTEGRATION_VERSION = "northstar_memory_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "memory_integration",
        "mutation_class": "memory_persistence",
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": True,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_operational_state": False,
        "can_mutate_workflow_state": False,
        "can_mutate_project_truth": False,
        "can_mutate_pm_authority": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_override_state_authority": False,
        "can_override_cross_core_integrity": False,
    }


def build_memory_integration_record(
    *,
    source: str,
    memory_type: str,
    inputs: Dict[str, Any] | None = None,
    signals: List[Dict[str, Any]] | None = None,
    summary: str = "",
    project_id: str = "",
    phase_id: str = "",
) -> Dict[str, Any]:
    clean_source = _safe_str(source)
    clean_memory_type = _safe_str(memory_type)

    if not clean_source:
        raise ValueError("source is required")

    if not clean_memory_type:
        raise ValueError("memory_type is required")

    return {
        "status": "recorded",
        "artifact_type": "memory_integration_record",
        "artifact_version": MEMORY_INTEGRATION_VERSION,
        "recorded_at": _utc_now_iso(),
        "source": clean_source,
        "memory_type": clean_memory_type,
        "project_id": _safe_str(project_id),
        "phase_id": _safe_str(phase_id),
        "summary": _safe_str(summary),
        "inputs": inputs or {},
        "signals": _safe_list(signals),
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def integrate_memory_signal(
    *,
    source: str,
    memory_type: str,
    inputs: Dict[str, Any] | None = None,
    signals: List[Dict[str, Any]] | None = None,
    summary: str = "",
    project_id: str = "",
    phase_id: str = "",
) -> Dict[str, Any]:
    """
    Build one advisory memory integration record.

    Northstar rule:
    - Memory may preserve context.
    - Memory may not become hidden authority.
    - Memory may not execute, mutate workflow truth, or override governance.
    """
    return build_memory_integration_record(
        source=source,
        memory_type=memory_type,
        inputs=inputs,
        signals=signals,
        summary=summary,
        project_id=project_id,
        phase_id=phase_id,
    )


def safely_integrate_memory_signal(
    *,
    source: str,
    memory_type: str,
    inputs: Dict[str, Any] | None = None,
    signals: List[Dict[str, Any]] | None = None,
    summary: str = "",
    project_id: str = "",
    phase_id: str = "",
) -> Dict[str, Any]:
    try:
        return integrate_memory_signal(
            source=source,
            memory_type=memory_type,
            inputs=inputs,
            signals=signals,
            summary=summary,
            project_id=project_id,
            phase_id=phase_id,
        )
    except Exception as exc:
        return {
            "status": "failed",
            "artifact_type": "memory_integration_record",
            "artifact_version": MEMORY_INTEGRATION_VERSION,
            "recorded_at": _utc_now_iso(),
            "source": _safe_str(source),
            "memory_type": _safe_str(memory_type),
            "project_id": _safe_str(project_id),
            "phase_id": _safe_str(phase_id),
            "classification": _classification_block(),
            "authority": _authority_block(),
            "error": f"{type(exc).__name__}: {exc}",
            "sealed": True,
        }


def _load_existing_records() -> List[Dict[str, Any]]:
    """
    Compatibility read surface.

    Current Northstar memory integration is advisory/build-only in this file,
    so there may be no persisted memory index yet. Return an empty list safely.
    """
    return []


def load_system_memory_index(limit: int = 1000) -> Dict[str, Any]:
    """
    Backward-compatible read surface for awareness modules.

    Read-only. Does not mutate state.
    """
    records = _load_existing_records()
    safe_limit = max(1, min(_safe_int(limit, 1000), 1000))
    bounded_records = records[-safe_limit:]

    records_by_id: Dict[str, Dict[str, Any]] = {}

    for index, record in enumerate(bounded_records):
        if not isinstance(record, dict):
            continue

        record_id = _safe_str(
            record.get("memory_id")
            or record.get("record_id")
            or record.get("governance_packet_id")
            or f"memory_record_{index}"
        )
        records_by_id[record_id] = dict(record)

    return {
        "status": "ok",
        "artifact_type": "system_memory_index",
        "artifact_version": MEMORY_INTEGRATION_VERSION,
        "visibility_mode": "read_only",
        "authority": _authority_block(),
        "classification": _classification_block(),
        "record_count": len(bounded_records),
        "total_record_count": len(records),
        "records": bounded_records,
        "records_by_id": records_by_id,
        "sealed": True,
    }


def query_system_memory(
    *,
    query: str = "",
    limit: int = 25,
) -> Dict[str, Any]:
    """
    Backward-compatible advisory query surface.

    Read-only. Does not mutate state.
    """
    index = load_system_memory_index(limit=limit)
    clean_query = _safe_str(query).lower()

    records = _safe_list(index.get("records"))
    if clean_query:
        records = [
            record
            for record in records
            if isinstance(record, dict)
            and clean_query
            in " ".join(
                [
                    _safe_str(record.get("source")),
                    _safe_str(record.get("memory_type")),
                    _safe_str(record.get("summary")),
                    _safe_str(record.get("project_id")),
                    _safe_str(record.get("phase_id")),
                ]
            ).lower()
        ]

    safe_limit = max(1, min(_safe_int(limit, 25), 1000))
    records = records[-safe_limit:]

    return {
        "status": "ok",
        "artifact_type": "system_memory_query",
        "artifact_version": MEMORY_INTEGRATION_VERSION,
        "visibility_mode": "read_only",
        "query": _safe_str(query),
        "record_count": len(records),
        "records": records,
        "authority": _authority_block(),
        "classification": _classification_block(),
        "sealed": True,
    }