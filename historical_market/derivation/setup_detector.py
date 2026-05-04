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
        row["timeframe"] = _safe_str(row["timeframe"], f"bars[{index}].timeframe").lower()
        row["bar_timestamp"] = _safe_str(row["bar_timestamp"], f"bars[{index}].bar_timestamp")
        row["open"] = _to_float(row["open"], f"bars[{index}].open")
        row["high"] = _to_float(row["high"], f"bars[{index}].high")
        row["low"] = _to_float(row["low"], f"bars[{index}].low")
        row["close"] = _to_float(row["close"], f"bars[{index}].close")
        prepared.append(row)

    prepared.sort(key=lambda x: x["bar_timestamp"])
    return prepared


@dataclass(frozen=True)
class DetectedSetup:
    status: str
    detected: bool
    setup_type: Optional[str]
    symbol: str
    asset_class: str
    timeframe: str
    detected_at: str
    window_start: str
    window_end: str
    supporting_features: Dict[str, Any]
    confidence: float


class SetupDetector:
    """
    Governed setup detector for daily bars.

    Supported setup types:
    - dip_rebound
    - breakout
    - continuation
    - fade
    - event_confirmation

    Design intent:
    - preserve existing stricter classes
    - slightly loosen thresholds so real market cases are not discarded too easily
    - add an event-led directional class that can activate historical lookup
      even when the move is real but not a textbook breakout
    """

    def detect_latest_setup(
        self,
        bars: Sequence[Mapping[str, Any]],
        *,
        min_bars: int = 3,
    ) -> DetectedSetup:
        ordered = _sort_bars_by_timestamp(bars)

        if len(ordered) < min_bars:
            raise ValueError(f"At least {min_bars} bars are required")

        timeframe = ordered[-1]["timeframe"]
        if timeframe != "1d":
            raise ValueError("SetupDetector first version supports only timeframe='1d'")

        window = ordered[-5:] if len(ordered) >= 5 else ordered[-3:]
        latest = window[-1]

        symbol = latest["symbol"]
        asset_class = latest["asset_class"]
        window_start = window[0]["bar_timestamp"]
        window_end = window[-1]["bar_timestamp"]
        detected_at = _utc_now_iso()

        breakout = self._detect_breakout(window)
        if breakout["detected"]:
            return DetectedSetup(
                status="ok",
                detected=True,
                setup_type="breakout",
                symbol=symbol,
                asset_class=asset_class,
                timeframe=timeframe,
                detected_at=detected_at,
                window_start=window_start,
                window_end=window_end,
                supporting_features=breakout["supporting_features"],
                confidence=breakout["confidence"],
            )

        dip_rebound = self._detect_dip_rebound(window)
        if dip_rebound["detected"]:
            return DetectedSetup(
                status="ok",
                detected=True,
                setup_type="dip_rebound",
                symbol=symbol,
                asset_class=asset_class,
                timeframe=timeframe,
                detected_at=detected_at,
                window_start=window_start,
                window_end=window_end,
                supporting_features=dip_rebound["supporting_features"],
                confidence=dip_rebound["confidence"],
            )

        fade = self._detect_fade(window)
        if fade["detected"]:
            return DetectedSetup(
                status="ok",
                detected=True,
                setup_type="fade",
                symbol=symbol,
                asset_class=asset_class,
                timeframe=timeframe,
                detected_at=detected_at,
                window_start=window_start,
                window_end=window_end,
                supporting_features=fade["supporting_features"],
                confidence=fade["confidence"],
            )

        continuation = self._detect_continuation(window)
        if continuation["detected"]:
            return DetectedSetup(
                status="ok",
                detected=True,
                setup_type="continuation",
                symbol=symbol,
                asset_class=asset_class,
                timeframe=timeframe,
                detected_at=detected_at,
                window_start=window_start,
                window_end=window_end,
                supporting_features=continuation["supporting_features"],
                confidence=continuation["confidence"],
            )

        event_confirmation = self._detect_event_confirmation(window)
        if event_confirmation["detected"]:
            return DetectedSetup(
                status="ok",
                detected=True,
                setup_type="event_confirmation",
                symbol=symbol,
                asset_class=asset_class,
                timeframe=timeframe,
                detected_at=detected_at,
                window_start=window_start,
                window_end=window_end,
                supporting_features=event_confirmation["supporting_features"],
                confidence=event_confirmation["confidence"],
            )

        return DetectedSetup(
            status="ok",
            detected=False,
            setup_type=None,
            symbol=symbol,
            asset_class=asset_class,
            timeframe=timeframe,
            detected_at=detected_at,
            window_start=window_start,
            window_end=window_end,
            supporting_features={"reason": "no_supported_setup_detected"},
            confidence=0.0,
        )

    def build_setup_pattern_record(
        self,
        *,
        event_id: str,
        bars: Sequence[Mapping[str, Any]],
        pattern_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        detection = self.detect_latest_setup(bars)
        if not detection.detected or not detection.setup_type:
            return None

        event_id_clean = _safe_str(event_id, "event_id")
        effective_pattern_id = pattern_id or self._build_pattern_id(
            event_id=event_id_clean,
            setup_type=detection.setup_type,
        )

        return {
            "pattern_id": effective_pattern_id,
            "event_id": event_id_clean,
            "setup_type": detection.setup_type,
            "detected_at": detection.detected_at,
            "window_start": detection.window_start,
            "window_end": detection.window_end,
            "supporting_features": detection.supporting_features,
            "confidence": detection.confidence,
        }

    def _build_pattern_id(self, *, event_id: str, setup_type: str) -> str:
        return f"{event_id}-{setup_type}"

    def _detect_dip_rebound(self, window: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if len(window) < 3:
            return self._no_match()

        closes = [float(bar["close"]) for bar in window]
        lows = [float(bar["low"]) for bar in window]
        highs = [float(bar["high"]) for bar in window]

        last_close = closes[-1]
        prev_close = closes[-2]
        pre_last_closes = closes[:-1]

        min_low = min(lows[:-1]) if len(lows) > 1 else min(lows)
        prior_high_close = max(pre_last_closes) if pre_last_closes else last_close
        prior_high = max(highs[:-1]) if len(highs) > 1 else max(highs)

        drawdown_pct = 0.0
        if prior_high_close > 0:
            drawdown_pct = ((min_low - prior_high_close) / prior_high_close) * 100.0

        rebound_pct = 0.0
        if prev_close > 0:
            rebound_pct = ((last_close - prev_close) / prev_close) * 100.0

        detected = (
            drawdown_pct <= -0.75 and
            rebound_pct >= 0.50 and
            last_close > prev_close and
            last_close <= prior_high * 1.003
        )

        if not detected:
            return self._no_match()

        confidence = min(
            1.0,
            0.52 + min(abs(drawdown_pct), 5.0) * 0.03 + min(rebound_pct, 3.0) * 0.10,
        )

        return {
            "detected": True,
            "confidence": round(confidence, 3),
            "supporting_features": {
                "drawdown_pct": round(drawdown_pct, 3),
                "rebound_pct": round(rebound_pct, 3),
                "prior_high_close": round(prior_high_close, 6),
                "prior_high": round(prior_high, 6),
                "window_close_min": round(min(closes), 6),
                "window_close_max": round(max(closes), 6),
            },
        }

    def _detect_breakout(self, window: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if len(window) < 3:
            return self._no_match()

        previous_highs = [float(bar["high"]) for bar in window[:-1]]
        previous_closes = [float(bar["close"]) for bar in window[:-1]]
        last_close = float(window[-1]["close"])
        last_high = float(window[-1]["high"])

        prior_high = max(previous_highs)
        prior_close_max = max(previous_closes)

        breakout_pct = 0.0
        if prior_high > 0:
            breakout_pct = ((last_close - prior_high) / prior_high) * 100.0

        detected = (
            last_high >= prior_high and
            last_close > prior_high and
            breakout_pct >= 0.30
        )

        if not detected:
            return self._no_match()

        confidence = min(1.0, 0.58 + min(breakout_pct, 4.0) * 0.08)

        return {
            "detected": True,
            "confidence": round(confidence, 3),
            "supporting_features": {
                "prior_high": round(prior_high, 6),
                "prior_close_max": round(prior_close_max, 6),
                "breakout_pct": round(breakout_pct, 3),
                "last_close": round(last_close, 6),
            },
        }

    def _detect_continuation(self, window: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if len(window) < 3:
            return self._no_match()

        closes = [float(bar["close"]) for bar in window]
        up_count = sum(1 for idx in range(1, len(closes)) if closes[idx] > closes[idx - 1])
        positive_steps_ratio = up_count / max(1, len(closes) - 1)

        start_close = closes[0]
        end_close = closes[-1]

        net_move_pct = 0.0
        if start_close > 0:
            net_move_pct = ((end_close - start_close) / start_close) * 100.0

        detected = (
            positive_steps_ratio >= 0.50 and
            net_move_pct >= 0.60
        )

        if not detected:
            return self._no_match()

        confidence = min(
            1.0,
            0.48 + positive_steps_ratio * 0.20 + min(net_move_pct, 4.0) * 0.06,
        )

        return {
            "detected": True,
            "confidence": round(confidence, 3),
            "supporting_features": {
                "positive_steps_ratio": round(positive_steps_ratio, 3),
                "net_move_pct": round(net_move_pct, 3),
                "start_close": round(start_close, 6),
                "end_close": round(end_close, 6),
            },
        }

    def _detect_fade(self, window: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if len(window) < 3:
            return self._no_match()

        highs = [float(bar["high"]) for bar in window[:-1]]
        last_close = float(window[-1]["close"])
        last_open = float(window[-1]["open"])
        prior_high = max(highs)

        rejection_pct = 0.0
        if prior_high > 0:
            rejection_pct = ((last_close - prior_high) / prior_high) * 100.0

        intraday_change_pct = 0.0
        if last_open > 0:
            intraday_change_pct = ((last_close - last_open) / last_open) * 100.0

        detected = (
            float(window[-1]["high"]) >= prior_high and
            last_close < prior_high and
            intraday_change_pct <= -0.35
        )

        if not detected:
            return self._no_match()

        confidence = min(
            1.0,
            0.52 + min(abs(intraday_change_pct), 3.0) * 0.08 + min(abs(rejection_pct), 2.0) * 0.05,
        )

        return {
            "detected": True,
            "confidence": round(confidence, 3),
            "supporting_features": {
                "prior_high": round(prior_high, 6),
                "rejection_pct_vs_prior_high": round(rejection_pct, 3),
                "intraday_change_pct": round(intraday_change_pct, 3),
                "last_open": round(last_open, 6),
                "last_close": round(last_close, 6),
            },
        }

    def _detect_event_confirmation(self, window: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if len(window) < 3:
            return self._no_match()

        closes = [float(bar["close"]) for bar in window]
        highs = [float(bar["high"]) for bar in window]
        lows = [float(bar["low"]) for bar in window]
        opens = [float(bar["open"]) for bar in window]

        last_close = closes[-1]
        last_open = opens[-1]
        start_close = closes[0]
        prev_close = closes[-2]

        net_move_pct = 0.0
        if start_close > 0:
            net_move_pct = ((last_close - start_close) / start_close) * 100.0

        last_day_change_pct = 0.0
        if prev_close > 0:
            last_day_change_pct = ((last_close - prev_close) / prev_close) * 100.0

        intraday_change_pct = 0.0
        if last_open > 0:
            intraday_change_pct = ((last_close - last_open) / last_open) * 100.0

        positive_steps = sum(1 for idx in range(1, len(closes)) if closes[idx] >= closes[idx - 1])
        positive_steps_ratio = positive_steps / max(1, len(closes) - 1)

        close_position_in_last_bar = 0.0
        last_range = highs[-1] - lows[-1]
        if last_range > 0:
            close_position_in_last_bar = (last_close - lows[-1]) / last_range

        detected = (
            net_move_pct >= 0.35 and
            last_day_change_pct >= 0.15 and
            intraday_change_pct >= -0.10 and
            positive_steps_ratio >= 0.50 and
            close_position_in_last_bar >= 0.55
        )

        if not detected:
            return self._no_match()

        confidence = min(
            0.82,
            0.46
            + min(net_move_pct, 2.5) * 0.08
            + min(last_day_change_pct, 1.5) * 0.10
            + positive_steps_ratio * 0.10
            + min(close_position_in_last_bar, 1.0) * 0.08,
        )

        return {
            "detected": True,
            "confidence": round(confidence, 3),
            "supporting_features": {
                "net_move_pct": round(net_move_pct, 3),
                "last_day_change_pct": round(last_day_change_pct, 3),
                "intraday_change_pct": round(intraday_change_pct, 3),
                "positive_steps_ratio": round(positive_steps_ratio, 3),
                "close_position_in_last_bar": round(close_position_in_last_bar, 3),
                "window_close_min": round(min(closes), 6),
                "window_close_max": round(max(closes), 6),
            },
        }

    def _no_match(self) -> Dict[str, Any]:
        return {
            "detected": False,
            "confidence": 0.0,
            "supporting_features": {},
        }