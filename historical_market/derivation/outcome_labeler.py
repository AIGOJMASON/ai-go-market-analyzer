from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Sequence


UTC = timezone.utc


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_str(value: Any, field_name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} must not be empty")
    return text


def _to_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc


def _require_fields(record: Mapping[str, Any], record_name: str, fields: Sequence[str]) -> None:
    missing = [field for field in fields if field not in record or record[field] in (None, "")]
    if missing:
        raise ValueError(f"{record_name} missing required fields: {', '.join(missing)}")


def _sort_bars_by_timestamp(bars: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    prepared: List[Dict[str, Any]] = []
    for index, bar in enumerate(bars):
        if not isinstance(bar, Mapping):
            raise TypeError(f"bars[{index}] must be a mapping")

        row = dict(bar)
        _require_fields(
            row,
            f"bars[{index}]",
            ["symbol", "asset_class", "bar_timestamp", "open", "high", "low", "close", "timeframe"],
        )

        row["symbol"] = _safe_str(row["symbol"], f"bars[{index}].symbol").upper()
        row["asset_class"] = _safe_str(row["asset_class"], f"bars[{index}].asset_class").lower()
        row["bar_timestamp"] = _safe_str(row["bar_timestamp"], f"bars[{index}].bar_timestamp")
        row["timeframe"] = _safe_str(row["timeframe"], f"bars[{index}].timeframe").lower()
        row["open"] = _to_float(row["open"], f"bars[{index}].open")
        row["high"] = _to_float(row["high"], f"bars[{index}].high")
        row["low"] = _to_float(row["low"], f"bars[{index}].low")
        row["close"] = _to_float(row["close"], f"bars[{index}].close")
        prepared.append(row)

    prepared.sort(key=lambda x: x["bar_timestamp"])
    return prepared


@dataclass(frozen=True)
class LabeledOutcome:
    status: str
    outcome_label: str
    symbol: str
    asset_class: str
    timeframe: str
    anchor_timestamp: str
    outcome_timestamp: str
    horizon_bars: int
    anchor_close: float
    final_close: float
    close_return_pct: float
    max_favorable_excursion_pct: float
    max_adverse_excursion_pct: float
    supporting_features: Dict[str, Any]


class OutcomeLabeler:
    """
    Minimal first-pass outcome labeler for daily bars.

    First-version labels:
    - follow_through
    - failure
    - stall

    Rules:
    - deterministic
    - daily bars only
    - explicit horizon sizing
    - outcome is measured from anchor close forward
    """

    def label_outcome(
        self,
        *,
        anchor_bar: Mapping[str, Any],
        future_bars: Sequence[Mapping[str, Any]],
        horizon_bars: int = 5,
        follow_through_threshold_pct: float = 1.5,
        failure_threshold_pct: float = -1.0,
    ) -> LabeledOutcome:
        anchor = self._prepare_anchor_bar(anchor_bar)
        future = _sort_bars_by_timestamp(future_bars)

        if not future:
            raise ValueError("future_bars must not be empty")

        timeframe = anchor["timeframe"]
        if timeframe != "1d":
            raise ValueError("OutcomeLabeler first version supports only timeframe='1d'")

        for index, row in enumerate(future):
            if row["timeframe"] != timeframe:
                raise ValueError(f"future_bars[{index}] timeframe mismatch")
            if row["symbol"] != anchor["symbol"]:
                raise ValueError(f"future_bars[{index}] symbol mismatch")
            if row["asset_class"] != anchor["asset_class"]:
                raise ValueError(f"future_bars[{index}] asset_class mismatch")
            if row["bar_timestamp"] <= anchor["bar_timestamp"]:
                raise ValueError("future_bars must occur strictly after anchor_bar")

        if horizon_bars < 1:
            raise ValueError("horizon_bars must be >= 1")

        horizon_window = future[:horizon_bars]
        anchor_close = anchor["close"]
        final_bar = horizon_window[-1]
        final_close = final_bar["close"]

        highest_high = max(float(bar["high"]) for bar in horizon_window)
        lowest_low = min(float(bar["low"]) for bar in horizon_window)

        close_return_pct = self._pct_change(final_close, anchor_close)
        max_favorable_excursion_pct = self._pct_change(highest_high, anchor_close)
        max_adverse_excursion_pct = self._pct_change(lowest_low, anchor_close)

        outcome_label = self._classify_outcome(
            close_return_pct=close_return_pct,
            max_favorable_excursion_pct=max_favorable_excursion_pct,
            max_adverse_excursion_pct=max_adverse_excursion_pct,
            follow_through_threshold_pct=follow_through_threshold_pct,
            failure_threshold_pct=failure_threshold_pct,
        )

        return LabeledOutcome(
            status="ok",
            outcome_label=outcome_label,
            symbol=anchor["symbol"],
            asset_class=anchor["asset_class"],
            timeframe=timeframe,
            anchor_timestamp=anchor["bar_timestamp"],
            outcome_timestamp=final_bar["bar_timestamp"],
            horizon_bars=len(horizon_window),
            anchor_close=round(anchor_close, 6),
            final_close=round(final_close, 6),
            close_return_pct=round(close_return_pct, 3),
            max_favorable_excursion_pct=round(max_favorable_excursion_pct, 3),
            max_adverse_excursion_pct=round(max_adverse_excursion_pct, 3),
            supporting_features={
                "highest_high": round(highest_high, 6),
                "lowest_low": round(lowest_low, 6),
                "bars_evaluated": len(horizon_window),
                "follow_through_threshold_pct": follow_through_threshold_pct,
                "failure_threshold_pct": failure_threshold_pct,
            },
        )

    def build_outcome_event_record(
        self,
        *,
        event_id: str,
        anchor_bar: Mapping[str, Any],
        future_bars: Sequence[Mapping[str, Any]],
        horizon_bars: int = 5,
        outcome_id: Optional[str] = None,
        follow_through_threshold_pct: float = 1.5,
        failure_threshold_pct: float = -1.0,
        notes: str = "",
    ) -> Dict[str, Any]:
        event_id_clean = _safe_str(event_id, "event_id")
        outcome = self.label_outcome(
            anchor_bar=anchor_bar,
            future_bars=future_bars,
            horizon_bars=horizon_bars,
            follow_through_threshold_pct=follow_through_threshold_pct,
            failure_threshold_pct=failure_threshold_pct,
        )

        effective_outcome_id = outcome_id or self._build_outcome_id(
            event_id=event_id_clean,
            horizon_bars=outcome.horizon_bars,
        )

        return {
            "outcome_id": effective_outcome_id,
            "event_id": event_id_clean,
            "outcome_timestamp": outcome.outcome_timestamp,
            "outcome_label": outcome.outcome_label,
            "horizon_bars": outcome.horizon_bars,
            "max_favorable_excursion_pct": outcome.max_favorable_excursion_pct,
            "max_adverse_excursion_pct": outcome.max_adverse_excursion_pct,
            "close_return_pct": outcome.close_return_pct,
            "notes": notes,
            "supporting_features": outcome.supporting_features,
        }

    def _prepare_anchor_bar(self, bar: Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(bar, Mapping):
            raise TypeError("anchor_bar must be a mapping")

        row = dict(bar)
        _require_fields(
            row,
            "anchor_bar",
            ["symbol", "asset_class", "bar_timestamp", "open", "high", "low", "close", "timeframe"],
        )

        row["symbol"] = _safe_str(row["symbol"], "anchor_bar.symbol").upper()
        row["asset_class"] = _safe_str(row["asset_class"], "anchor_bar.asset_class").lower()
        row["bar_timestamp"] = _safe_str(row["bar_timestamp"], "anchor_bar.bar_timestamp")
        row["timeframe"] = _safe_str(row["timeframe"], "anchor_bar.timeframe").lower()
        row["open"] = _to_float(row["open"], "anchor_bar.open")
        row["high"] = _to_float(row["high"], "anchor_bar.high")
        row["low"] = _to_float(row["low"], "anchor_bar.low")
        row["close"] = _to_float(row["close"], "anchor_bar.close")
        return row

    def _classify_outcome(
        self,
        *,
        close_return_pct: float,
        max_favorable_excursion_pct: float,
        max_adverse_excursion_pct: float,
        follow_through_threshold_pct: float,
        failure_threshold_pct: float,
    ) -> str:
        if close_return_pct >= follow_through_threshold_pct:
            return "follow_through"

        if close_return_pct <= failure_threshold_pct:
            return "failure"

        if max_adverse_excursion_pct <= failure_threshold_pct and max_favorable_excursion_pct < follow_through_threshold_pct:
            return "failure"

        return "stall"

    def _pct_change(self, observed: float, reference: float) -> float:
        if reference == 0:
            raise ValueError("reference value must not be zero")
        return ((observed - reference) / reference) * 100.0

    def _build_outcome_id(self, *, event_id: str, horizon_bars: int) -> str:
        return f"{event_id}-h{int(horizon_bars):02d}"