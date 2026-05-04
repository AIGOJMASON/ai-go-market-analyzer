# AI_GO/core/visibility/collectors/external_memory_collector.py

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


def _recent_json_files(root: Path, limit: int = 10) -> List[Path]:
    if not root.exists() or not root.is_dir():
        return []
    files = [path for path in root.rglob("*.json") if path.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def _candidate_roots() -> List[Path]:
    roots = [
        PROJECT_ROOT / "EXTERNAL_MEMORY",
        PROJECT_ROOT / "state" / "external_memory",
        PROJECT_ROOT / "external_memory",
        PROJECT_ROOT / "receipts" / "market_analyzer_v1" / "learning",
        PROJECT_ROOT / "receipts" / "market_analyzer_v1" / "learning_override",
    ]
    return [path for path in roots if path.exists()]


def _extract_symbol(record: Dict[str, Any]) -> Optional[str]:
    for key in ("symbol", "ticker", "primary_symbol"):
        value = record.get(key)
        if value:
            return str(value)
    return None


def _extract_event_theme(record: Dict[str, Any]) -> Optional[str]:
    for key in ("event_theme", "theme", "pattern_class", "classification"):
        value = record.get(key)
        if value:
            return str(value)
    return None


def collect_external_memory_view(limit: int = 10) -> Dict[str, Any]:
    roots = _candidate_roots()

    recent_records: List[Dict[str, Any]] = []
    symbol_counts: Dict[str, int] = {}
    theme_counts: Dict[str, int] = {}

    for root in roots:
        for path in _recent_json_files(root, limit=limit):
            data = _read_json(path)
            if not isinstance(data, dict):
                continue

            symbol = _extract_symbol(data)
            theme = _extract_event_theme(data)

            recent_records.append(
                {
                    "record_id": data.get("record_id") or data.get("receipt_id") or path.stem,
                    "timestamp": data.get("timestamp") or data.get("generated_at"),
                    "source_path": path.relative_to(PROJECT_ROOT).as_posix(),
                    "symbol": symbol,
                    "event_theme": theme,
                    "status": data.get("status") or data.get("decision") or data.get("promotion_status"),
                }
            )

            if symbol:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            if theme:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1

    recent_records.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
    recent_records = recent_records[:limit]

    top_symbols = [key for key, _ in sorted(symbol_counts.items(), key=lambda item: (-item[1], item[0]))[:5]]
    top_event_themes = [key for key, _ in sorted(theme_counts.items(), key=lambda item: (-item[1], item[0]))[:5]]

    strongest_pattern_detected: Dict[str, Any] = {}
    if top_event_themes:
        strongest_pattern_detected = {
            "pattern_id": f"pattern::{top_event_themes[0]}",
            "pattern_class": top_event_themes[0],
            "confidence": "observed",
        }

    last_retrieval_summary: Dict[str, Any] = {
        "timestamp": recent_records[0]["timestamp"] if recent_records else None,
        "match_count": len(recent_records),
        "top_match_class": top_event_themes[0] if top_event_themes else None,
    }

    promoted_records = [
        record
        for record in recent_records
        if str(record.get("status") or "").lower() in {"promoted", "approved", "persisted"}
    ]

    last_promotion_summary: Dict[str, Any] = {
        "timestamp": promoted_records[0]["timestamp"] if promoted_records else None,
        "promoted_count": len(promoted_records),
        "top_promotion_class": promoted_records[0]["event_theme"] if promoted_records else None,
    }

    return {
        "record_count": len(recent_records),
        "recent_records": recent_records,
        "top_symbols": top_symbols,
        "top_event_themes": top_event_themes,
        "last_retrieval_summary": last_retrieval_summary,
        "last_promotion_summary": last_promotion_summary,
        "strongest_pattern_detected": strongest_pattern_detected,
    }