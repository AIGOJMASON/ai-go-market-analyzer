from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, List
from uuid import uuid4

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
ARBITRATOR_DIR = os.path.join(REPO_ROOT, "engines", "refinement_arbitrator")
if ARBITRATOR_DIR not in sys.path:
    sys.path.insert(0, ARBITRATOR_DIR)

from persistence import persist_pm_intake_receipt  # noqa: E402


REQUIRED_ARBITRATION_FIELDS: List[str] = [
    "arbitration_id",
    "source_packet_id",
    "issuing_layer",
    "reasoning_weight",
    "human_tempering_weight",
    "child_core_fit_scores",
    "composite_weight",
    "recommended_action",
    "justification_summary",
    "timestamp",
]


class PMIntakeError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_pm_intake_id() -> str:
    return f"PMI-{uuid4().hex[:12].upper()}"


def validate_arbitration_packet(packet: Mapping[str, Any]) -> None:
    missing = [field for field in REQUIRED_ARBITRATION_FIELDS if field not in packet]
    if missing:
        raise PMIntakeError(f"Missing required arbitration fields: {', '.join(missing)}")
    if packet.get("issuing_layer") != "REFINEMENT_ARBITRATOR":
        raise PMIntakeError("PM intake accepts only REFINEMENT_ARBITRATOR decision packets.")


def intake_arbitration_decision(packet: Mapping[str, Any], *, persist: bool = True) -> Dict[str, Any]:
    validate_arbitration_packet(packet)

    target_core = packet.get("target_child_core")
    recommended_action = str(packet.get("recommended_action"))

    pm_ready = recommended_action in {
        "pass_to_pm",
        "condition_for_child_core",
        "send_to_curved_mirror",
        "send_to_rosetta",
        "hold",
        "discard",
    }

    pm_intake_id = build_pm_intake_id()
    timestamp = utc_now()

    record = {
        "pm_intake_id": pm_intake_id,
        "source_arbitration_id": packet["arbitration_id"],
        "source_packet_id": packet["source_packet_id"],
        "issuing_authority": "PM_CORE",
        "ingress_layer": "pm.refinement.arbitration_intake",
        "status": "accepted_for_pm_review" if pm_ready else "rejected",
        "recommended_action": recommended_action,
        "target_child_core": target_core,
        "composite_weight": float(packet["composite_weight"]),
        "reasoning_weight": float(packet["reasoning_weight"]),
        "human_tempering_weight": float(packet["human_tempering_weight"]),
        "child_core_fit_scores": dict(packet["child_core_fit_scores"]),
        "justification_summary": str(packet["justification_summary"]),
        "engine_invocations": list(packet.get("engine_invocations", [])),
        "decision_threshold_band": packet.get("decision_threshold_band"),
        "timestamp": timestamp,
        "receipt_ref": pm_intake_id,
    }

    receipt = {
        "receipt_type": "pm_intake_receipt",
        "pm_intake_id": pm_intake_id,
        "source_arbitration_id": packet["arbitration_id"],
        "status": record["status"],
        "recommended_action": recommended_action,
        "target_child_core": target_core,
        "timestamp": timestamp,
    }

    if persist:
        receipt_path = persist_pm_intake_receipt(receipt)
        record["receipt_path"] = receipt_path
        receipt["receipt_path"] = receipt_path

    return {
        "record": record,
        "receipt": receipt,
    }