from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Sequence

from historical_market.derivation.outcome_labeler import OutcomeLabeler
from historical_market.derivation.setup_detector import SetupDetector
from historical_market.storage.curated_store import CuratedStore, CuratedWriteResult


@dataclass(frozen=True)
class PatternPipelineResult:
    status: str
    event_id: str
    setup_written: bool
    outcome_written: bool
    setup_write_result: Optional[Dict[str, Any]]
    outcome_write_result: Optional[Dict[str, Any]]


class PatternPipeline:
    """
    Wire layer:
    - setup_detector -> curated_store.write_setup_pattern
    - outcome_labeler -> curated_store.write_outcome_event
    """

    def __init__(
        self,
        *,
        setup_detector: Optional[SetupDetector] = None,
        outcome_labeler: Optional[OutcomeLabeler] = None,
        curated_store: Optional[CuratedStore] = None,
    ) -> None:
        self.setup_detector = setup_detector or SetupDetector()
        self.outcome_labeler = outcome_labeler or OutcomeLabeler()
        self.curated_store = curated_store or CuratedStore()

    def process_event(
        self,
        *,
        event_id: str,
        setup_bars: Sequence[Mapping[str, Any]],
        anchor_bar: Mapping[str, Any],
        future_bars: Sequence[Mapping[str, Any]],
        horizon_bars: int = 5,
        outcome_notes: str = "",
    ) -> PatternPipelineResult:
        setup_record = self.setup_detector.build_setup_pattern_record(
            event_id=event_id,
            bars=setup_bars,
        )

        setup_write_result: Optional[CuratedWriteResult] = None
        if setup_record is not None:
            setup_write_result = self.curated_store.write_setup_pattern(setup_record)

        outcome_record = self.outcome_labeler.build_outcome_event_record(
            event_id=event_id,
            anchor_bar=anchor_bar,
            future_bars=future_bars,
            horizon_bars=horizon_bars,
            notes=outcome_notes,
        )
        outcome_write_result = self.curated_store.write_outcome_event(outcome_record)

        return PatternPipelineResult(
            status="ok",
            event_id=event_id,
            setup_written=setup_write_result is not None,
            outcome_written=outcome_write_result is not None,
            setup_write_result=self._to_dict(setup_write_result),
            outcome_write_result=self._to_dict(outcome_write_result),
        )

    def _to_dict(self, value: Optional[CuratedWriteResult]) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        return {
            "status": value.status,
            "artifact_type": value.artifact_type,
            "artifact_id": value.artifact_id,
            "artifact_path": value.artifact_path,
            "index_path": value.index_path,
            "receipt_path": value.receipt_path,
            "written_at": value.written_at,
        }