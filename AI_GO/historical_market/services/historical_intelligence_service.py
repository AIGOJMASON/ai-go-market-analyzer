from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence

from historical_market.adapters.operator_translation_adapter import OperatorTranslationAdapter
from historical_market.derivation.relationship_engine import RelationshipEngine
from historical_market.retrieval.historical_query_runtime import HistoricalQueryRuntime


@dataclass(frozen=True)
class HistoricalIntelligenceResult:
    status: str
    setup_history_panel: Optional[Dict[str, Any]]
    event_package_panel: Optional[Dict[str, Any]]
    relationship_panel: Optional[Dict[str, Any]]
    raw_sections: Dict[str, Any]


class HistoricalIntelligenceService:
    """
    Unified historical intelligence service.

    Purpose:
    - provide one callable surface over historical retrieval + translation
    - keep downstream callers away from internal module sprawl
    - support setup-history, event-package, and optional relationship context

    This service does not:
    - ingest live data
    - write historical records
    - mutate curated storage
    - determine execution authority
    """

    def __init__(
        self,
        *,
        query_runtime: Optional[HistoricalQueryRuntime] = None,
        translation_adapter: Optional[OperatorTranslationAdapter] = None,
        relationship_engine: Optional[RelationshipEngine] = None,
    ) -> None:
        self.query_runtime = query_runtime or HistoricalQueryRuntime()
        self.translation_adapter = translation_adapter or OperatorTranslationAdapter()
        self.relationship_engine = relationship_engine or RelationshipEngine()

    # -------------------------------------------------------------------------
    # Primary unified surface
    # -------------------------------------------------------------------------

    def build_historical_intelligence(
        self,
        *,
        setup_type: Optional[str] = None,
        event_id: Optional[str] = None,
        leader_bars: Optional[Sequence[Mapping[str, Any]]] = None,
        follower_bars: Optional[Sequence[Mapping[str, Any]]] = None,
        max_lag_bars: int = 3,
        min_overlap_points: int = 4,
    ) -> HistoricalIntelligenceResult:
        setup_history_panel: Optional[Dict[str, Any]] = None
        event_package_panel: Optional[Dict[str, Any]] = None
        relationship_panel: Optional[Dict[str, Any]] = None

        raw_sections: Dict[str, Any] = {
            "setup_summary": None,
            "event_package": None,
            "relationship_analysis": None,
        }

        if setup_type:
            setup_summary = self.query_runtime.summarize_setup_outcomes(setup_type=setup_type)
            raw_sections["setup_summary"] = setup_summary
            setup_history_panel = self.translation_adapter.build_setup_history_panel(
                setup_type=setup_type,
                setup_summary=setup_summary,
            )

        if event_id:
            event_package = self.query_runtime.get_event_package(event_id=event_id)
            raw_sections["event_package"] = {
                "status": event_package.status,
                "query_type": event_package.query_type,
                "match_count": event_package.match_count,
                "matches": event_package.matches,
            }
            if event_package.status == "ok":
                event_package_panel = self.translation_adapter.build_event_package_panel(
                    event_id=event_id,
                    event_records=event_package.matches,
                )

        if leader_bars is not None and follower_bars is not None:
            relationship_analysis = self.relationship_engine.analyze_pair(
                leader_bars=leader_bars,
                follower_bars=follower_bars,
                max_lag_bars=max_lag_bars,
                min_overlap_points=min_overlap_points,
            )
            raw_sections["relationship_analysis"] = {
                "status": relationship_analysis.status,
                "detected": relationship_analysis.detected,
                "leader_symbol": relationship_analysis.leader_symbol,
                "follower_symbol": relationship_analysis.follower_symbol,
                "relationship_type": relationship_analysis.relationship_type,
                "lag_bars": relationship_analysis.lag_bars,
                "confidence": relationship_analysis.confidence,
                "measured_window_start": relationship_analysis.measured_window_start,
                "measured_window_end": relationship_analysis.measured_window_end,
                "supporting_features": relationship_analysis.supporting_features,
                "computed_at": relationship_analysis.computed_at,
            }
            relationship_panel = self._build_relationship_panel(raw_sections["relationship_analysis"])

        return HistoricalIntelligenceResult(
            status="ok",
            setup_history_panel=setup_history_panel,
            event_package_panel=event_package_panel,
            relationship_panel=relationship_panel,
            raw_sections=raw_sections,
        )

    # -------------------------------------------------------------------------
    # Narrow helper surfaces
    # -------------------------------------------------------------------------

    def build_setup_history_only(self, *, setup_type: str) -> Dict[str, Any]:
        setup_summary = self.query_runtime.summarize_setup_outcomes(setup_type=setup_type)
        return self.translation_adapter.build_setup_history_panel(
            setup_type=setup_type,
            setup_summary=setup_summary,
        )

    def build_event_package_only(self, *, event_id: str) -> Optional[Dict[str, Any]]:
        event_package = self.query_runtime.get_event_package(event_id=event_id)
        if event_package.status != "ok":
            return None
        return self.translation_adapter.build_event_package_panel(
            event_id=event_id,
            event_records=event_package.matches,
        )

    def build_relationship_only(
        self,
        *,
        leader_bars: Sequence[Mapping[str, Any]],
        follower_bars: Sequence[Mapping[str, Any]],
        max_lag_bars: int = 3,
        min_overlap_points: int = 4,
    ) -> Dict[str, Any]:
        relationship_analysis = self.relationship_engine.analyze_pair(
            leader_bars=leader_bars,
            follower_bars=follower_bars,
            max_lag_bars=max_lag_bars,
            min_overlap_points=min_overlap_points,
        )
        return self._build_relationship_panel(
            {
                "status": relationship_analysis.status,
                "detected": relationship_analysis.detected,
                "leader_symbol": relationship_analysis.leader_symbol,
                "follower_symbol": relationship_analysis.follower_symbol,
                "relationship_type": relationship_analysis.relationship_type,
                "lag_bars": relationship_analysis.lag_bars,
                "confidence": relationship_analysis.confidence,
                "measured_window_start": relationship_analysis.measured_window_start,
                "measured_window_end": relationship_analysis.measured_window_end,
                "supporting_features": relationship_analysis.supporting_features,
                "computed_at": relationship_analysis.computed_at,
            }
        )

    # -------------------------------------------------------------------------
    # Internal translation helpers
    # -------------------------------------------------------------------------

    def _build_relationship_panel(self, analysis: Mapping[str, Any]) -> Dict[str, Any]:
        detected = bool(analysis.get("detected", False))
        relationship_type = str(analysis.get("relationship_type", "unknown"))
        leader_symbol = str(analysis.get("leader_symbol", "unknown"))
        follower_symbol = str(analysis.get("follower_symbol", "unknown"))
        lag_bars = int(analysis.get("lag_bars", 0) or 0)
        confidence = float(analysis.get("confidence", 0.0) or 0.0)

        if not detected:
            operator_summary = (
                f"No strong historical relationship detected between "
                f"{leader_symbol} and {follower_symbol} in the evaluated window."
            )
        elif relationship_type == "lead_lag":
            operator_summary = (
                f"{leader_symbol} has historically led {follower_symbol} by about "
                f"{lag_bars} bar(s) in the evaluated window."
            )
        elif relationship_type == "correlated":
            operator_summary = (
                f"{leader_symbol} and {follower_symbol} have moved together "
                f"historically in the evaluated window."
            )
        elif relationship_type == "inverse":
            operator_summary = (
                f"{leader_symbol} and {follower_symbol} have moved inversely "
                f"historically in the evaluated window."
            )
        else:
            operator_summary = (
                f"Historical relationship between {leader_symbol} and "
                f"{follower_symbol} is present but unclassified."
            )

        return {
            "panel_type": "relationship_history",
            "detected": detected,
            "leader_symbol": leader_symbol,
            "follower_symbol": follower_symbol,
            "relationship_type": relationship_type,
            "lag_bars": lag_bars,
            "confidence": round(confidence, 3),
            "measured_window_start": analysis.get("measured_window_start"),
            "measured_window_end": analysis.get("measured_window_end"),
            "supporting_features": dict(analysis.get("supporting_features", {})),
            "operator_summary": operator_summary,
        }