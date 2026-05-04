from __future__ import annotations

from typing import Any, Dict, List

try:
    from AI_GO.EXTERNAL_MEMORY.authority.memory_authority_guard import (
        apply_memory_authority_guard,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.authority.memory_authority_guard import (
        apply_memory_authority_guard,
    )

from AI_GO.EXTERNAL_MEMORY.retrieval.retrieval_runtime import (
    run_external_memory_retrieval,
)


READ_ONLY_CONTEXT_VERSION = "v5F.2"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _summarize_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    symbols: List[str] = []
    sectors: List[str] = []
    trust_classes: List[str] = []

    for record in records:
        payload_summary = _safe_dict(record.get("payload_summary"))
        symbol = _safe_str(payload_summary.get("symbol"))
        sector = _safe_str(payload_summary.get("sector"))
        trust_class = _safe_str(record.get("trust_class"))

        if symbol:
            symbols.append(symbol)
        if sector:
            sectors.append(sector)
        if trust_class:
            trust_classes.append(trust_class)

    return {
        "record_count": len(records),
        "symbols_seen": sorted(set(symbols)),
        "sectors_seen": sorted(set(sectors)),
        "trust_classes_seen": sorted(set(trust_classes)),
        "pattern_context_available": len(records) > 0,
    }


def build_external_memory_read_only_context(request: Dict[str, Any]) -> Dict[str, Any]:
    retrieval_result = run_external_memory_retrieval(request)

    artifact = _safe_dict(
        retrieval_result.get("artifact")
        or retrieval_result.get("retrieval_artifact")
    )
    receipt = _safe_dict(
        retrieval_result.get("receipt")
        or retrieval_result.get("retrieval_receipt")
    )

    records = _safe_list(artifact.get("records"))

    context = {
        "artifact_type": "external_memory_read_only_context",
        "artifact_version": READ_ONLY_CONTEXT_VERSION,
        "status": retrieval_result.get("status", "failed"),
        "retrieval_status": retrieval_result.get("status", "failed"),
        "request_summary": artifact.get("request_summary", {}),
        "retrieval_receipt_id": receipt.get("receipt_id", ""),
        "matched_count": artifact.get("matched_count", 0),
        "returned_count": artifact.get("returned_count", 0),
        "summary": _summarize_records(records),
        "records": records,
        "advisory_panel": {
            "visible": True,
            "source": "external_memory",
            "mode": "read_only",
            "advisory_only": True,
            "summary": "External Memory returned bounded historical context only.",
            "record_count": len(records),
            "pattern_context_available": len(records) > 0,
            "provenance_refs": [
                {
                    "memory_id": record.get("memory_id"),
                    "qualification_record_id": record.get("qualification_record_id"),
                }
                for record in records
            ],
        },
        "authority": {
            "memory_is_truth": False,
            "memory_is_candidate_signal": True,
            "advisory_only": True,
            "read_only_to_authority_chain": True,
            "can_override_state_authority": False,
            "can_override_canon": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_state": False,
            "can_mutate_operational_state": False,
            "can_mutate_child_core_state": False,
        },
        "limitations": [
            "context_only",
            "does_not_promote_memory",
            "does_not_score_recurrence",
            "does_not_change_recommendations",
            "does_not_change_pm_strategy",
            "does_not_mutate_state",
            "does_not_execute",
        ],
        "sealed": True,
    }

    return apply_memory_authority_guard(context)