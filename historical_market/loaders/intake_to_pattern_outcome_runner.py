# AI_GO/historical_market/loaders/intake_to_pattern_outcome_runner.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

try:
    from AI_GO.historical_market.derivation.pattern_pipeline import PatternPipeline
    from AI_GO.historical_market.storage.db_paths import HistoricalMarketPaths
    from AI_GO.historical_market.storage.raw_store import RawStore
except ModuleNotFoundError:
    from historical_market.derivation.pattern_pipeline import PatternPipeline
    from historical_market.storage.db_paths import HistoricalMarketPaths
    from historical_market.storage.raw_store import RawStore


UTC = timezone.utc
INTAKE_RUNNER_VERSION = "northstar_6a_intake_to_pattern_outcome_runner_v1"


@dataclass(frozen=True)
class IntakeDerivationRunResult:
    status: str
    processed_count: int
    written_count: int
    skipped_count: int
    results: List[Dict[str, Any]]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _read_governed_json(path: Path) -> Dict[str, Any]:
    import json

    parsed = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(parsed, dict) and parsed.get("artifact_type") == "governed_persistence_envelope":
        payload = parsed.get("payload", {})
        return payload if isinstance(payload, dict) else {}
    return parsed if isinstance(parsed, dict) else {}


class IntakeToPatternOutcomeRunner:
    """
    Curated intake_event to raw bar join to setup/outcome derivation.

    Northstar 6A rule:
    - This runner does not write directly.
    - It delegates all curated writes to PatternPipeline and governed stores.
    - It returns governed classification metadata for probe visibility.
    """

    def __init__(
        self,
        *,
        paths: Optional[HistoricalMarketPaths] = None,
        raw_store: Optional[RawStore] = None,
        pipeline: Optional[PatternPipeline] = None,
    ) -> None:
        self.paths = paths or HistoricalMarketPaths()
        self.paths.ensure_all()
        self.raw_store = raw_store or RawStore(paths=self.paths)
        self.pipeline = pipeline or PatternPipeline()

    def _classification(self) -> Dict[str, Any]:
        return {
            "persistence_type": "historical_derivation_runner_result",
            "mutation_class": "historical_market_derivation_orchestration",
            "execution_allowed": False,
            "runtime_mutation_allowed": False,
            "recommendation_mutation_allowed": False,
            "pm_authority_mutation_allowed": False,
            "direct_disk_write_allowed": False,
        }

    def _authority_metadata(self) -> Dict[str, Any]:
        return {
            "authority_id": "historical_market_intake_to_pattern_outcome_runner",
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_recommendations": False,
            "can_mutate_pm_authority": False,
            "can_override_governance": False,
            "writes_delegated_to_governed_stores": True,
            "governance_stage": "northstar_6a",
        }

    def run_for_all_intake_events(
        self,
        *,
        limit: int = 50,
        skip_unknown_signal_seed: bool = True,
        min_setup_bars: int = 3,
        setup_lookback_bars: int = 5,
        horizon_bars: int = 5,
    ) -> Dict[str, Any]:
        processed = 0
        written = 0
        skipped = 0
        results: List[Dict[str, Any]] = []

        intake_paths = sorted(self.paths.intake_events_dir.glob("*.json"))
        for intake_path in intake_paths[: max(0, int(limit))]:
            processed += 1
            try:
                result = self.run_for_event_file(
                    intake_path=intake_path,
                    skip_unknown_signal_seed=skip_unknown_signal_seed,
                    min_setup_bars=min_setup_bars,
                    setup_lookback_bars=setup_lookback_bars,
                    horizon_bars=horizon_bars,
                )
                if result.get("status") == "written":
                    written += 1
                else:
                    skipped += 1
                results.append(result)
            except Exception as exc:
                skipped += 1
                results.append(
                    {
                        "status": "skipped",
                        "reason": "runner_exception",
                        "path": str(intake_path),
                        "error": str(exc),
                    }
                )

        return {
            "status": "ok",
            "artifact_type": "historical_intake_derivation_run_result",
            "artifact_version": INTAKE_RUNNER_VERSION,
            "processed_count": processed,
            "written_count": written,
            "skipped_count": skipped,
            "results": results,
            "classification": self._classification(),
            "authority_metadata": self._authority_metadata(),
            "sealed": True,
        }

    def run_for_event_file(
        self,
        *,
        intake_path: Path,
        skip_unknown_signal_seed: bool = True,
        min_setup_bars: int = 3,
        setup_lookback_bars: int = 5,
        horizon_bars: int = 5,
    ) -> Dict[str, Any]:
        event = _read_governed_json(intake_path)
        return self.run_for_event(
            event=event,
            source_path=str(intake_path),
            skip_unknown_signal_seed=skip_unknown_signal_seed,
            min_setup_bars=min_setup_bars,
            setup_lookback_bars=setup_lookback_bars,
            horizon_bars=horizon_bars,
        )

    def run_for_event(
        self,
        *,
        event: Mapping[str, Any],
        source_path: str = "",
        skip_unknown_signal_seed: bool = True,
        min_setup_bars: int = 3,
        setup_lookback_bars: int = 5,
        horizon_bars: int = 5,
    ) -> Dict[str, Any]:
        payload = dict(event)
        symbol = _clean(payload.get("symbol")).upper()
        event_id = _clean(payload.get("event_id") or payload.get("artifact_id") or payload.get("request_id"))
        signal_seed = _clean(payload.get("signal_seed") or payload.get("event_theme") or payload.get("setup_type"))

        if not symbol:
            return self._skip("missing_symbol", source_path=source_path, event_id=event_id)

        if skip_unknown_signal_seed and signal_seed in {"", "unknown"}:
            return self._skip("unknown_signal_seed", source_path=source_path, event_id=event_id)

        bars = self.raw_store.read_bars(symbol=symbol, limit=10000)
        if len(bars) < max(min_setup_bars, setup_lookback_bars, horizon_bars):
            return self._skip(
                "insufficient_raw_bars",
                source_path=source_path,
                event_id=event_id,
                details={"bar_count": len(bars)},
            )

        if hasattr(self.pipeline, "derive_from_intake_event"):
            result = self.pipeline.derive_from_intake_event(
                intake_event=payload,
                bars=bars,
                min_setup_bars=min_setup_bars,
                setup_lookback_bars=setup_lookback_bars,
                horizon_bars=horizon_bars,
            )
        elif hasattr(self.pipeline, "run"):
            result = self.pipeline.run(
                intake_event=payload,
                bars=bars,
                min_setup_bars=min_setup_bars,
                setup_lookback_bars=setup_lookback_bars,
                horizon_bars=horizon_bars,
            )
        else:
            return self._skip(
                "pattern_pipeline_missing_entrypoint",
                source_path=source_path,
                event_id=event_id,
            )

        result_dict = _safe_dict(result)
        status = _clean(result_dict.get("status")) or "written"

        return {
            "status": status,
            "event_id": event_id,
            "symbol": symbol,
            "source_path": source_path,
            "pipeline_result": result_dict,
            "classification": self._classification(),
            "authority_metadata": self._authority_metadata(),
            "processed_at": _utc_now_iso(),
            "sealed": True,
        }

    def _skip(
        self,
        reason: str,
        *,
        source_path: str = "",
        event_id: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "status": "skipped",
            "reason": reason,
            "event_id": event_id,
            "source_path": source_path,
            "details": dict(details or {}),
            "classification": self._classification(),
            "authority_metadata": self._authority_metadata(),
            "processed_at": _utc_now_iso(),
            "sealed": True,
        }


def run_intake_to_pattern_outcome_derivation(**kwargs: Any) -> Dict[str, Any]:
    runner = IntakeToPatternOutcomeRunner()
    return runner.run_for_all_intake_events(**kwargs)