from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


DEFAULT_BOARD_SYMBOLS: tuple[str, ...] = (
    "SPY",
    "QQQ",
    "XLE",
    "XLP",
    "XLU",
    "TLT",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _state_root() -> Path:
    return state_root() / "operator_dashboard"


def board_snapshot_path() -> Path:
    return _state_root() / "board_quote_snapshot.json"


def board_snapshot_cursor_path() -> Path:
    return _state_root() / "board_quote_snapshot_cursor.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _persist_board_json(
    *,
    path: Path,
    payload: Dict[str, Any],
    operation: str,
    persistence_type: str,
) -> None:
    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="market_board_snapshot_persistence",
        persistence_type=persistence_type,
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": operation,
            "child_core_id": "market_analyzer_v1",
            "layer": "projection.board_snapshot_state",
        },
    )


def load_board_snapshot() -> Dict[str, Any]:
    path = board_snapshot_path()

    if not path.exists():
        return {
            "artifact_type": "board_quote_snapshot",
            "updated_at": None,
            "symbols": {},
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "artifact_type": "board_quote_snapshot",
            "updated_at": None,
            "symbols": {},
        }

    return payload if isinstance(payload, dict) else {
        "artifact_type": "board_quote_snapshot",
        "updated_at": None,
        "symbols": {},
    }


def save_board_snapshot(snapshot: Dict[str, Any]) -> Path:
    path = board_snapshot_path()
    payload = dict(snapshot if isinstance(snapshot, dict) else {})
    payload["artifact_type"] = "board_quote_snapshot"
    payload["artifact_version"] = "northstar_board_snapshot_v1"
    payload["updated_at"] = _utc_now_iso()
    payload.setdefault("symbols", {})
    payload["classification"] = {
        "persistence_type": "market_board_snapshot",
        "mutation_class": "market_board_snapshot_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": True,
    }
    payload["authority"] = {
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_recommendation": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
    }
    payload["sealed"] = True

    _persist_board_json(
        path=path,
        payload=payload,
        operation="save_board_snapshot",
        persistence_type="market_board_snapshot",
    )

    return path


def load_cursor() -> Dict[str, Any]:
    path = board_snapshot_cursor_path()

    if not path.exists():
        return {
            "last_index": -1,
            "updated_at": None,
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "last_index": -1,
            "updated_at": None,
        }

    return payload if isinstance(payload, dict) else {
        "last_index": -1,
        "updated_at": None,
    }


def save_cursor(cursor: Dict[str, Any]) -> Path:
    path = board_snapshot_cursor_path()
    payload = dict(cursor if isinstance(cursor, dict) else {})
    payload["artifact_type"] = "board_quote_snapshot_cursor"
    payload["artifact_version"] = "northstar_board_snapshot_cursor_v1"
    payload["updated_at"] = _utc_now_iso()
    payload.setdefault("last_index", -1)
    payload["classification"] = {
        "persistence_type": "market_board_snapshot_cursor",
        "mutation_class": "market_board_snapshot_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": True,
    }
    payload["sealed"] = True

    _persist_board_json(
        path=path,
        payload=payload,
        operation="save_board_snapshot_cursor",
        persistence_type="market_board_snapshot_cursor",
    )

    return path


def update_board_symbol(
    *,
    symbol: str,
    quote: Dict[str, Any],
) -> Dict[str, Any]:
    clean_symbol = str(symbol or "").strip().upper()
    if not clean_symbol:
        raise ValueError("symbol is required")

    snapshot = load_board_snapshot()
    symbols = _safe_dict(snapshot.get("symbols"))
    symbols[clean_symbol] = dict(quote if isinstance(quote, dict) else {})
    snapshot["symbols"] = symbols
    save_board_snapshot(snapshot)
    return snapshot


def next_board_symbol(symbols: Iterable[str] = DEFAULT_BOARD_SYMBOLS) -> str:
    symbol_list = [str(item).strip().upper() for item in symbols if str(item).strip()]
    if not symbol_list:
        symbol_list = list(DEFAULT_BOARD_SYMBOLS)

    cursor = load_cursor()
    try:
        last_index = int(cursor.get("last_index", -1))
    except (TypeError, ValueError):
        last_index = -1

    next_index = (last_index + 1) % len(symbol_list)
    save_cursor({"last_index": next_index})

    return symbol_list[next_index]