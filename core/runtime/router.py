from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping
from uuid import uuid4
from datetime import datetime, timezone


@dataclass(frozen=True)
class RouteDecision:
    status: str
    source_surface: str
    target_surface: str
    artifact_type: str
    reason: str
    receipt_id: str
    timestamp: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_receipt_id() -> str:
    return f"RR-{uuid4().hex[:12].upper()}"


def detect_artifact_type(payload: Mapping[str, Any]) -> str:
    if payload.get("issuing_layer") == "REFINEMENT_ARBITRATOR":
        return "arbitration_decision_packet"
    if payload.get("update_type") == "pm_continuity_update":
        return "pm_continuity_update"
    if str(payload.get("source_core", "")).lower() == "research_core" and str(payload.get("screening_status", "")).lower() == "screened":
        return "screened_research_packet"
    if "pm_intake_id" in payload and "source_arbitration_id" in payload and "recommended_action" in payload:
        return "pm_intake_record"
    if payload.get("artifact_type"):
        return str(payload["artifact_type"])
    return "unknown"


def route_payload(
    payload: Mapping[str, Any],
    *,
    source_surface: str = "runtime.router",
) -> Dict[str, Any]:
    artifact_type = detect_artifact_type(payload)
    receipt_id = build_receipt_id()
    timestamp = utc_now()

    if artifact_type == "screened_research_packet":
        decision = RouteDecision(
            status="routable",
            source_surface=source_surface,
            target_surface="engines.refinement_arbitrator",
            artifact_type=artifact_type,
            reason="Screened RESEARCH_CORE packet must pass through Stage 16 arbitration before PM intake.",
            receipt_id=receipt_id,
            timestamp=timestamp,
        )
    elif artifact_type == "arbitration_decision_packet":
        decision = RouteDecision(
            status="routable",
            source_surface=source_surface,
            target_surface="pm.refinement.arbitration_intake",
            artifact_type=artifact_type,
            reason="Arbitration decision packet is PM-intake-ready and may move to PM refinement intake.",
            receipt_id=receipt_id,
            timestamp=timestamp,
        )
    elif artifact_type == "pm_intake_record":
        decision = RouteDecision(
            status="routable",
            source_surface=source_surface,
            target_surface="pm.smi.continuity",
            artifact_type=artifact_type,
            reason="PM intake record must update Stage 17 PM continuity before later PM strategic use.",
            receipt_id=receipt_id,
            timestamp=timestamp,
        )
    elif artifact_type == "pm_continuity_update":
        decision = RouteDecision(
            status="routable",
            source_surface=source_surface,
            target_surface="pm.strategy",
            artifact_type=artifact_type,
            reason="PM continuity update must enter Stage 18 strategy before downstream routing preparation.",
            receipt_id=receipt_id,
            timestamp=timestamp,
        )
    else:
        decision = RouteDecision(
            status="not_routable",
            source_surface=source_surface,
            target_surface="unresolved",
            artifact_type=artifact_type,
            reason="Payload did not match a governed runtime route.",
            receipt_id=receipt_id,
            timestamp=timestamp,
        )

    return {
        "status": decision.status,
        "source_surface": decision.source_surface,
        "target_surface": decision.target_surface,
        "artifact_type": decision.artifact_type,
        "reason": decision.reason,
        "receipt": {
            "receipt_type": "runtime_route_receipt",
            "receipt_id": decision.receipt_id,
            "status": decision.status,
            "source_surface": decision.source_surface,
            "target_surface": decision.target_surface,
            "artifact_type": decision.artifact_type,
            "reason": decision.reason,
            "timestamp": decision.timestamp,
        },
    }