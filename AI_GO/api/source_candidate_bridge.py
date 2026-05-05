import re
from typing import List, Optional

from fastapi import HTTPException

try:
    from AI_GO.api.source_ingress_schema import SourceCandidateRecord, SourceSignalRecord
except ModuleNotFoundError:
    from api.source_ingress_schema import SourceCandidateRecord, SourceSignalRecord


_ALLOWED_CONFIRMATIONS = {"confirmed", "partial", "missing"}
_CONFIRMATION_WEIGHT = {"confirmed": 3, "partial": 2, "unknown": 1, "missing": 0}
_SEVERITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}
_TRUST_WEIGHT = {
    "high_structure": 4,
    "medium_structure": 3,
    "bounded_manual": 2,
    "low_structure": 1,
}


def _sanitize_request_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-")
    return cleaned[:128] if cleaned else "candidate-analysis"


def _matching_signals(
    candidate: SourceCandidateRecord,
    signals: List[SourceSignalRecord],
) -> List[SourceSignalRecord]:
    return [
        signal
        for signal in signals
        if signal.event_theme == candidate.event_theme
        and signal.normalized_sector == candidate.sector
        and signal.normalized_symbol == candidate.symbol
    ]


def _representative_signal(signals: List[SourceSignalRecord]) -> SourceSignalRecord:
    if not signals:
        raise HTTPException(status_code=404, detail="no related signals found for candidate")

    ranked = sorted(
        signals,
        key=lambda item: (
            _CONFIRMATION_WEIGHT.get(item.normalized_confirmation, 0),
            _SEVERITY_WEIGHT.get(item.severity, 0),
            _TRUST_WEIGHT.get(item.trust_class, 0),
            abs(item.price_change_pct or 0.0),
            item.request_id,
        ),
        reverse=True,
    )
    return ranked[0]


def _bridge_confirmation(
    candidate: SourceCandidateRecord,
    representative: SourceSignalRecord,
) -> str:
    if candidate.confirmation_state in _ALLOWED_CONFIRMATIONS:
        return candidate.confirmation_state

    if representative.normalized_confirmation in _ALLOWED_CONFIRMATIONS:
        return representative.normalized_confirmation

    return "partial"


def _bridge_headline(
    candidate: SourceCandidateRecord,
    representative: SourceSignalRecord,
) -> str:
    if representative.headline:
        return representative.headline

    symbol = candidate.symbol or "UNSPECIFIED_SYMBOL"
    event_theme = candidate.event_theme.replace("_", " ").title()
    return f"{symbol} candidate signal from {event_theme}"


def _bridge_price_change_pct(representative: SourceSignalRecord) -> float:
    if representative.price_change_pct is not None:
        return float(representative.price_change_pct)
    return 0.0


def build_live_analysis_request(
    candidate: SourceCandidateRecord,
    signals: List[SourceSignalRecord],
    request_id: Optional[str] = None,
) -> dict:
    related_signals = _matching_signals(candidate, signals)
    representative = _representative_signal(related_signals)

    symbol = candidate.symbol
    if not symbol:
        raise HTTPException(status_code=400, detail="candidate is missing symbol")

    generated_request_id = request_id or f"bridge-{candidate.candidate_id}"
    generated_request_id = _sanitize_request_id(generated_request_id)

    return {
        "request_id": generated_request_id,
        "symbol": symbol,
        "headline": _bridge_headline(candidate, representative),
        "price_change_pct": _bridge_price_change_pct(representative),
        "sector": candidate.sector,
        "confirmation": _bridge_confirmation(candidate, representative),
    }


def build_live_analysis_bridge_payload(
    candidate_id: str,
    request_id: Optional[str],
    candidates: List[SourceCandidateRecord],
    signals: List[SourceSignalRecord],
) -> dict:
    candidate = next((item for item in candidates if item.candidate_id == candidate_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail=f"candidate not found: {candidate_id}")

    analysis_request = build_live_analysis_request(
        candidate=candidate,
        signals=signals,
        request_id=request_id,
    )

    return {
        "status": "ok",
        "mode": "advisory",
        "execution_allowed": False,
        "candidate_id": candidate.candidate_id,
        "cluster_key": candidate.cluster_key,
        "analysis_request": analysis_request,
    }
