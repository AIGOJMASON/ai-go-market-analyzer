# AI_GO/historical_market/retrieval/historical_query_runtime.py

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from AI_GO.historical_market.storage.db_paths import HistoricalMarketPaths
except ModuleNotFoundError:
    from historical_market.storage.db_paths import HistoricalMarketPaths


HISTORICAL_QUERY_VERSION = "northstar_6a_historical_query_runtime_v1"


@dataclass(frozen=True)
class HistoricalQueryResult:
    status: str
    query_type: str
    match_count: int
    matches: List[Dict[str, Any]]


def _read_json(path: Path) -> Dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(parsed, dict) and parsed.get("artifact_type") == "governed_persistence_envelope":
        payload = parsed.get("payload", {})
        return payload if isinstance(payload, dict) else {}
    return parsed if isinstance(parsed, dict) else {}


def _safe_upper(value: Any) -> str:
    return str(value or "").strip().upper()


def _safe_lower(value: Any) -> str:
    return str(value or "").strip().lower()


def _classification() -> Dict[str, Any]:
    return {
        "persistence_type": "none_read_only_query",
        "mutation_class": "read_only_historical_retrieval",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "pm_authority_mutation_allowed": False,
        "disk_write_allowed": False,
        "advisory_only": True,
    }


def _authority_metadata() -> Dict[str, Any]:
    return {
        "authority_id": "historical_market_query_runtime",
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_mutate_recommendations": False,
        "can_mutate_pm_authority": False,
        "can_write_disk": False,
        "read_only": True,
        "governance_stage": "northstar_6a",
    }


class HistoricalQueryRuntime:
    """
    Read-only retrieval layer over governed historical artifacts.
    """

    def __init__(self, *, paths: Optional[HistoricalMarketPaths] = None) -> None:
        self.paths = paths or HistoricalMarketPaths()
        self.paths.ensure_all()

    def _with_governance(self, result: HistoricalQueryResult) -> Dict[str, Any]:
        return {
            "status": result.status,
            "artifact_type": "historical_query_result",
            "artifact_version": HISTORICAL_QUERY_VERSION,
            "query_type": result.query_type,
            "match_count": result.match_count,
            "matches": result.matches,
            "classification": _classification(),
            "authority_metadata": _authority_metadata(),
            "sealed": True,
        }

    def query_setup_patterns(
        self,
        *,
        setup_type: str,
        symbol: Optional[str] = None,
        limit: int = 20,
    ) -> HistoricalQueryResult:
        matches: List[Dict[str, Any]] = []
        setup_type_clean = _safe_lower(setup_type)
        symbol_clean = _safe_upper(symbol)

        for artifact_path in sorted(self.paths.setup_patterns_dir.glob("*.json")):
            payload = _read_json(artifact_path)
            if _safe_lower(payload.get("setup_type")) != setup_type_clean:
                continue
            if symbol_clean and symbol_clean not in json.dumps(payload).upper():
                continue
            matches.append(payload)
            if len(matches) >= limit:
                break

        return HistoricalQueryResult(
            status="ok",
            query_type="setup_patterns",
            match_count=len(matches),
            matches=matches,
        )

    def query_outcomes(
        self,
        *,
        outcome_label: str,
        limit: int = 20,
    ) -> HistoricalQueryResult:
        matches: List[Dict[str, Any]] = []
        outcome_label_clean = _safe_lower(outcome_label)

        for artifact_path in sorted(self.paths.outcome_events_dir.glob("*.json")):
            payload = _read_json(artifact_path)
            if outcome_label_clean not in json.dumps(payload).lower():
                continue
            matches.append(payload)
            if len(matches) >= limit:
                break

        return HistoricalQueryResult(
            status="ok",
            query_type="outcomes",
            match_count=len(matches),
            matches=matches,
        )

    def query_event_package(
        self,
        *,
        event_id: str,
    ) -> Dict[str, Any]:
        event_id_clean = str(event_id or "").strip()
        if not event_id_clean:
            raise ValueError("event_id is required")

        package = {
            "event_id": event_id_clean,
            "intake_events": self._find_by_event_id(self.paths.intake_events_dir, event_id_clean),
            "setup_patterns": self._find_by_event_id(self.paths.setup_patterns_dir, event_id_clean),
            "outcome_events": self._find_by_event_id(self.paths.outcome_events_dir, event_id_clean),
            "asset_relationships": self._find_by_event_id(self.paths.asset_relationships_dir, event_id_clean),
        }

        return {
            "status": "ok",
            "artifact_type": "historical_event_package",
            "artifact_version": HISTORICAL_QUERY_VERSION,
            "package": package,
            "classification": _classification(),
            "authority_metadata": _authority_metadata(),
            "sealed": True,
        }

    def summarize_setup_outcomes(
        self,
        *,
        setup_type: str,
        symbol: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        patterns = self.query_setup_patterns(
            setup_type=setup_type,
            symbol=symbol,
            limit=limit,
        ).matches

        outcome_counts: Dict[str, int] = {}
        for pattern in patterns:
            label = _safe_lower(pattern.get("outcome_label") or pattern.get("outcome_class") or "unknown")
            outcome_counts[label] = outcome_counts.get(label, 0) + 1

        return {
            "status": "ok",
            "artifact_type": "historical_setup_outcome_summary",
            "artifact_version": HISTORICAL_QUERY_VERSION,
            "setup_type": setup_type,
            "symbol": symbol,
            "sample_count": len(patterns),
            "outcome_counts": outcome_counts,
            "classification": _classification(),
            "authority_metadata": _authority_metadata(),
            "sealed": True,
        }

    def _find_by_event_id(self, root: Path, event_id: str) -> List[Dict[str, Any]]:
        matches: List[Dict[str, Any]] = []
        if not root.exists():
            return matches

        for artifact_path in sorted(root.glob("*.json")):
            payload = _read_json(artifact_path)
            if str(payload.get("event_id", "")).strip() == event_id:
                matches.append(payload)

        return matches

    def query_setup_patterns_dict(self, **kwargs: Any) -> Dict[str, Any]:
        return self._with_governance(self.query_setup_patterns(**kwargs))

    def query_outcomes_dict(self, **kwargs: Any) -> Dict[str, Any]:
        return self._with_governance(self.query_outcomes(**kwargs))