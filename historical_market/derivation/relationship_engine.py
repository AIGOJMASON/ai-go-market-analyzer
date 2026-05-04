from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


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


def _pct_change(current_value: float, prior_value: float) -> float:
    if prior_value == 0:
        raise ValueError("prior_value must not be zero")
    return ((current_value - prior_value) / prior_value) * 100.0


def _pearson_correlation(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys):
        raise ValueError("xs and ys length mismatch")
    n = len(xs)
    if n < 2:
        raise ValueError("at least 2 points required for correlation")

    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5

    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def _sort_bars(bars: Sequence[Mapping[str, Any]], *, name: str) -> List[Dict[str, Any]]:
    prepared: List[Dict[str, Any]] = []
    for index, row in enumerate(bars):
        if not isinstance(row, Mapping):
            raise TypeError(f"{name}[{index}] must be a mapping")
        item = dict(row)
        _require_fields(
            item,
            f"{name}[{index}]",
            ["symbol", "asset_class", "bar_timestamp", "timeframe", "close"],
        )
        item["symbol"] = _safe_str(item["symbol"], f"{name}[{index}].symbol").upper()
        item["asset_class"] = _safe_str(item["asset_class"], f"{name}[{index}].asset_class").lower()
        item["bar_timestamp"] = _safe_str(item["bar_timestamp"], f"{name}[{index}].bar_timestamp")
        item["timeframe"] = _safe_str(item["timeframe"], f"{name}[{index}].timeframe").lower()
        item["close"] = _to_float(item["close"], f"{name}[{index}].close")
        prepared.append(item)

    prepared.sort(key=lambda x: x["bar_timestamp"])
    return prepared


@dataclass(frozen=True)
class RelationshipAnalysis:
    status: str
    detected: bool
    leader_symbol: str
    follower_symbol: str
    relationship_type: str
    lag_bars: int
    confidence: float
    measured_window_start: str
    measured_window_end: str
    supporting_features: Dict[str, Any]
    computed_at: str


