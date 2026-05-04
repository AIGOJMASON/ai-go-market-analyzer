
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.state_runtime.state_paths import state_root


MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "external_memory_retrieval_read"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_mutate_runtime": False,
    "can_write_memory": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "external_memory_read_only",
}


def _memory_path() -> Path:
    return state_root() / "external_memory" / "external_memory_records.json"


def _read_store() -> Dict[str, Any]:
    path = _memory_path()
    if not path.exists():
        return {"records": []}

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"records": []}


def query_memory(
    *,
    query: str = "",
    limit: int = 10,
    core_id: str = "",
    event_theme: str = "",
    symbol: str = "",
) -> Dict[str, Any]:
    store = _read_store()
    records = store.get("records", [])
    if not isinstance(records, list):
        records = []

    clean_query = str(query or "").strip().lower()
    clean_core = str(core_id or "").strip()
    clean_theme = str(event_theme or "").strip()
    clean_symbol = str(symbol or "").strip().upper()

    matches: List[Dict[str, Any]] = []

    for record in records:
        if not isinstance(record, dict):
            continue

        blob = json.dumps(record, ensure_ascii=False).lower()

        if clean_query and clean_query not in blob:
            continue

        if clean_core and str(record.get("core_id", "")).strip() != clean_core:
            continue

        if clean_theme and str(record.get("event_theme", "")).strip() != clean_theme:
            continue

        if clean_symbol and str(record.get("symbol", "")).strip().upper() != clean_symbol:
            continue

        matches.append(dict(record))

    safe_limit = max(1, min(int(limit or 10), 100))

    return {
        "artifact_type": "external_memory_retrieval_result",
        "status": "ok",
        "query": query,
        "match_count": len(matches),
        "records": matches[-safe_limit:],
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "execution_allowed": False,
        "memory_mutation_allowed": False,
    }


def retrieve_similar_events(**kwargs: Any) -> Dict[str, Any]:
    return query_memory(**kwargs)

