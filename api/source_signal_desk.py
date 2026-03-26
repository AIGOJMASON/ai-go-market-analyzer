from typing import Dict, List

from fastapi import APIRouter, HTTPException

from AI_GO.api.source_candidate_bridge import build_live_analysis_bridge_payload
from AI_GO.api.source_ingress_schema import (
    SourceAnalyzeCandidateRequest,
    SourceIngressRequest,
    SourceSignalRecord,
)
from AI_GO.api.source_normalizer import normalize_source_item
from AI_GO.api.source_clusterer import cluster_signals
from AI_GO.api.source_dissemination import build_candidate_records, build_inbox_record


router = APIRouter(prefix="/market-analyzer/sources", tags=["market-analyzer-sources"])

_SIGNAL_STORE: List[dict] = []


@router.get("/health")
def source_signal_desk_health() -> dict:
    return {
        "status": "ok",
        "surface": "source_signal_desk",
        "mode": "advisory",
        "execution_allowed": False,
    }


@router.post("/ingest")
def ingest_source_item(request: SourceIngressRequest) -> dict:
    signal = normalize_source_item(request)
    _SIGNAL_STORE.append(signal.model_dump())

    return {
        "status": "ok",
        "mode": "advisory",
        "execution_allowed": False,
        "signal": signal.model_dump(),
    }


@router.get("/signals")
def list_signals() -> dict:
    return {
        "status": "ok",
        "mode": "advisory",
        "execution_allowed": False,
        "count": len(_SIGNAL_STORE),
        "signals": _SIGNAL_STORE,
    }


@router.get("/candidates")
def list_candidates() -> dict:
    if not _SIGNAL_STORE:
        return {
            "status": "ok",
            "mode": "advisory",
            "execution_allowed": False,
            "count": 0,
            "candidates": [],
        }

    signals = [rehydrate_signal(item) for item in _SIGNAL_STORE]
    clusters = cluster_signals(signals)
    candidates = build_candidate_records(signals, clusters)

    return {
        "status": "ok",
        "mode": "advisory",
        "execution_allowed": False,
        "count": len(candidates),
        "candidates": [candidate.model_dump() for candidate in candidates],
    }


@router.get("/inbox")
def get_inbox() -> dict:
    if not _SIGNAL_STORE:
        return {
            "status": "ok",
            "mode": "advisory",
            "execution_allowed": False,
            "inbox": {
                "artifact_type": "source_inbox_record",
                "sealed": True,
                "incoming_signals": [],
                "candidate_cases": [],
                "summary": {
                    "signal_count": 0,
                    "candidate_count": 0,
                    "analyze_count": 0,
                    "review_count": 0,
                    "monitor_count": 0,
                    "dismiss_count": 0,
                },
                "execution_influence": False,
                "recommendation_mutation_allowed": False,
                "runtime_mutation_allowed": False,
            },
        }

    signals = [rehydrate_signal(item) for item in _SIGNAL_STORE]
    clusters = cluster_signals(signals)
    candidates = build_candidate_records(signals, clusters)
    inbox = build_inbox_record(signals, candidates)

    return {
        "status": "ok",
        "mode": "advisory",
        "execution_allowed": False,
        "inbox": inbox.model_dump(),
    }


@router.post("/analyze-candidate")
def analyze_candidate_bridge(request: SourceAnalyzeCandidateRequest) -> dict:
    if not _SIGNAL_STORE:
        raise HTTPException(status_code=404, detail="no source signals available")

    signals = [rehydrate_signal(item) for item in _SIGNAL_STORE]
    clusters = cluster_signals(signals)
    candidates = build_candidate_records(signals, clusters)

    return build_live_analysis_bridge_payload(
        candidate_id=request.candidate_id,
        request_id=request.request_id,
        candidates=candidates,
        signals=signals,
    )


@router.delete("/reset")
def reset_signal_store() -> dict:
    _SIGNAL_STORE.clear()
    return {
        "status": "ok",
        "mode": "advisory",
        "execution_allowed": False,
        "message": "signal store cleared",
    }


def rehydrate_signal(payload: Dict) -> SourceSignalRecord:
    try:
        return SourceSignalRecord(**payload)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"invalid stored source signal record: {exc}",
        ) from exc