class RelationshipEngine:
    """
    First-pass pairwise relationship engine.

    Current capabilities:
    - compare two symbols on same timeframe
    - compute same-timeframe return correlation
    - test a small set of lag values
    - choose best absolute correlation lag
    - classify as:
        * lead_lag
        * correlated
        * inverse
        * no_relationship
    """

    def analyze_pair(
        self,
        *,
        leader_bars: Sequence[Mapping[str, Any]],
        follower_bars: Sequence[Mapping[str, Any]],
        max_lag_bars: int = 3,
        min_overlap_points: int = 4,
    ) -> RelationshipAnalysis:
        leader = _sort_bars(leader_bars, name="leader_bars")
        follower = _sort_bars(follower_bars, name="follower_bars")

        if len(leader) < min_overlap_points + 1 or len(follower) < min_overlap_points + 1:
            raise ValueError("not enough bars to analyze relationship")

        leader_symbol = leader[-1]["symbol"]
        follower_symbol = follower[-1]["symbol"]

        leader_timeframe = leader[-1]["timeframe"]
        follower_timeframe = follower[-1]["timeframe"]

        if leader_timeframe != follower_timeframe:
            raise ValueError("timeframe mismatch between leader_bars and follower_bars")
        if leader_symbol == follower_symbol:
            raise ValueError("leader_symbol and follower_symbol must differ")

        leader_returns = self._build_return_series(leader)
        follower_returns = self._build_return_series(follower)

        best = self._find_best_lag_alignment(
            leader_returns=leader_returns,
            follower_returns=follower_returns,
            max_lag_bars=max_lag_bars,
            min_overlap_points=min_overlap_points,
        )

        correlation = best["correlation"]
        lag_bars = best["lag_bars"]
        overlap = best["overlap_points"]

        if abs(correlation) >= 0.70 and lag_bars > 0:
            relationship_type = "lead_lag"
            confidence = min(1.0, 0.55 + abs(correlation) * 0.35 + min(lag_bars, 3) * 0.03)
            detected = True
        elif correlation >= 0.70 and lag_bars == 0:
            relationship_type = "correlated"
            confidence = min(1.0, 0.50 + correlation * 0.40)
            detected = True
        elif correlation <= -0.70:
            relationship_type = "inverse"
            confidence = min(1.0, 0.50 + abs(correlation) * 0.35)
            detected = True
        else:
            relationship_type = "no_relationship"
            confidence = 0.0
            detected = False

        measured_window_start = best["window_start"]
        measured_window_end = best["window_end"]

        return RelationshipAnalysis(
            status="ok",
            detected=detected,
            leader_symbol=leader_symbol,
            follower_symbol=follower_symbol,
            relationship_type=relationship_type,
            lag_bars=lag_bars,
            confidence=round(confidence, 3),
            measured_window_start=measured_window_start,
            measured_window_end=measured_window_end,
            supporting_features={
                "correlation": round(correlation, 4),
                "overlap_points": overlap,
                "leader_timeframe": leader_timeframe,
                "candidate_max_lag_bars": max_lag_bars,
            },
            computed_at=_utc_now_iso(),
        )

    def build_relationship_record(
        self,
        *,
        leader_bars: Sequence[Mapping[str, Any]],
        follower_bars: Sequence[Mapping[str, Any]],
        relationship_id: Optional[str] = None,
        max_lag_bars: int = 3,
        min_overlap_points: int = 4,
        notes: str = "",
    ) -> Optional[Dict[str, Any]]:
        analysis = self.analyze_pair(
            leader_bars=leader_bars,
            follower_bars=follower_bars,
            max_lag_bars=max_lag_bars,
            min_overlap_points=min_overlap_points,
        )
        if not analysis.detected:
            return None

        effective_relationship_id = relationship_id or self._build_relationship_id(
            leader_symbol=analysis.leader_symbol,
            follower_symbol=analysis.follower_symbol,
            relationship_type=analysis.relationship_type,
        )

        return {
            "relationship_id": effective_relationship_id,
            "leader_symbol": analysis.leader_symbol,
            "follower_symbol": analysis.follower_symbol,
            "relationship_type": analysis.relationship_type,
            "computed_at": analysis.computed_at,
            "lag_bars": analysis.lag_bars,
            "measured_window_start": analysis.measured_window_start,
            "measured_window_end": analysis.measured_window_end,
            "confidence": analysis.confidence,
            "notes": notes,
            "supporting_features": analysis.supporting_features,
        }

    def _build_return_series(self, bars: Sequence[Mapping[str, Any]]) -> List[Tuple[str, float]]:
        series: List[Tuple[str, float]] = []
        for index in range(1, len(bars)):
            current = float(bars[index]["close"])
            prior = float(bars[index - 1]["close"])
            timestamp = str(bars[index]["bar_timestamp"])
            series.append((timestamp, _pct_change(current, prior)))
        return series

    def _find_best_lag_alignment(
        self,
        *,
        leader_returns: Sequence[Tuple[str, float]],
        follower_returns: Sequence[Tuple[str, float]],
        max_lag_bars: int,
        min_overlap_points: int,
    ) -> Dict[str, Any]:
        best_result: Optional[Dict[str, Any]] = None

        for lag in range(0, max_lag_bars + 1):
            shifted_leader = leader_returns[:-lag] if lag > 0 else list(leader_returns)
            shifted_follower = follower_returns[lag:] if lag > 0 else list(follower_returns)

            overlap_count = min(len(shifted_leader), len(shifted_follower))
            if overlap_count < min_overlap_points:
                continue

            aligned_leader = shifted_leader[-overlap_count:]
            aligned_follower = shifted_follower[-overlap_count:]

            xs = [item[1] for item in aligned_leader]
            ys = [item[1] for item in aligned_follower]
            correlation = _pearson_correlation(xs, ys)

            candidate = {
                "lag_bars": lag,
                "correlation": correlation,
                "overlap_points": overlap_count,
                "window_start": aligned_follower[0][0],
                "window_end": aligned_follower[-1][0],
            }

            if best_result is None or abs(candidate["correlation"]) > abs(best_result["correlation"]):
                best_result = candidate

        if best_result is None:
            raise ValueError("no sufficient overlap for relationship analysis")

        return best_result

    def _build_relationship_id(
        self,
        *,
        leader_symbol: str,
        follower_symbol: str,
        relationship_type: str,
    ) -> str:
        return f"rel-{leader_symbol.lower()}-{follower_symbol.lower()}-{relationship_type}"